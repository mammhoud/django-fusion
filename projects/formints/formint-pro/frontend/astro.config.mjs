import { defineConfig } from 'astro/config';
import alpine from '@astrojs/alpinejs';
import tailwindcss from '@tailwindcss/vite';
import { fileURLToPath } from 'node:url';

export default defineConfig({
  integrations: [alpine()],
  vite: {
    plugins: [tailwindcss()],
    server: {
      proxy: {
        // ── ASGI backend (Daphne/uvicorn on 8766, was Robyn on 8767) ──
        '/htmx': 'http://127.0.0.1:8766',
        // Narrowed to concrete sidecar paths — a bare '/fusion' prefix would
        // shadow the Astro page route at /fusion/ (Vite proxy runs before the
        // page router in dev mode).
        '/fusion/page/': 'http://127.0.0.1:8766',
        '/fusion/pointer/': 'http://127.0.0.1:8766',
        '/fusion/session-mode/': 'http://127.0.0.1:8766',
        '/fusion/render-mode/': 'http://127.0.0.1:8766',
        '/fusion/navigation/': 'http://127.0.0.1:8766',
        '/fusion/assets/': 'http://127.0.0.1:8766',
        '/fusion/health/': 'http://127.0.0.1:8766',
        '/fusion/branding/': 'http://127.0.0.1:8766',
        '/fusion/layouts/': 'http://127.0.0.1:8766',
        '/fusion/branches/summary/': 'http://127.0.0.1:8766',
        '/api': 'http://127.0.0.1:8766',
        // POS data endpoints (HTMX fragments + checkout from sidecar).
        // NOTE: no '/pos/' proxy — the sidecar registers no /pos/* routes, and a
        // bare prefix would shadow the Astro pages at /pos/* (see /crm/ bypass).
        '/sales/': 'http://127.0.0.1:8766',
        '/kds/': 'http://127.0.0.1:8766',
        '/nodes/': 'http://127.0.0.1:8766',
        '/events': 'http://127.0.0.1:8766',
        '/sync/': 'http://127.0.0.1:8766',
        '/api-keys/': 'http://127.0.0.1:8766',
        '/transactions': 'http://127.0.0.1:8766',
        '/analytics': 'http://127.0.0.1:8766',
        '/approvals/': 'http://127.0.0.1:8766',
        '/webhooks/': 'http://127.0.0.1:8766',
        // /crm/<page>/ navigations are Astro pages (Accept: text/html); only
        // API fetches (Accept: */* or application/json) reach the sidecar.
        // Without the bypass, the bare prefix shadows every /crm/* page in dev.
        '/crm/': {
          target: 'http://127.0.0.1:8766',
          bypass(req) {
            if ((req.headers.accept || '').includes('text/html')) return req.url;
          },
        },
        '/reports/': 'http://127.0.0.1:8766',
        '/config/': 'http://127.0.0.1:8766',
        // Same page/API split as /crm/ — /ops/<page>/ is an Astro route.
        '/ops/': {
          target: 'http://127.0.0.1:8766',
          bypass(req) {
            if ((req.headers.accept || '').includes('text/html')) return req.url;
          },
        },
        '/coupons/': 'http://127.0.0.1:8766',
        '/delivery-types/': 'http://127.0.0.1:8766',
        '/delivery-zones/': 'http://127.0.0.1:8766',
        '/shifts/': 'http://127.0.0.1:8766',
        // Sidecar model CRUD endpoints (used by Astro form modals)
        '/products/': 'http://127.0.0.1:8766',
        '/customers/': 'http://127.0.0.1:8766',
        '/inventory/': 'http://127.0.0.1:8766',
        '/employees/': 'http://127.0.0.1:8766',
        '/categories/': 'http://127.0.0.1:8766',
        // ── WebSocket → Django Channels (ASGI server) ──
        '/ws': {
          target: 'ws://127.0.0.1:8766',
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
