// Pantalla 6: Info. Explica el método y cumple las licencias.
import { Tarjeta } from "../componentes/Comunes.jsx";
import { fecha } from "../lib/util.js";

export default function Info({ meta, sesion, onSalir }) {
  const desde = fecha(meta.datos_desde);
  const hasta = fecha(meta.datos_hasta);
  const f = meta.fuentes;
  const fuentes = [
    { texto: "Portal de Datos Abiertos de la Comunidad de Madrid", url: f["Portal de Datos Abiertos de la Comunidad de Madrid"] },
    { texto: "Powered by EMT de Madrid", url: f["EMT Madrid, tiempo real"] },
    { texto: "Fuente: Renfe", url: f["Renfe, horarios de viaje"] },
    {
      texto: `Fuente: Consorcio Regional de Transportes de Madrid. Datos extraídos del ${desde} al ${hasta}.`,
      url: f["Consorcio Regional de Transportes de Madrid"],
    },
  ];

  return (
    <div className="space-y-4">
      {sesion && (
        <Tarjeta className="flex items-center gap-3 p-4">
          <span className="pegatina flex h-[48px] w-[48px] shrink-0 items-center justify-center rounded-full bg-amarillo text-[20px] font-bold">
            {sesion.nombre.charAt(0)}
          </span>
          <span className="min-w-0 flex-1">
            <span className="block text-[17px] font-bold text-tinta">{sesion.nombre}</span>
            <span className="block truncate text-[14px] text-suave">{sesion.correo}</span>
          </span>
          <button onClick={onSalir} className="boton-pegatina min-h-[44px] shrink-0 rounded-xl bg-tarjeta px-3 text-[15px] font-bold">
            Cerrar sesión
          </button>
        </Tarjeta>
      )}
      <h1 className="titulo pt-2 text-[34px] text-tinta">Cómo funciona</h1>
      <p className="text-[17px] text-tinta">
        Grabamos lo que anuncian las apps oficiales y lo comparamos con cuándo llega de verdad. Con eso calculamos cuánto
        fiarse de cada anuncio.
      </p>
      <p className="text-[16px] text-tinta-2">
        Datos del {desde} al {hasta}.
      </p>

      <Tarjeta className="p-4">
        <h2 className="text-[17px] font-bold text-tinta">Fuentes</h2>
        <ul className="mt-1">
          {fuentes.map((x) => (
            <li key={x.texto}>
              <a href={x.url} target="_blank" rel="noreferrer" className="flex min-h-[44px] items-center text-[15px] text-principal underline">
                {x.texto}
              </a>
            </li>
          ))}
        </ul>
        <p className="mt-3 text-[15px] text-tinta-2">Los datos derivados se publican con licencia ODbL.</p>
      </Tarjeta>

      <Tarjeta className="p-4">
        <details>
          <summary className="min-h-[36px] cursor-pointer text-[17px] font-bold text-tinta">Límites de los datos</summary>
          <ul className="mt-2 list-disc space-y-2 pl-5 text-[15px] text-tinta-2">
            {meta.advertencias.map((a) => (
              <li key={a}>{a}</li>
            ))}
          </ul>
        </details>
      </Tarjeta>

      {/* PENDIENTE: el manual pide el repositorio de la app cuando sea público; mientras, el de datos, que ya lo es */}
      <a
        href="https://github.com/anti-miguel/datamad-2026-datos"
        target="_blank"
        rel="noreferrer"
        className="block min-h-[44px] text-[16px] text-principal underline"
      >
        Código abierto en GitHub
      </a>
    </div>
  );
}
