"""Tabla de fiabilidad: dado lo que anuncia el operador, ¿con qué probabilidad se cumple? Una entrada para la API.

Acierto: llega a ±2 min de lo anunciado. Cómo se conoce la llegada, según la red:
  renfe  GPS del tren (STOPPED_AT, o punto medio del paso por túnel, como analisis_nas.py). Medida independiente.
  emt    posición y estimación del autobús en la última consulta a <=120 s y <=600 m. Casi independiente.
         Esa última consulta no vale si la distancia es negativa o falta, o si positionTypeBus es 3 (ver README).
  metro  el tren desaparece del panel (punto medio, ±30 s). No es independiente: puede dar aciertos de más.
Los interurbanos no entran en la tabla: su panel no da una llegada real (ver README). Para ellos se calcula aparte
cuánto se mueve el anuncio (fiabilidad_interurbanos_estabilidad.csv).

Se muestrea para que las tres redes pesen parecido (~1 predicción cada 3 min por tren o autobús).
Las observaciones de un mismo vehículo están correlacionadas: el intervalo de confianza se calcula con n_llegadas.

Uso, desde la raíz de datos-transporte:
  python analisis/tabla_fiabilidad.py <carpeta temporal para la caché> [--corte AAAA-MM-DD] [--rehacer]
Salida: analisis/resultados/{fiabilidad,fiabilidad_interurbanos_estabilidad,fiabilidad_validacion}_AAAA-MM-DD.*
El corte predeterminado es ayer en Madrid. La caché se invalida si cambian las entradas o el corte.
"""
import argparse, collections as C, csv, glob, gzip, io, json, math, os, re, sys, time, zipfile
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import cargar as lectores

RES = "analisis/resultados"
HOR = "datos/horarios_oficiales"
BINS = [0, 3, 6, 10, 15, 25, 40]
ETQ = ["0-3", "3-6", "6-10", "10-15", "15-25", "25-40"]
MIN_LLEGADAS = 30
CORTE = (pd.Timestamp.now(tz="Europe/Madrid") - pd.Timedelta(days=1)).date().isoformat()


def franja(h):
    return "punta_manana" if 7 <= h < 9.5 else "valle" if 9.5 <= h < 17 else "punta_tarde" if 17 <= h < 20 else "noche"


def dias(fuente):
    return [p for p in sorted(glob.glob(f"datos/{fuente}/*.jsonl.gz")) if os.path.basename(p)[:10] <= CORTE]


def filas(f):
    yield from lectores.filas(os.path.basename(os.path.dirname(f)), os.path.basename(f)[:10])


def cabeceras_emt():
    """(línea, parada) donde la parada es la primera de algún viaje del GTFS."""
    with zipfile.ZipFile(f"{HOR}/crtm_gtfs_emt.zip") as z:
        rutas = {r["route_id"]: r["route_short_name"].strip()
                 for r in csv.DictReader(io.TextIOWrapper(z.open("routes.txt"), encoding="utf-8-sig"))}
        viajes = {r["trip_id"]: rutas.get(r["route_id"])
                  for r in csv.DictReader(io.TextIOWrapper(z.open("trips.txt"), encoding="utf-8-sig"))}
        cab = set()
        for r in csv.DictReader(io.TextIOWrapper(z.open("stop_times.txt"), encoding="utf-8-sig")):
            if r["stop_sequence"].strip() == "1":
                cab.add((viajes.get(r["trip_id"]), r["stop_id"].strip()))
    return cab


def extraer_emt():
    cab, out, cierres = cabeceras_emt(), [], [0, 0]
    for f in dias("emt"):
        dia = os.path.basename(f)[:10]
        obs = C.defaultdict(list)
        for r in filas(f):
            for lin, bus, est, dist, _lon, _lat, tipo, *_ in r.get("a", []):
                if bus and est is not None and est not in (888888, 999999):
                    fiable = dist is not None and dist >= 0 and str(tipo) != "3"
                    obs[(r["s"], lin, bus)].append((r["t"], est, dist or 0, fiable))
        for (s, lin, bus), seq in obs.items():
            seq.sort()
            visita = [seq[0]]
            for o in seq[1:] + [None]:  # visita nueva si el autobús desaparece >15 min
                if o is not None and o[0] - visita[-1][0] <= 900:
                    visita.append(o)
                    continue
                fin = visita[-1]
                if fin[1] <= 120 and fin[2] <= 600 and fin[3]:
                    real, ida = fin[0] + fin[1], f"{dia}|{s}|{lin}|{bus}|{fin[0]}"
                    cierres[0] += 1
                    for t, est, *_ in visita[:-1]:
                        out.append(("emt", dia, s, lin, "cabecera" if (lin, s) in cab else "intermedia", t,
                                    (real - t) / 60, (real - t - est) / 60, ida))
                else:
                    cierres[1] += 1
                if o is not None:
                    visita = [o]
    print(f"emt: {cierres[0]} llegadas; {cierres[1]} visitas sin cierre (pasó entre consultas o nunca llegó)", flush=True)
    return out, cierres


