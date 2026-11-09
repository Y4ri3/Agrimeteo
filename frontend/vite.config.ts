/// <reference types="vitest/config" />
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// En dev, /api est relayé vers le backend local ; en conteneur, c'est nginx qui le fait.
export default defineConfig({
  plugins: [react()],
  server: { proxy: { "/api": process.env.API_PROXY ?? "http://localhost:8000" } },
  // Dans jsdom, fetch exige une URL absolue : les tests visent une API simulée par MSW (FE-05).
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["tests/setup.ts"],
    env: { VITE_API_BASE: "http://api.test/api" },
  },
});
