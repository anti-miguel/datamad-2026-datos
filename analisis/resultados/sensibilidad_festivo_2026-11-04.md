# Sensibilidad al festivo del 02/11, corte 2026-11-04

Confirmado en código: preparar() mantiene la regla histórica que trata como festivo solo el 12/10, además de fines de semana. El 02/11/2026 es lunes y queda como laborable. cruce_catalogo.py lo excluye de laborables porque calendar_dates del GTFS no ofrece servicio LA.
Comprobado ejecutando: esta tabla alternativa solo cambia tipo_dia a finde el 02/11; conserva predicciones, llegadas y reglas de los demás días. Recalcula los agregados afectados. No sustituye la tabla principal ni modifica el servicio de consulta o la demo.

| Red | Predicciones reclasificadas | Llegadas reclasificadas |
|---|---:|---:|
| emt | 93813 | 10211 |
| metro | 135339 | 33983 |
| renfe | 18913 | 8763 |

Cambios en probabilidades publicadas redondeadas a tres decimales:
- 1_red: 17 celdas emparejadas; 0 cambian de acierto. Con al menos 30 llegadas en ambas versiones (17 celdas), cambio absoluto mediano 0.00 y máximo 0.00 puntos; 0 celdas nuevas y 0 desaparecidas.
- 2_franja: 136 celdas emparejadas; 104 cambian de acierto. Con al menos 30 llegadas en ambas versiones (136 celdas), cambio absoluto mediano 0.10 y máximo 3.00 puntos; 0 celdas nuevas y 0 desaparecidas.
- 3_tipo: 184 celdas emparejadas; 152 cambian de acierto. Con al menos 30 llegadas en ambas versiones (184 celdas), cambio absoluto mediano 0.30 y máximo 3.00 puntos; 0 celdas nuevas y 0 desaparecidas.
- 4_linea: 4916 celdas emparejadas; 4048 cambian de acierto. Con al menos 30 llegadas en ambas versiones (4354 celdas), cambio absoluto mediano 0.50 y máximo 16.50 puntos; 1 celdas nuevas y 24 desaparecidas.

Inferencia: la clasificación del festivo puede cambiar consultas por franja, tipo y línea (niveles 2 a 4); el nivel 1 por red y anuncio no usa tipo_dia y permanece igual. Esta sensibilidad no demuestra una diferencia real de servicio entre festivos y laborables.
