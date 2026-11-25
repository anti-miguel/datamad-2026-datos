// Pantalla «Mis rutas»: rutas guardadas (a la uni, al trabajo, a casa de la abuela) con sus
// opciones, transbordos y el tiempo total. Cada ruta se puede renombrar.
import { useMemo, useState } from "react";
import { Linea, Etiqueta, Tarjeta, Volver } from "../componentes/Comunes.jsx";
import {
  IconoAndar, IconoTransbordo, IconoLapiz, IconoUni, IconoTrabajo, IconoCasa, IconoRutas,
} from "../componentes/Iconos.jsx";
import { calcularRuta, cadenaDeLineas } from "../lib/rutas.js";

const ICONOS = { uni: IconoUni, trabajo: IconoTrabajo, casa: IconoCasa };

// Nombre editable en el sitio: lápiz → campo → guardar
export function NombreEditable({ nombre, onCambiar, className = "", etiqueta = "Cambiar nombre" }) {
  const [editando, setEditando] = useState(false);
  const [texto, setTexto] = useState(nombre);
  if (editando) {
    return (
      <form
        className="flex items-center gap-2"
        onSubmit={(e) => {
          e.preventDefault();
          const limpio = texto.trim();
          if (limpio) onCambiar(limpio.slice(0, 40));
          setEditando(false);
        }}
      >
        <input
          autoFocus
          value={texto}
          maxLength={40}
          onChange={(e) => setTexto(e.target.value)}
          aria-label={etiqueta}
          className="pegatina h-[44px] min-w-0 flex-1 rounded-xl bg-tarjeta px-3 text-[17px] font-bold"
        />
        <button type="submit" className="boton-pegatina min-h-[44px] rounded-xl bg-amarillo px-3 font-bold">
          Guardar
        </button>
      </form>
    );
  }
  return (
    <div className="flex items-start gap-2">
      <span className={className}>{nombre}</span>
      <button
        onClick={(e) => {
          e.stopPropagation();
          setTexto(nombre);
          setEditando(true);
        }}
        aria-label={etiqueta}
        className="boton-pegatina flex h-[36px] w-[36px] shrink-0 items-center justify-center rounded-lg bg-tarjeta"
      >
        <IconoLapiz className="h-4 w-4" />
      </button>
    </div>
  );
}

// Tira de líneas de la tarjeta: «4 106 159 287 ⇄ 2 ⇄ 5»
function Cadena({ ruta }) {
  return (
    <div className="flex flex-wrap items-center gap-1.5">
      {cadenaDeLineas(ruta).map((c, i) =>
        c.transbordo ? (
          <span key={i} className="flex items-center text-tinta" aria-label="transbordo">
            <IconoTransbordo className="h-5 w-5" />
          </span>
        ) : (
          <span key={i} className="flex flex-wrap items-center gap-1">
            {c.lineas.map((l, j) => (
              <span key={l.linea} className="flex items-center gap-1">
                {j > 0 && <span className="text-[13px] font-bold text-suave">o</span>}
                <Linea linea={l.linea} red={l.red} />
              </span>
            ))}
          </span>
        ),
      )}
    </div>
  );
}

function TextoTotal({ total }) {
  return total ? `${total.desde}–${total.hasta} min` : "Sin datos suficientes";
}