def extraer_metro():
    out, n = [], 0
    for f in dias("crtm"):
        dia = os.path.basename(f)[:10]
        por = C.defaultdict(list)
        for r in filas(f):
            if r.get("m") == "metro" and "a" in r:
                g = C.defaultdict(list)
                for lin, _d, dest, ts, _ in r["a"]:
                    if ts:
                        g[(lin, dest)].append(ts)
                por[r["s"]].append((r["t"], g))
        for s, seq in por.items():
            seq.sort(key=lambda x: x[0])
            vivos, nid = {}, 0
            for i, (t, g) in enumerate(seq):
                nuevos = {}
                for k, prev in g.items():
                    libres = {key: v for key, v in vivos.items() if key[:2] == k}
                    for p in sorted(prev):
                        cand = min(libres, key=lambda key: abs(libres[key][-1][1] - p), default=None)
                        if cand is not None and abs(libres[cand][-1][1] - p) < 240:
                            nuevos[cand] = libres.pop(cand) + [(t, p)]
                        else:
                            nid += 1
                            nuevos[k + (nid,)] = [(t, p)]
                for key, hist in vivos.items():
                    if key not in nuevos and i > 0 and t - seq[i - 1][0] <= 90 and hist[-1][1] - seq[i - 1][0] < 300:
                        real = (seq[i - 1][0] + t) / 2
                        n += 1
                        ida = f"{dia}|{s}|{key[0]}|{key[2]}"
                        for tc, p in hist:
                            if tc % 180 < 60:
                                out.append(("metro", dia, s, key[0], "estacion", tc, (real - tc) / 60, (real - p) / 60, ida))
                vivos = nuevos
        print(f"metro {dia}: {n} llegadas acumuladas", flush=True)
    return out


def horario_renfe(trips):
    """trip -> {parada: epoch programado}, con la fecha de calendar.txt (Europe/Madrid)."""
    sched = {}
    for z_ in sorted(glob.glob(f"{HOR}/renfe_gtfs_*.zip")):  # si un viaje está en los dos, manda el GTFS más reciente
        with zipfile.ZipFile(z_) as z:
            inicio = {r["service_id"].strip(): r["start_date"].strip()
                      for r in csv.DictReader(io.TextIOWrapper(z.open("calendar.txt"), encoding="utf-8-sig", errors="replace"))}
            with z.open("stop_times.txt") as raw:
                for fila in csv.reader(io.TextIOWrapper(raw, encoding="utf-8-sig", errors="replace")):
                    t = fila[0].strip()
                    if t not in trips:
                        continue
                    srv = t[:5]  # p. ej. 1065J = servicio del jueves 24/09
                    if srv not in inicio or not re.fullmatch(r"\d+:\d+:\d+", fila[1].strip()):
                        continue
                    h, m, s_ = map(int, fila[1].strip().split(":"))
                    base = datetime.strptime(inicio[srv], "%Y%m%d") + timedelta(hours=h, minutes=m, seconds=s_)
                    sched.setdefault(t, {})[fila[3].strip()] = base
    return sched


def epoch_madrid(dt):
    return pd.Timestamp(dt).tz_localize("Europe/Madrid", ambiguous=True).timestamp()  # 25/10: cambio de hora


