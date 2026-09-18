import { test as base, Page } from '@playwright/test';

/**
 * Shared authentication fixtures for POS E2E tests.
 *
 * POS editions use a Fusion server (Python/Sanic on port 8765) for
 * health checks and rendering preferences, and an RTK Query API on
 * port 8766 for data operations.
 *
 * These fixtures mock the auth layer so tests don't need a running
 * server or backend.
 *
 * Tauri invoke mock: The app imports `invoke` from `@tauri-apps/api/core`
 * (a real npm package). Internally it calls window.__TAURI_INTERNALS__.invoke().
 * Since that global doesn't exist in a regular browser, addInitScript()
 * defines it with sensible default responses so pages render without crashing.
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

// ── Tauri invoke mock (required for browser-only E2E) ────────

/**
 * Tauri's `invoke` function (from `@tauri-apps/api/core`) internally
 * calls `window.__TAURI_INTERNALS__.invoke()`. This global is only
 * available inside a Tauri webview, so we define it here.
 *
 * Returns sensible defaults for all commands the app uses so that
 * pages render with empty/default data instead of crashing.
 */
function getInvokeMockScript(): string {
  return `
(function() {
  if (window.__TAURI_INTERNALS__) return; // already set

  const MOCK_HANDLERS = {
    // Auth
    check_auth_required: () => Promise.resolve(false),
    verify_user: () => Promise.resolve(true),
    login_user: () => Promise.resolve({ id: 1, email: 'test@structa.cloud', name: 'Test User' }),
    setup_account: () => Promise.resolve({ id: 1, email: 'test@structa.cloud', name: 'Test User' }),
    send_auth_confirmation_code: () => Promise.resolve(null),

    // Data commands — sample data for sale interactions
    get_products: () => Promise.resolve([
      { id: 101, name: 'Espresso', price: 3.50, category_id: 1, unit: 'cup', stock: 100, active: true },
      { id: 102, name: 'Cappuccino', price: 4.50, category_id: 1, unit: 'cup', stock: 80, active: true },
      { id: 103, name: 'Latte', price: 5.00, category_id: 1, unit: 'cup', stock: 60, active: true },
      { id: 104, name: 'Croissant', price: 3.00, category_id: 2, unit: 'piece', stock: 40, active: true },
      { id: 105, name: 'Panini', price: 7.50, category_id: 2, unit: 'piece', stock: 25, active: true },
      { id: 106, name: 'Chocolate Cake', price: 6.00, category_id: 2, unit: 'slice', stock: 15, active: true },
    ]),
    get_categories: () => Promise.resolve([
      { id: 1, name: 'Coffee', description: 'Hot coffee beverages' },
      { id: 2, name: 'Pastries', description: 'Baked goods and desserts' },
    ]),
    get_ingredients: () => Promise.resolve([]),
    get_inventory_transactions: () => Promise.resolve([]),
    get_customers: () => Promise.resolve([]),
    get_employees: () => Promise.resolve([]),
    get_employee_types: () => Promise.resolve([]),
    get_suppliers: () => Promise.resolve([]),
    get_transactions: () => Promise.resolve([]),
    get_reports: () => Promise.resolve({ totalRevenue: 0, totalOrders: 0, avgOrderValue: 0 }),
    get_recipes: () => Promise.resolve([]),
    get_recipe_categories: () => Promise.resolve([]),
    get_roles: () => Promise.resolve([]),
    get_tax_reports: () => Promise.resolve([]),
    get_receipt_templates: () => Promise.resolve([]),
    get_employee_schedules: () => Promise.resolve([]),
    get_analytics: () => Promise.resolve({
      summary: { total_orders: 0, total_revenue: 0, average_order_value: 0 },
      daily_revenue: [],
      top_products: [],
      product_distribution: [],
    }),
    get_settings: () => Promise.resolve({}),
    get_kitchen_tickets: () => Promise.resolve([]),
    get_payroll: () => Promise.resolve([]),
    get_invoice: () => Promise.resolve(null),
    get_printers: () => Promise.resolve([]),

    // Settings
    save_settings: () => Promise.resolve(null),
    change_password_cmd: () => Promise.resolve(null),
    import_database_cmd: () => Promise.resolve(null),
    export_database_cmd: () => Promise.resolve(null),
    send_support_email: () => Promise.resolve(null),
    check_update: () => Promise.resolve({ hasUpdate: false }),
    restart_app: () => Promise.resolve(null),
  };

  // Mutation commands all return null (success, no return value)
  function mutationHandler() {
    return Promise.resolve(null);
  }

  function createHandler() {
    return Promise.resolve({ id: Date.now() });
  }

  window.__TAURI_INTERNALS__ = {
    invoke: function(cmd, args) {
      // Check explicit handlers first
      if (MOCK_HANDLERS[cmd]) {
        return MOCK_HANDLERS[cmd](args);
      }

      // Pattern-based fallbacks
      if (cmd.startsWith('get_')) return Promise.resolve([]);
      if (cmd.startsWith('add_')) return createHandler();
      if (cmd.startsWith('update_')) return mutationHandler();
      if (cmd.startsWith('delete_')) return mutationHandler();
      if (cmd.startsWith('soft_delete_')) return mutationHandler();

      // Unknown command — reject so tests can detect missing mocks
      return Promise.reject(new Error('Unmocked invoke command: ' + cmd));
    },
  };
})();
`;
}

// ── Mock helpers ────────────────────────────────────────────────

/**
 * Mock the Fusion server health check endpoint so the app starts
 * without needing a running Python server.
 */
export async function mockServerHealth(page: Page): Promise<void> {
  if (!page || typeof page.route !== 'function') return;
  try {
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
  } catch {
    // Mock may fail if page isn't fully initialized
  }
}

/**
 * Mock auth API responses for a given user profile.
 * Intercepts the RTK Query auth endpoint on port 8766.
 */
export async function mockAuthApi(page: Page, user: MockUser = DEFAULT_USER): Promise<void> {
  if (!page || typeof page.route !== 'function') return;
  try {
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
  } catch {
    // Mock may fail if page isn't fully initialized
  }
}

/**
 * Set up all mocks at once — Tauri IPC, server health, and auth API.
 *
 * The Tauri invoke mock is added via addInitScript so it's available
 * before any JavaScript executes on the page.
 */
export async function setupAuth(page: Page, user: MockUser = DEFAULT_USER): Promise<void> {
  if (!page || typeof page.route !== 'function') return;

  // Add the Tauri invoke mock via addInitScript (runs before any page JS)
  await page.addInitScript(getInvokeMockScript());

  // Mock network routes
  await mockServerHealth(page);
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
  adminPage: async ({ page }, use) => {
    await setupAuth(page, DEFAULT_USER);
    await use(page);
  },

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
