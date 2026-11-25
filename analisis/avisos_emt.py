"""Avisos EMT: contraste retrospectivo reproducible, fijado antes de calcular resultados.

Unidad: par (guid del aviso, línea GTFS exacta). Se toma la última versión del
aviso disponible, duración >0 y <=24 h, y todas las paradas grabadas de esa línea.
Franja: intervalo local exacto [desde, hasta), aplicado a la hora del anuncio;
no se infieren horarios adicionales del texto ni se corrigen fechas invertidas.
Al desplazar fechas, la hora repetida del cambio de octubre usa su primera
ocurrencia; una hora inexistente se lleva al siguiente instante válido.
Se conservan 001 y 002: son líneas distintas de 1 y 2 en el GTFS. Solo se quitan
ceros de una clave desconocida si identifica una única clave GTFS.

Llegada y acierto: método de tabla_fiabilidad.py (visita por parada/línea/bus,
separada por >900 s; cierre final a 0..120 s, 0..600 m, posición distinta de 3;
se excluye el cierre de los anuncios; horizonte 0..<40 min y llegada posterior
al anuncio; acierto a +/-120 s). Se filtran errores, control y códigos EMT.
Es una llegada estimada por EMT, no una observación independiente en la calle.

Control: misma línea y horario local desplazado -14, -7, +14, +21 días; +7 se
reserva al placebo. Se agrupan los anuncios de esas ventanas sin ponderar por
duración. Se descarta cada ventana que solape cualquier aviso conocido de esa
línea (también obras largas), o use un día ausente. Se exigen >=2 ventanas con
datos y, por brazo, >=20 anuncios y >=5 visitas distintas. El placebo usa el
mismo control y el intervalo a +7 días, sin avisos conocidos y con igual mínimo.
Se publica por separado el contraste principal y la muestra común al placebo.

Estimador: mediana entre pares de las tasas de acierto, y mediana de las
diferencias emparejadas. IC95 percentil: 5000 bootstrap agrupados por guid,
remuestreando avisos completos con todas sus líneas (semilla 20261105).
No se ajustan reglas para obtener el antiguo 67% -> 60%, 631 pares o placebo +1.

Uso desde la raíz: python analisis/avisos_emt.py
Salidas: analisis/resultados/avisos_emt_<corte>.{md,json} y *_pares.csv.
"""
import argparse
import collections as C
import csv
import io
import json
from pathlib import Path
import sys
import zipfile

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import cargar

TZ = "Europe/Madrid"
CONTROLES = (-14, -7, 14, 21)
MIN_ANUNCIOS = 20
MIN_LLEGADAS = 5


def lineas_gtfs():
    with zipfile.ZipFile("datos/horarios_oficiales/crtm_gtfs_emt.zip") as z:
        return {r["route_short_name"].strip() for r in csv.DictReader(
            io.TextIOWrapper(z.open("routes.txt"), encoding="utf-8-sig"))}


def normalizar_linea(valor, nombres):
    texto = str(valor).strip().upper()
    if texto in nombres or not texto.isdigit():
        return texto
    candidatas = [n for n in nombres if n.isdigit() and int(n) == int(texto)]
    return candidatas[0] if len(candidatas) == 1 else texto


def desplazar(inicio, fin, dias):
    return tuple((x.tz_localize(None) + pd.DateOffset(days=dias)).tz_localize(
        TZ, ambiguous=True, nonexistent="shift_forward") for x in (inicio, fin))


def contaminada(linea, inicio, fin, intervalos):
    return any(a < fin and b > inicio for a, b in intervalos.get(linea, []))


