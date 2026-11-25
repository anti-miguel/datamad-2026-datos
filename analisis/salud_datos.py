"""Salud de los grabadores, por fuente y día de Madrid, sin modificar datos.

Cobertura = unión de [t, t+cadencia), recortada al día civil (incluido el
cambio de hora). No mide cobertura de todas las paradas ni servicio prestado.
Un hueco sin posiciones/llegadas puede ser nocturno: no se atribuye por defecto
al operador. Los huecos sin filas tampoco prueban una caída del grabador.
Se aplican las atribuciones explícitas de catalogo.json; las nuevas son hipótesis.
"""
import argparse
from collections import Counter
from datetime import date, datetime, timedelta
import json
from pathlib import Path
import re
import sys
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import cargar

MADRID = ZoneInfo("Europe/Madrid")
CADENCIA = {"renfe": 30, "emt": 180, "crtm": 60, "trafico": 300, "avisos": 300}
RES = Path("analisis/resultados")


def limites_dia(dia):
    d = date.fromisoformat(dia)
    return (datetime.combine(d, datetime.min.time(), MADRID).timestamp(),
            datetime.combine(d + timedelta(days=1), datetime.min.time(), MADRID).timestamp())


def cobertura_huecos(tiempos, inicio, fin, cadencia):
    intervalos = []
    for t in sorted(set(tiempos)):
        a, b = max(inicio, t), min(fin, t + cadencia)
        if b <= a:
            continue
        if intervalos and a <= intervalos[-1][1]:
            intervalos[-1][1] = max(intervalos[-1][1], b)
        else:
            intervalos.append([a, b])
    huecos, cursor = [], inicio
    for a, b in intervalos:
        if a > cursor:
            huecos.append((cursor, a))
        cursor = b
    if cursor < fin:
        huecos.append((cursor, fin))
    return sum(b - a for a, b in intervalos), huecos


def es_error(r):
    return bool(r.get("err")) or any(v for k, v in r.items() if k.endswith("_err"))


def error_relevante(fuente, r):
    return es_error(r) and not (fuente == "emt" and r.get("k") in {"flota", "flota_descubrir", "login"})


def util(fuente, r):
    if error_relevante(fuente, r):
        return False
    if fuente == "renfe":
        return r.get("k") in {"vp", "tu"}
    if fuente in {"emt", "crtm"}:
        return bool(r.get("a"))
    if fuente == "trafico":
        return r.get("k") == "pm" and bool(r.get("r"))
    return r.get("k") in {"poll", "aviso", "baja"}


def reglas_catalogo(cat):
    reglas = []
    for h in cat["huecos"]:
        tramos = []
        if "desde" in h:
            tramos.append((datetime.fromisoformat(h["desde"]).replace(tzinfo=MADRID).timestamp(),
                           datetime.fromisoformat(h["hasta"]).replace(tzinfo=MADRID).timestamp()))
        for texto in h.get("fechas", []):
            dia = texto[:10]
            horas = re.search(r"(\d{2}:\d{2})-(\d{2}:\d{2})", texto)
            if horas:
                tramos.append(tuple(datetime.fromisoformat(f"{dia}T{x}").replace(tzinfo=MADRID).timestamp()
                                     for x in horas.groups()))
            else:
                tramos.append(limites_dia(dia))
        for a, b in tramos:
            reglas.append({"fuente": h["fuente"], "inicio": a, "fin": b, "tipo": h["tipo"],
                           "nota": h.get("nota", "Atribución declarada en catalogo.json")})
    return reglas


