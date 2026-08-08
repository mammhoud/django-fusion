import { staticPageData } from './content-translations';
import type { LangCode } from './translations';

export const SUPPORTED_LANGUAGE_CODES: LangCode[] = ['en', 'ar', 'sv', 'fr', 'de', 'es', 'pt'];

/**
 * Landing-fusion API client — fetches all data from the Wagtail/django-fusion backend.
 *
 * Every piece of content (branding, navigation, page data, contact info,
 * footer links) comes from the backend via these endpoints. No content is
 * hardcoded in the frontend — site.ts holds only config (URLs, keys).
 *
 * Backend endpoints (see apps/pages/api.py):
 *   GET /apis/site/settings/   — branding, social links, footer
 *   GET /apis/navigation/      — nav links from published pages
 *   GET /apis/contact/         — contact methods + form
 *   GET /apis/pages/<slug>/    — full page data (JSON)
 *   GET /apis/pages/           — page list
 */

/** Build-time content locale for static Astro output (override with PUBLIC_CONTENT_LANGUAGE=ar). */
export const CONTENT_LANGUAGE: LangCode = (() => {
  const requested = import.meta.env.PUBLIC_CONTENT_LANGUAGE as string | undefined;
  return requested && SUPPORTED_LANGUAGE_CODES.includes(requested as LangCode)
    ? (requested as LangCode)
    : 'en';
})();

/** Base URL for the Django backend. Set PUBLIC_FUSION_API_URL env var to override. */
export const API_BASE: string =
  (import.meta.env.PUBLIC_FUSION_API_URL as string | undefined) ||
  // Use an explicit IPv4 loopback by default. On Linux, `localhost` can
  // resolve to ::1 first while Django's development server is bound to
  // 127.0.0.1, which makes Astro's static build fail with ECONNREFUSED.
  'http://127.0.0.1:8074';

async function fetchJSON<T>(path: string): Promise<T> {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, {
    headers: { Accept: 'application/json' },
  });
  if (!res.ok) {
    throw new Error(`API ${path} returned ${res.status}`);
  }
  return res.json() as Promise<T>;
}

// ── Types ──────────────────────────────────────────────────────────────────

export interface SocialLink {
  platform: string;
  label: string;
  url: string;
  icon_class: string;
}

export interface FooterLink {
  label: string;
  url: string;
}

export interface FooterLinkGroup {
  title: string;
  links: FooterLink[];
}

export interface SiteSettings {
  site_name: string;
  site_tagline: string;
  logo_url: string | null;
  favicon_url: string | null;
  primary_color: string;
  accent_color: string;
  meta_description: string;
  meta_keywords: string;
  meta_author: string;
  og_image_url: string | null;
  twitter_handle: string;
  analytics_provider: string;
  google_tag_manager_id: string;
  google_analytics_id: string;
  nav_show_home: boolean;
  nav_show_contact: boolean;
  nav_cta_label: string;
  nav_cta_url: string;
  footer_description: string;
  footer_address: string;
  footer_phone: string;
  footer_email: string;
  footer_copyright: string;
  newsletter_prompt: string;
  google_play_url: string;
  apple_store_url: string;
  privacy_policy_url: string;
  terms_of_use_url: string;
  chat_enabled: boolean;
  chat_provider: string;
  chat_widget_id: string;
  social_links: SocialLink[];
  footer_link_groups: FooterLinkGroup[];
}

export interface NavItem {
  label: string;
  href: string;
  active?: boolean;
  /** Dropdown subpages (live Wagtail children) — empty for leaf nav items. */
  children?: { label: string; href: string; active?: boolean }[];
}

export interface NavigationData {
  nav_items: NavItem[];
  language?: LangCode;
  available_languages?: LangCode[];
}

export interface ContentLanguage {
  code: string;
  name: string;
  native: string;
  dir: 'ltr' | 'rtl';
  flag?: string;
}

export interface ContentLanguagesData {
  languages: ContentLanguage[];
  coverage: Record<string, number>;
  ui_languages?: string[];
}

export interface ContactMethod {
  type: string;
  label: string;
  value: string;
  href: string;
}

export interface ContactData {
  title: string;
  description: string;
  methods: ContactMethod[];
  form_title: string;
  form_description: string;
  topics: string[];
}

