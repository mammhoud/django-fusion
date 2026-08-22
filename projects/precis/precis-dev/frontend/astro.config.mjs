import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import mdx from '@astrojs/mdx';
import { fileURLToPath } from 'node:url';
import { readFileSync, existsSync } from 'node:fs';

import alpinejs from '@astrojs/alpinejs';

// ── Dependency-free .env loader ─────────────────────────────────────────────
// Astro/Vite do not reliably expose .env values to config files on every
// install layout, so read them here explicitly (shell env wins, then
// .env.local, then .env). Keeps port/URLs overridable via one frontend/.env
// (see .env.example).
const __env = {};
for (const __f of ['.env.local', '.env']) {
  if (!existsSync(__f)) continue;
  for (const __line of readFileSync(__f, 'utf8').split('\n')) {
    const __m = /^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$/.exec(__line);
    if (__m && !(__m[1] in __env)) __env[__m[1]] = __m[2].replace(/^['"]|['"]$/g, '');
  }
}
const envVal = (key, fallback) => process.env[key] ?? __env[key] ?? fallback;

/** Dev server port (default 3000). */
const PORT = Number(envVal('PORT', 3000));
/** Django backend origin for the dev proxy (default :8074). */
const BACKEND_URL = envVal('BACKEND_URL', 'http://127.0.0.1:8074');
/** Canonical site URL (SEO/sitemap). */
const SITE_URL = envVal('PUBLIC_SITE_URL', 'https://dev.structa.cloud');

// https://astro.build/config
export default defineConfig({
  // Landing site is fully static — HTML + HTMX/Alpine only.
  // Switch to `output: 'server'` + @astrojs/node when porting
  // CMS-backed dynamic pages (see ASTRO_MIGRATION_PLAN §7).
  output: 'static',
  site: SITE_URL,
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
        // Shared fusion-js modular TS bundles (htmx wrapper, SSE, fragments,
        // scroll reveal, theme) — consumed via src/fusion/* project bindings.
        '@fusion': fileURLToPath(
          new URL('../../../../libs/django-fusion/js/fusion-js/src', import.meta.url),
        ),
        // Shared django-fusion TEMPLATES — the single source of truth for
        // cross-road UI partials (brand_modal.html etc.). Imported raw
        // (?raw) so the Astro road renders the exact same markup the Django
        // road {% include %}s — they can never drift. NOTE: Django template
        // tags ({%% %}) would be emitted literally here, so these partials
        // must stay tag-free (HTML comments only).
        '@fusion-templates': fileURLToPath(
          new URL('../../../../libs/django-fusion/src/django_fusion/templates', import.meta.url),
        ),
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
        '/accounts': { target: BACKEND_URL, changeOrigin: true },
        '/apis': { target: BACKEND_URL, changeOrigin: true },
        '/fragment': { target: BACKEND_URL, changeOrigin: true },
        '/api': { target: BACKEND_URL, changeOrigin: true },
        '/admin': { target: BACKEND_URL, changeOrigin: true },
        '/static': { target: BACKEND_URL, changeOrigin: true },
        '/media': { target: BACKEND_URL, changeOrigin: true },
        '/learning': { target: BACKEND_URL, changeOrigin: true },
      },
    },
  },
  server: { port: PORT, host: true },
});
