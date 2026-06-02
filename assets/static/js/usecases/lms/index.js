import { registerUsecase } from '../helpers.js';

export const initLmsUsecase = registerUsecase('lms', ['.lms-shell', '[data-usecase~="lms"]']);
