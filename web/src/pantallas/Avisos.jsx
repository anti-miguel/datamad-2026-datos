// Pantalla 5: Avisos (simulación). Siguiente fase al estilo de avisos de viajeros, marcada como simulación.
// Los botones solo cambian el contador en pantalla: no se guarda nada.
import { useState } from "react";
import { Linea, Tarjeta } from "../componentes/Comunes.jsx";

const OPCIONES = ["Retraso", "Bus lleno", "No ha pasado", "Desvío", "Parada anulada", "Accesibilidad"];

// Las líneas de interurbanos (3 cifras que empiezan por 6) en gris, como en el boceto
function redDeLinea(linea) {
  return /^6\d\d$/.test(linea) ? "interurbano" : "emt";
}

function TarjetaAviso({ aviso }) {
  const [confirman, setConfirman] = useState(aviso.confirman);
  return (
    <Tarjeta className="p-4">
      <div className="flex items-center gap-3">
        <Linea linea={aviso.linea} red={redDeLinea(aviso.linea)} />
        <h2 className="text-[18px] font-bold text-tinta">{aviso.texto}</h2>
      </div>
      <p className="mt-2 text-[15px] text-suave" aria-live="polite">
        hace {aviso.hace_min} min · {confirman === 1 ? "1 viajero lo confirma" : `${confirman} viajeros lo confirman`}
      </p>
      <div className="mt-3 grid grid-cols-2 gap-2">
        <button
          onClick={() => setConfirman((n) => n + 1)}
          className="boton-pegatina min-h-[44px] rounded-xl bg-tarjeta text-[16px]"
        >
          Sigue pasando
        </button>
        <button
          onClick={() => setConfirman((n) => Math.max(0, n - 1))}
          className="boton-pegatina min-h-[44px] rounded-xl bg-tarjeta text-[16px]"
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
        <h1 className="titulo text-[34px] text-tinta">Avisos</h1>
        {avisos.map((a) => (
          <TarjetaAviso key={a.texto} aviso={a} />
        ))}
        {gracias && (
          <p role="status" className="rounded-2xl bg-aviso-simulado p-4 text-[15px] text-[#2A1060]">
            Gracias. En la versión real tu aviso se compartiría con otros viajeros.
          </p>
        )}
      </div>

      <button
        onClick={() => setAbierto(true)}
        className="fixed bottom-[calc(76px+env(safe-area-inset-bottom))] right-[max(16px,calc(50vw-215px+16px))] z-30 min-h-[52px] rounded-full bg-principal px-6 text-[18px] font-bold text-white boton-pegatina"
      >
        + Avisar
      </button>

      {abierto && (
        <div className="fixed inset-0 z-40 flex items-end justify-center bg-black/30" onClick={() => setAbierto(false)}>
          <div
            role="dialog"
            aria-label="Elige qué quieres avisar"
            className="w-full max-w-[430px] rounded-t-2xl bg-tarjeta p-4 pb-[calc(16px+env(safe-area-inset-bottom))]"
            onClick={(e) => e.stopPropagation()}
          >
            <ul className="divide-y divide-linea">
              {OPCIONES.map((o) => (
                <li key={o}>
                  <button
                    className="min-h-[52px] w-full text-left text-[17px] text-tinta"
                    onClick={() => {
                      setAbierto(false);
                      setGracias(true);
                    }}
                  >
                    {o}
                  </button>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}
