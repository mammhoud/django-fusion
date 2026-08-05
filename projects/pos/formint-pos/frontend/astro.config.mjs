import { defineConfig } from 'astro/config';
import alpine from '@astrojs/alpinejs';
import { fileURLToPath } from 'node:url';

export default defineConfig({
  integrations: [alpine()],
  vite: {
    server: {
      proxy: {
        '/htmx': 'http://127.0.0.1:8767',
        '/fusion': 'http://127.0.0.1:8767',
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
