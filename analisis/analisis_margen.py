"""Margen real en Cercanías Madrid a partir del histórico de rodalies-observatorio.

Entrada: rodalies-observaciones.csv.gz (release datos-2026-09-14, CC BY 4.0).
Cada fila es la última predicción de Renfe para un tren en una parada,
vista normalmente ~2,5 min antes de la llegada: se usa como proxy de llegada real.
"""
import sys
import pandas as pd

SRC = sys.argv[1] if len(sys.argv) > 1 else "datos/externos/rodalies-observatorio_observaciones.csv.gz"

TRAYECTOS = [
    # las cabeceras (Aranjuez, Guadalajara...) casi nunca salen en el feed: se usa la 2.ª-3.ª estación
    ("Valdemoro", "Madrid-Atocha Cercanías"),
    ("Alcalá de Henares", "Madrid-Atocha Cercanías"),
    ("Móstoles", "Madrid-Atocha Cercanías"),
    ("Fuenlabrada", "Madrid-Atocha Cercanías"),
    ("Madrid-Atocha Cercanías", "Madrid-Nuevos Ministerios"),
    ("Getafe-Centro", "Sol"),
]


def franja(h: float) -> str:
    if 7 <= h < 9.5:
        return "punta mañana 7-9:30"
    if 17 <= h < 20:
        return "punta tarde 17-20"
    return "resto"


def cargar() -> pd.DataFrame:
    d = pd.read_csv(SRC)
    m = d[d.nucleo_id == 10].copy()
    for c in ["scheduled_arrival", "arrival_time"]:
        m[c] = pd.to_datetime(m[c], utc=True).dt.tz_convert("Europe/Madrid")
    # fuera: saltos de día/zona horaria (|retraso| >= 3 h) y paradas suprimidas
    m = m[(m.delay_s.abs() < 3 * 3600) | (m.schedule_relationship == "SKIPPED")]
    # por fecha de servicio: las paradas SKIPPED no traen hora programada
    m["laborable"] = pd.to_datetime(m.service_date).dt.dayofweek < 5
    return m


def viajes(m: pd.DataFrame, origen: str, destino: str) -> pd.DataFrame:
    """Viajes directos (mismo tren) origen->destino con salida programada y llegada observada."""
    key = ["service_date", "trip_id"]
    m = m[m.schedule_relationship == "SCHEDULED"]
    o = m[m.estacion.str.startswith(origen)][key + ["scheduled_arrival", "delay_s", "linea"]]
    t = m[m.estacion == destino][key + ["scheduled_arrival", "delay_s"]]
    v = o.merge(t, on=key, suffixes=("_o", "_d"))
    v = v[v.scheduled_arrival_d > v.scheduled_arrival_o]  # sentido correcto
    v["min_programados"] = (v.scheduled_arrival_d - v.scheduled_arrival_o).dt.total_seconds() / 60
    v["retraso_llegada_min"] = v.delay_s_d / 60
    h = v.scheduled_arrival_o.dt.hour + v.scheduled_arrival_o.dt.minute / 60
    v["franja"] = h.map(franja)
    v["laborable"] = v.scheduled_arrival_o.dt.dayofweek < 5
    return v


def resumen(v: pd.DataFrame) -> pd.DataFrame:
    r = v.groupby("franja").retraso_llegada_min.agg(
        viajes="size",
        mediana="median",
        p90=lambda s: s.quantile(0.90),
        p95=lambda s: s.quantile(0.95),
        pct_mas_5=lambda s: (s > 5).mean() * 100,
        pct_mas_10=lambda s: (s > 10).mean() * 100,
    )
    r.insert(1, "min_programados", v.groupby("franja").min_programados.median())
    return r.round(1)


if __name__ == "__main__":
    m = cargar()
    lab = m[m.laborable & (m.service_date >= "2026-09-01")]
    dias = lab.groupby("service_date").trip_id.nunique()
    dias = dias[dias > 1000]  # solo días laborables completos
    lab = lab[lab.service_date.isin(dias.index)]
    print(f"Madrid, laborables 1-14 sep: {len(dias)} días, {dias.median():.0f} trenes/día observados "
          f"(el GTFS de Renfe programa ~1.300 por laborable)\n")
    ok = lab[lab.schedule_relationship == "SCHEDULED"]
    por_linea = ok.groupby("linea").delay_s.describe(percentiles=[.5, .9, .95])[["count", "50%", "90%", "95%"]]
    por_linea[["50%", "90%", "95%"]] /= 60
    por_linea["% paradas suprimidas"] = (
        lab.groupby("linea").schedule_relationship.apply(lambda s: (s == "SKIPPED").mean() * 100))
    print("Retraso de llegada por línea (min, todas las paradas):")
    print(por_linea.round(1).sort_values("count", ascending=False).head(10).to_string(), "\n")
    for o, dst in TRAYECTOS:
        v = viajes(lab, o, dst)
        if v.empty:
            print(f"== {o} -> {dst}: sin viajes directos\n")
            continue
        print(f"== {o} -> {dst}  (líneas {', '.join(sorted(v.linea.unique()))}, {v.service_date.nunique()} días)")
        print(resumen(v).to_string(), "\n")
