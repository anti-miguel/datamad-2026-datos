// Utilidades de la app: textos, fechas y cálculo de cada llegada.
import { consultar } from "./consultar.js";
import { ventana } from "./ventana.js";

export const NOMBRE_RED = {
  emt: "Bus EMT",
  interurbano: "Interurbano",
  metro: "Metro",
  renfe: "Cercanías",
};

// Icono genérico según la red (sección 1.2: nada de logotipos de operadores)
export function iconoDeRed(red) {
  if (red === "renfe") return "tren";
  if (red === "metro") return "metro";
  return "bus";
}

// Sin mayúsculas ni tildes, para el buscador
export function normalizar(texto) {
  return String(texto).normalize("NFD").replace(/\p{Diacritic}/gu, "").toLowerCase().trim();
}

// 8.5 -> "8:30"
export function horaTexto(decimal) {
  const h = Math.floor(decimal);
  const m = Math.round((decimal - h) * 60);
  return `${h}:${String(m).padStart(2, "0")}`;
}

// "7:35" -> minutos desde medianoche
export function aMinutos(hhmm) {
  const [h, m] = hhmm.split(":").map(Number);
  return h * 60 + m;
}

// "2026-09-24" -> "24/09/2026" (o "24/09" si corto)
export function fecha(iso, corto = false) {
  const [a, m, d] = iso.split("-");
  return corto ? `${d}/${m}` : `${d}/${m}/${a}`;
}

// Franja del día con las mismas horas que consultar.js, para el pie de la pantalla 2b
export function textoFranja(hora) {
  if (hora >= 7 && hora < 9.5) return "mañana";
  if (hora >= 9.5 && hora < 17) return hora < 14 ? "mañana" : "tarde";
  if (hora >= 17 && hora < 20) return "tarde";
  return "noche";
}

export function plural(n, uno, varios) {
  return n === 1 ? uno : varios;
}

// Calcula todo lo que se pinta de una llegada: resultado de consultar() y ventana.
export function calcularLlegada(datos, parada, llegada, contexto) {
  if (llegada.minutos >= 40) return { ...llegada, lejos: true, r: null, v: null };
  const r = consultar(datos, {
    red: parada.red,
    minutos: llegada.minutos,
    hora: contexto.hora,
    finde: contexto.finde,
    linea: llegada.linea,
    tipo: parada.tipo,
    parada: parada.codigo ?? null,
    sentido: parada.sentido ?? null,
  });
  return { ...llegada, lejos: false, r, v: ventana(llegada.minutos, r) };
}

// Llegadas que siguen pendientes tras «transcurrido» minutos de demo.
// Cuando pasa el último autobús, la demo vuelve a empezar (ciclo), así nunca se queda vacía.
export function llegadasVivas(parada, transcurrido) {
  const max = Math.max(...parada.llegadas.map((l) => l.minutos));
  const t = max > 0 ? transcurrido % max : 0;
  return parada.llegadas
    .map((l) => ({ ...l, minutos: l.minutos - t }))
    .filter((l) => l.minutos >= 1);
}

// Hora y tipo de día de la consulta. Para ensayar el pitch se puede forzar con ?hora=8:30&dia=laborable
export function contextoActual(fechaReal = new Date(), busqueda = "") {
  const q = new URLSearchParams(busqueda);
  let hora = fechaReal.getHours() + fechaReal.getMinutes() / 60;
  let finde = fechaReal.getDay() === 0 || fechaReal.getDay() === 6;
  if (q.get("hora") && /^\d{1,2}:\d{2}$/.test(q.get("hora"))) hora = aMinutos(q.get("hora")) / 60;
  if (q.get("dia") === "laborable") finde = false;
  if (q.get("dia") === "finde") finde = true;
  return { hora, finde };
}
