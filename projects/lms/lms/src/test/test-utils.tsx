/**
 * Integration test utilities — configures a real Redux store with RTK Query
 * using a mock base query so tests exercise the full Redux middleware stack
 * without making real HTTP calls.
 *
 * Usage:
 *
 *   // First, mock the baseApi module so students.ts uses our mock API:
 *   vi.mock('@/store/api/baseApi', () => import('@/test/mockApi'));
 *
 *   // Then register expected API responses
 *   mockApiResponse('POST', '/apis/enrollments', { id: 1, ... });
 *
 *   // Render hook with the test store
 *   const { result } = renderHookWithStore(() => useCheckout({ courseId: 42, price: 49.99 }));
 *
 *   // Clear between tests
 *   beforeEach(() => clearApiResponses());
 */

import { renderHook, RenderHookOptions, RenderHookResult } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore, Middleware } from '@reduxjs/toolkit';
import { api } from './mockApi';
import { sessionReducer } from '@/store/session/sessionSlice';
import React from 'react';

export { mockApiResponse, mockApiError, clearApiResponses } from './responseRegistry';

// ═════════════════════════════════════════════════════════════════════
// Test store factory
// ═════════════════════════════════════════════════════════════════════

let testStore: ReturnType<typeof createTestStore> | null = null;

function createTestStore() {
  const store = configureStore({
    reducer: {
      [api.reducerPath]: api.reducer,
      requestSession: sessionReducer,
    },
    middleware: (getDefaultMiddleware) =>
      getDefaultMiddleware().concat(api.middleware as Middleware),
  });

  return store;
}

/**
 * Get or create the test store. Creates a new one on first call.
 */
export function getTestStore() {
  if (!testStore) {
    testStore = createTestStore();
  }
  return testStore;
}

/**
 * Reset the test store (creates a new one).
 */
export function resetTestStore() {
  testStore = createTestStore();
}

// ═════════════════════════════════════════════════════════════════════
// Test wrapper
// ═════════════════════════════════════════════════════════════════════

interface WrapperOptions {
  store?: ReturnType<typeof createTestStore>;
}

function createWrapper(options?: WrapperOptions): React.FC<{ children: React.ReactNode }> {
  const store = options?.store || getTestStore();

  return function Wrapper({ children }: { children: React.ReactNode }) {
    return React.createElement(Provider, { store, children });
  };
}

/**
 * Render a hook wrapped in a Redux Provider with the test store.
 */
export function renderHookWithStore<Result, Props>(
  hook: (props: Props) => Result,
  options?: RenderHookOptions<Props> & WrapperOptions,
): RenderHookResult<Result, Props> {
  const wrapper = createWrapper(options);

  return renderHook(hook, {
    ...options,
    wrapper,
  });
}

// ═════════════════════════════════════════════════════════════════════
// Window location helpers
// ═════════════════════════════════════════════════════════════════════

export function captureWindowLocation(): string {
  const original = window.location.href;
  Object.defineProperty(window, 'location', {
    value: { href: '' },
    writable: true,
    configurable: true,
  });
  return original;
}

export function restoreWindowLocation(original: string) {
  Object.defineProperty(window, 'location', {
    value: { href: original },
    writable: true,
    configurable: true,
  });
}
