/**
 * RTK Query base API — single source of truth for all LMS REST endpoints.
 *
 * Mirrors the POS project's baseApi.ts pattern.
 * Includes automatic JWT refresh on 401 responses.
 */

import {
  createApi,
  fetchBaseQuery,
  BaseQueryFn,
  FetchArgs,
  FetchBaseQueryError,
} from '@reduxjs/toolkit/query/react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface PaginatedResponse<T> {
  results: T[];
  count: number;
  next: string | null;
  previous: string | null;
}

/**
 * Get the access token from localStorage (non-Redux fallback path).
 */
function getAccessToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('lms_token');
}

/**
 * Get the refresh token from localStorage.
 */
function getRefreshToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('lms_refresh_token');
}

/**
 * Attempt to refresh the JWT access token using the refresh token.
 * Returns the new access token or null on failure.
 */
async function attemptTokenRefresh(): Promise<{ access: string; refresh: string; expires_in: number } | null> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) return null;

  try {
    const response = await fetch(`${API_BASE}/apis/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh: refreshToken }),
    });

    if (!response.ok) {
      // Refresh failed — clear all tokens
      localStorage.removeItem('lms_token');
      localStorage.removeItem('lms_refresh_token');
      localStorage.removeItem('lms_token_expiry');
      return null;
    }

    const data = await response.json();
    // The backend returns AuthTokenResponse with access, refresh, user, expires_in
    const result = {
      access: data.access,
      refresh: data.refresh || refreshToken,
      expires_in: data.expires_in || 1800,
    };

    // Persist new tokens
    localStorage.setItem('lms_token', result.access);
    localStorage.setItem('lms_refresh_token', result.refresh);
    localStorage.setItem('lms_token_expiry', String(Date.now() + result.expires_in * 1000));

    return result;
  } catch {
    return null;
  }
}

/**
 * Custom base query with automatic JWT refresh on 401.
 *
 * Flow:
 * 1. Send the request with the current access token
 * 2. If 401, try to refresh using the refresh token
 * 3. If refresh succeeds, retry the original request with the new access token
 * 4. If refresh fails, clear auth state and propagate the 401
 */
const baseQueryWithRefresh: BaseQueryFn<
  string | FetchArgs,
  unknown,
  FetchBaseQueryError
> = async (args, api, extraOptions) => {
  const baseQuery = fetchBaseQuery({
    baseUrl: API_BASE,
    prepareHeaders: (headers, { getState }) => {
      const state = getState() as {
        requestSession?: { token?: string | null };
      };
      const token =
        state.requestSession?.token ?? getAccessToken();
      if (token) {
        headers.set('Authorization', `Bearer ${token}`);
      }
      return headers;
    },
  });

  let result = await baseQuery(args, api, extraOptions);

  // ── If 401, attempt token refresh and retry ──
  if (result.error && result.error.status === 401) {
    const tokens = await attemptTokenRefresh();

    if (tokens) {
      // Update Redux store if available
      const { setTokens } = await import('@/store/session/sessionSlice');
      api.dispatch(setTokens({
        access: tokens.access,
        refresh: tokens.refresh,
        expires_in: tokens.expires_in,
      }));

      // Retry the original request with the new access token
      result = await baseQuery(args, api, extraOptions);
    } else {
      // Refresh failed — clear session
      const { clearSession } = await import('@/store/session/sessionSlice');
      api.dispatch(clearSession());
    }
  }

  return result;
};

export const api = createApi({
  reducerPath: 'api',
  baseQuery: baseQueryWithRefresh,
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
    'Withdrawal',
    'Notification',
    'NotificationPrefs',
  ],
  endpoints: () => ({}),
  keepUnusedDataFor: 60,
});
