/**
 * @file modules/usecases/index.js
 * Unified Usecases Module  
 * Provides page-specific initialization for different website sections
 * (Landing, CRM, LMS, SPA, Animations, Forms, Modals, Notifications)
 */

// Use-case registry for lazy initialization
const usecaseRegistry = new Map();
const initializedUsecases = new Set();

/**
 * Register a usecase initializer function
 * @param {string} name - Usecase name (e.g., 'landing', 'lms')
 * @param {Function} initFn - Initialization function
 */
export function registerUsecase(name, initFn) {
  usecaseRegistry.set(name, initFn);
}

/**
 * Get a registered usecase
 * @param {string} name - Usecase name
 * @returns {Function|undefined} Initialization function
 */
export function getUsecase(name) {
  return usecaseRegistry.get(name);
}

/**
 * Get all registered usecase names
 * @returns {string[]} Array of usecase names
 */
export function getUsecaseNames() {
  return Array.from(usecaseRegistry.keys());
}

/**
 * Initialize a specific usecase if registered
 * @param {string} name - Usecase name
 * @returns {Promise<void>}
 */
export async function initUsecase(name) {
  if (initializedUsecases.has(name)) {
    console.log(`ℹ️ Usecase "${name}" already initialized`);
    return;
  }

  const initFn = usecaseRegistry.get(name);
  if (!initFn) {
    console.warn(`⚠️ Usecase "${name}" not found in registry`);
    return;
  }

  try {
    await initFn();
    initializedUsecases.add(name);
    console.log(`✅ Initialized usecase: ${name}`);
  } catch (error) {
    console.error(`❌ Failed to initialize usecase "${name}":`, error);
  }
}

/**
 * Initialize all registered usecases
 * @returns {Promise<void>}
 */
export async function initAllUsecases() {
  const usecases = Array.from(usecaseRegistry.keys());
  
  for (const name of usecases) {
    if (!initializedUsecases.has(name)) {
      await initUsecase(name);
    }
  }

  console.log(`✅ All usecases initialized. Total: ${initializedUsecases.size}`);
}

/**
 * Reset all initialized usecases (for testing/reinitialization)
 */
export function reinitUsecases() {
  initializedUsecases.clear();
}

/**
 * Get the USECASES object for reference
 */
export const USECASES = {
  ANIMATIONS: 'animations',
  LANDING: 'landing',
  LMS: 'lms',
  CRM: 'crm',
  FORMS: 'forms',
  MODALS: 'modals',
  SPA: 'spa',
  NOTIFICATIONS: 'notifications'
};

// Export init functions as stubs (override with actual implementations in website app.js)
export async function initAnimationsUsecase() {
  console.log('ℹ️ Animations usecase - override in website app.js');
}

export async function initLandingUsecase() {
  console.log('ℹ️ Landing usecase - override in website app.js');
}

export async function initLmsUsecase() {
  console.log('ℹ️ LMS usecase - override in website app.js');
}

export async function initCrmUsecase() {
  console.log('ℹ️ CRM usecase - override in website app.js');
}

export async function initFormsUsecase() {
  console.log('ℹ️ Forms usecase - override in website app.js');
}

export async function initModalUsecase() {
  console.log('ℹ️ Modal usecase - override in website app.js');
}

export async function initSpaUsecase() {
  console.log('ℹ️ SPA usecase - override in website app.js');
}

// Auto-register the stub functions
registerUsecase(USECASES.ANIMATIONS, initAnimationsUsecase);
registerUsecase(USECASES.LANDING, initLandingUsecase);
registerUsecase(USECASES.LMS, initLmsUsecase);
registerUsecase(USECASES.CRM, initCrmUsecase);
registerUsecase(USECASES.FORMS, initFormsUsecase);
registerUsecase(USECASES.MODALS, initModalUsecase);
registerUsecase(USECASES.SPA, initSpaUsecase);
registerUsecase(USECASES.NOTIFICATIONS, () => console.log('ℹ️ Notifications usecase - override in website app.js'));
