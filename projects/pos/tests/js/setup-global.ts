/**
 * Global vitest setup for unified POS test directory.
 *
 * Polyfills browser APIs not available in jsdom and sets up
 * shared mocks (matchMedia, ResizeObserver, scrollTo, etc.).
 *
 * @tauri-apps mocks are handled via resolve.alias in vitest.config.ts
 * (mocks/tauri-api-core.ts, mocks/tauri-plugin-dialog.ts, mocks/tauri-plugin-fs.ts)
 *
 * NOTE: @testing-library/jest-dom is NOT imported here to avoid
 * requiring it as a project dependency. Individual test files
 * that need jest-dom matchers should import it directly.
 */
import { vi } from 'vitest';

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

// Mock ResizeObserver
class ResizeObserverMock {
  observe = vi.fn();
  unobserve = vi.fn();
  disconnect = vi.fn();
}
vi.stubGlobal('ResizeObserver', ResizeObserverMock);

// Mock scrollTo
window.scrollTo = vi.fn() as any;
