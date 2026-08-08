/**
 * Landing-fusion site configuration — config only, no static content.
 *
 * All content (branding, navigation, footer links, contact methods, page data)
 * comes from the Wagtail/django-fusion backend via src/lib/api.ts.
 * This file holds only runtime config: URLs, theme keys, and environment vars.
 */

/** Theme localStorage key — shared between Layout.astro (FOUC-free init) and ThemeToggle.astro. */
export const THEME_STORAGE_KEY = 'fusion-theme';

/** Backend API base URL; empty means the current host via Traefik. */
export const fusionApiUrl: string =
  (import.meta.env.PUBLIC_FUSION_API_URL as string | undefined) || '';

/** Canonical public URL used for SEO metadata and social previews. */
export const siteUrl: string =
  (import.meta.env.PUBLIC_SITE_URL as string | undefined) || 'https://ctc-research.com';

/** Fallback site name (used only when the backend is unreachable). */
export const fallbackSiteName = 'Fusion LMS';

/** Fallback OG image path. */
export const ogImage = '/favicon.svg';