def predicciones_dia(filas, nombres, diagnostico):
    observaciones = C.defaultdict(list)
    for r in filas:
        if "err" in r or r.get("k") not in (None, "consulta"):
            continue
        for lin, bus, est, dist, _lon, _lat, tipo, *_ in r.get("a", []):
            if not bus or est is None or est in (888888, 999999):
                continue
            lin = normalizar_linea(lin, nombres)
            fiable = dist is not None and dist >= 0 and str(tipo) != "3"
            observaciones[(r["s"], lin, bus)].append((r["t"], est, dist, fiable))
    out, visita_id = [], 0
    for (_parada, lin, _bus), secuencia in observaciones.items():
        secuencia.sort()
        visita = [secuencia[0]]
        for o in secuencia[1:] + [None]:
            if o is not None and o[0] - visita[-1][0] <= 900:
                visita.append(o)
                continue
            tfin, estfin, distancia, fiable = visita[-1]
            if 0 <= estfin <= 120 and fiable and distancia <= 600:
                diagnostico["visitas_con_cierre"] += 1
                visita_id += 1
                real = tfin + estfin
                for t, est, *_ in visita[:-1]:
                    if 0 <= est < 2400 and real >= t:
                        out.append((lin, t, visita_id, abs(real - t - est) <= 120))
            else:
                diagnostico["visitas_sin_cierre"] += 1
            if o is not None:
                visita = [o]
    diagnostico["anuncios_elegibles"] += len(out)
    return pd.DataFrame(out, columns=["linea", "t", "llegada", "ok"])


def ventana_completa(inicio, fin, dias):
    fechas = pd.date_range(inicio.normalize(), (fin - pd.Timedelta(microseconds=1)).normalize(), freq="D")
    return all(f.strftime("%Y-%m-%d") in dias for f in fechas)


def construir_pares(avisos, dias, nombres, primeras):
    intervalos = C.defaultdict(list)
    for r in avisos.to_dict("records"):
        if pd.notna(r["desde"]) and pd.notna(r["hasta"]) and r["hasta"] > r["desde"]:
            for lin in set(normalizar_linea(l, nombres) for l in r.get("lineas", [])):
                intervalos[lin].append((r["desde"].timestamp(), r["hasta"].timestamp()))
    ventanas, pares, seleccion = {}, [], C.Counter()

    def registrar(lin, ini, fin):
        clave = (lin, ini.timestamp(), fin.timestamp())
        ventanas.setdefault(clave, {"n": 0, "aciertos": 0, "llegadas": set()})
        return clave

    for r in avisos.to_dict("records"):
        ini, fin = r["desde"], r["hasta"]
        if pd.isna(ini) or pd.isna(fin) or fin <= ini:
            seleccion["avisos_fechas_invalidas"] += 1
            continue
        if (fin - ini).total_seconds() > 86400:
            seleccion["avisos_mayores_24h"] += 1
            continue
        seleccion["avisos_hasta_24h"] += 1
        if not ventana_completa(ini, fin, dias):
            seleccion["avisos_con_fechas_sin_fichero"] += 1
            continue
        for lin in sorted(set(normalizar_linea(l, nombres) for l in r.get("lineas", []))):
            if lin not in nombres:
                seleccion["pares_linea_fuera_gtfs"] += 1
                continue
            control = []
            for salto in CONTROLES:
                a, b = desplazar(ini, fin, salto)
                if ventana_completa(a, b, dias) and not contaminada(lin, a.timestamp(), b.timestamp(), intervalos):
                    control.append(registrar(lin, a, b))
            a, b = desplazar(ini, fin, 7)
            placebo = None
            if ventana_completa(a, b, dias) and not contaminada(lin, a.timestamp(), b.timestamp(), intervalos):
                placebo = registrar(lin, a, b)
            pares.append({"guid": r["guid"], "linea": lin, "desde": ini.isoformat(),
                          "hasta": fin.isoformat(), "titulo": r.get("titulo", ""),
                          "primera_observacion": pd.Timestamp(primeras[r["guid"]], unit="s", tz="UTC").tz_convert(TZ).isoformat(),
                          "retrospectivo": ini.timestamp() < primeras[r["guid"]],
                          "aviso": registrar(lin, ini, fin), "controles": control, "placebo": placebo})
    return pares, ventanas, dict(seleccion)


