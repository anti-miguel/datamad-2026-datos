import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// base relativa: funciona igual en Vercel, en GitHub Pages o en una subcarpeta
export default defineConfig({
  base: "./",
  plugins: [react(), tailwindcss()],
});
