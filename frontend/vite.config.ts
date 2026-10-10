import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// During local development, /api requests are forwarded to FastAPI.
// Set VITE_API_BASE_URL for a deployed frontend with a different API domain.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
