import { test as base, Page } from '@playwright/test';

/**
 * Shared authentication fixtures for POS E2E tests.
 *
 * POS editions use a Fusion sidecar (Python/Sanic on port 8765) for
 * health checks and rendering preferences, and an RTK Query API on
 * port 8766 for data operations.
 *
 * These fixtures mock the auth layer so tests don't need a running
 * sidecar or backend.
 *
 * ## Usage
 *
 * ```ts
 * import { test } from '../../fixtures/auth';
 *
 * test('authenticated page', async ({ authenticatedPage }) => {
 *   await authenticatedPage.goto('/');
 *   // page is already authenticated as default user
 * });
 *
 * test('admin page', async ({ adminPage }) => {
 *   await adminPage.goto('/inventory');
 *   // page renders admin-only content
 * });
 * ```
 */

// ── Default mock user profiles ──────────────────────────────────

export interface MockUser {
  id: number;
  username: string;
  role: 'admin' | 'manager' | 'cashier' | 'staff';
  email: string;
  permissions: string[];
}

export const DEFAULT_USER: MockUser = {
  id: 1,
  username: 'testuser',
  role: 'admin',
  email: 'test@structa.cloud',
  permissions: ['*'],
};

export const CASHIER_USER: MockUser = {
  id: 2,
  username: 'cashier',
  role: 'cashier',
  email: 'cashier@structa.cloud',
  permissions: ['pos.sale', 'pos.inventory.view'],
};

export const MANAGER_USER: MockUser = {
  id: 3,
  username: 'manager',
  role: 'manager',
  email: 'manager@structa.cloud',
  permissions: ['pos.*', 'reports.*'],
};

// ── Mock helpers ────────────────────────────────────────────────

/**
 * Mock the Fusion sidecar health check endpoint so the app starts
 * without needing a running Python sidecar.
 */
export async function mockSidecarHealth(page: Page): Promise<void> {
  await page.route('**/fusion/health', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        status: 'ok',
        fusion_render_first: false,
        version: '1.0.0-test',
      }),
    })
  );
}

/**
 * Mock auth API responses for a given user profile.
 * Intercepts the RTK Query auth endpoint on port 8766.
 */
export async function mockAuthApi(page: Page, user: MockUser = DEFAULT_USER): Promise<void> {
  // Mock the auth profile/status endpoint
  await page.route('**/api/auth/status', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        isAuthenticated: true,
        user,
      }),
    })
  );

  // Mock the auth me/profile endpoint (common alternative path)
  await page.route('**/api/auth/me', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(user),
    })
  );

  // Mock RTK Query base URL auth check
  await page.route('http://localhost:8766/api/auth/status', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        isAuthenticated: true,
        user,
      }),
    })
  );
}

/**
 * Set up all auth mocks at once — sidecar health + auth API.
 */
export async function setupAuth(page: Page, user: MockUser = DEFAULT_USER): Promise<void> {
  await mockSidecarHealth(page);
  await mockAuthApi(page, user);
}

// ── Custom fixtures ─────────────────────────────────────────────

type AuthFixtures = {
  /** Page authenticated as admin (full permissions) */
  adminPage: Page;
  /** Page authenticated as cashier (limited permissions) */
  cashierPage: Page;
  /** Page authenticated as manager */
  managerPage: Page;
};

export const test = base.extend<AuthFixtures>({
  // adminPage is the default fixture — use for authenticated tests
  authenticatedPage: async ({ page }, use) => {
    await setupAuth(page, DEFAULT_USER);
    await use(page);
  },

  adminPage: ['authenticatedPage', async ({ authenticatedPage }, use) => {
    await use(authenticatedPage);
  }, { scope: 'test' }],

  cashierPage: async ({ page }, use) => {
    await setupAuth(page, CASHIER_USER);
    await use(page);
  },

  managerPage: async ({ page }, use) => {
    await setupAuth(page, MANAGER_USER);
    await use(page);
  },
});

export { expect } from '@playwright/test';
