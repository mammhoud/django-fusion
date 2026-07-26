/** Shared TypeScript types for the django-fusion fragment-rendering system. */

export interface FusionEnvelope<T = unknown> {
  status: number;
  message: string;
  data: T;
}

export interface FragmentPointer {
  component: string;
  fragment_name: string;
  fragment_url: string;
  fusion_render_first: boolean;
  page_slug?: string;
  title?: string;
  layout?: string;
  [key: string]: unknown;
}

export interface CodedPayload {
  encoded: string;
  version: string;
  b64: string;
}

export type FusionMode = 'fragment' | 'data' | 'loading';

export interface PageDataResponse {
  slug: string;
  title: string;
  encoded: string;
}

export interface HealthResponse {
  fusion_render_first: boolean;
  reason: string;
  session_cached: boolean;
}

export interface FusionBranding {
  site_name: string;
  company_name: string;
  creator_name: string;
  primary_color: string;
}

// ─── Wagtail FusionPage types ──────────────────────────────────────

export interface FusionWagtailPage {
  id: number;
  slug: string;
  title: string;
  type: 'FusionHomePage' | 'FusionContentPage';
  layout: 'default' | 'full_width' | 'sidebar' | 'blank';
  fusion_render_first: boolean;
  fragment_name: string;
  show_in_nav: boolean;
  seo_title: string;
  search_description: string;
  hero_heading?: string;
  hero_subheading?: string;
  body?: string;
  featured_image_url?: string;
  custom_css?: string;
  children?: FusionPageChild[];
}

export interface FusionPageChild {
  id: number;
  slug: string;
  title: string;
}

export interface PageListResponse {
  pages: FusionWagtailPage[];
  total: number;
}

export interface PageBlock {
  type: string;
  heading?: string;
  intro?: string;
  html?: string;
  items?: unknown[];
  ctas?: unknown[];
  [key: string]: unknown;
}
