"""Autobuses que «aparecen de la nada» y estimaciones que saltan, en los datos de la API de la EMT.

Aparición: un autobús que no estaba en la consulta anterior de esa parada (hecha <=4 min antes y con respuesta)
y aparece ya a <=8 min. Si la consulta anterior anunciaba como primer autobús de esa línea uno a más de 8 min,
la aparición cambia la decisión de quien espera («el siguiente en 35» pasa a «uno en 4»).
Salto: el mismo autobús, entre dos consultas seguidas, retrasa su llegada prevista más de 5 min.
Uso: python analisis_emt_sorpresas.py datos/emt/2026-10-05.jsonl.gz [...]
"""
import gzip, json, sys, collections as C

for fich in sys.argv[1:]:
    filas = sorted((json.loads(x) for x in gzip.open(fich, "rt", encoding="utf-8")), key=lambda r: r["t"])
    previa = {}
    por_linea = C.defaultdict(lambda: [0, 0, 0])  # apariciones, que cambian la decisión, consultas con la línea
    saltos, comparaciones, ejemplos = 0, 0, []
    for r in filas:
        if "a" not in r:
            continue
        ahora = C.defaultdict(dict)
        for lin, bus, est, dist, *_ in r["a"]:
            if bus and est is not None and est not in (888888, 999999):
                ahora[lin][bus] = r["t"] + est
        ant = previa.get(r["s"])
        if ant and r["t"] - ant[0] <= 240:
            for lin, buses in ahora.items():
                antes = ant[1].get(lin, {})
                por_linea[lin][2] += 1
                for bus, llega in buses.items():
                    if bus in antes:
                        comparaciones += 1
                        if llega - antes[bus] > 300:
                            saltos += 1
                    elif llega - r["t"] <= 480:
                        por_linea[lin][0] += 1
                        primero = min(antes.values(), default=None)
                        if primero is None or primero - ant[0] > 480:
                            por_linea[lin][1] += 1
                            if len(ejemplos) < 5:
                                ejemplos.append((r["s"], lin, (primero - ant[0]) // 60 if primero else None,
                                                 (llega - r["t"]) // 60, r["t"]))
        previa[r["s"]] = (r["t"], ahora)
    ap = sum(v[0] for v in por_linea.values())
    cambia = sum(v[1] for v in por_linea.values())
    cons = sum(v[2] for v in por_linea.values())
    print(f"{fich[-19:-9]}: {ap} autobuses aparecen ya a <=8 min sin estar 3 min antes "
          f"({cambia} de ellos cuando el primero anunciado estaba a >8 min o no había ninguno); "
          f"1 de cada {cons // max(cambia, 1)} consultas de una línea. "
          f"Saltos de >5 min del mismo autobús entre consultas: {saltos} de {comparaciones} ({saltos / max(comparaciones, 1):.1%})")
    peores = sorted(por_linea.items(), key=lambda kv: -kv[1][1] / max(kv[1][2], 1))[:6]
    print("   líneas con más apariciones que cambian la decisión:",
          ", ".join(f"{l} ({v[1]} de {v[2]} consultas)" for l, v in peores))
    import time
    for s, l, antes, ahora_min, t in ejemplos[:3]:
        print(f"   p. ej. parada {s}, línea {l}, {time.strftime('%H:%M', time.localtime(t))}: "
              f"3 min antes {'nada' if antes is None else f'primero en {antes} min'} -> ahora uno en {ahora_min} min")
