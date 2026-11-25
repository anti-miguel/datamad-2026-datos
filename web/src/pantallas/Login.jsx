// Pantalla de entrada de la demo. La web no tiene servidor: la cuenta se comprueba en el navegador
// y solo sirve para enseñar la app personalizada (no protege nada). Las credenciales van a la vista, abajo.
import { useState } from "react";
import { Logo } from "../componentes/Logo.jsx";
import { EscenaBus } from "../componentes/Escena.jsx";

export const CUENTA_DEMO = { correo: "demo@yavoy.app", clave: "yavoy2026", nombre: "Alejandro" };

export default function Login({ onEntrar }) {
  const [correo, setCorreo] = useState("");
  const [clave, setClave] = useState("");
  const [verClave, setVerClave] = useState(false);
  const [error, setError] = useState("");

  function entrar(e) {
    e.preventDefault();
    if (!correo.trim() || !clave) {
      setError("Escribe tu correo y tu contraseña.");
      return;
    }
    if (correo.trim().toLowerCase() === CUENTA_DEMO.correo && clave === CUENTA_DEMO.clave) {
      onEntrar({ correo: CUENTA_DEMO.correo, nombre: CUENTA_DEMO.nombre });
    } else {
      setError("El correo o la contraseña no son correctos.");
    }
  }

  return (
    <div className="mx-auto flex min-h-dvh max-w-[430px] flex-col px-4 pb-6">
      <div className="-mt-0">
        <EscenaBus />
      </div>

      <div className="mt-6 flex flex-col items-center text-center">
        <Logo alto={52} lema />
      </div>

      <form onSubmit={entrar} className="pegatina-grande mt-8 space-y-4 rounded-2xl bg-tarjeta p-5" noValidate>
        <h1 className="titulo text-[24px] text-tinta">Entra en tu cuenta</h1>

        <label className="block">
          <span className="text-[15px] font-bold text-tinta">Correo</span>
          <input
            type="email"
            autoComplete="email"
            value={correo}
            onChange={(e) => {
              setCorreo(e.target.value);
              setError("");
            }}
            placeholder="tu@correo.com"
            className="pegatina mt-1 h-[50px] w-full rounded-xl bg-tarjeta px-3 text-[16px] placeholder:text-suave"
          />
        </label>

        <label className="block">
          <span className="text-[15px] font-bold text-tinta">Contraseña</span>
          <span className="pegatina mt-1 flex h-[50px] items-center rounded-xl bg-tarjeta pr-1">
            <input
              type={verClave ? "text" : "password"}
              autoComplete="current-password"
              value={clave}
              onChange={(e) => {
                setClave(e.target.value);
                setError("");
              }}
              placeholder="Tu contraseña"
              className="h-full min-w-0 flex-1 bg-transparent px-3 text-[16px] placeholder:text-suave"
            />
            <button
              type="button"
              onClick={() => setVerClave((v) => !v)}
              className="min-h-[42px] rounded-lg px-3 text-[14px] font-bold text-principal"
              aria-label={verClave ? "Ocultar contraseña" : "Mostrar contraseña"}
            >
              {verClave ? "Ocultar" : "Ver"}
            </button>
          </span>
        </label>

        {error && (
          <p role="alert" className="rounded-xl border-2 border-[#111] bg-[#FFD9D6] px-3 py-2 text-[15px] font-bold text-[#7A0F0A]">
            {error}
          </p>
        )}

        <button type="submit" className="boton-pegatina min-h-[52px] w-full rounded-xl bg-principal text-[18px] font-bold text-white">
          Entrar
        </button>
      </form>

      {/* cuenta de demostración, a la vista para el jurado */}
      <div className="pegatina mt-6 rounded-2xl bg-amarillo p-4">
        <p className="text-[14px] font-bold uppercase tracking-wide">Cuenta de demostración</p>
        <dl className="mt-2 grid grid-cols-[auto_1fr] gap-x-3 gap-y-1 text-[16px]">
          <dt className="font-bold">Correo</dt>
          <dd className="break-all font-mono">{CUENTA_DEMO.correo}</dd>
          <dt className="font-bold">Contraseña</dt>
          <dd className="font-mono">{CUENTA_DEMO.clave}</dd>
        </dl>
        <button
          type="button"
          onClick={() => {
            setCorreo(CUENTA_DEMO.correo);
            setClave(CUENTA_DEMO.clave);
            setError("");
          }}
          className="boton-pegatina mt-3 min-h-[44px] w-full rounded-xl bg-tarjeta text-[16px] font-bold"
        >
          Usar estas credenciales
        </button>
      </div>
    </div>
  );
}
