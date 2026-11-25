# Salud de los datos

Comprobado ejecutando: corte 2026-11-04, 132 días-fuente, 20,596,566 filas crudas. Fechas y horas en Europe/Madrid.

Comprobado ejecutando: 0 ficheros con error de lectura; 5 huecos de actividad de al menos 20 min. El detalle permite distinguir el arranque de cada fuente de los fallos posteriores. Una respuesta vacía o un feed congelado pueden coexistir con actividad del grabador completa.

La cobertura mide presencia de filas del grabador en la red monitorizada. Cada marca cubre una cadencia hacia delante, recortada al día civil; el 25/10 dura 25 horas. No mide servicio ni todas las paradas. Contenido exige posiciones/retrasos, llegadas no vacías o puntos de tráfico; en avisos un poll correcto con cero novedades es contenido válido. Las filas de flota EMT 404 se cuentan en errores totales, pero no en errores relevantes de llegadas. Las respuestas vacías no son errores de parseo.

Confirmado en código: las atribuciones operador proceden de catalogo.json y solo cubren su solape. Inferencia: la falta de filas no demuestra una caída de la NAS. No se fuerza una etiqueta operador/grabador sin evidencia. Las noches sin trenes y los inicios de despliegue pueden generar huecos sin avería.

## Llegada de avisos

Comprobado ejecutando: 2026-11-04, 234 filas, parseo completo, tipos {'aviso': 198, 'poll': 36}; canales {'emt': {'marcas': 36, 'cobertura_actividad_pct': 12.162}, 'crtm': {'marcas': 0, 'cobertura_actividad_pct': 0.0}}.

Confirmado en código: avisos_crtm es un tipo dentro de datos/avisos, no una carpeta. Su recogida empieza el 2026-11-05 según el catálogo. No hay día cerrado esperado hasta el corte 2026-11-04. Ausencia local no demuestra fallo de la NAS; no se ha accedido a ella.

## Días que requieren revisión

- renfe 2026-09-23: cobertura de actividad inferior al 90%; puede ser inicio de despliegue; hueco de actividad de al menos 20 min.
- renfe 2026-09-26: anomalía declarada en catalogo.json.
- renfe 2026-09-28: anomalía declarada en catalogo.json.
- renfe 2026-09-30: anomalía declarada en catalogo.json.
- renfe 2026-10-03: anomalía declarada en catalogo.json.
- renfe 2026-10-20: anomalía declarada en catalogo.json.
- renfe 2026-10-29: anomalía declarada en catalogo.json.
- emt 2026-10-04: cobertura de actividad inferior al 90%; puede ser inicio de despliegue; hueco de actividad de al menos 20 min.
- emt 2026-10-19: más del 5% de filas con error relevante.
- emt 2026-10-20: más del 5% de filas con error relevante; anomalía declarada en catalogo.json.
- emt 2026-10-21: anomalía declarada en catalogo.json.
- crtm 2026-10-02: cobertura de actividad inferior al 90%; puede ser inicio de despliegue; hueco de actividad de al menos 20 min.
- crtm 2026-10-20: anomalía declarada en catalogo.json.
- crtm 2026-11-01: más del 5% de filas con error relevante.
- trafico 2026-10-14: cobertura de actividad inferior al 90%; puede ser inicio de despliegue; hueco de actividad de al menos 20 min.
- avisos 2026-11-04: cobertura de actividad inferior al 90%; puede ser inicio de despliegue; hueco de actividad de al menos 20 min.

## Detalle diario

Comprobado ejecutando. El JSON incluye todos los huecos de actividad de 20 min, las clases, los solapes y los tipos de fila. El mayor hueco incluye los bordes del día.

