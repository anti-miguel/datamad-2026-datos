// Pantalla 2: Parada, al estilo de la app de la EMT: todas las líneas que pasan, cuándo llega
// cada una (con la ventana medida), avisos de posible incidencia y «¿dónde te bajas?».
// Los porcentajes y el tablero siguen en la 2b (botón «i» de cada línea).
import { useEffect, useRef, useState } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { Linea, Etiqueta, Tarjeta, Volver } from "../componentes/Comunes.jsx";
import { IconoEstrella, IconoInfo, IconoAviso, IconoCampana } from "../componentes/Iconos.jsx";
import { NOMBRE_RED, horaTexto } from "../lib/util.js";
import { casillas } from "../lib/ventana.js";
import { NombreEditable } from "./Rutas.jsx";
import { incidenciasDelTramo } from "../lib/rutas.js";

function Minimapa({ lat, lon }) {
  const caja = useRef(null);
  useEffect(() => {
    const mapa = L.map(caja.current, {
      center: [lat, lon],
      zoom: 17,
      dragging: false,
      zoomControl: false,
      scrollWheelZoom: false,
      doubleClickZoom: false,
      touchZoom: false,
      boxZoom: false,
      keyboard: false,
    });
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution: "© OpenStreetMap",
    }).addTo(mapa);
    L.circleMarker([lat, lon], {
      radius: 9,
      color: "#111111",
      weight: 3,
      fillColor: "#FFE15A",
      fillOpacity: 1,
    }).addTo(mapa);
    // Si cambia el ancho (girar el móvil), el mapa se recoloca para no dejar zonas grises
    const observador = new ResizeObserver(() => mapa.invalidateSize());
    observador.observe(caja.current);
    return () => {
      observador.disconnect();
      mapa.remove();
    };
  }, [lat, lon]);
  return <div ref={caja} className="pegatina h-[150px] overflow-hidden rounded-2xl" role="img" aria-label="Mapa de la parada" />;
}

// Tarjetas grises vacías mientras carga fiabilidad.json
export function ParadaCargando() {
  return (
    <div className="space-y-3 animate-pulse" aria-label="Cargando">
      <div className="h-[200px] rounded-2xl bg-linea" />
      <div className="h-[200px] rounded-2xl bg-linea" />
    </div>
  );
}

const ventanaTexto = (l) =>
  l.lejos ? "Demasiado lejos para estimar" : l.v ? `Llega entre ${l.v.desde} y ${l.v.hasta} min` : "Sin datos suficientes";

// Una tarjeta por línea: la siguiente llegada en grande y la de después en pequeño
// Tramo dibujado parada a parada, desde la de subida hasta la de bajada, con las incidencias en su sitio
function TramoDibujado({ recorrido, fin, incidencias, subida }) {
  const tramo = recorrido.slice(0, fin + 1);
  const marca = (i) => incidencias.find((x) => x.posicion === i);
  const filas = [{ nombre: subida, subida: true }, ...tramo];
  return (
    <ol className="mt-3 space-y-0" aria-label="Tu tramo, parada a parada">
      {filas.map((p, i) => {
        const inc = i > 0 ? marca(i - 1) : null;
        const ultima = i === filas.length - 1;
        return (
          <li key={i} className="flex gap-3">
            <span className="flex w-[18px] flex-col items-center">
              <span
                className={`mt-1 h-[14px] w-[14px] shrink-0 rounded-full border-[3px] border-[#111] ${
                  inc ? "bg-rojo" : p.subida || ultima ? "bg-amarillo" : "bg-tarjeta"
                }`}
              />
              {!ultima && <span className="w-[4px] flex-1 bg-[#111]" />}
            </span>
            <span className="pb-2 text-[14px] leading-snug">
              <span className={`${p.subida || ultima ? "font-bold" : ""} ${inc ? "font-bold text-[#7A0F0A]" : "text-tinta"}`}>
                {p.nombre}
              </span>
              {p.subida && <span className="text-suave"> · subes aquí</span>}
              {ultima && <span className="text-suave"> · te bajas · {p.minutos} min de viaje</span>}
              {inc && <span className="block text-[13px] font-bold text-[#7A0F0A]">{inc.texto} · +{inc.retraso} min</span>}
            </span>
          </li>
        );
      })}
    </ol>
  );
}

