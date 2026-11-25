// Pantalla 5: Avisos (simulación). Siguiente fase: avisos de viajeros, dejando claro que es una simulación.
// Los botones solo cambian el contador en pantalla: no se guarda nada.
import { useState } from "react";
import { Linea, Tarjeta } from "../componentes/Comunes.jsx";
import { IconoGente, IconoCoche, IconoReloj, IconoAviso } from "../componentes/Iconos.jsx";

// Tipo de aviso según su texto: icono, color y nombre
function tipoDe(texto) {
  const t = texto.toLowerCase();
  if (t.includes("lleno")) return { Icono: IconoGente, color: "#D9C8FF", nombre: "Bus lleno" };
  if (t.includes("atasco") || t.includes("retraso")) return { Icono: IconoCoche, color: "#FFB547", nombre: "Retraso" };
  if (t.includes("no ha pasado")) return { Icono: IconoReloj, color: "#FF8A80", nombre: "No ha pasado" };
  return { Icono: IconoAviso, color: "#FFE15A", nombre: "Aviso" };
}

const OPCIONES = [
  { texto: "Retraso", Icono: IconoCoche, color: "#FFB547" },
  { texto: "Bus lleno", Icono: IconoGente, color: "#D9C8FF" },
  { texto: "No ha pasado", Icono: IconoReloj, color: "#FF8A80" },
  { texto: "Desvío", Icono: IconoAviso, color: "#FFE15A" },
  { texto: "Parada anulada", Icono: IconoAviso, color: "#FFE15A" },
  { texto: "Accesibilidad", Icono: IconoGente, color: "#B4F0C8" },
];

// Redes de cada línea para pintar la píldora con su color
function redDeLinea(linea) {
  return /^6\d\d$/.test(linea) ? "interurbano" : "emt";
}

function TarjetaAviso({ aviso }) {
  const [confirman, setConfirman] = useState(aviso.confirman);
  const [voto, setVoto] = useState(null);
  const { Icono, color, nombre } = tipoDe(aviso.texto);

  function votar(sigue) {
    if (voto === sigue) return;
    setConfirman((n) => Math.max(0, n + (sigue ? 1 : -1) + (voto === null ? 0 : sigue ? 1 : -1)));
    setVoto(sigue);
  }

  return (
    <Tarjeta className="overflow-hidden">
      <div className="flex gap-3 p-4">
        <span
          className="pegatina flex h-[52px] w-[52px] shrink-0 items-center justify-center rounded-xl"
          style={{ background: color }}
        >
          <Icono className="h-7 w-7" />
        </span>
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <Linea linea={aviso.linea} red={redDeLinea(aviso.linea)} />
            <span className="rounded-md border-2 border-[#111] bg-hundido px-1.5 text-[13px] font-bold">{nombre.toUpperCase()}</span>
          </div>
          <h2 className="titulo mt-1.5 text-[19px] text-tinta">{aviso.texto}</h2>
          <p className="mt-1 text-[14px] text-suave">hace {aviso.hace_min} min</p>
        </div>
      </div>

      {/* viajeros que lo confirman: un círculo por persona, hasta 6 */}
      <div className="flex items-center gap-2 px-4 pb-3" aria-live="polite">
        <span className="flex -space-x-2" aria-hidden="true">
          {Array.from({ length: Math.min(confirman, 6) }, (_, i) => (
            <span key={i} className="h-[24px] w-[24px] rounded-full border-2 border-[#111]" style={{ background: ["#B4C3FF", "#FFE15A", "#D9C8FF", "#B4F0C8"][i % 4] }} />
          ))}
        </span>
        <span className="text-[15px] font-bold text-tinta">
          {confirman === 1 ? "1 viajero lo confirma" : `${confirman} viajeros lo confirman`}
        </span>
      </div>

      <div className="grid grid-cols-2 border-t-[2.5px] border-[#111]">
        <button
          onClick={() => votar(true)}
          aria-pressed={voto === true}
          className={`min-h-[52px] border-r-[2.5px] border-[#111] text-[16px] font-bold ${voto === true ? "bg-amarillo" : "bg-tarjeta"}`}
        >
          Sigue pasando
        </button>
        <button
          onClick={() => votar(false)}
          aria-pressed={voto === false}
          className={`min-h-[52px] text-[16px] font-bold ${voto === false ? "bg-amarillo" : "bg-tarjeta"}`}
        >
          Ya no
        </button>
      </div>
    </Tarjeta>
  );
}

export default function Avisos({ avisos }) {
  const [abierto, setAbierto] = useState(false);
  const [gracias, setGracias] = useState(false);

  return (
    <div className="-mx-4 -mt-4">
      <div className="sticky top-0 z-20 border-b-[2.5px] border-[#111] bg-aviso-simulado px-4 py-3 text-[15px] font-bold text-[#2A1060]">
        SIMULACIÓN · Así funcionarían los avisos de viajeros
      </div>

      <div className="space-y-4 px-4 pt-4">
        <div className="flex items-end justify-between gap-3">
          <h1 className="titulo text-[34px] text-tinta">Avisos</h1>
          <span className="pegatina mb-1 rounded-full bg-amarillo px-3 py-1 text-[15px] font-bold">{avisos.length} cerca de ti</span>
        </div>
        <p className="text-[16px] text-tinta-2">Lo que cuentan otros viajeros ahora mismo. Confírmalo si lo estás viendo.</p>
        {avisos.map((a) => (
          <TarjetaAviso key={a.texto} aviso={a} />
        ))}
        {gracias && (
          <p role="status" className="pegatina rounded-2xl bg-aviso-simulado p-4 text-[15px] font-bold text-[#2A1060]">
            Gracias. En la versión real tu aviso se compartiría con otros viajeros.
          </p>
        )}
      </div>

      <button
        onClick={() => setAbierto(true)}
        className="boton-pegatina fixed bottom-[calc(76px+env(safe-area-inset-bottom))] right-[max(16px,calc(50vw-215px+16px))] z-30 min-h-[56px] rounded-full bg-principal px-6 text-[18px] font-bold text-white"
      >
        + Avisar
      </button>

      {abierto && (
        <div className="fixed inset-0 z-40 flex items-end justify-center bg-black/40" onClick={() => setAbierto(false)}>
          <div
            role="dialog"
            aria-label="Elige qué quieres avisar"
            className="w-full max-w-[430px] rounded-t-3xl border-x-[2.5px] border-t-[2.5px] border-[#111] bg-tarjeta p-4 pb-[calc(16px+env(safe-area-inset-bottom))]"
            onClick={(e) => e.stopPropagation()}
          >
            <p className="titulo mb-3 text-[20px]">¿Qué está pasando?</p>
            <div className="grid grid-cols-2 gap-3">
              {OPCIONES.map(({ texto, Icono, color }) => (
                <button
                  key={texto}
                  className="boton-pegatina flex min-h-[72px] flex-col items-start justify-center gap-1 rounded-xl px-3 text-left text-[16px] font-bold"
                  style={{ background: color }}
                  onClick={() => {
                    setAbierto(false);
                    setGracias(true);
                  }}
                >
                  <Icono className="h-6 w-6" />
                  {texto}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
