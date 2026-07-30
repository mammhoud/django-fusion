import { defineConfig } from '@playwright/test';
export default defineConfig({
  testDir: './tests/api',
  timeout: 30000,
  retries: 0,
  workers: 1,
  use: {
    baseURL: process.env.BACKEND_URL || 'http://localhost:5075',
  },
});
