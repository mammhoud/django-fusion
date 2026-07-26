/**
 * Mock RTK Query API — replaces the real baseApi in integration tests.
 *
 * The `api` object mirrors the real one from `@/store/api/baseApi` but
 * uses a mock baseQuery that reads from the shared response registry
 * instead of making real HTTP calls.
 *
 * Usage:
 *
 *   // In your test file, before any imports:
 *   vi.mock('@/store/api/baseApi', () => import('@/test/mockApi'));
 *
 *   // Now all imports that use @/store/api/baseApi (like students.ts)
 *   // will get this mock API with the mock baseQuery.
 */

import { createApi, BaseQueryFn } from '@reduxjs/toolkit/query/react';
import { findMockResponse } from './responseRegistry';

// ═════════════════════════════════════════════════════════════════════
// Mock base query — reads from the shared response registry
// ═════════════════════════════════════════════════════════════════════

const mockBaseQuery: BaseQueryFn = async (args) => {
  const url = typeof args === 'string' ? args : args.url;
  const method = typeof args === 'string' ? 'GET' : (args.method || 'GET');

  const response = findMockResponse(method, url);

  if (response?.error) {
    // Simulate delay if configured
    if (response.delay) {
      await new Promise((r) => setTimeout(r, response.delay));
    }
    return {
      error: {
        status: response.error.status,
        data: response.error.data,
      },
    };
  }

  if (response?.data) {
    if (response.delay) {
      await new Promise((r) => setTimeout(r, response.delay));
    }
    return { data: response.data };
  }

  // No mock registered — return a helpful error
  return {
    error: {
      status: 404,
      data: `No mock response registered for ${method} ${url}. Use mockApiResponse() to register one.`,
    },
  };
};

// ═════════════════════════════════════════════════════════════════════
// Create the mock API — matches the shape of the real baseApi
// ═════════════════════════════════════════════════════════════════════

export interface PaginatedResponse<T> {
  results: T[];
  count: number;
  next: string | null;
  previous: string | null;
}

export const api = createApi({
  reducerPath: 'api',
  baseQuery: mockBaseQuery,
  tagTypes: [
    'Course', 'Category', 'Lesson', 'Module',
    'Student', 'Enrollment', 'Progress',
    'Instructor', 'Review', 'Rating',
    'Blog', 'BlogCategory',
    'Shop', 'Product', 'Order', 'Cart',
    'Event', 'EventRegistration',
    'Contact', 'Inquiry',
    'Quiz', 'Attempt', 'Question',
    'Assignment', 'Submission',
    'Announcement',
    'Wishlist',
    'Page',
    'Dashboard',
    'User', 'Auth',
  ],
  endpoints: () => ({}),
  keepUnusedDataFor: 60,
});
