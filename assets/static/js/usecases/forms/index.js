import { registerUsecase } from '../helpers.js';

export const initFormsUsecase = registerUsecase('forms', ['.form-stack', '[data-usecase~="forms"]']);
