// Logo de YaVoy redibujado a partir del boceto del equipo: la «Y» es un pin de mapa
// y debajo va una estela de velocidad. Variantes con los colores de la app.

// Colores de cada variante: pin, punto del pin, letras, estela
export const VARIANTES = {
  color: { pin: "#2335F5", punto: "#FFE15A", letras: "#111111", estela: ["#2335F5", "#C8102E"] },
  amarillo: { pin: "#111111", punto: "#FFE15A", letras: "#111111", estela: ["#111111", "#2335F5"] },
  negativo: { pin: "#FFE15A", punto: "#2335F5", letras: "#FFFFFF", estela: ["#FFE15A", "#B4C3FF"] },
  negro: { pin: "#111111", punto: "#FFFFFF", letras: "#111111", estela: ["#111111", "#111111"] },
};

// El pin que hace de «Y»: cabeza redonda con punto y un rabo largo que es el palo de la letra
export function PinY({ variante = "color", className = "", contorno = false }) {
  const c = VARIANTES[variante];
  return (
    <svg viewBox="0 0 40 60" className={className} aria-hidden="true">
      <path
        d="M20 2C10.6 2 3 9.4 3 18.6c0 7 4.4 12.4 9.8 16.6 2.9 2.3 4.2 4.6 4.2 8V56a3 3 0 0 0 6 0V43.2c0-3.4 1.3-5.7 4.2-8C32.6 31 37 25.6 37 18.6 37 9.4 29.4 2 20 2z"
        fill={c.pin}
        stroke={contorno ? "#111" : "none"}
        strokeWidth={contorno ? 2.5 : 0}
      />
      <circle cx="20" cy="18.5" r="7.2" fill={c.punto} stroke={contorno ? "#111" : "none"} strokeWidth={contorno ? 2 : 0} />
    </svg>
  );
}

// Logo horizontal: pin + «aVoy», con estela y, si se pide, el lema debajo
export function Logo({ variante = "color", alto = 40, lema = false, className = "" }) {
  const c = VARIANTES[variante];
  return (
    <div className={`inline-flex flex-col ${className}`} role="img" aria-label="YaVoy">
      <div className="flex items-end" style={{ height: alto }}>
        <PinY variante={variante} className="h-full w-auto" />
        <span
          className="font-[family-name:var(--font-display)] font-extrabold leading-none"
          style={{ color: c.letras, fontSize: alto * 0.78, letterSpacing: "-0.03em", marginLeft: alto * -0.02, marginBottom: alto * 0.03 }}
        >
          aVoy
        </span>
      </div>
      {/* estela de velocidad */}
      <svg viewBox="0 0 200 8" preserveAspectRatio="none" className="w-full" style={{ height: Math.max(4, alto * 0.12), marginTop: alto * 0.08 }} aria-hidden="true">
        <defs>
          <linearGradient id={`estela-${variante}`} x1="0" x2="1">
            <stop offset="0" stopColor={c.estela[1]} stopOpacity="0" />
            <stop offset="0.5" stopColor={c.estela[1]} />
            <stop offset="1" stopColor={c.estela[0]} />
          </linearGradient>
        </defs>
        <path d="M0 6 L200 0 L200 4 L0 8z" fill={`url(#estela-${variante})`} />
      </svg>
      {lema && (
        <span className="font-bold" style={{ color: c.letras, fontSize: Math.max(12, alto * 0.3), marginTop: alto * 0.12 }}>
          ¡Tu transporte en Madrid, al segundo!
        </span>
      )}
    </div>
  );
}
