import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/e2e",
  fullyParallel: true,
  retries: 1,
  workers: 4,
  timeout: 30000,
  expect: { timeout: 10000 },
  reporter: [["html", { outputFolder: "playwright-report" }], ["list"]],
  use: {
    baseURL: process.env.PLAYWRIGHT_DOCKER_URL || "http://localhost:3458",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
  webServer: process.env.PLAYWRIGHT_DOCKER_URL
    ? undefined
    : process.env.CI
      ? {
          command: "npx next dev -p 3458",
          cwd: __dirname,
          url: "http://localhost:3458",
          reuseExistingServer: false,
          timeout: 120000,
        }
      : undefined,
});
