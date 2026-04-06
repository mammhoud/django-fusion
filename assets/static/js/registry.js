/**
 * @file registry.js
 * @description Unified Registry Manager that coordinates services, plugins, and module loading.
 * This class serves as the central orchestration point for the application's infrastructure.
 * @module RegistryManager
 */

import { BaseManager } from './utility/base.manager.js';
import { moduleManager } from './modules/manager.init.js';
import {
    ConfigHelpers,
    DEFAULT_LAYOUT,
    PAGE_TYPE_MAPPINGS,
    APP_SUB_TYPES
} from './config.helpers.js';

/**
 * Unified Registry Manager
 * @extends BaseManager
 */
export class RegistryManager extends BaseManager {
    /**
     * @param {Object} config - Registry configuration
     */
    constructor(config = {}) {
        super({
            debug: false,
            autoInitialize: true,

            // Core Service configuration (Implemented in modules/handlers/)
            services: {
                events: { enabled: true, priority: 1 },
                cookies: { enabled: true, priority: 3 },
                storage: { enabled: true, priority: 2 }, // Alias for cookies in serviceHandlers
                notifications: { enabled: true, priority: 6 }, // SSE-based notifications
                sse: { enabled: true, priority: 5 }, // SSE security/connection handling
                ...config.services
            },

            // Plugin configuration (Currently placeholders or for future use)
            plugins: {
                ...config.plugins
            },

            // Module configuration (Managed via ModuleManager)
            modules: {
                utility: {
                    enabled: true,
                    priority: 1,
                    alwaysLoad: true,
                    loader: () => import('./utility/index.js')
                },
                components: {
                    enabled: true,
                    priority: 3,
                    alwaysLoad: false,
                    loader: () => import('./modules/index.js')
                },
                ...config.modules
            },

            // Registry settings
            registry: {
                enablePageDetection: true,
                enableAutoRegistration: true,
                lazyLoadPlugins: false,
                isolatePluginErrors: true,
                ...config.registry
            },

            ...config
        });

        /** @type {ModuleManager} Reference to the module loader */
        this.moduleLoader = moduleManager;

        /** @type {Map} Internal registry for service instances */
        this.serviceRegistry = new Map();

        /** @type {Map} Internal registry for plugin instances */
        this.pluginRegistry = new Map();

        /** @type {Map} Internal registry for component metadata */
        this.componentRegistry = new Map();

        /** @type {Object|null} Application context */
        this.app = null;

        /** @type {Object|null} Detected page metadata */
        this.pageInfo = null;

        /** @type {Object} Performance metrics */
        this.performance = {
            initializationTime: 0,
            serviceLoadTimes: new Map(),
            pluginLoadTimes: new Map()
        };

        this.initCoreRegistries();
    }

    /**
     * Initialize core registries and default components
     * @private
     */
    initCoreRegistries() {
        this.serviceHandlers = new Map();
        this.pluginFactories = new Map();

        // Register default layout components
        this.registerDefaultComponents();
    }

    /**
     * Register default components that should always be considered
     * @private
     */
    registerDefaultComponents() {
        const defaults = {
            'layout-header': { priority: 1, alwaysLoad: true },
            'layout-footer': { priority: 1, alwaysLoad: true }
        };

        Object.entries(defaults).forEach(([name, config]) => {
            this.componentRegistry.set(name, config);
        });
    }

    /**
     * Initialize the registry with the application context
     * @param {Application} app - The main application instance
     * @returns {Promise<RegistryManager>}
     */
    async init(app) {
        if (this.initialized) return this;

        this.app = app || this.createAppContext();
        this.startLoading();
        const startTime = performance.now();

        try {
            this.log('🚀 Initializing Unified Registry...');

            // Step 1: Detect page if enabled
            if (this.config.registry.enablePageDetection) {
                await this.detectPage();
            }

            // Step 2: Initialize core services
            await this.initServices();

            // Step 3: Initialize modules via moduleLoader
            await this.initModules();

            // Step 4: Initialize custom components
            await this.initComponents();

            this.initialized = true;
            this.performance.initializationTime = performance.now() - startTime;

            this.log(`✅ Registry ready in ${this.performance.initializationTime.toFixed(2)}ms`);
            this.dispatch('registry:ready', this.getRegistryState());

        } catch (error) {
            this.handleError(error, 'registry-init');
        } finally {
            this.stopLoading();
        }

        return this;
    }

    /**
     * Detect current page information and apply layout classes
     * @private
     */
    async detectPage() {
        try {
            this.pageInfo = {
                type: ConfigHelpers.determinePageType(),
                layout: ConfigHelpers.detectLayoutFromURL(),
                subType: ConfigHelpers.detectSubTypeFromURL(),
                path: window.location.pathname,
                url: window.location.href,
                title: document.title,
                timestamp: Date.now()
            };

            const { components, elements } = ConfigHelpers.detectPageComponents();
            this.pageInfo.components = elements;
            this.pageInfo.features = components;

            ConfigHelpers.applyLayoutClasses(this.pageInfo.layout, this.pageInfo.subType);

            this.dispatch('page:detected', this.pageInfo);
            this.log(`📄 Page Type: ${this.pageInfo.type} | Layout: ${this.pageInfo.layout}`);

        } catch (error) {
            this.log('⚠️ Page detection failed:', error);
            this.pageInfo = {
                type: 'unknown',
                layout: 'default',
                path: window.location.pathname,
                timestamp: Date.now()
            };
        }
    }

