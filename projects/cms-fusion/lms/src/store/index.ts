/**
 * LMS Redux Store — centralized state with RTK Query.
 *
 * Mirrors the POS project's store pattern:
 *   - RTK Query for REST API calls (auto-caching, pagination, invalidation)
 *   - Typed hooks for use throughout the app
 */

import { configureStore } from '@reduxjs/toolkit';
import { api } from './api/baseApi';
import { sessionReducer } from './session/sessionSlice';

export const store = configureStore({
  reducer: {
    [api.reducerPath]: api.reducer,
    requestSession: sessionReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(api.middleware),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
