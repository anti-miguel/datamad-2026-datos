r"""Comprueba la sensibilidad de la fiabilidad de Renfe a la medición de llegada.

Ejecutar desde la raíz, con la caché de refrescar_resultados/tabla_fiabilidad:
  python analisis/comprobar_tuneles.py D:\Temp\datamad_codex_2026-11-05
  python analisis/comprobar_tuneles.py D:\Temp\datamad_codex_2026-11-05 --solo-bruto
  python analisis/comprobar_tuneles.py --autoprueba

Lee mediante cargar.filas un día a la vez. Reproduce la primera llegada de
tabla_fiabilidad.extraer_renfe: primer STOPPED_AT o primera transición a otra
parada con separación GPS <=90 s, en orden de ts (no de consulta). No interpola
estaciones omitidas. Conserva la consulta y coordenadas de la lectura elegida
para comprobar antigüedad y distancia a la estación del GTFS. El muestreo TU y
los filtros son los de aquella tabla; la comparación del portal usa anuncios
de 3 a <25 min y antelación real >=0. Las sensibilidades son subconjuntos de
la misma llegada, no una verdad terreno alternativa.

Denominador de cobertura: pares (día, viaje, parada) anunciados por TU válido
y muestreado, NO todo el servicio programado. Incluye viajes fuera de horario
o sin correspondencia GTFS; no equivale a cancelaciones. La estandarización
compara anuncios con la misma mezcla de horizontes y líneas en soporte común.
No presupone que timestamp/posición del feed sea GPS físico independiente.
"""
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import sys
import zipfile

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import cargar

OBJETIVOS = {"18002", "17000"}
CONTROLES = {"18101": "túnel: Sol", "18001": "túnel: Recoletos",
             "18004": "superficie: Delicias", "60100": "superficie: Villaverde Bajo",
             "97201": "superficie: Ramón y Cajal", "10002": "superficie: Pozuelo",
             "18000": "mixto: Atocha"}
BINS = [3, 6, 10, 15, 25]


def estaciones():
    zpath = sorted(Path("datos/horarios_oficiales").glob("renfe_gtfs_*.zip"))[-1]
    with zipfile.ZipFile(zpath) as z:
        return {r["stop_id"].strip(): r for r in csv.DictReader(
            io.TextIOWrapper(z.open("stops.txt"), encoding="utf-8-sig", errors="replace"))}


def distancia(lat, lon, stop, nombres):
    if stop not in nombres or lat is None or lon is None:
        return float("nan")
    s = nombres[stop]
    la, lo, a, b = map(math.radians, [float(lat), float(lon), float(s["stop_lat"]), float(s["stop_lon"])])
    h = math.sin((a-la)/2)**2 + math.cos(la)*math.cos(a)*math.sin((b-lo)/2)**2
    return 6371000 * 2 * math.asin(min(1, math.sqrt(h)))


def llegadas(seq):
    """La clave deduplicada y el orden coinciden con tabla_fiabilidad.py."""
    puntos = {}
    for ts, stop, estado, consulta, metros, *inmovil in seq:
        puntos.setdefault((ts, stop, estado), (consulta, metros, inmovil[0] if inmovil else 0))
    orden = sorted(puntos)
    out = {}
    for i, (ts, stop, estado) in enumerate(orden):
        consulta, metros, inmovil = puntos[(ts, stop, estado)]
        if estado == "STOPPED_AT" and stop not in out:
            out[stop] = (ts, "STOPPED_AT", consulta-ts, metros, 0, inmovil)
        if i+1 < len(orden) and orden[i+1][1] != stop and stop not in out and orden[i+1][0]-ts <= 90:
            nxt = orden[i+1]
            age2 = puntos[nxt][0]-nxt[0]
            out[stop] = ((ts+nxt[0])/2, "transición", max(consulta-ts, age2), metros, nxt[0]-ts, inmovil)
    return out


