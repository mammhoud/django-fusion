/**
 * HTMX binding — precis.
 *
 * Attaches the shared wrapper to `window.htmx` (the runtime is loaded by
 * `src/lib/htmx-bootstrap.ts` on pages that opt in). Keeps indicator +
 * swap helpers available to app code with project defaults.
 */
import { attachHtmx, bindIndicator } from '@fusion/modules/htmx';

export function initFusionHtmx(): void {
  const htmx = attachHtmx(undefined, { selfRequestsOnly: false });
  if (htmx) {
    bindIndicator(htmx, 'htmx-global-indicator');
  }
}

export { attachHtmx, isHtmxRequest, isFragmentRequest, onSwap } from '@fusion/modules/htmx';
export type { HtmxLike, HtmxConfig, HtmxSwapDetail } from '@fusion/modules/htmx';
