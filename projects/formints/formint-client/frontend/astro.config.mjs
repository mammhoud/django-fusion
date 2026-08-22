import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import alpinejs from '@astrojs/alpinejs';
import { readFileSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

// ── Dependency-free .env loader ─────────────────────────────────────────────
// Shell env wins, then .env.local, then .env (see frontend/.env.example).
const __env = {};
for (const __f of ['.env.local', '.env']) {
  if (!existsSync(__f)) {
    continue;
  }
  for (const __line of readFileSync(__f, 'utf8').split('\n')) {
    const __m = /^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$/.exec(__line);
    if (__m && !(__m[1] in __env)) {
      __env[__m[1]] = __m[2].replace(/^['"]|['"]$/g, '');
    }
  }
}
const envVal = (key, fallback) => process.env[key] ?? __env[key] ?? fallback;

/** Dev server port (default 4322). */
const PORT = Number(envVal('PORT', 4322));
/** Django backend origin for the dev proxy (default :8075). */
const BACKEND = envVal('BACKEND_URL', 'http://localhost:8075');
/** Canonical site URL (SEO). */
const SITE_URL = envVal('PUBLIC_SITE_URL', 'http://localhost:4322');
// Shared assets are available for future shell surfaces; Client keeps its
// own storefront favicon and Fontsource bundle as edition-specific overlays.
const SHARED_ASSETS = fileURLToPath(new URL('../../assets/shared', import.meta.url));

// https://astro.build/config
export default defineConfig({
  output: 'static',
  site: SITE_URL,
  integrations: [
    // Alpine with the Intersect + Collapse plugins (see src/alpine.js)
    alpinejs({ entrypoint: '@/alpine' }),
  ],
  vite: {
    plugins: [tailwindcss()],
    resolve: {
      alias: {
        '@formints-assets': SHARED_ASSETS,
      },
    },
    server: {
      fs: { allow: [SHARED_ASSETS] },
      proxy: {
        // Auth + shop + employee are owned by the Django backend (:8075).
        // The Astro dev server proxies every backend route so the AHA
        // storefront reads session + CSRF cookies on the same host.
        '/accounts': { target: BACKEND, changeOrigin: true },
        '/api': { target: BACKEND, changeOrigin: true },
        '/apis': { target: BACKEND, changeOrigin: true },
        '/shop': { target: BACKEND, changeOrigin: true },
        '/employee': { target: BACKEND, changeOrigin: true },
        '/checkout': { target: BACKEND, changeOrigin: true },
        '/orders': { target: BACKEND, changeOrigin: true },
        // django-fusion render-mode / navigation / assets / session-mode
        '/fusion': { target: BACKEND, changeOrigin: true },
        '/static': { target: BACKEND, changeOrigin: true },
        '/media': { target: BACKEND, changeOrigin: true },
        '/django-admin': { target: BACKEND, changeOrigin: true },
      },
    },
  },
  server: { port: PORT, host: true },
});