def extraer_dia(dia, nombres):
    vp = defaultdict(list)
    candidatos = set()
    raw = defaultdict(Counter)
    coordenadas = {}
    for r in cargar.filas("renfe", dia):
        if r.get("err"):
            continue
        if r.get("k") == "vp":
            stop = str(r.get("stop", ""))
            c = raw[stop]
            c["n_vp"] += 1
            if not r.get("ts"):
                c["n_sin_ts"] += 1
                continue
            try:
                ts = int(r["ts"])
            except (TypeError, ValueError):
                c["n_sin_ts"] += 1
                continue
            edad = r["t"]-ts
            c["n_antiguo_90s"] += int(edad > 90)
            c["n_futuro"] += int(edad < -5)
            m = distancia(r.get("lat"), r.get("lon"), stop, nombres)
            c["n_lejos_500m"] += int(m > 500)
            xy = (r.get("lat"), r.get("lon"))
            anterior = coordenadas.get(r["trip"])
            inicio = anterior[1] if anterior is not None and anterior[0] == xy else r["t"]
            coordenadas[r["trip"]] = (xy, inicio)
            inmovil = r["t"]-inicio
            c["n_inmovil_90s_lejos_500m"] += int(inmovil > 90 and m > 500)
            vp[r["trip"]].append((ts, stop, r.get("st"), r["t"], m, inmovil))
        elif r.get("k") == "tu" and r["t"] % 180 < 30:
            for stop, delay, rel in r.get("stops", []):
                if delay is not None and abs(delay) < 10800 and rel != "SKIPPED":
                    candidatos.add((r["trip"], str(stop)))
    eventos = []
    encontrados = set()
    for trip, seq in vp.items():
        for stop, (real, metodo, edad, m, salto, inmovil) in llegadas(seq).items():
            eventos.append((dia, trip+"|"+stop, stop, real, metodo, edad, m, salto, inmovil))
            encontrados.add((trip, stop))
    for trip, stop in candidatos:
        raw[stop]["n_tu_viaje_parada"] += 1
        raw[stop]["n_tu_con_llegada_bruta"] += int((trip, stop) in encontrados)
        raw[stop]["n_tu_sin_vp_viaje"] += int(trip not in vp)
    return pd.DataFrame(eventos, columns=["dia", "llegada", "parada", "real", "metodo", "edad_s", "distancia_m", "salto_s", "inmovil_s"]), raw


def bruto(cache, dias, nombres):
    carpeta = cache / "tuneles_por_dia"
    carpeta.mkdir(parents=True, exist_ok=True)
    coordenadas_gtfs = {s: [r["stop_lat"], r["stop_lon"]] for s, r in nombres.items()}
    firma_gtfs = hashlib.sha256(json.dumps(coordenadas_gtfs, sort_keys=True).encode("utf-8")).hexdigest()
    eventos, resumen = [], []
    for dia in dias:
        p, meta = carpeta/(dia+".parquet"), carpeta/(dia+".json")
        entrada = Path(cargar.RAIZ)/"renfe"/(dia+".jsonl.gz")
        firma = [entrada.stat().st_size, entrada.stat().st_mtime_ns, 2, firma_gtfs]
        if p.exists() and meta.exists() and json.loads(meta.read_text(encoding="utf-8"))["firma"] == firma:
            e = pd.read_parquet(p)
            raw = json.loads(meta.read_text(encoding="utf-8"))["resumen"]
        else:
            e, raw = extraer_dia(dia, nombres)
            e.to_parquet(p, index=False)
            meta.write_text(json.dumps({"firma": firma, "resumen": raw}, ensure_ascii=False), encoding="utf-8")
        eventos.append(e)
        resumen.extend({"dia": dia, "parada": s, **c} for s, c in raw.items())
        print(f"Renfe {dia}: {len(e):,} llegadas brutas", flush=True)
    detalle = pd.DataFrame(resumen).fillna(0)
    for col in ["n_vp", "n_sin_ts", "n_antiguo_90s", "n_futuro", "n_lejos_500m", "n_inmovil_90s_lejos_500m",
                "n_tu_viaje_parada", "n_tu_con_llegada_bruta", "n_tu_sin_vp_viaje"]:
        if col not in detalle:
            detalle[col] = 0
    return pd.concat(eventos, ignore_index=True), detalle


