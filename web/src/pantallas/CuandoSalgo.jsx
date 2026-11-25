// Pantalla 3: ¿Cuándo salgo? Convierte la fiabilidad en una hora de salida (caso fijo de demo.json).
import { Tarjeta } from "../componentes/Comunes.jsx";

function FilaDias({ dias }) {
  const aTiempo = dias.filter((d) => d === 1).length;
  return (
    <div className="mt-3">
      <div className="flex flex-wrap gap-1" role="img" aria-label={`A tiempo ${aTiempo} de ${dias.length} días medidos`}>
        {dias.map((d, i) => (
          <span key={i} className={`h-4 w-4 rounded-[3px] ${d === 1 ? "bg-principal" : "bg-rojo"}`} />
        ))}
      </div>
      <p className="mt-2 text-[16px] text-[#202124]">
        A tiempo {aTiempo} de {dias.length} días medidos
      </p>
    </div>
  );
}

export default function CuandoSalgo({ caso }) {
  const { recomendada: rec, rapida } = caso;
  const rapidaATiempo = rapida.dias.filter((d) => d === 1).length;
  const arriesgado = rapidaATiempo < rapida.dias.length / 2;

  return (
    <div className="space-y-4">
      <h1 className="pt-2 text-[32px] font-bold text-[#202124]">¿Cuándo salgo?</h1>

      <dl className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-1 text-[17px]">
        <dt className="text-[#5F6368]">Desde</dt>
        <dd className="text-[#202124]">{caso.desde}</dd>
        <dt className="text-[#5F6368]">Hasta</dt>
        <dd className="text-[#202124]">{caso.hasta}</dd>
        <dt className="text-[#5F6368]">Llegar</dt>
        <dd className="text-[#202124]">
          antes de las {caso.llegar_antes} · {caso.dia}
        </dd>
      </dl>

      <Tarjeta className="border-2 !border-principal p-4">
        <p className="text-[15px] font-bold text-principal">Te recomendamos</p>
        <p className="mt-1 text-[32px] font-extrabold leading-tight text-[#202124]">Sal a las {rec.salida}</p>
        <p className="mt-1 text-[16px] text-[#3C4043]">{rec.trayecto}</p>
        <div className="mt-3 grid grid-cols-2 gap-2">
          <div className="rounded-xl bg-[#F6F5F2] p-3">
            <p className="text-[14px] text-[#5F6368]">Llegada habitual</p>
            <p className="text-[20px] font-bold text-[#202124]">{rec.llegada_habitual}</p>
          </div>
          <div className="rounded-xl bg-[#F6F5F2] p-3">
            <p className="text-[14px] text-[#5F6368]">Peor día medido</p>
            <p className="text-[20px] font-bold text-[#202124]">{rec.peor_dia}</p>
          </div>
        </div>
        <FilaDias dias={rec.dias} />
      </Tarjeta>

      <Tarjeta className="p-4">
        <div className="flex items-start justify-between gap-2">
          <p className="text-[15px] font-bold text-[#5F6368]">La opción más rápida</p>
          {arriesgado && <span className="rounded-lg bg-rojo px-2.5 py-1 text-[15px] font-bold text-white">Arriesgado</span>}
        </div>
        <p className="mt-1 text-[26px] font-bold text-[#202124]">Sal a las {rapida.salida}</p>
        <p className="mt-1 text-[16px] text-[#3C4043]">{rapida.trayecto}</p>
        <FilaDias dias={rapida.dias} />
      </Tarjeta>

      <div className="flex flex-wrap items-center gap-x-5 gap-y-2 text-[15px] text-[#3C4043]">
        <span className="flex items-center gap-2">
          <span className="h-4 w-4 rounded-[3px] bg-principal" /> A tiempo
        </span>
        <span className="flex items-center gap-2">
          <span className="h-4 w-4 rounded-[3px] bg-rojo" /> Tarde
        </span>
      </div>
      <p className="text-[15px] text-[#5F6368]">Caso real medido con el GPS de los trenes.</p>
    </div>
  );
}
