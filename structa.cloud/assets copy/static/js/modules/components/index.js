/**
 * @file ui/index.js
 * UI Manager and Components Export
 */

import { UIManager, uiManager, UI_COMPONENTS } from './manager.init.js';

/**
 * Initialize UI Manager
 */
export async function initializeUI(config = {}) {
    console.log('🎨 Initializing UI Manager...');

    try {
        await uiManager.init(config);
        console.log('✅ UI Manager initialized');
        return uiManager;
    } catch (error) {
        console.error('❌ Failed to initialize UI Manager:', error);
        throw error;
    }
}

/**
 * Get component instances
 */
export function getComponent(componentId) {
    return uiManager.getComponent(componentId);
}

/**
 * Get all components
 */
export function getAllComponents() {
    return uiManager.getAllComponents();
}

/**
 * Register a component
 */
export function registerComponent(componentId, config, elements = []) {
    return uiManager.registerComponent(componentId, config, elements);
}

/**
 * Refresh all components
 */
export function refreshAllComponents() {
    return uiManager.refreshAll();
}

/**
 * Destroy a component
 */
export function destroyComponent(componentId) {
    return uiManager.destroyComponent(componentId);
}

/**
 * UI Utilities
 */
export const uiUtils = {
    /**
     * Debounce function
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    /**
     * Throttle function
     */
    throttle(func, limit) {
        let inThrottle;
        return function () {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },

    /**
     * Show loading
     */
    showLoading(selector) {
        return uiManager.showLoading(selector);
    },

    /**
     * Hide loading
     */
    hideLoading(selector) {
        return uiManager.hideLoading(selector);
    },

    /**
     * Show element
     */
    showElement(selector, display) {
        return uiManager.showElement(selector, display);
    },

    /**
     * Hide element
     */
    hideElement(selector) {
        return uiManager.hideElement(selector);
    },

    /**
     * Toggle element
     */
    toggleElement(selector, display) {
        return uiManager.toggleElement(selector, display);
    },

    /**
     * Get page type
     */
    getPageType() {
        return uiManager.getPageType();
    }
};

// Export everything
export {
    UIManager,
    uiManager,
    UI_COMPONENTS
};

// Default export
export default { uiManager, UI_COMPONENTS };