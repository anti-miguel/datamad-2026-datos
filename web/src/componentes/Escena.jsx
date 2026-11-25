// Escena de cabecera: el autobús (o el tren) entra, para en la parada
// y, según bajas por la página, sigue su recorrido hacia la derecha.
import { useEffect, useRef, useState } from "react";
import { DibujoBusEMT, DibujoBusInterurbano, DibujoTren, DibujoMetro, DibujoBici } from "./Vehiculos.jsx";

const PARADA = 0.5; // donde se detiene, en fracción del ancho (posición del morro)

function useRecorrido() {
  const [entrado, setEntrado] = useState(false);
  const [avance, setAvance] = useState(0); // 0 = en la parada, 1 = fuera por la derecha
  const [moviendo, setMoviendo] = useState(true);
  const temporizador = useRef(null);

  useEffect(() => {
    const reducido = matchMedia("(prefers-reduced-motion: reduce)").matches;
    const id = setTimeout(() => setEntrado(true), reducido ? 0 : 120);
    const parar = setTimeout(() => setMoviendo(false), reducido ? 0 : 2200);

    function alDesplazar() {
      // Los primeros 320 px de scroll bastan para que salga de la escena
      setAvance(Math.min(1, window.scrollY / 320));
      setMoviendo(true);
      clearTimeout(temporizador.current);
      temporizador.current = setTimeout(() => setMoviendo(false), 260);
    }
    addEventListener("scroll", alDesplazar, { passive: true });
    return () => {
      clearTimeout(id);
      clearTimeout(parar);
      clearTimeout(temporizador.current);
      removeEventListener("scroll", alDesplazar);
    };
  }, []);

  return { entrado, avance, moviendo };
}

function Ciudad() {
  // Bloques de edificios genéricos al fondo
  const bloques = [
    [0, 38, 46], [44, 22, 34], [76, 46, 40], [118, 30, 30], [150, 52, 44],
    [196, 26, 36], [230, 42, 48], [280, 34, 32], [316, 50, 42], [360, 30, 40],
  ];
  return (
    <g>
      {bloques.map(([x, alto, ancho]) => (
        <g key={x}>
          <rect x={x} y={86 - alto} width={ancho} height={alto} fill="#FFFDF6" stroke="#111" strokeWidth="1.5" />
          {Array.from({ length: Math.floor(alto / 12) }, (_, fila) =>
            Array.from({ length: Math.floor(ancho / 11) }, (_, col) => (
              <rect key={`${fila}-${col}`} x={x + 5 + col * 11} y={86 - alto + 6 + fila * 12} width="4" height="5" fill={(x + fila * 7 + col * 3) % 5 === 0 ? "#FFE15A" : "#B4C3FF"} />
            )),
          )}
        </g>
      ))}
    </g>
  );
}

function Marquesina({ x, color = "#1F5FD1" }) {
  return (
    <g>
      <rect x={x} y="56" width="34" height="3" rx="1" fill="#8E9BB0" />
      <rect x={x + 2} y="59" width="1.6" height="27" fill="#8E9BB0" />
      <rect x={x + 30} y="59" width="1.6" height="27" fill="#8E9BB0" />
      <rect x={x + 4} y="60" width="25" height="18" fill="#B4C3FF" opacity="0.6" />
      {/* poste con el cartel de parada */}
      <rect x={x + 40} y="48" width="2" height="38" fill="#8E9BB0" />
      <rect x={x + 35} y="44" width="12" height="12" rx="3" fill={color} />
      <path d={`M${x + 38} ${47}h6v5h-6z`} fill="#fff" />
    </g>
  );
}

// Bus urbano (azul) o interurbano (verde) parando en la marquesina
export function EscenaBus({ interurbano = false }) {
  const { entrado, avance, moviendo } = useRecorrido();
  // El morro va de fuera (izquierda) a la parada, y con el scroll sale por la derecha
  const morro = !entrado ? -0.05 : PARADA + avance * 0.75;
  return (
    <div className="relative -mx-4 h-[122px] overflow-hidden border-b-[2.5px] border-[#111]" aria-hidden="true">
      <svg viewBox="0 0 390 122" preserveAspectRatio="xMidYMax slice" className="absolute inset-0 h-full w-full">
        <Ciudad />
        <rect x="0" y="86" width="390" height="8" fill="#FFFDF6" stroke="#111" strokeWidth="1.5" />
        <rect x="0" y="94" width="390" height="28" fill="#2B2B33" />
        <line x1="0" y1="108" x2="390" y2="108" stroke="#F6F5F2" strokeWidth="2" strokeDasharray="14 12" />
        <Marquesina x={205} color={interurbano ? "#4FA324" : "#1F5FD1"} />
      </svg>
      {/* estación de bicis de alquiler en la acera, con su tótem */}
      <div className="absolute bottom-[30px] left-[72%] flex items-end gap-[2px]">
        <div className="mb-[2px] mr-1 h-[30px] w-[7px] rounded-t-[3px] bg-[#1D63B8]">
          <div className="mx-auto mt-[4px] h-[6px] w-[4px] rounded-[1px] bg-[#CFE0F7]" />
        </div>
        <DibujoBici className="w-[38px]" />
        <DibujoBici className="w-[38px]" />
      </div>
      <div
        className={`absolute bottom-[19px] w-[150px] transition-[left] ease-out motion-reduce:transition-none ${moviendo ? "" : "parado"}`}
        style={{ left: `calc(${morro * 100}% - 150px)`, transitionDuration: entrado && avance === 0 ? "2000ms" : "250ms" }}
      >
        {interurbano ? <DibujoBusInterurbano className="w-full vaiven" /> : <DibujoBusEMT className="w-full vaiven" />}
      </div>
    </div>
  );
}

