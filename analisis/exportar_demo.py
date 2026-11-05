"""Convierte la tabla de fiabilidad en demo/fiabilidad.json, lista para usarla desde una web sin servidor.

Solo incluye grupos con al menos 30 llegadas, los únicos que usa analisis/fiabilidad.py. Consulta en demo/consultar.js.
Uso, desde la raíz de datos-transporte: python analisis/exportar_demo.py
"""
import csv, json, os, re

CSV = "analisis/resultados/fiabilidad.csv"
VALIDACION = "analisis/resultados/fiabilidad_validacion.txt"
SALIDA = "demo/fiabilidad.json"
MIN_LLEGADAS = 30
ORDEN_BINS = ["0-3", "3-6", "6-10", "10-15", "15-25", "25-40"]

META = {
    "pregunta": "Si el operador anuncia X minutos, ¿con qué probabilidad llega a ±2 min de lo anunciado?",
    "min_llegadas": MIN_LLEGADAS,
    "anuncio_min": [[0, 3, "0-3"], [3, 6, "3-6"], [6, 10, "6-10"], [10, 15, "10-15"], [15, 25, "15-25"], [25, 40, "25-40"]],
    "franjas": {"punta_manana": [7, 9.5], "valle": [9.5, 17], "punta_tarde": [17, 20], "noche": "el resto"},
    "orden_consulta": ["linea", "tipo", "franja", "red"],
    "campos": {"p": "probabilidad de llegar a ±2 min", "ic": "intervalo de confianza del 95%", "n": "llegadas medidas",
               "tarde": "probabilidad de llegar más de 2 min tarde", "antes": "probabilidad de llegar más de 2 min antes",
               "mediana": "retraso mediano, en minutos", "p10": "retraso, percentil 10", "p90": "retraso, percentil 90"},
    "redes": {
        "emt": {"nombre": "EMT Madrid", "medida": "posición y estimación del autobús", "licencia": "ODbL",
                "atribucion": "Powered by EMT de Madrid", "complemento": False},
        "renfe": {"nombre": "Cercanías Renfe", "medida": "GPS del tren", "licencia": "CC BY 4.0",
                  "atribucion": "Fuente: Renfe", "complemento": False},
        "metro": {"nombre": "Metro de Madrid", "medida": "el tren desaparece del panel; puede dar aciertos de más",
                  "licencia": "sin licencia publicada para tiempo real", "atribucion": "Fuente: Consorcio Regional de Transportes de Madrid",
                  "complemento": True},
    },
    "sin_dato": ["interurbanos: su panel no da una llegada real", "Metro a 25 min o más", "anuncios de 40 min o más"],
    "advertencias": [
        "En paradas no medidas la tabla es optimista en la parte alta: en la EMT dice 93% y ocurre 83%.",
        "En la EMT, el 35% de las visitas de un autobús no se pueden cerrar y no entran en la cuenta. Si parte son autobuses que nunca llegan, la fiabilidad real es menor.",
    ],
    "cobertura_emt": {"paradas_medidas": 28, "paradas_red": 4932, "lineas_medidas": 96, "lineas_red": 236},
    "hallazgos": {
        "emt_hora_punta": {"intervalo_programado_min": [9.7, 9.8], "intervalo_real_min": [9.8, 10.3], "espera_programada_min": 4.9,
                           "espera_real_min": [7.2, 7.7], "espera_de_mas_min": [2.3, 2.9], "muestra": "26 paradas céntricas, laborables del 05/10 al 04/11",
                           "fuente": "analisis/resultados/cruce_catalogo.txt"},
    },
    "fuentes": {
        "Portal de Datos Abiertos de la Comunidad de Madrid": "https://datos.comunidad.madrid/catalogo/",
        "EMT Madrid, tiempo real": "https://datos.emtmadrid.es/dataset/tiempo-real-para-autobuses-de-emt",
        "Renfe, horarios de viaje": "https://data.renfe.com/dataset/horarios-viaje-cercanias",
        "Renfe, ubicación de los vehículos": "https://data.renfe.com/dataset/ubicacion-vehiculos",
    },
}


def registro(r):
    return {"p": float(r["p_acierto_2min"]), "ic": [float(r["ic95_bajo"]), float(r["ic95_alto"])], "n": int(float(r["n_llegadas"])),
            "tarde": float(r["p_tarde_mas_2min"]), "antes": float(r["p_antes_mas_2min"]), "mediana": float(r["retraso_mediano_min"]),
            "p10": float(r["retraso_p10_min"]), "p90": float(r["retraso_p90_min"])}


def main():
    tabla = {}
    with open(CSV, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if float(r["n_llegadas"]) < MIN_LLEGADAS:
                continue
            red = tabla.setdefault(r["red"], {"red": {}, "franja": {}, "tipo": {}, "linea": {}})
            clave = f'{r["tipo_dia"]}|{r["franja"]}'
            rec = registro(r)
            if r["nivel"] == "1_red":
                red["red"][r["anuncio_min"]] = rec
            elif r["nivel"] == "2_franja":
                red["franja"].setdefault(clave, {})[r["anuncio_min"]] = rec
            elif r["nivel"] == "3_tipo":
                red["tipo"].setdefault(f'{r["tipo"]}|{clave}', {})[r["anuncio_min"]] = rec
            else:
                red["linea"].setdefault(r["linea"], {}).setdefault(clave, {})[r["anuncio_min"]] = rec
    with open(VALIDACION, encoding="utf-8") as f:
        desde, hasta = re.search(r"Datos: (\S+) a (\S+)\.", f.read()).groups()
    salida = {"meta": {**META, "datos_desde": desde, "datos_hasta": hasta, "licencia_salida": "ODbL, por derivar de datos de la EMT"}, "tabla": tabla}
    os.makedirs("demo", exist_ok=True)
    with open(SALIDA, "w", encoding="utf-8", newline="\n") as f:
        json.dump(salida, f, ensure_ascii=False, separators=(",", ":"), sort_keys=False)
    print(SALIDA, os.path.getsize(SALIDA), "bytes;", {k: len(v["linea"]) for k, v in tabla.items()}, "líneas")


if __name__ == "__main__":
    main()
