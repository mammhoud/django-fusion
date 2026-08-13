/**
 * Scroll binding — precis.
 *
 * Initializes `[data-fusion-reveal]` reveals + smooth in-page anchors on
 * load. Independent of the Alpine `x-intersect` reveals used by the CMS
 * blocks; only elements carrying `data-fusion-reveal` are affected.
 */
import { initScrollReveal, initSmoothAnchors } from '@fusion/modules/scroll';
import type { ScrollHandle } from '@fusion/modules/scroll';

let started = false;
let stopReveal: ScrollHandle | null = null;
let stopAnchors: (() => void) | null = null;

export function initFusionScroll(): () => void {
  if (started) return () => undefined;
  started = true;
  stopReveal = initScrollReveal({ staggerMs: 80 });
  stopAnchors = initSmoothAnchors();
  return () => {
    stopReveal?.stop();
    stopAnchors?.();
    stopReveal = null;
    stopAnchors = null;
    started = false;
  };
}

/** Re-bind reveal and anchor behavior after an HTMX DOM swap. */
export function refreshFusionScroll(): void {
  stopReveal?.stop();
  stopAnchors?.();
  stopReveal = initScrollReveal({ staggerMs: 80 });
  stopAnchors = initSmoothAnchors();
}

export { initScrollReveal, initSmoothAnchors };
export type { ScrollHandle, ScrollRevealOptions } from '@fusion/modules/scroll';
