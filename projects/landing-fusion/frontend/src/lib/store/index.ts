/** Redux store — centralized state for the landing-fusion frontend.
 *
 *  Replaces scattered Alpine stores and module-level caches with
 *  a single Redux Toolkit store.  Slices:
 *    - site   → Wagtail settings, navigation, theme
 *    - toast  → notification toasts (replaces Alpine $store('toast'))
 *
 *  Usage in Astro script blocks:
 *    import { store } from '@/lib/store';
 *    store.dispatch(showToast({ message: 'Saved!', variant: 'success' }));
 *    store.subscribe(() => { /* update DOM from store.getState() * / });
 */
import { configureStore } from '@reduxjs/toolkit';
import siteReducer from './siteSlice';
import toastReducer from './toastSlice';
import pageReducer from './pageSlice';

export const store = configureStore({
  reducer: {
    site: siteReducer,
    toast: toastReducer,
    page: pageReducer,
  },
  devTools: import.meta.env.DEV,
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

export * from './siteSlice';
export * from './toastSlice';
export * from './pageSlice';
