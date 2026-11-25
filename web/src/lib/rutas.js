// Cálculo de rutas: ventana de espera de cada opción con consultar() y ventana(),
// la opción que conviene según el modo, el total, cuándo salir y cuánto se ahorra.
import { consultar } from "./consultar.js";
import { ventana } from "./ventana.js";
import { aMinutos } from "./util.js";

// Ventana de espera de una opción (bus, tren o metro) a partir de lo que anuncia la app
export function esperaDe(datos, opcion, contexto) {
  if (opcion.minutos >= 40) return { ...opcion, lejos: true, r: null, v: null };
  const r = consultar(datos, {
    red: opcion.red,
    minutos: opcion.minutos,
    hora: contexto.hora,
    finde: contexto.finde,
    linea: opcion.linea,
    tipo: opcion.tipo ?? (opcion.red === "emt" ? "intermedia" : "estacion"),
    parada: opcion.parada ?? null,
  });
  return { ...opcion, lejos: false, r, v: ventana(opcion.minutos, r) };
}

// Lo que tarda una opción desde que llegas a la parada hasta que te bajas: [lo mejor, lo peor]
function duracion(o) {
  const extra = o.andar_extra ?? 0;
  return [o.v.desde + o.viaje + extra, o.v.hasta + o.viaje + extra];
}

// Opción que conviene. «segura»: la que llega antes en el peor caso medido (lo normal).
// «rapida» (voy con prisa): la que llega antes si todo sale bien, aunque sea menos fiable.
// Las que no tienen datos nunca se recomiendan.
export function mejorOpcion(opciones, modo = "segura") {
  const conDatos = opciones.filter((o) => o.v);
  if (conDatos.length === 0) return opciones[0];
  const i = modo === "rapida" ? 0 : 1;
  return conDatos.reduce((a, b) => (duracion(b)[i] < duracion(a)[i] ? b : a));
}

// Calcula todos los tramos y el total. «elegidas» guarda la línea escogida a mano por tramo.
export function calcularRuta(datos, ruta, contexto, elegidas = {}, modo = "segura") {
  let desde = 0;
  let hasta = 0;
  let completo = true;
  let transbordos = 0;

  const tramos = ruta.tramos.map((t, i) => {
    if (t.tipo === "andar" || t.tipo === "transbordo") {
      if (t.tipo === "transbordo") transbordos += 1;
      desde += t.minutos;
      hasta += t.minutos;
      return t;
    }
    const lista = t.opciones ?? [{ red: t.red, linea: t.linea, tipo: "estacion", minutos: t.minutos, viaje: t.viaje }];
    const opciones = lista.map((o) => esperaDe(datos, o, contexto));
    const recomendada = mejorOpcion(opciones, modo);
    const elegida = opciones.find((o) => o.linea === elegidas[i]) ?? recomendada;
    if (elegida.v) {
      const [a, b] = duracion(elegida);
      desde += a;
      hasta += b;
    } else {
      completo = false;
    }
    return { ...t, opciones, recomendada, elegida };
  });

  return { tramos, transbordos, total: completo ? { desde, hasta } : null };
}

// Hora a la que hay que salir para llegar antes de «llegarAntes».
// «segura»: contando el peor caso medido. «rapida» (voy con prisa): si todo va bien, más arriesgado.
export function horaDeSalida(total, llegarAntes, modo = "segura") {
  if (!total || !llegarAntes) return null;
  const m = aMinutos(llegarAntes) - (modo === "rapida" ? total.desde : total.hasta);
  const h = Math.floor(m / 60);
  return `${h}:${String(m % 60).padStart(2, "0")}`;
}

// Minutos que te quedan para salir de casa y coger el primer vehículo de la ruta:
// lo antes que puede pasar menos lo que tardas en llegar andando a la parada.
export function salirEn(calculo) {
  let andar = 0;
  for (const t of calculo.tramos) {
    if (t.tipo === "andar") andar += t.minutos;
    else if (t.elegida) {
      if (!t.elegida.v) return null;
      return { minutos: t.elegida.v.desde - andar - (t.elegida.andar_extra ?? 0), linea: t.elegida.linea, red: t.elegida.red };
    }
  }
  return null;
}

// Líneas de cada tramo, en orden, para la tira de la tarjeta («4 o 106 o 159 o 287 ⇄ 2 ⇄ 5»)
export function cadenaDeLineas(ruta) {
  return ruta.tramos
    .filter((t) => t.tipo !== "andar")
    .map((t) =>
      t.tipo === "transbordo"
        ? { transbordo: true }
        : { lineas: (t.opciones ?? [t]).map((o) => ({ linea: o.linea, red: o.red })) },
    );
}
