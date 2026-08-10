/**
 * Shared mock for Tauri's `invoke` API used in Playwright e2e tests.
 *
 * Call `setupTauriMock` in each test's `page.addInitScript` to define
 * `window.__TAURI_INTERNALS__` before the React app mounts, so that
 * `@tauri-apps/api/core`'s `invoke` resolves with realistic data.
 *
 * Usage in a spec:
 * ```ts
 * await page.addInitScript({ path: './e2e/mocks/tauri.ts' });
 * ```
 *
 * The mock uses a global `window.__TAURI_MOCK__` map that can be updated
 * via `page.evaluate()` before navigation if a test needs custom responses.
 */

// Default mock responses for all invoke commands used by the Auth page.
// Tests can override individual entries before navigating.
const DEFAULT_RESPONSES: Record<string, unknown> = {
  check_auth_required: true,
  has_users: false,
  get_superuser_email: null,
};

// Expose a setter tests can call before navigating
(window as Record<string, unknown>).__TAURI_MOCK_SET__ = (cmd: string, value: unknown) => {
  (window as Record<string, unknown>).__TAURI_MOCK__ = {
    ...((window as Record<string, unknown>).__TAURI_MOCK__ as Record<string, unknown> || {}),
    [cmd]: value,
  };
};

// Seed the default map
(window as Record<string, unknown>).__TAURI_MOCK__ = { ...DEFAULT_RESPONSES };

// Tauri v2 internals — the `invoke` function the app uses
(window as Record<string, unknown>).__TAURI_INTERNALS__ = {
  invoke: (cmd: string, args?: Record<string, unknown>) => {
    const mockMap = (window as Record<string, unknown>).__TAURI_MOCK__ as Record<string, unknown> || {};
    const value = mockMap[cmd];

    if (value === undefined) {
      console.warn(`[tauri-mock] No mock response for "${cmd}" — returning null`);
      return Promise.resolve(null);
    }

    if (value instanceof Error) {
      return Promise.reject(value);
    }

    return Promise.resolve(value);
  },
  // Minimal stub to prevent TypeError from @tauri-apps/api/core
  convertFileSrc: (path: string) => `https://asset.local/${path}`,
};

// NOTE: no `export {}` here — this file is evaluated by Playwright's
// `page.addInitScript({ path })` as a plain script, not an ES module.
