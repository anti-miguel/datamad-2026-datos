// Copia la tabla de fiabilidad y su consulta desde ../demo, para que sean siempre idénticas (manual, sección 1.1).
// En el repositorio de la app no existe ../demo: ahí se usan las copias que ya van dentro de web/.
import { copyFileSync, existsSync, mkdirSync } from "node:fs";
if (existsSync("../demo/fiabilidad.json")) {
  mkdirSync("public/datos", { recursive: true });
  copyFileSync("../demo/fiabilidad.json", "public/datos/fiabilidad.json");
  copyFileSync("../demo/consultar.js", "src/lib/consultar.js");
} else {
  console.log("Sin ../demo: se usan public/datos/fiabilidad.json y src/lib/consultar.js tal como están");
}
