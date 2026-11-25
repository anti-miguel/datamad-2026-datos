"""Compara las salidas fechadas con las históricas, que se conservan intactas.

Uso desde la raíz: python analisis/comparar_refresh.py --corte 2026-11-04
Las diferencias de probabilidades usan el redondeo de tres decimales de las tablas.
"""
import argparse
from pathlib import Path

import pandas as pd
from tabla_fiabilidad import BINS, ETQ


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--corte", default="2026-11-04")
    parser.add_argument("--cache", help="Comprueba también la equivalencia de los grupos históricos hasta el 03/11.")
    args = parser.parse_args()
    res = Path("analisis/resultados")
    a = pd.read_csv(res / "fiabilidad.csv")
    b = pd.read_csv(res / f"fiabilidad_{args.corte}.csv")
    keys = ["nivel", "red", "linea", "tipo", "franja", "tipo_dia", "anuncio_min"]
    m = a.merge(b, on=keys, suffixes=("_antes", "_ahora"), how="outer", indicator=True)
    comun = m[m._merge == "both"].copy()
    comun["cambio_pp"] = 100 * (comun.p_acierto_2min_ahora - comun.p_acierto_2min_antes)
    comun.to_csv(res / f"fiabilidad_cambios_{args.corte}.csv", index=False, encoding="utf-8")
    robusto = comun[(comun.n_llegadas_antes >= 30) & (comun.n_llegadas_ahora >= 30)]
    red = comun[comun.nivel == "1_red"].copy()
    texto = [f"# Refresco con corte {args.corte}", "",
             f"Comprobado ejecutando. Fiabilidad histórica: hasta 03/11/2026, según fiabilidad_validacion.txt. Nuevo corte: todos los ficheros diarios cerrados hasta {args.corte}.",
             "Se conserva el método de llegada y acierto. La extracción de Renfe ahora procesa los crudos por día; los resultados de predicción se agrupan después. Las comparaciones parten de probabilidades publicadas redondeadas a tres decimales.", "",
             f"Tabla: {len(a)} celdas antes y {len(b)} ahora; {len(comun)} comparables, {int((m._merge == 'right_only').sum())} nuevas y {int((m._merge == 'left_only').sum())} desaparecidas.",
             f"En {len(robusto)} celdas con al menos 30 llegadas en ambos cortes: cambio absoluto mediano {robusto.cambio_pp.abs().median():.2f} puntos; máximo {robusto.cambio_pp.abs().max():.2f} puntos.", "",
             "| Red | Anuncio (min) | Llegadas antes | Llegadas ahora | Acierto antes | Acierto ahora | Cambio (puntos) |",
             "|---|---|---:|---:|---:|---:|---:|"]
    for r in red.itertuples():
        texto.append(f"| {r.red} | {r.anuncio_min} | {int(r.n_llegadas_antes)} | {int(r.n_llegadas_ahora)} | {r.p_acierto_2min_antes:.1%} | {r.p_acierto_2min_ahora:.1%} | {r.cambio_pp:+.2f} |")
    texto += ["", "Las llegadas de distintos intervalos de anuncio pueden coincidir; no deben sumarse. Los cambios en celdas pequeñas tienen mayor incertidumbre.", ""]
    if args.cache:
        d = pd.read_parquet(Path(args.cache) / "predicciones.parquet", columns=["red", "dia", "antel", "retraso", "llegada"])
        d = d[d.dia <= "2026-11-03"].copy()
        d["anuncio"] = d.antel - d.retraso
        d = d[(d.antel >= 0) & (d.anuncio >= 0) & (d.anuncio < 40) & ~((d.red == "metro") & (d.anuncio >= 25))]
        d["anuncio_min"] = pd.cut(d.anuncio, BINS, right=False, labels=ETQ).astype(str)
        d["ok"] = d.retraso.abs() <= 2
        g = d.groupby(["red", "anuncio_min"]).agg(n_predicciones=("ok", "size"), n_llegadas=("llegada", "nunique"), p_acierto_2min=("ok", "mean")).reset_index()
        x = a[a.nivel == "1_red"].merge(g, on=["red", "anuncio_min"], suffixes=("_historico", "_recalculado"))
        iguales = ((x.n_predicciones_historico == x.n_predicciones_recalculado) & (x.n_llegadas_historico == x.n_llegadas_recalculado) & (x.p_acierto_2min_historico == x.p_acierto_2min_recalculado.round(3)))
        texto.append(f"Control del método sobre el periodo antiguo hasta 03/11: {int(iguales.sum())} de {len(x)} grupos por red y anuncio reproducen exactamente los tamaños de muestra y aciertos publicados a tres decimales. Este control no vuelve a verificar todos los niveles ni todas las cuantiles.")
        del d
    for nombre, clave, metrica in (("cruce_catalogo_emt_lineas", "linea", "ewt_min"), ("cruce_catalogo_renfe_estaciones", "nombre", "acierto")):
        antes = pd.read_csv(res / f"{nombre}.csv")
        ahora = pd.read_csv(res / f"{nombre}_{args.corte}.csv")
        x = antes.merge(ahora, on=clave, suffixes=("_antes", "_ahora"))
        delta = x[f"{metrica}_ahora"] - x[f"{metrica}_antes"]
        unidad = "minutos" if metrica == "ewt_min" else "puntos porcentuales"
        if metrica == "acierto":
            delta *= 100
        texto.append(f"Cruce {clave}: {len(antes)} filas antes, {len(ahora)} ahora, {len(x)} emparejadas; diferencia absoluta mediana de {metrica}: {delta.abs().median():.3f} {unidad}; máxima {delta.abs().max():.3f}.")
        if metrica == "acierto":
            for t, g in (("antes", antes), ("ahora", ahora)):
                texto.append(f"Renfe {t}: {(g.acierto * g.n).sum() / g.n.sum():.2%} ponderado por viajeros; {g.acierto.mean():.2%} sin ponderar; {len(g)} estaciones.")
        else:
            texto.append(f"EMT: EWT mediana por línea {antes.ewt_min.median():.2f} a {ahora.ewt_min.median():.2f} min; muestras de intervalos de punta {int(antes.n.sum())} a {int(ahora.n.sum())}.")
    texto += ["", "El cruce EMT histórico ya cubría 05/10 a 04/11, según su texto: se esperaba estabilidad al mantener ese mismo corte. El histórico Renfe no documenta fecha final de caché en cruce_catalogo.txt; no se presupone su corte a partir del nombre sin fecha.",
              "Limitación confirmada en código: el cruce EMT conserva la normalización histórica que fusiona 001/1 y 002/2. Hay anuncios de 001 y 1 en la muestra y su fila agregada no representa una sola línea; las frecuencias de referencia de 1 y 2 también pueden mezclarse. El detalle y la sensibilidad al excluirlas están en lineas_emt_ambiguas_2026-11-04.md. Estos resultados comparables no validan esa identidad de líneas.",
              "Inferencia: una diferencia entre cortes no demuestra cambio del servicio; también cambian los días y la muestra observada. El sesgo de túneles se evalúa aparte.", ""]
    (res / f"refresco_{args.corte}.md").write_text("\n".join(texto), encoding="utf-8")
    print("\n".join(texto))


if __name__ == "__main__":
    main()