export function EscenaTren() {
  const { entrado, avance, moviendo } = useRecorrido();
  const morro = !entrado ? -0.05 : 0.86 + avance * 0.5;
  return (
    <div className="relative -mx-4 h-[110px] overflow-hidden border-b-[2.5px] border-[#111]" aria-hidden="true">
      <svg viewBox="0 0 390 110" preserveAspectRatio="xMidYMax slice" className="absolute inset-0 h-full w-full">
        {/* postes de la catenaria */}
        {[30, 150, 270].map((x) => (
          <g key={x}>
            <rect x={x} y="20" width="2.5" height="66" fill="#9AA0A6" />
            <rect x={x - 6} y="20" width="22" height="2" fill="#9AA0A6" />
          </g>
        ))}
        <line x1="0" y1="26" x2="390" y2="26" stroke="#9AA0A6" strokeWidth="1" />
        {/* andén con su cartel */}
        <rect x="250" y="76" width="140" height="12" fill="#FFFDF6" stroke="#111" strokeWidth="1.5" />
        <rect x="250" y="76" width="140" height="2.5" fill="#F2C94C" />
        <rect x="330" y="40" width="2" height="36" fill="#5F6368" />
        <rect x="306" y="34" width="50" height="12" rx="2" fill="#05080D" stroke="#3A4252" />
        <rect x="310" y="38" width="42" height="4" rx="1" fill="#FFB300" />
        {/* balasto, traviesas y raíles */}
        <rect x="0" y="88" width="390" height="22" fill="#8A8378" />
        {Array.from({ length: 33 }, (_, i) => (
          <rect key={i} x={i * 12 + 2} y="92" width="6" height="12" rx="1" fill="#5A5048" />
        ))}
        <rect x="0" y="94" width="390" height="2" fill="#A7ADB5" />
        <rect x="0" y="101" width="390" height="2" fill="#A7ADB5" />
      </svg>
      <div
        className={`absolute bottom-[11px] w-[250px] transition-[left] ease-out motion-reduce:transition-none ${moviendo ? "" : "parado"}`}
        style={{ left: `calc(${morro * 100}% - 250px)`, transitionDuration: entrado && avance === 0 ? "2400ms" : "250ms" }}
      >
        <DibujoTren className="w-full" />
      </div>
    </div>
  );
}

// Metro: estación subterránea con pared de azulejo amarillo, techo oscuro y borde de andén
export function EscenaMetro() {
  const { entrado, avance, moviendo } = useRecorrido();
  const morro = !entrado ? -0.05 : 0.9 + avance * 0.5;
  return (
    <div className="relative -mx-4 h-[118px] overflow-hidden border-b-[2.5px] border-[#111] bg-[#2B2F35]" aria-hidden="true">
      <svg viewBox="0 0 390 118" preserveAspectRatio="xMidYMax slice" className="absolute inset-0 h-full w-full">
        {/* bóveda oscura con las luces */}
        <rect x="0" y="0" width="390" height="30" fill="#33373D" />
        {[20, 110, 200, 290].map((x) => (
          <rect key={x} x={x} y="10" width="60" height="3" rx="1.5" fill="#FFF7DC" opacity="0.9" />
        ))}
        {/* pared de azulejo amarillo con su franja */}
        <rect x="0" y="30" width="390" height="56" fill="#F2C230" />
        {Array.from({ length: 20 }, (_, i) => (
          <line key={i} x1={i * 20} y1="30" x2={i * 20} y2="86" stroke="#E0B024" strokeWidth="0.8" />
        ))}
        <rect x="0" y="40" width="390" height="9" fill="#1D5FB8" />
        <rect x="150" y="42" width="90" height="5" rx="1" fill="#F6F5F2" />
        {/* andén con la línea de seguridad amarilla */}
        <rect x="0" y="86" width="390" height="12" fill="#D9D4CA" />
        <rect x="0" y="95" width="390" height="3" fill="#F2C94C" />
        {/* foso y vía */}
        <rect x="0" y="98" width="390" height="20" fill="#2B2F35" />
        <rect x="0" y="108" width="390" height="2" fill="#6B7178" />
      </svg>
      <div
        className={`absolute bottom-[6px] w-[180px] transition-[left] ease-out motion-reduce:transition-none ${moviendo ? "" : "parado"}`}
        style={{ left: `calc(${morro * 100}% - 180px)`, transitionDuration: entrado && avance === 0 ? "2200ms" : "250ms" }}
      >
        <DibujoMetro className="w-full" />
      </div>
    </div>
  );
}

// Escena de la portada según el filtro elegido
export function EscenaSegunModo({ modo }) {
  if (modo === "renfe") return <EscenaTren />;
  if (modo === "metro") return <EscenaMetro />;
  return <EscenaBus interurbano={modo === "interurbano"} />;
}
