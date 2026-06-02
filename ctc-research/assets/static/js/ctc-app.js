import { usecaseConfig } from './usecase-config.js';
import { ready, siteName } from '@base/utils';

window.STRUCTA_USECASE_CONFIG = usecaseConfig;

ready(() => {
  document.documentElement.dataset.site = siteName('ctc-research');
});
