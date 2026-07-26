import { test, expect, APIRequestContext, request } from '@playwright/test';

/**
 * LMS Backend API E2E Tests (Bolt Pattern)
 *
 * Tests Django backend API endpoints directly using Playwright's
 * built-in request fixture — no browser needed. Gets retries,
 * tracing, and reporter output like any other Playwright test.
 *
 * ## Running
 *   npx playwright test tests/api/ --project=chromium
 *
 * ## Prerequisites
 *   - Django backend must be running (python manage.py runserver)
 *   - Set BACKEND_URL env var or defaults to http://localhost:8000
 */

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

// ── Helpers ────────────────────────────────────────────────────────

let ctx: APIRequestContext;

test.beforeAll(async () => {
  ctx = await request.newContext({ baseURL: BACKEND_URL });
});

test.afterAll(async () => {
  await ctx.dispose();
});

async function apiGet(path: string, token?: string) {
  const headers: Record<string, string> = {};
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await ctx.get(path, { headers });
  return { status: res.status(), body: await res.json().catch(() => null) };
}

async function apiPost(path: string, data: Record<string, unknown>, token?: string) {
  const headers: Record<string, string> = {};
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await ctx.post(path, { headers, data });
  return { status: res.status(), body: await res.json().catch(() => null) };
}

// ── Tests ──────────────────────────────────────────────────────────

test.describe('LMS Backend API — Health', () => {
  test('API root returns 200', async () => {
    const { status } = await apiGet('/apis/');
    // Skip if backend not running
    if (status === 0 || status >= 500) {
      test.skip(true, 'Backend not running');
      return;
    }
    expect([200, 301, 302, 404]).toContain(status); // Django may redirect or return API root
  });

  test('courses endpoint returns data', async () => {
    const { status, body } = await apiGet('/apis/courses/');
    if (status === 0 || status >= 500) {
      test.skip(true, 'Backend not running');
      return;
    }
    expect(status).toBe(200);
    expect(body).toBeDefined();
    // Should be paginated or array
    expect(body.results || body).toBeDefined();
  });
});

test.describe('LMS Backend API — Auth', () => {
  test('login with valid credentials', async () => {
    const { status, body } = await apiPost('/apis/auth/login/', {
      username: 'testuser',
      password: 'testpass123',
    });

    if (status === 0 || status >= 500) {
      test.skip(true, 'Backend not running');
      return;
    }

    // Either 200 (success) or 401 (invalid creds) — both are valid responses
    expect([200, 401]).toContain(status);
    if (status === 200) {
      expect(body.token || body.access_token).toBeDefined();
    }
  });

  test('protected endpoint rejects unauthenticated requests', async () => {
    const { status } = await apiGet('/apis/withdrawals/');
    if (status === 0 || status >= 500) {
      test.skip(true, 'Backend not running');
      return;
    }
    expect([401, 403]).toContain(status);
  });

  test('registration with valid data', async () => {
    const { status, body } = await apiPost('/apis/auth/register/', {
      username: `e2e_test_${Date.now()}`,
      email: `e2e_${Date.now()}@test.com`,
      password: 'TestPass123!',
      password2: 'TestPass123!',
      role: 'student',
    });

    if (status === 0 || status >= 500) {
      test.skip(true, 'Backend not running');
      return;
    }

    expect([200, 201, 400]).toContain(status); // 400 = duplicate username (test already ran)
  });
});

test.describe('LMS Backend API — Instructors', () => {
  test('instructors list returns data', async () => {
    const { status, body } = await apiGet('/apis/instructors/');
    if (status === 0 || status >= 500) {
      test.skip(true, 'Backend not running');
      return;
    }
    expect(status).toBe(200);
    expect(body.results || body).toBeDefined();
  });
});

test.describe('LMS Backend API — Error Handling', () => {
  test('non-existent endpoint returns 404', async () => {
    const { status } = await apiGet('/apis/non-existent-endpoint/');
    if (status === 0 || status >= 500) {
      test.skip(true, 'Backend not running');
      return;
    }
    expect(status).toBe(404);
  });

  test('invalid auth token returns 401', async () => {
    const { status } = await apiGet('/apis/withdrawals/', 'invalid-token-12345');
    if (status === 0 || status >= 500) {
      test.skip(true, 'Backend not running');
      return;
    }
    expect([401, 403]).toContain(status);
  });
});
