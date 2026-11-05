# Datos de transporte de Madrid

Paquete de trabajo del equipo para DATAMAD 2026. Reúne lo que hemos medido sobre si el transporte público de Madrid cumple lo que anuncia:
- si el tren o el bus llega cuando dice la app o el panel,
- cuándo se cae la información en tiempo real,
- cómo influyen la lluvia y el tráfico.

De momento el planteamiento es una **app**. Todavía no hay nombre de proyecto. Los nombres de algunos ficheros (`llego...`) son provisionales.

**El repo se actualiza solo.** Cada noche, desde las 4:00, la NAS sube los días ya cerrados de los grabadores: haz `git pull` para tenerlos. Las cifras, la tabla de fiabilidad y `catalogo.json` no se regeneran solas y se calcularon con datos hasta el 03/11. El día en curso nunca está en el repo.

Si vas a usar un agente de IA, que empiece por [AGENTS.md](AGENTS.md). [catalogo.json](catalogo.json) describe cada conjunto de datos de forma legible por máquina.

## Qué hay

```
datos-transporte/
├── README.md, AGENTS.md, catalogo.json
├── cargar.py                  funciones para leer cualquier fuente (devuelve dicts o DataFrames de pandas)
├── datos/
│   ├── renfe/                 Cercanías Madrid, GPS y retrasos cada 30 s   23/09 → 03/11   264 MB
│   ├── emt/                   EMT, "llega en X" de 28 paradas cada ~3 min  04/10 → 03/11   124 MB
│   ├── crtm/                  Metro e interurbanos (widget del Consorcio)   02/10 → 03/11   169 MB
│   ├── trafico/               4.100 puntos de medida + incidencias           14/10 → 03/11   160 MB
│   ├── avisos/                alteraciones de servicio: EMT y Consorcio      desde 04/11
│   ├── catalogo_cm/           copia de datasets del portal de la Comunidad (CC BY)
│   ├── meteo/                 lluvia horaria (Open-Meteo)
│   ├── redes/                 menciones públicas a los operadores en X (solo agregados)
│   ├── externos/              histórico de Cercanías de toda España (rodalies-observatorio, CC BY 4.0)
│   └── horarios_oficiales/    GTFS de Renfe y del Consorcio + 1.180 horarios impresos en PDF
├── grabadores/                código de los 5 grabadores que corren en la NAS (Docker)
├── analisis/                  scripts de análisis y sus resultados en texto
├── demo/                      tabla de fiabilidad en JSON y su consulta, para la web
└── documentos/                propuesta, sprint 1, prototipo HTML
```

Son unos 1.000 MB en total. 345 MB corresponden a los horarios oficiales.

**Lo que no está en el paquete:**
- **Credenciales.** El `docker-compose.yml` de la EMT trae marcadores (`ESCRIBE_AQUI_...`), no claves.
- **Datos personales.** De X solo hay recuentos por hora y tema, sin usuarios ni textos.

## Cómo empezar

Requiere Python 3.10 o superior. Para las funciones de DataFrame hace falta `pandas`.

```python
import cargar                         # desde la carpeta datos-transporte
cargar.dias("emt")                    # días disponibles
df = cargar.emt("2026-10-15")         # una fila por autobús anunciado en cada consulta
df = cargar.crtm("2026-10-15")        # una fila por llegada anunciada (Metro e interurbanos)
df = cargar.renfe_posiciones("2026-10-15")
df = cargar.renfe_retrasos("2026-10-15")
df = cargar.trafico("2026-10-15")     # una fila por punto de medida y lectura
df = cargar.avisos()                  # última versión de cada aviso de la EMT
for fila in cargar.filas("renfe", "2026-10-15"): ...   # filas crudas
```

**Formato de los ficheros:**
- Un fichero por día: `AAAA-MM-DD.jsonl.gz`, en JSON Lines comprimido con gzip.
- El día es el de Madrid, y el fichero puede empezar unos segundos antes de medianoche.
- `t` es siempre el epoch (UTC) de la consulta.
- `cargar.py` añade la columna `hora` en hora de Madrid.

## Las fuentes, una a una

### 1. Renfe Cercanías Madrid (`datos/renfe/`)

- **Origen:** feeds abiertos GTFS-RT de Renfe (CC BY 4.0), `vehicle_positions.json` y `trip_updates.json`.
- **Cadencia:** una consulta cada 30 s.
- **Cobertura:** el grabador guarda todos los trenes del núcleo de Madrid.
- **Volumen:** 28 días, 10,5 M filas.

