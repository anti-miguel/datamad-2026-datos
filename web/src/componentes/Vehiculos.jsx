// Dibujos propios de los vehículos de Madrid, vistos de lado y mirando a la derecha.
// Siguen la forma y los colores de los modelos reales (Civia de Cercanías, bus eléctrico
// de la EMT, autocar interurbano, metro y BiciMAD), pero sin logotipos ni rótulos de operador.
// Las ruedas giran con la clase «rueda»; con «parado» en el padre se detienen.

function Rueda({ cx, cy, r = 5, llanta = "#C4C8CD" }) {
  return (
    <g className="rueda" style={{ transformOrigin: `${cx}px ${cy}px` }}>
      <circle cx={cx} cy={cy} r={r} fill="#1B1D20" />
      <circle cx={cx} cy={cy} r={r * 0.55} fill={llanta} />
      <circle cx={cx} cy={cy} r={r * 0.18} fill="#5F6368" />
      {[0, 72, 144, 216, 288].map((a) => (
        <line
          key={a}
          x1={cx}
          y1={cy}
          x2={cx + Math.cos((a * Math.PI) / 180) * r * 0.5}
          y2={cy + Math.sin((a * Math.PI) / 180) * r * 0.5}
          stroke="#7A7F86"
          strokeWidth="0.6"
        />
      ))}
    </g>
  );
}

// Paso de rueda: hueco oscuro en la carrocería
function Paso({ cx, cy, r }) {
  return <path d={`M${cx - r - 1.6} ${cy + 1}a${r + 1.6} ${r + 1.6} 0 0 1 ${2 * r + 3.2} 0z`} fill="#2A2D31" />;
}

// Puerta doble de cristal, con su marco y la junta central
function PuertaDoble({ x, y, ancho = 8, alto, marco = "#D9DDE2" }) {
  return (
    <g>
      <rect x={x} y={y} width={ancho} height={alto} rx="0.8" fill="#26303B" stroke={marco} strokeWidth="0.9" />
      <line x1={x + ancho / 2} y1={y} x2={x + ancho / 2} y2={y + alto} stroke={marco} strokeWidth="0.7" />
      <rect x={x + 1} y={y + alto * 0.55} width={ancho / 2 - 1.6} height="0.7" fill={marco} opacity="0.7" />
      <rect x={x + ancho / 2 + 0.6} y={y + alto * 0.55} width={ancho / 2 - 1.6} height="0.7" fill={marco} opacity="0.7" />
    </g>
  );
}

// Autobús urbano eléctrico de la EMT: azul, techo con carenado de baterías,
// cristalera corrida, tres puertas dobles y frontal casi vertical con gran parabrisas.
export function DibujoBusEMT({ className = "" }) {
  return (
    <svg viewBox="0 0 120 42" className={className} aria-hidden="true">
      <ellipse cx="60" cy="40.6" rx="56" ry="1.4" fill="#000" opacity="0.18" />
      {/* carenado del techo (baterías y climatización) */}
      <path d="M22 5.5c0-1.4 1.1-2.5 2.5-2.5h78c3 0 5.2 1.2 6.5 3.2L110 7H22z" fill="#E4E7EB" />
      <rect x="40" y="2.2" width="22" height="1.2" rx="0.6" fill="#C9CDD2" />
      {/* carrocería */}
      <path d="M3 9a3 3 0 0 1 3-3h101c3.4 0 6 1.6 7.4 4.6L117 17v16.5a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" fill="#1D63B8" />
      {/* faldón inferior más oscuro */}
      <rect x="3" y="30" width="114" height="5.5" rx="1.5" fill="#164E93" />
      {/* cristalera corrida con montantes */}
      <path d="M6 9h99.5c2.3 0 4 1 5 3l3.2 7.5H6z" fill="#1E2833" />
      {[24, 46, 78].map((x) => (
        <rect key={x} x={x} y="9" width="1.4" height="10.5" fill="#1D63B8" />
      ))}
      {/* reflejo del cristal */}
      <path d="M10 10l8 0-6 8.5h-4z" fill="#fff" opacity="0.12" />
      {/* letrero de línea y destino, ámbar, arriba en el frontal */}
      <rect x="99" y="9.8" width="12" height="2.6" rx="0.6" fill="#FFB300" />
      {/* puertas: trasera, central y delantera */}
      <PuertaDoble x={13} y={10} alto={24} />
      <PuertaDoble x={58} y={10} ancho={9} alto={24} />
      <PuertaDoble x={100} y={13} alto={21} />
      {/* faros, piloto trasero y retrovisor */}
      <rect x="114" y="27" width="3" height="2.2" rx="0.8" fill="#FFF3C4" />
      <rect x="3" y="24" width="1.6" height="4" rx="0.6" fill="#D93025" />
      <path d="M115 10.5c2.4-.4 3.6.6 3.6 2.4v2" stroke="#1B1D20" strokeWidth="0.9" fill="none" />
      <Paso cx={34} cy={36} r={5.2} />
      <Paso cx={88} cy={36} r={5.2} />
      <Rueda cx={34} cy={36} r={5.2} />
      <Rueda cx={88} cy={36} r={5.2} />
    </svg>
  );
}

