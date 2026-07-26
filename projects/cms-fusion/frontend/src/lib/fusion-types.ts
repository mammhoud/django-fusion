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

/** Top-level response envelope matching ``django_fusion.routes.renderers``. */
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
