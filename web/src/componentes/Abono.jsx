// Abono transporte: cuántos días le quedan y aviso en rojo si quedan menos de 3,
// porque mucha gente casi no lo mira. La fecha se guarda en el navegador.
import { useState } from "react";
import { Tarjeta } from "./Comunes.jsx";

const DIA = 24 * 60 * 60 * 1000;
const PERIODO = 30;

function hoy() {
  const d = new Date();
  d.setHours(0, 0, 0, 0);
  return d;
}

function aTexto(fecha) {
  const y = fecha.getFullYear();
  const m = String(fecha.getMonth() + 1).padStart(2, "0");
  const d = String(fecha.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

function deTexto(t) {
  const [y, m, d] = t.split("-").map(Number);
  return new Date(y, m - 1, d);
}

// Lee el abono guardado; la primera vez, el de la demo (caduca en unos días, para que se vea el aviso)
export function leerAbono(porDefecto) {
  try {
    const g = JSON.parse(localStorage.getItem("abono"));
    if (g?.caduca) return g;
  } catch {
    // sin almacenamiento se usa el de la demo
  }
  const d = hoy();
  d.setDate(d.getDate() + (porDefecto?.dias_demo ?? 2));
  return { tipo: porDefecto?.tipo ?? "Abono Transporte", caduca: aTexto(d) };
}

export function guardarAbono(a) {
  try {
    localStorage.setItem("abono", JSON.stringify(a));
  } catch {
    // dura hasta recargar
  }
}

export function diasQueQuedan(abono) {
  return Math.round((deTexto(abono.caduca) - hoy()) / DIA);
}

function frase(dias) {
  if (dias < 0) return "Tu abono está caducado";
  if (dias === 0) return "Tu abono caduca hoy";
  if (dias === 1) return "Te queda 1 día de abono";
  return `Te quedan ${dias} días de abono`;
}

// Mini aviso rojo que sale arriba en todas las pantallas cuando quedan menos de 3 días
export function AvisoAbono({ abono, onVer }) {
  const dias = diasQueQuedan(abono);
  if (dias >= 3) return null;
  const corto = dias < 0 ? "caducado" : dias === 0 ? "caduca hoy" : dias === 1 ? "1 día" : `${dias} días`;
  // pastilla pequeña y discreta, alineada a la derecha
  return (
    <div className="mb-2 flex justify-end">
      <button
        onClick={onVer}
        aria-label={`${frase(dias)}: recárgalo`}
        className="flex min-h-[32px] items-center gap-1.5 rounded-full border-2 border-[#111] bg-tarjeta px-3 text-[13px] font-bold text-tinta shadow-[2px_2px_0_#111]"
      >
        <span aria-hidden="true" className="h-[8px] w-[8px] animate-pulse rounded-full bg-rojo motion-reduce:animate-none" />
        Abono: {corto} · <span className="text-rojo-vivo underline">Recargar</span>
      </button>
    </div>
  );
}

// Tarjeta del abono en la portada
export default function TarjetaAbono({ abono, onCambiar }) {
  const [editando, setEditando] = useState(false);
  const dias = diasQueQuedan(abono);
  const urgente = dias < 3;
  const relleno = Math.max(0, Math.min(1, dias / PERIODO));
  const caduca = deTexto(abono.caduca).toLocaleDateString("es-ES", { day: "numeric", month: "long" });

  return (
    <Tarjeta id="abono" className="overflow-hidden">
      <div className="p-4">
        <div className="flex items-start justify-between gap-3">
          <div>
            <p className="text-[14px] font-bold uppercase tracking-wide text-tinta-2">{abono.tipo}</p>
            <p className={`cifra mt-1 text-[22px] ${urgente ? "text-rojo-vivo" : "text-tinta"}`}>{frase(dias)}</p>
            <p className="text-[14px] text-tinta-2">{dias < 0 ? `Caducó el ${caduca}` : `Válido hasta el ${caduca}`}</p>
          </div>
          {/* tarjeta del abono dibujada: roja, como la de Madrid */}
          <span
            aria-hidden="true"
            className="pegatina mt-1 flex h-[44px] w-[68px] shrink-0 flex-col justify-between rounded-lg bg-[#D7192D] p-1.5"
          >
            <span className="h-[9px] w-[12px] rounded-sm bg-[#F2C94C]" />
            <span className="h-[4px] w-full rounded-sm bg-white/70" />
          </span>
        </div>

        {/* barra de los 30 días */}
        <div
          className="mt-3 h-[14px] overflow-hidden rounded-full border-2 border-[#111] bg-tarjeta"
          role="img"
          aria-label={`${Math.max(dias, 0)} de ${PERIODO} días`}
        >
          <div className={`h-full ${urgente ? "bg-rojo" : "bg-verde"}`} style={{ width: `${relleno * 100}%` }} />
        </div>

        {urgente && (
          <p role="alert" className="mt-2 flex items-center gap-2 text-[14px] text-tinta-2">
            <span aria-hidden="true" className="h-[8px] w-[8px] shrink-0 animate-pulse rounded-full bg-rojo motion-reduce:animate-none" />
            <span>
              <span className="font-bold text-rojo-vivo">¡Recárgalo!</span> En las máquinas de Metro y Cercanías o en un estanco.
            </span>
          </p>
        )}

        {editando ? (
          <form
            className="mt-3 flex items-center gap-2"
            onSubmit={(e) => {
              e.preventDefault();
              setEditando(false);
            }}
          >
            <input
              type="date"
              value={abono.caduca}
              onChange={(e) => e.target.value && onCambiar({ ...abono, caduca: e.target.value })}
              className="pegatina h-[44px] min-w-0 flex-1 rounded-xl bg-tarjeta px-3 text-[16px]"
              aria-label="Fecha en la que caduca tu abono"
            />
            <button type="submit" className="boton-pegatina min-h-[44px] rounded-xl bg-amarillo px-4 font-bold">
              Listo
            </button>
          </form>
        ) : (
          <div className="mt-3 grid grid-cols-2 gap-2">
            <button
              onClick={() => {
                // recargado hoy: 30 días desde hoy (o desde que caducaba, si aún no había caducado)
                const base = dias > 0 ? deTexto(abono.caduca) : hoy();
                base.setDate(base.getDate() + PERIODO);
                onCambiar({ ...abono, caduca: aTexto(base) });
              }}
              className="boton-pegatina min-h-[44px] rounded-xl bg-amarillo px-2 text-[15px] font-bold"
            >
              Ya lo he recargado
            </button>
            <button onClick={() => setEditando(true)} className="boton-pegatina min-h-[44px] rounded-xl bg-tarjeta px-2 text-[15px] font-bold">
              Cambiar fecha
            </button>
          </div>
        )}
      </div>
    </Tarjeta>
  );
}