def estadistica(g):
    diario = g.groupby("dia").ok.agg(["sum", "size"])
    if len(diario) >= 2:
        idx = np.random.default_rng(20261105).integers(0, len(diario), (1000, len(diario)))
        proporciones = diario["sum"].to_numpy()[idx].sum(axis=1)/diario["size"].to_numpy()[idx].sum(axis=1)
        bajo, alto = map(float, np.quantile(proporciones, [.025, .975]))
    else:
        bajo, alto = None, None
    return {"n_predicciones": len(g), "n_llegadas": g[["dia", "llegada"]].drop_duplicates().shape[0],
            "acierto": float(g.ok.mean()) if len(g) else None,
            "ic95_dias_bajo": bajo, "ic95_dias_alto": alto,
            "p_tarde_mas_2min": float((g.retraso>2).mean()) if len(g) else None,
            "p_antes_mas_2min": float((g.retraso < -2).mean()) if len(g) else None,
            "acierto_por_llegada": float(g.groupby(["dia", "llegada"]).ok.mean().mean()) if len(g) else None,
            "error_mediano_min": float(g.retraso.median()) if len(g) else None,
            "anuncio_mediano_min": float(g.anuncio.median()) if len(g) else None}


def estandarizar(local, referencia, keys):
    a = local.groupby(keys, observed=True).agg(p=("ok", "mean"), n=("ok", "size"))
    b = referencia.groupby(keys, observed=True).agg(p=("ok", "mean"), n=("ok", "size"))
    m = a.join(b, lsuffix="_local", rsuffix="_ref", how="inner")
    m = m[(m.n_local >= 30) & (m.n_ref >= 30)]
    if m.empty:
        return {"local": None, "referencia": None, "cobertura_local": 0, "cobertura_ref": 0}
    w = m.n_ref / m.n_ref.sum()
    return {"local": float((m.p_local*w).sum()), "referencia": float((m.p_ref*w).sum()),
            "cobertura_local": float(m.n_local.sum()/len(local)), "cobertura_ref": float(m.n_ref.sum()/len(referencia))}


def ejemplos(eventos):
    out = []
    for s in sorted(OBJETIVOS):
        candidatos = eventos[(eventos.parada == s) & (eventos.distancia_m > 1000) &
                              (eventos.metodo == "STOPPED_AT") & (eventos.inmovil_s > 90)]
        if candidatos.empty:
            continue
        e = candidatos.sort_values(["dia", "real"]).iloc[0]
        trip = e.llegada.rsplit("|", 1)[0]
        filas = [r for r in cargar.filas("renfe", e.dia) if r.get("k") == "vp" and
                 r.get("trip") == trip and r.get("ts") and abs(int(r["ts"])-e.real) <= 120]
        out.append({"fuente": f"datos/renfe/{e.dia}.jsonl.gz", "dia": e.dia, "trip": trip,
                    "parada": s, "real_usado": float(e.real), "distancia_m": float(e.distancia_m),
                    "edad_s": float(e.edad_s), "inmovil_s": float(e.inmovil_s), "filas": filas[:12]})
    return out


def coinciden_llegadas(observadas, calculadas):
    return np.allclose(observadas, calculadas, atol=.01, rtol=0)


