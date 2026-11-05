# Datos para la demo

`fiabilidad.json` y `consultar.js` permiten responder desde una web sin servidor: "la app dice X minutos, ¿me fío?".

```js
import { consultar } from "./consultar.js";

const datos = await (await fetch("fiabilidad.json")).json();
const r = consultar(datos, { red: "emt", minutos: 18, hora: 8.5, finde: false, linea: "104" });
// r.p: probabilidad de llegar a ±2 min. r.nivel: linea, tipo, franja o red. null si no está medido.
```

- **Redes:** `emt`, `renfe` y `metro`.
- **Campos, franjas y orden de consulta:** están en `datos.meta`.
- **Regenerar:** `python analisis/exportar_demo.py`, desde la raíz de `datos-transporte`, después de regenerar la tabla.

## Al mostrarlo

- **Atribución:** usa `meta.redes.<red>.atribucion`.
- **Metro:** se mide con el widget del Consorcio. Cita la fuente y la fecha de extracción (`meta.datos_desde` y `meta.datos_hasta`), no alteres su sentido y no sugieras que el Consorcio patrocina el proyecto.
- **Honestidad:** muestra `meta.advertencias` cerca del resultado. Si `nivel` no es `linea`, di que es una estimación general de la red.
- **Licencia:** este JSON deriva de datos de la EMT, así que se publica con ODbL.