def extraer_renfe():
    todos = []
    trips = set()
    for f in dias("renfe"):
        trips.update(r["trip"] for r in filas(f) if r.get("k") == "vp" and r.get("ts"))
    sched = horario_renfe(trips)
    print(f"renfe: horario de {len(sched)} de {len(trips)} trenes", flush=True)
    for f in dias("renfe"):
        dia = os.path.basename(f)[:10]
        vp, tu = C.defaultdict(list), []
        for r in filas(f):
            if r["k"] == "vp" and r.get("ts"):
                vp[r["trip"]].append((int(r["ts"]), r.get("stop"), r.get("st")))
            elif r["k"] == "tu" and r["t"] % 180 < 30:
                for stop, delay, rel in r["stops"]:
                    if delay is not None and abs(delay) < 3 * 3600 and rel != "SKIPPED":
                        tu.append((r["trip"], stop, r["t"], delay))
        print(f"renfe {dia}: {len(vp)} trenes, {len(tu)} predicciones", flush=True)
        llegadas = {}
        for trip, seq in vp.items():
            seq = sorted(set(seq))
            for i, (ts, s, st) in enumerate(seq):
                if st == "STOPPED_AT" and (trip, s) not in llegadas:
                    llegadas[(trip, s)] = ts
                if i + 1 < len(seq) and seq[i + 1][1] != s and (trip, s) not in llegadas and seq[i + 1][0] - ts <= 90:
                    llegadas[(trip, s)] = (ts + seq[i + 1][0]) / 2
        cache = {}
        for trip, stop, t, delay in tu:
            real = llegadas.get((trip, stop))
            prog = sched.get(trip, {}).get(stop)
            if real is None or prog is None:
                continue
            p = cache.setdefault(prog, epoch_madrid(prog))
            if not -300 <= real - p <= 7200:  # el mismo filtro que analisis_nas.py
                continue
            m = re.search(r"(C\d+[a-z]?)$", trip)
            todos.append(("renfe", dia, stop, m.group(1) if m else "?", "estacion", t, (real - t) / 60,
                          (real - p - delay) / 60, f"{trip}|{stop}"))
    return todos


COLS = ["red", "dia", "parada", "linea", "tipo", "t", "antel", "retraso", "llegada"]


def cargar(cache, rehacer):
    p = os.path.join(cache, "predicciones.parquet")
    entradas = {f: [os.path.getsize(f), os.stat(f).st_mtime_ns]
                for fuente in ("emt", "crtm", "renfe") for f in dias(fuente)}
    entradas.update({f: [os.path.getsize(f), os.stat(f).st_mtime_ns] for f in glob.glob(f"{HOR}/*.zip")})
    if os.path.exists(p) and not rehacer:
        with open(p + ".json") as f:
            meta = json.load(f)
        if meta.get("entradas") == entradas and meta.get("corte") == CORTE:
            return pd.read_parquet(p), meta
        print("La caché no corresponde a las entradas y al corte actuales; se recalcula.", flush=True)
    emt, cierres = extraer_emt()
    filas_ = emt + extraer_metro() + extraer_renfe()
    d = pd.DataFrame(filas_, columns=COLS)
    os.makedirs(cache, exist_ok=True)
    d.to_parquet(p)
    meta = {"emt_cierres": cierres, "corte": CORTE, "entradas": entradas}
    with open(p + ".json", "w") as f:
        json.dump(meta, f)
    return d, meta


def preparar(d):
    d = d.assign(anuncio=d.antel - d.retraso)  # lo que anunciaba el operador, no lo que tardó de verdad
    d = d[(d.antel >= 0) & (d.anuncio >= 0) & (d.anuncio < 40)].copy()
    d = d[~((d.red == "metro") & (d.anuncio >= 25))]  # casi no hay anuncios tan lejanos y los que hay no son representativos
    h = pd.to_datetime(d.t, unit="s", utc=True).dt.tz_convert("Europe/Madrid")
    d["franja"] = (h.dt.hour + h.dt.minute / 60).map(franja)
    d["tipo_dia"] = np.where(pd.to_datetime(d.dia).dt.dayofweek >= 5, "finde", "laborable")
    d.loc[d.dia == "2026-10-12", "tipo_dia"] = "finde"  # festivo
    d["anuncio_min"] = pd.cut(d.anuncio, BINS, right=False, labels=ETQ).astype(str)
    d["ok"] = d.retraso.abs() <= 2
    return d


def wilson(p, n, z=1.96):
    if n == 0:
        return (0.0, 1.0)
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    m = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return (max(0, c - m), min(1, c + m))


