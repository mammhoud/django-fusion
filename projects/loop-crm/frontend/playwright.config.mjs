import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  timeout: 30_000,
  fullyParallel: false,
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 2 : 0,
  workers: 1,
  reporter: process.env.CI ? [['line'], ['html', { open: 'never' }]] : 'list',
  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL ?? 'http://127.0.0.1:8000',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    colorScheme: 'dark',
    channel: process.env.PLAYWRIGHT_CHANNEL ?? 'chrome',
    ...devices['Desktop Chrome'],
  },
  webServer: process.env.PLAYWRIGHT_BASE_URL
    ? undefined
    : {
        command: 'uv run --project ../.. python manage.py migrate --noinput && uv run --project ../.. python manage.py seed_playwright && uv run --project ../.. python manage.py runserver 127.0.0.1:8000 --noreload',
        cwd: '../backend',
        url: 'http://127.0.0.1:8000/accounts/login/',
        reuseExistingServer: !process.env.CI,
        timeout: 120_000,
      },
});
