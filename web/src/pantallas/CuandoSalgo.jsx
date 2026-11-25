// Pantalla 3: ¿Cuándo salgo? Convierte la fiabilidad en una hora de salida (caso fijo de demo.json).
import { Tarjeta } from "../componentes/Comunes.jsx";
import { EscenaTren } from "../componentes/Escena.jsx";

function FilaDias({ dias }) {
  const aTiempo = dias.filter((d) => d === 1).length;
  return (
    <div className="mt-3">
      <div className="flex flex-wrap gap-1" role="img" aria-label={`A tiempo ${aTiempo} de ${dias.length} días medidos`}>
        {dias.map((d, i) => (
          <span key={i} className={`h-4 w-4 rounded-[3px] ${d === 1 ? "bg-principal" : "bg-rojo"}`} />
        ))}
      </div>
      <p className="mt-2 text-[16px] text-tinta">
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
      <div className="-mt-4">
        <EscenaTren />
      </div>
      <h1 className="titulo text-[34px] text-tinta">¿Cuándo salgo?</h1>

      <dl className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-1 text-[17px]">
        <dt className="text-suave">Desde</dt>
        <dd className="text-tinta">{caso.desde}</dd>
        <dt className="text-suave">Hasta</dt>
        <dd className="text-tinta">{caso.hasta}</dd>
        <dt className="text-suave">Llegar</dt>
        <dd className="text-tinta">
          antes de las {caso.llegar_antes} · {caso.dia}
        </dd>
      </dl>

      <Tarjeta className="p-4 !bg-amarillo">
        <p className="text-[15px] font-bold uppercase tracking-wide text-[#111]">Te recomendamos</p>
        <p className="cifra mt-1 text-[36px] tabular-nums text-tinta">Sal a las {rec.salida}</p>
        <p className="mt-1 text-[16px] text-tinta-2">{rec.trayecto}</p>
        <div className="mt-3 grid grid-cols-2 gap-2">
          <div className="rounded-xl border-2 border-[#111] bg-tarjeta p-3">
            <p className="text-[14px] text-suave">Llegada habitual</p>
            <p className="text-[20px] font-bold text-tinta">{rec.llegada_habitual}</p>
          </div>
          <div className="rounded-xl border-2 border-[#111] bg-tarjeta p-3">
            <p className="text-[14px] text-suave">Peor día medido</p>
            <p className="text-[20px] font-bold text-tinta">{rec.peor_dia}</p>
          </div>
        </div>
        <FilaDias dias={rec.dias} />
      </Tarjeta>

      <Tarjeta className="p-4">
        <div className="flex items-start justify-between gap-2">
          <p className="text-[15px] font-bold text-suave">La opción más rápida</p>
          {arriesgado && <span className="rounded-lg bg-rojo px-2.5 py-1 text-[15px] font-bold text-white">Arriesgado</span>}
        </div>
        <p className="cifra mt-1 text-[28px] text-tinta">Sal a las {rapida.salida}</p>
        <p className="mt-1 text-[16px] text-tinta-2">{rapida.trayecto}</p>
        <FilaDias dias={rapida.dias} />
      </Tarjeta>

      <div className="flex flex-wrap items-center gap-x-5 gap-y-2 text-[15px] text-tinta-2">
        <span className="flex items-center gap-2">
          <span className="h-4 w-4 rounded-[3px] bg-principal" /> A tiempo
        </span>
        <span className="flex items-center gap-2">
          <span className="h-4 w-4 rounded-[3px] bg-rojo" /> Tarde
        </span>
      </div>
      <p className="text-[15px] text-suave">Caso real medido con el GPS de los trenes.</p>
    </div>
  );
}
