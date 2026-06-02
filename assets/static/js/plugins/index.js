/**
 * @file plugins/index.js
 * Plugin Manager
 */

import { BaseManager } from '../utility/base.manager.js';

/**
 * Plugin Item - Individual plugin wrapper
 * @description Reserved for future use when plugins need individual state management.
 * Currently plugins are managed directly by PluginManager.
 * @todo Integrate PluginItem for enhanced plugin lifecycle management
 */
class PluginItem extends BaseManager {
    constructor(name, plugin, config = {}) {
        super(config);
        this.name = name;
        this.plugin = plugin;
        this.type = 'plugin';
        this.requires = config.requires || [];
        this.priority = config.priority || 100;
        this.enabled = config.enabled !== false;
        this.instance = null;
        this.initialized = false;
        this.dependencies = {};
    }

    async init(app, services = {}) {
        if (!this.enabled) {
            this.log(`⏭️ Plugin ${this.name} disabled`);
            return null;
        }

        this.startLoading();
        
        try {
            this.log(`Initializing plugin: ${this.name}`);
            
            // Check dependencies
            const missingDeps = this.requires.filter(dep => !services[dep]);
            if (missingDeps.length > 0) {
                throw new Error(`Missing dependencies: ${missingDeps.join(', ')}`);
            }
            
            // Collect dependencies
            this.dependencies = {};
            this.requires.forEach(dep => {
                this.dependencies[dep] = services[dep];
            });
            
            // Create instance
            const PluginClass = typeof this.plugin === 'function' ? this.plugin : this.plugin.default;
            this.instance = new PluginClass();
            
            // Initialize with context
            const context = {
                app,
                services,
                config: this.config,
                dependencies: this.dependencies,
                emit: (event, data) => {
                    const events = services.events;
                    if (events && events.emit) events.emit(event, data);
                },
                log: this.log.bind(this)
            };
            
            if (typeof this.instance.init === 'function') {
                await this.instance.init(context);
            }
            
            this.initialized = true;
            this.log(`✅ Plugin ${this.name} ready`);
            
        } catch (error) {
            this.handleError(error, `plugin-${this.name}`);
        } finally {
            this.stopLoading();
        }
        
        return this.instance;
    }

    getInstance() {
        return this.instance;
    }

    isReady() {
        return this.initialized && this.instance !== null;
    }
}

export class PluginManager extends BaseManager {
    constructor(config = {}) {
        super({
            plugins: config.plugins || {},
            ...config
        });

        this.availablePlugins = {};
        this.appContext = null;
    }

    async init(app) {
        if (this.initialized) return this;

        this.startLoading();
        const startTime = Date.now();

        this.log('🔌 Initializing plugin manager...');

        try {
            // Set app context for plugins
            this.appContext = app;
            
            // Initialize all plugins based on configuration
            await this.initAllPlugins();

            this.initialized = true;
            this.metrics.loadTime = Date.now() - startTime;

            this.log(`✅ ${this.items.size} plugins initialized in ${this.metrics.loadTime}ms`);

            this.dispatch('initialized', {
                plugins: this.getNames(),
                metrics: this.getMetrics()
            });

        } catch (error) {
            this.handleError(error, 'init');
        } finally {
            this.stopLoading();
        }

        return this;
    }

    async initAllPlugins() {
        // Initialize each plugin based on configuration
        for (const [pluginName, pluginConfig] of Object.entries(this.config.plugins)) {
            if (pluginConfig.enabled !== false) {
                try {
                    await this.initPlugin(pluginName, pluginConfig);
                } catch (error) {
                    this.log(`⚠️ Plugin ${pluginName} initialization failed:`, error);
                }
            } else {
                this.log(`⏭️ Plugin ${pluginName} disabled, skipping`);
            }
        }
    }

    async initPlugin(pluginName, options = {}) {
        const pluginStartTime = Date.now();

        try {
            // Use the plugin system to load and initialize
            const PluginClass = await this.loadPlugin(pluginName, options);
            if (!PluginClass) {
                throw new Error(`Plugin ${pluginName} not found`);
            }

            // Create instance and initialize with app context
            const pluginInstance = new PluginClass(this, options);

            if (typeof pluginInstance.init === 'function') {
                await pluginInstance.init();
            }

            this.set(pluginName, pluginInstance, {
                type: 'plugin',
                class: PluginClass,
                loadTime: Date.now() - pluginStartTime
            });

            // Store in available plugins
            this.availablePlugins[pluginName] = PluginClass;

            this.log(`✅ Plugin initialized: ${pluginName}`);
            return pluginInstance;

        } catch (error) {
            this.handleError(error, `plugin-${pluginName}`);
            throw error;
        }
    }

    async loadPlugin(pluginName, _options = {}) {
        // This method should be implemented based on your plugin loading system
        // For now, we'll try to dynamically import from a known location
        // Note: _options reserved for future use (e.g., plugin configuration)
        try {
            const pluginModule = await import(`./${pluginName}.js`);
            return pluginModule.default || pluginModule[pluginName];
        } catch (error) {
            this.log(`Plugin ${pluginName} not found:`, error);
            return null;
        }
    }

    setAppContext(app) {
        this.appContext = app;
        return this;
    }

    getAppContext() {
        return this.appContext;
    }

    /**
     * Register a plugin
     */
    registerPlugin(name, plugin) {
        return this.set(name, plugin, { type: 'plugin' });
    }

    /**
     * Get a plugin
     */
    getPlugin(name) {
        return this.get(name);
    }

    /**
     * Check if plugin exists
     */
    hasPlugin(name) {
        return this.has(name);
    }

    /**
     * Get all plugins
     */
    getAllPlugins() {
        return this.getAll();
    }

    /**
     * Remove a plugin
     */
    async removePlugin(name) {
        return this.remove(name);
    }

    getAvailablePlugins() {
        return { ...this.availablePlugins };
    }
}

// Create singleton instance
export const pluginManager = new PluginManager();

// Helper functions
export async function initializePlugins(app, config = {}) {
    console.log('🔌 Initializing plugins...');
    
    pluginManager.updateConfig(config);
    await pluginManager.init(app);
    
    return pluginManager;
}

export function getPlugin(name) {
    return pluginManager.get(name);
}

export function registerPlugin(name, plugin) {
    return pluginManager.registerPlugin(name, plugin);
}

// Default export
export default pluginManager;

// UI Plugins
export * from './modal.js';
export * from './animations.js';
// Form Plugins
export * from './forms.js';

// ── UI Plugins (moved from modules/components) ──────────────────────────────
export { ModalController, ModalController as Modal } from './modal.js';
export { default as AnimationsPlugin } from './animations.js';

// ── Form Plugins ─────────────────────────────────────────────────────────────
export {
  FormsManager,
  UnifiedFormHandler,
  UnifiedFormHandler as FormHandler,
  AuthFormsHandler,
  ContactFormHandler,
} from './forms.js';
