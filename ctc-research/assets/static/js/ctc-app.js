import { ready, siteName } from '@base/utils';

ready(() => {
  document.documentElement.dataset.site = siteName('ctc-research');
});
