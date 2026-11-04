"""Atajos para leer los datos grabados. Ejecutar desde la raíz de datos-transporte (o importar desde ahí).

  import cargar
  cargar.dias("emt")                        # ['2026-10-04', ...]
  for fila in cargar.filas("crtm", "2026-10-15"): ...
  df = cargar.emt("2026-10-15")             # una fila por autobús y consulta
  df = cargar.crtm("2026-10-15")            # una fila por llegada anunciada (Metro e interurbanos)
  df = cargar.renfe_posiciones("2026-10-15")
  df = cargar.trafico("2026-10-15")         # una fila por punto de medida y lectura (5 min)
  df = cargar.avisos()                      # avisos de la EMT, en su última versión conocida

Las horas se devuelven en hora de Madrid (columna "hora"); "t" es el epoch UTC de la consulta.
pandas solo hace falta para las funciones que devuelven DataFrame.
"""
import glob, gzip, json, os

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "datos")
FUENTES = ("renfe", "emt", "crtm", "trafico", "avisos")


def dias(fuente):
    return [os.path.basename(f)[:10] for f in sorted(glob.glob(os.path.join(RAIZ, fuente, "*.jsonl.gz")))]


def filas(fuente, dia):
    """Filas crudas (dict) de un día, tal como las escribió el grabador."""
    with gzip.open(os.path.join(RAIZ, fuente, f"{dia}.jsonl.gz"), "rt", encoding="utf-8") as f:
        for linea in f:
            yield json.loads(linea)


def _hora(df, col="t"):
    import pandas as pd
    df["hora"] = pd.to_datetime(df[col], unit="s", utc=True).dt.tz_convert("Europe/Madrid")
    return df


def emt(dia):
    import pandas as pd
    cols = ["linea", "bus", "llega_en_s", "distancia_m", "lon", "lat", "tipo_posicion", "destino"]
    out = [{"t": r["t"], "parada": r["s"], **dict(zip(cols, a))}
           for r in filas("emt", dia) if "a" in r for a in r["a"]]
    return _hora(pd.DataFrame(out))


def crtm(dia):
    import pandas as pd
    out = [{"t": r["t"], "parada": r["s"], "modo": r["m"], "linea": a[0], "sentido": a[1],
            "destino": a[2], "llegada": a[3], "cod_viaje": a[4]}
           for r in filas("crtm", dia) if "a" in r for a in r["a"]]
    df = _hora(pd.DataFrame(out))
    df["llegada_hora"] = pd.to_datetime(df["llegada"], unit="s", utc=True).dt.tz_convert("Europe/Madrid")
    df["faltan_s"] = df["llegada"] - df["t"]
    return df


def renfe_posiciones(dia):
    import pandas as pd
    return _hora(pd.DataFrame([r for r in filas("renfe", dia) if r.get("k") == "vp"]).drop(columns="k"))


def renfe_retrasos(dia):
    """Una fila por tren, consulta y parada con el retraso anunciado (s)."""
    import pandas as pd
    out = [{"t": r["t"], "trip": r["trip"], "rel": r["rel"], "parada": s[0], "retraso_s": s[1], "rel_parada": s[2]}
           for r in filas("renfe", dia) if r.get("k") == "tu" for s in r["stops"]]
    return _hora(pd.DataFrame(out))


def trafico(dia):
    import pandas as pd
    out = [{"t": r["t"], **dict(zip(r["c"], v))} for r in filas("trafico", dia) if r.get("k") == "pm" for v in r["r"]]
    return _hora(pd.DataFrame(out))


def puntos_medida():
    """Catálogo de los puntos de medida de tráfico (id, descripción, coordenadas)."""
    with gzip.open(os.path.join(RAIZ, "trafico", "puntos_medida.json.gz"), "rt", encoding="utf-8") as f:
        return json.load(f)


def avisos():
    """Última versión de cada aviso de la EMT. "desde" y "hasta" pasan a hora de Madrid."""
    import pandas as pd
    ultimos = {}
    for dia in dias("avisos"):
        for r in filas("avisos", dia):
            if r.get("k") == "aviso":
                ultimos[r["guid"]] = r
    df = pd.DataFrame(ultimos.values())
    for c in ("desde", "hasta"):
        df[c] = pd.to_datetime(df[c], unit="s", utc=True).dt.tz_convert("Europe/Madrid")
    return df
