// @ts-check
import { defineConfig } from 'astro/config';
import react from '@astrojs/react';
import tailwindcss from '@tailwindcss/vite';
import { fileURLToPath } from 'node:url';

// Tauri sets TAURI_DEV_HOST to expose the dev server on the local network
// (e.g. mobile devices). Falls back to localhost-only, mirroring the old
// vite.config.ts.
const host = process.env.TAURI_DEV_HOST;

export default defineConfig({
  // Static output — the desktop app loads plain HTML pages from disk.
  output: 'static',

  // Tauri expects a fixed dev port; fail fast if it is unavailable.
  server: {
    port: 1420,
    strictPort: true,
    host: host || false,
  },

  // Same public folder the old Vite config used (Logo.svg, bg-texture.svg…).
  publicDir: './assets/public',

  vite: {
    plugins: [tailwindcss()],
    optimizeDeps: {
      // Astro's default scan glob (`src/**/*.{jsx,tsx,…}`) pulls `src/test/**`
      // files into the app's dependency optimizer. Test files import
      // `MemoryRouter` from react-router-dom, which this app aliases to the
      // MPA shim (no MemoryRouter export) — that crashes the esbuild scan and
      // kills `pnpm dev` / `pnpm tauri dev` on a fresh `.vite` cache. Restrict
      // the scan to real app sources.
      entries: [
        './src/**/*.{jsx,tsx,vue,svelte,html,astro}',
        '!**/test/**',
        '!**/*.test.{ts,tsx}',
      ],
    },
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
        // formintA now navigates through Astro's file-based routing — every
        // navigation is a full page load. The app components were written
        // against react-router hooks; this alias maps `react-router-dom` to a
        // thin MPA shim so pages keep working without rewrites. Tests still
        // resolve the real package (vitest.config.ts has no alias).
        'react-router-dom': fileURLToPath(
          new URL('./src/lib/reactRouterShim.tsx', import.meta.url),
        ),
      },
    },
    server: {
      watch: {
        // Don't watch the Rust backend while developing the frontend.
        ignored: ['**/src-tauri/**'],
      },
    },
  },

  integrations: [react()],
});
