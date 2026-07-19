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



// Mock the Tauri `invoke` function so all tests can call it.
// The mock implementation delegates to the configurable mock from mocks/tauri.ts
vi.mock('@tauri-apps/api/core', () => ({
  invoke: vi.fn((cmd: string, args?: Record<string, unknown>) => {
    const handler = getMockInvokeHandler(cmd);
    return handler(cmd, args);
  }),
}));
