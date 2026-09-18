import '@testing-library/jest-dom';
import { vi } from 'vitest';
import { getMockInvokeHandler } from './mocks/tauri';
import en from '../i18n/en.json';

// ---------------------------------------------------------------------------
// i18n – mock the whole module so components & contexts don't trigger
// react-i18next dependency resolution during tests.
//
// The mock resolves REAL en.json translations (with `{var}` interpolation to
// mirror src/i18n/index.ts), so tests can assert user-visible English text
// instead of raw i18n keys. Unknown keys fall back to the key itself.
// This lives in setup.ts (NOT test-utils.tsx) because some test files
// (e.g. Settings.test.tsx) import `render` directly from @testing-library/react
// and never go through renderWithRouter, so a per-file mock wouldn't apply.
// ---------------------------------------------------------------------------
const { mockChangeLanguage, mockOn, mockOff } = vi.hoisted(() => ({
  mockChangeLanguage: vi.fn(),
  mockOn: vi.fn(),
  mockOff: vi.fn(),
}));

function resolveTranslation(key: string, options?: Record<string, unknown> | string): string {
  let node: unknown = en;
  const parts = key.split('.');
  for (const part of parts) {
    if (node && typeof node === 'object' && part in node) {
      node = (node as Record<string, unknown>)[part];
    } else {
      return key;
    }
  }
  if (typeof node !== 'string') return key;
  // Interpolate {currency} / {{year}} style variables (src/i18n uses single braces)
  const opts = options && typeof options === 'object' ? options : undefined;
  return node.replace(/\{+([a-zA-Z0-9_]+)\}+/g, (match, name: string) =>
    opts && name in opts ? String(opts[name]) : match,
  );
}

vi.mock('../i18n', () => ({
  __esModule: true,
  default: {
    language: 'en',
    changeLanguage: mockChangeLanguage,
    on: mockOn,
    off: mockOff,
    dir: () => 'ltr',
    use: () => ({
      init: vi.fn(),
    }),
    t: (key: string, options?: Record<string, unknown> | string) => resolveTranslation(key, options),
  },
}));

vi.mock('react-i18next', () => ({
  initReactI18next: { type: '3rdParty', init: () => {} },
  useTranslation: () => ({
    t: (key: string, options?: Record<string, unknown> | string) => resolveTranslation(key, options),
    i18n: {
      language: 'en',
      changeLanguage: mockChangeLanguage,
      on: mockOn,
      off: mockOff,
      dir: () => 'ltr',
    },
  }),
}));

// AuthContext mocks are handled in mocks/tauri.ts defaultMock fallback.

// Polyfill window.matchMedia and Element.scrollIntoView (not available in jsdom)
Element.prototype.scrollIntoView = vi.fn();

// ---------------------------------------------------------------------------
// HTMLDialogElement polyfill — jsdom (v29) does not implement show()/showModal()/
// close(), so native <dialog> flows (KeyboardShortcutsModal,
// ThemePreviewModal) would throw on open and RTL would treat closed-dialog content
// as hidden. Mirror the spec: showModal/show set `open`, close removes it.
// ---------------------------------------------------------------------------
if (typeof window !== 'undefined' && window.HTMLDialogElement) {
  const dialogProto = window.HTMLDialogElement.prototype as HTMLDialogElement & {
    show?: () => void;
    showModal?: () => void;
    close?: () => void;
  };
  if (!dialogProto.showModal) {
    dialogProto.showModal = function (this: HTMLDialogElement) {
      this.setAttribute('open', '');
    };
  }
  if (!dialogProto.show) {
    dialogProto.show = function (this: HTMLDialogElement) {
      this.setAttribute('open', '');
    };
  }
  if (!dialogProto.close) {
    dialogProto.close = function (this: HTMLDialogElement) {
      this.removeAttribute('open');
      this.dispatchEvent(new Event('close'));
    };
  }
}

// Simulate a Tauri runtime so pages that gate on `__TAURI_INTERNALS__`
// (e.g. Auth's browser-mode check) take the mocked-invoke path instead of
// short-circuiting. See src/pages/auth/Auth.tsx `isBrowserMode`.
Object.defineProperty(window, '__TAURI_INTERNALS__', {
  writable: true,
  value: {},
});

Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated
    removeListener: vi.fn(), // deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});



// ── Invoke call history (for assertion in invoke.test.ts) ────────
const _invokeHistory: Array<{ cmd: string; args?: Record<string, unknown> }> = [];
export function getInvokeHistory() { return _invokeHistory; }
export function clearInvokeHistory() { _invokeHistory.length = 0; }

// Mock SVG/assets imports — Vite resolves these to URLs in dev, but jsdom has no Vite server
vi.mock('@formints-assets/images/formint-crest.svg', () => ({ default: 'mock-logo-url' }));

// Mock Tauri event API (listen/emit) — pages like Sale and ChatSupport
// ChatSupport call `listen(...)` on mount. Without a mock, the real module
// throws `transformCallback is not defined` in jsdom (unhandled rejection)
// which crashes the whole test file.
// IMPORTANT: Use plain functions, NOT vi.fn() — vi.clearAllMocks() in test
// files resets vi.fn() implementations (see note on the invoke mock above).
vi.mock('@tauri-apps/api/event', () => ({
  listen: () => Promise.resolve(() => {}),
  emit: () => Promise.resolve(),
  once: () => Promise.resolve(() => {}),
}));

// Mock Tauri plugins that some pages import directly (e.g. Settings, InvoicePage)
vi.mock('@tauri-apps/plugin-dialog', () => ({
  open: vi.fn().mockResolvedValue(null),
  save: vi.fn().mockResolvedValue('/tmp/test-file.pdf'),
}));

vi.mock('@tauri-apps/plugin-fs', () => ({
  readFile: vi.fn().mockResolvedValue(new Uint8Array()),
  writeFile: vi.fn().mockResolvedValue(undefined),
}));

// Mock the Tauri `invoke` function so all tests can call it.
// The mock implementation delegates to the configurable mock from mocks/tauri.ts
// IMPORTANT: Use a plain function, NOT vi.fn(). vi.clearAllMocks() in
// test files resets vi.fn() implementations, breaking ALL data loading.
vi.mock('@tauri-apps/api/core', () => ({
  invoke: (cmd: string, args?: Record<string, unknown>) => {
    _invokeHistory.push({ cmd, args });
    const handler = getMockInvokeHandler(cmd);
    return handler(cmd, args);
  },
}));