def medir_ventanas(ventanas, dias, nombres):
    diagnostico = C.Counter()
    por_linea = C.defaultdict(list)
    for clave in ventanas:
        por_linea[clave[0]].append(clave)
    for dia in dias:
        d = predicciones_dia(cargar.filas("emt", dia), nombres, diagnostico)
        for lin, g in d.groupby("linea"):
            if lin not in por_linea:
                continue
            g = g.sort_values("t")
            t = g.t.to_numpy()
            for clave in por_linea[lin]:
                lo, hi = np.searchsorted(t, [clave[1], clave[2]], side="left")
                if hi > lo:
                    x, v = g.iloc[lo:hi], ventanas[clave]
                    v["n"] += len(x)
                    v["aciertos"] += int(x.ok.sum())
                    v["llegadas"].update((dia, int(i)) for i in x.llegada.unique())
        print(f"EMT {dia}: {len(d)} anuncios elegibles", flush=True)
    return dict(diagnostico)


def resumir_pares(pares, ventanas):
    filas = []
    for par in pares:
        r = {k: v for k, v in par.items() if k not in ("aviso", "controles", "placebo")}
        control = [ventanas[k] for k in par["controles"] if ventanas[k]["n"]]
        r["ventanas_control_con_datos"] = len(control)
        r["desplazamientos_control_dias"] = ";".join(str(s) for s in CONTROLES if any(
            abs(k[1] - desplazar(pd.Timestamp(par["desde"]), pd.Timestamp(par["hasta"]), s)[0].timestamp()) < .1
            for k in par["controles"]))
        muestras = {"aviso": ventanas[par["aviso"]],
                    "control": {"n": sum(x["n"] for x in control), "aciertos": sum(x["aciertos"] for x in control),
                                "llegadas": set().union(*(x["llegadas"] for x in control))},
                    "placebo": ventanas.get(par["placebo"], {"n": 0, "aciertos": 0, "llegadas": set()})}
        for nombre, x in muestras.items():
            r[f"n_{nombre}"] = x["n"]
            r[f"llegadas_{nombre}"] = len(x["llegadas"])
            r[f"p_{nombre}"] = x["aciertos"] / x["n"] if x["n"] else np.nan
        r["elegible"] = (len(control) >= 2 and all(r[f"n_{brazo}"] >= MIN_ANUNCIOS and
                          r[f"llegadas_{brazo}"] >= MIN_LLEGADAS for brazo in ("aviso", "control")))
        r["elegible_placebo"] = (r["elegible"] and r["n_placebo"] >= MIN_ANUNCIOS and
                                r["llegadas_placebo"] >= MIN_LLEGADAS)
        r["diferencia_pp"] = 100 * (r["p_aviso"] - r["p_control"])
        r["placebo_pp"] = 100 * (r["p_placebo"] - r["p_control"])
        filas.append(r)
    return pd.DataFrame(filas)


def estadistica(d, variable, replicas, semilla):
    if d.empty:
        return {"pares": 0, "avisos": 0, "mediana_diferencia_pp": None, "ic95_pp": None}
    grupos = [g[variable].to_numpy() for _, g in d.groupby("guid")]
    rng = np.random.default_rng(semilla)
    sims = [np.median(np.concatenate([grupos[i] for i in rng.integers(len(grupos), size=len(grupos))]))
            for _ in range(replicas)]
    return {"pares": len(d), "avisos": len(grupos), "mediana_diferencia_pp": float(d[variable].median()),
            "ic95_pp": np.quantile(sims, [.025, .975]).tolist(),
            "mediana_control_pct": float(100 * d.p_control.median()),
            "mediana_aviso_pct": float(100 * d.p_aviso.median()),
            "mediana_placebo_pct": float(100 * d.p_placebo.median()) if d.p_placebo.notna().any() else None,
            "anuncios_aviso_sumados_por_par": int(d.n_aviso.sum()),
            "anuncios_control_sumados_por_par": int(d.n_control.sum()),
            "anuncios_placebo_sumados_por_par": int(d.n_placebo.sum())}