export function ListaRutas({ rutas, datos, contexto, nombres, onRenombrar, onAbrir }) {
  return (
    <div className="space-y-4">
      <h1 className="titulo pt-2 text-[32px] text-tinta">Mis rutas</h1>
      <p className="text-[16px] text-tinta-2">Tus viajes de siempre, con todas las formas de hacerlos y cuánto tardas de verdad.</p>
      {rutas.map((ruta) => {
        const Icono = ICONOS[ruta.icono] ?? IconoRutas;
        const { total } = datos ? calcularRuta(datos, ruta, contexto) : { total: null };
        const nombre = nombres[`ruta-${ruta.id}`] ?? ruta.nombre;
        return (
          <Tarjeta key={ruta.id} className="overflow-hidden">
            <div className="flex items-start gap-3 p-4 pb-3">
              <span className="pegatina flex h-[48px] w-[48px] shrink-0 items-center justify-center rounded-xl bg-amarillo">
                <Icono />
              </span>
              <div className="min-w-0 flex-1">
                <NombreEditable
                  nombre={nombre}
                  onCambiar={(n) => onRenombrar(`ruta-${ruta.id}`, n)}
                  etiqueta={`Cambiar el nombre de la ruta ${nombre}`}
                  className="titulo text-[19px] text-tinta"
                />
                <p className="mt-1 text-[15px] text-suave">
                  {ruta.desde} → {ruta.hasta}
                </p>
                {ruta.ejemplo && (
                  <span className="mt-1 inline-block rounded-md border-2 border-[#111] bg-aviso-simulado px-2 text-[13px] font-bold">
                    EJEMPLO
                  </span>
                )}
              </div>
            </div>
            <div className="px-4 pb-3">
              <Cadena ruta={ruta} />
            </div>
            <button
              onClick={() => onAbrir(ruta.id)}
              className="flex min-h-[56px] w-full items-center justify-between border-t-[2.5px] border-[#111] bg-hundido px-4 text-left"
            >
              <span className="text-[15px] text-tinta-2">Si sales ahora, llegas en</span>
              <span className="cifra text-[20px] text-principal">
                <TextoTotal total={total} /> →
              </span>
            </button>
          </Tarjeta>
        );
      })}
      <p className="text-[14px] text-suave">
        Las esperas salen de los datos medidos; los tiempos de viaje y de transbordo son aproximados.
      </p>
    </div>
  );
}

// Un tramo de la línea de tiempo vertical
function Paso({ color, children, punteado = false, ultimo = false }) {
  return (
    <div className="relative flex gap-3">
      <div className="flex w-[28px] shrink-0 flex-col items-center">
        <div
          className={`w-[6px] flex-1 ${ultimo ? "" : "min-h-[24px]"}`}
          style={
            punteado
              ? { backgroundImage: "radial-gradient(#111 1.6px, transparent 1.8px)", backgroundSize: "6px 9px", backgroundRepeat: "repeat-y" }
              : { background: color, border: "2px solid #111", borderRadius: 4 }
          }
        />
      </div>
      <div className="min-w-0 flex-1 pb-3">{children}</div>
    </div>
  );
}

function Hito({ texto, sub, final = false }) {
  return (
    <div className="flex items-center gap-3">
      <div className="flex w-[28px] justify-center">
        <div className={`h-[20px] w-[20px] rounded-full border-[3px] border-[#111] ${final ? "bg-amarillo" : "bg-tarjeta"}`} />
      </div>
      <div>
        <p className="text-[17px] font-bold text-tinta">{texto}</p>
        {sub && <p className="text-[14px] text-suave">{sub}</p>}
      </div>
    </div>
  );
}

const COLOR_TRAMO = { emt: "#2335F5", interurbano: "#3F8F1E", renfe: "#C8102E" };

function OpcionEspera({ o, elegida, recomendada, onElegir }) {
  const activa = elegida.linea === o.linea;
  return (
    <button
      onClick={onElegir}
      aria-pressed={activa}
      className={`boton-pegatina flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left ${activa ? "bg-amarillo" : "bg-tarjeta"}`}
    >
      <span className="self-start pt-0.5">
        <Linea linea={o.linea} red={o.red} />
      </span>
      <span className="min-w-0 flex-1">
        <span className="block text-[17px] font-bold leading-snug text-tinta">
          {o.lejos ? "Demasiado lejos para estimar" : o.v ? `Pasa entre ${o.v.desde} y ${o.v.hasta} min` : "Sin datos suficientes"}
        </span>
        <span className="mt-0.5 block text-[14px] text-suave">
          La app dice {o.minutos} min · viaje ≈ {o.viaje} min
        </span>
        {(o.v || (o.r && o.r.nivel !== "linea")) && (
          <span className="mt-1.5 flex flex-wrap items-center gap-2">
            {o.v && <Etiqueta p={o.r.p} />}
            {recomendada.linea === o.linea && o.v && (
              <span className="rounded-md border-2 border-[#111] bg-verde px-1.5 text-[13px] font-bold text-white">MEJOR OPCIÓN</span>
            )}
            {o.r && o.r.nivel !== "linea" && <span className="text-[13px] text-suave">estimación general de la red</span>}
          </span>
        )}
      </span>
    </button>
  );
}

