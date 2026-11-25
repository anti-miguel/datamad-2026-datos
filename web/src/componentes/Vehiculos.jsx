// Dibujos propios de los vehículos de Madrid, vistos de lado y mirando a la derecha.
// Siguen la forma y los colores de los modelos reales (fotos de referencia que pasó el equipo):
// bus de la EMT, interurbano verde, Cercanías tipo Civia, metro serie 5000 y BiciMAD.
// Sin logotipos ni rótulos de operador. Las ruedas giran con la clase «rueda»;
// con «parado» en el padre se detienen.

function Rueda({ cx, cy, r = 5, llanta = "#C4C8CD" }) {
  return (
    <g className="rueda" style={{ transformOrigin: `${cx}px ${cy}px` }}>
      <circle cx={cx} cy={cy} r={r} fill="#1B1D20" />
      <circle cx={cx} cy={cy} r={r * 0.58} fill={llanta} />
      <circle cx={cx} cy={cy} r={r * 0.2} fill="#3C4043" />
      {[0, 60, 120, 180, 240, 300].map((a) => (
        <circle
          key={a}
          cx={cx + Math.cos((a * Math.PI) / 180) * r * 0.38}
          cy={cy + Math.sin((a * Math.PI) / 180) * r * 0.38}
          r={r * 0.07}
          fill="#3C4043"
        />
      ))}
    </g>
  );
}

// Paso de rueda: hueco oscuro en la carrocería
function Paso({ cx, cy, r }) {
  return <path d={`M${cx - r - 1.8} ${cy + 1.5}a${r + 1.8} ${r + 1.8} 0 0 1 ${2 * r + 3.6} 0z`} fill="#202326" />;
}

// Puerta de cristal oscuro con su junta central
function PuertaCristal({ x, y, ancho, alto, marco }) {
  return (
    <g>
      <rect x={x} y={y} width={ancho} height={alto} rx="0.6" fill="#20262D" stroke={marco} strokeWidth="0.8" />
      <line x1={x + ancho / 2} y1={y + 0.5} x2={x + ancho / 2} y2={y + alto - 0.5} stroke={marco} strokeWidth="0.6" />
    </g>
  );
}

// Bus urbano de la EMT: techo blanco que baja hasta las ventanas, parte baja azul,
// faldón gris, cristalera oscura corrida y frontal negro alto con el letrero de destino.
export function DibujoBusEMT({ className = "" }) {
  return (
    <svg viewBox="0 0 120 44" className={className} aria-hidden="true">
      <ellipse cx="60" cy="42.6" rx="56" ry="1.4" fill="#000" opacity="0.18" />
      {/* parte baja azul (toda la carrocería, luego se tapa arriba con el techo) */}
      <path d="M3 14a4 4 0 0 1 4-4h104c3 0 5 1.6 5.6 4.4L118 21v14.5a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" fill="#3A8BDB" />
      {/* techo blanco, alto y redondeado */}
      {/* techo blanco grande y abombado, que baja hasta las ventanas */}
      <path d="M3 16c0-9 4.5-14.2 13-14.6L102 1c7 0 11 3 12.6 8.4l.4 6.6H3z" fill="#F4F5F4" />
      <path d="M14 2.6L100 2.2c4 0 7 1.4 8.6 3.6H10c1-1.8 2.4-2.8 4-3.2z" fill="#fff" />
      <path d="M3 16h112" stroke="#D5D8DB" strokeWidth="0.6" />
      {/* cristalera oscura corrida con montantes finos */}
      <rect x="5" y="16" width="104" height="9" fill="#262C33" />
      {[22, 44, 76, 93].map((x) => (
        <rect key={x} x={x} y="16" width="0.9" height="9" fill="#4A535D" />
      ))}
      {/* frontal: parabrisas negro alto, con el letrero arriba */}
      <path d="M109 9h5.4c1.4 0 2.2.8 2.6 2.2L118.6 29H109z" fill="#17191C" />
      <rect x="110" y="10.4" width="6.4" height="2.4" rx="0.5" fill="#FFB300" opacity="0.9" />
      <path d="M111 15l5 0 1.4 9h-6.4z" fill="#3A4654" opacity="0.8" />
      {/* faldón gris inferior */}
      <rect x="3" y="32" width="115" height="5.5" rx="1.5" fill="#8D9298" />
      {/* puertas: trasera, central y delantera */}
      <PuertaCristal x={20} y={16} ancho={8} alto={19} marco="#5E6A76" />
      <PuertaCristal x={60} y={16} ancho={9} alto={19} marco="#5E6A76" />
      <PuertaCristal x={100} y={16} ancho={8} alto={19} marco="#5E6A76" />
      {/* faros, piloto y retrovisor */}
      <rect x="114.5" y="29.5" width="3.4" height="2" rx="0.8" fill="#FFF3C4" />
      <rect x="3" y="25" width="1.6" height="4.5" rx="0.6" fill="#D93025" />
      <path d="M117 9.5c2.6-.3 3.6.8 3.6 2.6v2.4" stroke="#1B1D20" strokeWidth="1" fill="none" />
      <Paso cx={38} cy={37.5} r={5.2} />
      <Paso cx={89} cy={37.5} r={5.2} />
      <Rueda cx={38} cy={37.5} r={5.2} />
      <Rueda cx={89} cy={37.5} r={5.2} />
    </svg>
  );
}

