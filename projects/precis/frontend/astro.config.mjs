import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import mdx from '@astrojs/mdx';
import { fileURLToPath } from 'node:url';
import { readFileSync, existsSync } from 'node:fs';

import alpinejs from '@astrojs/alpinejs';

// ── Dependency-free .env loader ─────────────────────────────────────────────
// Shell env wins, then .env.local, then .env (see .env.example).
const __env = {};
for (const __f of ['.env.local', '.env']) {
  if (!existsSync(__f)) continue;
  for (const __line of readFileSync(__f, 'utf8').split('\n')) {
    const __m = /^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$/.exec(__line);
    if (__m && !(__m[1] in __env)) __env[__m[1]] = __m[2].replace(/^['"]|['"]$/g, '');
  }
}
const envVal = (key, fallback) => process.env[key] ?? __env[key] ?? fallback;

/** Dev server port (default 3002). */
const PORT = Number(envVal('PORT', 3002));
/** Canonical site URL (SEO/sitemap). */
const siteUrl = envVal('PUBLIC_SITE_URL', 'https://ctc-research.com');

// https://astro.build/config
export default defineConfig({
  // Landing site is fully static — HTML + HTMX/Alpine only.
  // Switch to `output: 'server'` + @astrojs/node when porting
  // CMS-backed dynamic pages (see ASTRO_MIGRATION_PLAN §7).
  output: 'static',
  // Emit directory-style routes so links such as /products/ resolve directly
  // through static hosts and Django's APPEND_SLASH contract.
  trailingSlash: 'always',
  site: siteUrl,
  integrations: [
    mdx(),
    // Alpine with the Intersect + Collapse plugins (see src/alpine.js) —
    // without them x-intersect reveals and x-collapse accordions no-op.
    alpinejs({ entrypoint: '@/alpine' }),
  ],
  vite: {
    server: {
      allowedHosts: true,
    },
    preview: {
      allowedHosts: true,
    },
    resolve: {
      alias: {
        // Project-level assets (fonts, icons, theme styles) — used by Layout
        // and Header components via `import … from '@assets/static/…'`.
        '@assets/styles': new URL('../assets/styles', import.meta.url).pathname,
        '@assets/static': new URL('../assets/static', import.meta.url).pathname,
        // Shared fusion-js modular TS bundles (htmx wrapper, SSE, fragments,
        // scroll reveal, theme) — consumed via src/fusion/* project bindings.
        '@fusion': fileURLToPath(
          new URL('../../../libs/django-fusion/js/fusion-js/src', import.meta.url),
        ),
      },
    },
    plugins: [
      // Tailwind 4 uses the Vite plugin (CSS-first config), not @astrojs/tailwind.
      tailwindcss(),
    ],
  },
  server: { port: PORT, host: true },
  preview: { port: PORT },
});