function TarjetaLinea({ linea, llegadas, red, primera, recorrido, avisosLinea, bajada, onBajada, onInfo, incidencias, subida, aproximado }) {
  const [a, b] = llegadas;
  const [destinoSel, setDestinoSel] = useState(bajada?.linea === linea ? bajada.codigo : "");
  const parada = recorrido?.find((p) => p.codigo === destinoSel);
  const avisando = bajada?.linea === linea && bajada.codigo === destinoSel;

  // Posible incidencia sacada de los datos: a esta hora y con lo que anuncia, acierta menos de la mitad de las veces
  const flojo = a.r && a.v && a.r.p < 0.5 ? casillas(a.r).aTiempo : null;

  return (
    <Tarjeta sombra={primera} className="overflow-hidden">
      <div className="p-4">
        <div className="flex items-center justify-between gap-3">
          <div className="flex min-w-0 items-center gap-3">
            <Linea linea={linea} red={red} grande />
            <span className="truncate text-[17px] text-tinta">→ {a.destino}</span>
          </div>
          <button
            onClick={onInfo}
            aria-label={`Qué conviene saber del ${linea}`}
            className="flex h-[44px] w-[44px] shrink-0 items-center justify-center rounded-full border-2 border-[#111] bg-amarillo text-[#111]"
          >
            <IconoInfo />
          </button>
        </div>

        <p className="mt-3 text-[15px] text-suave">La app oficial dice {a.minutos} min</p>
        <p className={`cifra mt-1 tabular-nums ${primera ? "text-[32px]" : "text-[26px]"}`}>{ventanaTexto(a)}</p>

        {a.v && (
          <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-2">
            <Etiqueta p={a.r.p} relleno />
            <span className="text-[15px] text-tinta">Si a los {a.v.hasta} min no ha llegado, algo pasa.</span>
          </div>
        )}
        {a.r && a.r.nivel !== "linea" && <p className="mt-2 text-[14px] text-suave">Estimación general de la red</p>}

        {b && (
          <p className="mt-3 rounded-lg bg-hundido px-3 py-2 text-[15px] text-tinta-2">
            El siguiente: <span className="font-bold text-tinta">{b.v ? `entre ${b.v.desde} y ${b.v.hasta} min` : `${b.minutos} min según la app`}</span>
          </p>
        )}
      </div>

      {/* avisos de posible incidencia */}
      {(flojo !== null || avisosLinea.length > 0) && (
        <div className="space-y-2 border-t-[2.5px] border-[#111] bg-amarillo px-4 py-3">
          {flojo !== null && (
            <p className="flex gap-2 text-[15px] font-bold">
              <IconoAviso className="mt-0.5 h-5 w-5 shrink-0" />
              Posible incidencia: a esta hora solo acierta {flojo} de cada 10 veces. Sal con margen.
            </p>
          )}
          {avisosLinea.map((av) => (
            <p key={av.texto} className="flex gap-2 text-[15px]">
              <IconoAviso className="mt-0.5 h-5 w-5 shrink-0" />
              <span>
                <span className="font-bold">Viajeros (simulación):</span> {av.texto} · hace {av.hace_min} min
              </span>
            </p>
          ))}
        </div>
      )}

      {/* ¿dónde te bajas? Se pregunta para revisar las incidencias de tu tramo, no de toda la línea */}
      {recorrido && (
        <div className="border-t-[2.5px] border-[#111] px-4 py-3">
          <label className="block text-[14px] font-bold uppercase text-suave" htmlFor={`bajada-${linea}`}>
            ¿Dónde te bajas?
          </label>
          <p className="text-[13px] text-suave">Así revisamos si hay algo en tu tramo, aunque el resto de la línea vaya bien.</p>
          <select
            id={`bajada-${linea}`}
            value={destinoSel}
            onChange={(e) => setDestinoSel(e.target.value)}
            className="pegatina mt-2 h-[48px] w-full rounded-xl bg-tarjeta px-3 text-[16px] font-bold"
          >
            <option value="">Elige tu parada de bajada</option>
            {recorrido.map((p, i) => (
              <option key={p.codigo} value={p.codigo}>
                {p.nombre} · {i + 1} {i === 0 ? "parada" : "paradas"}
              </option>
            ))}
          </select>
          {parada && (() => {
            const inc = incidenciasDelTramo(incidencias, red, linea, recorrido, parada.nombre);
            const afecta = inc.enTramo.length > 0;
            return (
              <>
                <div
                  className={`mt-3 rounded-xl border-2 border-[#111] px-3 py-2 ${afecta ? "bg-[#FFD9D6]" : "bg-[#C9F2D6]"}`}
                  role="status"
                >
                  <p className={`text-[15px] font-bold ${afecta ? "text-[#7A0F0A]" : "text-[#0C4A22]"}`}>
                    {afecta
                      ? `Incidencia en tu tramo: puedes tardar ${inc.retraso} min más de lo normal`
                      : "Tu tramo está despejado"}
                  </p>
                  {inc.despues.map((x) => (
                    <p key={x.parada} className="text-[13px] text-tinta-2">
                      Más adelante, en {x.parada}: {x.texto.toLowerCase()}. No te afecta.
                    </p>
                  ))}
                </div>
                <p className="mt-3 text-[16px] text-tinta">
                  Llegas a <span className="font-bold">{parada.nombre}</span>{" "}
                  {a.v ? (
                    <>
                      en{" "}
                      <span className="cifra text-[20px] text-principal">
                        {a.v.desde + parada.minutos + inc.retraso}–{a.v.hasta + parada.minutos + inc.retraso} min
                      </span>
                    </>
                  ) : (
                    `unos ${parada.minutos + inc.retraso} min después de subir`
                  )}
                </p>
                <p className="text-[13px] text-suave">
                  Espera medida + {parada.minutos} min de viaje según {aproximado ? "un horario aproximado" : "el horario oficial"}
                  {afecta ? ` + ${inc.retraso} min de la incidencia` : ""}.
                </p>
                <TramoDibujado recorrido={recorrido} fin={inc.fin} incidencias={inc.enTramo} subida={subida} />
                <button
                  onClick={() => onBajada(avisando ? null : { linea, codigo: parada.codigo, nombre: parada.nombre })}
                  aria-pressed={avisando}
                  className={`boton-pegatina mt-2 flex min-h-[44px] w-full items-center gap-2 rounded-xl px-3 text-left text-[15px] font-bold ${
                    avisando ? "bg-verde text-white" : "bg-tarjeta"
                  }`}
                >
                  <IconoCampana className="h-5 w-5" />
                  {avisando ? `Te avisamos una parada antes de ${parada.nombre}` : "Avisarme una parada antes de bajar"}
                </button>
              </>
            );
          })()}
        </div>
      )}
    </Tarjeta>
  );
}

