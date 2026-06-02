import { registerUsecase } from '../helpers.js';

export const initModalUsecase = registerUsecase('modal', ['.modal-shell', '[data-usecase~="modal"]']);
