import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const backendPort = process.env.VITE_BACKEND_PORT || "8000";

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    proxy: {
      "/api": `http://localhost:${backendPort}`,
    },
  },
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: "./src/test/setup.js",
    css: true,
  },
});
