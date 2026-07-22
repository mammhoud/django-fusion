/**
 * RTK Query base API — single source of truth for all LMS REST endpoints.
 *
 * Mirrors the POS project's baseApi.ts pattern.
 * All entity endpoints inject into this base API via injectEndpoints.
 */

import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface PaginatedResponse<T> {
  results: T[];
  count: number;
  next: string | null;
  previous: string | null;
}

export const api = createApi({
  reducerPath: 'api',
  baseQuery: fetchBaseQuery({
    baseUrl: API_BASE,
    prepareHeaders: (headers) => {
      const token = typeof window !== 'undefined' ? localStorage.getItem('lms_token') : null;
      if (token) {
        headers.set('Authorization', `Bearer ${token}`);
      }
      return headers;
    },
  }),
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
    'Dashboard',
    'User', 'Auth',
  ],
  endpoints: () => ({}),
  keepUnusedDataFor: 60,
});
