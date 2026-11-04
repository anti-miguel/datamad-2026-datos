"""El 104 en su cabecera (Mar de Cristal, parada 5848) y el interurbano 212.

104: la salida real de cada autobús se mide en la parada siguiente (4900, Arequipa - Emigrantes): última consulta en
que aparecía, si estaba a <=400 s (t + estimación). Para cada consulta de la cabecera se compara lo que decía la app
(«el próximo sale en X min» y qué autobús) con el autobús que salió de verdad a continuación.
212: si la hora anunciada de un mismo viaje (codIssue) cambia entre consultas, hay tiempo real; si no, es horario.
Uso: python analisis_104_212.py AAAA-MM-DD [AAAA-MM-DD ...]   (laborables)
"""
import gzip, json, sys, time, collections as C
import pandas as pd

CABECERA, SIGUIENTE = "5848", "4900"
TRAYECTO = 60  # s de 5848 a 4900 según el GTFS de la EMT


def hora(t):
    lt = time.localtime(t)
    return lt.tm_hour + lt.tm_min / 60


filas = []
pasos = []
for dia in sys.argv[1:]:
    cab, sig = [], C.defaultdict(list)
    for l in gzip.open(f"datos/emt/{dia}.jsonl.gz", "rt", encoding="utf-8"):
        r = json.loads(l)
        if r.get("s") == CABECERA and "a" in r:
            cab.append((r["t"], [(a[1], a[2], a[3]) for a in r["a"] if a[0] == "104" and a[2] not in (888888, 999999)]))
        elif r.get("s") == SIGUIENTE and "a" in r:
            for a in r["a"]:
                if a[0] == "104" and a[2] not in (888888, 999999):
                    sig[a[1]].append((r["t"], a[2], a[3] or 0))
    # salidas reales: paso por 4900 menos el trayecto
    salidas = []
    for bus, seq in sig.items():
        seq.sort()
        visita = [seq[0]]
        for o in seq[1:] + [None]:
            if o is not None and o[0] - visita[-1][0] <= 900:
                visita.append(o)
                continue
            t, est, dist = visita[-1]
            if est <= 400:  # desaparece ya cerca; con consultas cada 3 min el criterio estricto pierde ~20 % de salidas
                salidas.append((t + est - TRAYECTO, bus))
            if o is not None:
                visita = [o]
    salidas.sort()
    pasos += [(dia, s, b) for s, b in salidas]
    for t, lista in sorted(cab):
        if not lista or not 7 <= hora(t) < 21:
            continue
        prox = min(lista, key=lambda x: x[1])
        real = next(((s, b) for s, b in salidas if s >= t + 90), None)  # las que salen en <90 s pueden haber salido ya
        if real is None or real[0] - t > 3600:
            continue
        filas.append(dict(dia=dia, t=t, anunciado=prox[1] / 60, real=(real[0] - t) / 60,
                          mismo_bus=real[1] == prox[0], estaba=real[1] in {b for b, _e, _d in lista},
                          en_cabecera=prox[2] <= 50))
d = pd.DataFrame(filas)
d["dif"] = d.real - d.anunciado  # negativo: salió antes de lo anunciado
print(f"104 en Mar de Cristal, {len(sys.argv) - 1} laborables, 7-21 h: {len(d)} consultas de la app comparadas "
      f"con {len(pasos)} salidas reales")
print(f"  el autobús que sale a continuación es el que anunciaba la app: {d.mismo_bus.mean():.0%}; "
      f"no aparecía en la lista: {(~d.estaba).mean():.0%}")
for nombre, g in [("autobús ya parado en la cabecera", d[d.en_cabecera]), ("autobús todavía llegando", d[~d.en_cabecera])]:
    print(f"  {nombre} ({len(g)}): sale a ±2 min de lo anunciado {(g.dif.abs() <= 2).mean():.0%}, "
          f"sale >5 min ANTES {(g.dif < -5).mean():.0%}, sale >5 min DESPUÉS {(g.dif > 5).mean():.0%}")
lejos = d[d.anunciado >= 15]
print(f"  cuando la app dice 15 min o más ({len(lejos)} consultas): sale uno >5 min antes en "
      f"{(lejos.dif < -5).mean():.0%} de los casos; mediana de lo que se adelanta: {lejos.dif.median():+.1f} min")
ej = d[(d.anunciado >= 20) & (d.dif < -10)].head(3)
for _, e in ej.iterrows():
    print(f"    p. ej. {e.dia} {time.strftime('%H:%M', time.localtime(e.t))}: la app decía {e.anunciado:.0f} min, "
          f"salió uno a los {e.real:.0f} min")
# intervalos reales entre salidas
p = pd.DataFrame(pasos, columns=["dia", "s", "bus"]).sort_values(["dia", "s"])
p["intervalo"] = p.groupby("dia").s.diff() / 60
p = p[p.s.map(lambda t: 7 <= hora(t) < 21) & p.intervalo.between(0.5, 60)]
print(f"  intervalo real entre salidas (7-21 h): mediana {p.intervalo.median():.0f} min, "
      f"p10 {p.intervalo.quantile(.1):.0f}, p90 {p.intervalo.quantile(.9):.0f} min; "
      f"esperas >20 min: {(p.intervalo > 20).mean():.0%}\n")

# ---------- 212 ----------
pares = C.Counter()
saltos = []
for dia in sys.argv[1:]:
    try:
        f = gzip.open(f"datos/crtm/{dia}.jsonl.gz", "rt", encoding="utf-8")
    except FileNotFoundError:
        continue
    previa = {}
    for l in f:
        r = json.loads(l)
        if r.get("m") != "interurbanos" or "a" not in r:
            continue
        ahora = {cod: ts for lin, _d, _dest, ts, cod in r["a"] if lin == "212" and ts and ts > r["t"]}
        t0, antes = previa.get(r["s"], (0, {}))
        if r["t"] - t0 <= 120:  # consultas consecutivas de la misma parada
            for cod, ts in ahora.items():
                if cod in antes and abs(ts - antes[cod]) < 3600:
                    cambia = abs(ts - antes[cod]) > 30
                    pares[cambia] += 1
                    if cambia:
                        saltos.append((ts - antes[cod]) / 60)
        previa[r["s"]] = (r["t"], ahora)
if pares:
    print(f"212: {sum(pares.values())} comparaciones de la hora anunciada de un mismo viaje entre consultas seguidas (1 min)")
    print(f"  la hora cambia en {pares[True] / sum(pares.values()):.2%} de ellas"
          + (f" (mediana del cambio {pd.Series(saltos).median():+.1f} min)" if saltos else ""))
