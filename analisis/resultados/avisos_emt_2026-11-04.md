# Avisos EMT: contraste retrospectivo

Corte de llegadas: 2026-11-04. Trabajo previo al desarrollo de DATAMAD.

**Confirmado en código.** La definición completa de pares, franjas, control, placebo y selección está en la cabecera de `analisis/avisos_emt.py`. Las reglas se fijaron antes de ejecutar el contraste, sin buscar el antiguo resultado. Los desplazamientos conservan la hora local: en octubre, una hora repetida se interpreta como su primera ocurrencia; una hora inexistente se lleva al siguiente instante válido.

**Comprobado ejecutando.**

- Aviso frente a control: 299 pares, 52 avisos; diferencia mediana -6.56 puntos porcentuales; IC95 [-9.42, -3.24].
- Aviso frente a control, muestra común: 179 pares, 35 avisos; diferencia mediana -9.18 puntos porcentuales; IC95 [-12.71, -4.54].
- Placebo +7 días frente al mismo control, muestra común: 179 pares, 35 avisos; diferencia mediana +1.44 puntos porcentuales; IC95 [+0.01, +3.40].
- Aviso menos placebo, muestra común: 179 pares, 35 avisos; diferencia mediana -10.01 puntos porcentuales; IC95 [-15.67, -4.33].

La mediana entre pares pasa de 65.29% en control a 55.24% durante el aviso. La diferencia de estas dos medianas no es, en general, la mediana de las diferencias emparejadas.
Se suman 90,168 anuncios de aviso y 259,062 de control entre los pares; son sumas por par, con reutilización de observaciones, no anuncios independientes.

Avisos en la última versión: 198; pares candidatos con ficheros presentes en sus fechas y línea GTFS: 1252. Selección: `{"avisos_mayores_24h": 71, "avisos_hasta_24h": 126, "avisos_con_fechas_sin_fichero": 7, "pares_linea_fuera_gtfs": 8, "avisos_fechas_invalidas": 1, "pares_sin_dos_controles_con_datos": 915, "pares_aviso_muestra_insuficiente": 521, "pares_control_muestra_insuficiente": 597}`. Los recuentos de descarte por pares no son excluyentes; el CSV conserva todos los candidatos con sus tamaños y elegibilidad.
Extracción de llegadas: `{"visitas_con_cierre": 410538, "visitas_sin_cierre": 218706, "anuncios_elegibles": 2787660}`.

**Diferencia respecto al 67% → 60%, 631 pares y placebo +1.** El cálculo original no tiene código ni definición exacta de franjas, duración, umbrales, controles o normalización; por ello no puede certificarse una réplica literal. Este contraste usa episodios de hasta 24 h, ventanas locales exactas, controles semanales libres de avisos conocidos, mínimo de muestra por brazo, dos controles con datos y cierre estricto de 120 s igual al de `tabla_fiabilidad.extraer_emt` para todas las paradas. El cierre de 400 s en cabeceras que describe el README corresponde a otro criterio y aquí no se aplica. El universo disponible ahora llega al 04/11. No se han variado estas reglas para acercarse a esas cifras.

**Confirmado en código y GTFS local.** `001` (Atocha–Moncloa) y `1` (Cristo Rey–Prosperidad), así como `002` y `2`, son líneas distintas. Eliminar todos los ceros fusionaría servicios diferentes; aquí se conservan las claves exactas y solo se resuelven alias inequívocos. El consejo de normalizar ceros del README necesita esta salvedad.

**Retrospectiva y limitaciones.** 1248 de los pares candidatos empiezan antes de la primera observación local del aviso. El RSS comenzó a grabarse el 2026-11-04; solo conserva una selección de avisos antiguos y las versiones disponibles pueden haber cambiado después del suceso. No se usa `pub` como fecha de conocimiento. La ausencia de aviso conservado no acredita ausencia de incidencias en los controles. Las fechas invertidas se excluyen sin inventar una corrección.

**Inferencia.** El contraste describe asociación en las paradas medidas; un aviso afecta solo a parte de la línea. Las tasas no se estandarizan por parada, horizonte del anuncio, lluvia o festivos, y los controles agrupan las ventanas con datos. La existencia del fichero diario no acredita cobertura continua del grabador ni del operador; los umbrales de muestra no eliminan ese sesgo. La llegada está estimada con el propio operador; las visitas sin cierre no entran y podrían contener fallos importantes. No demuestra un efecto causal ni sirve como validación prospectiva de una alerta en la app. El placebo debe interpretarse con su intervalo, sin dar por supuesto un efecto exactamente nulo.

IC95 percentil con 5000 remuestreos de avisos completos, semilla 20261105. Se mantienen juntas sus líneas, pero pueden quedar dependencias entre avisos solapados, días, líneas y controles reutilizados. El tamaño independiente se aproxima por avisos; una muestra pequeña requiere cautela.

Comandos desde la raíz:

```powershell
python -m unittest analisis.test_avisos_emt
python analisis/avisos_emt.py
```

Intérprete ejecutado: `E:\Program Files\Python313\python.exe`; Python 3.13.2, pandas 2.2.3, NumPy 2.2.4.

Fuente: llegadas MobilityLabs y RSS público de EMT de Madrid, copia local hasta el corte indicado. Powered by EMT de Madrid. Condiciones: ODbL y MobilityLabs según README. Ningún acceso a red ni a NAS.
