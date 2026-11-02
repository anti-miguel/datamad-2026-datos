"""Descarga los horarios impresos (PDF) del Consorcio para todas las líneas de EMT e interurbanos del GTFS.

Dirección: https://www.crtm.es/datos_lineas/horarios/{6|8}{código}H{1|2}.pdf (6 = EMT por route_id, 8 = interurbanos
por número de línea). Ritmo lento (una petición cada 2 s); /datos_lineas/ está permitido en robots.txt.
"""
import csv, json, os, time, urllib.error, urllib.request

BASE = "https://www.crtm.es/datos_lineas/horarios/{}H{}.pdf"
UA = {"User-Agent": "Mozilla/5.0 (DATAMAD 2026, investigacion; 1 peticion/2 s)"}
GTFS = "../gtfs_crtm"
os.makedirs("pdf", exist_ok=True)

codigos = []
with open(f"{GTFS}/emt/routes.txt", encoding="utf-8-sig") as f:
    codigos += [("emt", r["route_short_name"], "6" + r["route_id"]) for r in csv.DictReader(f)]
with open(f"{GTFS}/interurbanos/routes.txt", encoding="utf-8-sig") as f:
    codigos += [("interurbanos", r["route_short_name"], "8" + r["route_short_name"]) for r in csv.DictReader(f)]

estado = json.load(open("estado.json")) if os.path.exists("estado.json") else {}
for i, (red, linea, cod) in enumerate(codigos):
    for sentido in (1, 2):
        nombre = f"{cod}H{sentido}"
        if nombre in estado:
            continue
        try:
            with urllib.request.urlopen(urllib.request.Request(BASE.format(cod, sentido), headers=UA), timeout=40) as r:
                datos = r.read()
            open(f"pdf/{nombre}.pdf", "wb").write(datos)
            estado[nombre] = {"red": red, "linea": linea, "sentido": sentido, "bytes": len(datos)}
        except urllib.error.HTTPError as ex:
            estado[nombre] = {"red": red, "linea": linea, "sentido": sentido, "http": ex.code}
        except Exception as ex:  # se reintenta en la siguiente pasada
            print(nombre, "error", ex, flush=True)
        json.dump(estado, open("estado.json", "w"))
        time.sleep(2)
    if i % 50 == 0:
        print(f"{i}/{len(codigos)} líneas; PDF descargados: {sum('bytes' in v for v in estado.values())}", flush=True)
print("fin:", sum("bytes" in v for v in estado.values()), "PDF;", sum("http" in v for v in estado.values()), "sin PDF")
