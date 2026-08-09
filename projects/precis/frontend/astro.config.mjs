import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import mdx from '@astrojs/mdx';
import { fileURLToPath } from 'node:url';

import alpinejs from '@astrojs/alpinejs';

const siteUrl = process.env.PUBLIC_SITE_URL || 'https://ctc-research.com';

// https://astro.build/config
export default defineConfig({
  // Landing site is fully static — HTML + HTMX/Alpine only.
  // Switch to `output: 'server'` + @astrojs/node when porting
  // CMS-backed dynamic pages (see ASTRO_MIGRATION_PLAN §7).
  output: 'static',
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
  server: { port: 3002 },
});