// Copia la tabla de fiabilidad y su consulta desde ../demo, para que sean siempre idénticas (manual, sección 1.1)
import { copyFileSync, mkdirSync } from "node:fs";
mkdirSync("public/datos", { recursive: true });
copyFileSync("../demo/fiabilidad.json", "public/datos/fiabilidad.json");
copyFileSync("../demo/consultar.js", "src/lib/consultar.js");
