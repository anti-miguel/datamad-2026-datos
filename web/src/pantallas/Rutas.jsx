// Pantalla «Rutas»: buscador de origen y destino que propone una ruta (como un planificador)
// y la compara con tus rutas personales, que salen de tu experiencia. Incluye «¿cuándo salgo?».
import { useMemo, useState } from "react";
import { Linea, Etiqueta, Tarjeta, Volver } from "../componentes/Comunes.jsx";
import {
  IconoAndar, IconoTransbordo, IconoLapiz, IconoUni, IconoTrabajo, IconoCasa, IconoRutas, IconoCampana, IconoReloj,
} from "../componentes/Iconos.jsx";
import { calcularRuta, cadenaDeLineas, horaDeSalida, salirEn } from "../lib/rutas.js";

const ICONOS = { uni: IconoUni, trabajo: IconoTrabajo, casa: IconoCasa };

function leerLocal(clave, porDefecto) {
  try {
    return JSON.parse(localStorage.getItem(clave)) ?? porDefecto;
  } catch {
    return porDefecto;
  }
}
function guardarLocal(clave, valor) {
  try {
    localStorage.setItem(clave, JSON.stringify(valor));
  } catch {
    // Sin almacenamiento se pierde al recargar
  }
}

// Nombre editable en el sitio: lápiz → campo → guardar
export function NombreEditable({ nombre, onCambiar, className = "", etiqueta = "Cambiar nombre" }) {
  const [editando, setEditando] = useState(false);
  const [texto, setTexto] = useState(nombre);
  if (editando) {
    return (
      <form
        className="flex items-center gap-2"
        onSubmit={(e) => {
          e.preventDefault();
          const limpio = texto.trim();
          if (limpio) onCambiar(limpio.slice(0, 40));
          setEditando(false);
        }}
      >
        <input
          autoFocus
          value={texto}
          maxLength={40}
          onChange={(e) => setTexto(e.target.value)}
          aria-label={etiqueta}
          className="pegatina h-[44px] min-w-0 flex-1 rounded-xl bg-tarjeta px-3 text-[17px] font-bold"
        />
        <button type="submit" className="boton-pegatina min-h-[44px] rounded-xl bg-amarillo px-3 font-bold">
          Guardar
        </button>
      </form>
    );
  }
  return (
    <div className="flex items-start gap-2">
      <span className={className}>{nombre}</span>
      <button
        onClick={(e) => {
          e.stopPropagation();
          setTexto(nombre);
          setEditando(true);
        }}
        aria-label={etiqueta}
        className="boton-pegatina flex h-[36px] w-[36px] shrink-0 items-center justify-center rounded-lg bg-tarjeta"
      >
        <IconoLapiz className="h-4 w-4" />
      </button>
    </div>
  );
}

// Tira de líneas: «4 o 106 o 159 o 287 ⇄ 2 ⇄ 5»
function Cadena({ ruta }) {
  return (
    <div className="flex flex-wrap items-center gap-1.5">
      {cadenaDeLineas(ruta).map((c, i) =>
        c.transbordo ? (
          <span key={i} className="flex items-center text-tinta" aria-label="transbordo">
            <IconoTransbordo className="h-5 w-5" />
          </span>
        ) : (
          <span key={i} className="flex flex-wrap items-center gap-1">
            {c.lineas.map((l, j) => (
              <span key={l.linea} className="flex items-center gap-1">
                {j > 0 && <span className="text-[13px] font-bold text-suave">o</span>}
                <Linea linea={l.linea} red={l.red} />
              </span>
            ))}
          </span>
        ),
      )}
    </div>
  );
}

const texTotal = (t) => (t ? `${t.desde}–${t.hasta} min` : "Sin datos suficientes");
const nombreLugar = (lugares, id) => lugares.find((l) => l.id === id);

// ───────────────────────── Buscador y lista ─────────────────────────

