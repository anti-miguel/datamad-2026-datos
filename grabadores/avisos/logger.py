"""Graba cada 5 min los avisos de alteraciones del servicio de la EMT (RSS público). El RSS solo conserva unas semanas.

Salida: /data/AAAA-MM-DD.jsonl.gz, una línea por novedad, en el día en que se ve:
  {"t": epoch, "k": "aviso", "estado": "nuevo"|"cambio", "guid", "titulo", "texto", "enlace", "pub", "fin_pub",
   "desde", "hasta", "causa", "efecto", "lineas": [...]}
  pub, fin_pub, desde y hasta son epoch UTC. lineas va tal cual en el RSS, a veces con ceros delante ("002").
  {"t": epoch, "k": "baja", "guid"}: el aviso ya no está en el RSS.
  {"t": epoch, "k": "poll", "n": avisos en el RSS, "novedades": cuántas}: si no ha cambiado, "sin_cambios": 1. Si falla, "err".
Guarda en /data/estado.json la huella de cada aviso, para no repetirlos al reiniciar.
Solo biblioteca estándar.
"""
import gzip, hashlib, html, json, os, re, time, urllib.error, urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime

DATA = os.environ.get("DATA_DIR", "/data")
CICLO = int(os.environ.get("CICLO_S", "300"))
URL = os.environ.get("URL_RSS", "http://feeds.emtmadrid.es:8082/")
UA = {"User-Agent": "avisos-logger (DATAMAD 2026, investigación; 1 consulta/5 min)"}
ESTADO = os.path.join(DATA, "estado.json")


def escribir(fila):
    os.makedirs(DATA, exist_ok=True)
    with gzip.open(os.path.join(DATA, f"{datetime.now():%Y-%m-%d}.jsonl.gz"), "at", encoding="utf-8") as f:
        f.write(json.dumps(fila, ensure_ascii=False, separators=(",", ":")) + "\n")


def epoch_local(txt):
    """El RSS da desde, hasta y fin_pub en hora de Madrid: 04/11/2026 18:00:00"""
    try:
        return int(datetime.strptime(txt.strip(), "%d/%m/%Y %H:%M:%S").timestamp())
    except ValueError:
        return None


def epoch_rfc(txt):
    try:
        return int(parsedate_to_datetime(txt).timestamp())
    except (TypeError, ValueError):
        return None


def leer_avisos(xml):
    avisos = {}
    for i in ET.fromstring(xml).find("channel").findall("item"):
        g = lambda k: (i.findtext(k) or "").strip()
        guid = g("guid") or g("link")
        avisos[guid] = {
            "guid": guid, "titulo": g("title"), "texto": html.unescape(re.sub(r"<[^>]+>", " ", g("description"))).strip(),
            "enlace": g("link"), "pub": epoch_rfc(g("pubDate")), "fin_pub": epoch_local(g("rssfinaldate")),
            "desde": epoch_local(g("rssAfectaDesde")), "hasta": epoch_local(g("rssAfectaHasta")),
            "causa": g("GoogleTransitCause"), "efecto": g("GoogleTransitEffect"),
            "lineas": [c.text.strip() for c in i.findall("category") if c.text and c.text.strip()],
        }
    return avisos


def huella(aviso):
    return hashlib.sha256(json.dumps(aviso, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:16]


def cargar_estado():
    try:
        with open(ESTADO, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def guardar_estado(estado):
    tmp = ESTADO + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(estado, f)
    os.replace(tmp, ESTADO)


def pasada(estado, validadores):
    """Una consulta. Devuelve el estado nuevo; validadores recuerda ETag y Last-Modified entre consultas."""
    t = int(time.time())
    cab = dict(UA)
    if validadores.get("etag"):
        cab["If-None-Match"] = validadores["etag"]
    if validadores.get("modificado"):
        cab["If-Modified-Since"] = validadores["modificado"]
    try:
        with urllib.request.urlopen(urllib.request.Request(URL, headers=cab), timeout=30) as r:
            xml = r.read()
            nuevos_validadores = {"etag": r.headers.get("ETag"), "modificado": r.headers.get("Last-Modified")}
        avisos = leer_avisos(xml)
    except urllib.error.HTTPError as ex:
        if ex.code == 304:
            escribir({"t": t, "k": "poll", "sin_cambios": 1})
        else:
            escribir({"t": t, "k": "poll", "err": f"HTTP {ex.code}"})
        return estado
    except Exception as ex:  # sin red o XML roto: se apunta y se reintenta en el siguiente ciclo
        escribir({"t": t, "k": "poll", "err": repr(ex)[:300]})
        return estado
    nuevo, novedades = {}, 0
    for guid, aviso in avisos.items():
        h = nuevo[guid] = huella(aviso)
        if estado.get(guid) != h:
            escribir({"t": t, "k": "aviso", "estado": "cambio" if guid in estado else "nuevo", **aviso})
            novedades += 1
    for guid in estado.keys() - avisos.keys():
        escribir({"t": t, "k": "baja", "guid": guid})
        novedades += 1
    escribir({"t": t, "k": "poll", "n": len(avisos), "novedades": novedades})
    guardar_estado(nuevo)
    validadores.update(nuevos_validadores)
    return nuevo


def main():
    print(f"avisos-logger: {URL} cada {CICLO} s en {DATA}", flush=True)
    os.makedirs(DATA, exist_ok=True)
    estado, validadores = cargar_estado(), {}
    while True:
        inicio = time.time()
        estado = pasada(estado, validadores)
        time.sleep(max(1, CICLO - (time.time() - inicio)))


if __name__ == "__main__":
    main()
