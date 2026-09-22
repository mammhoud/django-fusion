/**
 * Scroll binding — precis.
 *
 * Initializes `[data-fusion-reveal]` reveals + smooth in-page anchors on
 * load. Independent of the Alpine `x-intersect` reveals used by the CMS
 * blocks; only elements carrying `data-fusion-reveal` are affected.
 */
import { initScrollReveal, initSmoothAnchors } from '@fusion/modules/scroll';

let started = false;

export function initFusionScroll(): () => void {
  if (started) return () => undefined;
  started = true;
  const stopReveal = initScrollReveal({ staggerMs: 80 });
  const stopAnchors = initSmoothAnchors();
  return () => {
    stopReveal.stop();
    stopAnchors();
  };
}

export { initScrollReveal, initSmoothAnchors };
export type { ScrollHandle, ScrollRevealOptions } from '@fusion/modules/scroll';
