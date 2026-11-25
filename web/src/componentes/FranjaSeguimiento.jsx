// Franja de seguimiento (sección 1.6 del manual): un vehículo que avanza por una línea
// según lo que le falta, encima de la barra inferior.
import { useEffect, useState } from "react";
import { IconoVehiculo, IconoFlechaAbajo } from "./Iconos.jsx";

// Al aparecer, el vehículo sale del principio y avanza hasta su sitio: es el movimiento de la demo.
function usePosicionAnimada(destino) {
  const [pos, setPos] = useState(4);
  useEffect(() => {
    const id = requestAnimationFrame(() => setPos(destino));
    return () => cancelAnimationFrame(id);
  }, [destino]);
  return pos;
}

function Vehiculo({ tipo, pos, llegando }) {
  return (
    <div
      className="absolute top-1/2 z-10 transition-[left] duration-[1600ms] ease-out motion-reduce:transition-none"
      style={{ left: `${pos}%`, transform: "translate(-50%, -50%)" }}
    >
      <div
        className={`flex h-[26px] w-[30px] items-center justify-center rounded-md bg-principal text-white shadow-md vehiculo-rueda ${
          llegando ? "vehiculo-llegando" : ""
        }`}
      >
        <IconoVehiculo tipo={tipo} className="h-[18px] w-[18px]" />
      </div>
    </div>
  );
}

// Línea gris con la parte recorrida en color principal
function Recorrido({ pos, etiqueta, children }) {
  return (
    <div role="img" aria-label={etiqueta} className="relative mx-[9px] h-[26px]">
      <div className="absolute left-0 right-0 top-1/2 h-[3px] -translate-y-1/2 rounded bg-[#D5D3CE]" />
      <div
        className="absolute left-0 top-1/2 h-[3px] -translate-y-1/2 rounded bg-principal transition-[width] duration-[1600ms] ease-out motion-reduce:transition-none"
        style={{ width: `${pos}%` }}
      />
      {children}
    </div>
  );
}

function PuntoFinal() {
  return (
    <div className="absolute right-0 top-1/2 h-[18px] w-[18px] translate-x-1/2 -translate-y-1/2 rounded-full border-[3px] border-white bg-[#202124] outline outline-2 outline-[#202124]" />
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
      className="cursor-pointer border-t border-[#E4E2DD] bg-white px-4 pt-2.5 pb-2"
    >
      <div className="flex items-center justify-between gap-2">
        <button
          onClick={(e) => {
            e.stopPropagation();
            onCambiarModo();
          }}
          className="min-h-[44px] text-left text-[14px] font-bold text-[#202124] min-[385px]:text-[15px]"
        >
          {textoIzquierdo}
          <IconoFlechaAbajo className="ml-1 inline h-4 w-4 align-[-3px]" />
        </button>
        {textoDerecho && (
          <span className="shrink-0 text-[16px] font-bold text-principal">{textoDerecho}</span>
        )}
      </div>

      {seg.modo === "destino" && !seg.destino ? (
        <p className="py-3 text-[14px] text-[#5F6368]">
          Elige a dónde vas para seguir el viaje hasta tu destino.
        </p>
      ) : seg.modo === "parada" ? (
        <>
          <Recorrido pos={pos} etiqueta={etiqueta}>
            <PuntoFinal />
            <Vehiculo tipo={seg.icono} pos={pos} llegando={seg.minutos <= 1} />
          </Recorrido>
          <p className="text-[13px] text-[#5F6368]">{seg.siguienteTexto}</p>
        </>
      ) : (
        <>
          <Recorrido pos={pos} etiqueta={etiqueta}>
            {seg.destino.paradas.map((p) =>
              p.tipo === "fin" ? (
                <PuntoFinal key={p.nombre} />
              ) : (
                <div
                  key={p.nombre}
                  className={`absolute top-1/2 h-[14px] w-[14px] -translate-x-1/2 -translate-y-1/2 rounded-full ${
                    p.tipo === "inicio" ? "bg-principal" : "border-[3px] border-[#202124] bg-white"
                  }`}
                  style={{ left: `${p.pos}%` }}
                />
              ),
            )}
            <Vehiculo tipo={seg.destino.icono} pos={pos} />
          </Recorrido>
          {/* Nombres de las paradas debajo, en 12 px */}
          <div className="relative mx-[9px] h-[16px] text-[12px] text-[#5F6368]">
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
          <p className="text-[13px] text-[#5F6368]">{seg.destino.siguienteTexto}</p>
        </>
      )}
    </div>
  );
}
