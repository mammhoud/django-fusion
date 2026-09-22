/**
 * Playwright config for the tools-web dashboard.
 * Starts the vanilla Node server on port 4398 with a known unlock password.
 *
 * Run with (from application/tools/tools-web):
 *   npx playwright test
 */
import { defineConfig, devices } from '@playwright/test';

const PORT = 4398;

export default defineConfig({
  testDir: './tests',
  testMatch: '**/*.spec.mjs',
  timeout: 30_000,
  fullyParallel: false,
  workers: 1,
  use: {
    baseURL: `http://127.0.0.1:${PORT}`,
    ...devices['Desktop Chrome'],
  },
  webServer: {
    command: `node server.mjs`,
    url: `http://127.0.0.1:${PORT}/health/`,
    reuseExistingServer: false,
    timeout: 15_000,
    env: {
      PORT: String(PORT),
      HOST: '127.0.0.1',
      TOOLS_UNLOCK_PASSWORD: 'test-unlock-pass-123',
      TOOLS_SESSION_SECRET: 'test-session-secret',
    },
  },
});
