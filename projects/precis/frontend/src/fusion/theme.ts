/**
 * Theme binding — precis.
 *
 * Wraps the shared `createTheme` module with the project storage key and
 * keeps the Redux store (`window.__reduxStore`) in sync with theme
 * changes so Toast/Header components stay consistent.
 */
import { createTheme } from '@fusion/modules/theme';
import { THEME_STORAGE_KEY } from '@/lib/site';

export const theme = createTheme({ storageKey: THEME_STORAGE_KEY });

// Sync theme → Redux (the Layout store subscriber already does Redux → DOM).
theme.subscribe((name) => {
  const store = (window as unknown as { __reduxStore?: { dispatch: (action: unknown) => void } })
    .__reduxStore;
  if (store) {
    store.dispatch({ type: 'site/setTheme', payload: name });
  }
});

export { createTheme };
export type { ThemeManager, ThemeName } from '@fusion/modules/theme';
