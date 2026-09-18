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
const USE_LOCAL_SERVERS = Boolean(process.env.E2E_FRONTEND_URL || process.env.E2E_BACKEND_URL);
const FRONTEND_URL = process.env.E2E_FRONTEND_URL || 'https://ctc-research.com';
const BACKEND_URL = process.env.E2E_BACKEND_URL || FRONTEND_URL;
const FRONTEND_PORT = new URL(FRONTEND_URL).port || '3001';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  retries: 1,
  workers: 2,
  // Public deployment checks can traverse Traefik, Astro, and Django/Wagtail;
  // keep assertions strict while allowing cold-cache/backend startup latency.
  timeout: 120_000,
  expect: { timeout: 15_000 },
  navigationTimeout: 90_000,
  reporter: [
    ['list'],
    ['html', { outputFolder: 'playwright-report', open: 'never' }],
  ],
  use: {
    baseURL: FRONTEND_URL,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    // The local backend trusts X-Forwarded-Proto (Traefik sets it in front of
    // Django); without it, the backend's HTTPS redirect bounces API requests
    // to a TLS port the compose stack does not terminate.
    extraHTTPHeaders: { 'X-Forwarded-Proto': 'https' },
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  ],
  // Remote/public E2E runs must not try to start a local Astro server. Supply
  // E2E_FRONTEND_URL/E2E_BACKEND_URL to opt into the local compose workflow.
  ...(USE_LOCAL_SERVERS ? {
    webServer: {
      command: `node ./node_modules/.bin/astro dev --port ${FRONTEND_PORT}`,
      url: FRONTEND_URL,
      reuseExistingServer: true,
      timeout: 120_000,
    },
  } : {}),
});

export { FRONTEND_URL, BACKEND_URL };
