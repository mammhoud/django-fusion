import { ready } from '../../base/utils/index.js';

export function initModalUsecase(root = document) {
  root.querySelectorAll('.modal-shell, [data-usecase~="modal"]').forEach((shell) => {
    shell.dataset.usecaseReady = 'modal';
  });
}

ready(initModalUsecase);
