/** Redux slice for architecture config — render mode + unified asset manifest.
 *
 * Single source of truth for the two content-delivery roads:
 *   - `fusionRenderFirst` — the effective `fusion_render_first` preference
 *     (server-rendered components vs data-API rendering), mirrored from
 *     GET /apis/render-mode/ and GET /apis/assets/.
 *   - `assets` — the merged manifest (FUSION_ASSETS + webpack bundle links)
 *     served by GET /apis/assets/, so the Layout preloads exactly the same
 *     CSS/fonts/scripts the Django road renders (`{% fusion_top_assets %}`).
 *
 * Client-side components select this slice instead of re-reading env vars or
 * re-fetching, and the Layout's AssetPreload consumes `assets.top/bottom`.
 */
import { createSlice, type PayloadAction } from '@reduxjs/toolkit';
import type { AssetManifest } from '../api';

export interface RenderModeInfo {
  /** True → “fusion render first” (Django renders finished HTML). */
  fusion_render_first: boolean;
  /** 'fusion-render' | 'data-api' — derived human-readable mode. */
  mode: 'fusion-render' | 'data-api';
  /** Content pointers for the active road. */
  content: { html: string; data: string };
}

export interface ConfigState {
  /** Effective render mode (from /apis/render-mode/ or the SSR bridge). */
  renderMode: RenderModeInfo | null;
  /** Merged asset manifest (FUSION_ASSETS + webpack links) from /apis/assets/. */
  assets: AssetManifest | null;
  /** True once the render-mode preference has been resolved. */
  renderModeLoaded: boolean;
}

const initialState: ConfigState = {
  renderMode: null,
  assets: null,
  renderModeLoaded: false,
};

const configSlice = createSlice({
  name: 'config',
  initialState,
  reducers: {
    setRenderMode(state, action: PayloadAction<RenderModeInfo>) {
      state.renderMode = action.payload;
      state.renderModeLoaded = true;
    },
    setAssets(state, action: PayloadAction<AssetManifest>) {
      state.assets = action.payload;
    },
    /** Hydrate both from the SSR data bridge in one dispatch. */
    setConfig(
      state,
      action: PayloadAction<{
        renderMode?: RenderModeInfo | null;
        assets?: AssetManifest | null;
      }>
    ) {
      if (action.payload.renderMode) {
        state.renderMode = action.payload.renderMode;
        state.renderModeLoaded = true;
      }
      if (action.payload.assets) {
        state.assets = action.payload.assets;
      }
    },
  },
});

export const { setRenderMode, setAssets, setConfig } = configSlice.actions;
export default configSlice.reducer;
