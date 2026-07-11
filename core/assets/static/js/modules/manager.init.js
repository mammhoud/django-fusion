/**
 * @file modules/manager.init.js
 * Module Manager with full integration of all modules
 */

import { BaseManager } from '../utility/base.manager.js';


/**
 * Enhanced Module Loader with better caching and error handling
 */
class ModuleManager extends BaseManager {
    constructor(config = {}) {
        super({
            cacheModules: true,
            debug: false,
            lazyLoad: true,
            skipMissing: true,
            batchSize: 4,
            prioritySorting: true,
            prefetchOnIdle: false,
            retryFailed: false,
            maxRetries: 2,
            ...config
        });

        this.modules = new Map();
        this.cache = new Map();
        this.loadedModules = new Map();
        this.loadingModules = new Set();
        this.failedModules = new Set();

        this.metrics = {
            loadTimes: new Map(),
            cacheHits: 0,
            cacheMisses: 0,
            retryAttempts: 0,
            prefetches: 0
        };
    }

    /**
     * Register module with enhanced validation
     */
    registerModule(id, config) {
        const moduleConfig = {
            id,
            name: id,
            priority: 50,
            alwaysLoad: false,
            category: 'general',
            dependencies: [],
            requires: [],
            critical: false,
            version: '1.0.0',
            description: '',
            tags: [],
            condition: () => true,
            onLoad: null,
            onError: null,
            ...config
        };

        // Validate config
        if (!config.loader && !config.component) {
            throw new Error(`Module ${id} must have a loader or component`);
        }

        this.modules.set(id, moduleConfig);
        this.log(`📦 Module registered: ${id} (${moduleConfig.category})`);

        return this;
    }

    /**
     * Register multiple modules with dependency resolution
     */
    registerModules(modules) {
        // First pass: register all modules
        modules.forEach(module => {
            this.registerModule(module.id, module);
        });

        // Second pass: validate dependencies
        for (const [id, config] of this.modules) {
            const missingDeps = config.dependencies.filter(dep => !this.modules.has(dep));
            if (missingDeps.length > 0) {
                this.log(`⚠️ Module ${id} has missing dependencies: ${missingDeps.join(', ')}`);
            }
        }

        return this;
    }

    /**
     * Smart module loading with dependency resolution
     */
    async load(moduleIds, context = {}) {
        if (!Array.isArray(moduleIds)) {
            moduleIds = [moduleIds];
        }

        // Filter by condition if provided
        const filteredIds = moduleIds.filter(id => {
            const config = this.modules.get(id);
            return config && config.condition(context);
        });

        // Resolve dependencies
        const allModules = this.resolveDependencies(filteredIds);

        // Sort by priority
        const sortedModules = this.sortModulesByPriority(allModules);

        // Load in batches
        return await this.loadBatchWithProgress(sortedModules, context);
    }

    /**
     * Resolve module dependencies
     */
    resolveDependencies(moduleIds) {
        const resolved = new Set();
        const seen = new Set();

        const resolve = (id) => {
            if (seen.has(id)) return;
            seen.add(id);

            const config = this.modules.get(id);
            if (!config) return;

            // Resolve dependencies first
            config.dependencies.forEach(depId => {
                if (!resolved.has(depId)) {
                    resolve(depId);
                }
            });

            resolved.add(id);
        };

        moduleIds.forEach(id => resolve(id));
        return Array.from(resolved);
    }

    /**
     * Sort modules by priority
     */
    sortModulesByPriority(moduleIds) {
        return moduleIds.sort((a, b) => {
            const configA = this.modules.get(a);
            const configB = this.modules.get(b);
            const priorityA = configA?.priority ?? 50;
            const priorityB = configB?.priority ?? 50;
            return priorityA - priorityB;
        });
    }

    /**
     * Load a batch of modules
     */
    async loadModuleBatch(moduleIds, context) {
        const results = await Promise.allSettled(
            moduleIds.map(id => this.loadSingleModule(id, context))
        );
        
        return results
            .filter(result => result.status === 'fulfilled')
            .map(result => result.value);
    }

    /**
     * Load with progress tracking
     */
    async loadBatchWithProgress(moduleIds, context) {
        const results = [];
        const total = moduleIds.length;

        this.dispatch('modules:loading:start', {
            total,
            modules: moduleIds
        });

        for (let i = 0; i < moduleIds.length; i += this.config.batchSize) {
            const batch = moduleIds.slice(i, i + this.config.batchSize);

            this.dispatch('modules:batch:start', {
                batch,
                index: i,
                total
            });

            const batchResults = await this.loadModuleBatch(batch, context);
            results.push(...batchResults);

            this.dispatch('modules:batch:complete', {
                batch,
                loaded: batchResults.length,
                failed: batch.length - batchResults.length
            });
        }

        this.dispatch('modules:loading:complete', {
            loaded: results.length,
            total
        });

        return results;
    }

