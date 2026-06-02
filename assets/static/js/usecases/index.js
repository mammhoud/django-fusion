/*
 * Shared frontend usecase registry.
 * Categories map repository assets to the product surfaces used by the three
 * websites: lms, landing, crm, forms, modal, and spa.
 */
export { initLandingUsecase } from './landing/index.js';
export { initLmsUsecase } from './lms/index.js';
export { initCrmUsecase } from './crm/index.js';
export { initFormsUsecase } from './forms/index.js';
export { initModalUsecase } from './modal/index.js';
export { initSpaUsecase } from './spa/index.js';
