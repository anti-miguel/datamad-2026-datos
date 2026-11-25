// Casos de las listas «Comprobación» del manual de pantallas
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { consultar } from "./consultar.js";
import { casillas, nivelFiabilidad, ventana, posicionVehiculo } from "./ventana.js";
import { normalizar, llegadasVivas, calcularLlegada } from "./util.js";

const datos = JSON.parse(readFileSync(new URL("../../public/datos/fiabilidad.json", import.meta.url)));
const demo = JSON.parse(readFileSync(new URL("../../public/datos/demo.json", import.meta.url)));

test("etiquetas para p = 0.80, 0.60 y 0.40", () => {
  assert.equal(nivelFiabilidad(0.8).texto, "Fiable");
  assert.equal(nivelFiabilidad(0.6).texto, "Con margen");
  assert.equal(nivelFiabilidad(0.4).texto, "Poco fiable");
});

test("tablero: p 0.769, tarde 0.137, antes 0.094 -> 8, 1, 1", () => {
  assert.deepEqual(casillas({ p: 0.769, tarde: 0.137, antes: 0.094 }), { aTiempo: 8, tarde: 1, antes: 1 });
});

test("sin datos no hay ventana", () => {
  assert.equal(ventana(12, null), null);
});

test("con 45 min se dice que está demasiado lejos y no se consulta", () => {
  const l = calcularLlegada(datos, demo.paradas[0], { linea: "104", minutos: 45 }, { hora: 8.5, finde: false });
  assert.equal(l.lejos, true);
  assert.equal(l.v, null);
});

test("104 en Mar de Cristal, laborable 8:30, 12 min: hay ventana", () => {
  const r = consultar(datos, { red: "emt", minutos: 12, hora: 8.5, finde: false, linea: "104", tipo: "cabecera" });
  const v = ventana(12, r);
  assert.ok(v && v.desde <= 12 && v.hasta >= 12);
});

test("buscador sin mayúsculas ni tildes", () => {
  for (const q of ["MAR DE CRISTAL", "mar de cristal", "Már de crístal"]) {
    assert.ok(normalizar("Mar de Cristal").includes(normalizar(q)));
  }
});

test("posición del vehículo entre 4 y 94", () => {
  assert.equal(posicionVehiculo(60), 4);
  assert.equal(posicionVehiculo(0), 94);
});

test("la demo nunca se queda sin llegadas", () => {
  for (let t = 0; t < 60; t++) assert.ok(llegadasVivas(demo.paradas[0], t).length > 0);
});
