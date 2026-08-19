import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright E2E for Precis (ctc-research.com) — full feature surface.
 *
 * Targets the running CTC compose stack by default (frontend
 * :3003, backend :5070). Override with env vars to point elsewhere:
 *
 *   E2E_FRONTEND_URL=http://127.0.0.1:3003 npm run test:e2e:playwright
 *   E2E_BACKEND_URL=http://127.0.0.1:5070 npm run test:e2e:playwright
 *
 * The `webServer` reuses an already-running stack (`reuseExistingServer`),
 * or starts the Astro dev server on the configured port when none is
 * listening. NOTE: this workspace resolves `@playwright/test` through a
 * symlink into formints/tests/pos-e2e's node_modules (offline reuse of the
 * installed runner + browsers); a plain `npm install` after adding the
 * devDependency replaces it.
 */
const FRONTEND_URL = process.env.E2E_FRONTEND_URL || 'http://127.0.0.1:3003';
const BACKEND_URL = process.env.E2E_BACKEND_URL || 'http://127.0.0.1:5070';
const FRONTEND_PORT = new URL(FRONTEND_URL).port || '3001';

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
    // Match the configured URL port so a fallback dev server is actually
    // reachable when the compose stack is down.
    command: `node ./node_modules/.bin/astro dev --port ${FRONTEND_PORT}`,
    url: FRONTEND_URL,
    reuseExistingServer: true,
    timeout: 120_000,
  },
});

export { FRONTEND_URL, BACKEND_URL };
