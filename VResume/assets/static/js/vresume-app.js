import { usecaseConfig } from './usecases/config.js';
import { ready, siteName } from '@utility';
import './index';

window.STRUCTA_USECASE_CONFIG = usecaseConfig;

ready(() => {
  document.documentElement.dataset.site = siteName('vresume');
});

