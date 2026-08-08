/**
 * Landing-fusion API client — fetches all data from the Wagtail/django-fusion backend.
 *
 * Every piece of content (branding, navigation, page data, contact info,
 * footer links) comes from the backend via these endpoints. No content is
 * hardcoded in the frontend — site.ts holds only config (URLs, keys).
 * An empty API base uses the current host, which lets the same static build
 * work behind both the ctc-research.com and lms-fusion hostnames.
 *
 * Backend endpoints (see apps/pages/api.py):
 *   GET /apis/site/settings/   — branding, social links, footer
 *   GET /apis/navigation/      — nav links from published pages
 *   GET /apis/contact/         — contact methods + form
 *   GET /apis/pages/<slug>/    — full page data (JSON)
 *   GET /apis/pages/           — page list
 */

/** Base URL for the Django backend. Set PUBLIC_FUSION_API_URL env var to override. */
const browserApiBase = (import.meta.env.PUBLIC_FUSION_API_URL as string | undefined) || '';
const buildApiBase = (import.meta.env.PUBLIC_BUILD_API_URL as string | undefined) || 'https://ctc-research.com';

// Astro runs these fetches at build time for SSG pages. Keep browser requests
// same-origin for dual-host deployment, but give Node an absolute URL so the
// built HTML can include the reloaded Wagtail content instead of silently
// falling back when fetch() receives a relative path.
export const API_BASE: string = import.meta.env.SSR ? buildApiBase : browserApiBase;

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
}

export interface NavigationData {
  nav_items: NavItem[];
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
}

export interface PageData {
  id: number;
  slug: string;
  title: string;
  type: string;
  show_in_nav: boolean;
  seo_title: string;
  search_description: string;
  hero?: {
    badge?: string;
    title?: string;
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
  blog?: Record<string, any>[];
  tech?: string[];
  editions?: Record<string, any>[];
  snippets?: Record<string, any>[];
  products?: { title: string; slug: string; tagline: string; href: string }[];
  contact?: Record<string, any>[];
  // Blog post meta (BlogPostPage detail pages)
  category?: string;
  post_date?: string;
  read_time?: string;
  excerpt?: string;
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

/** Fetch unified asset manifest for frontend bundler integration. */
export function fetchAssets(): Promise<AssetManifest> {
  return fetchJSON<AssetManifest>('/apis/assets/');
}

/** Fetch site branding, social links, and footer content from Wagtail. */
export function fetchSiteSettings(): Promise<SiteSettings> {
  return fetchJSON<SiteSettings>('/apis/site/settings/');
}

/** Fetch main navigation from published Wagtail pages. */
export function fetchNavigation(): Promise<NavigationData> {
  return fetchJSON<NavigationData>('/apis/navigation/');
}

/** Fetch contact methods + form info from Wagtail ContactPage. */
export function fetchContact(): Promise<ContactData> {
  return fetchJSON<ContactData>('/apis/contact/');
}

/** Fetch full page data for a single page by slug. */
export function fetchPageData(slug: string): Promise<PageData> {
  return fetchJSON<PageData>(`/apis/pages/${slug}/`);
}

/** Fetch list of all published pages. */
export function fetchPageList(): Promise<PageListData> {
  return fetchJSON<PageListData>('/apis/pages/');
}

export interface CourseCard {
  id: number;
  title: string;
  slug: string;
  short_description: string;
  image_url: string | null;
  instructor: string;
  price: number;
  original_price: number | null;
  difficulty: string;
  language: string;
  duration: number;
  rating: number;
  reviews_count: number;
  is_featured: boolean;
  has_certificate: boolean;
}

export interface CourseListData {
  data: CourseCard[];
  pagination: {
    page: number;
    per_page: number;
    total: number;
    total_pages: number;
  };
}

export interface CourseDetail extends Omit<CourseCard, 'instructor'> {
  description: string;
  overview: unknown;
  preview_video_url: string[];
  objectives: string[];
  requirements: string[];
  target_audience: string[];
  specializations: string[];
  tags: string[];
  discount_percentage: number;
  enrollment_count: number;
  instructor: { name: string; bio: string };
  modules: {
    id: string | number;
    title: string;
    description: string;
    lessons: { id: string | number; title: string; is_preview: boolean; duration: number }[];
  }[];
}

/** Fetch the published medical-research course catalog. */
const COURSE_CONTENT_VERSION = '2026-08-08-medical-catalog-v2';

export async function fetchCourseList(): Promise<CourseListData> {
  const firstPage = await fetchJSON<CourseListData>(`/api/courses/?page=1&per_page=100&content_version=${COURSE_CONTENT_VERSION}`);
  const pages = [firstPage];

  for (let page = 2; page <= firstPage.pagination.total_pages; page += 1) {
    pages.push(await fetchJSON<CourseListData>(`/api/courses/?page=${page}&per_page=100&content_version=${COURSE_CONTENT_VERSION}`));
  }

  return {
    data: pages.flatMap((page) => page.data),
    pagination: {
      ...firstPage.pagination,
      per_page: 100,
      total_pages: pages.length,
    },
  };
}

/** Fetch a single published course for the preview/detail page. */
export function fetchCourseDetail(slug: string): Promise<CourseDetail> {
  return fetchJSON<CourseDetail>(`/api/courses/${encodeURIComponent(slug)}/?content_version=${COURSE_CONTENT_VERSION}`);
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
export const cachedSiteSettings = () => fetchCached('settings', fetchSiteSettings);
export const cachedNavigation = () => fetchCached('navigation', fetchNavigation);
export const cachedContact = () => fetchCached('contact', fetchContact);
export const cachedPageData = (slug: string) => fetchCached(`page:${slug}`, () => fetchPageData(slug));
