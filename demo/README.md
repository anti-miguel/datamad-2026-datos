# Datos para la demo

`fiabilidad.json` y `consultar.js` permiten responder desde una web sin servidor: "la app dice X minutos, ¿me fío?". No hace falta backend; se sirven como archivos estáticos junto a la web.

```js
import { consultar, paradasInterurbano } from "./consultar.js";

const datos = await (await fetch("fiabilidad.json")).json();

// EMT, Metro y Renfe: por línea, franja y tipo de día; si no hay dato de la línea, cae a tipo, franja o red.
const r = consultar(datos, { red: "emt", minutos: 12, hora: 8.5, finde: false, linea: "104" });

// Interurbanos (691): por parada, sentido y minuto anunciado.
const s = consultar(datos, { red: "interurbano", minutos: 20, finde: false, parada: "8_09193", linea: "691" });
// Ventana: de 20 + s.p10 a 20 + s.p90 -> "suele llegar entre 19 y 27".
```

- **Qué devuelve:** `{ p, ic, n, tarde, antes, mediana, p10, p90, nivel }`, o `null` si no está medido. `p10`, `mediana` y `p90` son el retraso en minutos sobre lo anunciado. Con esto funcionan `ventana()`, `casillas()` y `nivelFiabilidad()` del manual de pantallas.
- **Redes:** `emt`, `metro`, `renfe` e `interurbano`.
- **Líneas EMT:** sin ceros delante (`"1"`, `"104"`). `consultar` también acepta `"001"`.
- **Interurbanos:** `paradasInterurbano(datos)` lista las paradas medidas con nombre, coordenadas, sentidos y destino. En Zoco (`8_06516`) hay dos sentidos y hay que pasar `sentido: 1` (hacia Los Copos) o `sentido: 2` (hacia Moncloa); si no, devuelve `null`. Las cabeceras (Moncloa y Los Copos) no están porque allí el panel solo enseña el horario.
- **Campos, franjas, casillas quitadas y fechas:** están en `datos.meta`.

## Regenerar

Desde la raíz de `datos-transporte`, con el mismo corte en los tres pasos:

```
python analisis/tabla_fiabilidad.py <carpeta para la caché> --corte 2026-11-22
python analisis/ventanas_interurbanos.py --corte 2026-11-22
python analisis/exportar_demo.py --corte 2026-11-22
```

El exportador quita las casillas con p10 o p90 de más de 30 min, porque son ruido de pocas visitas; la consulta usa entonces el nivel siguiente.

## Al mostrarlo

- **Atribución:** usa `meta.redes.<red>.atribucion`.
- **Metro e interurbanos:** se miden con el panel del Consorcio. Cita la fuente y la fecha de extracción (`meta.datos_desde` y `meta.datos_hasta`), no alteres su sentido y no sugieras que el Consorcio patrocina el proyecto.
- **Interurbanos:** la llegada es aproximada, la última hora anunciada antes de que el autobús desaparezca del panel. Dilo en la pantalla de información.
- **Honestidad:** muestra `meta.advertencias` cerca del resultado. Si `nivel` es `tipo`, `franja` o `red`, di que es una estimación general.
- **Licencia:** este JSON deriva de datos de la EMT, así que se publica con ODbL.
