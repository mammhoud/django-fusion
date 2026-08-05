import { defineConfig } from 'astro/config';
import alpine from '@astrojs/alpinejs';
import { fileURLToPath } from 'node:url';

export default defineConfig({
  integrations: [alpine()],
  vite: {
    server: {
      proxy: {
        '/htmx': 'http://127.0.0.1:8767',
        // Narrowed to concrete sidecar paths — a bare '/fusion' prefix would
        // shadow the Astro page route at /fusion/ (Vite proxy runs before the
        // page router in dev mode).
        '/fusion/page/': 'http://127.0.0.1:8767',
        '/fusion/pointer/': 'http://127.0.0.1:8767',
        '/fusion/session-mode/': 'http://127.0.0.1:8767',
        '/fusion/render-mode/': 'http://127.0.0.1:8767',
        '/fusion/navigation/': 'http://127.0.0.1:8767',
        '/fusion/assets/': 'http://127.0.0.1:8767',
        '/fusion/health/': 'http://127.0.0.1:8767',
        '/fusion/branding/': 'http://127.0.0.1:8767',
        '/fusion/layouts/': 'http://127.0.0.1:8767',
        '/fusion/branches/summary/': 'http://127.0.0.1:8767',
        '/api': 'http://127.0.0.1:8767',
      },
    },
    resolve: {
      alias: {
        '@assets': fileURLToPath(new URL('../assets', import.meta.url)),
      },
    },
  },
});
