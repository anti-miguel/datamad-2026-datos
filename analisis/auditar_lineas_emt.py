"""Cuantifica las identidades que pierde la normalización histórica del cruce EMT.

Uso: python analisis/auditar_lineas_emt.py --corte 2026-11-04
No corrige el cruce comparable: separa observaciones brutas, elegibilidad y resultados ambiguos.
"""
import argparse
from collections import Counter, defaultdict
from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import cargar
from cruce_catalogo import CENT, FESTIVOS, hora_local, linea


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--corte", default="2026-11-04")
    args = parser.parse_args()
    cuentas = defaultdict(Counter)
    for dia in cargar.dias("emt"):
        if dia > args.corte:
            continue
        laborable = pd.Timestamp(dia).dayofweek < 5 and dia not in FESTIVOS
        for r in cargar.filas("emt", dia):
            for lin, bus, est, *_ in r.get("a", []):
                lin = str(lin).strip().upper()
                cuentas[lin]["anuncios_brutos"] += 1
                if laborable and bus and est is not None and est not in CENT:
                    cuentas[lin]["anuncios_seguibles_laborable"] += 1
                    h = hora_local(r["t"])
                    if 7 <= h < 9.5 or 17 <= h < 20:
                        cuentas[lin]["anuncios_seguibles_punta"] += 1
    grupos = defaultdict(list)
    for lin in cuentas:
        grupos[linea(lin)].append(lin)
    ambiguos = {lin: sorted(v) for lin, v in grupos.items() if len(v) > 1}
    filas = [{"linea_original": lin, "linea_normalizada": normal, **cuentas[lin]} for normal, originales in ambiguos.items() for lin in originales]
    res = Path("analisis/resultados")
    pd.DataFrame(filas).fillna(0).to_csv(res / f"lineas_emt_ambiguas_{args.corte}.csv", index=False, encoding="utf-8")
    texto = [f"# Identidad de líneas EMT en el cruce, corte {args.corte}", "",
             "Confirmado en código y GTFS local: la función linea() del cruce quita ceros iniciales. routes.txt contiene rutas diferentes con nombres cortos 1 (route_id 001) y 001 (route_id 361), y 2 (route_id 002) y 002 (route_id 362). La normalización histórica las fusiona.",
             f"Comprobado ejecutando: {len(cuentas)} nombres distintos de línea en los anuncios brutos del periodo; {len(ambiguos)} claves normalizadas con más de un nombre presente: {ambiguos}.", "",
             "| Línea original | Clave del cruce | Anuncios brutos | Seguibles en laborable | Seguibles en punta |", "|---|---|---:|---:|---:|"]
    for r in filas:
        texto.append(f"| {r['linea_original']} | {r['linea_normalizada']} | {r.get('anuncios_brutos', 0)} | {r.get('anuncios_seguibles_laborable', 0)} | {r.get('anuncios_seguibles_punta', 0)} |")
    t = pd.read_csv(res / f"cruce_catalogo_emt_lineas_{args.corte}.csv", dtype={"linea": str})
    afectadas = t[t.linea.isin(ambiguos)]
    candidatas = t[t.linea.isin(["1", "2"])]
    excluidas = t[~t.linea.isin(["1", "2"])]
    texto += ["", f"En la tabla actualizada de punta, {len(afectadas)} de {len(t)} filas conservan esas claves ambiguas y suman {int(afectadas.n.sum())} de {int(t.n.sum())} intervalos publicados. No se pueden atribuir sus métricas a una sola de las líneas originales.",
              "Seguible significa bus identificado, estimación numérica y distinta de 888888/999999 en un laborable según el cruce. Cuenta anuncios, no viajes ni intervalos finales. Una clave fusionada también puede contaminar el horario de referencia y la exclusión de cabeceras; estos recuentos no miden ese sesgo.",
              f"Las claves 1 y 2 también reúnen rutas distintas en el horario GTFS, aunque no se observan ambos nombres originales de 2 en la muestra. Sus {len(candidatas)} filas suman {int(candidatas.n.sum())} intervalos de punta potencialmente afectados por la normalización de referencia; no se ha determinado cuántos usan el destino exacto o el horario alternativo por línea. Excluyendo ambas filas como sensibilidad prudente quedan {len(excluidas)} líneas y EWT mediana {excluidas.ewt_min.median():.2f} min, frente a {t.ewt_min.median():.2f} en las {len(t)} originales. No es un recálculo con identidades corregidas.",
              "El refresco principal conserva el método para compararlo con el histórico. Deben reservarse las filas ambiguas y revisar sus efectos en agregados antes de usarlos como prueba de rendimiento. No se atribuye todo cambio de tabla a nuevos días.", ""]
    (res / f"lineas_emt_ambiguas_{args.corte}.md").write_text("\n".join(texto), encoding="utf-8")
    print("\n".join(texto))


if __name__ == "__main__":
    main()