def resumen(g):
    n, p = g.llegada.nunique(), g.ok.mean()
    lo, hi = wilson(p, n)
    return pd.Series({"n_predicciones": len(g), "n_llegadas": n, "p_acierto_2min": round(p, 3),
                      "ic95_bajo": round(lo, 3), "ic95_alto": round(hi, 3),
                      "p_tarde_mas_2min": round((g.retraso > 2).mean(), 3), "p_antes_mas_2min": round((g.retraso < -2).mean(), 3),
                      "retraso_mediano_min": round(g.retraso.median(), 2),
                      "retraso_p10_min": round(g.retraso.quantile(.1), 2), "retraso_p90_min": round(g.retraso.quantile(.9), 2)})


NIVELES = {
    "1_red": ["red", "anuncio_min"],
    "2_franja": ["red", "franja", "tipo_dia", "anuncio_min"],
    "3_tipo": ["red", "tipo", "franja", "tipo_dia", "anuncio_min"],
    "4_linea": ["red", "linea", "franja", "tipo_dia", "anuncio_min"],
}


def tabla(d):
    partes = []
    for nivel, keys in NIVELES.items():
        t = d.groupby(keys, observed=True)[["llegada", "ok", "retraso"]].apply(resumen).reset_index()
        t.insert(0, "nivel", nivel)
        partes.append(t)
    cols = ["nivel", "red", "linea", "tipo", "franja", "tipo_dia", "anuncio_min"]
    t = pd.concat(partes, ignore_index=True)
    for c in cols:
        t[c] = t[c].fillna("*") if c in t else "*"
    resto = [c for c in t.columns if c not in cols]
    return t[cols + resto]


def predecir(train, test, keys):
    """Probabilidad por nivel con la misma regla que la API: si falta muestra, sube de nivel."""
    base = train.groupby(["red", "anuncio_min"], observed=True).ok.mean().rename("p0")
    r = test[["red", "anuncio_min"]].join(base, on=["red", "anuncio_min"])["p0"]
    for k in keys:
        g = train.groupby(k, observed=True).agg(p=("ok", "mean"), n=("llegada", "nunique"))
        g = g[g.n >= MIN_LLEGADAS].p
        v = test[k].join(g.rename("px"), on=k)["px"]
        r = v.fillna(r)
    return r.fillna(train.ok.mean())


def validar(d):
    esc = {"solo por red y anuncio (referencia)": [NIVELES["1_red"]],
           "+ franja y tipo de día": [NIVELES["2_franja"]],
           "+ tipo de parada": [NIVELES["2_franja"], NIVELES["3_tipo"]],
           "+ línea": [NIVELES["2_franja"], NIVELES["3_tipo"], NIVELES["4_linea"]]}
    lin = []
    def informe(nombre, mascara_test):
        lin.append(f"\n## {nombre}")
        for red in ["emt", "metro", "renfe"]:
            x = d[d.red == red]
            m = mascara_test(x)
            tr, te = x[~m], x[m]
            if te.empty or tr.empty:
                continue
            lin.append(f"{red}: {tr.llegada.nunique()} llegadas de entrenamiento, {te.llegada.nunique()} de prueba")
            ref = None
            for e, ks in esc.items():
                pr = predecir(tr, te, ks)
                b = ((pr - te.ok.astype(float)) ** 2).mean()
                ref = b if ref is None else ref
                lin.append(f"  {e:38s} Brier {b:.4f}  mejora {100 * (1 - b / ref):+5.1f}%")
            pr = predecir(tr, te, list(esc.values())[-1])
            cal = pd.DataFrame({"p": pr, "ok": te.ok.astype(float)})
            cal["cubo"] = pd.cut(cal.p, [0, .4, .5, .6, .7, .8, .9, 1.0])
            c = cal.groupby("cubo", observed=True).agg(previsto=("p", "mean"), observado=("ok", "mean"), n=("ok", "size"))
            lin.append("  calibración: " + "; ".join(f"dice {a:.0%} y pasa {b:.0%}" for a, b, n in c.itertuples(index=False) if n >= 200))

    # por tiempo: el último ~30 % de los días de cada red
    def ultimos(x):
        u = sorted(x.dia.unique())
        return x.dia.isin(u[int(len(u) * .7):])
    informe("Días que no ha visto (último 30 % de días de cada red)", ultimos)

    # por parada: 1 de cada 4 paradas, escogidas por hash estable
    def paradas(x):
        return x.parada.map(lambda s: sum(map(ord, str(s))) % 4 == 0)
    informe("Paradas que no ha visto (1 de cada 4)", paradas)

    # por línea: 1 de cada 4 líneas
    def lineas(x):
        return x.linea.map(lambda s: sum(map(ord, str(s))) % 4 == 0)
    informe("Líneas que no ha visto (1 de cada 4)", lineas)
    return "\n".join(lin)