// Autobús interurbano: verde claro, tipo autocar (suelo alto, ventanas separadas,
// dos puertas y maleteros entre ejes).
export function DibujoBusInterurbano({ className = "" }) {
  return (
    <svg viewBox="0 0 120 44" className={className} aria-hidden="true">
      <ellipse cx="60" cy="42.6" rx="56" ry="1.4" fill="#000" opacity="0.18" />
      <path d="M3 7a3 3 0 0 1 3-3h102c3.6 0 6.2 2 7.4 5.4L117 15v20.5a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" fill="#7DBA3C" />
      {/* franja blanca bajo las ventanas */}
      <rect x="3" y="21" width="114" height="2.4" fill="#FFFFFF" opacity="0.9" />
      {/* ventanas separadas */}
      {[7, 21, 35, 49, 72, 86].map((x) => (
        <rect key={x} x={x} y="7.5" width="12" height="11.5" rx="1.4" fill="#1E2833" />
      ))}
      <path d="M100 7.5h7c2.2 0 3.8 1.2 4.6 3.4l2.4 8.1H100z" fill="#1E2833" />
      <rect x="101" y="5" width="11" height="1.8" rx="0.5" fill="#FFB300" />
      {/* puertas delantera y central */}
      <PuertaDoble x={101.5} y={10} ancho={7} alto={26} marco="#EAF4DF" />
      <PuertaDoble x={62} y={8} ancho={8} alto={28} marco="#EAF4DF" />
      {/* tapas de maletero */}
      {[38, 48].map((x) => (
        <rect key={x} x={x} y="26" width="9" height="8" rx="0.8" fill="none" stroke="#5E9A26" strokeWidth="0.8" />
      ))}
      <rect x="114" y="29" width="3" height="2.2" rx="0.8" fill="#FFF3C4" />
      <rect x="3" y="26" width="1.6" height="4" rx="0.6" fill="#D93025" />
      <path d="M115 9c2.4-.4 3.6.6 3.6 2.4v2" stroke="#1B1D20" strokeWidth="0.9" fill="none" />
      <Paso cx={25} cy={38} r={5.4} />
      <Paso cx={88} cy={38} r={5.4} />
      <Rueda cx={25} cy={38} r={5.4} />
      <Rueda cx={88} cy={38} r={5.4} />
    </svg>
  );
}

// Tren de Cercanías tipo Civia: blanco, franja roja baja, cristales oscuros corridos,
// frontal redondeado con máscara negra y puertas dobles de piso bajo. Se ven dos coches.
export function DibujoTren({ className = "" }) {
  return (
    <svg viewBox="0 0 200 42" className={className} aria-hidden="true">
      <ellipse cx="100" cy="40.6" rx="96" ry="1.4" fill="#000" opacity="0.18" />
      {/* pantógrafo sobre el coche trasero */}
      <path d="M40 6l7-5h12M47 1l7 5" stroke="#5F6368" strokeWidth="1.1" fill="none" />
      <rect x="38" y="5" width="20" height="1.6" rx="0.5" fill="#9AA0A6" />
      {/* coche trasero */}
      <rect x="2" y="6" width="93" height="28" rx="3" fill="#F7F7F5" stroke="#CDD1D5" strokeWidth="0.8" />
      {/* coche delantero con morro redondeado */}
      <path d="M97 6h80c8 0 14.5 5.5 17 13l2.6 8v5a2 2 0 0 1-2 2H97z" fill="#F7F7F5" stroke="#CDD1D5" strokeWidth="0.8" />
      {/* techo gris con equipos de climatización */}
      <rect x="2" y="6" width="93" height="2.4" rx="1.2" fill="#C9CDD2" />
      <path d="M97 6h80c3 0 5.6.8 7.6 2.4H97z" fill="#C9CDD2" />
      <rect x="14" y="4.4" width="14" height="1.8" rx="0.6" fill="#B5BAC0" />
      <rect x="122" y="4.4" width="14" height="1.8" rx="0.6" fill="#B5BAC0" />
      {/* cristales oscuros corridos */}
      <rect x="5" y="11" width="87" height="9" rx="1.5" fill="#1E2833" />
      <rect x="100" y="11" width="74" height="9" rx="1.5" fill="#1E2833" />
      {/* máscara negra del frontal con el parabrisas */}
      <path d="M176 9.5c6 .6 11 4.6 13.4 10.5l2.8 8.5H176z" fill="#15191E" />
      <path d="M179 12c4.4 1 7.6 4 9.2 8h-9.2z" fill="#3A4654" />
      {/* franja roja baja, que sube en el morro */}
      <rect x="2" y="27" width="93" height="3.4" fill="#D7192D" />
      <path d="M97 27h96.5l1 3.4H97z" fill="#D7192D" />
      {/* puertas dobles de piso bajo */}
      {[16, 66, 112, 156].map((x) => (
        <g key={x}>
          <rect x={x} y="9.5" width="11" height="24.5" rx="1" fill="#E6E8EB" stroke="#9AA0A6" strokeWidth="0.7" />
          <line x1={x + 5.5} y1="9.5" x2={x + 5.5} y2="34" stroke="#9AA0A6" strokeWidth="0.6" />
          <rect x={x + 1.4} y="11.5" width="3.3" height="10" rx="0.8" fill="#1E2833" />
          <rect x={x + 6.3} y="11.5" width="3.3" height="10" rx="0.8" fill="#1E2833" />
          <rect x={x} y="27" width="11" height="3.4" fill="#D7192D" />
        </g>
      ))}
      {/* faro y fuelle entre coches */}
      <rect x="190" y="30" width="4" height="2" rx="0.8" fill="#FFF3C4" />
      <rect x="95" y="10" width="2" height="22" fill="#6B7178" />
      {/* bogies */}
      {[14, 32, 70, 88, 108, 126, 164, 182].map((x) => (
        <Rueda key={x} cx={x} cy={36.5} r={3.6} />
      ))}
      <rect x="10" y="34.5" width="26" height="2" rx="1" fill="#3C4043" />
      <rect x="66" y="34.5" width="26" height="2" rx="1" fill="#3C4043" />
      <rect x="104" y="34.5" width="26" height="2" rx="1" fill="#3C4043" />
      <rect x="160" y="34.5" width="26" height="2" rx="1" fill="#3C4043" />
    </svg>
  );
}

