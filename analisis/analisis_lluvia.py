"""¿Van más lentos los autobuses de la EMT cuando llueve?

Velocidad real: el mismo autobús en dos consultas seguidas de una parada (3 min) acercándose a ella; la distancia
que le queda (DistanceBus, por la ruta) baja X metros en Y segundos. Solo tramos de 200-4000 m y que avanzan.
Lluvia: Open-Meteo, precipitación horaria en Madrid (lluvia_openmeteo.json). Hora lluviosa: >=0,2 mm en esa hora.
Se compara cada hora del día con la misma hora de los laborables secos, para no confundir lluvia con hora punta.
Uso: python analisis_lluvia.py
"""
import gzip, json, time, collections as C
import pandas as pd

LLUVIOSOS = ["2026-10-06", "2026-10-07"]
SECOS = ["2026-10-08", "2026-10-09", "2026-10-13"]
h = json.load(open("datos/meteo/lluvia_horaria_2026-09-23_a_10-13.json"))["hourly"]
lluvia = dict(zip(h["time"], h["precipitation"]))  # "2026-10-06T08:00" -> mm


def tramos(dia):
    previa = {}
    out = []
    for l in gzip.open(f"datos/emt/{dia}.jsonl.gz", "rt", encoding="utf-8"):
        r = json.loads(l)
        if "a" not in r:
            continue
        ahora = {}
        for lin, bus, est, dist, *_ in r["a"]:
            if bus and dist is not None and est not in (888888, 999999):
                ahora[(lin, bus)] = dist
        t0, antes = previa.get(r["s"], (0, {}))
        dt = r["t"] - t0
        if 150 <= dt <= 210:
            for k, d1 in ahora.items():
                d0 = antes.get(k)
                if d0 is not None and 200 <= d1 < d0 <= 4000:
                    lt = time.localtime(t0)
                    out.append(dict(dia=dia, hora=lt.tm_hour, linea=k[0], v=(d0 - d1) / dt * 3.6,
                                    mm=lluvia.get(time.strftime("%Y-%m-%dT%H:00", lt), 0) or 0))
        previa[r["s"]] = (r["t"], ahora)
    return out


d = pd.DataFrame([x for dia in LLUVIOSOS + SECOS for x in tramos(dia)])
d = d[(d.hora >= 7) & (d.hora < 22) & d.v.between(1, 60)]
d["tipo"] = d.apply(lambda x: "lluvia" if x.dia in LLUVIOSOS and x.mm >= 0.2 else
                    ("seco" if x.dia in SECOS else "día de lluvia, hora seca"), axis=1)
print(f"{len(d)} tramos medidos (7-22 h). Velocidad mediana del autobús acercándose a la parada (km/h):")
t = d.groupby(["hora", "tipo"]).v.median().unstack()
n = d.groupby(["hora", "tipo"]).size().unstack()
t["dif lluvia vs seco"] = (t["lluvia"] / t["seco"] - 1) * 100
print(pd.concat([t.round(1), n.add_prefix("n ")], axis=1).to_string())
pareado = t.dropna(subset=["lluvia", "seco"])
print(f"\nHoras con lluvia comparables: {len(pareado)}. Diferencia mediana de velocidad: "
      f"{pareado['dif lluvia vs seco'].median():+.0f} %")
for nombre, g in d.groupby("tipo"):
    print(f"  {nombre}: mediana {g.v.median():.1f} km/h ({len(g)} tramos)")
# por intensidad
ll = d[d.tipo == "lluvia"].copy()
ll["intensidad"] = pd.cut(ll.mm, [0.19, 1, 3, 100], labels=["0,2-1 mm/h", "1-3 mm/h", ">3 mm/h"])
base = d[d.tipo == "seco"].groupby("hora").v.median()
ll["rel"] = ll.apply(lambda x: x.v / base.get(x.hora, float("nan")) - 1, axis=1) * 100
print("\nSegún lo fuerte que llueve (velocidad respecto a la misma hora en seco):")
print(ll.groupby("intensidad", observed=True).rel.agg(tramos="size", mediana="median").round(0).to_string())
# el 104
b = d[d.linea == "104"]
print("\n104:", b.groupby("tipo").v.agg(tramos="size", mediana="median").round(1).to_string())
