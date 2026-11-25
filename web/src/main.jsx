import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
// Overpass en woff2 normal (Safari no siempre acepta la variable): solo los pesos que se usan, en latín
import "@fontsource/overpass/latin-400.css";
import "@fontsource/overpass/latin-700.css";
import "@fontsource/overpass/latin-800.css";
import "@fontsource/overpass/latin-900.css";
// Letra de los títulos y las cifras grandes
import "@fontsource/bricolage-grotesque/latin-700.css";
import "@fontsource/bricolage-grotesque/latin-800.css";
import "./index.css";
import App from "./App.jsx";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
