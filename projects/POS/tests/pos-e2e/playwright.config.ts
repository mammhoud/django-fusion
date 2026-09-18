import { defineConfig, devices } from '@playwright/test';

/**
 * Shared Playwright configuration for the canonical Formints editions.
 *
 * The retired `pos-full` / `pos-solo` / `pos-mini` / `pos-cloud` projects were
 * replaced by the current extension chain:
 *
 *   formint-community  → Astro + React (desktop POS UI)      :1420
 *   formint-standard   → Astro + React (desktop POS UI)      :1430
 *   formint-pro        → Astro + Alpine + HTMX               :4321
 *   formint-cloud      → Astro + React (cloud master UI)     :4323
 *   formint-client     → Vue 3 (desktop client)              :1433
 *   formint-cloud-sync → Django cloud API + WebSocket sync   :8767 (external)
 *
 * ## Running
 *   npx playwright test                          # all projects
 *   npx playwright test --project=formint-cloud  # one edition
 *   npx playwright test tests/sync/              # cloud sync contract
 *
 * The cloud sync project (API + WS) requires the Django cloud backend to be
 * booted first: `make dev-api` + `make dev-backend` in projects/formints/formint-cloud.
 * It does not start its own webServer because the backend needs migrations +
 * daphne, which are orchestrated by the edition Makefile.
 */

const CLOUD_API = process.env.CLOUD_API_URL ?? 'http://127.0.0.1:8767';

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
    baseURL: 'http://localhost:1420',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    // The React/Vue dev apps need extra flags to avoid renderer crashes in
    // constrained containers (64M /dev/shm). Django-served pages work without
    // them, but these are safe everywhere.
    launchOptions: {
      args: [
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--no-zygote',
        '--disable-gpu',
        '--disable-software-rasterizer',
      ],
    },
  },

  projects: [
    // ── Formint Community ────────────────────────────────────────
    {
      name: 'formint-community',
      testMatch: /frontends\.spec\.ts/,
      use: { ...devices['Desktop Chrome'], baseURL: 'http://localhost:1420' },
      webServer: {
        command: 'cd ../../formint-community && PORT=1420 ./node_modules/.bin/astro dev',
        port: 1420,
        reuseExistingServer: !process.env.CI,
        timeout: 60000,
      },
    },

    // ── Formint Standard ─────────────────────────────────────────
    {
      name: 'formint-standard',
      testMatch: /frontends\.spec\.ts/,
      use: { ...devices['Desktop Chrome'], baseURL: 'http://localhost:1430' },
      webServer: {
        command: 'cd ../../formint-standard && PORT=1430 ./node_modules/.bin/astro dev',
        port: 1430,
        reuseExistingServer: !process.env.CI,
        timeout: 60000,
      },
    },

    // ── Formint Pro (Astro frontend) ─────────────────────────────
    {
      name: 'formint-pro',
      testMatch: /frontends\.spec\.ts/,
      use: { ...devices['Desktop Chrome'], baseURL: 'http://localhost:4321' },
      webServer: {
        command: 'cd ../../formint-pro/frontend && PORT=4321 ./node_modules/.bin/astro dev',
        port: 4321,
        reuseExistingServer: !process.env.CI,
        timeout: 60000,
      },
    },

    // ── Formint Cloud (Astro frontend) ───────────────────────────
    {
      name: 'formint-cloud',
      testMatch: /frontends\.spec\.ts/,
      use: { ...devices['Desktop Chrome'], baseURL: 'http://localhost:4323' },
      webServer: {
        command: 'cd ../../formint-cloud/frontend && PORT=4323 ./node_modules/.bin/astro dev',
        port: 4323,
        reuseExistingServer: !process.env.CI,
        timeout: 60000,
      },
    },

    // ── Formint Client (Vue desktop) ─────────────────────────────
    {
      name: 'formint-client',
      testMatch: /frontends\.spec\.ts/,
      use: { ...devices['Desktop Chrome'], baseURL: 'http://localhost:1433' },
      webServer: {
        command: 'cd ../../formint-client && PORT=1433 ./node_modules/.bin/vite',
        port: 1433,
        reuseExistingServer: !process.env.CI,
        timeout: 60000,
      },
    },

    // ── Formint Cloud Sync (API + WebSocket, backend pre-booted) ──
    {
      name: 'formint-cloud-sync',
      testMatch: /cloud-sync\.spec\.ts|sdk\.spec\.ts|cloud\.spec\.ts/,
      use: {
        ...devices['Desktop Chrome'],
        baseURL: CLOUD_API,
      },
      // No webServer — the Django backend (daphne :8767 + runserver :8082)
      // is booted separately so migrations can run before the test suite.
    },
  ],

  // Retired-edition specs are kept for history but no longer target a
  // buildable edition; exclude them from the canonical run.
  testIgnore: [
    'e2e/auth.spec.ts',
    'e2e/home.spec.ts',
    'e2e/sale.spec.ts',
    'e2e/inventory.spec.ts',
    'e2e/responsive.spec.ts',
    'api/pos-api.spec.ts',
  ],

  globalSetup: undefined,
});
