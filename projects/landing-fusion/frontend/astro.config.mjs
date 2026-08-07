import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import mdx from '@astrojs/mdx';

import alpinejs from '@astrojs/alpinejs';

// https://astro.build/config
export default defineConfig({
  // Landing site is fully static — HTML + HTMX/Alpine only.
  // Switch to `output: 'server'` + @astrojs/node when porting
  // CMS-backed dynamic pages (see ASTRO_MIGRATION_PLAN §7).
  output: 'static',
  site: 'https://landing.structa.cloud',
  integrations: [
    mdx(),
    // Alpine with the Intersect + Collapse plugins (see src/alpine.js) —
    // without them x-intersect reveals and x-collapse accordions no-op.
    alpinejs({ entrypoint: '@/alpine' }),
  ],
  vite: {
    resolve: {
      alias: {
        // Project-level assets (images, fonts, icons) downloadable via import
        '@assets/images': new URL('../assets/images', import.meta.url).pathname,
        '@assets/styles': new URL('../assets/styles', import.meta.url).pathname,
        '@assets/static': new URL('../assets/static', import.meta.url).pathname,
      },
    },
    plugins: [
      // Tailwind 4 uses the Vite plugin (CSS-first config), not @astrojs/tailwind.
      tailwindcss(),
    ],
    // Dev proxy — auth is owned by the Django backend, not by Astro. Every
    // allauth page (/accounts/*), the headless API (/api/auth/*, newsletter),
    // the Wagtail admin (/admin/*), and Django static/media are served from
    // :8074 through the Astro dev server, so the frontend road renders the
    // SAME branded auth pages (same design tokens, Alpine/HTMX behaviors,
    // session + CSRF cookies on the localhost host) and both roads feel
    // identical. Dev-only: `astro build` stays fully static — production
    // nginx proxies these paths to the backend instead.
    server: {
      proxy: {
        '/accounts': { target: 'http://127.0.0.1:8074', changeOrigin: true },
        '/apis': { target: 'http://127.0.0.1:8074', changeOrigin: true },
        '/fragment': { target: 'http://127.0.0.1:8074', changeOrigin: true },
        '/api': { target: 'http://127.0.0.1:8074', changeOrigin: true },
        '/admin': { target: 'http://127.0.0.1:8074', changeOrigin: true },
        '/static': { target: 'http://127.0.0.1:8074', changeOrigin: true },
        '/media': { target: 'http://127.0.0.1:8074', changeOrigin: true },
        '/learning': { target: 'http://127.0.0.1:8074', changeOrigin: true },
      },
    },
  },
  server: { port: 3000, host: true },
});
