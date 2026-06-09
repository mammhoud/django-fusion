/**
 * @file lms-demo/assets/static/js/app.js
 * LMS Demo site entry point.
 *
 * Bootstraps the shared theme, applies site-specific usecase config,
 * and registers the HTMX lifecycle bridge so sliders/forms/notifications
 * reinitialise correctly after every fragment swap.
 */
import { usecaseConfig } from './usecase-config.js';
import { ready, siteName } from '@utility';
import { initAllUsecases } from '../../../../assets/static/js/modules/index.js';
import { HTMXBridge }      from '@htmx';

// Expose config so any module can read enabled components / overrides
window.STRUCTA_SITE          = 'lms-demo';
window.STRUCTA_USECASE_CONFIG = usecaseConfig;

ready(() => {
  // Mark <html> with the site identifier (used by CSS and JS selectors)
  document.documentElement.dataset.site = siteName('lms-demo');

  // Run all usecases on the initial full page
  initAllUsecases(document);
});

// Re-init after HTMX swaps (sliders, forms, animations, notifications)
document.addEventListener('htmx:afterSwap', (e) => {
  const root = e.detail?.target ?? document;
  initAllUsecases(root);
});