export interface PageData {
  id?: number;
  slug: string;
  title: string;
  type: string;
  show_in_nav: boolean;
  seo_title: string;
  search_description: string;
  hero?: {
    badge?: string;
    title?: string;
    accent?: string;
    subtitle?: string;
    primary_cta?: { label: string; href: string; style?: string } | null;
    secondary_cta?: { label: string; href: string; style?: string } | null;
    trusted_by?: string;
  };
  cta?: {
    title?: string;
    subtitle?: string;
    primary_cta?: { label: string; href: string; style?: string } | null;
    secondary_cta?: { label: string; href: string; style?: string } | null;
  };
  body?: string;
  stats?: Record<string, any>[];
  features?: Record<string, any>[];
  testimonials?: Record<string, any>[];
  pricing?: Record<string, any>[];
  faq?: Record<string, any>[];
  projects?: Record<string, any>[];
  services?: Record<string, any>[];
  process?: Record<string, any>[];
  phases?: { id: number; slug: string; title: string; phase_number?: number; phase_label?: string; href: string }[];
  blog?: Record<string, any>[];
  tech?: string[];
  editions?: Record<string, any>[];
  comparison?: Record<string, any>[];
  /** Deduplicated edition captures used by the product detail gallery. */
  preview_gallery?: PreviewMedia[];
  products?: {
    title: string;
    slug: string;
    tagline: string;
    version?: string;
    href: string;
    category?: string;
    logo_style?: string;
    status?: string;
    excerpt?: string;
    editions?: { name: string; price: string; period?: string; tier?: string; featured?: boolean; offer_label?: string; offer_old_price?: string }[];
    tech?: string[];
  }[];
  // ProductPage catalog fields
  logo_style?: string;
  version?: string;
  tagline?: string;
  status?: string;
  hidden?: boolean;
  // Wagtail-managed Services subpages
  phase_number?: number;
  phase_label?: string;
  outcomes?: string[];
  prompts?: { slug: string; title: string; href: string }[];
  prompt?: string;
  context?: string;
  output?: string;
  tool?: string;
  phase?: { title: string; slug: string; href: string };
  contact?: Record<string, any>[];
  // Blog post meta (BlogPostPage detail pages)
  category?: string;
  post_date?: string;
  read_time?: string;
  excerpt?: string;
  language?: LangCode;
  available_languages?: LangCode[];
  translation_source?: 'model' | 'fallback' | 'canonical';
  translation_language?: LangCode;
}

export interface PageListItem {
  id: number;
  slug: string;
  title: string;
  type: string;
}

export interface PageListData {
  pages: PageListItem[];
  total: number;
}

export interface PreviewMedia {
  url: string;
  kind?: 'image' | 'gif' | 'video';
  poster?: string;
  label?: string;
  alt?: string;
}

export interface PricingProduct {
  slug: string;
  title: string;
  tagline: string;
  version?: string;
  logo_style: string;
  status: string;
  href: string;
  editions: {
    name: string;
    price: string;
    period: string;
    tagline: string;
    tier: string;
    featured: boolean;
    features?: string[];
    offer_label?: string;
    offer_old_price?: string;
    cta_label?: string;
    cta_href?: string;
    preview_href?: string;
    preview_images?: PreviewMedia[];
  }[];
}

export interface PricingData {
  products: PricingProduct[];
}

export interface AssetManifest {
  version: string;
  static_url: string;
  enabled: boolean;
  webpack_enabled: boolean;
  webpack_bundle_dir: string;
  top: { preconnect?: string[]; fonts?: string[]; css?: string[]; inline_css?: string[] };
  bottom: { js?: string[]; inline_js?: string[] };
  fonts: string[];
  preconnect: string[];
}

// ── API Functions ──────────────────────────────────────────────────────────

export interface AuthStatus {
  authenticated: boolean;
  user: {
    email: string;
    display: string;
  } | null;
}

/** Fetch current auth status (backed by Django allauth session). */
export function fetchAuthStatus(): Promise<AuthStatus> {
  return fetchJSON<AuthStatus>('/apis/auth/status/');
}

/** Fetch unified asset manifest for frontend bundler integration. */
export function fetchAssets(): Promise<AssetManifest> {
  return fetchJSON<AssetManifest>('/apis/assets/');
}

/** Fetch site branding, social links, and footer content from Wagtail. */
export function fetchSiteSettings(): Promise<SiteSettings> {
  return fetchJSON<SiteSettings>('/apis/site/settings/');
}

export async function fetchSiteSettingsWithFallback(): Promise<SiteSettings> {
  try {
    return await fetchSiteSettings();
  } catch {
    return {
      site_name: 'Structa Cloud', site_tagline: 'Platforms that ship as finished HTML.',
      logo_url: null, favicon_url: null, primary_color: '#0B57D0', accent_color: '#FFE14D',
      meta_description: 'Platforms, AI tools, and open-source libraries shipped as finished HTML.',
      meta_keywords: '', meta_author: 'Mahmoud Ezzat Moustafa', og_image_url: null, twitter_handle: '',
      analytics_provider: '', google_tag_manager_id: '', google_analytics_id: '',
      nav_show_home: true, nav_show_contact: true, nav_cta_label: 'Get Started', nav_cta_url: '/contact/',
      footer_description: 'Platforms, AI tools, and open-source libraries.', footer_address: '', footer_phone: '',
      footer_email: 'structa.cloud@gmail.com', footer_copyright: '© 2026 structa.cloud. All rights reserved.',
      newsletter_prompt: '', google_play_url: '', apple_store_url: '', privacy_policy_url: '/privacy/',
      terms_of_use_url: '', chat_enabled: false, chat_provider: '', chat_widget_id: '', social_links: [], footer_link_groups: [],
    };
  }
}

