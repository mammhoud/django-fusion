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
  },
  server: { port: 3000 },
});