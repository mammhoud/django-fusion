import { ready } from '../../base/utils/index.js';

export function initLmsUsecase(root = document) {
  root.querySelectorAll('.lms-shell, [data-usecase~="lms"]').forEach((shell) => {
    shell.dataset.usecaseReady = 'lms';
  });
}

ready(initLmsUsecase);
