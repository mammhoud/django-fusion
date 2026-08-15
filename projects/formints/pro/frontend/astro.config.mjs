import { defineConfig } from 'astro/config';
import alpine from '@astrojs/alpinejs';
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

/** Dev server port (default 4321). */
const PORT = Number(envVal('PORT', 4321));
/** Django ASGI backend origin for the dev proxy (default :8766). */
const BACKEND = envVal('BACKEND_URL', 'http://localhost:8766');

export default defineConfig({
  integrations: [alpine()],
  server: { port: PORT, host: true },
  vite: {
    plugins: [tailwindcss()],
    server: {
      proxy: {
        // ── ASGI backend (Daphne/uvicorn on 8766, was Robyn on 8767) ──
        '/htmx': BACKEND,
        // Narrowed to concrete server paths — a bare '/fusion' prefix would
        // shadow the Astro page route at /fusion/ (Vite proxy runs before the
        // page router in dev mode).
        '/fusion/page/': BACKEND,
        '/fusion/pointer/': BACKEND,
        '/fusion/session-mode/': BACKEND,
        '/fusion/render-mode/': BACKEND,
        '/fusion/navigation/': BACKEND,
        '/fusion/assets/': BACKEND,
        '/fusion/health/': BACKEND,
        '/fusion/branding/': BACKEND,
        '/fusion/layouts/': BACKEND,
        '/fusion/branches/summary/': BACKEND,
        '/api': BACKEND,
        // POS data endpoints (HTMX fragments + checkout from server).
        // NOTE: no '/pos/' proxy — the server registers no /pos/* routes, and a
        // bare prefix would shadow the Astro pages at /pos/* (see /crm/ bypass).
        '/sales/': BACKEND,
        '/kds/': BACKEND,
        '/nodes/': BACKEND,
        '/events': BACKEND,
        '/sync/': BACKEND,
        '/api-keys/': BACKEND,
        '/transactions': BACKEND,
        '/analytics': BACKEND,
        '/approvals/': BACKEND,
        '/webhooks/': BACKEND,
        // /crm/<page>/ navigations are Astro pages (Accept: text/html); only
        // API fetches (Accept: */* or application/json) reach the server.
        // Without the bypass, the bare prefix shadows every /crm/* page in dev.
        '/crm/': {
          target: BACKEND,
          bypass(req) {
            if ((req.headers.accept || '').includes('text/html')) return req.url;
          },
        },
        '/reports/': BACKEND,
        '/config/': BACKEND,
        // Same page/API split as /crm/ — /ops/<page>/ is an Astro route.
        '/ops/': {
          target: BACKEND,
          bypass(req) {
            if ((req.headers.accept || '').includes('text/html')) return req.url;
          },
        },
        '/coupons/': BACKEND,
        '/delivery-types/': BACKEND,
        '/delivery-zones/': BACKEND,
        '/shifts/': BACKEND,
        // Server model CRUD endpoints (used by Astro form modals)
        '/products/': BACKEND,
        '/customers/': BACKEND,
        '/inventory/': BACKEND,
        '/employees/': BACKEND,
        '/categories/': BACKEND,
        // Barcode scanner resolution (GET /barcode/<value> → product JSON)
        '/barcode/': BACKEND,
        // ── WebSocket → Django Channels (ASGI server) ──
        '/ws': {
          target: BACKEND.replace(/^http/, 'ws'),
          ws: true,
        },
      },
    },
    resolve: {
      alias: {
        '@assets': fileURLToPath(new URL('../assets', import.meta.url)),
        '@styles': fileURLToPath(new URL('./src/styles', import.meta.url)),
      },
    },
  },
});
