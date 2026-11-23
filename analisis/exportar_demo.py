"""Convierte la tabla de fiabilidad en demo/fiabilidad.json, lista para usarla desde una web sin servidor.

Solo incluye grupos con al menos 30 llegadas, los únicos que usa analisis/fiabilidad.py. Consulta en demo/consultar.js.
Quita las casillas con percentiles absurdos (más de 30 min de retraso o de adelanto en p90 o p10): la consulta cae
entonces al nivel siguiente (tipo, franja o red). Une las líneas EMT escritas con ceros delante ("001" y "1").
Añade la red "interurbano" desde analisis/ventanas_interurbanos.py.
Uso, desde la raíz de datos-transporte, después de regenerar la tabla y las ventanas del mismo corte:
  python analisis/exportar_demo.py --corte AAAA-MM-DD
"""
import argparse, csv, json, os, re

RES = "analisis/resultados"
SALIDA = "demo/fiabilidad.json"
MIN_LLEGADAS = 30
ORDEN_BINS = ["0-3", "3-6", "6-10", "10-15", "15-25", "25-40"]
MAX_PERCENTIL = 30

META = {
    "pregunta": "Si el operador anuncia X minutos, ¿con qué probabilidad llega a ±2 min de lo anunciado?",
    "min_llegadas": MIN_LLEGADAS,
    "anuncio_min": [[0, 3, "0-3"], [3, 6, "3-6"], [6, 10, "6-10"], [10, 15, "10-15"], [15, 25, "15-25"], [25, 40, "25-40"]],
    "franjas": {"punta_manana": [7, 9.5], "valle": [9.5, 17], "punta_tarde": [17, 20], "noche": "el resto"},
    "orden_consulta": ["linea", "tipo", "franja", "red"],
    "interurbano": "por parada, línea, sentido, tipo de día y minuto anunciado (1 a 70); sin niveles de respaldo",
    "campos": {"p": "probabilidad de llegar a ±2 min", "ic": "intervalo de confianza del 95%", "n": "llegadas medidas",
               "tarde": "probabilidad de llegar más de 2 min tarde", "antes": "probabilidad de llegar más de 2 min antes",
               "mediana": "retraso mediano, en minutos", "p10": "retraso, percentil 10", "p90": "retraso, percentil 90"},
    "redes": {
        "emt": {"nombre": "EMT Madrid", "medida": "posición y estimación del autobús", "licencia": "ODbL",
                "atribucion": "Powered by EMT de Madrid", "dataset_del_portal": False},
        "renfe": {"nombre": "Cercanías Renfe", "medida": "GPS del tren", "licencia": "CC BY 4.0",
                  "atribucion": "Fuente: Renfe", "dataset_del_portal": False},
        "metro": {"nombre": "Metro de Madrid", "medida": "el tren desaparece del panel; puede dar aciertos de más",
                  "licencia": "aviso legal del Consorcio: reutilización citando la fuente y la fecha de extracción", "atribucion": "Fuente: Consorcio Regional de Transportes de Madrid",
                  "indicar_fecha_extraccion": True, "dataset_del_portal": False},
        "interurbano": {"nombre": "Autobuses interurbanos (Consorcio)", "lineas": ["691"],
                        "medida": "última hora anunciada antes de que el viaje desaparezca del panel; aproxima la llegada, no es GPS",
                        "licencia": "aviso legal del Consorcio: reutilización citando la fuente y la fecha de extracción",
                        "atribucion": "Fuente: Consorcio Regional de Transportes de Madrid", "indicar_fecha_extraccion": True,
                        "dataset_del_portal": False},
    },
    "sin_dato": ["interurbanos fuera de las paradas medidas del 691", "cabeceras de los interurbanos (Moncloa y Los Copos): el panel enseña el horario",
                 "Metro a 25 min o más", "anuncios de 40 min o más (70 en interurbanos)",
                 "casillas con percentiles de más de 30 min: se usa el nivel siguiente"],
    "advertencias": [
        "En paradas no medidas la tabla es optimista en la parte alta: en la EMT dice 93% y ocurre 82%.",
        "En la EMT, el 35% de las visitas de un autobús no se pueden cerrar y no entran en la cuenta. Si parte son autobuses que nunca llegan, la fiabilidad real es menor.",
        "En interurbanos la llegada es aproximada (última hora anunciada antes de desaparecer del panel). Con días no vistos, la ventana acierta el 82% de las veces; en Eras-Oficina de Correos, en laborable, el 76%.",
    ],
    "cobertura_emt": {"paradas_medidas": 28, "paradas_red": 4932, "lineas_red": 236},
    "hallazgos": {
        "emt_hora_punta": {"intervalo_programado_min": 9.7, "intervalo_real_min": [9.9, 10.4], "espera_programada_min": 4.87,
                           "espera_real_min": [7.46, 8.02], "espera_de_mas_min": [2.59, 3.15], "muestra": "26 paradas céntricas, laborables del 05/10 al 20/11",
                           "fuente": "analisis/resultados/cruce_catalogo_2026-11-22.txt"},
    },
    "fuentes": {
        "Portal de Datos Abiertos de la Comunidad de Madrid": "https://datos.comunidad.madrid/catalogo/",
        "EMT Madrid, tiempo real": "https://datos.emtmadrid.es/dataset/tiempo-real-para-autobuses-de-emt",
        "Renfe, horarios de viaje": "https://data.renfe.com/dataset/horarios-viaje-cercanias",
        "Renfe, ubicación de los vehículos": "https://data.renfe.com/dataset/ubicacion-vehiculos",
        "Consorcio Regional de Transportes de Madrid": "https://www.crtm.es/aviso-legal",
    },
}


