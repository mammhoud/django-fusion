import { store } from './index';
import { setPageData } from './pageSlice';
import { setSiteData, setTheme } from './siteSlice';
import { setConfig, type RenderModeInfo } from './configSlice';
import { setProducts } from './productsSlice';
import type { PageData, SiteSettings, NavItem, AssetManifest } from '../api';

interface FusionSiteData {
  siteSettings?: SiteSettings | null;
  navItems?: NavItem[];
  pageData?: PageData | null;
  pageSlug?: string;
  renderMode?: RenderModeInfo | null;
  assets?: AssetManifest | null;
}

function readSiteData(): FusionSiteData {
  const element = document.getElementById('fusion-site-data');
  if (!element?.textContent) return {};
  try {
    return JSON.parse(element.textContent) as FusionSiteData;
  } catch {
    return {};
  }
}

function removeHydrationState(): void {
  document.body.classList.remove('is-hydrating');
  store.dispatch({ type: 'site/setLoaded' });
}

const data = readSiteData();
const settings = data.siteSettings ?? null;
const navigation = data.navItems ?? [];

if (settings) {
  store.dispatch(setSiteData({ settings, navigation }));
} else {
  store.dispatch({ type: 'site/setLoaded' });
}

if (data.pageData && data.pageSlug) {
  store.dispatch(setPageData({ slug: data.pageSlug, data: data.pageData }));
}

// Preload the Wagtail product catalog into Redux whenever the page payload
// carries it (products page, home preview) — one source of truth for every
// listed product component.
if (data.pageData && Array.isArray(data.pageData.products) && data.pageData.products.length) {
  store.dispatch(setProducts(data.pageData.products as Parameters<typeof setProducts>[0]));
}

// Hydrate the architecture config slice — render mode + merged asset manifest
// (single source of truth for the fusion-render vs data-api road switch).
if (data.renderMode || data.assets) {
  store.dispatch(setConfig({ renderMode: data.renderMode ?? null, assets: data.assets ?? null }));
}

const initialTheme = document.documentElement.classList.contains('dark') ? 'dark' : 'light';
store.dispatch(setTheme(initialTheme));

(window as Window & { __reduxStore?: typeof store }).__reduxStore = store;
(window as Window & { __showToast?: (message: string, variant?: 'success' | 'error' | 'info' | 'warning') => void }).__showToast =
  (message, variant = 'success') => {
    store.dispatch({ type: 'toast/showToast', payload: { message, variant } });
    window.setTimeout(() => store.dispatch({ type: 'toast/hideToast' }), 3500);
  };

store.subscribe(() => {
  const theme = store.getState().site.theme;
  document.documentElement.classList.toggle('dark', theme === 'dark');
  document.documentElement.classList.toggle('light', theme !== 'dark');
});

document.addEventListener('alpine:initialized', removeHydrationState, { once: true });
window.setTimeout(removeHydrationState, 3000);