    /**
     * Load module with retry logic
     */
    async loadSingleModule(moduleId, context = {}) {
        // Check cache
        if (this.config.cacheModules && this.cache.has(moduleId)) {
            this.metrics.cacheHits++;
            const cached = this.cache.get(moduleId);
            this.dispatch('module:cache:hit', { moduleId, cached });
            return cached;
        }

        // Check if loading
        if (this.loadingModules.has(moduleId)) {
            return this.waitForModule(moduleId);
        }

        // Check if previously failed and retry disabled
        if (this.failedModules.has(moduleId) && !this.config.retryFailed) {
            throw new Error(`Module ${moduleId} previously failed to load`);
        }

        const config = this.modules.get(moduleId);
        if (!config) {
            throw new Error(`Module ${moduleId} not registered`);
        }

        this.loadingModules.add(moduleId);
        const startTime = performance.now();

        try {
            this.metrics.cacheMisses++;
            this.dispatch('module:loading:start', { moduleId, config });

            // Attempt loading with retries
            const loadWithRetry = async (attempt = 1) => {
                try {
                    const module = await this.importModule(config, context);
                    const instance = this.extractModuleInstance(module, config);
                    const initialized = await this.initializeModule(moduleId, instance, context);

                    // Call onLoad hook if provided
                    if (config.onLoad && typeof config.onLoad === 'function') {
                        await config.onLoad(initialized, context);
                    }

                    // Cache if enabled
                    if (this.config.cacheModules) {
                        try {
                            this.cache.set(moduleId, initialized);
                        } catch (cacheError) {
                            this.log(`Failed to cache module ${moduleId}:`, cacheError);
                        }
                    }

                    this.loadedModules.set(moduleId, initialized);

                    const loadTime = performance.now() - startTime;
                    this.metrics.loadTimes.set(moduleId, loadTime);

                    this.dispatch('module:loaded', {
                        moduleId,
                        instance: initialized,
                        loadTime,
                        attempt
                    });

                    // Clear from failed set if retry succeeded
                    this.failedModules.delete(moduleId);

                    return initialized;

                } catch (error) {
                    // Call onError hook if provided
                    if (config.onError && typeof config.onError === 'function') {
                        await config.onError(error, attempt);
                    }

                    if (attempt < (this.config.maxRetries + 1) && config.critical !== false) {
                        this.metrics.retryAttempts++;
                        this.dispatch('module:retry', {
                            moduleId,
                            attempt: attempt + 1,
                            error: error.message
                        });
                        return loadWithRetry(attempt + 1);
                    }
                    throw error;
                }
            };

            return await loadWithRetry();

        } catch (error) {
            this.failedModules.add(moduleId);

            // Try fallback
            if (config.fallback) {
                try {
                    const fallback = await config.fallback();
                    this.dispatch('module:fallback:used', { moduleId, fallback });
                    return fallback;
                } catch (fallbackError) {
                    this.log(`Fallback for ${moduleId} also failed:`, fallbackError);
                }
            }

            // Handle critical module failure
            if (config.critical) {
                this.dispatch('module:critical:failed', {
                    moduleId,
                    error: error.message
                });
                throw new Error(`Critical module ${moduleId} failed to load: ${error.message}`);
            }

            this.handleError(`Failed to load module ${moduleId}`, error);
            throw error;
        } finally {
            this.loadingModules.delete(moduleId);
        }
    }

    /**
     * Import module with context
     */
    async importModule(config, context) {
        if (config.loader) {
            return await config.loader(context);
        } else if (config.component) {
            return { default: config.component };
        } else if (config.url) {
            // Dynamic import from URL
            return await import(/* webpackIgnore: true */ config.url);
        }
        throw new Error(`No loader or component for module ${config.id}`);
    }

    /**
     * Enhanced module instance extraction
     */
    extractModuleInstance(module, config) {
        // Check for default export
        if (module.default) {
            // If default is a function, it might be a class or function
            if (typeof module.default === 'function') {
                return module.default;
            }
            // If default is an object with init/initialize methods
            if (typeof module.default === 'object' && module.default !== null) {
                if (module.default.init || module.default.initialize) {
                    return module.default;
                }
            }
            return module.default;
        }

        // Check for named export matching config
        if (config.exportName && module[config.exportName]) {
            return module[config.exportName];
        }

        // Try to find common patterns
        const className = config.name?.replace(/\s+/g, '');
        if (className && module[className]) {
            return module[className];
        }

        // Return the whole module as last resort
        return module;
    }

    /**
     * Initialize module with context
     */
    async initializeModule(moduleId, instance, context) {
        if (!instance) return instance;

        const initContext = {
            ...context,
            loader: this,
            log: this.log.bind(this),
            dispatch: this.dispatch.bind(this)
        };

        try {
            // Try different initialization patterns
            if (typeof instance.init === 'function') {
                await instance.init(initContext);
            } else if (typeof instance.initialize === 'function') {
                await instance.initialize(initContext);
            } else if (typeof instance.setup === 'function') {
                await instance.setup(initContext);
            } else if (typeof instance === 'function') {
                // Module is a class constructor
                const constructed = new instance(initContext);
                if (typeof constructed.init === 'function') {
                    await constructed.init(initContext);
                }
                return constructed;
            }
        } catch (error) {
            this.log(`⚠️ Module ${moduleId} initialization had errors:`, error.message);
            // Don't rethrow - return the instance anyway
        }

        return instance;
    }