function SelectorLugar({ etiqueta, valor, lugares, onCambiar }) {
  const l = nombreLugar(lugares, valor);
  return (
    <label className="flex min-h-[56px] items-center gap-3 px-3">
      <span className="w-[52px] shrink-0 text-[14px] font-bold uppercase text-suave">{etiqueta}</span>
      <span className="min-w-0 flex-1">
        <select
          value={valor}
          onChange={(e) => onCambiar(e.target.value)}
          className="w-full appearance-none bg-transparent text-[18px] font-bold text-tinta outline-none"
          aria-label={etiqueta}
        >
          {lugares.map((x) => (
            <option key={x.id} value={x.id}>
              {x.nombre}
            </option>
          ))}
        </select>
        {l && <span className="block text-[13px] text-suave">{l.detalle}</span>}
      </span>
      <span aria-hidden="true" className="text-suave">▾</span>
    </label>
  );
}

function TarjetaOpcion({ titulo, sello, ruta, calculo, onAbrir, destacada, ahorro, deExperiencia }) {
  return (
    <button onClick={onAbrir} className="block w-full text-left">
      <Tarjeta sombra={destacada} className={`overflow-hidden ${destacada ? "!bg-amarillo" : ""}`}>
        <div className="p-4">
          <div className="flex flex-wrap items-center gap-2">
            <span className={`rounded-md border-2 border-[#111] px-2 text-[13px] font-bold ${destacada ? "bg-tinta text-amarillo" : "bg-hundido"}`}>
              {sello}
            </span>
            {ahorro > 0 && (
              <span className="rounded-md border-2 border-[#111] bg-verde px-2 text-[13px] font-bold text-white">
                TE AHORRAS {deExperiencia ? "UNOS " : ""}{ahorro} MIN{deExperiencia ? " · TU EXPERIENCIA" : ""}
              </span>
            )}
          </div>
          <p className="titulo mt-2 text-[18px] text-tinta">{titulo}</p>
          <div className="mt-2">
            <Cadena ruta={ruta} />
          </div>
          <div className="mt-3 flex items-end justify-between gap-2">
            <span className="text-[14px] text-tinta-2">
              {calculo.transbordos === 0 ? "Sin transbordos" : calculo.transbordos === 1 ? "1 transbordo" : `${calculo.transbordos} transbordos`}
            </span>
            <span className="cifra text-[24px] tabular-nums text-tinta">{texTotal(calculo.total)} →</span>
          </div>
        </div>
      </Tarjeta>
    </button>
  );
}

