"""Ventana de confianza de los interurbanos: "la app dice X min; 8 de cada 10 veces llega entre A y B".

El panel del Consorcio no publica la llegada real. Se aproxima con la última hora anunciada para cada viaje
(cod_viaje) justo antes de que desaparezca del panel, y solo si desaparece a 3 min o menos de esa hora.
Para cada anuncio de X minutos (redondeado al minuto) se compara con esa llegada aproximada.

Grupos: parada, línea, sentido y tipo de día (laborable o fin de semana y festivo). Solo grupos con 30 anuncios o más.
Validación: ventanas calculadas con el primer 70 % de días y comprobadas en el 30 % restante.

Uso, desde la raíz de datos-transporte:
  python analisis/ventanas_interurbanos.py [--corte AAAA-MM-DD] [--desde 2026-10-14] [--lineas 691]
Salida: analisis/resultados/ventanas_interurbanos_AAAA-MM-DD.csv y ventanas_interurbanos_validacion_AAAA-MM-DD.txt
"""
import argparse, csv, glob, gzip, io, json, math, os, zipfile
import pandas as pd

RES = "analisis/resultados"
GTFS = "datos/horarios_oficiales/crtm_gtfs_interurbanos.zip"
# Festivos en laborable dentro del periodo medido: 2/11 (Comunidad de Madrid) y 9/11 (Almudena, en Madrid capital,
# donde está la cabecera de Moncloa).
FESTIVOS = {"2026-11-02", "2026-11-09"}
MIN_N = 30
MAX_ANUNCIO = 70
MAX_DESAPARECE_S = 180
CABECERA = 0.8


def nombres_paradas():
    with zipfile.ZipFile(GTFS) as z:
        crudo = z.read("stops.txt")
    try:
        texto = crudo.decode("utf-8-sig")
    except UnicodeDecodeError:
        texto = crudo.decode("cp1252")
    return {r["stop_id"].removeprefix("par_"): {"nombre": r["stop_name"].strip(), "lat": float(r["stop_lat"]), "lon": float(r["stop_lon"])}
            for r in csv.DictReader(io.StringIO(texto))}


def leer(desde, corte, lineas):
    filas = []
    for f in sorted(glob.glob("datos/crtm/*.jsonl.gz")):
        dia = os.path.basename(f)[:10]
        if not desde <= dia <= corte:
            continue
        with gzip.open(f, "rt", encoding="utf-8") as fh:
            for l in fh:
                try:
                    d = json.loads(l)
                except json.JSONDecodeError:
                    continue
                for a in d.get("a", []):
                    if str(a[0]) in lineas and a[3] and a[4]:
                        filas.append((dia, d["t"], d["s"], str(a[0]), a[1], a[2], a[3], a[4]))
    return pd.DataFrame(filas, columns=["dia", "t", "parada", "linea", "sentido", "destino", "llega", "cod"])


def preparar(df):
    fecha = pd.to_datetime(df.dia)
    df["laborable"] = (fecha.dt.weekday < 5) & ~df.dia.isin(FESTIVOS)
    df = df.sort_values("t")
    fin = df.groupby(["dia", "parada", "linea", "cod"]).agg(t_fin=("t", "last"), final=("llega", "last")).reset_index()
    d = df.merge(fin, on=["dia", "parada", "linea", "cod"])
    d = d[(d.final - d.t_fin) <= MAX_DESAPARECE_S].copy()
    d["anuncio"] = (d.llega - d.t) / 60
    d["real"] = (d.final - d.t) / 60
    d = d[(d.anuncio >= 1) & (d.anuncio <= MAX_ANUNCIO)].copy()
    d["minuto"] = d.anuncio.round().astype(int)
    d["retraso"] = d.real - d.anuncio
    return d


CLAVE = ["parada", "linea", "sentido", "laborable", "minuto"]


def resumir(d):
    g = d.groupby(CLAVE).retraso
    v = pd.DataFrame({"n": g.size(), "p10": g.quantile(.1), "mediana": g.median(), "p90": g.quantile(.9),
                      "p": g.apply(lambda x: (x.abs() <= 2).mean()), "tarde": g.apply(lambda x: (x > 2).mean()),
                      "antes": g.apply(lambda x: (x < -2).mean())}).reset_index()
    return v[v.n >= MIN_N]


def wilson(p, n, z=1.96):
    c = p + z * z / (2 * n)
    m = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (c - m) / (1 + z * z / n), (c + m) / (1 + z * z / n)


