"""Graba los avisos de alteraciones del servicio: el RSS público de la EMT cada 5 min (solo conserva unas semanas) y la web
del Consorcio cada 15 min (avisos por red y semáforo del estado de cada red).

Salida: /data/AAAA-MM-DD.jsonl.gz, una línea por novedad, en el día en que se ve:
  {"t": epoch, "k": "aviso", "estado": "nuevo"|"cambio", "guid", "titulo", "texto", "enlace", "pub", "fin_pub",
   "desde", "hasta", "causa", "efecto", "lineas": [...]}
  pub, fin_pub, desde y hasta son epoch UTC. lineas va tal cual en el RSS, a veces con ceros delante ("002").
  {"t": epoch, "k": "baja", "guid"}: el aviso ya no está en el RSS.
  {"t": epoch, "k": "poll", "n": avisos en el RSS, "novedades": cuántas}: si no ha cambiado, "sin_cambios": 1. Si falla, "err".
Del Consorcio, solo los cambios:
  {"t": epoch, "k": "estado_red", "redes": {"Metro": "Amarillo", ...}}: el semáforo de cada red.
  {"t": epoch, "k": "aviso_crtm", "red", "estado": "nuevo"|"cambio", "id", "fecha", "titulo", "texto", "nivel", "enlace"}
  {"t": epoch, "k": "baja_crtm", "red", "id"}: el aviso ya no está publicado.
  {"t": epoch, "k": "poll_crtm", "novedades": cuántas}: con "err" si falla alguna página.
Condiciones del Consorcio (crtm.es/aviso-legal): no alterar la información, citar la fuente e indicar la fecha de extracción.
Guarda en /data/estado.json y /data/estado_crtm.json la huella de cada aviso, para no repetirlos al reiniciar.
Solo biblioteca estándar.
"""
import gzip, hashlib, html, json, os, re, time, urllib.error, urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime

DATA = os.environ.get("DATA_DIR", "/data")
CICLO = int(os.environ.get("CICLO_S", "300"))
CICLO_CRTM = int(os.environ.get("CICLO_CRTM_S", "900"))
URL = os.environ.get("URL_RSS", "http://feeds.emtmadrid.es:8082/")
UA = {"User-Agent": "avisos-logger (DATAMAD 2026, investigación; consultas cada 5 y 15 min)"}
ESTADO = os.path.join(DATA, "estado.json")
ESTADO_CRTM = os.path.join(DATA, "estado_crtm.json")
CRTM_BASE = os.environ.get("URL_CRTM", "https://www.crtm.es/comunicacion/actualidad-del-servicio/avisos")
CRTM_PAGINAS = {"metro": "/avisos-metro", "metro_ligero": "/avisos-metro-ligero", "cercanias": "/avisos-cercanias",
                "emt": "/avisos-emt", "interurbanos": "/avisos-interurbanos"}


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


