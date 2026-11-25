// Tren con los vagones numerados (el 1 es el de cabeza) y los que conviene coger para salir antes
// o hacer el transbordo más rápido. Tocando un vagón se marca o se desmarca: es «tu truco».
// Plegado en una sola línea para no cargar el itinerario; se abre al tocarlo.
import { useState } from "react";

function listaTexto(n) {
  if (n.length === 1) return `el vagón ${n[0]}`;
  return `el vagón ${n.slice(0, -1).join(", ")} o ${n[n.length - 1]}`;
}

export default function Vagones({ total = 6, numeros = [], motivo, color = "#2335F5", onCambiar }) {
  const marcados = [...numeros].sort((a, b) => a - b);
  const [abierto, setAbierto] = useState(false);

  function alternar(n) {
    onCambiar(marcados.includes(n) ? marcados.filter((x) => x !== n) : [...marcados, n]);
  }

  return (
    <div className="mt-2 rounded-xl border-2 border-[#111] bg-tarjeta">
      <button
        type="button"
        onClick={() => setAbierto((x) => !x)}
        aria-expanded={abierto}
        className="flex min-h-[44px] w-full items-center justify-between gap-2 px-3 text-left text-[15px] font-bold text-tinta"
      >
        <span>{marcados.length ? `Ponte en ${listaTexto(marcados)}` : "¿En qué vagón te pones?"}</span>
        <span aria-hidden="true" className={`transition-transform ${abierto ? "rotate-180" : ""}`}>▾</span>
      </button>
      {abierto && (
      <div className="px-3 pb-3">
      {motivo && marcados.length > 0 && <p className="text-[13px] text-suave">{motivo}</p>}

      {/* el tren va hacia la derecha: el vagón 1 es el de cabeza */}
      <div className="mt-2 flex items-end gap-[3px]" role="group" aria-label="Vagones del tren, del último al primero">
        {Array.from({ length: total }, (_, i) => total - i).map((n) => {
          const activo = marcados.includes(n);
          const cabeza = n === 1;
          return (
            <button
              key={n}
              type="button"
              aria-pressed={activo}
              aria-label={`Vagón ${n}${cabeza ? " (cabeza)" : ""}`}
              onClick={() => alternar(n)}
              className={`flex h-[40px] min-w-0 flex-1 items-center justify-center border-2 border-[#111] text-[14px] font-bold transition-colors ${
                cabeza ? "rounded-l-md rounded-r-[14px]" : "rounded-md"
              } ${activo ? "text-white" : "bg-hundido text-tinta"}`}
              style={activo ? { background: color } : undefined}
            >
              {n}
            </button>
          );
        })}
      </div>
      <div className="mt-1 flex justify-between text-[12px] font-bold text-suave">
        <span>cola</span>
        <span>sentido de la marcha →</span>
      </div>
      </div>
      )}
    </div>
  );
}
