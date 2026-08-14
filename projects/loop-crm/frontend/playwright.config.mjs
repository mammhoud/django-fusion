import { defineConfig, devices } from '@playwright/test';

// The Django backend port. Override with PLAYWRIGHT_PORT when 8000 is taken
// locally (e.g. another app owns it); CI/Compose keep the default.
const PORT = process.env.PLAYWRIGHT_PORT ?? '8000';
const BASE_URL = process.env.PLAYWRIGHT_BASE_URL ?? `http://127.0.0.1:${PORT}`;

export default defineConfig({
  testDir: './tests/e2e',
  timeout: 30_000,
  fullyParallel: false,
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 2 : 0,
  workers: 1,
  reporter: process.env.CI ? [['line'], ['html', { open: 'never' }]] : 'list',
  use: {
    baseURL: BASE_URL,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    // Video recording needs an ffmpeg build that Playwright 1.62 no longer
    // ships for macOS 12; set PLAYWRIGHT_VIDEO=off on such hosts.
    video: process.env.PLAYWRIGHT_VIDEO === 'off' ? 'off' : 'retain-on-failure',
    colorScheme: 'dark',
    channel: process.env.PLAYWRIGHT_CHANNEL ?? 'chrome',
    ...devices['Desktop Chrome'],
  },
  webServer: process.env.PLAYWRIGHT_BASE_URL
    ? undefined
    : {
        command: `uv run --project ../.. python manage.py migrate --noinput && uv run --project ../.. python manage.py seed_playwright && uv run --project ../.. python manage.py runserver 127.0.0.1:${PORT} --noreload`,
        cwd: '../backend',
        url: `${BASE_URL}/accounts/login/`,
        reuseExistingServer: !process.env.CI,
        timeout: 120_000,
      },
});
