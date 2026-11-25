// Copiado tal cual del manual de pantallas (sección 1.6 y 2.3). No cambiar estas reglas.

// Posición del vehículo en la franja, en %, hasta tu parada. 30 min o más = al principio.
export function posicionVehiculo(minutosAnunciados) {
  return Math.max(4, Math.min(94, (1 - minutosAnunciados / 30) * 100));
}

// Convierte el resultado de consultar() en lo que se pinta. No cambiar estas reglas.
export function nivelFiabilidad(p) {
  if (p >= 0.75) return { texto: "Fiable", clase: "verde" };
  if (p >= 0.50) return { texto: "Con margen", clase: "ambar" };
  return { texto: "Poco fiable", clase: "rojo" };
}

// Ventana en la que llega 8 de cada 10 veces.
// Si el margen pasa de 30 min el dato está mal (hay casillas con percentiles de ~900 min): se trata como sin datos.
export function ventana(minutosAnunciados, r) {
  if (!r) return null;
  const desde = Math.max(0, Math.floor(minutosAnunciados + r.p10));
  const hasta = Math.ceil(minutosAnunciados + r.p90);
  if (hasta - minutosAnunciados > 30 || minutosAnunciados - desde > 30) return null;
  return { desde, hasta, normal: Math.round(minutosAnunciados + r.mediana) };
}

// Tablero de 10 casillas para la pantalla 2b: cuántas de cada 10 veces llegó a tiempo, tarde o antes.
export function casillas(r) {
  const aTiempo = Math.round(r.p * 10);
  const tarde = Math.min(10 - aTiempo, Math.round(r.tarde * 10));
  return { aTiempo, tarde, antes: 10 - aTiempo - tarde };
}

export function porcentaje(x) {
  return `${Math.round(x * 100)} %`;
}

export function horaDecimal(fecha = new Date()) {
  return fecha.getHours() + fecha.getMinutes() / 60;
}

export function esFinde(fecha = new Date()) {
  const d = fecha.getDay();
  return d === 0 || d === 6;
}
