// Pantalla 2: Parada. Responde «¿me fío de lo que dice la app?». Es la pantalla más importante.
// Aquí NO van porcentajes, barras de rango ni número de llegadas: están en la 2b.
import { useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { Linea, Etiqueta, Tarjeta, Volver } from "../componentes/Comunes.jsx";
import { IconoEstrella, IconoInfo } from "../componentes/Iconos.jsx";
import { NOMBRE_RED, horaTexto } from "../lib/util.js";

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
      color: "#FFFFFF",
      weight: 3,
      fillColor: "#1F5FD1",
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
  return (
    <div
      ref={caja}
      className="h-[160px] overflow-hidden rounded-2xl border border-[#E4E2DD]"
      role="img"
      aria-label="Mapa de la parada"
    />
  );
}

// Tarjetas grises vacías mientras carga fiabilidad.json
export function ParadaCargando() {
  return (
    <div className="space-y-3 animate-pulse" aria-label="Cargando">
      <div className="h-[160px] rounded-2xl bg-[#E4E2DD]" />
      <div className="h-[200px] rounded-2xl bg-[#E4E2DD]" />
      <div className="h-[64px] rounded-2xl bg-[#E4E2DD]" />
    </div>
  );
}

function TarjetaPrimera({ llegada, red, onInfo }) {
  const { linea, destino, minutos, lejos, r, v } = llegada;
  return (
    <Tarjeta sombra className="p-4">
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <Linea linea={linea} red={red} grande />
          <span className="text-[18px] text-[#202124]">{destino}</span>
        </div>
        <button
          onClick={onInfo}
          aria-label={`Qué conviene saber del ${linea}`}
          className="flex h-[44px] w-[44px] shrink-0 items-center justify-center rounded-full bg-[#E8F0FE] text-principal"
        >
          <IconoInfo />
        </button>
      </div>

      <p className="mt-3 text-[15px] text-[#5F6368]">La app oficial dice {minutos} min</p>

      <p className="mt-1 text-[32px] font-extrabold leading-tight text-[#202124]">
        {lejos ? "Demasiado lejos para estimar" : v ? `Llega entre ${v.desde} y ${v.hasta} min` : "Sin datos suficientes"}
      </p>

      {v && (
        <>
          <div className="mt-3 flex flex-wrap items-center gap-x-3 gap-y-2">
            <Etiqueta p={r.p} relleno />
            <span className="text-[16px] text-[#202124]">Si a los {v.hasta} min no ha llegado, algo pasa.</span>
          </div>
          {r.nivel !== "linea" && (
            <p className="mt-2 text-[14px] text-[#5F6368]">Estimación general de la red</p>
          )}
        </>
      )}
    </Tarjeta>
  );
}

function FilaSiguiente({ llegada, red }) {
  const { linea, lejos, r, v } = llegada;
  return (
    <Tarjeta className="flex min-h-[56px] items-center gap-3 px-4 py-3">
      <Linea linea={linea} red={red} />
      <span className="flex-1 text-[17px] font-bold text-[#202124]">
        {lejos ? "Demasiado lejos para estimar" : v ? `Entre ${v.desde} y ${v.hasta} min` : "Sin datos suficientes"}
      </span>
      {v && <Etiqueta p={r.p} />}
    </Tarjeta>
  );
}

export default function Parada({ parada, llegadas, contexto, favorita, onFavorita, onVolver, onInfoLinea, cargando, error, onReintentar }) {
  const [primera, ...resto] = llegadas;
  const tipoDia = contexto.finde ? "Fin de semana" : "Laborable";

  return (
    <div className="space-y-4">
      <div>
        <Volver texto="Mis paradas" onClick={onVolver} />
        <div className="flex items-start justify-between gap-3">
          <div>
            <h1 className="text-[30px] font-bold leading-tight text-[#202124]">{parada.nombre}</h1>
            <p className="text-[16px] text-[#5F6368]">
              {NOMBRE_RED[parada.red]} · parada {parada.id.split("-")[1]}
            </p>
          </div>
          <button
            onClick={onFavorita}
            aria-pressed={favorita}
            aria-label={favorita ? "Quitar de favoritas" : "Añadir a favoritas"}
            className="flex h-[48px] w-[48px] shrink-0 items-center justify-center rounded-2xl border border-[#E4E2DD] bg-white text-principal"
          >
            <IconoEstrella llena={favorita} />
          </button>
        </div>
      </div>

      <Minimapa lat={parada.lat} lon={parada.lon} />

      {error ? (
        <Tarjeta className="space-y-3 p-4">
          <p className="text-[16px] text-[#202124]">No hemos podido cargar los datos. Vuelve a intentarlo.</p>
          <button onClick={onReintentar} className="min-h-[44px] rounded-xl bg-principal px-5 font-bold text-white">
            Reintentar
          </button>
        </Tarjeta>
      ) : cargando ? (
        <ParadaCargando />
      ) : (
        <>
          {primera && <TarjetaPrimera llegada={primera} red={parada.red} onInfo={() => onInfoLinea(primera.linea)} />}
          {resto.map((l, i) => (
            <FilaSiguiente key={`${l.linea}-${i}`} llegada={l} red={parada.red} />
          ))}
          <p className="text-[15px] text-[#5F6368]">
            {tipoDia}, {horaTexto(contexto.hora)}. Más datos en la i de cada línea.
          </p>
        </>
      )}
    </div>
  );
}
