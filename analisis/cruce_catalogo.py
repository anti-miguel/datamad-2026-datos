"""Cruza lo medido con datos del portal de la Comunidad de Madrid. Solo usa fuentes con licencia abierta publicada.

  EMT    intervalo real frente al programado (GTFS del portal) y frente al intervalo oficial de hora punta (1919185),
         velocidad frente a la oficial (1919184) y horas de espera de más según la demanda oficial (902003).
  Renfe  acierto de los anuncios por estación frente a sus viajeros (1923861).
El Metro no entra: se mide con el widget del Consorcio, que no tiene una licencia publicada para tiempo real.

Paso real de un autobús: la última lectura de cada visita, si anunciaba hasta 4 o hasta 10 min con posición fiable
(distancia no negativa y positionTypeBus distinto de 3). Se dan las dos cifras como rango. Solo cuenta un intervalo si la parada se consultó con datos al menos cada
10 min durante todo el intervalo. Se excluyen las cabeceras. Espera de más (EWT): espera real media (suma h² / 2 suma h)
menos la que correspondería con buses regulares a la frecuencia programada (h/2). Supone viajeros que llegan al azar.

Uso, desde la raíz de datos-transporte:
  python analisis/cruce_catalogo.py <carpeta de caché de tabla_fiabilidad.py>
Salida: analisis/resultados/cruce_catalogo.txt, cruce_catalogo_emt_lineas.csv, cruce_catalogo_renfe_estaciones.csv
Copia de los datos del portal: datos/catalogo_cm/
"""
import collections as C, csv, glob, gzip, io, json, os, re, sys, unicodedata, urllib.request, zipfile
from datetime import datetime, timedelta, timezone
import numpy as np
import pandas as pd

sys.path.insert(0, "analisis")
from tabla_fiabilidad import cabeceras_emt

RES = "analisis/resultados"
CM = "datos/catalogo_cm"
PORTAL = "https://datos.comunidad.madrid/api/3/action/package_show?id="
DATASETS = {"1919185": "intervalo_hora_punta", "1919184": "velocidad_comercial", "902003": "billetes_por_modo",
            "1923861": "viajeros_cercanias_estaciones"}
FESTIVOS = {"2026-10-12", "2026-11-02"}  # laborables sin servicio LA, según calendar_dates del GTFS
CENT = (888888, 999999)
ALIAS_ESTACIONES = {"MADRID ATOCHA C": "MADRID ATOCHA CERCANIAS", "MADRID CHAMARTIN": "MADRID CHAMARTIN CLARA CAMPOAMOR",
                    "NUEVOS MINISTERIOS": "MADRID NUEVOS MINISTERIOS", "MENDEZ ALVARO": "MENDEZ ALVARO P V", "RECOLETOS": "MADRID RECOLETOS",
                    "CANTOBLANCO": "UNIVERSIDAD CANTOBLANCO", "ENTREVIAS": "ASAMBLEA DE MADRID ENTREVIAS", "VILLAVERDE ALTO": "MADRID VILLAVERDE ALTO",
                    "VILLAVERDE BAJO": "MADRID VILLAVERDE BAJO", "GETAFE": "GETAFE CENTRO", "LA SERNA": "LA SERNA FUENLABRADA"}  # portal -> GTFS de Renfe
CAMBIO_HORA = datetime(2026, 10, 25, 1, tzinfo=timezone.utc).timestamp()
FRANJAS = {"punta": ((7.0, 9.5), (17.0, 20.0)), "dia": ((6.0, 23.0),)}
lineas_txt = []


def di(*a):
    t = " ".join(str(x) for x in a)
    print(t, flush=True)
    lineas_txt.append(t)


def norma(t):
    t = unicodedata.normalize("NFD", str(t)).encode("ascii", "ignore").decode().upper()
    return re.sub(r"[^A-Z0-9]+", " ", t).strip()


def linea(l):
    return str(l).strip().upper().lstrip("0") or "0"


def hora_local(t):
    d = t + (7200 if t < CAMBIO_HORA else 3600)
    return (d % 86400) / 3600


