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
    baseURL: process.env.E2E_BASE_URL || 'http://127.0.0.1:4323',
    // Local CI/dev images may provide Chromium through the OS instead of a
    // Playwright browser cache. Keep the default bundled-browser behavior,
    // but allow an explicit executable path without hard-coding one here.
    launchOptions: process.env.E2E_CHROMIUM_PATH
      ? { executablePath: process.env.E2E_CHROMIUM_PATH }
      : undefined,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  webServer: {
    // Run the astro binary directly instead of `pnpm dev`: the cloud
    // edition's predev hooks (kill-port/ensure-db → cargo seed) fail
    // because there is no src-tauri/ in this checkout.
    // Run the Astro dev server directly so its configured API proxy remains
    // available to the client-only telemetry island. The route readiness URL
    // below warms the first island transform before the browser test starts.
    command: './node_modules/.bin/astro dev --host 127.0.0.1',
    // Warm the actual client-only route before tests begin. The root HTML
    // shell can be ready while the first island transform is still compiling.
    url: 'http://127.0.0.1:4323/telemetry',
    // Never reuse an unrelated/stale dev server: E2E must exercise the
    // current checkout and provider wiring, not whichever process happens to
    // own :4323 from a previous local run.
    reuseExistingServer: false,
    timeout: 180_000,
  },
  outputDir: 'test-results/e2e',
});
