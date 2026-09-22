import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright E2E for Precis Landing (structa.cloud) — full
 * feature surface: static Astro pages + the Django/Wagtail backend roads
 * (learning, fragments, APIs, admin).
 *
 * Defaults target the dev stack: Astro on :3000 (dev server proxies
 * /apis, /fragment, /api, /admin, /static, /media, /learning to the
 * backend on :8074). Override via env:
 *
 *   E2E_FRONTEND_URL=http://127.0.0.1:3000 npm run test:e2e
 *   E2E_BACKEND_URL=http://127.0.0.1:8074 npm run test:e2e
 *
 * NOTE: this workspace resolves `@playwright/test` through a symlink into
 * formints/tests/pos-e2e's node_modules (offline reuse of the installed
 * runner + browsers); a plain `npm install` after adding the devDependency
 * replaces it.
 */
const FRONTEND_URL = process.env.E2E_FRONTEND_URL || 'http://127.0.0.1:3000';
const BACKEND_URL = process.env.E2E_BACKEND_URL || 'http://127.0.0.1:8074';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  retries: 1,
  workers: 2,
  timeout: 30_000,
  expect: { timeout: 10_000 },
  reporter: [
    ['list'],
    ['html', { outputFolder: 'playwright-report', open: 'never' }],
  ],
  use: {
    baseURL: FRONTEND_URL,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  ],
  webServer: {
    command: 'npm run dev',
    url: FRONTEND_URL,
    reuseExistingServer: true,
    timeout: 120_000,
  },
});

export { FRONTEND_URL, BACKEND_URL };
