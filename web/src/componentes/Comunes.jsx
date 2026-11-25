// Piezas pequeñas que se repiten en varias pantallas
import { nivelFiabilidad } from "../lib/ventana.js";

// Color de cada línea de metro, como en los planos (fondo, texto)
const COLOR_METRO = {
  1: ["#38A3DC", "#fff"], 2: ["#E2231A", "#fff"], 3: ["#FFD200", "#111"], 4: ["#B4692E", "#fff"],
  5: ["#9BBF2B", "#111"], 6: ["#9AA0A6", "#111"], 7: ["#F7A738", "#111"], 8: ["#EC6CA8", "#111"],
  9: ["#A3268E", "#fff"], 10: ["#1B4D9C", "#fff"], 11: ["#00A04F", "#fff"], 12: ["#B5A21B", "#111"],
};

// Número de línea en una píldora: EMT azul, interurbano verde, Cercanías rojo y metro con el color de su línea
export function Linea({ linea, red = "emt", grande = false }) {
  let fondo = "#2335F5";
  let texto = "#fff";
  if (red === "renfe") fondo = "#C8102E";
  else if (red === "interurbano") fondo = "#3F8F1E";
  else if (red === "metro") [fondo, texto] = COLOR_METRO[linea] ?? ["#3A4558", "#fff"];
  const metro = red === "metro";
  return (
    <span
      className={`inline-flex items-center justify-center border-2 border-[#111] font-bold ${metro ? "rounded-full" : "rounded-lg"} ${
        grande ? "h-[32px] min-w-[52px] px-3 text-[18px]" : "h-[26px] min-w-[44px] px-2.5 text-[16px]"
      } ${metro && grande ? "!min-w-[32px] !px-0" : metro ? "!min-w-[26px] !px-0" : ""}`}
      style={{ background: fondo, color: texto }}
      aria-label={metro ? `Metro línea ${linea}` : undefined}
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

export function Tarjeta({ children, className = "", sombra = false, ...resto }) {
  return (
    <div
      {...resto}
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
