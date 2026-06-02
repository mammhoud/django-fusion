import { usecaseConfig } from './usecase-config.js';
import { ready, siteName } from '@utility';

window.STRUCTA_USECASE_CONFIG = usecaseConfig;

ready(() => {
  document.documentElement.dataset.site = siteName('ctc-research');
});