def analizar(cache, eventos, raw, nombres, corte):
    d = pd.read_parquet(cache/"predicciones.parquet", filters=[("red", "==", "renfe"), ("dia", "<=", corte)])
    d["parada"] = d.parada.astype(str)
    d["anuncio"] = d.antel-d.retraso
    d = d[(d.antel >= 0) & (d.anuncio >= 3) & (d.anuncio < 25)].copy()
    d["ok"] = d.retraso.abs() <= 2
    d["horizonte"] = pd.cut(d.anuncio, BINS, right=False).astype(str)
    e = eventos.drop(columns="parada")
    d = d.merge(e, on=["dia", "llegada"], how="left", validate="many_to_one")
    if d.metodo.isna().any():
        raise ValueError("Hay llegadas de la caché sin reconstrucción bruta: revisar fechas/firma de la caché")
    if not coinciden_llegadas(d.real, d.t+d.antel*60):
        raise ValueError("Las llegadas reconstruidas no coinciden con la caché de fiabilidad")
    r = raw.groupby("parada").sum(numeric_only=True)
    registros = []
    escenarios = {"base": lambda g: np.ones(len(g), bool),
                  "edad_30s": lambda g: g.edad_s.between(-5, 30),
                  "edad_90s": lambda g: g.edad_s.between(-5, 90),
                  "coordenadas_sin_cambio_90s": lambda g: g.inmovil_s <= 90,
                  "edad_90s_cerca_300m": lambda g: g.edad_s.between(-5, 90) & (g.distancia_m <= 300),
                  "parado_edad_90s_cerca_300m": lambda g: g.edad_s.between(-5, 90) & (g.distancia_m <= 300) & (g.metodo == "STOPPED_AT")}
    for s, g in d.groupby("parada"):
        for escenario, mascara in escenarios.items():
            registros.append({"parada": s, "nombre": nombres.get(s, {}).get("stop_name", s),
                              "escenario": escenario, **estadistica(g[mascara(g)])})
    tasas = pd.DataFrame(registros)
    medidas = eventos.groupby("parada").agg(n_llegadas_brutas=("llegada", "size"),
                edad_mediana_s=("edad_s", "median"), edad_p95_s=("edad_s", lambda x:x.quantile(.95)),
                p_llegadas_antiguas_90s=("edad_s", lambda x:(x>90).mean()),
                p_llegadas_parado=("metodo", lambda x:(x=="STOPPED_AT").mean()),
                p_llegadas_inmovil_90s=("inmovil_s", lambda x:(x>90).mean()),
                distancia_mediana_m=("distancia_m", "median"),
                p_llegadas_lejos_500m=("distancia_m", lambda x:(x>500).mean()))
    r = r.join(medidas)
    r["p_tu_con_llegada_bruta"] = r.n_tu_con_llegada_bruta/r.n_tu_viaje_parada
    for col in ["n_sin_ts", "n_antiguo_90s", "n_futuro", "n_lejos_500m", "n_inmovil_90s_lejos_500m"]:
        r["p_"+col[2:]] = r[col]/r.n_vp
    comparaciones = {}
    for s in sorted(OBJETIVOS):
        g, ref = d[d.parada == s], d[d.parada != s]
        comparaciones[s] = {"horizonte": estandarizar(g, ref, ["horizonte"]),
                            "linea_horizonte": estandarizar(g, ref, ["linea", "horizonte"])}
    res = Path("analisis/resultados")
    res.mkdir(exist_ok=True)
    pref = res/f"tuneles_{corte}"
    tasas.to_csv(str(pref)+"_sensibilidad.csv", index=False, encoding="utf-8")
    r.reset_index().to_csv(str(pref)+"_medicion.csv", index=False, encoding="utf-8")
    raw.to_csv(str(pref)+"_diario.csv", index=False, encoding="utf-8")
    mezcla = d.groupby(["parada", "linea", "horizonte"], observed=True).agg(n=("ok", "size"), acierto=("ok", "mean")).reset_index()
    mezcla.to_csv(str(pref)+"_anuncios.csv", index=False, encoding="utf-8")
    meta = {"corte": corte, "dias": int(raw.dia.nunique()), "muestra": estadistica(d),
            "estandarizacion": comparaciones, "validacion_llegadas_cache": "coincidencia con tolerancia absoluta 0,01 s (rtol=0)",
            "error_maximo_llegadas_s": float(np.max(np.abs(d.real-(d.t+d.antel*60)))),
            "veredicto": "inferencia: no se identifica causalmente cuánto del error procede de la medición o del servicio"}
    Path(str(pref)+".json").write_text(json.dumps(meta, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    muestra = ejemplos(eventos)
    Path(str(pref)+"_ejemplos.json").write_text(json.dumps(muestra, ensure_ascii=False, indent=2), encoding="utf-8")
    texto = informe(d, tasas, r, comparaciones, corte, muestra)
    Path(str(pref)+".md").write_text(texto, encoding="utf-8")
    print(texto)


def informe(d, tasas, r, comp, corte, muestra):
    p = lambda x: "sin muestra" if x is None or pd.isna(x) else f"{x:.1%}"
    out = [f"# Comprobación de túneles: corte {corte}", "",
           "**Veredicto (inferencia):** con estos feeds no se puede atribuir causalmente la baja fiabilidad a túneles ni a peor servicio. La selección de llegadas observables y el patrón de anuncios importan. Mantener la cautela del README sobre las dos estaciones; no presentar sus tasas como puntualidad real.", "",
           "**Confirmado en código:** la tabla toma ts del feed, sin filtrar su antigüedad ni comprobar la distancia a la estación. Usa el primer STOPPED_AT o el punto medio de una transición entre stop_id distintos si sus ts distan ≤90 s; no reconstruye estaciones omitidas en túneles. GPS/ts es la descripción del catálogo, no una garantía de independencia física del dato. Los retrasos ±86400 s quedan fuera por el filtro abs(delay)<10800.", "",
           f"**Comprobado ejecutando:** se reconstruyeron por día las llegadas y coinciden con la caché de fiabilidad a 0,01 s. Anuncios de 3 a <25 min: {len(d):,} predicciones, {d[['dia','llegada']].drop_duplicates().shape[0]:,} llegadas, acierto global por predicción {p(d.ok.mean())}. Este global de todas las estaciones no es el 64,6% ponderado por viajeros de las 18 estaciones del portal.", "",
           "La comparación se limita a los anuncios que tienen una llegada reconstruida, horario y filtros válidos. Cobertura TU: pares día/viaje/parada anunciados que tienen llegada bruta; no proporción del servicio realizado. Las tasas de antigüedad por fila pueden sobrerrepresentar vehículos congelados.", "",
           "Las celdas de sensibilidad muestran acierto y número de llegadas retenidas. El filtro de edad admite -5 s ≤ t-ts ≤ límite, excluyendo también marcas adelantadas más de 5 s. El CSV incluye IC95 por remuestreo de días (1.000 réplicas, semilla fija), que recoge variación diaria pero no el sesgo sistemático de la medición; no se calcula con menos de dos días.", "",
           "| Estación | Predicciones / llegadas | Base | Edad ≤30 s | Edad ≤90 s | Además ≤300 m | Además STOPPED_AT |", "|---|---:|---:|---:|---:|---:|---:|"]
    for s in ["18002", "17000", *CONTROLES]:
        t = tasas[tasas.parada == s].set_index("escenario")
        if t.empty:
            continue
        a = t.loc["base"]
        etiqueta = str(a.nombre).replace("�", "?")
        if s in CONTROLES:
            etiqueta += " ("+CONTROLES[s]+")"
        out.append(f"| {etiqueta} | {a.n_predicciones:,} / {a.n_llegadas:,} | "+" | ".join(f"{p(t.loc[x].acierto)} ({t.loc[x].n_llegadas:,})" for x in ["base","edad_30s","edad_90s","edad_90s_cerca_300m","parado_edad_90s_cerca_300m"])+" |")
    pequenas = tasas[(tasas.escenario == "parado_edad_90s_cerca_300m") &
                     tasas.parada.isin(CONTROLES) & (tasas.n_llegadas < 30)]
    if not pequenas.empty:
        detalle = "; ".join(f"{x.nombre}: {x.n_llegadas:,} llegadas, acierto {p(x.acierto)}" for x in pequenas.itertuples())
        out += ["", "Muestra pequeña en el escenario más estricto: "+detalle+". Estas tasas no permiten extrapolar al servicio."]
    out += ["", "**Inferencia (clasificación de controles):** Sol y Recoletos se proponen como estaciones subterráneas; Delicias, Villaverde Bajo, Ramón y Cajal y Pozuelo como controles de superficie, y Atocha como mixto. Esta clasificación geográfica no se ha cotejado con un inventario de infraestructura; no es una variable causal validada.", "",
            "| Estación | VP sin ts | VP ts >90 s | TU con llegada bruta | Llegadas STOPPED_AT | Llegadas >500 m | Edad p95 (s) |", "|---|---:|---:|---:|---:|---:|---:|"]
    for s in ["18002", "17000", *CONTROLES]:
        if s not in r.index:
            continue
        q = r.loc[s]
        nombre = tasas[tasas.parada == s].nombre.iloc[0] if (tasas.parada == s).any() else s
        out.append(f"| {nombre} | {p(q.p_sin_ts)} | {p(q.p_antiguo_90s)} | {p(q.p_tu_con_llegada_bruta)} ({int(q.n_tu_viaje_parada):,} pares) | {p(q.p_llegadas_parado)} | {p(q.p_llegadas_lejos_500m)} | {q.edad_p95_s:.0f} |")
    out += ["", "**Comprobado ejecutando: repetición de anuncios.** La tabla histórica pondera cada anuncio; un viaje con más anuncios pesa más. Promediar primero los aciertos de cada llegada y dar después el mismo peso a cada llegada es otra pregunta y produce:", ""]
    for s in sorted(OBJETIVOS):
        q = tasas[(tasas.parada == s) & (tasas.escenario == "base")].iloc[0]
        out.append(f"- {s}: {p(q.acierto)} por anuncio frente a {p(q.acierto_por_llegada)} dando igual peso a cada llegada; {q.n_predicciones/q.n_llegadas:.2f} anuncios por llegada en promedio.")
    out += ["", "No se sustituye la tasa histórica por esta alternativa: cambia la unidad de ponderación y no resuelve la llegada física."]
    out += ["", "**Comprobado ejecutando: mezcla de anuncios y líneas.** Se asigna a cada estación la mezcla de la referencia (todas las demás estaciones) en celdas comunes con ≥30 anuncios en ambos lados. Los CSV guardan tamaños de cada celda; observaciones repetidas del mismo tren no son independientes.", ""]
    for s, c in comp.items():
        out.append(f"- {s}: "+"; ".join(f"{k}: estación {p(v['local'])}, referencia {p(v['referencia'])}, soporte {p(v['cobertura_local'])} local / {p(v['cobertura_ref'])} referencia" for k,v in c.items())+".")
    out += ["", "**Comprobado ejecutando: coordenadas inmóviles.** Se mide cuánto tiempo llevan exactamente iguales lat/lon del viaje desde la primera consulta del día con esas coordenadas. No es antigüedad GPS demostrada: un tren puede estar físicamente parado. Se reinicia al cambiar de coordenadas y al empezar el día, por lo que es una cota inferior del tiempo sin cambio.", ""]
    for s in sorted(OBJETIVOS):
        q = r.loc[s]
        t = tasas[(tasas.parada == s) & (tasas.escenario == "coordenadas_sin_cambio_90s")].iloc[0]
        out.append(f"- {s}: {p(q.p_inmovil_90s_lejos_500m)} de las VP tienen coordenadas sin cambio >90 s y están a >500 m del stop_id; {p(q.p_llegadas_inmovil_90s)} de llegadas brutas tienen coordenadas sin cambio >90 s. Reteniendo coordenadas sin cambio ≤90 s: acierto {p(t.acierto)}, {t.n_llegadas:,} llegadas.")
    for e in muestra:
        out.append(f"- Ejemplo {e['fuente']}, viaje {e['trip']}, estación {e['parada']}: la lectura usada como STOPPED_AT tiene ts {e['real_usado']:.0f}, edad {e['edad_s']:.0f} s, coordenadas a {e['distancia_m']:.0f} m del centro GTFS y sin cambiar al menos {e['inmovil_s']:.0f} s. Las filas originales de ±120 s están en el JSON de ejemplos; prueban una discrepancia entre estado y coordenadas, sin decidir cuál representa mejor el paso real.")
    out += ["", "**Límites (inferencia):** filtrar coordenadas o edad cambia la muestra y no demuestra que el resto de llegadas sea correcto. Las llegadas por transición pueden ser anteriores al paso real si stop_id indica destino próximo. STOPPED_AT y una posición cercana también pueden proceder de estimación del operador. No hay observación independiente de paso, inventario de túneles ni experimento que separe medición, información publicada y servicio. No se han imputado llegadas faltantes ni corregido las tasas mediante un supuesto causal.", "",
            "**Reproducción:** `python analisis/comprobar_tuneles.py <carpeta de predicciones.parquet>`. La caché bruta auxiliar se guarda fuera del repositorio, por día y con firma de tamaño/mtime del fichero fuente y SHA256 de las coordenadas GTFS. Salidas: sensibilidad, medición, diario, anuncios, JSON, ejemplos y este informe. No se lee datos/redes ni se accede a la red."]
    return "\n".join(out)+"\n"


def autoprueba():
    from unittest.mock import patch

    a = llegadas([(100, "a", "IN_TRANSIT_TO", 500, 1000), (160, "b", "STOPPED_AT", 170, 10)])
    assert a["a"][:3] == (130, "transición", 400)
    assert a["b"][:3] == (160, "STOPPED_AT", 10)
    assert "a" not in llegadas([(100, "a", "IN_TRANSIT_TO", 110, 1), (191, "b", "STOPPED_AT", 200, 1)])
    a = llegadas([(100, "a", "IN_TRANSIT_TO", 110, 1), (150, "b", "IN_TRANSIT_TO", 160, 1), (200, "a", "STOPPED_AT", 210, 1)])
    assert a["a"][0] == 125  # La transición inicial no se sustituye por una parada posterior.
    assert llegadas([(100,"a","STOPPED_AT",500,1),(100,"a","STOPPED_AT",530,1)])["a"][2] == 400
    registros = [{"k": "vp", "trip": "x", "stop": "a", "st": "STOPPED_AT", "t": t,
                  "ts": ts, "lat": 40., "lon": -3.} for t, ts in [(100, "90"), (200, "190"), (230, None)]]
    registros.append({"k": "tu", "trip": "x", "t": 200, "stops": [["a", 0, None]]})
    with patch.object(cargar, "filas", return_value=iter(registros)):
        e, r = extraer_dia("prueba", {"a": {"stop_lat": "41", "stop_lon": "-3"}})
    assert len(e) == 1 and r["a"]["n_tu_con_llegada_bruta"] == 1
    assert r["a"]["n_sin_ts"] == 1 and r["a"]["n_inmovil_90s_lejos_500m"] == 1
    assert coinciden_llegadas([1790000000.], [1790000000.])
    assert not coinciden_llegadas([1790000000.], [1790000001.])
    print("Autoprueba: transición, hueco >90 s, prioridad, deduplicación, coordenadas inmóviles y tolerancia absoluta de 0,01 s comprobadas (6 casos).")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cache", nargs="?", type=Path)
    ap.add_argument("--hasta")
    ap.add_argument("--solo-bruto", action="store_true")
    ap.add_argument("--autoprueba", action="store_true")
    args = ap.parse_args()
    if args.autoprueba:
        autoprueba()
        return
    if args.cache is None:
        ap.error("hace falta la carpeta de caché")
    dias = [x for x in cargar.dias("renfe") if args.hasta is None or x <= args.hasta]
    nombres = estaciones()
    eventos, raw = bruto(args.cache, dias, nombres)
    if not args.solo_bruto:
        analizar(args.cache, eventos, raw, nombres, dias[-1])


if __name__ == "__main__":
    main()
