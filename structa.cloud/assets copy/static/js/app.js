/**
 * @file app.js
 * Clean Application Core with Direct UI and Modules Management
 */

import { URLTrackerMixin } from './utility/url.js';
import { moduleManager, NotificationModule } from './modules/index.js';
import { uiManager } from './modules/components/index.js';

/**
 * Minimal Application Class
 */
export class Application extends URLTrackerMixin(class { }) {
    constructor(config = {}) {
        super({
            debug: config.debug || false,
            history: true,
            hash: true,
            popstate: true,
            ...config.urlConfig
        });

        // Main application configuration
        this.config = {
            debug: config.debug || false,
            autoInit: config.autoInit !== false,
            trackURL: config.trackURL !== false,
            trackErrors: config.trackErrors !== false,
            notifications: config.notifications || {},
            ...config
        };

        // Core managers
        this.managers = {
            modules: moduleManager,
            ui: uiManager
        };

        // Runtime state
        this.initialized = false;
        this.loading = false;
        this.errors = [];
        this.events = new Map();

        // Performance tracking
        this.startTime = Date.now();
        this.timers = new Map();

        // Bind methods
        this.handleError = this.handleError.bind(this);
        this.handleResize = this.handleResize.bind(this);
        this.handleVisibilityChange = this.handleVisibilityChange.bind(this);

        console.log('🚀 Application instance created');
    }

    /**
     * Initialize the application
     */
    async init() {
        if (this.initialized) {
            console.warn('Application already initialized');
            return this;
        }

        this.startLoading();
        this.emit('app:init:start');

        try {
            console.log('🚀 Application initializing...');

            // Step 1: Initialize URL tracking
            if (this.config.trackURL) {
                await this.initURLTracking();
                this.onURLEvent('url:changed', (event) => {
                    this.handleURLChange(event);
                });
            }

            // Step 2: Initialize Notification System
            if (this.config.notifications) {
                await NotificationModule.initialize(this.config.notifications);
            }

            // Step 3: Setup core listeners
            this.setupCoreListeners();

            // Step 4: Finalize initialization
            await this.finalizeInit();

        } catch (error) {
            this.handleError('Initialization failed', error);
            throw error;
        } finally {
            this.stopLoading();
        }

        return this;
    }

