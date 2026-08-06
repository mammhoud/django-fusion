/** Redux slice for per-page data — hero, CTA, stats, features, etc.
 *
 * Each Astro page embeds its backend-fetched data as a JSON bridge
 * in the HTML. The Layout's inline Redux script reads the bridge
 * and dispatches `setPageData` to hydrate this slice.
 *
 * Client-side components can then select `store.getState().page`
 * instead of re-fetching from the API.
 */
import { createSlice, type PayloadAction } from '@reduxjs/toolkit';
import type { PageData } from '../api';

export interface PageState {
  /** The current page's full data from /apis/pages/<slug>/ */
  current: PageData | null;
  /** Cache of previously visited pages keyed by slug */
  cache: Record<string, PageData>;
  /** Loading state */
  loading: boolean;
  /** Error message if fetch failed */
  error: string | null;
}

const initialState: PageState = {
  current: null,
  cache: {},
  loading: false,
  error: null,
};

const pageSlice = createSlice({
  name: 'page',
  initialState,
  reducers: {
    /** Set the current page data (from SSR JSON bridge or API call) */
    setPageData(state, action: PayloadAction<{ slug: string; data: PageData }>) {
      const { slug, data } = action.payload;
      state.current = data;
      state.cache[slug] = data;
      state.loading = false;
      state.error = null;
    },
    /** Mark page data as loading */
    setPageLoading(state) {
      state.loading = true;
      state.error = null;
    },
    /** Set an error when page data fails to load */
    setPageError(state, action: PayloadAction<string>) {
      state.error = action.payload;
      state.loading = false;
    },
  },
});

export const { setPageData, setPageLoading, setPageError } = pageSlice.actions;
export default pageSlice.reducer;
