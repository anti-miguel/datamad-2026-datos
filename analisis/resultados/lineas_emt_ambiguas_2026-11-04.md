# Identidad de líneas EMT en el cruce, corte 2026-11-04

Confirmado en código y GTFS local: la función linea() del cruce quita ceros iniciales. routes.txt contiene rutas diferentes con nombres cortos 1 (route_id 001) y 001 (route_id 361), y 2 (route_id 002) y 002 (route_id 362). La normalización histórica las fusiona.
Comprobado ejecutando: 132 nombres distintos de línea en los anuncios brutos del periodo; 1 claves normalizadas con más de un nombre presente: {'1': ['001', '1']}.

| Línea original | Clave del cruce | Anuncios brutos | Seguibles en laborable | Seguibles en punta |
|---|---|---:|---:|---:|
| 001 | 1 | 161771 | 109597 | 35461 |
| 1 | 1 | 113636 | 76438 | 24413 |

En la tabla actualizada de punta, 1 de 63 filas conservan esas claves ambiguas y suman 7842 de 140171 intervalos publicados. No se pueden atribuir sus métricas a una sola de las líneas originales.
Seguible significa bus identificado, estimación numérica y distinta de 888888/999999 en un laborable según el cruce. Cuenta anuncios, no viajes ni intervalos finales. Una clave fusionada también puede contaminar el horario de referencia y la exclusión de cabeceras; estos recuentos no miden ese sesgo.
Las claves 1 y 2 también reúnen rutas distintas en el horario GTFS, aunque no se observan ambos nombres originales de 2 en la muestra. Sus 2 filas suman 11519 intervalos de punta potencialmente afectados por la normalización de referencia; no se ha determinado cuántos usan el destino exacto o el horario alternativo por línea. Excluyendo ambas filas como sensibilidad prudente quedan 61 líneas y EWT mediana 2.47 min, frente a 2.47 en las 63 originales. No es un recálculo con identidades corregidas.
El refresco principal conserva el método para compararlo con el histórico. Deben reservarse las filas ambiguas y revisar sus efectos en agregados antes de usarlos como prueba de rendimiento. No se atribuye todo cambio de tabla a nuevos días.
