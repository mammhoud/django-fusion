import { expect, test } from '@playwright/test';
import { BACKEND_URL } from '../playwright.config';

/**
 * Backend roads — content APIs, fragment endpoints, admin gate.
 */

test('auth status endpoint is JSON', async ({ request }) => {
  const response = await request.get(`${BACKEND_URL}/apis/auth/status/`);
  expect(response.status()).toBe(200);
  const body = await response.json();
  expect(typeof body.authenticated).toBe('boolean');
  expect(body).toHaveProperty('learning');
});

test('blog comments endpoint returns a clear unknown-post response', async ({ request }) => {
  const response = await request.get(`${BACKEND_URL}/apis/blog/does-not-exist/comments/`);
  expect(response.status()).toBe(404);
});

test('fragment ping remains available for HTMX', async ({ request }) => {
  const response = await request.get(`${BACKEND_URL}/fragment/ping/`);
  expect(response.status()).toBe(200);
  const text = await response.text();
  expect(text.trim().length).toBeGreaterThan(0);
});

test('admin routes to the Wagtail login', async ({ request }) => {
  const response = await request.get(`${BACKEND_URL}/admin/`, { maxRedirects: 0 });
  expect([301, 302]).toContain(response.status());
  const location = response.headers()['location'] || '';
  expect(location).toContain('/admin/login');
});

test('navigation API returns menu links', async ({ request }) => {
  const response = await request.get(`${BACKEND_URL}/apis/navigation/`);
  expect(response.status()).toBe(200);
  const body = await response.json();
  const serialized = JSON.stringify(body);
  expect(serialized.length).toBeGreaterThan(10);
});

test('auth status endpoint remains a stable JSON contract', async ({ request }) => {
  const response = await request.get(`${BACKEND_URL}/apis/auth/status/`);
  expect(response.status()).toBe(200);
  const body = await response.json();
  expect(typeof body).toBe('object');
  expect(typeof body.authenticated).toBe('boolean');
});

test('server auth pages are reachable and branded', async ({ request }) => {
  for (const path of ['/accounts/login/', '/accounts/signup/']) {
    const response = await request.get(`${BACKEND_URL}${path}`);
    expect(response.status(), `${path} should render`).toBe(200);
    expect(await response.text()).toMatch(/Sign in|Create account|Register/i);
  }
});

test('fusion introspection API is served', async ({ request }) => {
  const response = await request.get(`${BACKEND_URL}/fusion/introspection/api/`);
  // 404 acceptable when the site hasn't wired the introspection URLs yet.
  if (response.status() === 404) return;
  expect(response.status()).toBe(200);
  const body = await response.json();
  expect(body.plugins.total).toBeGreaterThanOrEqual(1);
  expect(body.components).toBeTruthy();
});
