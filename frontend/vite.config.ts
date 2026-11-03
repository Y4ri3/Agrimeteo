/// <reference types="vitest/config" />
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// En dev, /api est relayé vers le backend local ; en conteneur, c'est nginx qui le fait.
export default defineConfig({
  plugins: [react()],
  server: { proxy: { "/api": process.env.API_PROXY ?? "http://localhost:8000" } },
  test: { environment: "jsdom", globals: true, setupFiles: ["tests/setup.ts"] },
});
