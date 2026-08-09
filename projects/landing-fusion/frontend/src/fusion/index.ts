/**
 * Fusion bundle entry — precis.
 *
 * Aggregates the modular fusion-js bindings for this project and kicks
 * off the page-level behaviors (scroll reveal, smooth anchors, fragment
 * hydration). Individual modules remain importable for tree-shaking:
 *
 * ```ts
 * import { createSSEClient } from '../fusion/sse';
 * import { hydrateFragments } from '../fusion/fragments';
 * ```
 */
import { initFusionScroll } from './scroll';
import { initFusionFragments } from './fragments';

export * from './theme';
export * from './scroll';
export * from './fragments';
export * from './sse';
export * from './htmx';

let initialized = false;

/** Initialize page-level fusion behaviors (idempotent). */
export function initFusion(): void {
  if (initialized) return;
  initialized = true;
  initFusionScroll();
  initFusionFragments();
}

// Script runs at the end of <body> — DOM is ready.
initFusion();

// Expose for E2E/debugging: proves the fusion bundle executed on the page.
declare global {
  interface Window {
    __FUSION__?: boolean;
  }
}
window.__FUSION__ = true;
