import '@testing-library/jest-dom';
import { vi } from 'vitest';
import { getMockInvokeHandler } from './mocks/tauri';

// Polyfill window.matchMedia (not available in jsdom)
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// ── Mock sessionStorage (needed by Fusion components) ─────────────
const store: Record<string, string> = {};

Object.defineProperty(globalThis, 'sessionStorage', {
  value: {
    getItem: vi.fn((key: string) => store[key] ?? null),
    setItem: vi.fn((key: string, value: string) => {
      store[key] = value;
    }),
    removeItem: vi.fn((key: string) => {
      delete store[key];
    }),
    clear: vi.fn(() => {
      Object.keys(store).forEach((k) => delete store[k]);
    }),
    get length() {
      return Object.keys(store).length;
    },
    key: vi.fn((index: number) => Object.keys(store)[index] ?? null),
  } as Storage,
  writable: true,
  configurable: true,
});

// ── Mock fetch (global) — needed by FusionProxy ──────────────────
globalThis.fetch = vi.fn() as unknown as typeof fetch;

// ── Cleanup between tests ────────────────────────────────────────
beforeEach(() => {
  vi.clearAllMocks();
  Object.keys(store).forEach((k) => delete store[k]);
  _pluginStoreData.clear();
});

// ── Invoke call history (for assertion in invoke.test.ts) ────────
const _invokeHistory: Array<{ cmd: string; args?: Record<string, unknown> }> = [];
export function getInvokeHistory() { return _invokeHistory; }
export function clearInvokeHistory() { _invokeHistory.length = 0; }

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

// @tauri-apps/plugin-store is already aliased in vitest.config.ts,
// so the vi.mock below is only a fallback. Remove once alias is
// confirmed working in all environments.
const _pluginStoreData = new Map<string, unknown>();
vi.mock('@tauri-apps/plugin-store', () => ({
  Store: {
    load: vi.fn().mockResolvedValue({
      get: async (key: string) => _pluginStoreData.get(key) ?? null,
      set: async (key: string, value: unknown) => { _pluginStoreData.set(key, value); },
      save: async () => {},
      delete: async (key: string) => { _pluginStoreData.delete(key); },
    }),
  },
}));
