// @ts-check
import { defineConfig } from 'astro/config';
import react from '@astrojs/react';
import tailwindcss from '@tailwindcss/vite';
import { fileURLToPath } from 'node:url';
import { readFileSync, existsSync } from 'node:fs';

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

// Tauri sets TAURI_DEV_HOST to expose the dev server on the local network
// (e.g. mobile devices). Falls back to localhost-only, mirroring the old
// vite.config.ts.
const host = process.env.TAURI_DEV_HOST;

/** Dev server port — keep 1420 for Tauri (tauri.conf.json devUrl is fixed). */
const PORT = Number(envVal('PORT', 1420));

export default defineConfig({
  // Static output — the desktop app loads plain HTML pages from disk.
  output: 'static',

  // Tauri expects a fixed dev port; fail fast if it is unavailable.
  server: {
    port: PORT,
    strictPort: true,
    host: host || false,
  },

  // Same public folder the old Vite config used (Logo.svg, bg-texture.svg…).
  publicDir: './assets/public',

  vite: {
    plugins: [tailwindcss()],
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