export default function Parada({
  parada, llegadas, contexto, favorita, nombre, onRenombrar, onFavorita, onVolver, onInfoLinea,
  cargando, error, onReintentar, avisos = [], bajada, onBajada, incidencias = [],
}) {
  const tipoDia = contexto.finde ? "Fin de semana" : "Laborable";
  const propio = nombre && nombre !== parada.nombre;

  // Agrupa las llegadas por línea, en el orden en que llega la primera de cada una
  const porLinea = [];
  [...llegadas]
    .sort((x, y) => x.minutos - y.minutos)
    .forEach((l) => {
      const g = porLinea.find((x) => x.linea === l.linea);
      if (g) g.llegadas.push(l);
      else porLinea.push({ linea: l.linea, llegadas: [l] });
    });

  return (
    <div className="space-y-4">
      <div>
        <Volver texto="Mis paradas" onClick={onVolver} />
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <NombreEditable
              nombre={nombre ?? parada.nombre}
              onCambiar={onRenombrar}
              etiqueta="Cambiar el nombre de esta parada"
              className="titulo text-[28px] leading-tight text-tinta"
            />
            {propio && <p className="mt-1 text-[15px] font-bold text-tinta-2">{parada.nombre}</p>}
            <p className="text-[15px] text-suave">
              {parada.etiqueta ?? `${NOMBRE_RED[parada.red]} · parada ${parada.id.split("-")[1]}`}
            </p>
          </div>
          <button
            onClick={onFavorita}
            aria-pressed={favorita}
            aria-label={favorita ? "Quitar de favoritas" : "Añadir a favoritas"}
            className="boton-pegatina flex h-[48px] w-[48px] shrink-0 items-center justify-center rounded-2xl bg-amarillo text-[#111]"
          >
            <IconoEstrella llena={favorita} />
          </button>
        </div>
        <div className="mt-2 flex flex-wrap gap-1.5">
          {porLinea.map((g) => (
            <Linea key={g.linea} linea={g.linea} red={parada.red} />
          ))}
        </div>
      </div>

      <Minimapa lat={parada.lat} lon={parada.lon} />

      {error ? (
        <Tarjeta className="space-y-3 p-4">
          <p className="text-[16px] text-tinta">No hemos podido cargar los datos. Vuelve a intentarlo.</p>
          <button onClick={onReintentar} className="boton-pegatina min-h-[44px] rounded-xl bg-principal px-5 font-bold text-white">
            Reintentar
          </button>
        </Tarjeta>
      ) : cargando ? (
        <ParadaCargando />
      ) : (
        <>
          {porLinea.map((g, i) => (
            <TarjetaLinea
              key={g.linea}
              linea={g.linea}
              llegadas={g.llegadas}
              red={parada.red}
              primera={i === 0}
              recorrido={parada.recorridos?.[g.linea]}
              avisosLinea={avisos.filter((a) => a.linea === g.linea)}
              bajada={bajada}
              onBajada={onBajada}
              onInfo={() => onInfoLinea(g.linea)}
              incidencias={incidencias}
              subida={parada.nombre}
              aproximado={parada.recorrido_aproximado}
            />
          ))}
          <p className="text-[15px] text-suave">
            {tipoDia}, {horaTexto(contexto.hora)}. Los minutos que dice la app son de demostración; las ventanas, de los datos
            medidos. Más datos en la i de cada línea.
          </p>
        </>
      )}
    </div>
  );
}