def estabilidad_interurbanos():
    """Cuánto se mueve el anuncio entre que se hace y la última hora publicada. NO mide la llegada real."""
    filas_ = []
    for f in dias("crtm"):
        dia = os.path.basename(f)[:10]
        v = C.defaultdict(list)
        for r in filas(f):
            if r.get("m") == "interurbanos" and "a" in r:
                for lin, _d, _dest, ts, cod in r["a"]:
                    if ts and cod and lin in ("212", "691"):
                        v[(r["s"], lin, cod)].append((r["t"], ts))
        for (s, lin, _c), seq in v.items():
            seq.sort()
            ult_t, final = seq[-1]
            se_va = final - ult_t > 300  # desaparece >5 min antes de lo anunciado
            for t, ts in seq:
                if t % 180 < 60:
                    filas_.append((lin, s, (ts - t) / 60, (final - ts) / 60, se_va))
    d = pd.DataFrame(filas_, columns=["linea", "parada", "antel", "mov", "se_va"])
    d = d[(d.antel >= 0) & (d.antel < 40)]
    d["anuncio_min"] = pd.cut(d.antel, BINS, right=False, labels=ETQ).astype(str)
    g = d.groupby(["linea", "parada", "anuncio_min"])
    t = pd.DataFrame({"n": g.size(), "p_no_se_mueve_2min": g.apply(lambda x: (x.mov.abs() <= 2).mean(), include_groups=False).round(3),
                      "p_desaparece_antes": g.se_va.mean().round(3)}).reset_index()
    t["mide"] = "estabilidad del anuncio, no llegada real"
    return t


def main():
    global CORTE
    parser = argparse.ArgumentParser(description="Actualiza la tabla sin sobrescribir las salidas históricas.")
    parser.add_argument("cache")
    parser.add_argument("--corte", default=CORTE)
    parser.add_argument("--rehacer", action="store_true")
    parser.add_argument("--reemplazar", action="store_true", help="Regenera solo las salidas fechadas de este corte; preserva las históricas sin fecha.")
    args = parser.parse_args()
    CORTE = pd.Timestamp(args.corte).date().isoformat()
    if pd.Timestamp(CORTE).date() >= pd.Timestamp.now(tz="Europe/Madrid").date():
        parser.error("El corte debe ser un día cerrado de Madrid.")
    nombres = [f"{RES}/{n}_{CORTE}.{ext}" for n, ext in (("fiabilidad", "csv"), ("fiabilidad_interurbanos_estabilidad", "csv"), ("fiabilidad_validacion", "txt"))]
    if any(os.path.exists(p) for p in nombres) and not args.reemplazar:
        parser.error("Ya existe una salida de este corte; usa --reemplazar para regenerar solo las salidas fechadas.")
    d, meta = cargar(args.cache, args.rehacer)
    d = preparar(d)
    t = tabla(d)
    t.to_csv(nombres[0], index=False, encoding="utf-8")
    estabilidad_interurbanos().to_csv(nombres[1], index=False, encoding="utf-8")
    o, s = meta["emt_cierres"]
    cab = [f"Comprobado ejecutando. Corte solicitado: {CORTE}; extracción por día de Madrid.", f"Datos: {d.dia.min()} a {d.dia.max()}. Predicciones {len(d)}, llegadas {d.llegada.nunique()}.",
           "Por red: " + ", ".join(f"{r} {g.llegada.nunique()} llegadas" for r, g in d.groupby("red")),
           f"EMT: {s} de {o + s} visitas ({100 * s / (o + s):.0f}%) no se cierran y no entran: el autobús pasó entre consultas "
           f"o nunca llegó. Si parte son fantasmas, la fiabilidad real de la EMT es menor que la de la tabla.",
           "Validación (Brier: menos es mejor; mejora frente a usar solo red y anuncio)."]
    texto = "\n".join(cab) + "\n" + validar(d) + "\n"
    with open(nombres[2], "w", encoding="utf-8") as f:
        f.write(texto)
    print(texto)
    print(t[t.nivel == "1_red"][["red", "anuncio_min", "n_llegadas", "p_acierto_2min", "ic95_bajo", "ic95_alto", "p_tarde_mas_2min", "p_antes_mas_2min", "retraso_mediano_min"]].to_string(index=False))


if __name__ == "__main__":
    main()
