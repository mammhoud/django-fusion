// @ts-check
import { defineConfig } from 'astro/config';
import react from '@astrojs/react';
import tailwindcss from '@tailwindcss/vite';
import { fileURLToPath } from 'node:url';

// POS Cloud frontend (formintA Community UI + pos-cloud data layer).
// The sidecar (Robyn, :8767) owns the REST APIs; the Django backend
// (:8082) owns /admin and the fusion-render road. Both are proxied in dev
// so cookies/session stay on one host, mirroring formintC's proxy pattern.
const SIDECAR = process.env.SIDECAR_URL || 'http://127.0.0.1:8767';
const BACKEND = process.env.BACKEND_URL || 'http://127.0.0.1:8082';

export default defineConfig({
  output: 'static',

  server: {
    port: 4323,
    host: true,
  },

  // Same public folder the formintA Vite config used (Logo.svg, …).
  publicDir: './assets/public',

  vite: {
    plugins: [tailwindcss()],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
        // The app components were written against react-router hooks; this
        // alias maps `react-router-dom` to a thin MPA shim so pages keep
        // working without rewrites.
        'react-router-dom': fileURLToPath(
          new URL('./src/lib/reactRouterShim.tsx', import.meta.url),
        ),
      },
    },
    server: {
      proxy: {
        // Sidecar REST + fusion API (Robyn, pos-cloud Django ORM)
        '/health': { target: SIDECAR, changeOrigin: true },
        '/stats': { target: SIDECAR, changeOrigin: true },
        '/organizations': { target: SIDECAR, changeOrigin: true },
        '/branches': { target: SIDECAR, changeOrigin: true },
        '/leads': { target: SIDECAR, changeOrigin: true },
        '/contacts': { target: SIDECAR, changeOrigin: true },
        '/deals': { target: SIDECAR, changeOrigin: true },
        '/inventory-reports': { target: SIDECAR, changeOrigin: true },
        '/branch-reports': { target: SIDECAR, changeOrigin: true },
        '/device-tokens': { target: SIDECAR, changeOrigin: true },
        '/conflicts': { target: SIDECAR, changeOrigin: true },
        '/queue': { target: SIDECAR, changeOrigin: true },
        '/fusion': { target: SIDECAR, changeOrigin: true },
        // Django backend (admin + fusion-render road)
        '/admin': { target: BACKEND, changeOrigin: true },
        '/static': { target: BACKEND, changeOrigin: true },
        '/media': { target: BACKEND, changeOrigin: true },
        '/apis': { target: BACKEND, changeOrigin: true },
        '/api': { target: SIDECAR, changeOrigin: true },
      },
    },
  },

  integrations: [react()],
});
