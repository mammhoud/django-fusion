import { BaseManager } from '../lib/base-manager.js';
import { moduleManager } from '../lib/module-manager.js';
import { ConfigHelpers, DEFAULT_LAYOUT } from './config.js';

export class RegistryManager extends BaseManager {
    constructor(config = {}) {
        super({
            debug: false,
            autoInitialize: true,

            // ── Core services ─────────────────────────────────
            // Each maps to a file in modules/handlers/<name>.js
            services: {
                events:        { enabled: true, priority: 1 },
                cookies:       { enabled: true, priority: 2 },
                notifications: { enabled: true, priority: 3 },
                sse:           { enabled: true, priority: 4 },
                ...config.services,
            },

            // ── Modules ───────────────────────────────────────
            modules: {
                utility: {
                    enabled:    true,
                    priority:   1,
                    alwaysLoad: true,
                    loader:     () => import('../lib/index.js'),
                },
                components: {
                    enabled:    true,
                    priority:   2,
                    alwaysLoad: false,
                    loader:     () => import('../components/index.js'),
                },
                ...config.modules,
            },

            // ── Registry settings ─────────────────────────────
            registry: {
                enablePageDetection:    true,
                enableAutoRegistration: true,
                isolatePluginErrors:    true,
                ...config.registry,
            },

            ...config,
        });

        this.moduleLoader    = moduleManager;
        this.serviceRegistry = new Map();
        this.componentRegistry = new Map();
        this.app             = null;
        this.pageInfo        = null;
        this.performance     = {
            initializationTime: 0,
            serviceLoadTimes:   new Map(),
        };

        this._initCoreRegistries();
    }

    _initCoreRegistries() {
        // Default layout components always considered present
        this.componentRegistry.set('layout-sidebar', { priority: 1, alwaysLoad: true });
        this.componentRegistry.set('layout-navbar',  { priority: 1, alwaysLoad: true });
    }

    // ── Initialization ────────────────────────────────────────

    async init(app) {
        if (this.initialized) return this;

        this.app = app || this._createAppContext();
        this.startLoading();
        const t0 = performance.now();

        try {
            this.log('🚀 Initializing Registry...');

            if (this.config.registry.enablePageDetection) {
                await this._detectPage();
            }

            await this._initServices();
            await this._initModules();
            await this._initComponents();

            this.initialized = true;
            this.performance.initializationTime = performance.now() - t0;
            this.log(`✅ Registry ready in ${this.performance.initializationTime.toFixed(2)}ms`);
            this.dispatch('registry:ready', this.getRegistryState());

        } catch (error) {
            this.handleError(error, 'registry-init');
        } finally {
            this.stopLoading();
        }

        return this;
    }

    // ── Page detection ────────────────────────────────────────

    async _detectPage() {
        try {
            this.pageInfo = {
                type:      ConfigHelpers.determinePageType(),
                layout:    ConfigHelpers.detectLayoutFromURL(),
                subType:   ConfigHelpers.detectSubTypeFromURL(),
                path:      window.location.pathname,
                url:       window.location.href,
                title:     document.title,
                timestamp: Date.now(),
            };

            const { components, elements } = ConfigHelpers.detectPageComponents();
            this.pageInfo.components = elements;
            this.pageInfo.features   = components;

            ConfigHelpers.applyLayoutClasses(this.pageInfo.layout, this.pageInfo.subType);
            this.dispatch('page:detected', this.pageInfo);
            this.log(`📄 Page: ${this.pageInfo.type} | Layout: ${this.pageInfo.layout}`);

        } catch (error) {
            this.log('⚠️ Page detection failed:', error);
            this.pageInfo = {
                type:      'vcard',
                layout:    DEFAULT_LAYOUT,
                path:      window.location.pathname,
                timestamp: Date.now(),
            };
        }
    }

    // ── Services ──────────────────────────────────────────────

