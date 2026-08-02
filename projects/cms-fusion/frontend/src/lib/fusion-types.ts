/**
 * Shared TypeScript types for the django-fusion fragment-rendering system.
 *
 * These types are used by FusionMiddleware, FusionProxy, FusionPage, and
 * FusionDecoder.  Extracting them into a standalone file avoids circular
 * imports and keeps the decoder class focused on logic.
 *
 * Usage::
 *
 *     import type { FusionEnvelope, FragmentPointer, CodedPayload } from '@/lib/fusion-types';
 */

// ─── Envelope types ────────────────────────────────────────────────

/** Top-level response envelope matching ``django_fusion.routes.rendering.renderers``. */
export interface FusionEnvelope<T = unknown> {
  status: number;
  message: string;
  data: T;
}

/** Fragment pointer as returned by ``/apis/pages/<slug>/fragment/``. */
export interface FragmentPointer {
  component: string;
  fragment_name: string;
  fragment_url: string;
  fusion_render_first: boolean;
  page_slug?: string;
  title?: string;
  [key: string]: unknown; // allow extra metadata
}

/** Shape of the codec prefix+base64 payload from ``FusionCodec.encode()``. */
export interface CodedPayload {
  /** The full encoded string, e.g. ``fusion_v1:eyJrZXkiOiAidmFsdWUifQ==`` */
  encoded: string;
  /** Decoded version number from the prefix (e.g. ``\"1\"``). */
  version: string;
  /** Base64 portion after the prefix. */
  b64: string;
}

/** Rendering mode, used by FusionMiddleware. */
export type FusionMode = 'fragment' | 'data' | 'loading';

// ─── Page data response types ─────────────────────────────────────

/** Response from /apis/pages/<slug>/data/ */
export interface PageDataResponse {
  slug: string;
  title: string;
  encoded: string;
}

/** Response from /apis/health/ */
export interface HealthResponse {
  fusion_render_first: boolean;
  reason: string;
  session_cached: boolean;
}

/** Branding response from /apis/branding/ */
export interface FusionBranding {
  site_name: string;
  company_name: string;
  creator_name: string;
  primary_color: string;
}

// ─── Wagtail FusionPage types ──────────────────────────────────────

/** A Wagtail FusionPage as returned by the API. */
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

/** Child page reference in navigation. */
export interface FusionPageChild {
  id: number;
  slug: string;
  title: string;
}

/** Response from GET /apis/pages/ */
export interface PageListResponse {
  pages: FusionWagtailPage[];
  total: number;
}

/** A CMS page block (dashboard content, etc.). */
export interface PageBlock {
  type: string;
  heading?: string;
  intro?: string;
  html?: string;
  items?: unknown[];
  ctas?: unknown[];
  [key: string]: unknown;
}
