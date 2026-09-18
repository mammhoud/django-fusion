/**
 * Mock for @tauri-apps/api/core — used in vitest tests running in jsdom.
 *
 * Provides a stub `invoke` function that returns sensible defaults for
 * common Tauri commands. Tests can customize behavior via window.__TAURI_MOCKS__.
 */

type InvokeHandler = (args?: Record<string, unknown>) => unknown;

declare global {
  interface Window {
    __TAURI_MOCKS__?: Map<string, InvokeHandler>;
    __TAURI_INVOKE_CALLS__?: Array<{ cmd: string; args?: Record<string, unknown> }>;
  }
}

if (typeof window !== 'undefined') {
  window.__TAURI_INVOKE_CALLS__ = [];
  window.__TAURI_MOCKS__ = new Map();
}

export async function invoke<T = unknown>(
  cmd: string,
  args?: Record<string, unknown>,
): Promise<T> {
  // Track calls for assertions
  if (typeof window !== 'undefined' && window.__TAURI_INVOKE_CALLS__) {
    window.__TAURI_INVOKE_CALLS__.push({ cmd, args });
  }

  // Check for registered mock handler
  const mocks = typeof window !== 'undefined' ? window.__TAURI_MOCKS__ : undefined;
  if (mocks) {
    const handler = mocks.get(cmd) ?? mocks.get('*');
    if (handler) return (await handler(args)) as T;
  }

  // Sensible defaults for common commands
  const defaults: Record<string, unknown> = {
    get_products: [],
    get_customers: [],
    get_sales: [],
    get_employees: [],
    get_inventory: [],
    get_categories: [],
    get_settings: {},
    get_current_user: null,
    check_auth_required: { required: false, email: null },
    has_users: false,
    get_sidebar_items: [],
    get_recent_sales: [],
    get_dashboard_stats: { total_sales: 0, total_products: 0, total_customers: 0 },
    get_analytics: { revenue: [], orders: [], top_products: [] },
    get_suppliers: [],
    get_delivery_types: [],
    get_ingredients: [],
    get_inventory_transactions: [],
    get_recipes: [],
    get_transactions: [],
  };

  if (cmd in defaults) return defaults[cmd] as T;

  // For unknown commands, return null
  console.warn(`[tauri-mock] No handler for command: ${cmd}`);
  return null as T;
}

// Re-export other commonly used Tauri utilities as stubs
export const convertFileSrc = (filePath: string) => filePath;
export const transformCallback = <T>(callback?: (response: T) => void) => callback;