| `k` | Qué es | Campos |
|---|---|---|
| `vp` | posición de un tren | `trip`, `stop` (estación), `st` (`STOPPED_AT`, `INCOMING_AT`, `IN_TRANSIT_TO`), `ts` (marca del GPS, epoch en texto), `lat`, `lon`, `lbl` (p. ej. `C2-21642-PLATF.(2)`: línea, tren y vía) |
| `tu` | retraso anunciado | `trip`, `rel` (`SCHEDULED`, `CANCELED`...), `delay` (s), `stops` = lista `[estación, retraso_s, relación]` |
| `poll` | control de cada consulta | `vp_n`, `tu_n` (trenes de Madrid), `vp_total`, `tu_total` (de toda España), `vp_hdr` (marca del feed), `*_retries`, `*_err` |

```json
{"t":1792447201,"k":"vp","trip":"1090L21642C2","stop":"70107","st":"STOPPED_AT","ts":"1792447192","lat":40.50538,"lon":-3.3352833,"lbl":"C2-21642-PLATF.(2)"}
{"t":1792015202,"k":"tu","trip":"1085X20520C4b","rel":"SCHEDULED","delay":-85500,"stops":[["37012",-85500,null]]}
```

- Para cruzar `trip` y `stop` con horarios y nombres de estación, usa `datos/horarios_oficiales/renfe_gtfs_*.zip`.
- `ultima_version.txt` no está incluido. Solo indicaba cuándo cambió el GTFS en la NAS.

**Ojo:**
- Hay retrasos de alrededor de −86.400 s: son viajes del día anterior o siguiente. Hay que filtrarlos.
- En los túneles no hay GPS. Para estimar el paso por una estación se toma el punto medio entre la última posición antes del túnel y la primera después.
- **29/10:** el grabador consultó con normalidad, pero el feed de Renfe solo daba unos 10–50 trenes de Madrid durante todo el día, frente a unos 100–130 de un día normal. No sabemos la causa.
- **Horarios:** cada versión del GTFS de Renfe llega unas semanas por delante. La NAS sube la más reciente como mucho una vez por semana, en `datos/horarios_oficiales/`.
- **Caídas de Renfe:** la información en tiempo real de Renfe falló (feed vacío o congelado):
  - 26/09
  - 28/09, 05:00–10:31
  - 30/09, 05:00–10:42
  - 03/10
  - 20/10, 10:08–10:31
  - 29/10, 08:50–09:10

  En esos ratos el grabador funcionaba. Lo que falla es el dato de Renfe, y eso es justo lo que queremos detectar.

### 2. EMT, autobuses de Madrid (`datos/emt/`)

- **Origen:** API MobilityLabs de la EMT, endpoint de llegadas por parada.
- **Cadencia:** cada ~3 min.
  - Con cuenta de email la cuota es de ~20.000 consultas/día, así que cada parada se consulta 1 de cada 3 ciclos.
- **Cobertura:** 28 paradas.
  - 25 desde el 04/10, en Cibeles, Atocha, Prado, Neptuno, Castellana, Bernabéu, Plaza de España, Ciudad Lineal...
  - 3 del 104 desde el 06/10: 5848 (cabecera de Mar de Cristal), 4900 y 4897.
- **Volumen:** 386.000 consultas.

| Fila | Contenido |
|---|---|
| consulta | `{"t","s": parada,"a": [[línea, nº autobús, llega_en_s, distancia_m, lon, lat, tipo_posición, destino], ...]}` |
| `k:"login"` | inicio de sesión en la API (sin credenciales) |
| `k:"flota"`, `k:"flota_descubrir"` | intento de leer la flota completa: siempre da HTTP 404. Se puede ignorar |
| `k:"err"` | error de una consulta (timeouts, etc.) |

```json
{"t":1792447259,"s":"82","a":[["N12",5588,1017,4208,-3.6950182,40.3908577,"0","CIBELES"], ...]}
```

