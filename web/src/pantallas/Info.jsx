// Pantalla 6: Info. Explica el método y cumple las licencias.
import { Tarjeta } from "../componentes/Comunes.jsx";
import { fecha } from "../lib/util.js";

export default function Info({ meta }) {
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
        <h2 className="text-[17px] font-bold text-tinta">Límites</h2>
        <ul className="mt-2 list-disc space-y-2 pl-5 text-[15px] text-tinta-2">
          {meta.advertencias.map((a) => (
            <li key={a}>{a}</li>
          ))}
        </ul>
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
