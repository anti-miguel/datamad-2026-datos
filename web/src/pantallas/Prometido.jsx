// Pantalla 4: Lo prometido frente a lo real. Obligatoria: sin datos del portal el jurado no evalúa.
import { Tarjeta, Volver } from "../componentes/Comunes.jsx";

export default function Prometido({ casos, onVolver }) {
  return (
    <div className="space-y-4">
      <Volver texto="Volver" onClick={onVolver} />
      {casos.map((c) => (
        <section key={c.titulo} className="space-y-3">
          <h1 className="text-[24px] font-bold leading-tight text-[#202124]">{c.titulo}</h1>
          <div className="grid gap-3 min-[400px]:grid-cols-2">
            <Tarjeta className="p-4">
              <p className="text-[14px] font-bold uppercase tracking-wide text-[#5F6368]">Prometido</p>
              <p className="mt-1 text-[20px] font-bold text-[#202124]">{c.prometido}</p>
              <a href={c.enlace} target="_blank" rel="noreferrer" className="mt-1 flex min-h-[44px] items-center text-[14px] text-principal underline">
                {c.fuente_prometido}
              </a>
            </Tarjeta>
            <Tarjeta className="border-2 !border-principal p-4">
              <p className="text-[14px] font-bold uppercase tracking-wide text-principal">Medido por nosotros</p>
              <p className="mt-1 text-[20px] font-bold text-[#202124]">{c.medido}</p>
            </Tarjeta>
          </div>
          <p className="text-[17px] font-bold text-[#202124]">La media cumple. Lo que falla es la regularidad.</p>
        </section>
      ))}
    </div>
  );
}
