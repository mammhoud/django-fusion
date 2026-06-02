import { registerUsecase } from '../helpers.js';

export const initLandingUsecase = registerUsecase('landing', ['.landing-shell', '[data-usecase~="landing"]']);
