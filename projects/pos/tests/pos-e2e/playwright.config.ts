import { defineConfig, devices } from '@playwright/test';

/**
 * Shared Playwright configuration for all POS editions.
 *
 * Each edition is a separate Playwright "project" so you can run tests
 * against a specific edition with `--project=pos-full`, or all at once.
 *
 * ## Running tests
 *   npx playwright test                          # all editions
 *   npx playwright test --project=pos-full       # full edition only
 *   npx playwright test tests/e2e/home.spec.ts   # specific test file
 *
 * ## Page E2E vs API E2E
 *   - tests/e2e/   = browser-based (render first)
 *   - tests/api/   = API-only (bolt pattern — no browser needed)
 *
 * Each edition runs its own Vite dev server on a dedicated port:
 *   pos-full  → 1420
 *   pos-solo  → 1421
 *   pos-mini  → 1422
 *   pos-client → 1423
 *   pos-cloud  → 1424  (scaffolded; tests skipped until src/ is built)
 */

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: process.env.CI ? 2 : undefined,
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['list'],
  ],
  timeout: 30000,
  expect: { timeout: 10000 },

  use: {
    // Default baseURL — overridden per project below
    baseURL: 'http://localhost:1420',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },

  projects: [
    // ── POS Full Edition ────────────────────────────────────────
    {
      name: 'pos-full',
      use: {
        ...devices['Desktop Chrome'],
        baseURL: 'http://localhost:1420',
      },
      webServer: {
        command: 'cd ../pos-full && npx vite --port 1420 --strictPort',
        port: 1420,
        reuseExistingServer: !process.env.CI,
        timeout: 30000,
      },
    },

    // ── POS Solo Edition ────────────────────────────────────────
    {
      name: 'pos-solo',
      use: {
        ...devices['Desktop Chrome'],
        baseURL: 'http://localhost:1421',
      },
      webServer: {
        command: 'cd ../pos-solo && npx vite --port 1421 --strictPort',
        port: 1421,
        reuseExistingServer: !process.env.CI,
        timeout: 30000,
      },
    },

    // ── POS Mini Edition ────────────────────────────────────────
    {
      name: 'pos-mini',
      use: {
        ...devices['Desktop Chrome'],
        baseURL: 'http://localhost:1422',
      },
      timeout: 60000,
      webServer: {
        command: 'cd ../pos-mini && npx vite --port 1422 --strictPort',
        port: 1422,
        reuseExistingServer: !process.env.CI,
        timeout: 30000,
      },
    },

    // ── POS Client Edition ──────────────────────────────────────
    {
      name: 'pos-client',
      use: {
        ...devices['Desktop Chrome'],
        baseURL: 'http://localhost:1423',
      },
      webServer: {
        command: 'cd ../pos-client && npx vite --port 1423 --strictPort',
        port: 1423,
        reuseExistingServer: !process.env.CI,
        timeout: 30000,
      },
    },

    // ── POS Cloud Edition (scaffolded) ──────────────────────────
    {
      name: 'pos-cloud',
      use: {
        ...devices['Desktop Chrome'],
        baseURL: 'http://localhost:1424',
      },
      // No webServer yet — cloud edition src/ not built.
      // Skip all tests until the edition is ready.
      testIgnore: ['**/*'],
    },
  ],
});
