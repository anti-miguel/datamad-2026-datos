// Iconos propios y genéricos en SVG (sin logotipos de operadores, sección 1.2 del manual)
const base = {
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 2,
  strokeLinecap: "round",
  strokeLinejoin: "round",
  "aria-hidden": true,
};

export function IconoBus({ className = "w-5 h-5" }) {
  return (
    <svg viewBox="0 0 24 24" className={className} {...base}>
      <rect x="5" y="3" width="14" height="15" rx="3" />
      <path d="M5 11h14M8 21v-3M16 21v-3" />
      <circle cx="8.5" cy="14.5" r="0.8" fill="currentColor" />
      <circle cx="15.5" cy="14.5" r="0.8" fill="currentColor" />
    </svg>
  );
}

export function IconoTren({ className = "w-5 h-5" }) {
  return (
    <svg viewBox="0 0 24 24" className={className} {...base}>
      <path d="M6 4h12a1 1 0 0 1 1 1v10a3 3 0 0 1-3 3H8a3 3 0 0 1-3-3V5a1 1 0 0 1 1-1z" />
      <path d="M5 10h14M9 21l1.5-3M15 21l-1.5-3" />
      <circle cx="9" cy="14" r="0.8" fill="currentColor" />
      <circle cx="15" cy="14" r="0.8" fill="currentColor" />
    </svg>
  );
}

export function IconoMetro({ className = "w-5 h-5" }) {
  return (
    <svg viewBox="0 0 24 24" className={className} {...base}>
      <rect x="5" y="4" width="14" height="13" rx="4" />
      <path d="M8 8h8M8 21l2-4M16 21l-2-4" />
      <circle cx="9" cy="13" r="0.8" fill="currentColor" />
      <circle cx="15" cy="13" r="0.8" fill="currentColor" />
    </svg>
  );
}

export function IconoVehiculo({ tipo, className }) {
  if (tipo === "tren") return <IconoTren className={className} />;
  if (tipo === "metro") return <IconoMetro className={className} />;
  return <IconoBus className={className} />;
}

export function IconoPin({ className = "w-6 h-6" }) {
  return (
    <svg viewBox="0 0 24 24" className={className} {...base}>
      <path d="M12 21s-6-5.5-6-11a6 6 0 0 1 12 0c0 5.5-6 11-6 11z" />
      <circle cx="12" cy="10" r="2.2" />
    </svg>
  );
}

export function IconoReloj({ className = "w-6 h-6" }) {
  return (
    <svg viewBox="0 0 24 24" className={className} {...base}>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 7v5l3 2" />
    </svg>
  );
}

export function IconoCampana({ className = "w-6 h-6" }) {
  return (
    <svg viewBox="0 0 24 24" className={className} {...base}>
      <path d="M6 16V11a6 6 0 0 1 12 0v5l1.5 2h-15z" />
      <path d="M10 20a2 2 0 0 0 4 0" />
    </svg>
  );
}

export function IconoInfo({ className = "w-6 h-6" }) {
  return (
    <svg viewBox="0 0 24 24" className={className} {...base}>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 11v6M12 7.5v.01" />
    </svg>
  );
}

export function IconoEstrella({ llena, className = "w-6 h-6" }) {
  return (
    <svg viewBox="0 0 24 24" className={className} {...base} fill={llena ? "currentColor" : "none"}>
      <path d="M12 3.5l2.6 5.3 5.9.9-4.3 4.1 1 5.8L12 16.9l-5.2 2.7 1-5.8-4.3-4.1 5.9-.9z" />
    </svg>
  );
}

export function IconoLupa({ className = "w-5 h-5" }) {
  return (
    <svg viewBox="0 0 24 24" className={className} {...base}>
      <circle cx="11" cy="11" r="6.5" />
      <path d="M20 20l-4.2-4.2" />
    </svg>
  );
}

export function IconoAviso({ className = "w-5 h-5" }) {
  return (
    <svg viewBox="0 0 24 24" className={className} {...base}>
      <path d="M12 4l9 16H3z" />
      <path d="M12 10v4M12 17v.01" />
    </svg>
  );
}

export function IconoFlechaAbajo({ className = "w-4 h-4" }) {
  return (
    <svg viewBox="0 0 24 24" className={className} {...base}>
      <path d="M6 9l6 6 6-6" />
    </svg>
  );
}
