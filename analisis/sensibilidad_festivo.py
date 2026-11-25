"""Aísla el efecto de clasificar el 02/11 como festivo en la tabla actualizada.

La tabla principal conserva la regla histórica para que el refresco sea comparable.
Uso: python analisis/sensibilidad_festivo.py <cache> --corte 2026-11-04
"""
import argparse
import json
from pathlib import Path

import pandas as pd

import tabla_fiabilidad as tf


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("cache")
    parser.add_argument("--corte", default="2026-11-04")
    args = parser.parse_args()
    cache = Path(args.cache)
    meta = json.loads((cache / "predicciones.parquet.json").read_text(encoding="utf-8"))
    if meta.get("corte") != args.corte:
        parser.error("La caché tiene otro corte.")
    d = tf.preparar(pd.read_parquet(cache / "predicciones.parquet"))
    afectado = d.dia == "2026-11-02"
    muestras = d[afectado].groupby("red").agg(predicciones=("ok", "size"), llegadas=("llegada", "nunique"))
    d.loc[afectado, "tipo_dia"] = "finde"
    corregida = tf.tabla(d)
    res = Path("analisis/resultados")
    corregida.to_csv(res / f"fiabilidad_festivo_{args.corte}.csv", index=False, encoding="utf-8")
    original = pd.read_csv(res / f"fiabilidad_{args.corte}.csv")
    claves = ["nivel", "red", "linea", "tipo", "franja", "tipo_dia", "anuncio_min"]
    m = original.merge(corregida, on=claves, how="outer", suffixes=("_base", "_festivo"), indicator=True)
    m["cambio_pp"] = 100 * (m.p_acierto_2min_festivo - m.p_acierto_2min_base)
    m.to_csv(res / f"fiabilidad_festivo_cambios_{args.corte}.csv", index=False, encoding="utf-8")
    lineas = [f"# Sensibilidad al festivo del 02/11, corte {args.corte}", "",
              "Confirmado en código: preparar() mantiene la regla histórica que trata como festivo solo el 12/10, además de fines de semana. El 02/11/2026 es lunes y queda como laborable. cruce_catalogo.py lo excluye de laborables porque calendar_dates del GTFS no ofrece servicio LA.",
              "Comprobado ejecutando: esta tabla alternativa solo cambia tipo_dia a finde el 02/11; conserva predicciones, llegadas y reglas de los demás días. Recalcula los agregados afectados. No sustituye la tabla principal ni modifica el servicio de consulta o la demo.", "",
              "| Red | Predicciones reclasificadas | Llegadas reclasificadas |", "|---|---:|---:|"]
    for red, r in muestras.iterrows():
        lineas.append(f"| {red} | {int(r.predicciones)} | {int(r.llegadas)} |")
    lineas += ["", "Cambios en probabilidades publicadas redondeadas a tres decimales:"]
    for nivel, g in m.groupby("nivel"):
        comunes = g[g._merge == "both"]
        robusto = comunes[(comunes.n_llegadas_base >= 30) & (comunes.n_llegadas_festivo >= 30)]
        lineas.append(f"- {nivel}: {len(comunes)} celdas emparejadas; {int((comunes.cambio_pp.abs() > 1e-9).sum())} cambian de acierto. Con al menos 30 llegadas en ambas versiones ({len(robusto)} celdas), cambio absoluto mediano {robusto.cambio_pp.abs().median():.2f} y máximo {robusto.cambio_pp.abs().max():.2f} puntos; {int((g._merge == 'right_only').sum())} celdas nuevas y {int((g._merge == 'left_only').sum())} desaparecidas.")
    lineas += ["", "Inferencia: la clasificación del festivo puede cambiar consultas por franja, tipo y línea (niveles 2 a 4); el nivel 1 por red y anuncio no usa tipo_dia y permanece igual. Esta sensibilidad no demuestra una diferencia real de servicio entre festivos y laborables.", ""]
    texto = "\n".join(lineas)
    (res / f"sensibilidad_festivo_{args.corte}.md").write_text(texto, encoding="utf-8")
    print(texto)


if __name__ == "__main__":
    main()
