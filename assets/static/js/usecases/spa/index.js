import { registerUsecase } from '../helpers.js';

export const initSpaUsecase = registerUsecase('spa', ['.spa-shell', '[data-usecase~="spa"]']);