    async _initServices() {
        const entries = Object.entries(this.config.services)
            .filter(([, cfg]) => cfg.enabled !== false)
            .sort(([, a], [, b]) => (a.priority || 50) - (b.priority || 50));

        for (const [name, cfg] of entries) {
            await this._initService(name, cfg);
        }
    }

    async _initService(name, config) {
        const t0 = performance.now();
        try {
            this.log(`🔧 Service: ${name}`);
            const service = await this._loadServiceModule(name, config);

            if (typeof service.init === 'function') {
                await service.init(this.app, this._getServiceDeps(name));
            }

            this.serviceRegistry.set(name, {
                instance: service,
                config,
                loadTime: performance.now() - t0,
            });
            this.performance.serviceLoadTimes.set(name, performance.now() - t0);
            this.dispatch('service:initialized', { name, service });

        } catch (error) {
            this.handleError(`Service failed: ${name}`, error);
            // Provide a no-op fallback so the rest of the app keeps running
            this.serviceRegistry.set(name, {
                instance: this._createFallback(name),
                config:   { ...config, fallback: true },
                loadTime: 0,
                isFallback: true,
            });
        }
    }

    async _loadServiceModule(name, config) {
        if (config.handler) return new config.handler(config);

        const mod = await import(`../services/${name}.js`);
        const cap = name.charAt(0).toUpperCase() + name.slice(1);
        const Cls = mod.default
            || mod[`${cap}Service`]
            || mod[`${cap}Handler`]
            || Object.values(mod).find(v => typeof v === 'function' && v.prototype);

        if (!Cls) throw new Error(`No class found for service: ${name}`);
        return new Cls(config);
    }

    _createFallback(name) {
        if (name === 'events') {
            const listeners = new Map();
            return {
                on:   (e, cb) => { if (!listeners.has(e)) listeners.set(e, []); listeners.get(e).push(cb); },
                emit: (e, d)  => (listeners.get(e) || []).forEach(cb => cb(d)),
            };
        }
        return { init: () => Promise.resolve() };
    }

    _getServiceDeps(name) {
        const deps = this.config.services[name]?.dependencies || [];
        return Object.fromEntries(
            deps.map(d => [d, this.getService(d)]).filter(([, v]) => v)
        );
    }

    // ── Modules ───────────────────────────────────────────────

    async _initModules() {
        Object.entries(this.config.modules).forEach(([id, cfg]) => {
            if (cfg.enabled !== false) this.moduleLoader.registerModule(id, cfg);
        });

        const toLoad = Object.entries(this.config.modules)
            .filter(([, cfg]) => cfg.alwaysLoad && cfg.enabled !== false)
            .map(([id]) => id);

        if (toLoad.length > 0) {
            await this.moduleLoader.load(toLoad, {
                app:      this.app,
                page:     this.pageInfo,
                services: this.getAllServices(),
            });
        }
    }

    // ── Components ────────────────────────────────────────────

    async _initComponents() {
        for (const [name, cfg] of this.componentRegistry) {
            if (cfg.enabled !== false) {
                this.dispatch('component:registered', { name, cfg });
            }
        }
    }

    _createAppContext() {
        return {
            name:        document.title || 'vResume',
            version:     '1.0.0',
            environment: this.config.debug ? 'development' : 'production',
            timestamp:   Date.now(),
            registry:    this,
        };
    }

    // ── Public API ────────────────────────────────────────────

    getService(name) {
        return this.serviceRegistry.get(name)?.instance ?? null;
    }

    getAllServices() {
        return Object.fromEntries(
            [...this.serviceRegistry.entries()].map(([k, v]) => [k, v.instance])
        );
    }

    getRegistryState() {
        return {
            initialized:   this.initialized,
            services:      [...this.serviceRegistry.keys()],
            loadedModules: [...this.moduleLoader.loadedModules.keys()],
            page:          this.pageInfo,
        };
    }
}

export const registry = new RegistryManager();
export default registry;
