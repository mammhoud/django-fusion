/** FormintC purchase app — site config + backend URL resolution. */

/** Base URL for the Django backend. Dev default is the proxied same-origin
 * path (Astro dev proxies /api, /shop, /accounts to :8075). */
export const API_BASE: string =
  (import.meta.env.PUBLIC_FUSION_API_URL as string | undefined) ||
  '';

export const browserApiUrl = API_BASE || 'http://localhost:4322';

/** Build a same-origin browser endpoint (used by Alpine fetch calls). */
export function browserEndpoint(path: string): string {
  const base = browserApiUrl.replace(/\/$/, '');
  return `${base}${path}`;
}

export const SHOP_NAME = 'The Daily Grind';
export const SHOP_TAGLINE = 'Roasted to order. Brewed to the table.';
export const SHOP_OPEN_HOURS = 'Mon–Sun · 7:00 → 19:00';

export const THEME_STORAGE_KEY = 'formintc-theme';
