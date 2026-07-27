/**
 * @file base-manager.js
 * Base Manager class with common functionality for all managers
 */

export class BaseManager {
    constructor(config = {}) {
        this.config = {
            debug: config.debug || false,
            performanceTracking: true,
            autoInitialize: true,
            ...config
        };

        this.initialized = false;
        this.isLoading = false;
        this.hasErrors = false;
        this.items = new Map(); // Generic storage for services, modules, plugins, components

        this.metrics = {
            loadTime: 0,
            itemLoadTimes: new Map(),
            itemCount: 0,
            errors: []
        };

        this.events = new Map();
    }

    /**
     * Initialize the manager (to be implemented by child classes)
     */
    async init(app) {
        throw new Error('init() method must be implemented by child class');
    }

    /**
     * Add an item to the manager
     */
    set(name, item, metadata = {}) {
        this.items.set(name, {
            instance: item,
            metadata: {
                added: Date.now(),
                ...metadata
            }
        });

        this.metrics.itemCount = this.items.size;

        this.dispatch('item:added', {
            name,
            item,
            metadata,
            itemCount: this.items.size
        });

        this.log(`✅ Item added: ${name}`);
        return this;
    }

    /**
     * Get an item from the manager
     */
    get(name) {
        const item = this.items.get(name);
        return item ? item.instance : null;
    }

    /**
     * Get item with metadata
     */
    getWithMetadata(name) {
        return this.items.get(name);
    }

    /**
     * Check if item exists
     */
    has(name) {
        return this.items.has(name);
    }

    /**
     * Remove an item from the manager
     */
    async remove(name) {
        const item = this.items.get(name);

        if (item) {
            // Call destroy method if it exists
            if (typeof item.instance.destroy === 'function') {
                try {
                    await item.instance.destroy();
                } catch (error) {
                    console.warn(`Error destroying item ${name}:`, error);
                }
            }

            this.items.delete(name);
            this.metrics.itemCount = this.items.size;

            this.dispatch('item:removed', {
                name,
                item,
                itemCount: this.items.size
            });

            this.log(`🗑️ Item removed: ${name}`);
            return true;
        }

        return false;
    }

    /**
     * Get all items
     */
    getAll() {
        const result = {};

        this.items.forEach((item, name) => {
            result[name] = item.instance;
        });

        return result;
    }

    /**
     * Get all items with metadata
     */
    getAllWithMetadata() {
        const result = {};

        this.items.forEach((item, name) => {
            result[name] = item;
        });

        return result;
    }

    /**
     * Get item names
     */
    getNames() {
        return Array.from(this.items.keys());
    }

    /**
     * Get item count
     */
    getCount() {
        return this.items.size;
    }

    /**
     * Update configuration
     */
    updateConfig(config) {
        Object.assign(this.config, config);

        this.dispatch('config:updated', {
            config: this.config
        });

        return this;
    }

    /**
     * Get configuration
     */
    getConfig() {
        return { ...this.config };
    }

    /**
     * Get metrics
     */
    getMetrics() {
        return {
            ...this.metrics,
            itemCount: this.items.size,
            initialized: this.initialized,
            isLoading: this.isLoading,
            hasErrors: this.hasErrors
        };
    }

    /**
     * Add event listener
     */
    on(event, callback) {
        if (!this.events.has(event)) {
            this.events.set(event, new Set());
        }
        this.events.get(event).add(callback);
        return this;
    }

    /**
     * Remove event listener
     */
    off(event, callback) {
        if (this.events.has(event)) {
            this.events.get(event).delete(callback);
        }
        return this;
    }

    /**
     * Dispatch event
     */
    dispatch(event, data = {}) {
        // Call registered callbacks
        if (this.events.has(event)) {
            this.events.get(event).forEach(callback => {
                try {
                    callback({ ...data, manager: this, event });
                } catch (error) {
                    console.error(`Error in event callback for ${event}:`, error);
                }
            });
        }

        // Also dispatch as CustomEvent on document
        const customEvent = new CustomEvent(`manager:${event}`, {
            detail: { ...data, manager: this },
            bubbles: true
        });
        document.dispatchEvent(customEvent);

        return this;
    }

    /**
     * Log message if debug is enabled
     */
    log(...args) {
        if (this.config.debug) {
            console.log(`[${this.constructor.name}]`, ...args);
        }
    }

    /**
     * Log error
     */
    error(context, error) {
        const errorInfo = {
            message: error.message,
            stack: error.stack,
            context,
            timestamp: Date.now()
        };

        this.metrics.errors.push(errorInfo);

        console.error(`[${this.constructor.name}] Error in ${context}:`, error.message);
        this.dispatch('error', errorInfo);

        this.hasErrors = true;
    }

    /**
     * Handle error with context
     */
    handleError(error, context) {
        this.error(context, error);
        return null;
    }

    /**
     * Start loading
     */
    startLoading() {
        this.isLoading = true;
        this.dispatch('loading:start');
        return this;
    }

    /**
     * Stop loading
     */
    stopLoading() {
        this.isLoading = false;
        this.dispatch('loading:stop');
        return this;
    }

    /**
     * Reset metrics
     */
    resetMetrics() {
        this.metrics = {
            loadTime: 0,
            itemLoadTimes: new Map(),
            itemCount: this.items.size,
            errors: []
        };

        return this;
    }

    /**
     * Clear all items
     */
    async clear() {
        const removePromises = Array.from(this.items.keys()).map(name =>
            this.remove(name)
        );

        await Promise.allSettled(removePromises);

        this.dispatch('cleared');
        return this;
    }

    /**
     * Destroy manager
     */
    async destroy() {
        await this.clear();

        // Clear events
        this.events.clear();

        // Reset state
        this.initialized = false;
        this.isLoading = false;
        this.resetMetrics();

        this.dispatch('destroyed');
        this.log('Manager destroyed');

        return this;
    }

    /**
     * Static helper to check if manager is an instance of BaseManager
     */
    static isManager(obj) {
        return obj instanceof BaseManager;
    }
}