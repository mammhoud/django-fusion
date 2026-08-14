/**
 * Formint Café — django-fusion site contract client.
 *
 * The backend exposes /fusion/navigation/, /fusion/branding/ and
 * /fusion/assets/ (see backend/shop/fusion.py). The storefront consumes them
 * so the header/footer branding and versions stay in sync with the Django
 * site config instead of hardcoded copies. Build-time fetches fall back to
 * the static site config when the backend is offline (astro build never
 * blocks); the Alpine shell re-fetches live in the browser.
 */
import { API_BASE, SHOP_NAME, SHOP_TAGLINE } from './site';

export interface FusionNavRoute {
  label: string;
  href: string;
  icon?: string;
  active?: boolean;
}

export interface FusionNavModule {
  id: string;
  label: string;
  icon?: string;
  active?: boolean;
  routes: FusionNavRoute[];
}

export interface FusionNavigation {
  brand: { label: string; href: string; tag: string };
  modules: FusionNavModule[];
}

export interface FusionBranding {
  site: { name: string; tagline: string; language: string };
  palette: Record<string, string>;
}

export interface FusionAssets {
  version: string;
  static_url: string;
  fusion_render_first: boolean;
  enabled: boolean;
  webpack_enabled: boolean;
  webpack_bundle_dir: string;
  top: Record<string, unknown>;
  bottom: Record<string, unknown>;
  fonts: string[];
  preconnect: string[];
}

async function fetchJSON<T>(path: string): Promise<T> {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, { headers: { Accept: 'application/json' } });
  if (!res.ok) {
    throw new Error(`API ${path} returned ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export async function fetchFusionNavigation(): Promise<FusionNavigation | null> {
  try {
    return await fetchJSON<FusionNavigation>('/fusion/navigation/');
  } catch {
    return null;
  }
}

export async function fetchFusionBranding(): Promise<FusionBranding | null> {
  try {
    return await fetchJSON<FusionBranding>('/fusion/branding/');
  } catch {
    return {
      site: { name: SHOP_NAME, tagline: SHOP_TAGLINE, language: 'en' },
      palette: {},
    };
  }
}

export async function fetchFusionAssets(): Promise<FusionAssets | null> {
  try {
    return await fetchJSON<FusionAssets>('/fusion/assets/');
  } catch {
    return null;
  }
}