def clasificar_hueco(fuente, inicio, fin, reglas, actividad_propia, otras_activas):
    coincidencias = [h for h in reglas if h["fuente"] == fuente and
                     min(fin, h["fin"]) > max(inicio, h["inicio"])]
    if coincidencias:
        h = max(coincidencias, key=lambda h: min(fin, h["fin"]) - max(inicio, h["inicio"]))
        solape = min(fin, h["fin"]) - max(inicio, h["inicio"])
        return {"clase": "operador" if h["tipo"] == "operador" else "errores_de_consulta",
                "evidencia": "confirmado en código", "nota": h.get("nota", "Catálogo"),
                "solape_catalogado_s": round(solape),
                "limite": "La atribución solo cubre el solape; el resto del hueco es indeterminado."}
    if actividad_propia and otras_activas:
        return {"clase": "operador_o_acceso", "evidencia": "inferencia",
                "nota": "Hay consultas propias y otras fuentes activas. Puede ser horario sin servicio, respuesta vacía o fallo del endpoint; no demuestra caída del operador."}
    if not actividad_propia and not otras_activas:
        return {"clase": "indeterminado", "evidencia": "inferencia",
                "nota": "Compatible con caída del grabador o ausencia de recogida; sin registros de la NAS no se puede confirmar."}
    return {"clase": "indeterminado", "evidencia": "inferencia",
            "nota": "No hay evidencia suficiente para separar operador, acceso, horario y grabador."}


def hora(t):
    return datetime.fromtimestamp(t, MADRID).isoformat(timespec="seconds")


