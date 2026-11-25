// Cálculo de las rutas guardadas: ventana de espera de cada opción con consultar() y ventana(),
// la opción que conviene coger y el total de la ruta (de lo más rápido a lo más lento).
import { consultar } from "./consultar.js";
import { ventana } from "./ventana.js";

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

// La opción que conviene: la que antes llega a destino en el peor caso medido.
// Las que no tienen datos van al final: no se recomienda nada sin datos detrás.
export function mejorOpcion(opciones) {
  const conDatos = opciones.filter((o) => o.v);
  if (conDatos.length === 0) return opciones[0];
  return conDatos.reduce((a, b) => (b.v.hasta + b.viaje < a.v.hasta + a.viaje ? b : a));
}

// Calcula todos los tramos y el total. «elegidas» guarda la opción escogida por tramo (índice → línea).
export function calcularRuta(datos, ruta, contexto, elegidas = {}) {
  let desde = 0;
  let hasta = 0;
  let completo = true;

  const tramos = ruta.tramos.map((t, i) => {
    if (t.tipo === "andar" || t.tipo === "transbordo") {
      desde += t.minutos;
      hasta += t.minutos;
      return t;
    }
    const lista = t.opciones ?? [{ red: t.red, linea: t.linea, tipo: "estacion", minutos: t.minutos, viaje: t.viaje }];
    const opciones = lista.map((o) => esperaDe(datos, o, contexto));
    const recomendada = mejorOpcion(opciones);
    const elegida = opciones.find((o) => o.linea === elegidas[i]) ?? recomendada;
    if (elegida.v) {
      desde += elegida.v.desde + elegida.viaje;
      hasta += elegida.v.hasta + elegida.viaje;
    } else {
      completo = false;
    }
    return { ...t, opciones, recomendada, elegida };
  });

  return { tramos, total: completo ? { desde, hasta } : null };
}

// Líneas de cada tramo, en orden, para la tira de la tarjeta («4 · 106 · 159 · 287 → 2 → 5»)
export function cadenaDeLineas(ruta) {
  return ruta.tramos
    .filter((t) => t.tipo !== "andar")
    .map((t) =>
      t.tipo === "transbordo"
        ? { transbordo: true }
        : { lineas: (t.opciones ?? [t]).map((o) => ({ linea: o.linea, red: o.red })) },
    );
}
