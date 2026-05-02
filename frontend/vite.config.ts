import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const devHost = process.env.VITE_HOST ?? "0.0.0.0";

export default defineConfig({
  clearScreen: false,
  plugins: [react()],
  server: {
    host: devHost,
    port: 1420,
    strictPort: true,
    watch: {
      ignored: ["**/src-tauri/**"],
    },
  },
  preview: {
    host: devHost,
    port: 1420,
    strictPort: true,
  },
});
