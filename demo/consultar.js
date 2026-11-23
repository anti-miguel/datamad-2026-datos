// Consulta de demo/fiabilidad.json. Sigue la misma regla que analisis/fiabilidad.py.
//   const datos = await (await fetch("fiabilidad.json")).json();
//   consultar(datos, { red: "emt", minutos: 18, hora: 8.5, finde: false, linea: "104" });
//   consultar(datos, { red: "interurbano", minutos: 20, finde: false, parada: "8_09193", linea: "691" });
//   -> { p, ic, n, tarde, antes, mediana, p10, p90, nivel }
// p10, mediana y p90 son el retraso en minutos sobre lo anunciado: la ventana es minutos + p10 … minutos + p90.
// Devuelve null si no está medido: la app no debe inventar una probabilidad.

function franja(hora) {
  if (hora >= 7 && hora < 9.5) return "punta_manana";
  if (hora >= 9.5 && hora < 17) return "valle";
  if (hora >= 17 && hora < 20) return "punta_tarde";
  return "noche";
}

// Interurbanos: por parada, línea, sentido y minuto anunciado. Sin niveles de respaldo.
// Si la parada tiene un solo sentido para esa línea, no hace falta pasarlo.
function consultarInterurbano(t, { minutos, finde = false, parada, linea, sentido = null }) {
  const sentidos = t.parada[parada]?.lineas[linea];
  if (!sentidos) return null;
  const s = sentido != null ? sentidos[String(sentido)] : Object.keys(sentidos).length === 1 ? Object.values(sentidos)[0] : null;
  const r = s?.[finde ? "finde" : "laborable"]?.[String(Math.round(minutos))];
  return r ? { ...r, nivel: "parada", destino: s.destino } : null;
}

export function consultar(datos, { red, minutos, hora, finde = false, linea = null, tipo = null, parada = null, sentido = null }) {
  const t = datos.tabla[red];
  if (!t) return null;
  if (red === "interurbano") return consultarInterurbano(t, { minutos, finde, parada, linea, sentido });
  const bin = datos.meta.anuncio_min.find(([desde, hasta]) => minutos >= desde && minutos < hasta)?.[2];
  if (!bin) return null;
  const clave = `${finde ? "finde" : "laborable"}|${franja(hora)}`;
  const l = linea != null && /^\d+$/.test(String(linea)) && red === "emt" ? String(Number(linea)) : linea;
  const niveles = [
    ["linea", t.linea[l]?.[clave]?.[bin]],
    ["tipo", t.tipo[`${tipo}|${clave}`]?.[bin]],
    ["franja", t.franja[clave]?.[bin]],
    ["red", t.red[bin]],
  ];
  const hallado = niveles.find(([, r]) => r);
  return hallado ? { ...hallado[1], nivel: hallado[0] } : null;
}

// Paradas de interurbanos medidas, para el buscador o el mapa.
export function paradasInterurbano(datos) {
  return Object.entries(datos.tabla.interurbano?.parada ?? {}).map(([codigo, p]) => ({
    codigo, nombre: p.nombre, lat: p.lat, lon: p.lon,
    lineas: Object.fromEntries(Object.entries(p.lineas).map(([l, s]) => [l, Object.entries(s).map(([sentido, v]) => ({ sentido, destino: v.destino }))])),
  }));
}
