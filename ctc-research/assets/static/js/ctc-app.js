/**
 * CTC-Research entry point.
 * Loads the shared theme and bootstraps site-specific usecases.
 */
import { usecaseConfig } from './usecase-config.js';
import { ready, siteName } from '@utility';
import { initAllUsecases } from '@theme/usecases';
import { HTMXBridge } from '@htmx';

// Expose config for modular plugin/component system
window.STRUCTA_USECASE_CONFIG = usecaseConfig;

ready(() => {
  document.documentElement.dataset.site = siteName('ctc-research');

  // Boot all usecases on initial page load
  initAllUsecases(document);

  // Re-run usecases after any HTMX swap (sliders, forms, animations)
  HTMXBridge.reinit(document);
});