| Fuente | Día | Filas | Errores total/relevantes | Actividad % | Contenido % | Mayor hueco actividad min / clase |
|---|---|---:|---:|---:|---:|---|
| renfe | 2026-09-23 | 22250 | 0/0 | 6.65 | 6.62 | 1340.7 / indeterminado |
| renfe | 2026-09-24 | 461934 | 0/0 | 99.87 | 84.49 | 0.1 / indeterminado |
| renfe | 2026-09-25 | 463066 | 0/0 | 99.91 | 84.63 | 0.0 / indeterminado |
| renfe | 2026-09-26 | 173539 | 0/0 | 99.95 | 42.14 | 0.3 / operador |
| renfe | 2026-09-27 | 367732 | 0/0 | 99.92 | 87.23 | 0.2 / indeterminado |
| renfe | 2026-09-28 | 308962 | 0/0 | 99.96 | 62.84 | 0.4 / indeterminado |
| renfe | 2026-09-29 | 457404 | 0/0 | 99.52 | 85.39 | 5.1 / indeterminado |
| renfe | 2026-09-30 | 304226 | 0/0 | 99.89 | 60.34 | 0.6 / indeterminado |
| renfe | 2026-10-01 | 455566 | 0/0 | 99.69 | 84.03 | 0.4 / indeterminado |
| renfe | 2026-10-02 | 462955 | 1/1 | 99.84 | 87.10 | 0.5 / indeterminado |
| renfe | 2026-10-03 | 191325 | 2/2 | 99.90 | 49.45 | 0.6 / operador |
| renfe | 2026-10-04 | 367906 | 2/2 | 99.86 | 86.80 | 0.5 / indeterminado |
| renfe | 2026-10-05 | 433592 | 5/5 | 99.94 | 72.65 | 0.2 / indeterminado |
| renfe | 2026-10-06 | 463551 | 1/1 | 99.82 | 89.30 | 0.3 / indeterminado |
| renfe | 2026-10-07 | 458458 | 2/2 | 99.90 | 89.07 | 0.1 / indeterminado |
| renfe | 2026-10-08 | 464915 | 7/7 | 99.88 | 84.81 | 0.4 / indeterminado |
| renfe | 2026-10-09 | 453260 | 3/3 | 99.75 | 87.39 | 0.3 / indeterminado |
| renfe | 2026-10-10 | 376093 | 3/3 | 99.88 | 83.84 | 0.1 / indeterminado |
| renfe | 2026-10-11 | 357392 | 3/3 | 99.67 | 81.30 | 0.2 / indeterminado |
| renfe | 2026-10-12 | 384298 | 1/1 | 99.83 | 82.46 | 0.2 / indeterminado |
| renfe | 2026-10-13 | 475465 | 1/1 | 99.94 | 83.30 | 0.0 / indeterminado |
| renfe | 2026-10-14 | 474376 | 2/2 | 99.89 | 89.20 | 0.4 / indeterminado |
| renfe | 2026-10-15 | 472479 | 1/1 | 99.92 | 89.47 | 0.1 / indeterminado |
| renfe | 2026-10-16 | 461715 | 2/2 | 99.81 | 84.63 | 0.3 / indeterminado |
| renfe | 2026-10-17 | 369852 | 2/2 | 99.79 | 83.96 | 0.5 / indeterminado |
| renfe | 2026-10-18 | 383689 | 1/1 | 99.92 | 88.42 | 0.3 / indeterminado |
| renfe | 2026-10-19 | 468929 | 6/6 | 99.86 | 83.30 | 0.2 / indeterminado |
| renfe | 2026-10-20 | 453224 | 3/3 | 99.86 | 86.14 | 0.4 / indeterminado |
| renfe | 2026-10-21 | 468195 | 3/3 | 99.89 | 87.92 | 0.1 / indeterminado |
| renfe | 2026-10-22 | 458201 | 2/2 | 99.84 | 87.79 | 0.5 / indeterminado |
| renfe | 2026-10-23 | 449169 | 3/3 | 99.88 | 86.82 | 0.3 / indeterminado |
| renfe | 2026-10-24 | 372630 | 0/0 | 99.90 | 86.15 | 0.2 / indeterminado |
| renfe | 2026-10-25 | 355346 | 2/2 | 99.88 | 83.55 | 0.4 / indeterminado |
| renfe | 2026-10-26 | 449475 | 1/1 | 99.87 | 82.06 | 0.3 / indeterminado |
| renfe | 2026-10-27 | 457259 | 1/1 | 99.93 | 88.06 | 0.3 / indeterminado |
| renfe | 2026-10-28 | 474015 | 0/0 | 99.89 | 87.08 | 0.5 / indeterminado |
| renfe | 2026-10-29 | 139368 | 8/8 | 98.98 | 47.87 | 0.1 / operador |
| renfe | 2026-10-30 | 395300 | 11/11 | 99.65 | 76.87 | 0.5 / indeterminado |
| renfe | 2026-10-31 | 329346 | 0/0 | 99.92 | 89.26 | 0.5 / indeterminado |
| renfe | 2026-11-01 | 319383 | 2/2 | 99.97 | 86.29 | 0.2 / indeterminado |
| renfe | 2026-11-02 | 317038 | 4/4 | 99.92 | 85.33 | 0.4 / indeterminado |
| renfe | 2026-11-03 | 408436 | 6/6 | 99.55 | 83.33 | 5.8 / indeterminado |
| renfe | 2026-11-04 | 420653 | 1/1 | 99.91 | 84.91 | 0.5 / indeterminado |
| emt | 2026-10-04 | 674 | 73/1 | 5.04 | 5.04 | 1367.5 / indeterminado |
| emt | 2026-10-05 | 13441 | 1497/57 | 100.00 | 100.00 | 0 |
| emt | 2026-10-06 | 13867 | 1853/414 | 100.00 | 100.00 | 0 |
| emt | 2026-10-07 | 15356 | 2027/587 | 99.96 | 99.81 | 0.5 / indeterminado |
| emt | 2026-10-08 | 15356 | 2009/570 | 99.94 | 99.79 | 0.8 / indeterminado |
| emt | 2026-10-09 | 15354 | 2010/570 | 99.98 | 99.76 | 0.3 / indeterminado |
| emt | 2026-10-10 | 15361 | 1998/558 | 99.96 | 99.74 | 0.6 / indeterminado |
| emt | 2026-10-11 | 15327 | 1993/555 | 99.93 | 99.86 | 0.9 / indeterminado |
| emt | 2026-10-12 | 15356 | 2028/588 | 100.00 | 100.00 | 0 |
| emt | 2026-10-13 | 15355 | 2139/699 | 100.00 | 100.00 | 0 |
| emt | 2026-10-14 | 14971 | 1817/380 | 99.97 | 99.69 | 0.3 / indeterminado |
| emt | 2026-10-15 | 15073 | 1984/547 | 99.99 | 99.99 | 0.1 / indeterminado |
| emt | 2026-10-16 | 15223 | 2111/671 | 100.00 | 100.00 | 0 |
| emt | 2026-10-17 | 14998 | 1886/447 | 99.97 | 99.82 | 0.4 / indeterminado |
| emt | 2026-10-18 | 14881 | 1720/280 | 99.98 | 99.77 | 0.2 / indeterminado |
| emt | 2026-10-19 | 15272 | 2700/1262 | 99.94 | 99.15 | 0.9 / indeterminado |
| emt | 2026-10-20 | 14557 | 2490/1101 | 99.61 | 74.22 | 0.9 / indeterminado |
| emt | 2026-10-21 | 14850 | 1457/20 | 100.00 | 69.84 | 0 |
| emt | 2026-10-22 | 14881 | 1446/6 | 100.00 | 100.00 | 0 |
| emt | 2026-10-23 | 14881 | 1443/3 | 99.96 | 99.81 | 0.6 / indeterminado |
| emt | 2026-10-24 | 15243 | 1802/362 | 99.96 | 99.81 | 0.6 / indeterminado |
| emt | 2026-10-25 | 16000 | 2000/500 | 99.96 | 99.96 | 0.6 / indeterminado |
| emt | 2026-10-26 | 15362 | 1944/504 | 99.96 | 99.81 | 0.6 / indeterminado |
| emt | 2026-10-27 | 15361 | 1922/482 | 99.96 | 99.81 | 0.6 / indeterminado |
| emt | 2026-10-28 | 15362 | 1926/486 | 99.96 | 99.81 | 0.6 / indeterminado |
| emt | 2026-10-29 | 15363 | 1926/486 | 99.96 | 99.81 | 0.6 / indeterminado |
| emt | 2026-10-30 | 15366 | 1928/488 | 99.95 | 99.80 | 0.7 / indeterminado |
| emt | 2026-10-31 | 15360 | 1920/480 | 99.95 | 99.80 | 0.7 / indeterminado |
| emt | 2026-11-01 | 15359 | 1924/484 | 99.95 | 99.80 | 0.7 / indeterminado |
| emt | 2026-11-02 | 15365 | 1945/505 | 99.95 | 99.95 | 0.7 / indeterminado |
| emt | 2026-11-03 | 15304 | 1920/486 | 99.73 | 99.51 | 3.2 / indeterminado |
| emt | 2026-11-04 | 15366 | 1936/496 | 100.00 | 100.00 | 0 |
| crtm | 2026-10-02 | 40416 | 291/291 | 33.53 | 33.53 | 955.8 / indeterminado |
| crtm | 2026-10-03 | 131424 | 511/511 | 99.36 | 99.36 | 3.4 / indeterminado |
| crtm | 2026-10-04 | 130982 | 466/466 | 100.00 | 99.97 | 0 |
| crtm | 2026-10-05 | 87172 | 552/552 | 99.98 | 95.61 | 0.3 / indeterminado |
| crtm | 2026-10-06 | 87544 | 582/582 | 99.84 | 98.07 | 1.3 / indeterminado |
| crtm | 2026-10-07 | 86676 | 799/799 | 99.59 | 96.36 | 2.5 / indeterminado |
| crtm | 2026-10-08 | 87358 | 524/524 | 99.92 | 92.98 | 1.2 / indeterminado |
| crtm | 2026-10-09 | 89426 | 448/448 | 99.92 | 95.88 | 0.6 / indeterminado |
| crtm | 2026-10-10 | 95676 | 318/318 | 100.00 | 99.92 | 0 |
| crtm | 2026-10-11 | 94928 | 644/644 | 99.58 | 99.10 | 2.4 / indeterminado |
| crtm | 2026-10-12 | 94996 | 811/811 | 99.45 | 98.77 | 2.3 / indeterminado |
| crtm | 2026-10-13 | 85544 | 2029/2029 | 93.09 | 92.19 | 3.8 / indeterminado |
| crtm | 2026-10-14 | 92708 | 1302/1302 | 97.53 | 96.97 | 3.5 / indeterminado |
| crtm | 2026-10-15 | 101602 | 579/579 | 100.00 | 99.95 | 0 |
| crtm | 2026-10-16 | 97976 | 1037/1037 | 96.86 | 96.72 | 4.0 / indeterminado |
| crtm | 2026-10-17 | 102712 | 828/828 | 99.45 | 98.74 | 2.4 / indeterminado |
| crtm | 2026-10-18 | 100492 | 712/712 | 98.00 | 97.88 | 3.3 / indeterminado |
| crtm | 2026-10-19 | 100048 | 915/915 | 99.83 | 99.40 | 1.5 / indeterminado |
| crtm | 2026-10-20 | 95830 | 1981/1981 | 95.90 | 94.10 | 3.9 / indeterminado |
| crtm | 2026-10-21 | 100418 | 842/842 | 99.84 | 99.81 | 1.8 / indeterminado |
| crtm | 2026-10-22 | 101972 | 707/707 | 99.99 | 99.91 | 0.1 / indeterminado |
| crtm | 2026-10-23 | 100936 | 550/550 | 99.97 | 99.86 | 0.5 / indeterminado |
| crtm | 2026-10-24 | 102605 | 669/669 | 99.63 | 99.48 | 4.2 / indeterminado |
| crtm | 2026-10-25 | 106950 | 1436/1436 | 99.04 | 98.14 | 3.5 / indeterminado |
| crtm | 2026-10-26 | 100950 | 3277/3277 | 99.95 | 97.74 | 0.7 / indeterminado |
| crtm | 2026-10-27 | 88650 | 4347/4347 | 90.46 | 84.39 | 4.4 / indeterminado |
| crtm | 2026-10-28 | 99600 | 2400/2400 | 98.18 | 97.09 | 4.3 / indeterminado |
| crtm | 2026-10-29 | 100500 | 1282/1282 | 99.68 | 99.36 | 1.6 / indeterminado |
| crtm | 2026-10-30 | 99450 | 3253/3253 | 99.53 | 97.50 | 2.4 / indeterminado |
| crtm | 2026-10-31 | 102375 | 1991/1991 | 99.66 | 98.47 | 3.0 / indeterminado |
| crtm | 2026-11-01 | 102750 | 6543/6543 | 99.71 | 94.14 | 1.3 / indeterminado |
| crtm | 2026-11-02 | 102675 | 1215/1215 | 99.74 | 99.34 | 1.7 / indeterminado |
| crtm | 2026-11-03 | 99825 | 1819/1819 | 98.85 | 97.59 | 5.4 / indeterminado |
| crtm | 2026-11-04 | 100200 | 1642/1642 | 98.67 | 97.80 | 4.4 / indeterminado |
| trafico | 2026-10-14 | 31 | 0/0 | 5.52 | 5.17 | 1360.5 / indeterminado |
| trafico | 2026-10-15 | 550 | 1/1 | 99.62 | 91.98 | 5.0 / indeterminado |
| trafico | 2026-10-16 | 540 | 0/0 | 99.97 | 87.47 | 0.5 / indeterminado |
| trafico | 2026-10-17 | 537 | 0/0 | 99.62 | 87.81 | 5.0 / indeterminado |
| trafico | 2026-10-18 | 531 | 0/0 | 99.27 | 88.51 | 5.0 / indeterminado |
| trafico | 2026-10-19 | 535 | 0/0 | 99.97 | 86.42 | 0.5 / indeterminado |
| trafico | 2026-10-20 | 540 | 0/0 | 99.97 | 87.81 | 0.5 / indeterminado |
| trafico | 2026-10-21 | 532 | 0/0 | 99.27 | 87.47 | 5.0 / indeterminado |
| trafico | 2026-10-22 | 530 | 0/0 | 99.62 | 88.16 | 5.0 / indeterminado |
| trafico | 2026-10-23 | 523 | 0/0 | 99.97 | 84.03 | 0.5 / indeterminado |
| trafico | 2026-10-24 | 530 | 1/1 | 99.27 | 87.81 | 5.0 / indeterminado |
| trafico | 2026-10-25 | 551 | 1/1 | 99.63 | 84.67 | 5.0 / indeterminado |
| trafico | 2026-10-26 | 539 | 1/1 | 99.97 | 87.81 | 0.5 / indeterminado |
| trafico | 2026-10-27 | 539 | 0/0 | 99.97 | 87.47 | 0.5 / indeterminado |
| trafico | 2026-10-28 | 504 | 0/0 | 98.92 | 81.56 | 5.0 / indeterminado |
| trafico | 2026-10-29 | 512 | 0/0 | 99.27 | 80.17 | 5.0 / indeterminado |
| trafico | 2026-10-30 | 514 | 0/0 | 99.62 | 82.95 | 5.0 / indeterminado |
| trafico | 2026-10-31 | 522 | 0/0 | 99.97 | 81.91 | 0.5 / indeterminado |
| trafico | 2026-11-01 | 526 | 0/0 | 99.62 | 83.99 | 5.0 / indeterminado |
| trafico | 2026-11-02 | 503 | 3/3 | 99.27 | 82.29 | 5.0 / indeterminado |
| trafico | 2026-11-03 | 535 | 0/0 | 99.45 | 85.76 | 5.0 / indeterminado |
| trafico | 2026-11-04 | 530 | 2/2 | 99.10 | 86.60 | 5.0 / indeterminado |
| avisos | 2026-11-04 | 234 | 0/0 | 12.16 | 12.16 | 1264.9 / indeterminado |

## Fuentes sin partición diaria

Confirmado en código: meteo, catalogo_cm, externos/rodalies y horarios_oficiales son instantáneas o históricos publicados, no grabadores diarios. No se interpreta su ausencia de ficheros por día como caída. datos/redes se excluye por la restricción de licencia. Las métricas de salud no validan la veracidad de cada llegada ni la vigencia de los horarios.
