"""Consulta de la tabla de fiabilidad (fiabilidad.csv). Solo biblioteca estándar.

  from analisis.fiabilidad import consultar
  consultar("emt", 18, hora=8.5, finde=False, linea="104")
  -> {"p_acierto_2min": 0.61, "ic95": [...], "retraso_mediano_min": ..., "nivel": "4_linea", "n_llegadas": ...}

Busca del grupo más concreto al más general y se queda con el primero que tenga al menos 30 llegadas:
línea > tipo de parada > franja horaria > toda la red. Devuelve None si la red o la antelación no están medidas
(interurbanos, Metro a 25 min o más, anuncios a 40 min o más): la app no debe inventar una probabilidad.
"""
import csv, os

CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultados", "fiabilidad.csv")
BINS = [(0, 3, "0-3"), (3, 6, "3-6"), (6, 10, "6-10"), (10, 15, "10-15"), (15, 25, "15-25"), (25, 40, "25-40")]
MIN_LLEGADAS = 30
_tabla = {}


def _cargar():
    with open(CSV, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            _tabla[(r["nivel"], r["red"], r["linea"], r["tipo"], r["franja"], r["tipo_dia"], r["anuncio_min"])] = r


def franja(h):
    return "punta_manana" if 7 <= h < 9.5 else "valle" if 9.5 <= h < 17 else "punta_tarde" if 17 <= h < 20 else "noche"


def consultar(red, minutos, hora, finde=False, linea=None, tipo=None):
    """red: emt|metro|renfe. minutos: lo que anuncia el operador. hora: 8.5 = 8:30. tipo: cabecera|intermedia|estacion."""
    if not _tabla:
        _cargar()
    b = next((e for lo, hi, e in BINS if lo <= minutos < hi), None)
    if b is None:
        return None
    fr, td = franja(hora), "finde" if finde else "laborable"
    claves = [("4_linea", red, linea or "", "*", fr, td, b), ("3_tipo", red, "*", tipo or "", fr, td, b),
              ("2_franja", red, "*", "*", fr, td, b), ("1_red", red, "*", "*", "*", "*", b)]
    for k in claves:
        r = _tabla.get(k)
        if r and float(r["n_llegadas"]) >= MIN_LLEGADAS:
            return {"p_acierto_2min": float(r["p_acierto_2min"]), "ic95": [float(r["ic95_bajo"]), float(r["ic95_alto"])],
                    "p_tarde_mas_2min": float(r["p_tarde_mas_2min"]), "p_antes_mas_2min": float(r["p_antes_mas_2min"]),
                    "retraso_mediano_min": float(r["retraso_mediano_min"]), "nivel": k[0], "n_llegadas": int(float(r["n_llegadas"]))}
    return None
