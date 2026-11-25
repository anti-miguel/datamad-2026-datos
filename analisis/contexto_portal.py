"""Demanda histórica oficial y sensibilidad de la extrapolación EMT, sin red.

Usa 902003 y 1923861 ya copiados en datos/catalogo_cm. No añade datasets.
Las horas son escenarios con la misma espera adicional: no miden pérdidas reales.
Uso desde la raíz: python analisis/contexto_portal.py --corte 2026-11-04
"""
import argparse
from pathlib import Path

import pandas as pd

from cruce_catalogo import ALIAS_ESTACIONES, catalogo, norma


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--corte", default="2026-11-04")
    args = parser.parse_args()
    cat, _ = catalogo()
    demanda = cat["billetes_por_modo"].copy()
    demanda["valor"] = pd.to_numeric(demanda.valor.str.replace(",", "."), errors="coerce")
    demanda = demanda.dropna(subset=["valor"])
    filas = []
    for concepto, g in demanda.groupby("concepto"):
        g = g.sort_values("ano")
        base = g[g.ano == "2019"]
        if base.empty:
            continue
        ultimo = g.iloc[-1]
        filas.append({"concepto": concepto, "ano_base": "2019", "valor_base": base.iloc[-1].valor,
                      "ano_ultimo": ultimo.ano, "valor_ultimo": ultimo.valor,
                      "unidad": ultimo.unidad, "cambio_pct": 100 * (ultimo.valor / base.iloc[-1].valor - 1),
                      "n_anos_validos": g.ano.nunique()})
    t = pd.DataFrame(filas)
    out = Path("analisis/resultados")
    t.to_csv(out / f"contexto_portal_demanda_{args.corte}.csv", index=False, encoding="utf-8")
    emt = t[t.concepto.str.contains(r"\(EMT\)", regex=True)].iloc[0]
    lineas = pd.read_csv(out / f"cruce_catalogo_emt_lineas_{args.corte}.csv")
    ew = lineas.ewt_min.median()
    estaciones = cat["viajeros_cercanias_estaciones"].copy()
    estaciones["n"] = pd.to_numeric(estaciones.valor, errors="coerce")
    ano = estaciones.ano.max()
    v = estaciones[(estaciones.ano == ano) & estaciones.n.notna()]
    cruce = pd.read_csv(out / f"cruce_catalogo_renfe_estaciones_{args.corte}.csv")
    cobertura = cruce.n.sum() / v.n.sum()
    estaciones["nombre"] = estaciones.concepto.str.extract(r"estaci.n de (.*)$", expand=False).map(norma).replace(ALIAS_ESTACIONES)
    pesos = []
    for ano_peso, g in estaciones.dropna(subset=["n"]).groupby("ano"):
        m = cruce[["nombre", "acierto"]].merge(g[["nombre", "n"]], on="nombre")
        if m.empty:
            continue
        pesos.append({"ano_demanda": ano_peso, "n_estaciones_portal": len(g), "n_estaciones_cruzadas": len(m),
                      "acierto_ponderado": (m.acierto * m.n).sum() / m.n.sum(),
                      "cobertura_viajeros_publicados": m.n.sum() / g.n.sum(), "corte_observaciones": args.corte})
    pesos = pd.DataFrame(pesos)
    pesos.to_csv(out / f"contexto_portal_pesos_renfe_{args.corte}.csv", index=False, encoding="utf-8")
    a2019 = pesos[pesos.ano_demanda == "2019"]
    aultimo = pesos[pesos.ano_demanda == ano].iloc[0]
    texto = [f"# Contexto del portal, corte {args.corte}", "",
             "Comprobado ejecutando: copias locales de los datasets 902003 y 1923861, descargadas el 05/11/2026.", "",
             f"EMT: {emt.valor_base:.1f} millones de billetes en 2019 frente a {emt.valor_ultimo:.1f} en {emt.ano_ultimo}, cambio {emt.cambio_pct:+.1f}%; {int(emt.n_anos_validos)} años válidos.",
             f"Sensibilidad de escenario: usando EWT mediana de punta {ew:.2f} min ({len(lineas)} líneas de al menos 100 intervalos), serían {emt.valor_base * ew / 60:.2f} M horas con demanda de 2019 y {emt.valor_ultimo * ew / 60:.2f} M horas con la última demanda. Es una extrapolación de paradas céntricas a toda la red, con viajeros que llegan al azar; no mide horas perdidas reales ni demanda de 2026.", "",
             "Limitación confirmada en código: el cruce histórico quita ceros de las líneas y puede mezclar 001/1 y 002/2. Las métricas de esas claves y su efecto en horarios requieren corrección independiente; véase lineas_emt_ambiguas_2026-11-04.md. El escenario mantiene el método histórico para su comparación.", "",
             f"Renfe: {len(cruce)} de {len(v)} estaciones con dato oficial de {ano} se cruzan con al menos 500 llegadas; cubren {cobertura:.1%} de los viajeros subidos y bajados publicados para esas {len(v)} estaciones. No equivale a cobertura de toda la red ni a personas únicas.",
             f"Sensibilidad Renfe al año del peso: {len(pesos)} años con cruces. Acierto ponderado con pesos {ano}: {aultimo.acierto_ponderado:.2%}. " + (f"Con pesos 2019: {a2019.iloc[0].acierto_ponderado:.2%}; diferencia {100 * (aultimo.acierto_ponderado - a2019.iloc[0].acierto_ponderado):+.2f} puntos porcentuales." if len(a2019) else "No hay pesos válidos de 2019."),
             "Se mantienen las tasas observadas en septiembre-noviembre de 2026 y se varían solo los pesos. Se usan las tasas de estación redondeadas a tres decimales del cruce (hasta 0,05 puntos porcentuales de redondeo); los cambios de cobertura anual también influyen. No es una evolución histórica de la fiabilidad.",
             "La cobertura por volumen permite describir el subconjunto al que se aplica la ponderación. Las tasas de error siguen dependiendo del método de observación y de su posible sesgo en túneles.", "",
             "Inferencia: conviene presentar el periodo de demanda junto a cada ponderación y comparar estaciones con independencia de la demanda antes de convertir la tasa en una prioridad de producto.", ""]
    (out / f"contexto_portal_{args.corte}.md").write_text("\n".join(texto), encoding="utf-8")
    print("\n".join(texto))


if __name__ == "__main__":
    main()
