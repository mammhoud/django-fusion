import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import type { RootState } from '@/store';

export interface RequestSessionState {
  token: string | null;
  refreshToken: string | null;
  sessionId: string | null;
  cookies: Record<string, string>;
  hydrated: boolean;
}

const initialState: RequestSessionState = {
  token: null,
  refreshToken: null,
  sessionId: null,
  cookies: {},
  hydrated: false,
};

function parseCookieHeader(cookieHeader = ''): Record<string, string> {
  return cookieHeader
    .split(';')
    .map((part) => part.trim())
    .filter(Boolean)
    .reduce<Record<string, string>>((cookies, part) => {
      const [name, ...valueParts] = part.split('=');
      if (name) {
        cookies[decodeURIComponent(name)] = decodeURIComponent(
          valueParts.join('='),
        );
      }
      return cookies;
    }, {});
}

export const sessionSlice = createSlice({
  name: 'requestSession',
  initialState,
  reducers: {
    hydrateFromRequest: (
      state,
      action: PayloadAction<{
        cookies?: Record<string, string>;
        token?: string | null;
        refreshToken?: string | null;
        sessionId?: string | null;
      }>,
    ) => {
      state.cookies = action.payload.cookies ?? {};
      state.token = action.payload.token ?? state.cookies.lms_token ?? null;
      state.refreshToken = action.payload.refreshToken ?? null;
      state.sessionId = action.payload.sessionId ?? state.cookies.sessionid ?? null;
      state.hydrated = true;
    },
    setTokens: (
      state,
      action: PayloadAction<{ access: string; refresh: string; expires_in?: number }>,
    ) => {
      state.token = action.payload.access;
      state.refreshToken = action.payload.refresh;
      // Also persist to localStorage for RTK Query baseApi fallback
      if (typeof window !== 'undefined') {
        localStorage.setItem('lms_token', action.payload.access);
        localStorage.setItem('lms_refresh_token', action.payload.refresh);
        if (action.payload.expires_in) {
          localStorage.setItem('lms_token_expiry', String(Date.now() + action.payload.expires_in * 1000));
        }
      }
    },
    hydrateFromCookieHeader: (state, action: PayloadAction<string>) => {
      const cookies = parseCookieHeader(action.payload);
      state.cookies = cookies;
      state.token = cookies.lms_token ?? state.token;
      state.sessionId = cookies.sessionid ?? state.sessionId;
      state.hydrated = true;
    },
    clearSession: () => {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('lms_token');
        localStorage.removeItem('lms_refresh_token');
        localStorage.removeItem('lms_token_expiry');
      }
      return initialState;
    },
  },
});

export const { hydrateFromRequest, hydrateFromCookieHeader, setTokens, clearSession } =
  sessionSlice.actions;
export const selectSession = (state: RootState) => state.requestSession;
export const selectSessionToken = (state: RootState) => state.requestSession.token;
export const selectSessionRefreshToken = (state: RootState) => state.requestSession.refreshToken;
export const selectSessionCookies = (state: RootState) => state.requestSession.cookies;
export const selectIsSessionHydrated = (state: RootState) => state.requestSession.hydrated;
export const sessionReducer = sessionSlice.reducer;
