import { ready } from '../base/utils/index.js';
import { initializeUsecaseComponents } from './component-registry.js';

export function markUsecaseReady(usecase, selectors, root = document) {
  const selectorList = Array.isArray(selectors) ? selectors.join(', ') : selectors;

  root.querySelectorAll(selectorList).forEach((shell) => {
    const readyUsecases = new Set((shell.dataset.usecaseReady || '').split(' ').filter(Boolean));
    readyUsecases.add(usecase);
    shell.dataset.usecaseReady = Array.from(readyUsecases).join(' ');
  });
}

export function registerUsecase(usecase, selectors) {
  const init = async (root = document) => {
    markUsecaseReady(usecase, selectors, root);
    await initializeUsecaseComponents(usecase, root);
  };

  ready(init);
  return init;
}
