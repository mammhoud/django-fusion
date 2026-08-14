/**
 * Shared TypeScript types for the Formint POS django-fusion fragment system.
 *
 * Mirrors the payloads served by the formint server:
 *   - `/fusion/pointer/`  → `{ encoded, decoded, fusion_render_first }`
 *   - `/fusion/page/`     → PageHandler full page (browser) or fragment (HTMX)
 *   - `/api/v1/render-mode` → fusion envelope `{ status, message, data }`
 */

/** A decoded Formint fragment pointer (shape served by /fusion/pointer/). */
export interface FragmentPointer {
  component: string;
  fusion_render_first: boolean;
  htmx?: boolean;
  [key: string]: unknown;
}

export interface CodedPayload {
  encoded: string;
  version: string;
  b64: string;
}
