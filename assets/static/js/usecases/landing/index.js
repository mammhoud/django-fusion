import { ready } from '../../base/utils/index.js';

export function initLandingUsecase(root = document) {
  root.querySelectorAll('.landing-shell, [data-usecase~="landing"]').forEach((shell) => {
    shell.dataset.usecaseReady = 'landing';
  });
}

ready(initLandingUsecase);
