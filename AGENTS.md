# Guía para agentes de IA

Este paquete reúne los datos y el código de un proyecto de DATAMAD 2026 (datatón de datos abiertos de la Comunidad de Madrid). Mide cuánto cumple el transporte público de Madrid lo que anuncia. El planteamiento actual es una app.

## Por dónde empezar

1. `catalogo.json`: lista de conjuntos de datos con ruta, periodo, cadencia, esquema y advertencias. Léelo primero.
2. `README.md`: explicación para personas, con los hallazgos y el método de cada análisis.
3. `cargar.py`: usa sus funciones en vez de reimplementar el parseo.
   - `cargar.dias(fuente)`
   - `cargar.filas(fuente, dia)`
   - `cargar.emt`, `cargar.crtm`, `cargar.renfe_posiciones`, `cargar.renfe_retrasos`, `cargar.trafico`: estas devuelven DataFrames de pandas.
   - `cargar.puntos_medida()`

Trabaja con la raíz `datos-transporte/` como directorio actual. Los scripts de `analisis/` cuentan con ello.

## Cosas que conviene saber antes de analizar

- **Tiempo:** `t` es epoch UTC. Los ficheros diarios usan el día de Madrid. Convierte con `Europe/Madrid`; `cargar.py` ya añade la columna `hora`.
- **Tamaño:** los ficheros son JSONL comprimidos con gzip. Un día de Renfe tiene ~400.000 filas y un día de tráfico ~1,3 M filas una vez expandido. No cargues todos los días a la vez si no hace falta: itera por día.
- **Errores y control:** en todas las fuentes hay filas de error (`"err"`) y de control (`k: "poll"`, `"login"`, `"flota"`). Fíltralas.
- **Huecos conocidos:** están en `catalogo.json → huecos`. Distingue entre:
  - caída del dato del operador (lo que el proyecto quiere detectar);
  - caída de nuestro grabador (no es un hallazgo).
- **Renfe:** hay retrasos de alrededor de ±86.400 s que corresponden a viajes de otro día. Descártalos.
- **EMT:** `llega_en_s` = 999999 (diurnas, más de 45 min) y 888888 (nocturnas, `>90` en la app de la EMT) son códigos, no segundos. Fíltralos: `cargar.emt` los deja tal cual.
- **Paradas del Consorcio:** cada consulta del widget devuelve las próximas llegadas de una parada. Un tren o bus se sigue entre consultas por (parada, línea, sentido, destino) y la hora de llegada anunciada.
- **Horarios oficiales:** están en zips GTFS sin descomprimir (`datos/horarios_oficiales/`). Descomprímelos fuera del paquete (por ejemplo en una carpeta temporal) si los necesitas.
- **Conclusiones:** algunas muestras son pequeñas (2 días de lluvia, 15–40 mensajes de X por búsqueda). Indícalo al sacar conclusiones.

## Reglas

- No hay credenciales en el paquete, y no hay que añadirlas.
  - El `docker-compose.yml` de la EMT lleva marcadores `ESCRIBE_AQUI_...`; quien lo despliegue pone sus propias claves en la NAS.
  - No pidas ni escribas claves en ficheros del repositorio.
- `datos/redes/` solo contiene agregados. No intentes reconstruir mensajes ni usuarios.
- No modifiques `datos/`: es la copia de referencia. Escribe los resultados nuevos en `analisis/resultados/` o en una carpeta tuya.
- La NAS añade los días cerrados cada noche: haz `git pull` antes de analizar. `catalogo.json` y la tabla de fiabilidad se calcularon con datos hasta el 03/11/2026 y no se actualizan solos.
- El proyecto aún no tiene nombre. No le pongas uno en los materiales que generes.
