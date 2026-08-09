import { attachHtmx, bindIndicator, isFragmentRequest, isHtmxRequest, onSwap } from './htmx';
import { createSSEClient } from './sse';
import { loadFragment, refreshFragments } from './fragments';
import { initScrollReveal, initSmoothAnchors } from './scroll';
import { createTheme } from './theme';

/** Default export aggregating every fusion-js module. */
const fusion = {
  attachHtmx,
  bindIndicator,
  isFragmentRequest,
  isHtmxRequest,
  onSwap,
  createSSEClient,
  loadFragment,
  refreshFragments,
  initScrollReveal,
  initSmoothAnchors,
  createTheme,
};

export default fusion;
