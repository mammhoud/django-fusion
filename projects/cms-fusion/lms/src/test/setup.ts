// ── jest-dom custom matchers (e.g. toBeInTheDocument) ───────────
import '@testing-library/jest-dom/vitest';

// ── Mock sessionStorage ─────────────────────────────────────────
const store: Record<string, string> = {};

const mockStorage: Storage = {
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
};

Object.defineProperty(globalThis, 'sessionStorage', {
  value: mockStorage,
  writable: true,
  configurable: true,
});

// ── Mock fetch (global) ─────────────────────────────────────────
globalThis.fetch = vi.fn() as unknown as typeof fetch;

// ── Cleanup between tests ───────────────────────────────────────
beforeEach(() => {
  vi.clearAllMocks();
  Object.keys(store).forEach((k) => delete store[k]);
});