- **`llega_en_s` = 999999 u 888888 no son segundos:** son esperas demasiado largas para dar minutos, y hay que filtrarlos antes de calcular nada. Antes decíamos que 999999 era "más de 20 min". Era un error.
  - **999999:** más de 45 min, en líneas diurnas. La app de la EMT muestra `>45`.
  - **888888:** líneas nocturnas. La app de la EMT muestra `>90`, y la API no lo documenta: dice que 999999 cubre también las nocturnas.
  - **En nuestros datos** cada código sale solo en su tipo de línea (140.939 filas de 999999 en diurnas y 143.227 de 888888 en nocturnas, ninguna cruzada).
  - **El límite real:** las diurnas casi nunca dan minutos por encima de 45 (166 filas). Las nocturnas casi nunca pasan de 60 (693 filas), así que en ellas el cambio parece estar en ~60 min, no en 90.
  - **Su distancia no siempre es real:** el 20% de estas filas marca 360–400 m, pero el GPS de esos autobuses está a unos 5 km de la parada (mediana). Casi todas tienen `tipo_posición` 3 y salen al empezar el servicio.
- `tipo_posición` es el campo `positionTypeBus` de la EMT. Casi siempre vale `"0"` y a veces `"3"`; con `"3"` la distancia puede no ser real.
- La lista de paradas con nombre está en `grabadores/emt/docker-compose.yml`. Esa copia tiene las 25 iniciales; las 3 del 104 se añadieron directamente en la NAS.

**Cómo reconstruimos la llegada real:** por cada autobús (parada, línea, nº de autobús), la última consulta en la que aparecía a ≤120 s y ≤600 m. En la tabla de fiabilidad esa consulta no vale si la distancia es negativa o `tipo_posición` es 3; sus minutos sí cuentan como anuncios. En cabeceras se usa ≤400 s para las salidas.

**Ojo:** el 20/10 la EMT no dio datos en dos ratos:
- de 14:24 a 14:42;
- de 17:58 al 21/10 a las ~07:10. Empieza con timeouts y errores, y después las respuestas llegan vacías, también las de los autobuses nocturnos.

Esa tarde el Consorcio también falló: casi solo errores de 17:20 a 18:30 y de 19:10 a 19:30. El tráfico grabó con normalidad, así que la NAS seguía en marcha. Las respuestas vacías de la EMT desde las ~19:30, con el Consorcio ya normal, apuntan a la EMT. Antes decíamos que el Consorcio y el tráfico pararon ~2 h a las 21:50 y que Renfe estuvo parada el 06/10. Era un error: los ficheros de este paquete estaban cortados y ya están completos. Entre el 04/10 y el 19/10, y del 21/10 al 02/11, no hubo ninguna caída diurna de 20 min o más.

### 3. Consorcio: Metro e interurbanos (`datos/crtm/`)

- **Origen:** el widget público de tiempos de paso del Consorcio (`GetStopsTimes.php?codStop=...`).
- **Volumen:** 1,8 M filas.
- **Cobertura:**

| Modo | Paradas | Periodo |
|---|---|---|
| Metro (`4_`) | 62 estaciones fijas | 02/10 → 03/11 |
| Interurbanos 212 (`8_`) | 6 (Canillejas ⇄ Barajas ⇄ Paracuellos) | 09/10 → 03/11 |
| Interurbanos 691 (`8_`) | 6 (Moncloa ⇄ Collado Villalba ⇄ Navacerrada) | 14/10 → 03/11 |
| Pruebas iniciales: 25 paradas de interurbanos (3 con el 691), Metro Ligero (`10_`) y EMT (`6_`) | | solo 02/10 → 04/10 |

**Interurbanos, sin datos del 05/10 al 08/10.** No fue una caída: el grabador se dejó solo con Metro, que sí tiene datos esos días.

```json
{"t":1792447154,"s":"4_189","m":"metro","a":[["10",1,"4_205",1792447301,""], ...]}
```

- `a` = `[línea, sentido, parada_destino, llegada_epoch, codIssue]`.
- `codIssue` es el **código del viaje**, no una incidencia. Solo viene en interurbanos; en Metro, Ligero y EMT va vacío.
  - En el 691 es un número y el mismo viaje conserva el código de una parada a otra.
  - En el 212 es un texto que incluye la hora programada de salida.