// Metro: coche blanco con franja azul, cristales oscuros y frontal recto
export function DibujoMetro({ className = "" }) {
  return (
    <svg viewBox="0 0 110 40" className={className} aria-hidden="true">
      <ellipse cx="55" cy="38.6" rx="52" ry="1.4" fill="#000" opacity="0.18" />
      <path d="M3 8a3 3 0 0 1 3-3h93c4.5 0 7.5 3 8.5 7.5L108 31a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" fill="#F4F5F7" stroke="#C9CDD2" strokeWidth="0.8" />
      <rect x="6" y="10" width="86" height="9" rx="1.5" fill="#1E2833" />
      <path d="M96 9.5h3.5c3 0 5 2 5.8 5l.8 4.5H96z" fill="#15191E" />
      <rect x="3" y="23" width="105" height="3" fill="#1D63B8" />
      <rect x="3" y="26" width="105" height="1.2" fill="#D93025" />
      {[18, 48, 78].map((x) => (
        <PuertaDoble key={x} x={x} y={8.5} ancho={10} alto={23.5} marco="#9AA0A6" />
      ))}
      <rect x="103" y="28" width="3.5" height="2" rx="0.8" fill="#FFF3C4" />
      {[14, 26, 82, 94].map((x) => (
        <Rueda key={x} cx={x} cy={34.5} r={3.4} />
      ))}
    </svg>
  );
}

// Bicicleta eléctrica de alquiler tipo BiciMAD: cuadro bajo blanco, detalles azules,
// cesta delantera y batería en el tubo.
export function DibujoBici({ className = "" }) {
  return (
    <svg viewBox="0 0 48 30" className={className} aria-hidden="true">
      <ellipse cx="24" cy="29" rx="21" ry="0.9" fill="#000" opacity="0.16" />
      <g fill="none" strokeLinecap="round" strokeLinejoin="round">
        {/* ruedas */}
        <circle cx="10" cy="21" r="7" stroke="#1B1D20" strokeWidth="2" />
        <circle cx="38" cy="21" r="7" stroke="#1B1D20" strokeWidth="2" />
        {/* cuadro bajo */}
        <path d="M10 21l7-1 9-9 5 0M17 20l3-11M26 11l12 10" stroke="#F2F3F5" strokeWidth="3" />
        <path d="M10 21l7-1 9-9 5 0M17 20l3-11M26 11l12 10" stroke="#C9CDD2" strokeWidth="0.6" />
        {/* guardabarros azules */}
        <path d="M3.5 18a7 7 0 0 1 11-4.5M31.5 17.5a7 7 0 0 1 12 0" stroke="#1D63B8" strokeWidth="1.6" />
        {/* manillar y sillín */}
        <path d="M31 11l2-5h4" stroke="#1B1D20" strokeWidth="1.6" />
        <path d="M17 8.5h6" stroke="#1B1D20" strokeWidth="2.2" />
      </g>
      {/* batería y cesta */}
      <rect x="20.5" y="13" width="5" height="3" rx="1" transform="rotate(-45 23 14.5)" fill="#1D63B8" />
      <rect x="35" y="7.5" width="9" height="5" rx="1" fill="none" stroke="#5F6368" strokeWidth="1.1" />
    </svg>
  );
}

// Elige el dibujo según la red de la parada
export function DibujoVehiculo({ tipo, red, className }) {
  if (tipo === "tren") return <DibujoTren className={className} />;
  if (tipo === "metro") return <DibujoMetro className={className} />;
  if (red === "interurbano") return <DibujoBusInterurbano className={className} />;
  return <DibujoBusEMT className={className} />;
}
