/**
 * @file lms-demo/assets/static/js/app.js
 * LMS-Demo site entry point.
 */
import { usecaseConfig } from './usecase-config.js';
import { ready, siteName } from '@utility';
import { initAllUsecases } from '../../../../assets/static/js/modules/index.js';

window.STRUCTA_SITE           = 'lms-demo';
window.STRUCTA_USECASE_CONFIG  = usecaseConfig;

ready(() => {
  document.documentElement.dataset.site = siteName('lms-demo');
  initAllUsecases(document);
});

document.addEventListener('htmx:afterSwap', (e) => {
  initAllUsecases(e.detail?.target ?? document);
});