- De la respuesta del widget no se guardan `destination` (texto), los detalles de `line` ni `codVehicle`. `codVehicle` venía vacío en las 178 llegadas consultadas el 02/11.
- Si la consulta falla, la fila es `{"t","s","m","err"}`.
- **Parada rotatoria (desde el 24/10):** además de las fijas, cada día se graba una parada elegida al azar que no se ha grabado ningún día anterior. El modo va alternando: Metro, Ligero, interurbanos y EMT.
  - Sus filas llevan `"r":1`.
  - `datos/crtm/rotacion.json` registra la parada de cada día, su modo, su nombre, y las consultas y llegadas que ha dado.
  - Si una parada no da ninguna llegada entre las 6:00 y las 10:00, se cambia por otra ese mismo día.
- Los nombres de las estaciones de Metro están en `grabadores/crtm/paradas_metro.json`.
- Los nombres de las paradas del 212 y el 691 están en `grabadores/crtm/docker-compose.yml`.

**Cómo reconstruimos la llegada real en Metro:** el tren desaparece de la lista. La llegada se toma como el punto medio entre la última consulta en que salía y la primera en que ya no.

### 4. Tráfico (`datos/trafico/`)

- **Cadencia:** cada 5 min.
- **Cobertura:** 14/10 → 03/11.
- **Fuentes:** tres, cada una en su tipo de fila:

| `k` | Origen | Contenido |
|---|---|---|
| `pm` | Ayuntamiento, `informo.madrid.es/.../pm.xml` | `c` = `["idelem","intensidad","ocupacion","carga","nivelServicio","error"]`, `r` = una fila por punto de medida (~4.100). Solo se guarda si el fichero ha cambiado |
| `incid` | Ayuntamiento, incidencias en la vía pública | lista de incidencias (tipo, descripción, inicio y fin, coordenadas). Solo se guarda si cambia |
| `dgt` | DGT, punto de acceso nacional DATEX II v3.7 | incidencias de carretera dentro de la Comunidad de Madrid. Solo se guarda si cambian |
| `err` | | error de una de las tres fuentes |

**Unidades de `pm`:**
- `intensidad`: vehículos por hora.
- `ocupacion`: % de tiempo que el detector está ocupado.
- `carga`: índice de 0 a 100.
- `nivelServicio`: de 0 (fluido) a 3 (congestión).
- `error`: `N` = lectura válida.

**Catálogo de puntos de medida:** `datos/trafico/puntos_medida.json.gz`, el más reciente. Es un diccionario `idelem → [descripción, utm_x, utm_y, subárea]`. Las coordenadas están en UTM 30N ETRS89, con coma decimal.

**Ojo:** las incidencias del Ayuntamiento no han cambiado desde el 14/10 (hay una sola fila `incid`). Puede que ese servicio no se actualice.

### 5. Avisos de la EMT y del Consorcio (`datos/avisos/`)

- **Origen:** RSS público de alteraciones del servicio, `http://feeds.emtmadrid.es:8082/`: desvíos, obras, manifestaciones, eventos.
- **Cadencia:** se consulta cada 5 min, y solo se descarga si ha cambiado.
- **Cobertura:** desde el 04/11. La primera copia trae los avisos que el RSS aún conservaba, publicados desde el 11/10. El RSS los retira al cabo de unas semanas, así que lo anterior se ha perdido.

| `k` | Contenido |
|---|---|
| `aviso` | `estado` (`nuevo` o `cambio`), `guid`, `titulo`, `texto`, `enlace` (PDF), `pub`, `fin_pub`, `desde`, `hasta`, `causa`, `efecto`, `lineas` |
| `baja` | `guid` de un aviso que ya no está en el RSS |
| `poll` | control de cada consulta: `n`, `novedades`, `sin_cambios` o `err` |
| `estado_red` | semáforo del Consorcio al cambiar: `redes`, por ejemplo `{"Metro": "Amarillo"}` |
| `aviso_crtm` | aviso del Consorcio: `red`, `estado`, `id`, `fecha`, `titulo`, `texto`, `nivel`, `enlace` |
| `baja_crtm` | aviso del Consorcio que ya no está publicado: `red`, `id` |
| `poll_crtm` | control de la consulta al Consorcio: `novedades` o `err` |

`pub`, `fin_pub`, `desde` y `hasta` son epoch UTC. `cargar.avisos()` y `cargar.avisos_crtm()` devuelven la última versión de cada aviso; `cargar.estado_red()`, los cambios del semáforo.

