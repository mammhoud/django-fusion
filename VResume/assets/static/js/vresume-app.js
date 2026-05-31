import { ready, siteName } from '@base/utils';
import './index';

ready(() => {
  document.documentElement.dataset.site = siteName('vresume');
});
