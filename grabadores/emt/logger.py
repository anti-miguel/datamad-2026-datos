"""Graba cada minuto las llegadas en tiempo real de los autobuses EMT en una muestra de paradas,
con la API oficial de MobilityLabs (incluye número de autobús, distancia a la parada y posición GPS).

Credenciales: EMT_CLIENT_ID y EMT_PASSKEY (aplicación de mobilitylabs.emtmadrid.es) o EMT_EMAIL y EMT_PASSWORD (cuenta).
Nunca se escriben en el registro ni en los datos.

Salida: /data/AAAA-MM-DD.jsonl.gz, una línea por parada y consulta:
  {"t": epoch, "s": parada, "a": [[línea, autobús, segundos_estimados, distancia_m, lon, lat, tipo_posición, destino], ...]}
Posición de toda la flota: {"t": epoch, "k": "flota", "n": autobuses, "r": [registros de la colección]}.
Si falla: {"t": epoch, "s": parada, "err": "..."}. Tras cada inicio de sesión: {"t": epoch, "k": "login", "cuota_usada": n}.
Solo biblioteca estándar.
"""
import gzip, json, os, time, urllib.error, urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

DATA = os.environ.get("DATA_DIR", "/data")
CICLO = int(os.environ.get("CICLO_S", "60"))
API = "https://openapi.emtmadrid.es"
PARADAS = json.loads(os.environ.get("PARADAS_JSON") or "[]")
CLIENT_ID = os.environ.get("EMT_CLIENT_ID", "").strip()
PASSKEY = os.environ.get("EMT_PASSKEY", "").strip()
# alternativa: email y contraseña de la cuenta de MobilityLabs (cuota menor, ~20.000 consultas/día)
EMAIL = os.environ.get("EMT_EMAIL", "").strip()
PASSWORD = os.environ.get("EMT_PASSWORD", "").strip()
# colección reactiva "Posición de la Flota de Autobuses de EMT": toda la flota en una sola petición
FLOTA = os.environ.get("EMT_FLOTA_COLECCION", "ff594c7a-8a7c-423a-8a06-c14a4fac5bff")
CUERPO = json.dumps({"cultureInfo": "ES", "Text_StopRequired_YN": "N", "Text_EstimationsRequired_YN": "Y",
                     "Text_IncidencesRequired_YN": "N"}).encode()

_token = {"valor": None, "caduca": 0}


def _relleno(v):
    return bool(v) and "PEGA" not in v.upper() and "ESCRIBE" not in v.upper()


def modo_login():
    if _relleno(CLIENT_ID) and _relleno(PASSKEY):
        return "aplicacion"
    if _relleno(EMAIL) and _relleno(PASSWORD):
        return "cuenta"
    return None


def login(registro):
    cab = ({"X-ClientId": CLIENT_ID, "passKey": PASSKEY} if modo_login() == "aplicacion"
           else {"email": EMAIL, "password": PASSWORD})
    req = urllib.request.Request(f"{API}/v1/mobilitylabs/user/login/", headers=cab)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.load(r)
    except urllib.error.HTTPError as ex:  # la API devuelve sus errores con estados HTTP raros (p. ej. 405) y JSON
        try:
            d = json.load(ex)
        except ValueError:
            d = {"code": f"HTTP {ex.code}", "description": ex.reason}
    if not d.get("data") or not d["data"][0].get("accessToken"):
        motivo = {"84": "X-ClientId o passKey no válidos", "92": "usuario o contraseña incorrectos",
                  "99": "faltan credenciales"}.get(str(d.get("code")), d.get("description"))
        raise RuntimeError(f"inicio de sesión rechazado (código {d.get('code')}: {motivo})")
    datos = d["data"][0]
    _token["valor"] = datos["accessToken"]
    _token["caduca"] = time.time() + int(datos.get("tokenSecExpiration", 3600)) - 60
    registro.append({"t": int(time.time()), "k": "login", "cuota_usada": datos.get("apiCounter", {})})


