import { ready } from '../../base/utils/index.js';

export function initFormsUsecase(root = document) {
  root.querySelectorAll('.form-stack, [data-usecase~="forms"]').forEach((shell) => {
    shell.dataset.usecaseReady = 'forms';
  });
}

ready(initFormsUsecase);
