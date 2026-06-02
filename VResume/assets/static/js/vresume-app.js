import { usecaseConfig } from './usecases/config.js';
import { ready, siteName } from '@base/utils';
import './index';

window.STRUCTA_USECASE_CONFIG = usecaseConfig;

ready(() => {
  document.documentElement.dataset.site = siteName('vresume');
});
