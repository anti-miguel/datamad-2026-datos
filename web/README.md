# DATAMAD · front de la demo

Las siete pantallas de `MANUAL_PANTALLAS.md` en React + Vite + Tailwind, con el autobús que avanza en la franja de abajo.

## Arrancar

```
npm install
npm run dev        # http://localhost:5173
npm test           # casos de «Comprobación» del manual
npm run build      # web estática en dist/ (en Vercel: carpeta raíz `web`)
```

Para ensayar el pitch:

- `?hora=8:30&dia=laborable` fija la hora y el tipo de día de la consulta (como en el boceto).
- `?rapido` hace que cada minuto de la demo dure 5 s, para ver avanzar el autobús.

## Datos

- `public/datos/fiabilidad.json` y `src/lib/consultar.js`: se copian solos de `../demo` al hacer `dev`, `build` o `test` (`copiar-datos.mjs`), así siempre son idénticos. No se editan aquí.
- `src/lib/ventana.js`: copiado tal cual del manual (sección 2.3).
- `public/datos/demo.json`: el de la sección 2.4 del manual.

## Decisiones que no vienen en el manual

- Las llegadas de `demo.json` cuentan hacia atrás un minuto por minuto real; cuando pasa el último autobús la demo vuelve a empezar.
- En «¿Cuándo salgo?» el tren se enseña con el viaje ya empezado (22 min) y Atocha a dos tercios del recorrido (el manual no da su hora).
- Los `// PENDIENTE` del código marcan los huecos del manual.
