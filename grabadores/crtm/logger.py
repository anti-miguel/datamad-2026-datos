"""Graba cada minuto los tiempos de llegada del Metro de Madrid en una muestra de estaciones (7 por línea),
desde el widget público del Consorcio Regional de Transportes de Madrid. Admite también otros modos (ver PARADAS).

Salida: /data/AAAA-MM-DD.jsonl.gz, una línea por parada y consulta:
  {"t": epoch, "s": "4_47", "m": "metro", "a": [[línea, sentido, destino, llegada_epoch, codIssue], ...]}
  codIssue identifica el viaje en interurbanos (incluye su hora de salida programada); vacío en Metro y EMT.
Si la consulta falla: {"t": epoch, "s": ..., "m": ..., "err": "..."}.
También archiva una vez al día los GTFS del Consorcio en /data/gtfs/ si su contenido ha cambiado.

Paradas rotatorias (ROTAR_MODOS): además de las fijas, cada día graba ROTAR_N paradas elegidas al azar entre todas
las del GTFS, sin repetir ninguna de días anteriores. El modo va alternando (metro, ligero, interurbanos, emt...).
Sus filas llevan "r": 1. Si a las 10:00 una no ha dado ninguna llegada desde las 6:00, se cambia por otra.
Registro de las elegidas en /data/rotacion.json.
Solo biblioteca estándar.
"""
import csv, gzip, hashlib, io, json, os, random, time, urllib.request, zipfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

DATA = os.environ.get("DATA_DIR", "/data")
CICLO = int(os.environ.get("CICLO_S", "60"))  # cada parada se consulta una vez por ciclo
URL = "https://www.crtm.es/widgets/api/GetStopsTimes.php?codStop={}&type=1&orderBy=2&stopTimesByIti=3"
UA = {"User-Agent": "crtm-logger (DATAMAD 2026, investigación; 1 consulta/parada/min)"}

# muestra: ~7 estaciones por línea de Metro repartidas por el recorrido (GTFS del Consorcio), comprobando
# que el widget devuelve tiempos. La EMT se graba aparte con la API oficial (emt-logger).
PARADAS = json.loads(os.environ.get("PARADAS_JSON") or "[]")

GTFS = {  # ArcGIS del Consorcio (enlazados desde datos.comunidad.madrid)
    "metro": "5c7f2951962540d69ffe8f640d94c246",
    "ligero": "aaed26cc0ff64b0c947ac0bc3e033196",
    "interurbanos": "885399f83408473c8d815e40c5e702b7",
    "emt": "868df0e58fca47e79b942902dffd7da0",
}
GTFS_CADA = 24 * 3600

ROTAR_MODOS = [m.strip() for m in os.environ.get("ROTAR_MODOS", "").split(",") if m.strip() in GTFS]
ROTAR_N = int(os.environ.get("ROTAR_N", "1"))
ROTACION = os.path.join(DATA, "rotacion.json")


def epoch(iso):
    try:
        return int(datetime.fromisoformat(iso).timestamp())
    except (TypeError, ValueError):
        return None


def consultar(stop):
    req = urllib.request.Request(URL.format(stop), headers=UA)
    with urllib.request.urlopen(req, timeout=20) as r:
        d = json.load(r)["stopTimes"]
    t = d.get("times") or {}
    lista = t.get("Time", []) if isinstance(t, dict) else []
    lista = lista if isinstance(lista, list) else [lista]
    return [[x.get("line", {}).get("shortDescription"), x.get("direction"),
             x.get("destinationStop", {}).get("codStop"), epoch(x.get("time")), x.get("codIssue") or ""]
            for x in lista]


def archivar_gtfs():
    carpeta = os.path.join(DATA, "gtfs")
    os.makedirs(carpeta, exist_ok=True)
    huellas = set()
    for n in os.listdir(carpeta):
        if n.endswith(".zip"):
            with open(os.path.join(carpeta, n), "rb") as f:
                huellas.add(hashlib.sha256(f.read()).hexdigest())
    modos = {m for m, _s, _n in PARADAS} | set(ROTAR_MODOS)  # solo el horario de los transportes que se graban
    for nombre, item in GTFS.items():
        if nombre not in modos:
            continue
        try:
            url = f"https://www.arcgis.com/sharing/rest/content/items/{item}/data"
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=600) as r:
                datos = r.read()
            sha = hashlib.sha256(datos).hexdigest()
            if sha in huellas:
                continue
            destino = os.path.join(carpeta, f"{nombre}_{datetime.now():%Y-%m-%d}_{sha[:8]}.zip")
            with open(destino, "wb") as f:
                f.write(datos)
            print(f"{datetime.now():%H:%M:%S} GTFS archivado: {os.path.basename(destino)} "
                  f"({len(datos) // 1_000_000} MB)", flush=True)
        except Exception as ex:  # no debe parar la grabación
            print(f"{datetime.now():%H:%M:%S} no se pudo archivar el GTFS {nombre}: {ex}", flush=True)


def paradas_gtfs(modo):
    """Paradas (código del widget, nombre) del GTFS más reciente archivado de ese modo."""
    carpeta = os.path.join(DATA, "gtfs")
    zips = sorted((os.path.getmtime(os.path.join(carpeta, n)), n) for n in os.listdir(carpeta)
                  if n.startswith(modo + "_") and n.endswith(".zip"))
    if not zips:
        return []
    out = []
    with zipfile.ZipFile(os.path.join(carpeta, zips[-1][1])) as z:
        for r in csv.DictReader(io.TextIOWrapper(z.open("stops.txt"), encoding="utf-8-sig")):
            if (r.get("location_type") or "0") != "0":
                continue
            sid = r["stop_id"].strip()
            if sid.startswith("par_"):
                sid = sid[4:]  # par_4_189 -> 4_189
            elif modo == "emt" and sid.isdigit():
                sid = "6_" + sid  # el GTFS de la EMT no lleva prefijo
            else:
                continue
            out.append((sid, r.get("stop_name", "").strip()))
    return out