def informe(resultado):
    def linea(nombre, s):
        if not s["pares"]:
            return f"- {nombre}: sin pares elegibles."
        a, b = s["ic95_pp"]
        return (f"- {nombre}: {s['pares']} pares, {s['avisos']} avisos; diferencia mediana "
                f"{s['mediana_diferencia_pp']:+.2f} puntos porcentuales; IC95 [{a:+.2f}, {b:+.2f}].")
    p = resultado["principal"]
    texto = ["# Avisos EMT: contraste retrospectivo", "", f"Corte de llegadas: {resultado['corte']}. Trabajo previo al desarrollo de DATAMAD.", "",
             "**Confirmado en código.** La definición completa de pares, franjas, control, placebo y selección está en la cabecera de `analisis/avisos_emt.py`. Las reglas se fijaron antes de ejecutar el contraste, sin buscar el antiguo resultado. Los desplazamientos conservan la hora local: en octubre, una hora repetida se interpreta como su primera ocurrencia; una hora inexistente se lleva al siguiente instante válido.", "",
             "**Comprobado ejecutando.**", "", linea("Aviso frente a control", p),
             linea("Aviso frente a control, muestra común", resultado["comun_aviso"]),
             linea("Placebo +7 días frente al mismo control, muestra común", resultado["comun_placebo"]),
             linea("Aviso menos placebo, muestra común", resultado["aviso_menos_placebo"])]
    if p["pares"]:
        texto += ["", f"La mediana entre pares pasa de {p['mediana_control_pct']:.2f}% en control a {p['mediana_aviso_pct']:.2f}% durante el aviso. La diferencia de estas dos medianas no es, en general, la mediana de las diferencias emparejadas.",
                  f"Se suman {p['anuncios_aviso_sumados_por_par']:,} anuncios de aviso y {p['anuncios_control_sumados_por_par']:,} de control entre los pares; son sumas por par, con reutilización de observaciones, no anuncios independientes."]
    texto += ["", f"Avisos en la última versión: {resultado['avisos_totales']}; pares candidatos con ficheros presentes en sus fechas y línea GTFS: {resultado['pares_candidatos']}. Selección: `{json.dumps(resultado['seleccion'], ensure_ascii=False)}`. Los recuentos de descarte por pares no son excluyentes; el CSV conserva todos los candidatos con sus tamaños y elegibilidad.",
              f"Extracción de llegadas: `{json.dumps(resultado['extraccion'], ensure_ascii=False)}`.", "",
              "**Diferencia respecto al 67% → 60%, 631 pares y placebo +1.** El cálculo original no tiene código ni definición exacta de franjas, duración, umbrales, controles o normalización; por ello no puede certificarse una réplica literal. Este contraste usa episodios de hasta 24 h, ventanas locales exactas, controles semanales libres de avisos conocidos, mínimo de muestra por brazo, dos controles con datos y cierre estricto de 120 s igual al de `tabla_fiabilidad.extraer_emt` para todas las paradas. El cierre de 400 s en cabeceras que describe el README corresponde a otro criterio y aquí no se aplica. El universo disponible ahora llega al 04/11. No se han variado estas reglas para acercarse a esas cifras.", "",
              "**Confirmado en código y GTFS local.** `001` (Atocha–Moncloa) y `1` (Cristo Rey–Prosperidad), así como `002` y `2`, son líneas distintas. Eliminar todos los ceros fusionaría servicios diferentes; aquí se conservan las claves exactas y solo se resuelven alias inequívocos. El consejo de normalizar ceros del README necesita esta salvedad.", "",
              f"**Retrospectiva y limitaciones.** {resultado['pares_inicio_anterior_observacion']} de los pares candidatos empiezan antes de la primera observación local del aviso. El RSS comenzó a grabarse el {resultado['primer_dia_avisos']}; solo conserva una selección de avisos antiguos y las versiones disponibles pueden haber cambiado después del suceso. No se usa `pub` como fecha de conocimiento. La ausencia de aviso conservado no acredita ausencia de incidencias en los controles. Las fechas invertidas se excluyen sin inventar una corrección.", "",
              "**Inferencia.** El contraste describe asociación en las paradas medidas; un aviso afecta solo a parte de la línea. Las tasas no se estandarizan por parada, horizonte del anuncio, lluvia o festivos, y los controles agrupan las ventanas con datos. La existencia del fichero diario no acredita cobertura continua del grabador ni del operador; los umbrales de muestra no eliminan ese sesgo. La llegada está estimada con el propio operador; las visitas sin cierre no entran y podrían contener fallos importantes. No demuestra un efecto causal ni sirve como validación prospectiva de una alerta en la app. El placebo debe interpretarse con su intervalo, sin dar por supuesto un efecto exactamente nulo.", "",
              f"IC95 percentil con {resultado['bootstrap_replicas']} remuestreos de avisos completos, semilla {resultado['semilla']}. Se mantienen juntas sus líneas, pero pueden quedar dependencias entre avisos solapados, días, líneas y controles reutilizados. El tamaño independiente se aproxima por avisos; una muestra pequeña requiere cautela.", "",
              "Comandos desde la raíz:", "", "```powershell", "python -m unittest analisis.test_avisos_emt", "python analisis/avisos_emt.py", "```", "",
              f"Intérprete ejecutado: `{resultado['python']}`; Python {resultado['version_python']}, pandas {pd.__version__}, NumPy {np.__version__}.", "",
              "Fuente: llegadas MobilityLabs y RSS público de EMT de Madrid, copia local hasta el corte indicado. Powered by EMT de Madrid. Condiciones: ODbL y MobilityLabs según README. Ningún acceso a red ni a NAS.", ""]
    return "\n".join(texto)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bootstrap", type=int, default=5000, help="Número de réplicas (>=100).")
    args = parser.parse_args()
    if args.bootstrap < 100:
        parser.error("Se requieren al menos 100 réplicas.")
    dias = cargar.dias("emt")
    avisos = cargar.avisos()
    primeras = {}
    for dia in cargar.dias("avisos"):
        for r in cargar.filas("avisos", dia):
            if r.get("k") == "aviso":
                primeras[r["guid"]] = min(primeras.get(r["guid"], r["t"]), r["t"])
    nombres = lineas_gtfs()
    pares, ventanas, seleccion = construir_pares(avisos, set(dias), nombres, primeras)
    diagnostico = medir_ventanas(ventanas, dias, nombres)
    d = resumir_pares(pares, ventanas)
    seleccion.update({"pares_sin_dos_controles_con_datos": int((d.ventanas_control_con_datos < 2).sum()),
                      "pares_aviso_muestra_insuficiente": int(((d.n_aviso < MIN_ANUNCIOS) | (d.llegadas_aviso < MIN_LLEGADAS)).sum()),
                      "pares_control_muestra_insuficiente": int(((d.n_control < MIN_ANUNCIOS) | (d.llegadas_control < MIN_LLEGADAS)).sum())})
    principal, comun = d[d.elegible], d[d.elegible_placebo].copy()
    comun["aviso_menos_placebo"] = 100 * (comun.p_aviso - comun.p_placebo)
    resultado = {"corte": dias[-1], "python": sys.executable, "version_python": sys.version.split()[0],
                 "avisos_totales": len(avisos), "pares_candidatos": len(d),
                 "primer_dia_avisos": cargar.dias("avisos")[0],
                 "pares_inicio_anterior_observacion": int(d.retrospectivo.sum()),
                 "seleccion": seleccion, "extraccion": diagnostico, "bootstrap_replicas": args.bootstrap, "semilla": 20261105,
                 "principal": estadistica(principal, "diferencia_pp", args.bootstrap, 20261105),
                 "comun_aviso": estadistica(comun, "diferencia_pp", args.bootstrap, 20261105),
                 "comun_placebo": estadistica(comun, "placebo_pp", args.bootstrap, 20261105),
                 "aviso_menos_placebo": estadistica(comun, "aviso_menos_placebo", args.bootstrap, 20261105)}
    destino = Path("analisis/resultados")
    destino.mkdir(exist_ok=True)
    prefijo = destino / f"avisos_emt_{dias[-1]}"
    d.to_csv(f"{prefijo}_pares.csv", index=False, encoding="utf-8")
    Path(f"{prefijo}.json").write_text(json.dumps(resultado, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    Path(f"{prefijo}.md").write_text(informe(resultado), encoding="utf-8")
    print(json.dumps(resultado, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