export function ListaRutas({ demo, datos, contexto, nombres, onRenombrar, onAbrir, onCasoMedido }) {
  const lugares = demo.lugares ?? [];
  const [origen, setOrigen] = useState("casa");
  const [destino, setDestino] = useState("uni");
  const rutas = demo.rutas ?? [];
  const planes = demo.planificador ?? [];

  const tuya = rutas.find((r) => r.origen === origen && r.destino === destino);
  const plan = planes.find((r) => r.origen === origen && r.destino === destino);
  const cTuya = tuya && datos ? calcularRuta(datos, tuya, contexto, {}, "segura", demo) : null;
  const cPlan = plan && datos ? calcularRuta(datos, plan, contexto, {}, "segura", demo) : null;
  // ahorro según tu experiencia (lo apuntas tú en la ruta); si no hay, el que sale de los datos
  const ahorro = tuya?.ahorro_experiencia ?? (cTuya?.total && cPlan?.total ? cPlan.total.hasta - cTuya.total.hasta : 0);
  const deExperiencia = tuya?.ahorro_experiencia != null;

  return (
    <div className="space-y-4">
      <h1 className="titulo pt-2 text-[32px] text-tinta">¿A dónde vas?</h1>

      <Tarjeta className="relative">
        <SelectorLugar etiqueta="Desde" valor={origen} lugares={lugares} onCambiar={setOrigen} />
        <div className="mx-3 border-t-2 border-dashed border-[#111]/30" />
        <SelectorLugar etiqueta="Hasta" valor={destino} lugares={lugares} onCambiar={setDestino} />
        <button
          onClick={() => {
            setOrigen(destino);
            setDestino(origen);
          }}
          aria-label="Intercambiar origen y destino"
          className="boton-pegatina absolute right-10 top-1/2 flex h-[40px] w-[40px] -translate-y-1/2 items-center justify-center rounded-full bg-amarillo text-[18px] font-bold"
        >
          ⇅
        </button>
      </Tarjeta>

      {origen === destino ? (
        <p className="text-[16px] text-tinta-2">Elige un destino distinto del origen.</p>
      ) : (
        <section className="space-y-3" aria-live="polite">
          {tuya && cTuya && (
            <TarjetaOpcion
              titulo={nombres[`ruta-${tuya.id}`] ?? tuya.nombre}
              sello="TU RUTA · POR EXPERIENCIA"
              ruta={tuya}
              calculo={cTuya}
              destacada
              ahorro={ahorro}
              deExperiencia={deExperiencia}
              onAbrir={() => onAbrir(tuya.id)}
            />
          )}
          {plan && cPlan && (
            <TarjetaOpcion
              titulo="La que te daría un planificador"
              sello="PLANIFICADOR · EJEMPLO"
              ruta={plan}
              calculo={cPlan}
              destacada={!tuya}
              onAbrir={() => onAbrir(plan.id)}
            />
          )}
          {!tuya && !plan && (
            <Tarjeta className="p-4">
              <p className="text-[16px] font-bold text-tinta">En la demo solo hay rutas preparadas desde Casa.</p>
              <p className="mt-1 text-[14px] text-suave">En la versión real, el planificador calcularía cualquier trayecto.</p>
            </Tarjeta>
          )}
          {!tuya && plan && (
            <p className="text-[14px] text-tinta-2">¿Conoces un camino mejor? Guárdalo como tu ruta y te lo propondremos primero.</p>
          )}
        </section>
      )}

      <h2 className="titulo pt-2 text-[22px] text-tinta">Mis rutas</h2>
      {rutas.map((ruta) => {
        const Icono = ICONOS[ruta.icono] ?? IconoRutas;
        const c = datos ? calcularRuta(datos, ruta, contexto, {}, "segura", demo) : null;
        const nombre = nombres[`ruta-${ruta.id}`] ?? ruta.nombre;
        return (
          <Tarjeta key={ruta.id} className="overflow-hidden">
            <div className="flex items-start gap-3 p-4 pb-3">
              <span className="pegatina flex h-[48px] w-[48px] shrink-0 items-center justify-center rounded-xl bg-amarillo">
                <Icono />
              </span>
              <div className="min-w-0 flex-1">
                <NombreEditable
                  nombre={nombre}
                  onCambiar={(n) => onRenombrar(`ruta-${ruta.id}`, n)}
                  etiqueta={`Cambiar el nombre de la ruta ${nombre}`}
                  className="titulo text-[19px] text-tinta"
                />
                <p className="mt-1 text-[15px] text-suave">
                  {ruta.desde} → {ruta.hasta}
                </p>
                {ruta.ejemplo && (
                  <span className="mt-1 inline-block rounded-md border-2 border-[#111] bg-aviso-simulado px-2 text-[13px] font-bold">
                    EJEMPLO
                  </span>
                )}
              </div>
            </div>
            <div className="px-4 pb-3">
              <Cadena ruta={ruta} />
            </div>
            <button
              onClick={() => onAbrir(ruta.id)}
              className="flex min-h-[56px] w-full items-center justify-between border-t-[2.5px] border-[#111] bg-hundido px-4 text-left"
            >
              <span className="text-[15px] text-tinta-2">
                {ruta.llegar_antes ? `Para llegar a las ${ruta.llegar_antes}, sal a las ` : "Si sales ahora, llegas en"}
              </span>
              <span className="cifra text-[20px] text-principal">
                {ruta.llegar_antes ? horaDeSalida(c?.total, ruta.llegar_antes) ?? "—" : texTotal(c?.total)} →
              </span>
            </button>
          </Tarjeta>
        );
      })}

      <button onClick={onCasoMedido} className="block w-full text-left">
        <Tarjeta className="flex items-center gap-3 p-4">
          <span className="pegatina flex h-[48px] w-[48px] shrink-0 items-center justify-center rounded-xl bg-aviso-simulado">
            <IconoReloj />
          </span>
          <span className="min-w-0 flex-1">
            <span className="block text-[16px] font-bold text-tinta">Caso real medido: ¿cuándo salgo?</span>
            <span className="block text-[14px] text-suave">Móstoles → Nuevos Ministerios, con el GPS de los trenes</span>
          </span>
          <span className="text-[20px]">→</span>
        </Tarjeta>
      </button>

      <p className="text-[14px] text-suave">
        Las esperas salen de los datos medidos. Los tiempos de viaje del bus salen del horario oficial; los de metro, andando y
        transbordo son aproximados. La ruta del planificador es un ejemplo.
      </p>
    </div>
  );
}