def leer_rotacion():
    try:
        with open(ROTACION, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {"usadas": []}


def guardar_rotacion(rot):
    tmp = ROTACION + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(rot, f, ensure_ascii=False, indent=1)
    os.replace(tmp, ROTACION)


def elegir(rot, hoy, motivo):
    """Añade una parada nueva (nunca usada ni fija) a las de hoy, alternando el modo."""
    vetadas = {s for _m, s, _n in PARADAS} | {u["s"] for u in rot["usadas"]}
    for k in range(len(ROTAR_MODOS)):
        modo = ROTAR_MODOS[(len(rot["usadas"]) + k) % len(ROTAR_MODOS)]
        libres = [p for p in paradas_gtfs(modo) if p[0] not in vetadas]
        if libres:
            s, nombre = random.choice(libres)
            rot["usadas"].append({"fecha": hoy, "m": modo, "s": s, "nombre": nombre, "motivo": motivo,
                                  "consultas": 0, "llegadas": 0})
            print(f"{datetime.now():%H:%M:%S} parada rotatoria {hoy}: {modo} {s} {nombre} "
                  f"(quedan {len(libres) - 1} sin grabar en {modo})", flush=True)
            return True
    print(f"{datetime.now():%H:%M:%S} sin paradas libres para rotar (¿falta el GTFS?)", flush=True)
    return False


def rotatorias(rot, hoy):
    """Las paradas rotatorias de hoy: elige las que falten y cambia las que no dan datos."""
    if not ROTAR_MODOS:
        return []
    de_hoy = [u for u in rot["usadas"] if u["fecha"] == hoy and not u.get("descartada")]
    cambio = False
    if datetime.now().hour >= 10:
        for u in de_hoy:
            if u["llegadas"] == 0 and u["consultas"] >= 60:
                u["descartada"] = "sin llegadas entre las 6:00 y las 10:00"
                cambio = True
    de_hoy = [u for u in de_hoy if not u.get("descartada")]
    while len(de_hoy) < ROTAR_N and elegir(rot, hoy, "reemplazo" if cambio else "diaria"):
        de_hoy.append(rot["usadas"][-1])
        cambio = True
    if cambio:
        guardar_rotacion(rot)
    return de_hoy


def main():
    os.makedirs(DATA, exist_ok=True)
    print(f"crtm-logger: {len(PARADAS)} paradas fijas + {ROTAR_N if ROTAR_MODOS else 0} rotatoria(s) al día "
          f"({','.join(ROTAR_MODOS) or 'sin rotación'}), cada {CICLO} s -> {DATA}", flush=True)
    ultimo_gtfs, stats = 0, {}
    rot = leer_rotacion()
    while True:
        inicio = time.time()
        if inicio - ultimo_gtfs >= GTFS_CADA:
            archivar_gtfs()
            ultimo_gtfs = inicio = time.time()
        rotar = rotatorias(rot, datetime.now().strftime("%Y-%m-%d"))
        lista = [(m, s, 0) for m, s, _n in PARADAS] + [(u["m"], u["s"], 1) for u in rotar]
        # ritmo fijo (una petición cada CICLO/len s) y hasta 4 en curso, porque cada respuesta tarda ~1,5 s
        paso = CICLO / max(1, len(lista))
        futuros = []
        with ThreadPoolExecutor(max_workers=4) as pool:
            for i, (modo, stop, r) in enumerate(lista):
                time.sleep(max(0, inicio + i * paso - time.time()))
                futuros.append((modo, stop, r, int(time.time()), pool.submit(consultar, stop)))
        lineas = []
        for modo, stop, r, t, fut in futuros:
            st = stats.setdefault(modo, [0, 0, 0])
            try:
                fila = {"t": t, "s": stop, "m": modo, "a": fut.result()}
                st[0] += 1
                st[1] += len(fila["a"])
            except Exception as ex:
                fila = {"t": t, "s": stop, "m": modo, "err": f"{type(ex).__name__}: {ex}"[:120]}
                st[2] += 1
            if r:
                fila["r"] = 1
                if datetime.now().hour >= 6:  # de madrugada es normal que no haya llegadas
                    u = next(u for u in rotar if u["s"] == stop)
                    u["consultas"] += 1
                    u["llegadas"] += len(fila.get("a", []))
            lineas.append(json.dumps(fila, separators=(",", ":"), ensure_ascii=False))
        path = os.path.join(DATA, datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d") + ".jsonl.gz")
        with gzip.open(path, "at", encoding="utf-8") as f:  # cada escritura es un miembro gzip válido
            f.write("\n".join(lineas) + "\n")
        if int(inicio) % 600 < CICLO:  # resumen cada 10 min
            resumen = ", ".join(f"{m}: {v[0]} ok / {v[2]} err / {v[1]} llegadas" for m, v in sorted(stats.items()))
            print(f"{datetime.now():%H:%M:%S} {resumen}", flush=True)
            stats = {}
            if rotar:
                guardar_rotacion(rot)


if __name__ == "__main__":
    main()
