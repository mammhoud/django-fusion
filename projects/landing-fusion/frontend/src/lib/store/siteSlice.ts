/** Redux slice for site-level data — settings, navigation, theme. */
import { createSlice, type PayloadAction } from '@reduxjs/toolkit';
import type { SiteSettings, NavItem } from '../api';

export interface SiteState {
  /** Wagtail-managed site settings */
  settings: SiteSettings | null;
  /** Wagtail navigation from published pages */
  navigation: NavItem[];
  /** Current theme: 'light' | 'dark' */
  theme: 'light' | 'dark';
  /** Whether site data has been loaded */
  loaded: boolean;
  /** Whether there was an error loading site data */
  error: string | null;
}

const initialState: SiteState = {
  settings: null,
  navigation: [],
  theme: 'light',
  loaded: false,
  error: null,
};

const siteSlice = createSlice({
  name: 'site',
  initialState,
  reducers: {
    setSettings(state, action: PayloadAction<SiteSettings>) {
      state.settings = action.payload;
    },
    setNavigation(state, action: PayloadAction<NavItem[]>) {
      state.navigation = action.payload;
    },
    setTheme(state, action: PayloadAction<'light' | 'dark'>) {
      state.theme = action.payload;
      try {
        localStorage.setItem('fusion-theme', action.payload);
      } catch {
        /* localStorage unavailable */
      }
    },
    setSiteData(
      state,
      action: PayloadAction<{
        settings: SiteSettings;
        navigation: NavItem[];
      }>
    ) {
      state.settings = action.payload.settings;
      state.navigation = action.payload.navigation;
      state.loaded = true;
      state.error = null;
    },
    setError(state, action: PayloadAction<string>) {
      state.error = action.payload;
      state.loaded = true;
    },
  },
});

export const { setSettings, setNavigation, setTheme, setSiteData, setError } =
  siteSlice.actions;
export default siteSlice.reducer;
