// configSlice — fusion render-mode switch.
//
// renderMode mirrors the django-fusion FUSION_RENDER_FIRST flag on the client:
//   'html'  → server-rendered road (HTML already in the document)
//   'data'  → data-API road (fetch JSON and hydrate islands from Redux)
// The switch lets components pick the correct road without duplicating logic.
import { createSlice, type PayloadAction } from '@reduxjs/toolkit';

export type RenderMode = 'html' | 'data';

export interface ConfigState {
  renderMode: RenderMode;
  backendUrl: string;
  apiPrefix: string;
  fallbackApiPrefix: string;
}

const initialState: ConfigState = {
  renderMode: 'html',
  backendUrl: import.meta.env.PUBLIC_BACKEND_URL ?? 'http://127.0.0.1:8000',
  // Canonical API road: /bolt when the django-bolt runtime is installed,
  // /apis/core/ (named road) when it is not. /api/v1 is the deprecated fallback.
  apiPrefix: import.meta.env.PUBLIC_API_PREFIX ?? '/bolt',
  fallbackApiPrefix: import.meta.env.PUBLIC_API_FALLBACK_PREFIX ?? '/api/v1',
};

const configSlice = createSlice({
  name: 'config',
  initialState,
  reducers: {
    setRenderMode(state, action: PayloadAction<RenderMode>) {
      state.renderMode = action.payload;
    },
  },
});

export const { setRenderMode } = configSlice.actions;
export default configSlice.reducer;
