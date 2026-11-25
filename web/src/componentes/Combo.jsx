// Desplegable con buscador: escribes «s» y salen Sol, Sevilla, Suanzes...
// Primero las opciones que empiezan por lo escrito, luego las que lo contienen. Teclado: ↑ ↓ Enter Esc.
import { useEffect, useId, useMemo, useRef, useState } from "react";
import { normalizar } from "../lib/util.js";

export default function Combo({ id, etiqueta, opciones, valor, onCambiar, placeholder = "Escribe para buscar", icono = null }) {
  const autoId = useId();
  const idCampo = id ?? `combo-${autoId}`;
  const elegida = opciones.find((o) => o.valor === valor) ?? null;
  const [texto, setTexto] = useState(elegida?.texto ?? "");
  const [abierto, setAbierto] = useState(false);
  const [activa, setActiva] = useState(0);
  const caja = useRef(null);
  const lista = useRef(null);

  // si cambia la opción elegida desde fuera, el campo muestra su nombre
  useEffect(() => {
    setTexto(elegida?.texto ?? "");
  }, [elegida?.texto]);

  // cerrar al tocar fuera
  useEffect(() => {
    if (!abierto) return;
    const fuera = (e) => caja.current && !caja.current.contains(e.target) && cerrar();
    document.addEventListener("pointerdown", fuera);
    return () => document.removeEventListener("pointerdown", fuera);
  });

  const filtradas = useMemo(() => {
    const q = normalizar(texto);
    if (!q || (elegida && texto === elegida.texto)) return opciones;
    const empieza = [];
    const contiene = [];
    for (const o of opciones) {
      const n = normalizar(o.texto);
      // «s» encuentra «Sol» y también «Avenida de Canillejas - Suecia» (palabra que empieza por s)
      if (n.startsWith(q)) empieza.push(o);
      else if (n.split(/[\s\-/.]+/).some((p) => p.startsWith(q))) empieza.push(o);
      else if (n.includes(q)) contiene.push(o);
    }
    return [...empieza, ...contiene];
  }, [texto, opciones, elegida]);

  function cerrar() {
    setAbierto(false);
    setTexto(elegida?.texto ?? "");
  }

  function elegir(o) {
    onCambiar(o.valor);
    setTexto(o.texto);
    setAbierto(false);
  }

  function teclas(e) {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setAbierto(true);
      setActiva((a) => Math.min(a + 1, filtradas.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActiva((a) => Math.max(a - 1, 0));
    } else if (e.key === "Enter" && abierto && filtradas[activa]) {
      e.preventDefault();
      elegir(filtradas[activa]);
    } else if (e.key === "Escape") {
      cerrar();
    }
  }

  // la opción activa siempre a la vista
  useEffect(() => {
    lista.current?.children[activa]?.scrollIntoView({ block: "nearest" });
  }, [activa]);

  return (
    <div ref={caja} className="relative">
      {etiqueta && (
        <label htmlFor={idCampo} className="block text-[14px] font-bold uppercase text-suave">
          {etiqueta}
        </label>
      )}
      <div className={`pegatina mt-1 flex h-[50px] items-center gap-2 rounded-xl bg-tarjeta px-3 ${abierto ? "shadow-[4px_4px_0_#2335F5]" : ""}`}>
        {icono}
        <input
          id={idCampo}
          role="combobox"
          aria-expanded={abierto}
          aria-controls={`${idCampo}-lista`}
          aria-autocomplete="list"
          aria-activedescendant={abierto && filtradas[activa] ? `${idCampo}-op-${activa}` : undefined}
          value={texto}
          placeholder={placeholder}
          onFocus={(e) => {
            setAbierto(true);
            setActiva(0);
            e.target.select();
          }}
          onChange={(e) => {
            setTexto(e.target.value);
            setAbierto(true);
            setActiva(0);
          }}
          onKeyDown={teclas}
          className="h-full min-w-0 flex-1 bg-transparent text-[16px] font-bold placeholder:font-normal placeholder:text-suave"
        />
        {texto && (
          <button
            type="button"
            aria-label="Borrar"
            onClick={() => {
              setTexto("");
              setAbierto(true);
              caja.current?.querySelector("input")?.focus();
            }}
            className="flex h-[32px] w-[32px] shrink-0 items-center justify-center rounded-full bg-hundido text-[18px] font-bold"
          >
            ×
          </button>
        )}
        <span aria-hidden="true" className={`shrink-0 text-suave transition-transform ${abierto ? "rotate-180" : ""}`}>
          ▾
        </span>
      </div>

      {abierto && (
        <ul
          ref={lista}
          id={`${idCampo}-lista`}
          role="listbox"
          aria-label={etiqueta ?? placeholder}
          // la lista va en su sitio, debajo del campo (no flotando): así no la recorta ninguna tarjeta
          className="pegatina relative z-10 mt-2 max-h-[264px] overflow-y-auto overscroll-contain rounded-xl bg-tarjeta py-1"
        >
          {filtradas.length === 0 && <li className="px-3 py-3 text-[15px] text-suave">No hay ninguna con «{texto}»</li>}
          {filtradas.map((o, i) => (
            <li
              key={o.valor}
              id={`${idCampo}-op-${i}`}
              role="option"
              aria-selected={o.valor === valor}
              onPointerDown={(e) => e.preventDefault()}
              onClick={() => elegir(o)}
              onPointerEnter={() => setActiva(i)}
              className={`flex min-h-[48px] cursor-pointer items-center gap-3 px-3 py-2 ${i === activa ? "bg-amarillo" : ""} ${
                i > 0 ? "border-t border-[#111]/10" : ""
              }`}
            >
              {o.marca}
              <span className="min-w-0 flex-1">
                <span className="block text-[16px] font-bold text-tinta">{o.texto}</span>
                {o.detalle && <span className="block text-[13px] text-suave">{o.detalle}</span>}
              </span>
              {o.valor === valor && <span className="text-[16px] font-bold">✓</span>}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