def cargar_estado(ruta=ESTADO):
    try:
        with open(ruta, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def guardar_estado(estado, ruta=ESTADO):
    tmp = ruta + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(estado, f)
    os.replace(tmp, ruta)


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


def texto_html(h):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", h))).strip()


def leer_crtm(pagina):
    """(estado de cada red, avisos) de una página de avisos del Consorcio, sin lo que tiene comentado."""
    p = re.sub(r"<!--.*?-->", "", re.sub(r"<script.*?</script>|<style.*?</style>", "", pagina, flags=re.S | re.I), flags=re.S)
    i = p.find("Estado del sistema de transporte")
    if i < 0:
        raise ValueError("página sin estado del sistema")
    fin = p.find("<ul", i)
    estado = dict(re.findall(r"Estado_([A-Za-z]+)_([A-Za-z]+)\.png", p[i:fin if fin > 0 else i + 6000]))
    avisos = {}
    trozos = list(re.finditer(r'<h3 id="([^"]+)"[^>]*>(.*?)</h3>', p, flags=re.S))
    for n, m in enumerate(trozos):
        ident = html.unescape(m.group(1)).strip()
        hasta = trozos[n + 1].start() if n + 1 < len(trozos) else len(p)
        cuerpo = p[m.end():hasta]
        corte = re.search(r"Vol?ver(?:\s|&nbsp;|<[^>]+>)+a(?:\s|&nbsp;|<[^>]+>)+Avisos", cuerpo)
        cuerpo = cuerpo[:corte.start()] if corte else cuerpo
        # el icono del aviso va justo antes de su título
        nivel = re.findall(r"Estado_[A-Za-z]+_([A-Za-z]+)\.png", p[max(0, m.start() - 400):m.start()])
        fecha = re.match(r"(\d\d)_(\d\d)_(\d{4})", ident)
        enlaces = [a for a, txt in re.findall(r'<a\b[^>]*?href="\s*([^"#\s][^"]*?)\s*"[^>]*>(.*?)</a>', cuerpo, flags=re.S) if "inf" in txt.lower()]
        texto = re.sub(r"^Avisos (Metro Ligero|Metro|Cercan[ií]as|EMT|Interurbanos)\s+", "", texto_html(cuerpo))
        avisos[ident] = {"id": ident, "fecha": f"{fecha[3]}-{fecha[2]}-{fecha[1]}" if fecha else None, "titulo": texto_html(m.group(2)),
                         "texto": re.sub(r"\s*Más\s*inf\s*ormación\s*\.*\s*$", "", texto).strip(),
                         "nivel": nivel[-1] if nivel else None, "enlace": html.unescape(enlaces[-1]) if enlaces else None}
    return estado, avisos


def pasada_crtm(estado):
    """Una consulta de las páginas de avisos. Una página que falla no da de baja sus avisos."""
    t = int(time.time())
    vistos, redes, errores, novedades = dict(estado.get("avisos", {})), {}, [], 0
    for red, ruta in CRTM_PAGINAS.items():
        try:
            with urllib.request.urlopen(urllib.request.Request(CRTM_BASE + ruta + "/", headers=UA), timeout=30) as r:
                est, avisos = leer_crtm(r.read().decode("utf-8", "replace"))
        except Exception as ex:
            errores.append(f"{red}: {ex!r}"[:200])
            continue
        redes = redes or est  # todas las páginas traen el mismo semáforo
        prefijo = red + "|"
        for ident, aviso in avisos.items():
            clave, h = prefijo + ident, huella(aviso)
            if vistos.get(clave) != h:
                escribir({"t": t, "k": "aviso_crtm", "red": red, "estado": "cambio" if clave in vistos else "nuevo", **aviso})
                vistos[clave] = h
                novedades += 1
        for clave in [c for c in vistos if c.startswith(prefijo) and c[len(prefijo):] not in avisos]:
            escribir({"t": t, "k": "baja_crtm", "red": red, "id": clave[len(prefijo):]})
            del vistos[clave]
            novedades += 1
    if redes and redes != estado.get("redes"):
        escribir({"t": t, "k": "estado_red", "redes": redes})
        novedades += 1
    fila = {"t": t, "k": "poll_crtm", "novedades": novedades}
    if errores:
        fila["err"] = errores
    escribir(fila)
    nuevo = {"avisos": vistos, "redes": redes or estado.get("redes", {})}
    guardar_estado(nuevo, ESTADO_CRTM)
    return nuevo


def main():
    print(f"avisos-logger: {URL} cada {CICLO} s y {CRTM_BASE} cada {CICLO_CRTM} s en {DATA}", flush=True)
    os.makedirs(DATA, exist_ok=True)
    estado, validadores = cargar_estado(), {}
    estado_crtm, ultimo_crtm = cargar_estado(ESTADO_CRTM), 0
    while True:
        inicio = time.time()
        estado = pasada(estado, validadores)
        if inicio - ultimo_crtm >= CICLO_CRTM:
            ultimo_crtm = inicio
            try:
                estado_crtm = pasada_crtm(estado_crtm)
            except Exception as ex:  # que un fallo aquí no pare el RSS de la EMT
                escribir({"t": int(inicio), "k": "poll_crtm", "err": [repr(ex)[:300]]})
        time.sleep(max(1, CICLO - (time.time() - inicio)))


if __name__ == "__main__":
    main()
