// Abono transporte: cuántos días le quedan y aviso en rojo si quedan menos de 3,
// porque mucha gente casi no lo mira. La fecha se guarda en el navegador.
import { useState } from "react";

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
        className="flex min-h-[28px] items-center gap-1.5 rounded-full border-[1.5px] border-[#111] bg-tarjeta px-2.5 text-[12px] font-bold text-tinta"
      >
        <span aria-hidden="true" className="h-[7px] w-[7px] animate-pulse rounded-full bg-rojo motion-reduce:animate-none" />
        Abono: {corto} · <span className="text-rojo-vivo underline">Recargar</span>
      </button>
    </div>
  );
}

// Tarjeta del abono en la portada: una sola línea; las opciones se abren con «Recargar»
export default function TarjetaAbono({ abono, onCambiar }) {
  const [abierta, setAbierta] = useState(false);
  const dias = diasQueQuedan(abono);
  const urgente = dias < 3;
  const relleno = Math.max(0, Math.min(1, dias / PERIODO));
  const caduca = deTexto(abono.caduca).toLocaleDateString("es-ES", { day: "numeric", month: "long" });
  const corto = dias < 0 ? "caducado" : dias === 0 ? "caduca hoy" : dias === 1 ? "1 día" : `${dias} días`;

  return (
    <div id="abono" className="rounded-xl border-2 border-[#111] bg-tarjeta px-3 py-2">
      <div className="flex items-center gap-2.5">
        {/* abono dibujado en pequeño: rojo, como el de Madrid */}
        <span aria-hidden="true" className="flex h-[22px] w-[34px] shrink-0 flex-col justify-between rounded-[4px] border-[1.5px] border-[#111] bg-[#D7192D] p-[3px]">
          <span className="h-[5px] w-[7px] rounded-[1px] bg-[#F2C94C]" />
          <span className="h-[2px] w-full rounded-sm bg-white/70" />
        </span>
        <div className="min-w-0 flex-1">
          <p className="flex items-center gap-1.5 text-[14px] font-bold text-tinta">
            {urgente && <span aria-hidden="true" className="h-[7px] w-[7px] shrink-0 animate-pulse rounded-full bg-rojo motion-reduce:animate-none" />}
            <span className="truncate">
              Abono · <span className={urgente ? "text-rojo-vivo" : ""}>{corto}</span>
            </span>
          </p>
          {/* barrita de los 30 días */}
          <div className="mt-1 h-[5px] overflow-hidden rounded-full bg-hundido" role="img" aria-label={`${frase(dias)}, hasta el ${caduca}`}>
            <div className={`h-full ${urgente ? "bg-rojo" : "bg-verde"}`} style={{ width: `${relleno * 100}%` }} />
          </div>
        </div>
        <button
          onClick={() => setAbierta((a) => !a)}
          aria-expanded={abierta}
          className={`min-h-[36px] shrink-0 rounded-lg border-[1.5px] border-[#111] px-2.5 text-[13px] font-bold ${urgente ? "bg-amarillo" : "bg-hundido"}`}
        >
          {abierta ? "Cerrar" : "Recargar"}
        </button>
      </div>

      {abierta && (
        <div className="mt-2 space-y-2 border-t border-[#111]/15 pt-2">
          <p className="text-[13px] text-tinta-2">
            {dias < 0 ? `Caducó el ${caduca}.` : `Válido hasta el ${caduca}.`} Se recarga en las máquinas de Metro y Cercanías o desde la app.
          </p>
          <div className="flex gap-2">
            <button
              onClick={() => {
                // recargado: 30 días desde hoy (o desde que caducaba, si aún no había caducado)
                const base = dias > 0 ? deTexto(abono.caduca) : hoy();
                base.setDate(base.getDate() + PERIODO);
                onCambiar({ ...abono, caduca: aTexto(base) });
                setAbierta(false);
              }}
              className="boton-pegatina min-h-[40px] flex-1 rounded-lg bg-amarillo px-2 text-[14px] font-bold"
            >
              Ya lo he recargado
            </button>
            <input
              type="date"
              value={abono.caduca}
              onChange={(e) => e.target.value && onCambiar({ ...abono, caduca: e.target.value })}
              className="h-[40px] min-w-0 flex-1 rounded-lg border-[1.5px] border-[#111] bg-tarjeta px-2 text-[14px]"
              aria-label="Fecha en la que caduca tu abono"
            />
          </div>
        </div>
      )}
    </div>
  );
}