def catalogo():
    """Descarga una vez cada CSV del portal y guarda de dónde sale."""
    os.makedirs(CM, exist_ok=True)
    fuentes = os.path.join(CM, "fuentes.json")
    meta = json.load(open(fuentes, encoding="utf-8")) if os.path.exists(fuentes) else {}
    out = {}
    for ident, nombre in DATASETS.items():
        p = os.path.join(CM, nombre + ".csv")
        if not os.path.exists(p):
            with urllib.request.urlopen(urllib.request.Request(PORTAL + ident, headers={"User-Agent": "datamad"}), timeout=40) as r:
                d = json.load(r)["result"]
            rec = next(x for x in d["resources"] if (x.get("format") or "").upper() == "CSV")
            with urllib.request.urlopen(urllib.request.Request(rec["url"], headers={"User-Agent": "datamad"}), timeout=60) as r:
                b = r.read()
            with open(p, "wb") as f:
                f.write(b)
            meta[nombre] = {"dataset": ident, "titulo": d["title"], "licencia": d.get("license_title"), "ficha": f"https://datos.comunidad.madrid/dataset/{ident}",
                            "recurso": rec["url"], "modificado": d.get("metadata_modified"), "descargado": datetime.now().strftime("%Y-%m-%d")}
        b = open(p, "rb").read()
        try:
            s = b.decode("utf-8-sig")
        except UnicodeDecodeError:
            s = b.decode("latin-1")
        out[nombre] = pd.read_csv(io.StringIO(s), sep=";", dtype=str)
        out[nombre].columns = [norma(c).lower() for c in out[nombre].columns]
    with open(fuentes, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
    return out, meta


def ultimo(df, patron):
    x = df[df.concepto.str.contains(patron, regex=True, na=False)].copy()
    x["v"] = pd.to_numeric(x.valor.str.replace(",", "."), errors="coerce")
    x = x.dropna(subset=["v"])
    fila = x.sort_values("ano").iloc[-1]
    return fila.v, fila.ano


def horario_emt():
    """(línea, destino normalizado, servicio) -> lista de (inicio_h, fin_h, intervalo_min), y lo mismo por línea."""
    with zipfile.ZipFile("datos/horarios_oficiales/crtm_gtfs_emt.zip") as z:
        lee = lambda n: list(csv.DictReader(io.TextIOWrapper(z.open(n), encoding="utf-8-sig")))
        rutas = {r["route_id"]: linea(r["route_short_name"]) for r in lee("routes.txt")}
        viajes = {t["trip_id"]: (rutas[t["route_id"]], norma(t.get("trip_headsign") or ""), t["service_id"]) for t in lee("trips.txt")}
        frec = lee("frequencies.txt")
    h = lambda s: sum(float(x) / 60 ** i for i, x in enumerate(s.split(":")))
    por_dest, por_lin = C.defaultdict(C.Counter), C.defaultdict(C.Counter)
    for f in frec:
        if f["trip_id"] not in viajes:
            continue
        lin, dest, srv = viajes[f["trip_id"]]
        ventana = (h(f["start_time"]), h(f["end_time"]), int(f["headway_secs"]) / 60)
        por_dest[(lin, dest, srv)][ventana] += 1
        por_lin[(lin, srv)][ventana] += 1
    return por_dest, por_lin


def programado(tabla, clave, hora):
    v = [w[2] for w in tabla.get(clave, ()) if w[0] <= hora < w[1]]
    return float(np.median(v)) if v else None


def pasos_emt(limite_s):
    """Pasos por (parada, línea, destino) y horas con datos por parada, de los laborables."""
    cab = {(linea(l), str(s)) for l, s in cabeceras_emt()}
    pasos, consultas, velocidad = C.defaultdict(list), C.defaultdict(list), C.defaultdict(lambda: [0.0, 0.0])
    for f in sorted(glob.glob("datos/emt/*.jsonl.gz")):
        dia = os.path.basename(f)[:10]
        if pd.Timestamp(dia).dayofweek >= 5 or dia in FESTIVOS:
            continue
        obs = C.defaultdict(list)
        with gzip.open(f, "rt", encoding="utf-8") as g:
            for l in g:
                r = json.loads(l)
                if not r.get("a"):
                    continue
                reales = False
                for lin, bus, est, dist, _lo, _la, tipo, dest in r["a"]:
                    if bus and est is not None and est not in CENT:
                        reales = True
                        obs[(str(r["s"]), linea(lin), dest, bus)].append((r["t"], est, dist, str(tipo)))
                if reales:
                    consultas[(dia, str(r["s"]))].append(r["t"])
        for (s, lin, dest, bus), seq in obs.items():
            if (lin, s) in cab:
                continue
            seq.sort()
            visita = [seq[0]]
            for o in seq[1:] + [None]:
                if o is not None and o[0] - visita[-1][0] <= 900:
                    a = visita[-1]
                    if a[3] != "3" and o[3] != "3" and a[2] and o[2] and a[2] > 1500 and 120 <= o[0] - a[0] <= 240 and 7 <= hora_local(a[0]) < 21:
                        dd = a[2] - o[2]
                        if 0 <= dd / (o[0] - a[0]) <= 20:
                            velocidad[lin][0] += dd
                            velocidad[lin][1] += o[0] - a[0]
                    visita.append(o)
                    continue
                t, est, dist, tipo = visita[-1]
                if est <= limite_s and dist is not None and dist >= 0 and tipo != "3":
                    pasos[(dia, s, lin, dest)].append(t + est)
                if o is not None:
                    visita = [o]
    return pasos, consultas, velocidad


def intervalos(pasos, consultas):
    filas = []
    arr = {k: np.array(sorted(v)) for k, v in consultas.items()}
    for (dia, s, lin, dest), ts in pasos.items():
        ts = sorted(ts)
        c = arr.get((dia, s))
        for a, b in zip(ts, ts[1:]):
            h = b - a
            if h <= 0 or h > 7200 or c is None:
                continue
            i, j = np.searchsorted(c, a), np.searchsorted(c, b)
            tramo = np.concatenate(([a], c[i:j], [b]))
            if np.diff(tramo).max() > 600:
                continue
            filas.append((dia, s, lin, dest, hora_local(a), h / 60))
    return pd.DataFrame(filas, columns=["dia", "parada", "linea", "destino", "hora", "h"])


def en_franja(d, nombre):
    return np.logical_or.reduce([(d.hora >= a) & (d.hora < b) for a, b in FRANJAS[nombre]])


def resumen(d):
    """Espera real, programada, EWT y pasos vistos frente a esperados."""
    if d.empty or d.h.sum() == 0:
        return None
    awt = (d.h ** 2).sum() / (2 * d.h.sum())
    swt = (d.h * d.prog).sum() / d.h.sum() / 2
    return pd.Series({"n": len(d), "prog_min": round(2 * swt, 1), "real_media_min": round(d.h.mean(), 1), "real_mediana_min": round(d.h.median(), 1),
                      "espera_real_min": round(awt, 2), "espera_prog_min": round(swt, 2), "ewt_min": round(awt - swt, 2),
                      "pasos_vistos_frente_a_esperados": round(len(d) / (d.h / d.prog).sum(), 2), "p_mas_del_doble": round((d.h > 2 * d.prog).mean(), 3)})


def bloque_emt(cat):
    por_dest, por_lin = horario_emt()
    oficial, ano = ultimo(cat["intervalo_hora_punta"], "autobuses urbanos de Madrid")
    vel_of, ano_v = ultimo(cat["velocidad_comercial"], "velocidad comercial de los autobuses urbanos")
    demanda, ano_d = ultimo(cat["billetes_por_modo"], r"red de autob.s \(EMT\)")
    todos = [w[2] for k, c in por_lin.items() if k[1] == "LA" for w, n in c.items() for _ in range(n) if (w[0] < 9.5 and w[1] > 7) or (w[0] < 20 and w[1] > 17)]
    di(f"EMT. Oficial: {oficial} min de intervalo medio en hora punta ({ano}). GTFS del portal, media de sus ventanas de punta (todas las líneas): {np.mean(todos):.1f} min.")
    res = {}
    for nombre, limite in (("hasta 4 min", 240), ("hasta 10 min", 600)):  # se consulta cada 3 min: el resultado se estabiliza desde 5 min
        pasos, consultas, velocidad = pasos_emt(limite)
        d = intervalos(pasos, consultas)
        d["prog"] = [programado(por_dest, (l, norma(x), "LA"), h) or programado(por_lin, (l, "LA"), h) for l, x, h in zip(d.linea, d.destino, d.hora)]
        sin = d.prog.isna().mean()
        d = d.dropna(subset=["prog"])
        res[nombre] = d
        di(f"\nÚltima lectura {nombre}: {len(d)} intervalos, {d.linea.nunique()} líneas, {d.parada.nunique()} paradas, días {d.dia.min()} a {d.dia.max()}; sin horario: {sin:.1%}")
        for f in FRANJAS:
            x = d[en_franja(d, f)]
            r = resumen(x)
            di(f"  {f}: programado {r.prog_min}, real media {r.real_media_min}, mediana {r.real_mediana_min}; espera real {r.espera_real_min} frente a {r.espera_prog_min}; "
               f"EWT {r.ewt_min} min; pasos vistos/esperados {r.pasos_vistos_frente_a_esperados}; más del doble de lo programado {r.p_mas_del_doble:.0%}")
    d = res["hasta 10 min"]  # la lectura más generosa da la cifra más prudente
    t = d[en_franja(d, "punta")].groupby("linea")[["h", "prog"]].apply(resumen).dropna()
    t = t[t.n >= 100].sort_values("ewt_min", ascending=False)
    t.to_csv(f"{RES}/cruce_catalogo_emt_lineas.csv", encoding="utf-8")
    di(f"\nPunta, {len(t)} líneas con 100 intervalos o más. EWT mediana {t.ewt_min.median():.2f} min; pasos vistos/esperados, mediana {t.pasos_vistos_frente_a_esperados.median():.2f}")
    bien = t[t.pasos_vistos_frente_a_esperados >= 0.9]
    di(f"  Líneas con 90% de pasos vistos o más: {len(bien)}; su EWT mediana {bien.ewt_min.median():.2f} min")
    di("  Mayor EWT:\n" + t.head(8)[["n", "prog_min", "real_media_min", "ewt_min", "pasos_vistos_frente_a_esperados"]].to_string())
    di("\nImpacto, orden de magnitud. Demanda oficial EMT: %.1f M viajes (%s). Extrapola paradas céntricas y laborables a toda la red: no es una medición." % (demanda, ano_d))
    for nombre, x in res.items():
        dia = x[en_franja(x, "dia")]
        tl = dia.groupby("linea")[["h", "prog"]].apply(resumen).dropna()
        tl = tl[tl.n >= 100]
        for rot, ew in (("mediana de líneas", tl.ewt_min.median()), ("líneas con 90% de pasos vistos", tl[tl.pasos_vistos_frente_a_esperados >= 0.9].ewt_min.median())):
            di(f"  Lectura {nombre}, {rot}: EWT {ew:.2f} min -> {demanda * ew / 60:.1f} M horas al año")
    pasos, _c, velocidad = pasos_emt(240)
    m = sum(v[0] for v in velocidad.values())
    s = sum(v[1] for v in velocidad.values())
    di(f"\nVelocidad, laborables de 7 a 21 h, según la distancia a paradas céntricas: {3.6 * m / s:.1f} km/h. Oficial: {vel_of} km/h ({ano_v}, media diaria anual de toda la red). No son directamente comparables.")


def bloque_renfe(cat, cache):
    p = os.path.join(cache, "predicciones.parquet")
    d = pd.read_parquet(p, columns=["red", "dia", "parada", "antel", "retraso", "llegada"])
    d = d[d.red == "renfe"].copy()
    d["an"] = d.antel - d.retraso
    d = d[(d.antel >= 0) & (d.an >= 3) & (d.an < 25)]
    d["ok"] = d.retraso.abs() <= 2
    gt = sorted(glob.glob("datos/horarios_oficiales/renfe_gtfs_*.zip"))[-1]
    with zipfile.ZipFile(gt) as z:
        nombres = {r["stop_id"].strip(): norma(r["stop_name"]) for r in csv.DictReader(io.TextIOWrapper(z.open("stops.txt"), encoding="utf-8-sig", errors="replace"))}
    d["nombre"] = d.parada.astype(str).str.strip().map(nombres)
    a = d.groupby("nombre").agg(acierto=("ok", "mean"), llegadas=("llegada", "nunique"), tarde=("retraso", lambda x: (x > 2).mean()))
    a = a[a.llegadas >= 500]
    v = cat["viajeros_cercanias_estaciones"].copy()
    v["n"] = pd.to_numeric(v.valor, errors="coerce")
    v["nombre"] = v.concepto.str.extract(r"estaci.n de (.*)$", expand=False).map(norma).replace(ALIAS_ESTACIONES)
    v = v.dropna(subset=["n"])  # el portal pone "-" en varias estaciones
    ano = v.ano.max()
    v = v[v.ano == ano].set_index("nombre").n
    m = a.join(v, how="inner")
    m["viajeros_fallo"] = (m.n * (1 - m.acierto)).round()
    m = m.sort_values("viajeros_fallo", ascending=False)
    m.round(3).to_csv(f"{RES}/cruce_catalogo_renfe_estaciones.csv", encoding="utf-8")
    di(f"\nRenfe. Viajeros por estación de {ano}: {len(v)} estaciones con dato en el portal, {len(m)} cruzadas con las nuestras de 500 llegadas o más.")
    di(f"  Del portal sin cruzar: {sorted(set(v.index) - set(m.index))}")
    di(f"  Correlación de rangos entre viajeros y acierto: {m.n.corr(m.acierto, method='spearman'):.2f}")
    di(f"  Acierto ponderado por viajeros: {(m.acierto * m.n).sum() / m.n.sum():.1%}; sin ponderar: {m.acierto.mean():.1%}")
    t = m.head(10).copy()
    t["acierto"] = (t.acierto * 100).round().astype(int)
    t["M_viajeros"] = (t.n / 1e6).round(1)
    di("  Más viajeros expuestos a un anuncio que no se cumple:\n" + t[["M_viajeros", "acierto", "llegadas"]].to_string())


def main():
    cat, meta = catalogo()
    di("Fuentes del portal:", "; ".join(f"{v['dataset']} ({v['licencia']})" for v in meta.values()))
    bloque_emt(cat)
    bloque_renfe(cat, sys.argv[1])
    with open(f"{RES}/cruce_catalogo.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(lineas_txt) + "\n")


if __name__ == "__main__":
    main()
