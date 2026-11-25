# Uso de datos del portal de la Comunidad de Madrid

Inventario revisado el 05/11/2026. Corte de grabaciones: 04/11/2026, día cerrado de Madrid. Esta revisión usa únicamente ficheros locales y código; no consulta la API ni verifica cambios posteriores en las fichas.

**Confirmado en código y metadatos locales:** los cuatro CSV siguientes proceden del portal, según `datos/catalogo_cm/fuentes.json`, que registra ficha, recurso, modificación y descarga del 05/11/2026. La licencia conservada es `Creative Commons Attribution` (CC BY); el fichero no identifica versión. Se debe citar al portal y la ficha concreta, sin añadir una versión de licencia por suposición.

| ID y ficha | Dataset | Uso analítico que ejecuta el código | Periodo oficial de referencia |
|---|---|---|---|
| [1919185](https://datos.comunidad.madrid/dataset/1919185) | Intervalo medio en hora punta del transporte metropolitano | `cruce_catalogo.py`: compara el intervalo oficial EMT con la frecuencia GTFS y los intervalos observados; contextualiza el cálculo de espera adicional. | Último dato válido EMT: 2024. |
| [1919184](https://datos.comunidad.madrid/dataset/1919184) | Velocidad comercial de los medios de transporte metropolitanos | `cruce_catalogo.py`: referencia de velocidad anual EMT frente a velocidad inferida de distancias a paradas céntricas, de 7 a 21 h laborables. No son directamente comparables. | Último dato válido EMT: 2024. |
| [902003](https://datos.comunidad.madrid/dataset/902003) | Billetes por modo de transporte | `cruce_catalogo.py`: convierte escenarios de espera adicional EMT en un orden de magnitud de horas anuales. `contexto_portal.py`: serie por modo, cambio de demanda desde 2019 y sensibilidad de ese escenario al año de demanda. | Último dato válido EMT: 2023; no se interpreta como demanda de 2026. |
| [1923861](https://datos.comunidad.madrid/dataset/1923861) | Viajeros subidos y bajados en trenes de cercanías por estaciones | `cruce_catalogo.py`: pondera aciertos de anuncios Renfe por volumen oficial de estación, correlaciona demanda y acierto y ordena escenarios de exposición. `contexto_portal.py`: cobertura de viajeros publicada y sensibilidad al año de ponderación. | Último año: 2024; 27 estaciones en el CSV y 21 con dato válido ese año. Son subidas y bajadas, no personas únicas. |

**Confirmado en código:** el GTFS `datos/horarios_oficiales/crtm_gtfs_emt.zip` también interviene en `tabla_fiabilidad.py` (identifica cabeceras), `cruce_catalogo.py` (intervalos por línea, destino, servicio y ventana horaria) y `avisos_emt.py` (identidad de líneas). El README atribuye los GTFS CRTM al portal y recoge la licencia propia de datos abiertos del Consorcio: atribuir, mostrar «Powered by CRTM» con enlace y respetar sus condiciones. **No consta su ID de dataset en los metadatos locales**, y el ZIP EMT no contiene `feed_info.txt`; `agency.txt` identifica al CRTM. No se le atribuye CC BY. El ID y la ficha deben completarse con una consulta autorizada del portal antes de una entrega que exija esa identificación.

Los GTFS locales de Metro, Ligero e interurbanos contienen `feed_info.txt` del CRTM, pero el inventario de scripts ejecutados en este refresco no los usa para contrastar oferta planificada. No se cuentan como uso analítico adicional por el mero hecho de estar descargados. El auxiliar `descargar_pdf_consorcio.py` lee rutas EMT e interurbanas de una extracción externa para localizar PDF; no acredita aquí resultados de un cruce con demanda o frecuencia.

**Confirmado en código y comprobado ejecutando:** el cruce conserva una normalización histórica que quita ceros iniciales y fusiona 001/1 y 002/2. Se observan ambas identidades 001/1 en la muestra: su clave 1 reúne 7.842 de 140.171 intervalos de punta publicados. Las frecuencias GTFS de 1 y 2 también pueden mezclarse. Estas filas no deben atribuirse a una sola línea. El detalle de muestras y sensibilidad al excluir ambas está en [lineas_emt_ambiguas_2026-11-04.md](lineas_emt_ambiguas_2026-11-04.md); el refresco comparable mantiene el método para mostrar sus movimientos, sin dar por corregido este defecto.

**Confirmado en código:** las llegadas del widget CRTM, la API EMT, los feeds Renfe, Open-Meteo, tráfico municipal y DGT no se convierten en datasets del portal de la Comunidad por cruzarlos con él. Los datos del widget deben citar al Consorcio y la fecha de extracción conforme a su aviso legal. Las condiciones de uso de cada fuente se mantienen; el uso de CC BY en un CSV no permite atribuir esa licencia a todo el producto.

## Ampliaciones posibles con el límite de trabajo local

**Confirmado en metadatos locales:** `catalogo.json` y `datos/catalogo_cm/fuentes.json` solo identifican los cuatro datasets CC BY anteriores, ya utilizados. Los otros conjuntos del catálogo son de otros proveedores o tienen condiciones diferentes. No hay un quinto dataset local con ID del portal y licencia CC BY acreditados. Se proponen **cero datasets adicionales verificados**, dentro del máximo de cinco: no sería reproducible inventar IDs, títulos o licencias y no se permite red en este encargo. Queda pendiente explorar la API del portal cuando se autorice acceso a red y conservar su metadata antes de incorporarlos.

**Propuesta pendiente de verificación, inferencia:** la memoria local del proyecto conserva como candidato el ID **1919180**, «redes de autobuses», pero su ficha y licencia no están copiadas en este paquete. Si se confirma CC BY y se dispone de su serie de extensión de red por año, un análisis concreto sería cruzar esa extensión con billetes por modo (902003) e intervalo punta (1919185), para distinguir crecimiento de red y cambios de demanda/oferta al contextualizar la muestra de paradas céntricas. No se presenta como incorporación CC BY acreditada ni se presupone su esquema; no se ha descargado ni implementado con datos inventados.

Se ha implementado la ampliación útil que permiten las copias existentes, sin presentarla como incorporación de un dataset:

- `contexto_portal.py` genera una tabla de demanda por modo respecto de 2019 (902003), para que el escenario de impacto no oculte la antigüedad de su demanda.
- Calcula cuánto cambia el acierto Renfe ponderado al usar distintos años de viajeros por estación (1923861), manteniendo fijas las tasas observadas en 2026 y registrando cobertura y estaciones emparejadas en cada año. Es sensibilidad de pesos, no evolución de la puntualidad.
- Informa qué fracción de los viajeros subidos y bajados publicados queda cubierta por las estaciones con al menos 500 llegadas observadas. Ese denominador abarca solo las estaciones publicadas, no toda la red.

**Comprobado ejecutando:** las cifras, tamaños de muestra y limitaciones de esta ampliación están en [contexto_portal_2026-11-04.md](contexto_portal_2026-11-04.md), `contexto_portal_demanda_2026-11-04.csv` y `contexto_portal_pesos_renfe_2026-11-04.csv`. Las tasas de estación empleadas se publican redondeadas a tres decimales, que limitan la precisión de la comparación a unos 0,05 puntos porcentuales. El análisis de túneles debe acompañar cualquier priorización por estación.

## Reproducción y límites

Desde la raíz, con Python 3.13, pandas 2.2.3 y pyarrow 23.0.1:

```powershell
python analisis/tabla_fiabilidad.py D:\Temp\datamad_codex_2026-11-05 --corte 2026-11-04 --reemplazar
python analisis/cruce_catalogo.py D:\Temp\datamad_codex_2026-11-05 --corte 2026-11-04 --reemplazar
python analisis/contexto_portal.py --corte 2026-11-04
python analisis/comparar_refresh.py --corte 2026-11-04 --cache D:\Temp\datamad_codex_2026-11-05
python analisis/sensibilidad_festivo.py D:\Temp\datamad_codex_2026-11-05 --corte 2026-11-04
python analisis/auditar_lineas_emt.py --corte 2026-11-04
python analisis/verificar_refresh.py
```

Sin `--reemplazar`, los dos primeros comandos protegen las salidas fechadas ya existentes. El indicador permite regenerar solo las salidas del corte elegido; no afecta a las históricas sin fecha. La caché es temporal y externa al repositorio, con huellas de tamaño y fecha de modificación de las entradas para evitar reutilizar un corte diferente.

**Comprobado ejecutando:** `verificar_refresh.py` lee el catálogo con red y escrituras en `datos/` bloqueadas, comprueba el fallo ante copias ausentes, contrasta las copias locales byte a byte y verifica que las seis salidas históricas conservan su contenido de Git. No se verifican por red las licencias actuales ni se valida representatividad de todas las estaciones y paradas de Madrid.

