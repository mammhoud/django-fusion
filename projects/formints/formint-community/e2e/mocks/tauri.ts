/**
 * Shared mock for Tauri's `invoke` API used in Playwright e2e tests.
 *
 * Define `window.__TAURI_INTERNALS__` before the React app mounts so that
 * `@tauri-apps/api/core`'s `invoke` resolves with realistic data.
 *
 * Usage in a spec:
 * ```ts
 * await page.addInitScript({ path: './e2e/mocks/tauri.ts' });
 * ```
 *
 * The mock uses a global `window.__TAURI_MOCK__` map that can be updated
 * via `window.__TAURI_MOCK_SET__` in a later init script or page.evaluate().
 *
 * NOTE: this file is evaluated by `page.addInitScript({ path })` as a PLAIN
 * script in the browser — it must stay valid JavaScript (no TS annotations).
 */

// Default mock responses for all invoke commands used by the Auth page.
// Tests can override individual entries before navigating.
var DEFAULT_RESPONSES = {
  check_auth_required: true,
  has_users: false,
  get_superuser_email: null,
};

// Expose a setter tests can call before navigating.
window.__TAURI_MOCK_SET__ = function (cmd, value) {
  var current = window.__TAURI_MOCK__ || {};
  current[cmd] = value;
  window.__TAURI_MOCK__ = current;
};

// Seed the default map.
window.__TAURI_MOCK__ = Object.assign({}, DEFAULT_RESPONSES);

// Minimal callback bridge for @tauri-apps/api/event (listen/once).
function tauriTransformCallback(callback) {
  var key = 'c_' + Math.random().toString(36).slice(2);
  window[key] = callback;
  return key;
}

// Tauri v2 internals — the `invoke` function the app uses.
window.__TAURI_INTERNALS__ = {
  invoke: function (cmd, args) {
    var mockMap = window.__TAURI_MOCK__ || {};
    var value = mockMap[cmd];

    if (value === undefined) {
      console.warn('[tauri-mock] No mock response for "' + cmd + '" — returning null');
      return Promise.resolve(null);
    }

    if (value instanceof Error) {
      return Promise.reject(value);
    }

    return Promise.resolve(value);
  },
  // Minimal stubs to prevent TypeErrors from @tauri-apps/api/core + event.
  convertFileSrc: function (path) {
    return 'https://asset.local/' + path;
  },
  transformCallback: tauriTransformCallback,
};