// Interurbano: verde lima entero, banda negra de ventanas corrida, techo redondeado
// hacia el frontal, dos puertas y llantas verdes.
export function DibujoBusInterurbano({ className = "" }) {
  return (
    <svg viewBox="0 0 120 44" className={className} aria-hidden="true">
      <ellipse cx="60" cy="42.6" rx="56" ry="1.4" fill="#000" opacity="0.18" />
      {/* módulo del techo */}
      <rect x="18" y="3" width="10" height="2.4" rx="0.8" fill="#4FA324" />
      <rect x="100" y="3.4" width="7" height="2" rx="0.8" fill="#2F3A2A" />
      {/* carrocería verde, con el techo que se curva hacia el frontal */}
      <path d="M3 10c0-3.3 2.7-5.5 6-5.5h96c6 0 10 3 11.5 8.5L118 19v16.5a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" fill="#63BD2F" />
      {/* brillo del techo */}
      <path d="M8 5.6h96c3 0 5.6 1 7.4 2.8H5.4C6 6.6 7 5.6 8 5.6z" fill="#fff" opacity="0.2" />
      {/* banda negra de ventanas */}
      <path d="M4 11h103c3.4 0 5.6 1.8 6.6 5l1.6 7H4z" fill="#1E2226" />
      {[26, 48, 70, 88].map((x) => (
        <rect key={x} x={x} y="11" width="1.2" height="12" fill="#63BD2F" />
      ))}
      {/* parabrisas */}
      <path d="M108 11.5c3 .3 4.8 2 5.6 4.6l1.5 6.9H108z" fill="#2E3A44" />
      <rect x="99" y="11.8" width="8" height="2.2" rx="0.5" fill="#FFB300" opacity="0.85" />
      {/* puertas delantera y central */}
      <PuertaCristal x={97} y={14} ancho={8} alto={21} marco="#3E8A1A" />
      <PuertaCristal x={55} y={11.5} ancho={9} alto={23.5} marco="#3E8A1A" />
      {/* parte baja algo más oscura */}
      <rect x="3" y="33" width="115" height="4.5" rx="1.5" fill="#4FA324" />
      <rect x="114.5" y="29.5" width="3.4" height="2" rx="0.8" fill="#FFF3C4" />
      <rect x="3" y="25" width="1.6" height="4.5" rx="0.6" fill="#D93025" />
      <path d="M116.5 11c2.6-.3 3.6.8 3.6 2.6v2.4" stroke="#1B1D20" strokeWidth="1" fill="none" />
      <Paso cx={30} cy={37.5} r={5.4} />
      <Paso cx={86} cy={37.5} r={5.4} />
      <Rueda cx={30} cy={37.5} r={5.4} llanta="#6CC63A" />
      <Rueda cx={86} cy={37.5} r={5.4} llanta="#6CC63A" />
    </svg>
  );
}

