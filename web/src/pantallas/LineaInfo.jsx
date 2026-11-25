// Pantalla 2b: Lo que conviene saber de la línea. Aquí van las estadísticas que no caben en la 2.
import { Linea, Tarjeta, Volver } from "../componentes/Comunes.jsx";
import { casillas, porcentaje } from "../lib/ventana.js";
import { fecha, plural, textoFranja } from "../lib/util.js";

function Casilla({ tipo }) {
  const estilo = {
    tiempo: "bg-verde",
    tarde: "bg-ambar",
    antes: "bg-transparent border-2 border-dashed border-suave",
  }[tipo];
  return <div className={`aspect-square flex-1 rounded-md ${estilo}`} />;
}

function Leyenda({ tipo, numero, texto }) {
  return (
    <li className="flex items-center gap-2 text-[16px] text-tinta">
      <span className="flex h-[18px] w-[18px] shrink-0">
        <Casilla tipo={tipo} />
      </span>
      <span className="w-4 font-bold">{numero}</span>
      <span>{texto}</span>
    </li>
  );
}

export default function LineaInfo({ parada, linea, llegada, meta, contexto, rarezas, onVolver, onPrometido }) {
  const r = llegada?.r ?? null;
  const c = r ? casillas(r) : null;
  const tipoDia = contexto.finde ? "Fines de semana" : "Laborables";

  return (
    <div className="space-y-4">
      <Volver texto={parada.nombre} onClick={onVolver} />
      <div className="flex items-center gap-3">
        <Linea linea={linea} red={parada.red} grande />
        <h1 className="titulo text-[28px] leading-tight text-tinta">Lo que conviene saber</h1>
      </div>

      <Tarjeta className="divide-y divide-linea">
        {rarezas.length === 0 ? (
          <p className="p-4 text-[16px] text-tinta">Esta línea no tiene nada raro que contar.</p>
        ) : (
          rarezas.map((a) => (
            <div key={a.titulo} className="p-4">
              <h2 className="text-[17px] font-bold text-tinta">{a.titulo}</h2>
              <p className="mt-1 text-[15px] text-tinta-2">{a.texto}</p>
            </div>
          ))
        )}
      </Tarjeta>

      <Tarjeta className="p-4">
        <h2 className="text-[18px] font-bold text-tinta">
          De cada 10 veces que la app dijo «{llegada?.minutos} min»
        </h2>
        {c ? (
          <>
            <div className="mt-3 flex gap-1.5" role="img" aria-label={`${c.aTiempo} a tiempo, ${c.tarde} tarde y ${c.antes} antes de cada 10`}>
              {Array.from({ length: c.aTiempo }, (_, i) => <Casilla key={`v${i}`} tipo="tiempo" />)}
              {Array.from({ length: c.tarde }, (_, i) => <Casilla key={`a${i}`} tipo="tarde" />)}
              {Array.from({ length: c.antes }, (_, i) => <Casilla key={`b${i}`} tipo="antes" />)}
            </div>
            <ul className="mt-3 space-y-1.5">
              <Leyenda tipo="tiempo" numero={c.aTiempo} texto={`${plural(c.aTiempo, "llegó", "llegaron")} cuando decía (±2 min)`} />
              <Leyenda tipo="tarde" numero={c.tarde} texto={`${plural(c.tarde, "llegó", "llegaron")} más de 2 min tarde`} />
              <Leyenda tipo="antes" numero={c.antes} texto={`${plural(c.antes, "llegó", "llegaron")} más de 2 min antes`} />
            </ul>
            <p className="mt-3 text-[14px] text-suave">
              {tipoDia} por la {textoFranja(contexto.hora)}, {r.n} llegadas medidas del {fecha(meta.datos_desde, true)} al{" "}
              {fecha(meta.datos_hasta, true)}.
            </p>
          </>
        ) : (
          // PENDIENTE: el manual no define el tablero sin datos; se dice lo mismo que en la pantalla 2
          <p className="mt-3 text-[16px] text-suave">Sin datos suficientes</p>
        )}
      </Tarjeta>

      {r && (
        <details className="rounded-2xl border border-linea bg-tarjeta">
          <summary className="min-h-[52px] cursor-pointer px-4 py-3.5 text-[17px] text-tinta">Datos completos</summary>
          <p className="px-4 pb-4 text-[15px] text-tinta-2">
            Acierta a ±2 min el {porcentaje(r.p)} (intervalo del {porcentaje(r.ic[0])} al {porcentaje(r.ic[1])}). Tarde el{" "}
            {porcentaje(r.tarde)}, antes el {porcentaje(r.antes)}.
          </p>
        </details>
      )}

      <button
        onClick={onPrometido}
        className="flex min-h-[52px] w-full items-center justify-between px-1 text-[18px] text-principal"
      >
        <span>Lo prometido frente a lo real</span>
        <span aria-hidden>→</span>
      </button>
    </div>
  );
}
