// Pantalla 1: Paradas (inicio). Objetivo: llegar en dos toques a una parada.
import { useState } from "react";
import { Linea, Tarjeta } from "../componentes/Comunes.jsx";
import { IconoLupa, IconoAviso, IconoEstrella } from "../componentes/Iconos.jsx";
import { NOMBRE_RED, normalizar } from "../lib/util.js";
import { EscenaSegunModo } from "../componentes/Escena.jsx";
import { Logo } from "../componentes/Logo.jsx";

const FILTROS = [
  { id: "todo", texto: "Todo" },
  { id: "emt", texto: "Bus EMT" },
  { id: "interurbano", texto: "Interurbano" },
  { id: "metro", texto: "Metro" },
  { id: "renfe", texto: "Cercanías" },
];

function lineasDe(parada) {
  return [...new Set(parada.llegadas.map((l) => l.linea))];
}

function numeroDeParada(parada) {
  return parada.id.split("-")[1];
}

function TarjetaParada({ parada, favorita, nombre, onAbrir }) {
  return (
    <button onClick={onAbrir} className="block w-full text-left">
      <Tarjeta className="p-4">
        <div className="flex items-start justify-between gap-3">
          <div>
            <h3 className="text-[20px] font-bold text-tinta">{nombre ?? parada.nombre}</h3>
            {nombre && nombre !== parada.nombre && <p className="text-[14px] text-suave">{parada.nombre}</p>}
            <p className="text-[15px] text-suave">
              {NOMBRE_RED[parada.red]} · parada {numeroDeParada(parada)}
            </p>
          </div>
          {favorita && <IconoEstrella llena className="h-6 w-6 shrink-0 text-principal" />}
        </div>
        <div className="mt-2 flex flex-wrap gap-2">
          {lineasDe(parada).map((l) => (
            <Linea key={l} linea={l} red={parada.red} />
          ))}
        </div>
      </Tarjeta>
    </button>
  );
}

export default function Paradas({ demo, favoritas, nombres = {}, usuario, onAbrirParada }) {
  const [busqueda, setBusqueda] = useState("");
  const [filtro, setFiltro] = useState("todo");

  const q = normalizar(busqueda);
  const buscando = q.length >= 2;
  const porModo = demo.paradas.filter((p) => filtro === "todo" || p.red === filtro);
  const resultados = buscando
    ? porModo.filter((p) => normalizar(p.nombre).includes(q) || normalizar(nombres[p.id] ?? "").includes(q) || lineasDe(p).some((l) => normalizar(l).includes(q)))
    : [];
  const listaFavoritas = porModo.filter((p) => favoritas.includes(p.id));

  return (
    <div className="space-y-4">
      <div className="-mt-4">
        {/* key: al cambiar de filtro, el vehículo vuelve a entrar */}
        <EscenaSegunModo key={filtro} modo={filtro} />
      </div>
      <div className="flex flex-wrap-reverse items-end justify-between gap-x-3 gap-y-1">
        <div>
          {usuario && <p className="text-[16px] font-bold text-tinta-2">Hola, {usuario}</p>}
          <h1 className="titulo text-[30px] text-tinta min-[360px]:text-[34px]">Mis paradas</h1>
        </div>
        <Logo alto={30} className="mb-1 w-[112px] shrink-0" />
      </div>

      <label className="flex min-h-[48px] items-center gap-2 pegatina rounded-2xl bg-tarjeta px-4 focus-within:shadow-[4px_4px_0_#2335F5]">
        <IconoLupa className="h-5 w-5 text-suave" />
        <input
          type="search"
          value={busqueda}
          onChange={(e) => setBusqueda(e.target.value)}
          placeholder="Busca parada, línea o estación"
          aria-label="Busca parada, línea o estación"
          className="h-[46px] w-full bg-transparent text-[16px] outline-none placeholder:text-suave"
        />
      </label>

      <div className="flex flex-wrap gap-2" role="radiogroup" aria-label="Filtrar por modo">
        {FILTROS.map((f) => (
          <button
            key={f.id}
            role="radio"
            aria-checked={filtro === f.id}
            onClick={() => setFiltro(f.id)}
            className={`min-h-[44px] rounded-full border px-4 text-[16px] transition-colors ${
              filtro === f.id
                ? "boton-pegatina bg-principal font-bold text-white"
                : "boton-pegatina bg-tarjeta text-tinta"
            }`}
          >
            {f.texto}
          </button>
        ))}
      </div>

      {demo.aviso_oficial && (
        <div className="flex gap-3 rounded-2xl bg-aviso-oficial pegatina p-4 text-[#111]">
          <IconoAviso className="mt-0.5 h-5 w-5 shrink-0" />
          <p className="text-[15px]">
            {typeof demo.aviso_oficial === "string" ? demo.aviso_oficial : demo.aviso_oficial.texto}
          </p>
        </div>
      )}

      {buscando ? (
        <section className="space-y-3" aria-live="polite">
          {resultados.length === 0 ? (
            <p className="text-[15px] text-suave">No tenemos datos de esa parada todavía.</p>
          ) : (
            resultados.map((p) => (
              <TarjetaParada key={p.id} parada={p} favorita={favoritas.includes(p.id)} nombre={nombres[p.id]} onAbrir={() => onAbrirParada(p.id)} />
            ))
          )}
        </section>
      ) : (
        <section className="space-y-3">
          {listaFavoritas.length > 0 && <h2 className="text-[16px] font-bold text-tinta-2">Favoritas</h2>}
          {listaFavoritas.map((p) => (
            <TarjetaParada key={p.id} parada={p} favorita nombre={nombres[p.id]} onAbrir={() => onAbrirParada(p.id)} />
          ))}
          {listaFavoritas.length === 0 && (
            <p className="text-[15px] text-suave">Busca tu parada y pulsa la estrella para tenerla aquí.</p>
          )}
        </section>
      )}
    </div>
  );
}
