/**
 * @file modules/index.js
 * Main Modules Entry Point
 */

import { moduleManager, ModuleManager } from './manager.init.js';

// Re-export service modules
export { navigationTracker } from './navigations/index.js';
export { NotificationModule } from './notifications/index.js';
export { FormsManager } from './forms/index.js';

// Re-export usecases
export {
  registerUsecase,
  getUsecase,
  getUsecaseNames,
  reinitUsecases,
  initAnimationsUsecase,
  initLandingUsecase,
  initLmsUsecase,
  initCrmUsecase,
  initFormsUsecase,
  initModalUsecase,
  initSpaUsecase,
  initAllUsecases,
  initUsecase,
  USECASES
} from './usecases/index.js';

// Export the main manager and class
export { moduleManager, ModuleManager };

// Helper functions for backward compatibility
export async function initializeModules(app, config = {}) {
    console.log('📦 Initializing modules...');

    moduleManager.updateConfig(config);
    await moduleManager.init(app);

    return moduleManager;
}

export function getModule(name) {
    return moduleManager.getModule(name);
}

export function registerModule(name, module, options = {}) {
    return moduleManager.registerCustomModule(name, module, options);
}

export function getServiceModule(name) {
    return moduleManager.getServiceModule(name);
}

export function registerServiceModule(name, module, options = {}) {
    return moduleManager.registerServiceModule(name, module, options);
}

// Export module statistics
export function getModuleStats() {
    return {
        total: moduleManager.getTotalModuleCount(),
        app: moduleManager.getAppModuleNames().length,
        services: moduleManager.getServiceModuleNames().length,
        custom: moduleManager.getCustomModuleNames().length,
        metrics: moduleManager.getMetrics()
    };
}

// Make available globally
if (typeof window !== 'undefined') {
    window.Modules = {
        manager: moduleManager,
        getModule,
        registerModule,
        getServiceModule,
        registerServiceModule,
        getModuleStats
    };
}

// Default export
export default moduleManager;