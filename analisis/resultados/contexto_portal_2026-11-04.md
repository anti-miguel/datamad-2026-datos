# Contexto del portal, corte 2026-11-04

Comprobado ejecutando: copias locales de los datasets 902003 y 1923861, descargadas el 05/11/2026.

EMT: 439.8 millones de billetes en 2019 frente a 454.6 en 2023, cambio +3.4%; 39 años válidos.
Sensibilidad de escenario: usando EWT mediana de punta 2.47 min (63 líneas de al menos 100 intervalos), serían 18.11 M horas con demanda de 2019 y 18.71 M horas con la última demanda. Es una extrapolación de paradas céntricas a toda la red, con viajeros que llegan al azar; no mide horas perdidas reales ni demanda de 2026.

Limitación confirmada en código: el cruce histórico quita ceros de las líneas y puede mezclar 001/1 y 002/2. Las métricas de esas claves y su efecto en horarios requieren corrección independiente; véase lineas_emt_ambiguas_2026-11-04.md. El escenario mantiene el método histórico para su comparación.

Renfe: 18 de 21 estaciones con dato oficial de 2024 se cruzan con al menos 500 llegadas; cubren 91.6% de los viajeros subidos y bajados publicados para esas 21 estaciones. No equivale a cobertura de toda la red ni a personas únicas.
Sensibilidad Renfe al año del peso: 20 años con cruces. Acierto ponderado con pesos 2024: 64.54%. Con pesos 2019: 64.79%; diferencia -0.25 puntos porcentuales.
Se mantienen las tasas observadas en septiembre-noviembre de 2026 y se varían solo los pesos. Se usan las tasas de estación redondeadas a tres decimales del cruce (hasta 0,05 puntos porcentuales de redondeo); los cambios de cobertura anual también influyen. No es una evolución histórica de la fiabilidad.
La cobertura por volumen permite describir el subconjunto al que se aplica la ponderación. Las tasas de error siguen dependiendo del método de observación y de su posible sesgo en túneles.

Inferencia: conviene presentar el periodo de demanda junto a cada ponderación y comparar estaciones con independencia de la demanda antes de convertir la tasa en una prioridad de producto.
