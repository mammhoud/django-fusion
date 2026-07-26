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
