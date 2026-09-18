import { expect, test } from '@playwright/test';
import { BACKEND_URL } from '../playwright.config';

/**
 * Task Center — the authenticated background-job history page served by the
 * Django backend road. Mirrors the auth-gate contract used elsewhere: anonymous
 * traffic must be bounced to allauth login with a `next` target, never render
 * the audit table. (Authenticated rendering is covered by the backend suite;
 * this keeps the browser contract robust against workspace credential drift.)
 */

test('task center is auth-gated on the backend', async ({ request }) => {
  const response = await request.get(`${BACKEND_URL}/tasks/`, { maxRedirects: 0 });
  expect([301, 302, 303]).toContain(response.status());
  const location = response.headers()['location'] || '';
  expect(location).toContain('/accounts/login/');
  expect(location).toContain('next=');
  expect(location).toContain('tasks');
});

test('task center redirects anonymous browser traffic to login', async ({ page }) => {
  await page.goto(`${BACKEND_URL}/tasks/`);
  await page.waitForURL(/\/accounts\/login\//, { timeout: 10_000 });
  expect(page.url()).toContain('next=');
});
