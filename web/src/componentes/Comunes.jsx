// Piezas pequeñas que se repiten en varias pantallas
import { nivelFiabilidad } from "../lib/ventana.js";

// Número de línea en una píldora. EMT en color principal; el resto, en gris oscuro.
export function Linea({ linea, red = "emt", grande = false }) {
  const color = red === "emt" ? "bg-principal" : red === "renfe" ? "bg-[#C8102E]" : red === "interurbano" ? "bg-[#3F8F1E]" : "bg-[#3A4558]";
  return (
    <span
      className={`${color} inline-flex items-center justify-center rounded-lg border-2 border-[#111] font-bold text-white ${
        grande ? "min-w-[52px] px-3 h-[32px] text-[18px]" : "min-w-[44px] px-2.5 h-[26px] text-[16px]"
      }`}
    >
      {linea}
    </span>
  );
}

const COLOR_TEXTO = { verde: "text-verde-vivo", ambar: "text-ambar-vivo", rojo: "text-rojo-vivo" };
const COLOR_FONDO = { verde: "bg-verde", ambar: "bg-ambar", rojo: "bg-rojo" };

// Etiqueta de fiabilidad: siempre texto además del color (sección 1.4)
export function Etiqueta({ p, relleno = false }) {
  const n = nivelFiabilidad(p);
  if (relleno) {
    return (
      <span className={`${COLOR_FONDO[n.clase]} inline-block rounded-lg border-2 border-[#111] px-2.5 py-1 font-bold text-white`}>
        {n.texto}
      </span>
    );
  }
  return <span className={`${COLOR_TEXTO[n.clase]} font-bold`}>{n.texto}</span>;
}

export function Tarjeta({ children, className = "", sombra = false }) {
  return (
    <div
      className={`rounded-2xl bg-tarjeta ${sombra ? "pegatina-grande" : "pegatina"} ${className}`}
    >
      {children}
    </div>
  );
}

export function Volver({ texto, onClick }) {
  return (
    <button onClick={onClick} className="min-h-[44px] text-principal text-[16px] -ml-1 px-1">
      ← {texto}
    </button>
  );
}