def consultar(stop, registro):
    if time.time() >= _token["caduca"]:
        login(registro)
    for intento in range(2):
        req = urllib.request.Request(f"{API}/v2/transport/busemtmad/stops/{stop}/arrives/", data=CUERPO,
                                     headers={"accessToken": _token["valor"], "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                d = json.load(r)
        except urllib.error.HTTPError as ex:
            if ex.code == 401 and intento == 0:
                login(registro)
                continue
            raise
        if str(d.get("code", "")).startswith("8") and intento == 0:  # token caducado o no válido
            login(registro)
            continue
        if str(d.get("code")) not in ("00", "0", "01"):
            raise RuntimeError(f"código {d.get('code')}: {d.get('description')}"[:120])
        llegadas = (d.get("data") or [{}])[0].get("Arrive") or []
        return [[a.get("line"), a.get("bus"), a.get("estimateArrive", a.get("estimate_seconds")), a.get("DistanceBus"),
                 *((a.get("geometry") or {}).get("coordinates") or [None, None])[:2], a.get("positionTypeBus"),
                 a.get("destination")] for a in llegadas]
    raise RuntimeError("no se pudo renovar el acceso")


def _peticion(metodo, ruta, cuerpo=None):
    req = urllib.request.Request(f"{API}{ruta}", data=cuerpo, method=metodo,
                                 headers={"accessToken": _token["valor"], "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as ex:
        try:
            return json.load(ex)
        except ValueError:
            return {"code": f"HTTP {ex.code}", "description": ex.reason}


_enlace_flota = {"valor": None}


def descubrir_flota(lineas):
    """Busca el enlace de lectura de la colección de la flota y guarda su descripción una vez (para el esquema)."""
    d = _peticion("GET", f"/v1/mobilitylabs/discover/collection/{FLOTA}/")
    lineas.append(json.dumps({"t": int(time.time()), "k": "flota_descubrir", "r": d}, ensure_ascii=False)[:20000])
    enlaces = ((d.get("data") or [{}])[0].get("links") or []) if isinstance(d.get("data"), list) else []
    _enlace_flota["valor"] = (enlaces[0].get("CD_LINK") if enlaces else 1) or 1
    print(f"{datetime.now():%H:%M:%S} flota: colección {FLOTA[:8]}…, enlace {_enlace_flota['valor']} "
          f"({len(enlaces)} enlaces; código {d.get('code')})", flush=True)


def leer_flota():
    d = _peticion("POST", f"/v1/mobilitylabs/collection/reactive/{FLOTA}/{_enlace_flota['valor']}/", b"{}")
    if str(d.get("code")) not in ("00", "0"):
        raise RuntimeError(f"flota: código {d.get('code')}: {d.get('description')}"[:120])
    registros = d.get("data") or []
    for r in registros:  # quita lo decorativo (icono, HTML) y conserva el resto tal cual
        r.pop("shape", None)
        if isinstance(r.get("state"), dict):
            r["state"].pop("description", None)
    return registros


def main():
    os.makedirs(DATA, exist_ok=True)
    print(f"emt-logger: {len(PARADAS)} paradas, cada {CICLO} s -> {DATA}", flush=True)
    while not modo_login():
        print(f"{datetime.now():%H:%M:%S} faltan las claves: rellena EMT_CLIENT_ID y EMT_PASSKEY "
              f"(o EMT_EMAIL y EMT_PASSWORD) en la configuración", flush=True)
        time.sleep(600)
    # con email y contraseña la cuota es ~20.000/día: las paradas se consultan 1 de cada 3 ciclos
    cada_paradas = int(os.environ.get("PARADAS_CADA_N_CICLOS") or (1 if modo_login() == "aplicacion" else 3))
    print(f"{datetime.now():%H:%M:%S} inicio de sesión con {'aplicación (X-ClientId)' if modo_login() == 'aplicacion' else 'cuenta (email)'}; "
          f"paradas cada {cada_paradas} ciclo(s), flota cada ciclo", flush=True)
    stats, n_ciclo = [0, 0, 0, 0], 0
    while True:
        inicio = time.time()
        registro, lineas = [], []
        try:
            if time.time() >= _token["caduca"]:
                login(registro)
            if _enlace_flota["valor"] is None:
                descubrir_flota(lineas)
        except Exception as ex:
            print(f"{datetime.now():%H:%M:%S} {ex}; reintento en 5 min", flush=True)
            time.sleep(300)
            continue
        try:
            flota = leer_flota()
            lineas.append(json.dumps({"t": int(time.time()), "k": "flota", "n": len(flota), "r": flota},
                                     separators=(",", ":"), ensure_ascii=False))
            stats[3] += len(flota)
        except Exception as ex:
            lineas.append(json.dumps({"t": int(time.time()), "k": "flota", "err": f"{type(ex).__name__}: {ex}"[:120]}))
        paradas = PARADAS if n_ciclo % cada_paradas == 0 else []
        n_ciclo += 1
        paso = CICLO / max(1, len(paradas))
        futuros = []
        with ThreadPoolExecutor(max_workers=4) as pool:
            for i, (stop, _nombre) in enumerate(paradas):
                time.sleep(max(0, inicio + i * paso - time.time()))
                futuros.append((stop, int(time.time()), pool.submit(consultar, stop, registro)))
        for stop, t, fut in futuros:
            try:
                fila = {"t": t, "s": stop, "a": fut.result()}
                stats[0] += 1
                stats[1] += len(fila["a"])
            except Exception as ex:
                fila = {"t": t, "s": stop, "err": f"{type(ex).__name__}: {ex}"[:120]}
                stats[2] += 1
            lineas.append(json.dumps(fila, separators=(",", ":"), ensure_ascii=False))
        lineas += [json.dumps(r, separators=(",", ":")) for r in registro]
        path = os.path.join(DATA, datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d") + ".jsonl.gz")
        with gzip.open(path, "at", encoding="utf-8") as f:
            f.write("\n".join(lineas) + "\n")
        for r in registro:
            print(f"{datetime.now():%H:%M:%S} sesión iniciada; cuota usada hoy: {r['cuota_usada']}", flush=True)
        if int(inicio) % 600 < CICLO:
            print(f"{datetime.now():%H:%M:%S} paradas: {stats[0]} ok / {stats[2]} errores / {stats[1]} llegadas | "
                  f"flota: {stats[3]} posiciones", flush=True)
            stats = [0, 0, 0, 0]
        time.sleep(max(0, inicio + CICLO - time.time()))


if __name__ == "__main__":
    main()
