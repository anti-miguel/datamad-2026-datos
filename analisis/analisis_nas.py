"""Un día de Cercanías Madrid grabado en el NAS (renfe-logger): llegada real por GPS frente a horario y predicción.

- Llegada observada a una estación: primera marca de tiempo del vehículo con estado STOPPED_AT en esa parada
  (resolución ~30 s, el intervalo de consulta).
- Predicción: retraso que Renfe publicaba para esa parada en cada consulta anterior a la llegada.
Uso: python analisis_nas.py datos/renfe/2026-09-24.jsonl.gz <carpeta GTFS de Renfe>
"""
import gzip, json, sys, csv, collections as C
from datetime import datetime, timedelta
import pandas as pd

SRC, GTFS = sys.argv[1], sys.argv[2]
DIA = datetime.strptime(SRC.replace("\\", "/").split("/")[-1][:10], "%Y-%m-%d")

L = [json.loads(x) for x in gzip.open(SRC, "rt", encoding="utf-8")]
# service_id del día en el GTFS de Renfe (p. ej. 1065J = jue 24/09): el prefijo más frecuente en el feed
PREFIJO = C.Counter(r["trip"][:5] for r in L if r["k"] == "vp").most_common(1)[0][0]
print(f"### {DIA:%A %d/%m/%Y} (servicio {PREFIJO})")
vp = pd.DataFrame([r for r in L if r["k"] == "vp"])
tu = [r for r in L if r["k"] == "tu"]
trips = set(vp.trip) | {r["trip"] for r in tu}

# horario oficial de los trenes que aparecen en el feed
sched = {}
with open(f"{GTFS}/stop_times.txt", encoding="utf-8", errors="replace") as f:
    for row in csv.reader(f):
        t = row[0].strip()
        if t in trips:
            h, m, s = map(int, row[1].strip().split(":"))
            sched[(t, row[3].strip())] = DIA + timedelta(hours=h, minutes=m, seconds=s)
names = {r["stop_id"].strip(): r["stop_name"].strip()
         for r in csv.DictReader(open(f"{GTFS}/stops.txt", encoding="utf-8", errors="replace"))}
lineas = {t: t[len(PREFIJO) + 5:] if t.startswith(PREFIJO) else "?" for t in trips}

