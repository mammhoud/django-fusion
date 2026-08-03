import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import mdx from '@astrojs/mdx';

// https://astro.build/config
export default defineConfig({
  // Landing site is fully static — HTML + HTMX/Alpine only.
  // Switch to `output: 'server'` + @astrojs/node when porting
  // CMS-backed dynamic pages (see ASTRO_MIGRATION_PLAN §7).
  output: 'static',
  site: 'https://landing.structa.cloud',
  integrations: [mdx()],
  vite: {
    plugins: [
      // Tailwind 4 uses the Vite plugin (CSS-first config), not @astrojs/tailwind.
      tailwindcss(),
    ],
  },
  server: { port: 3000 },
});
