// @ts-check
import { defineConfig } from 'astro/config';
import react from '@astrojs/react';
import tailwindcss from '@tailwindcss/vite';
import { fileURLToPath } from 'node:url';
import { readFileSync, existsSync } from 'node:fs';

// ── Dependency-free .env loader ─────────────────────────────────────────────
// Shell env wins, then .env.local, then .env (see frontend/.env.example).
const __env = {};
for (const __f of ['.env.local', '.env']) {
  if (!existsSync(__f)) continue;
  for (const __line of readFileSync(__f, 'utf8').split('\n')) {
    const __m = /^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$/.exec(__line);
    if (__m && !(__m[1] in __env)) __env[__m[1]] = __m[2].replace(/^['"]|['"]$/g, '');
  }
}
const envVal = (key, fallback) => process.env[key] ?? __env[key] ?? fallback;

// Formint Cloud frontend (Community UI + Cloud Django data layer).
// Django (:8767) owns the REST/API surface (server-compatible
// contract after the Robyn server was removed) and the admin/fusion road
// (:8082). Both are proxied in dev so cookies/session stay on one host.
const SERVER = envVal('SERVER_URL', 'http://127.0.0.1:8767');
const BACKEND = envVal('BACKEND_URL', 'http://127.0.0.1:8082');
const PORT = Number(envVal('PORT', 4323));

export default defineConfig({
  output: 'static',

  server: {
    port: PORT,
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
        // Server REST + fusion API (Django, Formint Cloud ORM)
        '/health': { target: SERVER, changeOrigin: true },
        '/stats': { target: SERVER, changeOrigin: true },
        '/organizations': { target: SERVER, changeOrigin: true },
        '/branches': { target: SERVER, changeOrigin: true },
        '/leads': { target: SERVER, changeOrigin: true },
        '/contacts': { target: SERVER, changeOrigin: true },
        '/deals': { target: SERVER, changeOrigin: true },
        '/inventory-reports': { target: SERVER, changeOrigin: true },
        '/branch-reports': { target: SERVER, changeOrigin: true },
        '/device-tokens': { target: SERVER, changeOrigin: true },
        '/conflicts': { target: SERVER, changeOrigin: true },
        '/queue': { target: SERVER, changeOrigin: true },
        '/monitor': { target: SERVER, changeOrigin: true },
        '/fusion': { target: SERVER, changeOrigin: true },
        // Django backend (admin + fusion-render road)
        '/admin': { target: BACKEND, changeOrigin: true },
        '/static': { target: BACKEND, changeOrigin: true },
        '/media': { target: BACKEND, changeOrigin: true },
        '/apis': { target: BACKEND, changeOrigin: true },
        '/api': { target: SERVER, changeOrigin: true },
      },
    },
  },

  integrations: [react()],
});
