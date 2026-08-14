import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import mdx from '@astrojs/mdx';
import alpinejs from '@astrojs/alpinejs';
import react from '@astrojs/react';
import { fileURLToPath } from 'node:url';
import { readFileSync, existsSync } from 'node:fs';

// ── Dependency-free .env loader (mirrors landing-fusion) ────────────────────
const __env = {};
for (const __f of ['.env.local', '.env']) {
  if (!existsSync(__f)) continue;
  for (const __line of readFileSync(__f, 'utf8').split('\n')) {
    const __m = /^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$/.exec(__line);
    if (__m && !(__m[1] in __env)) __env[__m[1]] = __m[2].replace(/^['"]|['"]$/g, '');
  }
}
const envVal = (key, fallback) => process.env[key] ?? __env[key] ?? fallback;

const PORT = Number(envVal('PORT', 4321));
const BACKEND_URL = envVal('BACKEND_URL', 'http://127.0.0.1:8000');
const SITE_URL = envVal('PUBLIC_SITE_URL', 'https://crm.structa.cloud');

export default defineConfig({
  output: 'static',
  site: SITE_URL,
  integrations: [
    mdx(),
    alpinejs({ entrypoint: '@/alpine' }),
    react(), // React islands (RevOps dashboard, pipeline) — Redux-backed.
  ],
  vite: {
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
        '@fusion': fileURLToPath(
          new URL('../../../libs/django-fusion/js/fusion-js/src', import.meta.url),
        ),
      },
    },
    plugins: [tailwindcss()],
    server: {
      proxy: {
        '/api': { target: BACKEND_URL, changeOrigin: true },
        '/bolt': { target: BACKEND_URL, changeOrigin: true },
        '/accounts': { target: BACKEND_URL, changeOrigin: true },
        '/static': { target: BACKEND_URL, changeOrigin: true },
        '/media': { target: BACKEND_URL, changeOrigin: true },
        '/admin': { target: BACKEND_URL, changeOrigin: true },
        '/fragment': { target: BACKEND_URL, changeOrigin: true },
        '/fragments': { target: BACKEND_URL, changeOrigin: true },
      },
    },
  },
  server: { port: PORT, host: true },
});
