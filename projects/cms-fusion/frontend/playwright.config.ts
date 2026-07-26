import { defineConfig, devices } from "@playwright/test";

/**
 * Playwright E2E configuration for lms/lms (original Next.js project).
 *
 * Dev server: `npm run dev` starts Next.js on port 3000 (default).
 * Test directory: tests/e2e/
 *
 * CI runs these via the `lms-e2e` job in .github/workflows/js-test.yml
 * (currently commented out until test files exist).
 */
export default defineConfig({
  testDir: "./tests/e2e",
  fullyParallel: true,
  retries: 1,
  workers: 4,
  timeout: 30000,
  expect: { timeout: 10000 },
  reporter: [
    ["html", { outputFolder: "playwright-report" }],
    ["list"],
  ],
  use: {
    baseURL: "http://localhost:3000",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
  webServer: {
    command: "npx next dev -p 3000",
    cwd: __dirname,
    url: "http://localhost:3000",
    reuseExistingServer: true,
    timeout: 60000,
  },
});