// ───────────────────────── Detalle de una ruta ─────────────────────────

function Paso({ color, children, punteado = false }) {
  return (
    <div className="relative flex gap-3">
      <div className="flex w-[28px] shrink-0 flex-col items-center">
        <div
          className="min-h-[24px] w-[6px] flex-1"
          style={
            punteado
              ? { backgroundImage: "radial-gradient(#111 1.6px, transparent 1.8px)", backgroundSize: "6px 9px", backgroundRepeat: "repeat-y" }
              : { background: color, border: "2px solid #111", borderRadius: 4 }
          }
        />
      </div>
      <div className="min-w-0 flex-1 pb-3">{children}</div>
    </div>
  );
}

function Hito({ texto, sub, final = false }) {
  return (
    <div className="flex items-center gap-3">
      <div className="flex w-[28px] justify-center">
        <div className={`h-[20px] w-[20px] rounded-full border-[3px] border-[#111] ${final ? "bg-amarillo" : "bg-tarjeta"}`} />
      </div>
      <div>
        <p className="text-[17px] font-bold text-tinta">{texto}</p>
        {sub && <p className="text-[14px] text-suave">{sub}</p>}
      </div>
    </div>
  );
}

const COLOR_TRAMO = { emt: "#2335F5", interurbano: "#3F8F1E", renfe: "#C8102E" };
const COLOR_METRO = { 1: "#38A3DC", 2: "#E2231A", 5: "#9BBF2B", 6: "#9AA0A6", 9: "#A3268E" };