# llegada observada por GPS. En estaciones de túnel (Sol, N. Ministerios en C3/C4...) el feed nunca marca
# STOPPED_AT: ahí se toma el punto medio entre la última posición "hacia S" y la primera "hacia la siguiente",
# solo si ese intervalo es de 90 s o menos.
v = vp[vp.ts.notna()].copy()
v["ts"] = v.ts.astype(int)
v = v.drop_duplicates(["trip", "ts"]).sort_values(["trip", "ts"])
llegadas = {}
for trip, g in v.groupby("trip"):
    stops, sts, tss = g.stop.tolist(), g.st.tolist(), g.ts.tolist()
    for i, (s, e, ts) in enumerate(zip(stops, sts, tss)):
        if e == "STOPPED_AT" and (trip, s) not in llegadas:
            llegadas[(trip, s)] = (ts, "gps parado")
        if i + 1 < len(stops) and stops[i + 1] != s and (trip, s) not in llegadas and tss[i + 1] - ts <= 90:
            llegadas[(trip, s)] = ((ts + tss[i + 1]) // 2, "gps estimado")
obs = pd.DataFrame.from_dict(llegadas, orient="index", columns=["ts", "metodo"])
obs.index = pd.MultiIndex.from_tuples(obs.index, names=["trip", "stop"])
obs["obs"] = pd.to_datetime(obs.ts, unit="s", utc=True).dt.tz_convert("Europe/Madrid").dt.tz_localize(None)
obs = obs.drop(columns="ts")
obs["sched"] = [sched.get(k) for k in obs.index]
obs = obs.dropna()
obs["retraso"] = (obs.obs - obs.sched).dt.total_seconds() / 60
obs = obs[obs.retraso.between(-5, 120)]
obs["linea"] = [lineas[t] for t, _ in obs.index]
obs["hora"] = obs.sched.dt.hour + obs.sched.dt.minute / 60


def franja(h):
    return "punta mañana 7-9:30" if 7 <= h < 9.5 else "punta tarde 17-20" if 17 <= h < 20 else "resto"


obs["franja"] = obs.hora.map(franja)

paradas_prog = sum(1 for k in sched)
print(f"Trenes con GPS: {vp.trip.nunique()} | llegadas observadas: {len(obs)} de {paradas_prog} paradas programadas "
      f"({len(obs) / paradas_prog:.0%}) — {dict(obs.metodo.value_counts())}\n")

print("== Retraso real al llegar (min), por franja ==")
print(obs.groupby("franja").retraso.describe(percentiles=[.5, .9, .95])[["count", "50%", "90%", "95%"]]
      .round(1).to_string(), "\n")
print("== Punta de mañana por línea ==")
pm = obs[obs.franja.str.startswith("punta mañana")]
print(pm.groupby("linea").retraso.agg(llegadas="size", mediana="median", p95=lambda s: s.quantile(.95),
                                      mas_5min=lambda s: (s > 5).mean() * 100).round(1)
      .sort_values("llegadas", ascending=False).to_string(), "\n")

# precisión de la predicción de Renfe según antelación
pred = []
for r in tu:
    for stop, delay, rel in r["stops"]:
        k = (r["trip"], stop)
        if delay is None or k not in obs.index:
            continue
        o = obs.loc[k]
        llegada_pred = o.sched + timedelta(seconds=delay)
        antel = (o.obs - datetime.fromtimestamp(r["t"])).total_seconds() / 60
        if antel >= 0:
            pred.append((antel, (llegada_pred - o.obs).total_seconds() / 60, (o.sched - o.obs).total_seconds() / 60))
P = pd.DataFrame(pred, columns=["antelacion", "err_renfe", "err_horario"])
P["bin"] = pd.cut(P.antelacion, [0, 2, 5, 10, 20, 40], right=False,
                  labels=["0-2 min", "2-5 min", "5-10 min", "10-20 min", "20-40 min"])
g = P.groupby("bin", observed=True)
print("== ¿Acierta Renfe? Error de la predicción según cuánto antes se hizo (min; negativo = optimista) ==")
print(pd.DataFrame({
    "predicciones": g.size(),
    "error mediano": g.err_renfe.median(),
    "error abs p90": g.err_renfe.apply(lambda s: s.abs().quantile(.9)),
    "% a ±1 min": g.err_renfe.apply(lambda s: (s.abs() <= 1).mean() * 100),
    "% a ±2 min": g.err_renfe.apply(lambda s: (s.abs() <= 2).mean() * 100),
    "horario: % a ±2 min": g.err_horario.apply(lambda s: (s.abs() <= 2).mean() * 100),
}).round(1).to_string(), "\n")

# supresiones (paradas marcadas SKIPPED)
sk = {(r["trip"], s[0]) for r in tu for s in r["stops"] if s[2] == "SKIPPED"}
print(f"== Supresiones: {len(sk)} paradas suprimidas en {len({t for t, _ in sk})} trenes ==")
print(C.Counter(lineas.get(t, "?") for t, _ in sk).most_common(8), "\n")

# el plan de Google: C5 Móstoles -> Atocha -> Nuevos Ministerios, llegar antes de las 9:00
MOST, ATO, NM = "35606", "18000", "18002"
c5 = [(t, sched[(t, MOST)]) for t in trips if lineas[t] == "C5" and (t, MOST) in sched
      and (t, ATO) in sched and sched[(t, ATO)] > sched[(t, MOST)]
      and timedelta(hours=7, minutes=30) <= sched[(t, MOST)] - DIA <= timedelta(hours=8, minutes=25)]
hacia_nm = [(o_at, obs.loc[(t, NM)].obs) for (t, s), o_at in obs.obs.items()
            if s == ATO and (t, NM) in obs.index and obs.loc[(t, NM)].obs > o_at]
print(f"== {DIA:%d/%m}: C5 desde Móstoles Central, transbordo 4 min en Atocha, 1 min a pie; ¿antes de las 9:00? ==")
for t, sale in sorted(c5, key=lambda x: x[1]):
    if (t, ATO) not in obs.index:
        print(f"  {sale:%H:%M}  sin llegada GPS a Atocha");  continue
    at = obs.loc[(t, ATO)].obs
    sig = sorted(n for a, n in hacia_nm if a >= at + timedelta(minutes=4))
    llega = sig[0] + timedelta(minutes=1) if sig else None
    marca = "" if llega is None else ("a tiempo" if llega <= DIA + timedelta(hours=9) else "TARDE")
    print(f"  {sale:%H:%M}  Atocha {at:%H:%M} (prog {sched[(t, ATO)]:%H:%M})  ->  N. Ministerios "
          f"{llega:%H:%M}  {marca}" if llega else f"  {sale:%H:%M}  Atocha {at:%H:%M}  sin enlace observado")