// Cercanías tipo Civia: caja blanca, techo gris oscuro, cristales oscuros corridos,
// morro rojo que rodea un gran parabrisas negro, parachoques blanco y franjas
// finas roja y morada en el lateral. Se ven dos coches.
export function DibujoTren({ className = "" }) {
  return (
    <svg viewBox="0 0 200 42" className={className} aria-hidden="true">
      <ellipse cx="100" cy="40.6" rx="96" ry="1.4" fill="#000" opacity="0.18" />
      {/* pantógrafo */}
      <path d="M40 5.5l7-5h12M47 .5l7 5" stroke="#5F6368" strokeWidth="1.1" fill="none" />
      {/* bastidor negro bajo la caja */}
      <rect x="4" y="31" width="182" height="4" fill="#2A2D31" />
      {/* coche trasero */}
      <rect x="2" y="5" width="92" height="27" rx="3" fill="#F8F8F6" stroke="#D3D6DA" strokeWidth="0.7" />
      <rect x="2" y="5" width="92" height="3.2" rx="1.5" fill="#4A4F55" />
      {/* coche delantero: caja + morro */}
      <path d="M96 5h76c9 0 16 6 19.5 14l3 8.5c.6 2-.8 4.5-3 4.5H96z" fill="#F8F8F6" stroke="#D3D6DA" strokeWidth="0.7" />
      <path d="M96 5h76c3.4 0 6.4.9 9 2.6H96z" fill="#4A4F55" />
      {/* cristales oscuros corridos */}
      <rect x="5" y="11" width="86" height="8.5" rx="1.5" fill="#22282F" />
      <rect x="99" y="11" width="66" height="8.5" rx="1.5" fill="#22282F" />
      {/* morro rojo que envuelve el parabrisas negro */}
      <path d="M166 5.4c10 0 18 5.4 22.6 14.6l2.6 7c.3 1-.4 2-1.4 2H178c-6 0-10-3-11.5-7.5L163 9z" fill="#D7192D" />
      <path d="M170 8.6c7 .6 12.4 5 15.4 11.4l.9 2.4h-9.4c-3.4 0-5.6-1.8-6.6-4.8z" fill="#15191E" />
      <path d="M172.5 10.4c4.6.8 8 3.8 10.2 8h-8.4z" fill="#3A4654" />
      {/* parachoques blanco con el faro */}
      <path d="M176 26h14.6c1.4 0 2.4 1.4 2 2.8l-.6 2.2H176z" fill="#FFFFFF" stroke="#D3D6DA" strokeWidth="0.6" />
      <circle cx="187" cy="24" r="1.3" fill="#FFF3C4" stroke="#D3D6DA" strokeWidth="0.4" />
      {/* franjas finas del lateral: roja bajo las ventanas, morada y roja abajo */}
      <rect x="2" y="21" width="92" height="0.9" fill="#D7192D" />
      <rect x="96" y="21" width="72" height="0.9" fill="#D7192D" />
      <rect x="2" y="26.5" width="92" height="1.6" fill="#6B2C83" />
      <rect x="2" y="28.4" width="92" height="1.2" fill="#D7192D" />
      <path d="M96 26.5h70l2 1.6H96z" fill="#6B2C83" />
      <path d="M96 28.4h72.6l1 1.2H96z" fill="#D7192D" />
      {/* puertas dobles blancas con ventanillas */}
      {[16, 64, 108, 146].map((x) => (
        <g key={x}>
          <rect x={x} y="9.5" width="11" height="22" rx="0.8" fill="#EEF0F2" stroke="#A9AEB4" strokeWidth="0.6" />
          <line x1={x + 5.5} y1="9.5" x2={x + 5.5} y2="31.5" stroke="#A9AEB4" strokeWidth="0.5" />
          <rect x={x + 1.3} y="11.5" width="3.4" height="9" rx="0.8" fill="#22282F" />
          <rect x={x + 6.3} y="11.5" width="3.4" height="9" rx="0.8" fill="#22282F" />
        </g>
      ))}
      {/* fuelle entre coches */}
      <rect x="94" y="9" width="2" height="22" fill="#4A4F55" />
      {/* bogies */}
      {[14, 30, 68, 84, 108, 124, 160, 176].map((x) => (
        <Rueda key={x} cx={x} cy={36.5} r={3.6} />
      ))}
    </svg>
  );
}

