import { ready } from '../../base/utils/index.js';

export function initSpaUsecase(root = document) {
  root.querySelectorAll('.spa-shell, [data-usecase~="spa"]').forEach((shell) => {
    shell.dataset.usecaseReady = 'spa';
  });
}

ready(initSpaUsecase);
