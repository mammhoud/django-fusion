/**
 * @file crm/assets/static/js/app.js
 * CRM site entry point.
 *
 * Bootstraps shared theme, HTMX bridge, and Alpine.js for the CRM POS
 * sale creation component.
 */
import { ready } from '@utility';
import { initAllUsecases } from '../../../../assets/static/js/modules/index.js';
import { HTMXBridge } from '@htmx';

window.STRUCTA_SITE = 'crm';

ready(() => {
  document.documentElement.dataset.site = 'crm';
  initAllUsecases(document);
});

// Re-init after every HTMX fragment swap
document.addEventListener('htmx:afterSwap', (e) => {
  const root = e.detail?.target ?? document;
  initAllUsecases(root);
});