    /**
     * Initialize registered services
     * @private
     */
    async initServices() {
        const serviceEntries = Object.entries(this.config.services)
            .filter(([_, config]) => config.enabled !== false)
            .sort(([_, a], [__, b]) => (a.priority || 50) - (b.priority || 50));

        for (const [name, config] of serviceEntries) {
            await this.initService(name, config);
        }
    }

    /**
     * Initialize a single service
     * @param {string} name - Service name
     * @param {Object} config - Service configuration
     * @private
     */
    async initService(name, config) {
        const startTime = performance.now();

        try {
            this.log(`🔧 Initializing service: ${name}`);

            let service;
            if (config.handler) {
                const Handler = config.handler;
                service = new Handler(config);
            } else {
                service = await this.loadServiceModule(name, config);
            }

            if (typeof service.init === 'function') {
                await service.init(this.app, this.getServiceDependencies(name));
            }

            this.serviceRegistry.set(name, {
                instance: service,
                config,
                loadTime: performance.now() - startTime,
                dependencies: config.dependencies || []
            });

            this.performance.serviceLoadTimes.set(name, performance.now() - startTime);
            this.dispatch('service:initialized', { name, service, config });

        } catch (error) {
            this.handleError(`Failed to initialize service: ${name}`, error);

            if (config.critical !== false) {
                const fallback = this.createServiceFallback(name);
                this.serviceRegistry.set(name, {
                    instance: fallback,
                    config: { ...config, fallback: true },
                    loadTime: 0,
                    isFallback: true
                });
            }
        }
    }

    /**
     * Dynamically load a service module from the handlers directory
     * @param {string} name - Service filename
     * @param {Object} config - Service configuration
     * @private
     */
    async loadServiceModule(name, config) {
        try {
            const module = await import(`./modules/handlers/${name}.js`);
            const capitalizedName = name.charAt(0).toUpperCase() + name.slice(1);
            const ServiceClass = module.default ||
                module[`${capitalizedName}Service`] ||
                module[`${capitalizedName}Handler`] ||
                module[`${name}Service`] ||
                module[`${name}Handler`];

            if (!ServiceClass) {
                const exportedClass = Object.values(module).find(
                    exp => typeof exp === 'function' && exp.prototype
                );
                if (exportedClass) return new exportedClass(config);
                throw new Error(`Service class not found for: ${name}`);
            }

            return new ServiceClass(config);
        } catch (error) {
            throw new Error(`Failed to load service module ${name}: ${error.message}`);
        }
    }

    /**
     * Initialize modules through the ModuleManager
     * @private
     */
    async initModules() {
        Object.entries(this.config.modules).forEach(([id, config]) => {
            if (config.enabled !== false) {
                this.moduleLoader.registerModule(id, config);
            }
        });

        const modulesToLoad = this.getModulesForCurrentPage();
        if (modulesToLoad.length > 0) {
            await this.moduleLoader.load(modulesToLoad, {
                app: this.app,
                page: this.pageInfo,
                services: this.getAllServices()
            });
        }
    }

    /**
     * Determine which modules should be loaded for the current page state
     * @returns {string[]}
     * @private
     */
    getModulesForCurrentPage() {
        const modules = [];
        for (const [id, config] of Object.entries(this.config.modules)) {
            if (config.alwaysLoad && config.enabled !== false) {
                modules.push(id);
            }
        }
        return [...new Set(modules)];
    }

    /**
     * Initialize component metadata registration
     * @private
     */
    async initComponents() {
        for (const [name, config] of this.componentRegistry) {
            if (config.enabled !== false) {
                this.dispatch('component:registered', { name, config });
            }
        }
    }

    /**
     * Create a basic application context if one is not provided
     * @private
     */
    createAppContext() {
        return {
            name: document.title || 'App',
            version: '1.0.0',
            environment: this.config.debug ? 'development' : 'production',
            timestamp: Date.now(),
            registry: this
        };
    }

    /**
     * Create fallback behaviors for critical services
     * @private
     */
    createServiceFallback(name) {
        if (name === 'events') {
            const listeners = new Map();
            return {
                on: (event, callback) => {
                    if (!listeners.has(event)) listeners.set(event, []);
                    listeners.get(event).push(callback);
                },
                emit: (event, data) => {
                    (listeners.get(event) || []).forEach(cb => cb(data));
                }
            };
        }
        return { init: () => Promise.resolve(), error: `Fallback for ${name}` };
    }

    /**
     * Resolve service dependencies
     * @private
     */
    getServiceDependencies(serviceName) {
        const config = this.config.services[serviceName];
        if (!config || !config.dependencies) return {};
        const dependencies = {};
        config.dependencies.forEach(depName => {
            const service = this.getService(depName);
            if (service) dependencies[depName] = service;
        });
        return dependencies;
    }

    /* ---- Public API ---- */

    getService(name) {
        const data = this.serviceRegistry.get(name);
        return data ? data.instance : null;
    }

    getAllServices() {
        const services = {};
        for (const [name, data] of this.serviceRegistry.entries()) {
            services[name] = data.instance;
        }
        return services;
    }

    getRegistryState() {
        return {
            initialized: this.initialized,
            services: Array.from(this.serviceRegistry.keys()),
            loadedModules: Array.from(this.moduleLoader.loadedModules.keys()),
            page: this.pageInfo
        };
    }
}

// Create singleton instance
export const registry = new RegistryManager();
export default registry;