    /**
     * Wait for module with timeout
     */
    waitForModule(moduleId, timeout = 10000) {
        return new Promise((resolve, reject) => {
            const startTime = Date.now();

            const checkInterval = setInterval(() => {
                if (this.loadedModules.has(moduleId)) {
                    clearInterval(checkInterval);
                    clearTimeout(timeoutId);
                    resolve(this.loadedModules.get(moduleId));
                } else if (Date.now() - startTime > timeout) {
                    clearInterval(checkInterval);
                    reject(new Error(`Timeout waiting for module ${moduleId}`));
                }
            }, 50);

            const timeoutId = setTimeout(() => {
                clearInterval(checkInterval);
                reject(new Error(`Timeout waiting for module ${moduleId}`));
            }, timeout);
        });
    }

    /**
     * Prefetch modules during idle time
     */
    async prefetchModules(moduleIds, priority = 'low') {
        if (!this.config.prefetchOnIdle || typeof requestIdleCallback !== 'function') {
            return;
        }

        return new Promise((resolve) => {
            requestIdleCallback(async () => {
                try {
                    this.metrics.prefetches++;

                    // Only prefetch modules not already loaded or cached
                    const toPrefetch = moduleIds.filter(id =>
                        !this.loadedModules.has(id) &&
                        !this.cache.has(id) &&
                        !this.loadingModules.has(id)
                    );

                    if (toPrefetch.length === 0) {
                        resolve([]);
                        return;
                    }

                    this.dispatch('modules:prefetch:start', {
                        modules: toPrefetch,
                        priority
                    });

                    // Load with low priority (non-blocking)
                    const results = await Promise.allSettled(
                        toPrefetch.map(async (id) => {
                            try {
                                const module = await this.importModule(this.modules.get(id), {});
                                // Only cache, don't initialize
                                this.cache.set(id, module);
                                return { id, success: true };
                            } catch (error) {
                                return { id, success: false, error: error.message };
                            }
                        })
                    );

                    this.dispatch('modules:prefetch:complete', {
                        results: results.map(r => r.value)
                    });

                    resolve(results.map(r => r.value));
                } catch (error) {
                    this.log('Prefetch failed:', error);
                    resolve([]);
                }
            }, { timeout: 5000 });
        });
    }

    /**
     * Get module with fallback
     */
    async getModule(moduleId, fallback = null) {
        try {
            // Try to get from cache or loaded modules
            if (this.loadedModules.has(moduleId)) {
                return this.loadedModules.get(moduleId);
            }
            if (this.cache.has(moduleId)) {
                return this.cache.get(moduleId);
            }

            // Try to load it
            return await this.loadSingleModule(moduleId);
        } catch (error) {
            this.log(`Cannot get module ${moduleId}:`, error.message);
            return fallback;
        }
    }

    /**
     * Check if module exists and is loadable
     */
    hasModule(moduleId) {
        return this.modules.has(moduleId) ||
            this.loadedModules.has(moduleId) ||
            this.cache.has(moduleId);
    }

    /**
     * Clear cache selectively
     */
    clearCache(pattern = null) {
        let cleared = 0;

        if (pattern) {
            // Clear by pattern (regex or function)
            const test = typeof pattern === 'function'
                ? pattern
                : (key) => new RegExp(pattern).test(key);

            for (const [key] of this.cache) {
                if (test(key)) {
                    this.cache.delete(key);
                    this.loadedModules.delete(key);
                    cleared++;
                }
            }
        } else {
            // Clear all
            cleared = this.cache.size;
            this.cache.clear();
            this.loadedModules.clear();
        }

        this.dispatch('cache:cleared', { cleared, pattern });
        return cleared;
    }

    /**
     * Get enhanced metrics
     */
    getEnhancedMetrics() {
        const total = this.metrics.cacheHits + this.metrics.cacheMisses;

        return {
            registered: this.modules.size,
            loaded: this.loadedModules.size,
            cached: this.cache.size,
            loading: this.loadingModules.size,
            failed: this.failedModules.size,
            cacheHits: this.metrics.cacheHits,
            cacheMisses: this.metrics.cacheMisses,
            hitRate: total > 0 ? (this.metrics.cacheHits / total * 100).toFixed(1) + '%' : '0%',
            retryAttempts: this.metrics.retryAttempts,
            prefetches: this.metrics.prefetches,
            avgLoadTime: this.getAverageLoadTime()
        };
    }

    getAverageLoadTime() {
        const times = Array.from(this.metrics.loadTimes.values());
        return times.length > 0
            ? times.reduce((a, b) => a + b, 0) / times.length
            : 0;
    }
}

// Create singleton instance
export const moduleManager = new ModuleManager();

// Export the class for extension
export { ModuleManager };

// Auto-initialize with app if available
if (typeof window !== 'undefined' && window.app) {
    document.addEventListener('DOMContentLoaded', () => {
        moduleManager.init(window.app).catch(console.error);
    });
}