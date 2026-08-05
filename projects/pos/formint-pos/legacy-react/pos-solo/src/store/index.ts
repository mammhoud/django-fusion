/**
 * POS-KO Redux Store — centralized state with RTK Query + WebSocket middleware.
 *
 * Replaces all 24 Zustand stores. Provides:
 *   - RTK Query for REST API calls (auto-caching, pagination, invalidation)
 *   - WebSocket middleware for real-time entity events from Robyn sidecar
 *   - Typed hooks for use throughout the app
 */

import { configureStore } from '@reduxjs/toolkit';
import { api } from './api/baseApi';
import { websocketMiddleware } from './middleware/websocket';

export const store = configureStore({
  reducer: {
    [api.reducerPath]: api.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(api.middleware, websocketMiddleware),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
