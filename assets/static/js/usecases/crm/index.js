import { ready } from '../../base/utils/index.js';

export function initCrmUsecase(root = document) {
  root.querySelectorAll('.crm-shell, [data-usecase~="crm"]').forEach((shell) => {
    shell.dataset.usecaseReady = 'crm';
  });
}

ready(initCrmUsecase);
