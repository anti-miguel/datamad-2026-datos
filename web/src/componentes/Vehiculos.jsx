// Dibujos propios de los vehículos, vistos de lado y mirando a la derecha.
// No copian ningún diseño de operador (manual, sección 1.2): son genéricos.
// Las ruedas giran con la clase «rueda»; con «parado» en el padre se detienen.

function Rueda({ cx, cy, r = 5 }) {
  return (
    <g className="rueda" style={{ transformOrigin: `${cx}px ${cy}px` }}>
      <circle cx={cx} cy={cy} r={r} fill="#202124" />
      <circle cx={cx} cy={cy} r={r * 0.45} fill="#BFC3C8" />
      <path d={`M${cx - r * 0.42} ${cy}h${r * 0.84}M${cx} ${cy - r * 0.42}v${r * 0.84}`} stroke="#5F6368" strokeWidth="1" />
    </g>
  );
}

// Autobús urbano (azul) o interurbano (verde)
export function DibujoBus({ color = "#1F5FD1", className = "" }) {
  return (
    <svg viewBox="0 0 80 36" className={className} aria-hidden="true">
      {/* sombra en el suelo */}
      <ellipse cx="40" cy="34.5" rx="34" ry="1.6" fill="#000" opacity="0.15" />
      {/* carrocería */}
      <path d="M4 6a4 4 0 0 1 4-4h58c4 0 7 2 8.5 5.5L77 14v13a3 3 0 0 1-3 3H6a2 2 0 0 1-2-2z" fill={color} />
      {/* techo más claro */}
      <path d="M8 2h58c2.4 0 4.4.8 6 2.2H6.3A4 4 0 0 1 8 2z" fill="#fff" opacity="0.25" />
      {/* ventanas */}
      {[8, 20, 32, 44].map((x) => (
        <rect key={x} x={x} y="7" width="10" height="9" rx="1.5" fill="#DCE8FB" />
      ))}
      {/* parabrisas */}
      <path d="M61 7h6.5c1.7 0 3 .9 3.8 2.4L74 15H61z" fill="#DCE8FB" />
      {/* puerta */}
      <rect x="56" y="7" width="4" height="21" rx="1" fill="#000" opacity="0.18" />
      <rect x="56.6" y="8" width="2.8" height="8" rx="0.8" fill="#DCE8FB" />
      {/* franja blanca */}
      <rect x="4" y="20" width="52" height="2.2" fill="#fff" opacity="0.85" />
      {/* faro e intermitente */}
      <rect x="73" y="22" width="3.2" height="2.6" rx="1" fill="#FFE08A" />
      <rect x="4" y="22" width="2" height="3" rx="0.8" fill="#E8453C" />
      {/* letrero de línea */}
      <rect x="62" y="3.4" width="9" height="2.6" rx="0.8" fill="#FFB300" />
      <Rueda cx={17} cy={29.5} />
      <Rueda cx={64} cy={29.5} />
    </svg>
  );
}

// Tren de cercanías de dos coches, genérico
export function DibujoTren({ className = "" }) {
  return (
    <svg viewBox="0 0 132 38" className={className} aria-hidden="true">
      <ellipse cx="66" cy="36.5" rx="62" ry="1.5" fill="#000" opacity="0.15" />
      {/* pantógrafo */}
      <path d="M86 6l6-5h9M92 1l6 5" stroke="#5F6368" strokeWidth="1.2" fill="none" />
      {/* coche trasero */}
      <rect x="2" y="6" width="60" height="25" rx="4" fill="#F4F5F7" stroke="#C9CDD2" />
      {/* coche delantero con morro */}
      <path d="M64 6h52c6 0 10 4 12 10l2 6v7a2 2 0 0 1-2 2H64z" fill="#F4F5F7" stroke="#C9CDD2" />
      {/* franja de ventanas */}
      <rect x="5" y="10" width="54" height="8" rx="2" fill="#2C3440" />
      <rect x="67" y="10" width="44" height="8" rx="2" fill="#2C3440" />
      <path d="M114 10h3c3 0 5.6 2.4 7 6.5l.5 1.5H114z" fill="#2C3440" />
      {/* banda de color */}
      <rect x="2" y="21" width="60" height="3" fill="#1F5FD1" />
      <path d="M64 21h65.5l.5 3H64z" fill="#1F5FD1" />
      {/* puertas: hoja clara con su ventanilla */}
      {[18, 42, 80, 100].map((x) => (
        <g key={x}>
          <rect x={x} y="9" width="7" height="21" rx="1" fill="#DDE1E6" stroke="#9AA0A6" strokeWidth="0.8" />
          <rect x={x + 1.5} y="11" width="4" height="7" rx="0.8" fill="#2C3440" />
          <rect x={x} y="21" width="7" height="3" fill="#1F5FD1" />
        </g>
      ))}
      {/* faro */}
      <rect x="125" y="25" width="3.5" height="2.4" rx="1" fill="#FFE08A" />
      {/* bogies */}
      <Rueda cx={12} cy={33} r={4} />
      <Rueda cx={52} cy={33} r={4} />
      <Rueda cx={74} cy={33} r={4} />
      <Rueda cx={116} cy={33} r={4} />
    </svg>
  );
}

// Metro: coche corto con frontal redondeado
export function DibujoMetro({ className = "" }) {
  return (
    <svg viewBox="0 0 80 36" className={className} aria-hidden="true">
      <ellipse cx="40" cy="34.5" rx="34" ry="1.5" fill="#000" opacity="0.15" />
      <path d="M3 8a4 4 0 0 1 4-4h58c6 0 10 5 11 11v13a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" fill="#E9EDF2" stroke="#BCC3CB" />
      <rect x="7" y="9" width="44" height="8" rx="2" fill="#2C3440" />
      <path d="M62 9h3c4 0 7 3 8 7v1H62z" fill="#2C3440" />
      <rect x="3" y="20" width="73" height="3" fill="#1F5FD1" />
      {[20, 54].map((x) => (
        <g key={x}>
          <rect x={x} y="8" width="7" height="21" rx="1" fill="#D3D9E0" stroke="#9AA0A6" strokeWidth="0.8" />
          <rect x={x + 1.5} y="10" width="4" height="7" rx="0.8" fill="#2C3440" />
          <rect x={x} y="20" width="7" height="3" fill="#1F5FD1" />
        </g>
      ))}
      <Rueda cx={16} cy={31} r={4} />
      <Rueda cx={62} cy={31} r={4} />
    </svg>
  );
}

// Elige el dibujo según la red de la parada
export function DibujoVehiculo({ tipo, red, className }) {
  if (tipo === "tren") return <DibujoTren className={className} />;
  if (tipo === "metro") return <DibujoMetro className={className} />;
  return <DibujoBus color={red === "interurbano" ? "#1F8A55" : "#1F5FD1"} className={className} />;
}
