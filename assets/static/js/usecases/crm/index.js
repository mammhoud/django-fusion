import { registerUsecase } from '../helpers.js';

export const initCrmUsecase = registerUsecase('crm', ['.crm-shell', '[data-usecase~="crm"]']);
