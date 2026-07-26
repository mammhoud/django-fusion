import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import type { RootState } from '@/store';

export interface RequestSessionState {
  token: string | null;
  sessionId: string | null;
  cookies: Record<string, string>;
  hydrated: boolean;
}

const initialState: RequestSessionState = {
  token: null,
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
        sessionId?: string | null;
      }>,
    ) => {
      state.cookies = action.payload.cookies ?? {};
      state.token = action.payload.token ?? state.cookies.lms_token ?? null;
      state.sessionId = action.payload.sessionId ?? state.cookies.sessionid ?? null;
      state.hydrated = true;
    },
    hydrateFromCookieHeader: (state, action: PayloadAction<string>) => {
      const cookies = parseCookieHeader(action.payload);
      state.cookies = cookies;
      state.token = cookies.lms_token ?? state.token;
      state.sessionId = cookies.sessionid ?? state.sessionId;
      state.hydrated = true;
    },
    clearSession: () => initialState,
  },
});

export const { hydrateFromRequest, hydrateFromCookieHeader, clearSession } =
  sessionSlice.actions;
export const selectSession = (state: RootState) => state.requestSession;
export const selectSessionToken = (state: RootState) => state.requestSession.token;
export const selectSessionCookies = (state: RootState) => state.requestSession.cookies;
export const selectIsSessionHydrated = (state: RootState) => state.requestSession.hydrated;
export const sessionReducer = sessionSlice.reducer;
