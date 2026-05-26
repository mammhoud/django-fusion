/**
 * @file modules/navigations/index.js
 * Main navigation exports and integration with app system
 */

// Import the merged navigation components from menu.init.js
import {
    NavigationTracker,
    HeaderMenu,
    UnifiedNavigationSystem,
    unifiedNavigation as unifiedNavigationSingleton,
    navigationTracker as navigationTrackerSingleton
} from './menu.init.js';

// Create singleton instances
export const navigationTracker = navigationTrackerSingleton;
export const unifiedNavigation = unifiedNavigationSingleton;

/**
 * Navigation Manager - Integrates with app system
 */
export class NavigationManager {
    constructor(config = {}) {
        this.config = {
            autoInitialize: true,
            useUnifiedNavigation: true,
            enablePlugins: false,
            ...config
        };

        this.initialized = false;
        this.activePlugins = new Map();
    }

    async initialize(app) {
        if (this.initialized) return this;

        console.log('🧭 Initializing Navigation Manager...');

        try {
            // Check which navigation system to use
            const useUnified = this.config.useUnifiedNavigation && 
                             document.querySelector('[data-unified-navigation]');

            if (useUnified) {
                // Initialize unified navigation
                await unifiedNavigation.initialize();
                console.log('🚀 Unified Navigation System initialized');
                
                // Register unified navigation as a service
                if (app && app.serviceManager) {
                    app.serviceManager.register('unifiedNavigation', unifiedNavigation);
                }
            } else {
                // Initialize legacy navigation tracker
                await navigationTracker.initialize();
                console.log('🧭 Navigation Tracker initialized');
                
                // Register navigation tracker as a service
                if (app && app.serviceManager) {
                    app.serviceManager.register('navigation', navigationTracker);
                }

                // Initialize header menu if needed
                if (document.querySelector('[data-header-menu]')) {
                    const headerMenu = new HeaderMenu();
                    await headerMenu.init();
                    console.log('🍔 Header Menu initialized');
                }

            }

            this.initialized = true;
            console.log('✅ Navigation Manager ready');

            // Emit event
            if (app) {
                app.emit('navigation:initialized', {
                    unified: useUnified,
                });
            }

        } catch (error) {
            console.error('Failed to initialize navigation manager:', error);
            throw error;
        }

        return this;
    }

    /**
     * Handle page navigation
     */
    async navigateTo(url, options = {}) {
        if (this.config.useUnifiedNavigation && unifiedNavigation.navigateTo) {
            return unifiedNavigation.navigateTo(url, options);
        }
        
        if (navigationTracker.navigateTo) {
            return navigationTracker.navigateTo(url, options);
        }

        // Fallback to window navigation
        window.location.href = url;
        return Promise.resolve();
    }

    /**
     * Go back in history
     */
    goBack() {
        if (this.config.useUnifiedNavigation && unifiedNavigation.goBack) {
            return unifiedNavigation.goBack();
        }
        
        if (navigationTracker.goBack) {
            return navigationTracker.goBack();
        }

        window.history.back();
    }

    /**
     * Refresh current page
     */
    refresh() {
        if (this.config.useUnifiedNavigation && unifiedNavigation.refresh) {
            return unifiedNavigation.refresh();
        }
        
        if (navigationTracker.refresh) {
            return navigationTracker.refresh();
        }

        window.location.reload();
    }

    /**
     * Update navigation configuration
     */
    updateConfig(config) {
        Object.assign(this.config, config);
        
        // if (config.plugins) {
        //     Object.assign(this.config.plugins, config.plugins);
        // }
        
        return this;
    }

    /**
     * Cleanup navigation manager
     */
    async destroy() {
        console.log('🧹 Cleaning up Navigation Manager...');
        
        
        
        // Destroy navigation systems if they have destroy methods
        if (typeof unifiedNavigation.destroy === 'function') {
            await unifiedNavigation.destroy();
        }
        
        if (typeof navigationTracker.destroy === 'function') {
            await navigationTracker.destroy();
        }
        
        this.initialized = false;
        console.log('✅ Navigation Manager cleaned up');
    }
}

// Create singleton instance
export const navigationManager = new NavigationManager();

// Auto-initialize with app if available
if (typeof window !== 'undefined') {
    window.addEventListener('DOMContentLoaded', () => {
        // Wait for app to be available
        const initNavigation = () => {
            if (window.App && !navigationManager.initialized) {
                navigationManager.initialize(window.App).catch(console.error);
            } else {
                // Initialize standalone if no app
                setTimeout(() => {
                    if (!navigationManager.initialized) {
                        navigationManager.initialize().catch(console.error);
                    }
                }, 100);
            }
        };

        // Try immediately
        initNavigation();
        
        // Also try after a delay
        setTimeout(initNavigation, 1000);
    });
}

// Export django_grep.comp for manual use
export {
    NavigationTracker,
    HeaderMenu,
    UnifiedNavigationSystem,
};

// Default export for backward compatibility
export default navigationManager;