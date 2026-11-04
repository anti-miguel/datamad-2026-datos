"""¿Se cumple el "llega en X min"? EMT (API oficial, autobús a autobús) y Metro (widget del CRTM).

EMT: cada autobús se sigue por (parada, línea, nº de autobús). Su llegada real se toma de la última consulta en
que estaba a <=120 s y <=600 m de la parada (t + estimación; a esa distancia el error es de segundos).
Metro: sin identificador de tren; cada tren anunciado se sigue entre consultas por línea, destino y hora más
cercana (<4 min). Su llegada real es el punto medio entre la última consulta en que aparece y la primera en que
ya no (±30 s).
Uso: python analisis_emt_metro.py datos/emt/2026-10-05.jsonl.gz datos/crtm/2026-10-05.jsonl.gz
"""
import gzip, json, sys, time, collections as C
import pandas as pd

EMT, METRO = sys.argv[1], sys.argv[2]
BINS = [0, 3, 6, 10, 15, 25]
ETQ = ["0-3 min", "3-6 min", "6-10 min", "10-15 min", "15-25 min"]


def tabla(err):
    d = pd.DataFrame(err, columns=["antel", "error", "hora"])
    d["bin"] = pd.cut(d.antel, BINS, right=False, labels=ETQ)
    g = d.groupby("bin", observed=True).error
    return pd.DataFrame({"predicciones": g.size(), "error mediano (min)": g.median(),
                         "% a ±1 min": g.apply(lambda s: (s.abs() <= 1).mean() * 100),
                         "% a ±2 min": g.apply(lambda s: (s.abs() <= 2).mean() * 100),
                         "error abs p90": g.apply(lambda s: s.abs().quantile(.9))}).round(1)


def franja(t):
    h = time.localtime(t).tm_hour + time.localtime(t).tm_min / 60
    return "punta mañana" if 7 <= h < 9.5 else "punta tarde" if 17 <= h < 20 else "resto"


# ---------- EMT ----------
L = [json.loads(x) for x in gzip.open(EMT, "rt", encoding="utf-8")]
obs = C.defaultdict(list)
for r in L:
    for lin, bus, est, dist, lon, lat, tipo, dest in r.get("a", []):
        if bus and est is not None and est not in (888888, 999999):
            obs[(r["s"], lin, bus)].append((r["t"], est, dist or 0))
err, llegadas, sin_cierre = [], 0, 0
for k, seq in obs.items():
    seq.sort()
    visita = [seq[0]]
    for o in seq[1:] + [None]:  # parte en visitas cuando el autobús desaparece >15 min
        if o is not None and o[0] - visita[-1][0] <= 900:
            visita.append(o)
            continue
        fin = visita[-1]
        if fin[1] <= 120 and fin[2] <= 600:
            real = fin[0] + fin[1]
            llegadas += 1
            for t, est, _d in visita[:-1]:
                err.append(((real - t) / 60, (t + est - real) / 60, franja(t)))
        else:
            sin_cierre += 1
        if o is not None:
            visita = [o]
print(f"EMT ({EMT[-19:-9]}): {llegadas} llegadas de autobús reconstruidas "
      f"({sin_cierre} visitas sin cerrar: el autobús pasó entre dos consultas)")
print("¿Acierta el 'llega en X min'? (error = previsto - real; negativo = llegó más tarde de lo anunciado)")
print(tabla(err).to_string(), "\n")
e = pd.DataFrame(err, columns=["antel", "error", "franja"])
e = e[(e.antel >= 6) & (e.antel < 15)]
print("  con 6-15 min de antelación, por franja:",
      {f: f"{(g.error.abs() <= 2).mean():.0%} a ±2 min, mediana {g.error.median():+.1f}" for f, g in e.groupby("franja")}, "\n")

# ---------- METRO ----------
L = [json.loads(x) for x in gzip.open(METRO, "rt", encoding="utf-8")]
por_est = C.defaultdict(list)
for r in L:
    if r.get("m") == "metro" and "a" in r:
        g = C.defaultdict(list)
        for lin, d, dest, ts, _ in r["a"]:
            if ts:
                g[(lin, dest)].append(ts)
        por_est[r["s"]].append((r["t"], g))
err, llegadas, esperas = [], [], C.defaultdict(list)
for s, seq in por_est.items():
    seq.sort(key=lambda x: x[0])
    vivos = {}  # (línea, destino, id) -> lista de (t_consulta, previsto)
    nid = 0
    for i, (t, g) in enumerate(seq):
        nuevos = {}
        for k, previstos in g.items():
            libres = {key: v for key, v in vivos.items() if key[:2] == k}
            for p in sorted(previstos):
                cand = min(libres, key=lambda key: abs(libres[key][-1][1] - p), default=None)
                if cand is not None and abs(libres[cand][-1][1] - p) < 240:
                    nuevos[cand] = libres.pop(cand) + [(t, p)]
                else:
                    nid += 1
                    nuevos[k + (nid,)] = [(t, p)]
        for key, hist in vivos.items():
            if key not in nuevos and i > 0 and t - seq[i - 1][0] <= 90:
                real = (seq[i - 1][0] + t) / 2  # desapareció entre la consulta anterior y esta
                if hist[-1][1] - seq[i - 1][0] < 300:  # descarta trenes que salen de la lista lejos (corte de horizonte)
                    llegadas.append((s, key[0], key[1], real))
                    for tc, p in hist:
                        err.append(((real - tc) / 60, (p - real) / 60, franja(tc)))
        vivos = nuevos
print(f"METRO ({METRO[-19:-9]}): {len(llegadas)} llegadas de tren reconstruidas en {len(por_est)} estaciones")
print("¿Acierta el 'llega en X min' del Metro?")
print(tabla(err).to_string(), "\n")
# intervalo real entre trenes (misma estación, línea y destino), en hora punta de mañana
ll = pd.DataFrame(llegadas, columns=["est", "linea", "dest", "t"]).sort_values("t")
ll["espera"] = ll.groupby(["est", "linea", "dest"]).t.diff() / 60
ll["franja"] = ll.t.map(lambda t: franja(int(t)))
pm = ll[(ll.franja == "punta mañana") & ll.espera.between(0.5, 30)]
res = pm.groupby("linea").espera.agg(trenes="size", intervalo_mediano="median",
                                     p90=lambda s: s.quantile(.9),
                                     pct_huecos=lambda s: (s > 1.5 * s.median()).mean() * 100).round(1)
print("Intervalo real entre trenes en punta de mañana (min) y % de huecos >1,5× el intervalo mediano:")
print(res.sort_values("trenes", ascending=False).to_string())
