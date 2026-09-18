/**
 * Precis Landing site configuration — config only, no static content.
 *
 * All content (branding, navigation, footer links, contact methods, page data)
 * comes from the Wagtail/django-fusion backend via src/lib/api.ts.
 * This file holds only runtime config: URLs, theme keys, and environment vars.
 */

/** Theme localStorage key — shared between Layout.astro (FOUC-free init) and ThemeToggle.astro. */
export const THEME_STORAGE_KEY = 'fusion-theme';

/**
 * Server-side backend URL. Never use this value in browser-rendered HTML:
 * Compose service names are only resolvable inside the Docker network.
 */
export const fusionApiUrl: string =
  (import.meta.env.PUBLIC_FUSION_API_URL as string | undefined) ?? '';

/** Browser-safe public origin. Empty means same-origin production routing. */
export const browserApiUrl: string =
  (import.meta.env.PUBLIC_BROWSER_API_URL as string | undefined) ?? '';

/** Build a browser URL for a backend-owned path without leaking Docker DNS. */
export function browserEndpoint(path: string): string {
  const normalized = `/${path.replace(/^\/+/, '')}`;
  return `${browserApiUrl.replace(/\/+$/, '')}${normalized}`;
}

/** Fallback site name (used only when the backend is unreachable). */
export const fallbackSiteName = 'Structa Cloud';

/** Fallback OG image path. */
export const ogImage = '/favicon.svg';