function OpcionEspera({ o, elegida, recomendada, onElegir, modo }) {
  const activa = elegida.linea === o.linea;
  return (
    <button
      onClick={onElegir}
      aria-pressed={activa}
      className={`boton-pegatina flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left ${activa ? "bg-amarillo" : "bg-tarjeta"}`}
    >
      <span className="self-start pt-0.5">
        <Linea linea={o.linea} red={o.red} />
      </span>
      <span className="min-w-0 flex-1">
        <span className="block text-[17px] font-bold leading-snug text-tinta">
          {o.lejos ? "Demasiado lejos para estimar" : o.v ? `Pasa entre ${o.v.desde} y ${o.v.hasta} min` : "Sin datos suficientes"}
        </span>
        <span className="mt-0.5 block text-[14px] text-suave">
          {o.desde_parada ? `Desde ${o.desde_parada} · ` : ""}La app dice {o.minutos} min · viaje {o.aproximado ? "≈ " : ""}
          {o.viaje} min{o.andar_extra ? ` · +${o.andar_extra} min andando` : ""}
        </span>
        {o.incidencias?.enTramo.map((x) => (
          <span key={x.parada} className="mt-1.5 block rounded-lg border-2 border-[#111] bg-[#FFD9D6] px-2 py-1 text-[13px] font-bold text-[#7A0F0A]">
            En tu tramo: {x.texto.toLowerCase()} en {x.parada} · +{x.retraso} min
          </span>
        ))}
        {o.incidencias?.despues.map((x) => (
          <span key={x.parada} className="mt-1.5 block text-[13px] text-suave">
            Más adelante, en {x.parada}: {x.texto.toLowerCase()}. No te afecta.
          </span>
        ))}
        {(o.v || (o.r && o.r.nivel !== "linea")) && (
          <span className="mt-1.5 flex flex-wrap items-center gap-2">
            {o.v && <Etiqueta p={o.r.p} />}
            {recomendada.linea === o.linea && o.v && (
              <span className="rounded-md border-2 border-[#111] bg-verde px-1.5 text-[13px] font-bold text-white">
                {modo === "rapida" ? "LA MÁS RÁPIDA" : "LA MÁS SEGURA"}
              </span>
            )}
            {o.r && o.r.nivel !== "linea" && <span className="text-[13px] text-suave">estimación general de la red</span>}
          </span>
        )}
      </span>
    </button>
  );
}

// Tren visto desde arriba con el vagón donde conviene ponerse para el transbordo
function Vagones({ vagon, onCambiar }) {
  const posiciones = [
    { id: "cabeza", texto: "Cabeza" },
    { id: "centro", texto: "Centro" },
    { id: "cola", texto: "Cola" },
  ];
  const indice = { cabeza: [0, 1], centro: [2, 3], cola: [4, 5] }[vagon] ?? [];
  return (
    <div className="mt-2 rounded-xl border-2 border-[#111] bg-tarjeta p-3">
      <p className="text-[14px] font-bold text-tinta">
        Tu truco: ponte en {vagon === "cola" ? "el último vagón" : vagon === "cabeza" ? "el primer vagón" : "los vagones del centro"}
      </p>
      <div className="mt-2 flex items-center gap-1" role="img" aria-label={`Vagón recomendado: ${vagon}`}>
        <span className="text-[12px] font-bold text-suave">← sentido</span>
        {Array.from({ length: 6 }, (_, i) => (
          <span
            key={i}
            className={`h-[18px] flex-1 border-2 border-[#111] ${i === 0 ? "rounded-l-full" : ""} ${i === 5 ? "rounded-r-md" : "rounded-sm"} ${
              indice.includes(i) ? "bg-amarillo" : "bg-hundido"
            }`}
          />
        ))}
      </div>
      <div className="mt-2 flex gap-2" role="radiogroup" aria-label="Dónde te pones">
        {posiciones.map((p) => (
          <button
            key={p.id}
            role="radio"
            aria-checked={vagon === p.id}
            onClick={() => onCambiar(p.id)}
            className={`boton-pegatina min-h-[40px] flex-1 rounded-lg text-[14px] font-bold ${vagon === p.id ? "bg-amarillo" : "bg-tarjeta"}`}
          >
            {p.texto}
          </button>
        ))}
      </div>
    </div>
  );
}

function AvisoBajada({ activo, onCambiar, parada }) {
  return (
    <button
      onClick={onCambiar}
      aria-pressed={activo}
      className={`boton-pegatina mt-2 flex min-h-[44px] w-full items-center gap-2 rounded-xl px-3 text-left text-[14px] font-bold ${
        activo ? "bg-verde text-white" : "bg-tarjeta text-tinta"
      }`}
    >
      <IconoCampana className="h-5 w-5" />
      {activo ? `Te avisamos una parada antes de ${parada}` : `Avisarme antes de bajar en ${parada}`}
    </button>
  );
}