export function DetalleRuta({ ruta, datos, contexto, nombres, onRenombrar, onVolver }) {
  const [elegidas, setElegidas] = useState({});
  const calculo = useMemo(() => calcularRuta(datos, ruta, contexto, elegidas), [datos, ruta, contexto, elegidas]);
  const nombre = nombres[`ruta-${ruta.id}`] ?? ruta.nombre;
  const nTransbordos = ruta.tramos.filter((t) => t.tipo === "transbordo").length;

  return (
    <div className="space-y-4">
      <Volver texto="Mis rutas" onClick={onVolver} />
      <NombreEditable
        nombre={nombre}
        onCambiar={(n) => onRenombrar(`ruta-${ruta.id}`, n)}
        etiqueta={`Cambiar el nombre de la ruta ${nombre}`}
        className="titulo text-[28px] text-tinta"
      />

      <Tarjeta sombra className="!bg-amarillo p-4">
        <p className="text-[14px] font-bold uppercase tracking-wide">Si sales ahora, llegas en</p>
        <p className="cifra mt-1 text-[36px] tabular-nums">
          <TextoTotal total={calculo.total} />
        </p>
        <p className="mt-1 text-[15px]">
          {nTransbordos === 0 ? "Sin transbordos" : nTransbordos === 1 ? "1 transbordo" : `${nTransbordos} transbordos`} · elige
          la línea en cada tramo y el total se recalcula
        </p>
      </Tarjeta>

      <Tarjeta className="p-4">
        <Hito texto={ruta.desde} sub="Salida" />
        {calculo.tramos.map((t, i) => {
          if (t.tipo === "andar" || t.tipo === "transbordo") {
            return (
              <Paso key={i} punteado>
                <div
                  className={`mt-2 flex items-center gap-2 rounded-xl px-3 py-2 ${
                    t.tipo === "transbordo" ? "pegatina bg-aviso-simulado" : "bg-hundido"
                  }`}
                >
                  {t.tipo === "transbordo" ? <IconoTransbordo /> : <IconoAndar />}
                  <span className="text-[15px] font-bold text-tinta">{t.texto}</span>
                  <span className="ml-auto shrink-0 text-[14px] text-tinta-2">{t.minutos} min</span>
                </div>
              </Paso>
            );
          }
          const color = t.tipo === "metro" ? null : COLOR_TRAMO[t.elegida.red];
          return (
            <div key={i}>
              {/* si se viene de un transbordo en la misma estación, no se repite su nombre */}
              {t.tipo === "metro" && calculo.tramos[i - 1]?.tipo !== "transbordo" && <Hito texto={`Metro ${t.desde}`} />}
              <Paso color={color ?? colorMetro(t.linea)}>
                {t.tipo === "metro" ? (
                  <div className="space-y-2 pt-1">
                    <div className="flex items-center gap-2">
                      <Linea linea={t.linea} red="metro" grande />
                      <span className="text-[16px] font-bold text-tinta">Dirección {t.hasta}</span>
                    </div>
                    <OpcionEspera o={t.elegida} elegida={t.elegida} recomendada={t.recomendada} onElegir={() => {}} />
                    <details className="text-[14px] text-tinta-2">
                      <summary className="min-h-[36px] py-1.5">{t.paradas.length} paradas entre medias</summary>
                      <p>{t.paradas.join(" · ")}</p>
                    </details>
                  </div>
                ) : (
                  <div className="space-y-2 pt-1">
                    <p className="text-[16px] font-bold text-tinta">{t.titulo}</p>
                    {t.nota && <p className="text-[14px] text-suave">{t.nota}</p>}
                    {t.opciones.map((o) => (
                      <OpcionEspera
                        key={o.linea}
                        o={o}
                        elegida={t.elegida}
                        recomendada={t.recomendada}
                        onElegir={() => setElegidas((e) => ({ ...e, [i]: o.linea }))}
                      />
                    ))}
                  </div>
                )}
              </Paso>
              {t.tipo === "metro" && <Hito texto={`Metro ${t.hasta}`} />}
            </div>
          );
        })}
        <Hito texto={ruta.hasta} sub="Llegada" final />
      </Tarjeta>

      <p className="text-[14px] text-suave">
        {ruta.ejemplo ? "Ruta de ejemplo. " : ""}Las esperas salen de los datos medidos; los tiempos de viaje y de transbordo son
        aproximados.
      </p>
    </div>
  );
}

// Color de la línea de metro para la barra del tramo
function colorMetro(linea) {
  return { 1: "#38A3DC", 2: "#E2231A", 5: "#9BBF2B" }[linea] ?? "#3A4558";
}