// Metro de Madrid tipo serie 5000: caja blanca, cabina azul con gran parabrisas,
// franja azul en diagonal desde la cabina hasta la banda azul de abajo.
export function DibujoMetro({ className = "" }) {
  return (
    <svg viewBox="0 0 110 40" className={className} aria-hidden="true">
      <ellipse cx="55" cy="38.6" rx="52" ry="1.4" fill="#000" opacity="0.18" />
      <rect x="4" y="31" width="100" height="3" fill="#2A2D31" />
      {/* caja blanca */}
      <rect x="2" y="5" width="104" height="27" rx="2.5" fill="#F6F7F8" stroke="#CDD1D5" strokeWidth="0.7" />
      <rect x="2" y="5" width="104" height="1.6" rx="0.8" fill="#1D5FB8" />
      {/* cabina azul y diagonal */}
      <path d="M86 5h17.5c1.4 0 2.5 1.1 2.5 2.5V32H72z" fill="#1D5FB8" />
      <path d="M80 5h4L68 32h-4z" fill="#1D5FB8" />
      {/* banda azul inferior */}
      <rect x="2" y="27" width="70" height="2.6" fill="#1D5FB8" />
      {/* parabrisas de la cabina */}
      <rect x="93" y="8" width="11" height="12" rx="1.2" fill="#22282F" />
      <rect x="86.5" y="9" width="4" height="10" rx="0.8" fill="#22282F" />
      {/* ventanas pequeñas separadas */}
      {[6, 34, 54].map((x) => (
        <rect key={x} x={x} y="10" width="7" height="8" rx="1" fill="#22282F" />
      ))}
      {/* puertas dobles con dos ventanillas */}
      {[17, 42, 64].map((x) => (
        <g key={x}>
          <rect x={x} y="8" width="9" height="23" rx="0.6" fill="#EEF0F2" stroke="#A9AEB4" strokeWidth="0.6" />
          <line x1={x + 4.5} y1="8" x2={x + 4.5} y2="31" stroke="#A9AEB4" strokeWidth="0.5" />
          <rect x={x + 1.1} y="10" width="2.6" height="8" rx="0.7" fill="#22282F" />
          <rect x={x + 5.3} y="10" width="2.6" height="8" rx="0.7" fill="#22282F" />
        </g>
      ))}
      <rect x="102" y="26" width="3" height="2" rx="0.8" fill="#FFF3C4" />
      {[12, 24, 84, 96].map((x) => (
        <Rueda key={x} cx={x} cy={34.8} r={3.3} />
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
        <circle cx="10" cy="21" r="7" stroke="#1B1D20" strokeWidth="2" />
        <circle cx="38" cy="21" r="7" stroke="#1B1D20" strokeWidth="2" />
        <path d="M10 21l7-1 9-9 5 0M17 20l3-11M26 11l12 10" stroke="#F2F3F5" strokeWidth="3" />
        <path d="M10 21l7-1 9-9 5 0M17 20l3-11M26 11l12 10" stroke="#C9CDD2" strokeWidth="0.6" />
        <path d="M3.5 18a7 7 0 0 1 11-4.5M31.5 17.5a7 7 0 0 1 12 0" stroke="#1D63B8" strokeWidth="1.6" />
        <path d="M31 11l2-5h4" stroke="#1B1D20" strokeWidth="1.6" />
        <path d="M17 8.5h6" stroke="#1B1D20" strokeWidth="2.2" />
      </g>
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