def main():
    ayer = (pd.Timestamp.now(tz="Europe/Madrid") - pd.Timedelta(days=1)).date().isoformat()
    ap = argparse.ArgumentParser()
    ap.add_argument("--corte", default=ayer)
    ap.add_argument("--desde", default="2026-10-14", help="primer día con las paradas fijas del 691")
    ap.add_argument("--lineas", default="691", help="separadas por comas")
    a = ap.parse_args()
    d = preparar(leer(a.desde, a.corte, set(a.lineas.split(","))))
    # En cabecera el panel enseña la hora de salida programada y el viaje desaparece a esa hora: el anuncio
    # coincide siempre con la "llegada" y no mide nada. Se detecta porque casi todos los retrasos son 0.
    ceros = d.groupby(["parada", "linea", "sentido"]).retraso.apply(lambda x: (x.abs() < 0.1).mean())
    cabeceras = ceros[ceros > CABECERA].index
    d = d[~d.set_index(["parada", "linea", "sentido"]).index.isin(cabeceras)]
    dias = sorted(d.dia.unique())
    corte_val = dias[int(len(dias) * 0.7)]
    entreno, prueba = d[d.dia < corte_val], d[d.dia >= corte_val]
    m = prueba.merge(resumir(entreno), on=CLAVE)
    dentro = ((m.retraso >= m.p10) & (m.retraso <= m.p90))

    v = resumir(d)
    ic = [wilson(p, n) for p, n in zip(v.p, v.n)]
    v["ic_bajo"], v["ic_alto"] = [round(x[0], 3) for x in ic], [round(x[1], 3) for x in ic]
    paradas = nombres_paradas()
    destino = d.groupby(["parada", "linea", "sentido"]).destino.agg(lambda x: x.mode().iat[0]).rename("destino").reset_index()
    v = v.merge(destino, on=["parada", "linea", "sentido"])
    v["nombre_parada"] = v.parada.map(lambda s: paradas.get(s, {}).get("nombre", ""))
    v["nombre_destino"] = v.destino.map(lambda s: paradas.get(s, {}).get("nombre", ""))
    v["lat"] = v.parada.map(lambda s: paradas.get(s, {}).get("lat"))
    v["lon"] = v.parada.map(lambda s: paradas.get(s, {}).get("lon"))
    for c in ["p10", "mediana", "p90"]:
        v[c] = v[c].round(2)
    for c in ["p", "tarde", "antes"]:
        v[c] = v[c].round(3)
    os.makedirs(RES, exist_ok=True)
    v.to_csv(f"{RES}/ventanas_interurbanos_{a.corte}.csv", index=False, encoding="utf-8")

    lineas = [f"Comprobado ejecutando. Líneas {a.lineas}; días {dias[0]} a {dias[-1]} ({len(dias)} días); {len(d)} anuncios con llegada aproximada.",
              "Llegada aproximada: última hora anunciada antes de que el viaje desaparezca del panel (a 3 min o menos). No es una llegada medida por GPS.",
              f"Fuera de muestra (ventanas con días hasta {corte_val}, comprobadas desde ese día): {dentro.mean():.1%} de {len(m)} anuncios dentro de la ventana p10-p90 (lo esperado es 80%).",
              "Fuera de la tabla, por ser cabecera (más del 80 % de anuncios con retraso 0): "
              + ", ".join(f"{s} {paradas.get(s, {}).get('nombre', '')} línea {l} sentido {se} ({ceros[(s, l, se)]:.0%})" for s, l, se in cabeceras),
              "", "Por parada y sentido, laborable, fuera de muestra:"]
    for (s, se), g in m[m.laborable].groupby(["parada", "sentido"]):
        x = dentro[g.index]
        lineas.append(f"  {s} {paradas.get(s, {}).get('nombre', '')} sentido {se}: {x.mean():.1%} de {len(x)}")
    lineas += ["", "Ejemplos, laborable (la app dice X -> suele llegar entre A y B):"]
    for _, r in v[v.laborable & v.minuto.isin([10, 20, 30])].iterrows():
        lineas.append(f"  {r.nombre_parada} ({r.parada}) hacia {r.nombre_destino}, dice {r.minuto}: entre {r.minuto + r.p10:.1f} y {r.minuto + r.p90:.1f} (n={r.n})")
    texto = "\n".join(lineas) + "\n"
    with open(f"{RES}/ventanas_interurbanos_validacion_{a.corte}.txt", "w", encoding="utf-8") as f:
        f.write(texto)
    print(texto)


if __name__ == "__main__":
    main()
