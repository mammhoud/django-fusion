import { defineConfig } from 'vitest/config';
import path from 'path';

/**
 * Unified vitest configuration for POS editions.
 *
 * Discovers tests from all three editions (mini, solo, full) as well
 * as any new tests added directly under `tests/js/` or `tests/api/`.
 *
 * @tauri-apps imports are redirected to local mocks via resolve.alias
 * since tests run in jsdom without the Tauri Rust backend.
 *
 * Run from the project root (projects/pos):
 *   npx vitest run --config tests/js/vitest.config.ts
 */
const ROOT = path.resolve(__dirname, '..', '..');
const MOCKS = path.resolve(__dirname, 'mocks');

export default defineConfig({
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: [
      // Polyfills for browser APIs not in jsdom (matchMedia, ResizeObserver, scrollTo)
      // Also mocks @tauri-apps/api/core via vi.mock (resolve.alias is the primary mechanism)
      path.join(__dirname, 'setup-global.ts'),
    ],
    testTimeout: 10000,
    hookTimeout: 10000,
    include: [
      // Tests from each edition (shared identical copies — run one edition)
      path.join(ROOT, 'pos-full', 'src', 'test', '**', '*.test.{ts,tsx}'),
      // formint-pos (merged package) frontend tests — Astro shell contract
      path.join(ROOT, 'formint-pos', 'frontend', 'src', '**', '*.test.{ts,tsx}'),
      // New tests in the unified test directory
      path.join(__dirname, '*.test.{ts,tsx}'),
      path.join(__dirname, '..', 'api', '*.test.{ts,tsx}'),
    ],
    exclude: [
      '**/node_modules/**',
      '**/dist/**',
      '**/__pycache__/**',
    ],
  },
  resolve: {
    alias: {
      '@': path.resolve(ROOT, 'pos-full', 'src'),
      // Redirect all @tauri-apps imports to local mocks (no Tauri Rust backend in jsdom)
      '@tauri-apps/api/core': path.join(MOCKS, 'tauri-api-core.ts'),
      '@tauri-apps/plugin-dialog': path.join(MOCKS, 'tauri-plugin-dialog.ts'),
      '@tauri-apps/plugin-fs': path.join(MOCKS, 'tauri-plugin-fs.ts'),
    },
  },
  server: {
    // Allow test files outside the runner's root (pos-full) — e.g. the
    // formint-pos merged package tests — to be loaded by vite/vitest.
    fs: {
      allow: [ROOT],
    },
  },
});
