/**
 * @file VResume/assets/static/js/app.js
 * VResume site entry point.
 */
import { usecaseConfig } from './usecases/config.js';
import { ready, siteName } from '@utility';
import { initAllUsecases } from '../../../../assets/static/js/modules/index.js';
import './index';          // VResume-specific core/lib/services/navigation/components barrel

window.STRUCTA_SITE           = 'vresume';
window.STRUCTA_USECASE_CONFIG  = usecaseConfig;

ready(() => {
  document.documentElement.dataset.site = siteName('vresume');
  initAllUsecases(document);
});

document.addEventListener('htmx:afterSwap', (e) => {
  initAllUsecases(e.detail?.target ?? document);
});