**Consorcio:** se consulta [su web](https://www.crtm.es/comunicacion/actualidad-del-servicio/avisos/) cada 15 min, para Metro, Metro Ligero, Cercanías, EMT e interurbanos. Empezamos a grabarla el 05/11. Ese día solo traía cortes y desvíos programados: falta ver si recoge incidencias del momento y qué significa cada color del semáforo.

**Ojo:**
- `lineas` viene como en el RSS, a veces con ceros delante (`002`). Hay que normalizarlas para cruzarlas con la EMT.
- `desde` y `hasta` son aproximados, y un aviso afecta a una parte de la línea, no necesariamente a todas sus paradas.
- `pub` puede ser posterior a `desde`: no todos los avisos llegan antes del problema. No sabemos si esa fecha cambia al editarlos.
- Las obras pueden durar meses: filtra por duración si buscas sucesos puntuales.

### 6. Otras fuentes

- **`catalogo_cm/`:** copia de cuatro datasets del portal de la Comunidad: intervalo medio en hora punta (1919185), velocidad comercial (1919184), billetes por modo (902003) y viajeros de Cercanías por estación (1923861). `fuentes.json` guarda la ficha, la licencia y la fecha de cada uno.
- **`meteo/`:** precipitación horaria de Open-Meteo para un punto de Madrid. Hay dos descargas:
  - del 23/09 al 13/10, con `precipitation` y `rain`;
  - desde el 14/09, solo `precipitation`.

  El formato es la respuesta tal cual de la API, con `hourly.time[]` y `hourly.precipitation[]`.
- **`redes/x_menciones_agregadas.json`:** muestras de menciones públicas a EMT, Metro (L6 y L12) y Renfe en X, en días concretos.
  - Solo contiene recuentos por hora y tema (`retraso_espera`, `averia_interrupcion`, `aglomeracion`, `calor_aire`, `otros`).
  - Son muestras pequeñas (15–40 mensajes cada una), útiles como indicio y no como estadística.
- **`externos/rodalies-observatorio_observaciones.csv.gz`:** histórico público de llegadas de Cercanías en toda España.
  - Publicado por el proyecto rodalies-observatorio, licencia CC BY 4.0, versión del 14/09/2026.
  - 863.000 filas: fecha, núcleo, línea, tren, estación, hora programada y real, `delay_s`.
  - Lo usamos antes de tener nuestro grabador y para Madrid fuera de nuestras fechas.
- **`horarios_oficiales/`:**
  - `renfe_gtfs_*.zip`: versiones del GTFS de Renfe; el calendario cambia entre ellas. La NAS añade la más reciente como mucho una vez por semana.
  - `crtm_gtfs_{metro,ligero,interurbanos,emt}.zip`: GTFS "oferta planificada" del portal de datos abiertos de la Comunidad.
    - El de Metro está fechado en 05/2025 y va por frecuencias.
    - El de la EMT también va solo por frecuencias, sin horas de paso.
  - `pdf_consorcio/`: los 1.180 horarios impresos de todas las líneas de EMT e interurbanos.
    - Se descargaron de `crtm.es/datos_lineas/horarios/{6|8}{línea}H{1|2}.pdf` (6 = EMT, 8 = interurbanos; H1/H2 = sentido).
    - El índice está en `pdf_consorcio_indice.json`. Todavía no los hemos analizado.

## Lo que hemos encontrado (resumen)

Los números exactos y el método están en `analisis/resultados/`.

**Cercanías** (`resultados_nas_*.txt`, script `analisis_nas.py`):
- **Predicciones de Renfe:** cuando faltan menos de 5 min, aciertan con ±2 min el 74–80% de las veces.
- Cuando faltan 10–20 min, aciertan igual que el horario (~36%), y suelen ser optimistas por 1–3 min.
- **Ejemplo real:** el C5 de las 8:17 que propone Google llegó tarde 8 de 9 laborables. El de las 7:47 llegó a su hora los 8 días con GPS.

**EMT** (`fiabilidad.csv`):
- **"Llega en 3–6 min":** se cumple a ±2 min el 82% de las veces.
- **"Llega en 15–25 min":** se cumple el 55%, y los autobuses llegan tarde algo más a menudo que antes de tiempo (27% frente a 19%).

**El 104** (`resultados_104_212.txt`, `resultados_sorpresas.txt`):
- **Autobuses fantasma:** el 40% de las veces aparecen autobuses que no estaban anunciados.
- **Autobús parado en la cabecera:** la app marca "1 min", pero sale con una mediana de 6 min más tarde. La estimación va por distancia, no por tiempo.
- **Frecuencia:** el intervalo real es de 13 min (mediana) frente a 10–12 programados, y el 12% de las esperas superan los 20 min.

**Interurbanos:**
- **En las cabeceras es horario:** en las del 212 y en Moncloa (691) la hora anunciada no cambia nunca.
- **Con el viaje en ruta se actualiza:** en las paradas intermedias de las dos líneas la hora cambia en el 0,2–1,1% de las consultas seguidas. Parece poco, pero a lo largo de un viaje se nota: con 15–25 min de antelación, entre un 36% y un 56% de los viajes del 691 y hasta un 49% de los del 212 se mueven más de 2 min (`fiabilidad_interurbanos_estabilidad.csv`).
- Antes decíamos que el 212 era solo horario. Era un error: esa cifra mezclaba cabeceras con paradas intermedias.

**Metro:**
- **L12:** huecos anómalos entre trenes el 24–28% del tiempo (27% el 19/10).
- **L6:** huecos anómalos el 17–22% del tiempo.
- **L3, L5 y L7:** regulares.

**Comparado con el portal de la Comunidad** (`cruce_catalogo.txt`, script `cruce_catalogo.py`):
- **EMT en hora punta:** el intervalo real (9,8–10,3 min) casi coincide con el programado (9,7–9,8 min), pero la espera media es de 7,2–7,7 min frente a los 4,9 que correspondería. Los buses cumplen la frecuencia de media, y su irregularidad añade 2,3–2,9 min de espera.
- **Rango:** depende de si una visita cuenta como paso con una última lectura de hasta 4 o de hasta 10 min. Son 26 paradas céntricas, en laborables del 05/10 al 04/11, y supone viajeros que llegan al azar.
- **Pasos esperados:** se ven el 84–89%. No podemos distinguir un bus retirado de un paso no detectado.
- **Impacto:** con la demanda oficial (454,6 M de viajes en 2023), unos 13–22 M de horas de espera de más al año si valiera para toda la red. Es una extrapolación, no una medición.
- **Intervalo oficial (8,6 min en punta, 2024):** es de toda la red y no es comparable con esta muestra de líneas.
- **Renfe por estación:** el acierto ponderado por viajeros es del 64,6% (67,8% sin ponderar), en 18 estaciones. Nuevos Ministerios (40%) y Chamartín (48%) salen bajas, pero falta descartar un efecto de medir en túnel: no uses esas dos cifras todavía.

**Lluvia** (`resultados_lluvia.txt`):
- Con lluvia en la punta de 16–19 h, los autobuses de la EMT van un 5–10% más lentos, y el 104 un 16% el día de lluvia.
- A mediodía no se nota.
- Solo hay 2 días de lluvia medidos.
- La hipótesis del equipo es que la causa real son los coches y no la lluvia. Para comprobarla está el grabador de tráfico.

**X** (`redes/`):
- **Quejas a la EMT:** el 20/10 tuvieron un pico a las 21 h.
- **Incidencia de la L6 en Legazpi:** el 20/10 de 08:24 a 08:53 la gente la comentaba en X, pero no apareció en la información del Consorcio.

**Otras observaciones:** el bus nocturno de la línea 4 sale de Ciudad Lineal en minutos fijos.

**Competencia** (detalle en `documentos/`):
- **Madrid Transporte** (4,5★): cuando no hay tiempo real, usa el horario.
- **Mobility 360:** 1,7★.

## Tabla de fiabilidad

Es la primera versión de "la probabilidad que aporta la API": dado lo que anuncia el operador, ¿con qué probabilidad llega a ±2 min?

- **Tabla:** `analisis/resultados/fiabilidad.csv`, a cuatro niveles de detalle (red, franja, tipo de parada, línea).
- **Consulta:** `analisis/fiabilidad.py`. `consultar("emt", 18, hora=8.5, linea="104")` busca del grupo más concreto al más general con al menos 30 llegadas.
- **Validación:** `analisis/resultados/fiabilidad_validacion.txt`, con días, paradas y líneas que no ha visto.
- **Generarla otra vez:** `python analisis/tabla_fiabilidad.py <carpeta temporal> --rehacer`, unos 20 min. Necesita pandas y pyarrow.

| El operador anuncia | EMT | Metro | Renfe |
|---|---|---|---|
| 3–6 min | 82% | 91% | 67% |
| 6–10 min | 72% | 84% | 48% |
| 10–15 min | 64% | 77% | 39% |
| 15–25 min | 55% | 57% | 42% |
| 25–40 min | 47% | sin dato | 45% |

Datos hasta el 03/11. Antes la tabla agrupaba por lo que tardó de verdad, no por lo anunciado, y daba cifras como un 91% en EMT a 3–6 min. Era un error: esa versión no contestaba a la pregunta de quien mira la app.

**Limitaciones:**
- **Cómo se mide la llegada:** Renfe usa GPS, la medida más independiente. EMT usa la posición del autobús a ≤600 m. Metro usa la desaparición del panel, que puede dar aciertos de más.
- **EMT:** el 35% de las visitas de un autobús a una parada no se cierran y no entran en la cuenta, porque pasó entre dos consultas (cada 3 min) o nunca llegó. Si parte son fantasmas, la fiabilidad real es menor.
- **Interurbanos:** no están en la tabla porque su panel no da una llegada real. `fiabilidad_interurbanos_estabilidad.csv` solo mide cuánto se mueve el anuncio.
- **Renfe:** solo entran los trenes con horario en algún GTFS del paquete (45.121 de 48.158).
- **Generalizar:** en días nuevos está bien calibrada. Por línea mejora un 3–6% frente a usar solo red y anuncio; por franja casi no aporta. En paradas que no ha visto se pasa de optimista en la parte alta (dice 93% y pasa 83% en EMT, dice 83% y pasa 67% en Renfe), y ahí el nivel de línea no ayuda en EMT ni en Renfe.

## Análisis (`analisis/`)

Los scripts se ejecutan desde la raíz `datos-transporte/`. Las rutas ya apuntan a `datos/...`. Solo usan la biblioteca estándar, salvo que se indique lo contrario.

| Script | Qué hace | Ejemplo |
|---|---|---|
| `analisis_nas.py` | Cercanías: llegada por GPS frente a horario y predicción | `python analisis/analisis_nas.py datos/renfe/2026-09-24.jsonl.gz <carpeta con renfe_gtfs_2026-09-24.zip descomprimido>` |
| `analisis_emt_metro.py` | Error de la estimación según lo que faltaba de verdad, EMT y Metro. Para "anuncia X", usa la tabla de fiabilidad | `python analisis/analisis_emt_metro.py datos/emt/2026-10-13.jsonl.gz datos/crtm/2026-10-13.jsonl.gz` |
| `analisis_emt_sorpresas.py` | autobuses que aparecen de la nada y estimaciones que saltan | `python analisis/analisis_emt_sorpresas.py datos/emt/2026-10-1*.jsonl.gz` |
| `analisis_104_212.py` | salidas reales del 104 en cabecera y estabilidad del 212 | `python analisis/analisis_104_212.py 2026-10-07 2026-10-08 2026-10-09 2026-10-13` |
| `analisis_lluvia.py` | velocidad de la EMT con y sin lluvia | `python analisis/analisis_lluvia.py` |
| `analisis_margen.py` | margen necesario en Cercanías con el histórico de rodalies | `python analisis/analisis_margen.py` |
| `simular_plan.py` | ¿habría llegado a tiempo? (Móstoles → Nuevos Ministerios antes de las 9:00) | `python analisis/simular_plan.py` |
| `cruce_catalogo.py` | lo medido frente a datos del portal de la Comunidad. Necesita pandas, pyarrow y la caché de `tabla_fiabilidad.py` | `python analisis/cruce_catalogo.py <carpeta de caché>` |
| `exportar_demo.py` | pasa la tabla de fiabilidad a `demo/fiabilidad.json` | `python analisis/exportar_demo.py` |
| `tabla_fiabilidad.py` | tabla de fiabilidad y su validación (ver arriba) | `python analisis/tabla_fiabilidad.py <carpeta temporal> --rehacer` |
| `descargar_pdf_consorcio.py` | descarga de los PDF de horarios. No hace falta volver a ejecutarlo | — |

`descargar_pdf_consorcio.py` espera los GTFS del Consorcio descomprimidos en `../gtfs_crtm/`.

## Grabadores (`grabadores/`)

Cada carpeta contiene `logger.py` y `docker-compose.yml`. El compose lleva el mismo script embebido, y es lo que se pega en la NAS como proyecto de Docker. Todos usan la imagen `python:3.12-alpine`, sin dependencias, con la zona horaria de Madrid (`TZ`).

| Grabador | Cada | Endpoint |
|---|---|---|
| renfe | 30 s | `gtfsrt.renfe.com/{vehicle_positions,trip_updates}.json` (+ GTFS cada 6 h) |
| emt | ~3 min por parada | `openapi.emtmadrid.es`. Necesita cuenta de MobilityLabs (variables `EMT_*`) |
| crtm | ~1 min por parada | `crtm.es/widgets/api/GetStopsTimes.php` (+ GTFS cada 24 h) |
| trafico | 5 min | `informo.madrid.es` (pm.xml, incidencias) + `nap.dgt.es` (DATEX II) |
| avisos | 5 y 15 min | `feeds.emtmadrid.es:8082` (RSS de la EMT) y `crtm.es/comunicacion/actualidad-del-servicio/avisos/` |

`grabadores/sync/` es el proyecto que sube los datos a este repo. Usa una clave SSH que se genera en la NAS y no sale de ella, con permiso de escritura solo en este repo. Ve las carpetas `data/` de los grabadores en modo lectura. No sube `puntos/` del tráfico.

**Pendiente:** el catálogo de puntos de medida se reescribe casi a diario porque cambia el campo `subarea` (~20 MB por semana). Hay que guardar solo cuando cambien la descripción o las coordenadas.

## Documentos (`documentos/`)

- `propuesta_idea.pdf`, `llego_a_tiempo_propuesta.pdf`: propuesta de la idea para el equipo.
- `sprint1_datamad.docx`, `sprint1_datamad_presentacion.pdf`: el sprint 1 entregado.
- `llego.html`: prototipo navegable con los casos reales (C5, 104, 212...). Se abre en el navegador.
- `app_o_servicio.html`: comparativa entre app y servicio. Hay una versión más completa en Claude Docs: https://claude.ai/artifact/Fg4s4stZC93Uky4LJc74RC.

## Licencias y uso

Revisado el 05/11/2026. En la formación de DATAMAD se dijo que un dataset sin licencia no puntúa en esa parte; falta confirmarlo por escrito. Lo que no puntúe se puede seguir usando en la app si sus condiciones lo permiten.

| Fuente | Licencia publicada | Qué exige |
|---|---|---|
| Portal de la Comunidad (`datos/catalogo_cm/`) | CC BY | Citar la fuente |
| GTFS del Consorcio en el portal | Licencia de datos abiertos del Consorcio | Citar, mostrar "Powered by CRTM" con enlace y no dañar la imagen del Consorcio ni del transporte público |
| Renfe (GTFS y GTFS-RT) | CC BY 4.0 | Citar la fuente |
| EMT: llegadas y avisos | ODbL, más las condiciones de MobilityLabs | Citar, compartir igual lo derivado de sus datos, mostrar "Powered by EMT de Madrid" y no dañar su imagen |
| Rodalies-observatorio | CC BY 4.0 | Citar la fuente |
| Open-Meteo | CC BY 4.0 | Citar; la API gratuita es solo para uso no comercial |
| Tráfico del Ayuntamiento | Licencia de su portal | Texto sin revisar |
| DGT (NAP) | Depende de cada dataset | Sin revisar |
| Widget y avisos del Consorcio (Metro e interurbanos medidos) | [Aviso legal del Consorcio](https://www.crtm.es/aviso-legal): permite reutilizar los contenidos y datos de su web. No es una licencia tipo CC; falta confirmar si puntúa | No alterar la información ni su sentido, citar la fuente, indicar la fecha de extracción y no sugerir que el Consorcio patrocina el proyecto |
| Web, notas de prensa y app de Metro de Madrid | Ninguna: su [aviso legal](https://www.metromadrid.es/es/aviso-legal) exige autorización escrita | No usar sin permiso |
| Noticias de apps de terceros | Ninguna: servidores privados | No usar |
| Agregados de X (`datos/redes/`) | Ninguna | No usar en la entrega |

**Para la entrega:** los resultados que dependen del criterio de datos abiertos salen de la EMT, Renfe y el portal de la Comunidad. El Metro y los avisos del Consorcio forman parte del producto: se dice de dónde salen, con cita y fecha de extracción, y no se presentan como dataset del portal.

Para la entrega de DATAMAD hay que declarar como trabajo previo lo que ya teníamos, y las bases lo permiten.
