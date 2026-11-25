// Barra inferior (sección 1.3): cuatro botones, en este orden y con estos textos
import { IconoPin, IconoCampana, IconoInfo, IconoRutas } from "./Iconos.jsx";

const BOTONES = [
  { id: "paradas", texto: "Paradas", Icono: IconoPin },
  { id: "rutas", texto: "Rutas", Icono: IconoRutas },
  { id: "avisos", texto: "Avisos", Icono: IconoCampana },
  { id: "info", texto: "Info", Icono: IconoInfo },
];

export default function BarraInferior({ activo, onIr }) {
  return (
    <nav className="grid grid-cols-4 border-t-[2.5px] border-[#111] bg-tarjeta pb-[env(safe-area-inset-bottom)]">
      {BOTONES.map(({ id, texto, Icono }) => {
        const esActivo = activo === id;
        return (
          <button
            key={id}
            onClick={() => onIr(id)}
            aria-current={esActivo ? "page" : undefined}
            className={`flex min-h-[60px] flex-col items-center justify-center gap-0.5 px-1 text-[14px] leading-tight ${
              esActivo ? "font-bold text-principal" : "text-suave"
            }`}
          >
            <Icono />
            <span>{texto}</span>
          </button>
        );
      })}
    </nav>
  );
}
