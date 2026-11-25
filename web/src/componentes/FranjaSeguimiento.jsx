// Franja de seguimiento (sección 1.6 del manual): el vehículo dibujado avanza
// por su carretera o su vía según lo que le falta, encima de la barra inferior.
import { useEffect, useState } from "react";
import { IconoFlechaAbajo } from "./Iconos.jsx";
import { DibujoVehiculo } from "./Vehiculos.jsx";

// Al aparecer, el vehículo sale del principio y avanza hasta su sitio
function usePosicionAnimada(destino) {
  const [pos, setPos] = useState(4);
  useEffect(() => {
    const id = requestAnimationFrame(() => setPos(destino));
    return () => cancelAnimationFrame(id);
  }, [destino]);
  return pos;
}

// El vehículo con el morro en la posición que toca. Las ruedas giran mientras avanza.
function Vehiculo({ tipo, red, pos, llegando }) {
  const [moviendo, setMoviendo] = useState(true);
  useEffect(() => {
    setMoviendo(true);
    const id = setTimeout(() => setMoviendo(false), 1700);
    return () => clearTimeout(id);
  }, [pos]);
  const ancho = tipo === "tren" ? 104 : tipo === "metro" ? 64 : 62;
  return (
    <div
      className={`absolute bottom-[6px] z-10 transition-[left] duration-[1600ms] ease-out motion-reduce:transition-none ${
        moviendo ? "" : "parado"
      } ${llegando ? "vehiculo-llegando" : ""}`}
      style={{ left: `calc(${pos}% - ${ancho - 6}px)`, width: ancho }}
    >
      <DibujoVehiculo tipo={tipo} red={red} className={`block w-full ${tipo === "tren" ? "" : "vaiven"}`} />
    </div>
  );
}

// Carretera (bus) o vía (tren y metro); la parte ya recorrida se marca en color principal
function Recorrido({ pos, etiqueta, tipo, children }) {
  const via = tipo === "tren" || tipo === "metro";
  return (
    <div role="img" aria-label={etiqueta} className="relative mx-[9px] h-[42px]">
      <div className={`${via ? "via" : "carretera"} absolute inset-x-0 bottom-0 h-[10px] rounded-sm`} />
      <div
        className="absolute bottom-[3.5px] left-0 h-[3px] rounded bg-principal transition-[width] duration-[1600ms] ease-out motion-reduce:transition-none"
        style={{ width: `${pos}%` }}
      />
      {children}
    </div>
  );
}

// Tu parada o tu destino: un poste con su cartel al final del recorrido
function PuntoFinal() {
  return (
    <div className="absolute bottom-[8px] right-0 flex translate-x-1/2 flex-col items-center">
      <div className="h-[16px] w-[16px] rounded-full border-[3px] border-fondo bg-tinta outline outline-2 outline-tinta" />
      <div className="h-[16px] w-[2px] bg-tinta" />
    </div>
  );
}

export default function FranjaSeguimiento({ seg, onAbrir, onCambiarModo }) {
  const destinoPos = seg.modo === "parada" ? seg.posicion : seg.destino ? seg.destino.posicion : 4;
  const pos = usePosicionAnimada(destinoPos);

  const textoIzquierdo =
    seg.modo === "parada"
      ? `Siguiendo el ${seg.linea} · hasta tu parada`
      : `Siguiendo el ${seg.destino ? seg.destino.linea : seg.linea} · hasta tu destino`;

  let textoDerecho = null;
  if (seg.modo === "parada") {
    if (seg.minutos <= 1) textoDerecho = "Llegando";
    else if (seg.v) textoDerecho = `${seg.v.desde}–${seg.v.hasta} min`;
    // PENDIENTE: el manual no dice qué poner a la derecha si no hay ventana; se deja vacío
  } else if (seg.destino) {
    textoDerecho = `Llegas ${seg.destino.llegada}`;
  }

  const etiqueta =
    seg.modo === "parada"
      ? `El ${seg.linea} está a ${seg.minutos} ${seg.minutos === 1 ? "minuto" : "minutos"} de tu parada`
      : seg.destino
        ? `El ${seg.destino.linea} va de camino a tu destino; llegas a las ${seg.destino.llegada}`
        : "";

  return (
    <div
      role="button"
      tabIndex={0}
      onClick={onAbrir}
      onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && onAbrir()}
      className="cursor-pointer border-t-[2.5px] border-[#111] bg-amarillo px-4 pt-1.5 pb-2"
    >
      <div className="flex items-center justify-between gap-2">
        <button
          onClick={(e) => {
            e.stopPropagation();
            onCambiarModo();
          }}
          className="min-h-[44px] text-left text-[14px] font-bold text-tinta min-[385px]:text-[15px]"
        >
          {textoIzquierdo}
          <IconoFlechaAbajo className="ml-1 inline h-4 w-4 align-[-3px]" />
        </button>
        {textoDerecho && (
          <span className="cifra shrink-0 text-[19px] tabular-nums text-principal">{textoDerecho}</span>
        )}
      </div>

      {seg.modo === "destino" && !seg.destino ? (
        <p className="py-3 text-[14px] text-suave">Elige a dónde vas para seguir el viaje hasta tu destino.</p>
      ) : seg.modo === "parada" ? (
        <>
          <Recorrido pos={pos} etiqueta={etiqueta} tipo={seg.icono}>
            <PuntoFinal />
            <Vehiculo tipo={seg.icono} red={seg.red} pos={pos} llegando={seg.minutos <= 1} />
          </Recorrido>
          <p className="mt-1 text-[13px] text-suave">{seg.siguienteTexto}</p>
        </>
      ) : (
        <>
          <Recorrido pos={pos} etiqueta={etiqueta} tipo={seg.destino.icono}>
            {seg.destino.paradas.map((p) =>
              p.tipo === "fin" ? (
                <PuntoFinal key={p.nombre} />
              ) : (
                <div
                  key={p.nombre}
                  className={`absolute bottom-[-1px] h-[12px] w-[12px] -translate-x-1/2 rounded-full ${
                    p.tipo === "inicio" ? "bg-principal" : "border-[3px] border-tinta bg-fondo"
                  }`}
                  style={{ left: `${p.pos}%` }}
                />
              ),
            )}
            <Vehiculo tipo={seg.destino.icono} pos={pos} />
          </Recorrido>
          {/* Nombres de las paradas debajo, en 12 px */}
          <div className="relative mx-[9px] mt-0.5 h-[16px] text-[12px] text-suave">
            {seg.destino.paradas.map((p) => (
              <span
                key={p.nombre}
                className="absolute whitespace-nowrap"
                style={
                  p.tipo === "inicio"
                    ? { left: "-9px" }
                    : p.tipo === "fin"
                      ? { right: "-9px" }
                      : { left: `${p.pos}%`, transform: "translateX(-50%)" }
                }
              >
                {p.nombre}
              </span>
            ))}
          </div>
          <p className="text-[13px] text-suave">{seg.destino.siguienteTexto}</p>
        </>
      )}
    </div>
  );
}