export function DetalleRuta({ ruta, datos, contexto, nombres, onRenombrar, onVolver, esPlan = false, demo = {} }) {
  const [elegidas, setElegidas] = useState({});
  const [modo, setModo] = useState("segura");
  const [llegar, setLlegar] = useState(ruta.llegar_antes ?? "9:00");
  const [vagones, setVagones] = useState(() => leerLocal("vagones", {}));
  const [avisos, setAvisos] = useState({});
  const calculo = useMemo(() => calcularRuta(datos, ruta, contexto, elegidas, modo, demo), [datos, ruta, contexto, elegidas, modo, demo]);
  const nombre = esPlan ? "La que te daría un planificador" : nombres[`ruta-${ruta.id}`] ?? ruta.nombre;
  const salida = horaDeSalida(calculo.total, llegar, modo);
  const ya = salirEn(calculo);

  function cambiarVagon(clave, v) {
    const nuevos = { ...vagones, [clave]: v };
    setVagones(nuevos);
    guardarLocal("vagones", nuevos);
  }

  return (
    <div className="space-y-4">
      <Volver texto="Rutas" onClick={onVolver} />
      {esPlan ? (
        <h1 className="titulo text-[26px] text-tinta">{nombre}</h1>
      ) : (
        <NombreEditable
          nombre={nombre}
          onCambiar={(n) => onRenombrar(`ruta-${ruta.id}`, n)}
          etiqueta={`Cambiar el nombre de la ruta ${nombre}`}
          className="titulo text-[28px] text-tinta"
        />
      )}

      {/* ¿cuándo salgo? */}
      <Tarjeta sombra className="!bg-amarillo p-4">
        <div className="flex flex-wrap items-center gap-2 text-[15px] font-bold">
          <span>Quiero llegar antes de las</span>
          <input
            type="time"
            value={llegar.padStart(5, "0")}
            onChange={(e) => setLlegar(e.target.value.replace(/^0/, ""))}
            className="pegatina h-[40px] rounded-lg bg-tarjeta px-2 text-[17px] font-bold"
            aria-label="Hora a la que quieres llegar"
          />
        </div>
        <p className="cifra mt-2 text-[34px] tabular-nums">{salida ? `Sal a las ${salida}` : "Sin datos suficientes"}</p>
        <p className="mt-1 text-[15px]">
          El viaje dura {texTotal(calculo.total)} · {calculo.transbordos === 1 ? "1 transbordo" : `${calculo.transbordos} transbordos`}
        </p>
        {modo === "rapida" && salida && (
          <p className="mt-2 inline-block rounded-md border-2 border-[#111] bg-rojo px-2 py-0.5 text-[14px] font-bold text-white">
            Arriesgado: solo llegas si todo va bien
          </p>
        )}
      </Tarjeta>

      {ya && (
        <Tarjeta className="flex items-center gap-3 p-4">
          <span className="pegatina flex h-[48px] w-[48px] shrink-0 items-center justify-center rounded-xl bg-aviso-simulado">
            <IconoReloj />
          </span>
          <p className="text-[16px] font-bold text-tinta">
            {ya.minutos > 0
              ? `Si sales ahora: sal de casa en ${ya.minutos} min para coger el ${ya.linea}`
              : ya.minutos === 0
                ? `¡Sal ya para coger el ${ya.linea}!`
                : `Al ${ya.linea} que viene ya no llegas: mira la siguiente opción`}
          </p>
        </Tarjeta>
      )}

      {/* modo «voy con prisa» */}
      <div className="grid grid-cols-2 gap-2" role="radiogroup" aria-label="Cómo quieres ir">
        {[
          { id: "segura", t: "Lo más seguro", s: "llega antes en el peor caso" },
          { id: "rapida", t: "Voy con prisa", s: "lo más rápido si todo va bien" },
        ].map((m) => (
          <button
            key={m.id}
            role="radio"
            aria-checked={modo === m.id}
            onClick={() => {
              setModo(m.id);
              setElegidas({});
            }}
            className={`boton-pegatina min-h-[60px] rounded-xl px-3 py-2 text-left ${modo === m.id ? "bg-principal text-white" : "bg-tarjeta text-tinta"}`}
          >
            <span className="block text-[16px] font-bold">{m.t}</span>
            <span className={`block text-[13px] ${modo === m.id ? "text-white/85" : "text-suave"}`}>{m.s}</span>
          </button>
        ))}
      </div>

      <Tarjeta className="p-4">
        <Hito texto={ruta.desde ?? "Salida"} sub="Salida" />
        {calculo.tramos.map((t, i) => {
          if (t.tipo === "andar" || t.tipo === "transbordo") {
            const clave = `${ruta.id}-${i}`;
            return (
              <Paso key={i} punteado>
                <div
                  className={`mt-2 flex items-center gap-2 rounded-xl px-3 py-2 ${t.tipo === "transbordo" ? "pegatina bg-aviso-simulado" : "bg-hundido"}`}
                >
                  {t.tipo === "transbordo" ? <IconoTransbordo /> : <IconoAndar />}
                  <span className="text-[15px] font-bold text-tinta">{t.texto}</span>
                  <span className="ml-auto shrink-0 text-[14px] text-tinta-2">{t.minutos} min</span>
                </div>
                {t.tipo === "transbordo" && t.vagon && (
                  <Vagones vagon={vagones[clave] ?? t.vagon} onCambiar={(v) => cambiarVagon(clave, v)} />
                )}
              </Paso>
            );
          }
          const metro = t.tipo === "metro";
          const bajada = metro ? t.hasta : t.bajada ?? t.titulo;
          return (
            <div key={i}>
              {metro && calculo.tramos[i - 1]?.tipo !== "transbordo" && <Hito texto={`Metro ${t.desde}`} />}
              <Paso color={metro ? COLOR_METRO[t.linea] ?? "#3A4558" : COLOR_TRAMO[t.elegida.red]}>
                <div className="space-y-2 pt-1">
                  {metro ? (
                    <div className="flex items-center gap-2">
                      <Linea linea={t.linea} red="metro" grande />
                      <span className="text-[16px] font-bold text-tinta">Dirección {t.hasta}</span>
                    </div>
                  ) : (
                    <>
                      <p className="text-[16px] font-bold text-tinta">{t.titulo}</p>
                      {t.nota && <p className="text-[14px] text-suave">{t.nota}</p>}
                    </>
                  )}
                  {t.opciones.map((o) => (
                    <OpcionEspera
                      key={o.linea}
                      o={o}
                      elegida={t.elegida}
                      recomendada={t.recomendada}
                      modo={modo}
                      onElegir={() => setElegidas((e) => ({ ...e, [i]: o.linea }))}
                    />
                  ))}
                  {metro && t.paradas.length > 0 && (
                    <details className="text-[14px] text-tinta-2">
                      <summary className="min-h-[36px] py-1.5">{t.paradas.length} paradas entre medias</summary>
                      <p>{t.paradas.join(" · ")}</p>
                    </details>
                  )}
                  <AvisoBajada activo={!!avisos[i]} onCambiar={() => setAvisos((a) => ({ ...a, [i]: !a[i] }))} parada={bajada} />
                </div>
              </Paso>
              {metro && <Hito texto={`Metro ${t.hasta}`} />}
            </div>
          );
        })}
        <Hito texto={ruta.hasta ?? "Llegada"} sub="Llegada" final />
      </Tarjeta>

      <p className="text-[14px] text-suave">
        {ruta.ejemplo || esPlan ? "Ruta de ejemplo. " : ""}Las esperas salen de los datos medidos; los minutos que dice la app son
        de demostración. El aviso al bajar es una simulación.
      </p>
    </div>
  );
}
