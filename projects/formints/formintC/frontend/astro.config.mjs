import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import alpinejs from '@astrojs/alpinejs';

// https://astro.build/config
export default defineConfig({
  output: 'static',
  site: 'http://localhost:4322',
  integrations: [
    // Alpine with the Intersect + Collapse plugins (see src/alpine.js)
    alpinejs({ entrypoint: '@/alpine' }),
  ],
  vite: {
    plugins: [tailwindcss()],
    server: {
      proxy: {
        // Auth + shop + employee are owned by the Django backend (:8075).
        // The Astro dev server proxies every backend route so the AHA
        // storefront reads session + CSRF cookies on the same host.
        '/accounts': { target: 'http://127.0.0.1:8075', changeOrigin: true },
        '/api': { target: 'http://127.0.0.1:8075', changeOrigin: true },
        '/apis': { target: 'http://127.0.0.1:8075', changeOrigin: true },
        '/shop': { target: 'http://127.0.0.1:8075', changeOrigin: true },
        '/employee': { target: 'http://127.0.0.1:8075', changeOrigin: true },
        '/checkout': { target: 'http://127.0.0.1:8075', changeOrigin: true },
        '/orders': { target: 'http://127.0.0.1:8075', changeOrigin: true },
        '/static': { target: 'http://127.0.0.1:8075', changeOrigin: true },
        '/media': { target: 'http://127.0.0.1:8075', changeOrigin: true },
        '/django-admin': { target: 'http://127.0.0.1:8075', changeOrigin: true },
      },
    },
  },
  server: { port: 4322, host: true },
});
