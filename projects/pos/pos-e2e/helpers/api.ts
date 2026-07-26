import { APIRequestContext, request } from '@playwright/test';

/**
 * API Helpers for "bolt pattern" E2E tests.
 *
 * These helpers test backend API endpoints directly (no browser).
 * Use Playwright's built-in `request` fixture for HTTP calls.
 *
 * ## Usage
 *
 * ```ts
 * import { test, expect } from '@playwright/test';
 * import { createApiContext, apiHealthCheck } from '../../helpers/api';
 *
 * test('sidecar health', async () => {
 *   const ctx = await createApiContext('http://localhost:8765');
 *   const healthy = await apiHealthCheck(ctx);
 *   expect(healthy).toBe(true);
 * });
 * ```
 */

/** Default sidecar URL shared across POS editions */
export const SIDECAR_URL = 'http://localhost:8765';

/** Default RTK Query API URL */
export const API_URL = 'http://localhost:8766';

/**
 * Create an API request context for direct API testing.
 */
export async function createApiContext(baseURL: string = API_URL): Promise<APIRequestContext> {
  return request.newContext({ baseURL });
}

/**
 * Health check — GET /fusion/health or /api/health
 */
export async function apiHealthCheck(ctx: APIRequestContext, path: string = '/fusion/health'): Promise<boolean> {
  try {
    const res = await ctx.get(path, { timeout: 5000 });
    if (!res.ok()) return false;
    const body = await res.json();
    return body?.status === 'ok';
  } catch {
    return false;
  }
}

/**
 * Login via API and return the auth token + user.
 */
export async function apiLogin(
  ctx: APIRequestContext,
  username: string = 'admin',
  password: string = 'admin123',
  loginPath: string = '/api/auth/login'
): Promise<{ token: string; user: Record<string, unknown> }> {
  const res = await ctx.post(loginPath, {
    data: { username, password },
  });
  const body = await res.json();
  return { token: body.token ?? body.access_token, user: body.user };
}

/**
 * Make an authenticated API request (bolt pattern).
 */
export async function authenticatedRequest(
  ctx: APIRequestContext,
  method: 'get' | 'post' | 'put' | 'patch' | 'delete',
  url: string,
  token: string,
  data?: Record<string, unknown>
) {
  const headers: Record<string, string> = {
    Authorization: `Bearer ${token}`,
  };
  if (data) headers['Content-Type'] = 'application/json';

  return ctx[method](url, { headers, data });
}

/**
 * CRUD helpers for common entity types.
 */
export async function listEntities(ctx: APIRequestContext, token: string, endpoint: string) {
  const res = await authenticatedRequest(ctx, 'get', endpoint, token);
  return res.json();
}

export async function createEntity(
  ctx: APIRequestContext,
  token: string,
  endpoint: string,
  data: Record<string, unknown>
) {
  const res = await authenticatedRequest(ctx, 'post', endpoint, token, data);
  return { status: res.status(), body: await res.json() };
}

export async function getEntity(ctx: APIRequestContext, token: string, endpoint: string, id: number) {
  const res = await authenticatedRequest(ctx, 'get', `${endpoint}${id}/`, token);
  return { status: res.status(), body: await res.json() };
}

export async function deleteEntity(ctx: APIRequestContext, token: string, endpoint: string, id: number) {
  const res = await authenticatedRequest(ctx, 'delete', `${endpoint}${id}/`, token);
  return { status: res.status() };
}