def registro(r):
    return {"p": float(r["p_acierto_2min"]), "ic": [float(r["ic95_bajo"]), float(r["ic95_alto"])], "n": int(float(r["n_llegadas"])),
            "tarde": float(r["p_tarde_mas_2min"]), "antes": float(r["p_antes_mas_2min"]), "mediana": float(r["retraso_mediano_min"]),
            "p10": float(r["retraso_p10_min"]), "p90": float(r["retraso_p90_min"])}


def absurdo(rec):
    return rec["p90"] > MAX_PERCENTIL or rec["p10"] < -MAX_PERCENTIL


def clave_linea(red, linea):
    return (linea.lstrip("0") or "0") if red == "emt" and linea.isdigit() else linea


def poner(destino, bin_, rec):
    """Guarda la casilla; si ya hay una (líneas "001" y "1"), se queda la de más llegadas."""
    if bin_ not in destino or destino[bin_]["n"] < rec["n"]:
        destino[bin_] = rec


def interurbanos(corte):
    paradas, quitadas = {}, 0
    with open(f"{RES}/ventanas_interurbanos_{corte}.csv", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            rec = {"p": float(r["p"]), "ic": [float(r["ic_bajo"]), float(r["ic_alto"])], "n": int(r["n"]),
                   "tarde": float(r["tarde"]), "antes": float(r["antes"]), "mediana": float(r["mediana"]),
                   "p10": float(r["p10"]), "p90": float(r["p90"])}
            if absurdo(rec):
                quitadas += 1
                continue
            p = paradas.setdefault(r["parada"], {"nombre": r["nombre_parada"], "lat": float(r["lat"]), "lon": float(r["lon"]), "lineas": {}})
            s = p["lineas"].setdefault(r["linea"], {}).setdefault(r["sentido"], {"destino": r["nombre_destino"], "laborable": {}, "finde": {}})
            s["laborable" if r["laborable"] == "True" else "finde"][r["minuto"]] = rec
    return {"parada": paradas}, quitadas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corte", required=True)
    corte = ap.parse_args().corte
    tabla, quitadas = {}, {}
    with open(f"{RES}/fiabilidad_{corte}.csv", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if float(r["n_llegadas"]) < MIN_LLEGADAS:
                continue
            red = tabla.setdefault(r["red"], {"red": {}, "franja": {}, "tipo": {}, "linea": {}})
            clave = f'{r["tipo_dia"]}|{r["franja"]}'
            rec = registro(r)
            if absurdo(rec):
                quitadas[r["red"]] = quitadas.get(r["red"], 0) + 1
                continue
            if r["nivel"] == "1_red":
                poner(red["red"], r["anuncio_min"], rec)
            elif r["nivel"] == "2_franja":
                poner(red["franja"].setdefault(clave, {}), r["anuncio_min"], rec)
            elif r["nivel"] == "3_tipo":
                poner(red["tipo"].setdefault(f'{r["tipo"]}|{clave}', {}), r["anuncio_min"], rec)
            else:
                poner(red["linea"].setdefault(clave_linea(r["red"], r["linea"]), {}).setdefault(clave, {}), r["anuncio_min"], rec)
    tabla["interurbano"], quitadas["interurbano"] = interurbanos(corte)
    with open(f"{RES}/fiabilidad_validacion_{corte}.txt", encoding="utf-8") as f:
        desde, hasta = re.search(r"Datos: (\S+) a (\S+)\.", f.read()).groups()
    meta = {**META, "datos_desde": desde, "datos_hasta": hasta, "corte": corte, "casillas_quitadas": quitadas,
            "licencia_salida": "ODbL, por derivar de datos de la EMT"}
    meta["cobertura_emt"] = {**META["cobertura_emt"], "lineas_medidas": len(tabla["emt"]["linea"])}
    os.makedirs("demo", exist_ok=True)
    with open(SALIDA, "w", encoding="utf-8", newline="\n") as f:
        json.dump({"meta": meta, "tabla": tabla}, f, ensure_ascii=False, separators=(",", ":"), sort_keys=False)
    print(SALIDA, os.path.getsize(SALIDA), "bytes; líneas:", {k: len(v["linea"]) for k, v in tabla.items() if "linea" in v},
          "paradas interurbano:", len(tabla["interurbano"]["parada"]), "quitadas:", quitadas)


if __name__ == "__main__":
    main()
