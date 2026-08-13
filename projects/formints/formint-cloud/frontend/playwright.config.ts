import { defineConfig } from '@playwright/test';

/**
 * Playwright configuration for Formint e2e / visual regression tests.
 *
 * The Vite dev server is started automatically via the `webServer` option.
 * Tauri's `invoke` API is mocked in each test via `page.addInitScript`
 * so the frontend can render without a running Tauri backend.
 */
export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['list'],
    ['html', { outputFolder: 'playwright-report' }],
  ],
  use: {
    // The cloud Astro dev server binds :4323 (see astro.config.mjs) — not
    // the :1420 Tauri port the sibling editions use.
    baseURL: 'http://localhost:4323',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  webServer: {
    // Run the astro binary directly instead of `pnpm dev`: the cloud
    // edition's predev hooks (kill-port/ensure-db → cargo seed) fail
    // because there is no src-tauri/ in this checkout.
    command: './node_modules/.bin/astro dev',
    url: 'http://localhost:4323',
    reuseExistingServer: !process.env.CI,
    timeout: 30_000,
  },
  outputDir: 'test-results/e2e',
});