    /**
     * Setup core event listeners
     */
    setupCoreListeners() {
        // Window resize with debounce
        let resizeTimer;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(() => {
                this.handleResize();
            }, 250);
        });

        // Visibility changes
        document.addEventListener('visibilitychange', () => {
            this.handleVisibilityChange();
        });

        // Online/offline status
        window.addEventListener('online', () => {
            this.emit('app:online');
            this.showNotification('You are back online', 'success');
        });

        window.addEventListener('offline', () => {
            this.emit('app:offline');
            this.showNotification('You are offline', 'warning');
        });

        // Global error handling
        if (this.config.trackErrors) {
            this.setupErrorHandling();
        }

        console.log('🎧 Core event listeners set up');
    }

    /**
     * Setup error handling
     */
    setupErrorHandling() {
        // Window error events
        window.addEventListener('error', (event) => {
            this.handleError('Unhandled error', event.error || event);
        });

        // Unhandled promise rejections
        window.addEventListener('unhandledrejection', (event) => {
            this.handleError('Unhandled promise rejection', event.reason);
        });

        console.log('⚠️ Error tracking enabled');
    }

    /**
     * Finalize initialization
     */
    async finalizeInit() {
        // Set flags
        this.initialized = true;
        this.loading = false;

        // Log success
        console.log(`✅ Application initialized`);

        // Show welcome notification
        this.showNotification('Application is ready!', 'success');

        // Emit ready event
        this.emit('app:ready', {
            initialized: true,
            timestamp: Date.now(),
            uptime: Date.now() - this.startTime
        });

        return this;
    }

    /**
     * Handle URL changes
     */
    handleURLChange(event) {
        const urlState = this.getURLState();

        // Emit app event
        this.emit('app:url:changed', {
            urlState,
            event
        });

        // Debug logging
        if (this.config.debug) {
            console.debug(`🔗 URL changed: ${urlState.previousUrl} → ${urlState.currentUrl}`);
        }
    }

    /**
     * Handle window resize
     */
    handleResize() {
        const isMobile = window.innerWidth <= 768;
        const isTablet = window.innerWidth <= 1024 && window.innerWidth > 768;

        this.emit('app:resize', {
            width: window.innerWidth,
            height: window.innerHeight,
            isMobile,
            isTablet,
            breakpoint: isMobile ? 'mobile' : isTablet ? 'tablet' : 'desktop'
        });
    }

    /**
     * Handle visibility change
     */
    handleVisibilityChange() {
        const visible = document.visibilityState === 'visible';
        const state = document.visibilityState;

        this.emit('app:visibility', {
            visible,
            state,
            timestamp: Date.now()
        });
    }

    /**
     * Handle errors
     */
    handleError(context, error) {
        const errorData = {
            context,
            error: error instanceof Error ? {
                message: error.message,
                stack: error.stack,
                name: error.name
            } : error,
            timestamp: new Date().toISOString(),
            url: window.location.href,
            userAgent: navigator.userAgent,
            appState: {
                initialized: this.initialized,
                loading: this.loading
            }
        };

        // Store error (limit to 50)
        this.errors.push(errorData);
        if (this.errors.length > 50) this.errors.shift();

        // Log error
        console.error(`❌ Error in ${context}:`, error);

        // Show user notification
        this.showNotification(`Error: ${error.message || 'Something went wrong'}`, 'error');

        // Emit event
        this.emit('app:error', errorData);

        return errorData;
    }

    /**
     * Log warning
     */
    logWarning(message, data = {}) {
        console.warn(`⚠️ ${message}`, data);
        this.emit('app:warning', { message, data, timestamp: Date.now() });
    }

    /**
     * Start loading
     */
    startLoading() {
        this.loading = true;
        this.emit('app:loading:start');
    }

    /**
     * Stop loading
     */
    stopLoading() {
        this.loading = false;
        this.emit('app:loading:stop');
    }

    /**
     * Event system methods
     */
    on(event, callback) {
        if (!this.events.has(event)) {
            this.events.set(event, new Set());
        }
        this.events.get(event).add(callback);

        return () => this.off(event, callback);
    }

    off(event, callback) {
        if (this.events.has(event)) {
            this.events.get(event).delete(callback);
        }
    }

    emit(event, data = {}) {
        // Call internal event handlers
        if (this.events.has(event)) {
            this.events.get(event).forEach(callback => {
                try {
                    callback({ ...data, event, timestamp: Date.now(), app: this });
                } catch (err) {
                    console.error(`Error in ${event} handler:`, err);
                }
            });
        }

        // Also dispatch as DOM event
        const customEvent = new CustomEvent(event, {
            detail: { ...data, app: this },
            bubbles: true
        });
        document.dispatchEvent(customEvent);
    }

    /**
     * Manager access methods
     */
    getManager(name) {
        return this.managers[name] || null;
    }

    getAllManagers() {
        return { ...this.managers };
    }

    /**
     * Get module from module manager
     */
    getModule(moduleId) {
        return this.managers.modules?.getModule?.(moduleId) || null;
    }

    /**
     * Check if module exists
     */
    hasModule(moduleId) {
        return this.managers.modules?.hasModule?.(moduleId) || false;
    }

    /**
     * Load a module dynamically
     */
    async loadModule(moduleId) {
        if (this.managers.modules?.loadModule) {
            return await this.managers.modules.loadModule(moduleId);
        }
        return null;
    }

    /**
     * Get all modules
     */
    getModules() {
        return this.managers.modules?.getModules?.() || [];
    }

    /**
     * Get UI component
     */
    getComponent(componentId) {
        return this.managers.ui?.getComponent?.(componentId) || null;
    }

    /**
     * Check if UI component exists
     */
    hasComponent(componentId) {
        return this.managers.ui?.hasComponent?.(componentId) || false;
    }

    /**
     * Notification helpers
     */
    showNotification(message, type = 'info', options = {}) {
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };

        const icon = icons[type] || '📢';
        // console.log(`${icon} ${message}`);

        // Use NotificationModule if available
        if (NotificationModule) {
            return NotificationModule.show(message, { type, ...options });
        }

        return null;
    }

    showSuccess(message, options = {}) {
        return this.showNotification(message, 'success', options);
    }

    showError(message, options = {}) {
        return this.showNotification(message, 'error', options);
    }

    showWarning(message, options = {}) {
        return this.showNotification(message, 'warning', options);
    }

    showInfo(message, options = {}) {
        return this.showNotification(message, 'info', options);
    }

    /**
     * Navigation helpers
     */
    navigateTo(url, options = {}) {
        return super.navigateTo(url, options);
    }

    goBack() {
        window.history.back();
    }

    refresh() {
        window.location.reload();
    }

    /**
     * Public API methods
     */
    getURLState() {
        return super.getURLState();
    }

    getStats() {
        return {
            initialized: this.initialized,
            loading: this.loading,
            errors: this.errors.length,
            modules: this.managers.modules?.getModuleCount?.() || 0,
            components: this.managers.ui?.getComponentCount?.() || 0,
            urlState: this.getURLState(),
            uptime: Date.now() - this.startTime
        };
    }

    /**
     * Performance methods
     */
    startTimer(name) {
        this.timers.set(name, performance.now());
        return name;
    }

    endTimer(name) {
        if (!this.timers.has(name)) return 0;
        const duration = performance.now() - this.timers.get(name);
        this.timers.delete(name);

        if (this.config.debug && duration > 100) {
            console.warn(`Timer ${name} took ${duration.toFixed(2)}ms`);
        }

        return duration;
    }

    /**
     * Configuration methods
     */
    updateConfig(config) {
        Object.assign(this.config, config);

        // Update manager configurations
        if (config.managers) {
            Object.entries(config.managers).forEach(([name, managerConfig]) => {
                const manager = this.managers[name];
                if (manager && manager.updateConfig) {
                    manager.updateConfig(managerConfig);
                }
            });
        }

        this.emit('app:config:updated', { config });
        return this;
    }

    /**
     * Cleanup
     */
    async destroy() {
        console.log('🧹 Cleaning up application...');

        // Destroy managers
        const managers = ['ui', 'modules'];

        for (const managerName of managers) {
            const manager = this.managers[managerName];
            if (manager && typeof manager.destroy === 'function') {
                try {
                    await manager.destroy();
                    console.log(`✅ ${managerName} manager destroyed`);
                } catch (error) {
                    console.error(`Failed to destroy ${managerName} manager:`, error);
                }
            }
        }

        // Destroy URL tracking
        if (this.isURLTracking) {
            this.destroyURLTracking();
        }

        // Clear events
        this.events.clear();

        // Reset state
        this.initialized = false;
        this.loading = false;
        this.timers.clear();

        this.emit('app:destroyed');
        console.log('✅ Application cleaned up');
    }

    /**
     * Static creator
     */
    static async create(config = {}) {
        const app = new Application(config);
        await app.init();
        return app;
    }
}

/**
 * Singleton instance
 */
let appInstance = null;

export const createApp = (config = {}) => {
    if (!appInstance) {
        appInstance = new Application(config);

        // Auto-initialize on DOM ready
        if (config.autoInit !== false && typeof document !== 'undefined') {
            document.addEventListener('DOMContentLoaded', () => {
                setTimeout(() => {
                    appInstance.init().catch(error => {
                        console.error('Failed to initialize application:', error);
                        document.dispatchEvent(new CustomEvent('app:init:failed', {
                            detail: { error }
                        }));
                    });
                }, 100);
            });
        }
    }

    return appInstance;
};

// Export singleton
export const app = createApp();

// Global access
if (typeof window !== 'undefined') {
    window.App = app;
    window.Application = Application;
}

export default app;