def escanear(fuente, dia):
    a, b = limites_dia(dia)
    cuenta, tipos = Counter(), Counter()
    actividad, utiles, errores = set(), set(), set()
    canales = {"emt": set(), "crtm": set()}
    cambios = Counter()
    paginas, poll_renfe = set(), []
    fallo = None
    try:
        for r in cargar.filas(fuente, dia):
            cuenta["filas"] += 1
            k = r.get("k", r.get("m", "consulta"))
            tipos[k] += 1
            cuenta["filas_error"] += int(es_error(r))
            relevante = error_relevante(fuente, r)
            cuenta["errores_relevantes"] += int(relevante)
            t = r.get("t")
            if not isinstance(t, (int, float)):
                cuenta["sin_t_valida"] += 1
                continue
            if not a <= t < b:
                cuenta["fuera_del_dia"] += 1
            actividad.add(t)
            if relevante:
                errores.add(t)
            if util(fuente, r):
                utiles.add(t)
                cuenta["filas_utiles"] += 1
            if "a" in r:
                cuenta["consultas"] += 1
                cuenta["consultas_vacias"] += int(not r["a"])
                paginas.add(str(r.get("s")))
            if fuente == "renfe" and k == "poll":
                poll_renfe.append({c: r.get(c) for c in ("t", "vp_n", "tu_n", "vp_hdr", "tu_hdr")})
            if fuente == "avisos":
                canal = "crtm" if k in {"poll_crtm", "aviso_crtm", "baja_crtm", "estado_red"} else "emt"
                canales[canal].add(t)
                cambios[k] += 1
    except (ValueError, OSError, EOFError) as e:
        fallo = f"{type(e).__name__}: {e}"
    cad = CADENCIA[fuente]
    cub, huecos = cobertura_huecos(actividad, a, b, cad)
    cub_util, huecos_utiles = cobertura_huecos(utiles, a, b, cad)
    salida = {"fuente": fuente, "dia": dia, "duracion_dia_s": int(b - a),
              **{k: cuenta[k] for k in ("filas", "filas_error", "errores_relevantes", "filas_utiles",
                                         "sin_t_valida", "fuera_del_dia", "consultas", "consultas_vacias")},
              "tipos": dict(tipos), "paradas_consultadas": len(paginas), "parseo_error": fallo,
              "cobertura_actividad_pct": round(100 * cub / (b - a), 3),
              "cobertura_con_contenido_pct": round(100 * cub_util / (b - a), 3),
              "_actividad": actividad, "_errores": errores, "_huecos": huecos,
              "_huecos_utiles": huecos_utiles, "_inicio": a, "_fin": b}
    if fuente == "avisos":
        salida["canales"] = {c: {"marcas": len(ts), "cobertura_actividad_pct":
                                 round(100 * cobertura_huecos(ts, a, b, 900 if c == "crtm" else 300)[0] / (b - a), 3)}
                              for c, ts in canales.items()}
        salida["eventos"] = dict(cambios)
    if poll_renfe:
        vp = sorted(p["vp_n"] for p in poll_renfe if isinstance(p["vp_n"], (int, float)))
        salida["renfe_poll"] = {"n": len(poll_renfe), "vp_n_mediana": vp[len(vp)//2] if vp else None,
                                 "vp_n_cero": sum(x == 0 for x in vp)}
        for campo in ("vp_hdr", "tu_hdr"):
            anterior, desde, maximo = None, None, 0
            for p in sorted(poll_renfe, key=lambda p: p["t"]):
                if p[campo] is None:
                    continue
                if p[campo] != anterior:
                    anterior, desde = p[campo], p["t"]
                maximo = max(maximo, p["t"] - desde)
            salida["renfe_poll"][f"congelacion_{campo}_max_s"] = maximo
    return salida


def enriquecer(registros, reglas):
    por_dia = {}
    for r in registros:
        por_dia.setdefault(r["dia"], []).append(r)
    for r in registros:
        otros = por_dia[r["dia"]]
        def detalle(par):
            a, b = par
            propio = any(a <= t < b for t in r["_actividad"])
            otras = [o["fuente"] for o in otros if o is not r and any(a <= t < b for t in o["_actividad"])]
            return {"desde": hora(a), "hasta": hora(b), "duracion_s": round(b-a),
                    "otras_fuentes_con_filas": otras,
                    **clasificar_hueco(r["fuente"], a, b, reglas, propio, bool(otras))}
        for nombre, clave in (("hueco_max_actividad", "_huecos"), ("hueco_max_contenido", "_huecos_utiles")):
            r[nombre] = detalle(max(r[clave], key=lambda x: x[1]-x[0])) if r[clave] else None
        r["huecos_actividad_20min"] = [detalle(x) for x in r["_huecos"] if x[1]-x[0] >= 1200]
        motivos = []
        if r["parseo_error"]:
            motivos.append("fichero no legible completo")
        if not r["filas"]:
            motivos.append("día esperado sin fichero o sin filas")
        if r["cobertura_actividad_pct"] < 90:
            motivos.append("cobertura de actividad inferior al 90%; puede ser inicio de despliegue")
        if r["huecos_actividad_20min"]:
            motivos.append("hueco de actividad de al menos 20 min")
        if r["errores_relevantes"] / max(1, r["filas"]) > .05:
            motivos.append("más del 5% de filas con error relevante")
        if r.get("renfe_poll", {}).get("congelacion_vp_hdr_max_s", 0) >= 1200:
            motivos.append("cabecera de posiciones congelada al menos 20 min (incluye noches)")
        if any(h["fuente"] == r["fuente"] and h["inicio"] < r["_fin"] and h["fin"] > r["_inicio"] for h in reglas):
            motivos.append("anomalía declarada en catalogo.json")
        r["revisar"] = motivos
    return [{k: v for k, v in r.items() if not k.startswith("_")} for r in registros]


def informe(resultado):
    registros = resultado["dias"]
    fallidos = sum(bool(r["parseo_error"]) for r in registros)
    largos = [(r["fuente"], r["dia"], h) for r in registros for h in r["huecos_actividad_20min"]]
    inicio_crtm = resultado.get("desde_consorcio", "2026-11-05")
    hay_crtm = any(r.get("canales", {}).get("crtm", {}).get("marcas", 0) for r in registros)
    estado_crtm = ("Hay filas del canal Consorcio en el detalle diario." if hay_crtm else
                   f"No hay día cerrado esperado hasta el corte {resultado['corte']}." if resultado["corte"] < inicio_crtm else
                   "No se observan filas del canal Consorcio pese a que su inicio declarado ya queda dentro del corte.")
    lineas = ["# Salud de los datos", "", f"Comprobado ejecutando: corte {resultado['corte']}, {len(registros)} días-fuente, "
              f"{sum(r['filas'] for r in registros):,} filas crudas. Fechas y horas en Europe/Madrid.", "",
              f"Comprobado ejecutando: {fallidos} ficheros con error de lectura; {len(largos)} huecos de actividad de al menos "
              "20 min. El detalle permite distinguir el arranque de cada fuente de los fallos posteriores. "
              "Una respuesta vacía o un feed congelado pueden coexistir con actividad del grabador completa.", "",
              "La cobertura mide presencia de filas del grabador en la red monitorizada. Cada marca cubre una cadencia "
              "hacia delante, recortada al día civil; el 25/10 dura 25 horas. No mide servicio ni todas las paradas. "
              "Contenido exige posiciones/retrasos, llegadas no vacías o puntos de tráfico; en avisos un poll correcto "
              "con cero novedades es contenido válido. Las filas de flota EMT 404 se cuentan en errores totales, "
              "pero no en errores relevantes de llegadas. Las respuestas vacías no son errores de parseo.", "",
              "Confirmado en código: las atribuciones operador proceden de catalogo.json y solo cubren su solape. "
              "Inferencia: la falta de filas no demuestra una caída de la NAS. No se fuerza una etiqueta operador/grabador "
              "sin evidencia. Las noches sin trenes y los inicios de despliegue pueden generar huecos sin avería.", "",
              "## Llegada de avisos", ""]
    for r in registros:
        if r["fuente"] == "avisos":
            lineas.append(f"Comprobado ejecutando: {r['dia']}, {r['filas']} filas, parseo "
                          f"{'completo' if not r['parseo_error'] else r['parseo_error']}, tipos {r['tipos']}; canales {r.get('canales')}.")
    lineas.extend(["", "Confirmado en código: avisos_crtm es un tipo dentro de datos/avisos, no una carpeta. "
                   f"Su recogida empieza el {inicio_crtm} según el catálogo. {estado_crtm} "
                   "Ausencia local no demuestra fallo de la NAS; no se ha accedido a ella.", "", "## Días que requieren revisión", ""])
    for r in registros:
        if r["revisar"]:
            lineas.append(f"- {r['fuente']} {r['dia']}: {'; '.join(r['revisar'])}.")
    lineas.extend(["", "## Detalle diario", "", "Comprobado ejecutando. El JSON incluye todos los huecos de actividad de 20 min, "
                   "las clases, los solapes y los tipos de fila. El mayor hueco incluye los bordes del día.", "",
                   "| Fuente | Día | Filas | Errores total/relevantes | Actividad % | Contenido % | Mayor hueco actividad min / clase |",
                   "|---|---|---:|---:|---:|---:|---|"])
    for r in registros:
        h = r["hueco_max_actividad"]
        hueco = f"{h['duracion_s']/60:.1f} / {h['clase']}" if h else "0"
        lineas.append(f"| {r['fuente']} | {r['dia']} | {r['filas']} | {r['filas_error']}/{r['errores_relevantes']} | "
                      f"{r['cobertura_actividad_pct']:.2f} | {r['cobertura_con_contenido_pct']:.2f} | {hueco} |")
    lineas.extend(["", "## Fuentes sin partición diaria", "",
                   "Confirmado en código: meteo, catalogo_cm, externos/rodalies y horarios_oficiales son instantáneas "
                   "o históricos publicados, no grabadores diarios. No se interpreta su ausencia de ficheros por día como caída. "
                   "datos/redes se excluye por la restricción de licencia. Las métricas de salud no validan la veracidad "
                   "de cada llegada ni la vigencia de los horarios.", ""])
    return "\n".join(lineas)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corte", default="2026-11-04")
    args = parser.parse_args()
    cat = json.loads(Path("catalogo.json").read_text(encoding="utf-8"))
    registros = []
    for fuente in CADENCIA:
        dias = cargar.dias(fuente)
        if not dias:
            continue
        d, final = date.fromisoformat(dias[0]), date.fromisoformat(args.corte)
        while d <= final:
            dia = d.isoformat()
            print(f"{fuente} {dia}", flush=True)
            registros.append(escanear(fuente, dia))
            d += timedelta(days=1)
    resultado = {"evidencia": "comprobado ejecutando", "corte": args.corte,
                 "desde_consorcio": next(c["desde_consorcio"] for c in cat["conjuntos"] if c["id"] == "avisos"),
                 "metodo": "unión de [t,t+cadencia) por fuente, recortada al día civil de Madrid",
                 "dias": enriquecer(registros, reglas_catalogo(cat))}
    RES.mkdir(exist_ok=True)
    (RES / "salud_datos.json").write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
    (RES / "salud_datos.md").write_text(informe(resultado), encoding="utf-8")
    print(f"Comprobado ejecutando: {len(registros)} días-fuente; salidas en {RES}/salud_datos.*")


if __name__ == "__main__":
    main()
