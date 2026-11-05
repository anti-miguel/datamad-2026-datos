// Consulta de demo/fiabilidad.json. Sigue la misma regla que analisis/fiabilidad.py.
//   const datos = await (await fetch("fiabilidad.json")).json();
//   consultar(datos, { red: "emt", minutos: 18, hora: 8.5, finde: false, linea: "104" });
//   -> { p: 0.638, ic: [...], n: ..., tarde: ..., antes: ..., mediana: ..., p10: ..., p90: ..., nivel: "linea" }
// Devuelve null si no está medido: la app no debe inventar una probabilidad.

function franja(hora) {
  if (hora >= 7 && hora < 9.5) return "punta_manana";
  if (hora >= 9.5 && hora < 17) return "valle";
  if (hora >= 17 && hora < 20) return "punta_tarde";
  return "noche";
}

export function consultar(datos, { red, minutos, hora, finde = false, linea = null, tipo = null }) {
  const bin = datos.meta.anuncio_min.find(([desde, hasta]) => minutos >= desde && minutos < hasta)?.[2];
  const t = datos.tabla[red];
  if (!bin || !t) return null;
  const clave = `${finde ? "finde" : "laborable"}|${franja(hora)}`;
  const niveles = [
    ["linea", t.linea[linea]?.[clave]?.[bin]],
    ["tipo", t.tipo[`${tipo}|${clave}`]?.[bin]],
    ["franja", t.franja[clave]?.[bin]],
    ["red", t.red[bin]],
  ];
  const hallado = niveles.find(([, r]) => r);
  return hallado ? { ...hallado[1], nivel: hallado[0] } : null;
}