/** Fetch main navigation from published Wagtail pages. */
export function fetchNavigation(language: LangCode = CONTENT_LANGUAGE): Promise<NavigationData> {
  const query = language === 'en' ? '' : `?lang=${encodeURIComponent(language)}`;
  return fetchJSON<NavigationData>(`/apis/navigation/${query}`);
}

export async function fetchNavigationWithFallback(language: LangCode = CONTENT_LANGUAGE): Promise<NavigationData> {
  try {
    return await fetchNavigation(language);
  } catch {
    const arabic = language === 'ar';
    return {
      language,
      available_languages: SUPPORTED_LANGUAGE_CODES,
      nav_items: [
        { label: arabic ? 'الرئيسية' : 'Home', href: '/' },
        { label: arabic ? 'الخدمات' : 'Services', href: '/services/' },
        { label: arabic ? 'المنتجات' : 'Products', href: '/products/' },
        { label: arabic ? 'المدونة' : 'Blog', href: '/blog/' },
        { label: arabic ? 'الأسعار' : 'Pricing', href: '/pricing/' },
        { label: arabic ? 'من نحن' : 'About', href: '/about/' },
        { label: arabic ? 'تواصل معنا' : 'Contact', href: '/contact/' },
      ],
    };
  }
}

/** Fetch backend editorial language metadata and translation coverage. */
export function fetchContentLanguages(): Promise<ContentLanguagesData> {
  return fetchJSON<ContentLanguagesData>('/apis/content/languages/');
}

/** Fetch contact methods + form info from Wagtail ContactPage. */
export function fetchContact(): Promise<ContactData> {
  return fetchJSON<ContactData>('/apis/contact/');
}

/** Fetch every live, non-hidden product with its editions (pricing tabs). */
export function fetchPricing(): Promise<PricingData> {
  return fetchJSON<PricingData>('/apis/pricing/');
}

/** Fetch full page data for a single page by slug. */
export function fetchPageData(slug: string, language: LangCode = CONTENT_LANGUAGE): Promise<PageData> {
  const query = language === 'en' ? '' : `?lang=${encodeURIComponent(language)}`;
  return fetchJSON<PageData>(`/apis/pages/${slug}/${query}`);
}

/**
 * Fetch backend-owned content with a static bilingual fallback for Astro
 * builds/offline previews. Wagtail remains authoritative whenever reachable.
 */
export async function fetchPageDataWithFallback(
  slug: string,
  language: LangCode = CONTENT_LANGUAGE,
): Promise<PageData> {
  try {
    return await fetchPageData(slug, language);
  } catch (error) {
    const fallback = staticPageData(slug, language);
    if (fallback) return fallback;
    throw error;
  }
}

/** Fetch list of all published pages. */
export function fetchPageList(): Promise<PageListData> {
  return fetchJSON<PageListData>('/apis/pages/');
}

// ── Caching helpers (build-time dedup for SSG, TTL for dev-server HMR) ─────

const cache = new Map<string, { data: unknown; ts: number }>();
// During `astro build` all pages compile sequentially in a single process,
// so the cache eliminates duplicate fetches. During `astro dev` the TTL
// ensures fresh data on hot-reload without hammering the backend.
const TTL = import.meta.env.DEV ? 30_000 : Infinity; // 30s dev, infinite build

async function fetchCached<T>(key: string, fetcher: () => Promise<T>): Promise<T> {
  const cached = cache.get(key);
  if (cached && Date.now() - cached.ts < TTL) {
    return cached.data as T;
  }
  const data = await fetcher();
  cache.set(key, { data, ts: Date.now() });
  return data;
}

export const cachedAssets = () => fetchCached('assets', fetchAssets);
export const cachedSiteSettings = () => fetchCached('settings', fetchSiteSettingsWithFallback);
export const cachedNavigation = (language: LangCode = CONTENT_LANGUAGE) => fetchCached(`navigation:${language}`, () => fetchNavigationWithFallback(language));
export const cachedContact = () => fetchCached('contact', fetchContact);
export const cachedPricing = () => fetchCached('pricing', fetchPricing);
export const cachedPageData = (slug: string, language: LangCode = CONTENT_LANGUAGE) =>
  fetchCached(`page:${slug}:${language}`, () => fetchPageDataWithFallback(slug, language));
