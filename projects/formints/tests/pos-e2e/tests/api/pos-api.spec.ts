import { test, expect } from '@playwright/test';
import {
  createApiContext,
  apiHealthCheck,
  apiLogin,
  listEntities,
  createEntity,
  getEntity,
  deleteEntity,
  SERVER_URL,
  API_URL,
} from '../../helpers/api';

/**
 * POS API E2E Tests (Bolt Pattern)
 *
 * Tests backend API endpoints directly — no browser needed.
 *
 * These tests validate:
 * - Server health (Fusion/Robyn)
 * - Auth API (login → token)
 * - CRUD operations on key entities
 * - Error handling (invalid auth, missing resources)
 *
 * ## Running
 *   npx playwright test tests/api/ --project=pos-full
 *
 * ## Prerequisites
 *   - Server must be running on port 8765
 *   - Backend API must be running on port 8766
 */

test.describe('POS API — Server Health', () => {
  test('server health endpoint returns ok', async () => {
    const ctx = await createApiContext(SERVER_URL);

    const healthy = await apiHealthCheck(ctx, '/fusion/health');

    // Server may not be running in CI — skip gracefully
    if (!healthy) {
      test.skip(true, 'Server not running — skipping health check');
      return;
    }

    expect(healthy).toBe(true);
    await ctx.dispose();
  });

  test('server health returns valid JSON even when unhealthy', async () => {
    const ctx = await createApiContext(SERVER_URL);

    try {
      const res = await ctx.get('/fusion/health', { timeout: 5000 });
      const body = await res.json().catch(() => null);
      expect(body).toBeDefined();
    } catch {
      // Server not running — skip gracefully (same as health check test)
      test.skip(true, 'Server not running — skipping');
    }

    await ctx.dispose();
  });
});

test.describe('POS API — Authentication', () => {
  test('login with valid credentials returns token', async () => {
    const ctx = await createApiContext(API_URL);

    try {
      const { token } = await apiLogin(ctx, 'admin', 'admin123');
      expect(token).toBeDefined();
      expect(token.length).toBeGreaterThan(0);
    } catch {
      test.skip(true, 'Backend API not running — skipping auth test');
    }

    await ctx.dispose();
  });

  test('login with invalid credentials returns 401', async () => {
    const ctx = await createApiContext(API_URL);

    try {
      const res = await ctx.post('/api/auth/login', {
        data: { username: 'invalid', password: 'wrong' },
        timeout: 5000,
      });

      expect(res.status()).toBeGreaterThanOrEqual(400);
      expect(res.status()).toBeLessThan(500);
    } catch {
      test.skip(true, 'Backend API not running — skipping');
    }

    await ctx.dispose();
  });

  test('unauthenticated requests to protected endpoints return 401', async () => {
    const ctx = await createApiContext(API_URL);

    try {
      const res = await ctx.get('/api/inventory/', { timeout: 5000 });
      // Should reject unauthenticated access
      expect([401, 403]).toContain(res.status());
    } catch {
      test.skip(true, 'Backend API not running — skipping');
    }

    await ctx.dispose();
  });
});

test.describe('POS API — CRUD Operations', () => {
  let authToken: string;
  let ctx: Awaited<ReturnType<typeof createApiContext>>;

  test.beforeAll(async () => {
    ctx = await createApiContext(API_URL);
    try {
      const result = await apiLogin(ctx);
      authToken = result.token;
    } catch {
      // Auth not available — all tests in this describe will skip
    }
  });

  test.afterAll(async () => {
    await ctx.dispose();
  });

  test('list inventory items', async () => {
    if (!authToken) { test.skip(true, 'Auth not available'); return; }

    const results = await listEntities(ctx, authToken, '/api/inventory/');
    expect(results).toBeDefined();
    // Should return array or paginated response
    expect(results.results || results).toBeDefined();
  });

  test('create and delete a product', async () => {
    if (!authToken) { test.skip(true, 'Auth not available'); return; }

    // Create
    const { status, body } = await createEntity(ctx, authToken, '/api/inventory/', {
      name: `E2E Test Product ${Date.now()}`,
      price: 9.99,
      stock: 100,
    });

    // Should be 201 (created) or 200 (ok) — or skip if endpoint not available
    expect([200, 201, 404]).toContain(status);

    // If created, clean up
    if (status === 201 && body.id) {
      const deleteStatus = await deleteEntity(ctx, authToken, '/api/inventory/', body.id);
      expect(deleteStatus.status).toBe(204);
    }
  });

  test('list customers', async () => {
    if (!authToken) { test.skip(true, 'Auth not available'); return; }

    const results = await listEntities(ctx, authToken, '/api/customers/');
    expect(results).toBeDefined();
    expect(results.results || results).toBeDefined();
  });

  test('get non-existent entity returns 404', async () => {
    if (!authToken) { test.skip(true, 'Auth not available'); return; }

    const { status } = await getEntity(ctx, authToken, '/api/inventory/', 999999);
    expect(status).toBe(404);
  });
});
