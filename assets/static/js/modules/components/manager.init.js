/**
 * @file modules/components/manager.js
 * Enhanced UI Manager - Integrated with Unified Registry System
 */

import { BaseManager } from '../../utility/base.manager.js';

// Unified UI Components Registry
export const UI_COMPONENTS = {
    definitions: new Map([
        ['sliders', {
            name: 'Sliders',
            loader: () => import('./media/sliders.init.js'),
            className: 'Sliders',
            autoInit: true,
            priority: 10,
            dependencies: [],
            selectors: ['[data-slider]', '.swiper', '.carousel', '.owl-carousel', '.slider'],
            detection: 'auto'
        }],
        ['masonry', {
            name: 'Masonry',
            loader: () => import('./media/masonry.init.js'),
            className: 'MasonryManager',
            autoInit: true,
            priority: 20,
            dependencies: [],
            selectors: ['[data-masonry]', '.masonry-grid', '.grid'],
            detection: 'auto'
        }],
        ['preloader', {
            name: 'Preloader',
            loader: () => import('./partials/preloader.init.js'),
            autoInit: true,
            priority: 5,
            dependencies: [],
            selectors: ['[data-preloader]'],
            detection: 'auto'
        }],
        ['portfolio', {
            name: 'Portfolio',
            loader: () => import('./features/portfolio.init.js'),
            className: 'Portfolio',
            autoInit: true,
            priority: 30,
            dependencies: ['masonry'],
            selectors: ['[data-portfolio]', '.portfolio-grid', '.projects'],
            detection: 'auto'
        }],
        ['accordion', {
            name: 'Accordion',
            loader: () => import('./accordion.init.js'),
            className: 'Accordion',
            autoInit: true,
            priority: 40,
            dependencies: [],
            selectors: ['[data-accordion]', '.accordion', '.collapse'],
            detection: 'auto'
        }],
        ['countdown', {
            name: 'Countdown',
            loader: () => import('./widgets/countdown.init.js'),
            className: 'Countdown',
            autoInit: false,
            priority: 50,
            dependencies: [],
            selectors: ['[data-countdown]', '.countdown', '.timer'],
            detection: 'manual'
        }],
        ['counter', {
            name: 'Counter',
            loader: () => import('./widgets/counter.init.js'),
            className: 'Counter',
            autoInit: true,
            priority: 60,
            dependencies: [],
            selectors: ['[data-counter]', '.counter', '[data-number]'],
            detection: 'auto'
        }],
        ['progress', {
            name: 'Progress',
            loader: () => import('./progress.init.js'),
            className: 'Progress',
            autoInit: true,
            priority: 70,
            dependencies: [],
            selectors: ['[data-progress]', '.progress-bar', '.progress'],
            detection: 'auto'
        }],
        ['maps', {
            name: 'Maps',
            loader: () => import('./partials/maps.init.js'),
            className: 'Maps',
            autoInit: false,
            priority: 80,
            dependencies: [],
            selectors: ['[data-map]', '.map-container', '[data-gmap]'],
            detection: 'conditional',
            condition: () => window.google && window.google.maps
        }],
        ['tabs', {
            name: 'Tabs',
            loader: () => import('./tabs.init.js'),
            className: 'Tabs',
            autoInit: true,
            priority: 90,
            dependencies: [],
            selectors: ['[data-tabs]', '.nav-tabs', '.tab-content'],
            detection: 'auto'
        }],
        ['modal', {
            name: 'Modal',
            loader: () => import('./modal.init.js'),
            className: 'Modal',
            autoInit: true,
            priority: 100,
            dependencies: [],
            selectors: ['[data-modal]', '.modal', '[data-toggle="modal"]'],
            detection: 'auto'
        }],
        ['animations', {
            name: 'Animations',
            loader: () => import('./partials/animations.init.js'),
            className: 'Animations',
            autoInit: true,
            priority: 15,
            dependencies: [],
            selectors: ['[data-animate]', '.counter', '.accordion', '.animated-progress'],
            detection: 'auto'
        }],
        ['cursor', {
            name: 'Cursor',
            loader: () => import('./partials/cursor.init.js'),
            className: 'Cursor',
            autoInit: true,
            priority: 12,
            dependencies: [],
            selectors: ['#cursor', '[data-cursor]'],
            detection: 'auto'
        }],
        ['fullscreen', {
            name: 'Fullscreen',
            loader: () => import('./partials/fullscreen.init.js'),
            className: 'Fullscreen',
            autoInit: true,
            priority: 25,
            dependencies: [],
            selectors: ['.fullscreen-menu', '[data-fullscreen]'],
            detection: 'auto'
        }],
        ['parallax', {
            name: 'Parallax',
            loader: () => import('./partials/parallax.init.js'),
            className: 'Parallax',
            autoInit: true,
            priority: 35,
            dependencies: [],
            selectors: ['.parallax', '.parallax-section'],
            detection: 'conditional',
            condition: () => window.innerWidth > 1200
        }],
        ['backgroundImages', {
            name: 'BackgroundImages',
            loader: () => import('../../plugins/backgroundImages.js'),
            className: 'BackgroundImages',
            autoInit: true,
            priority: 8,
            dependencies: [],
            selectors: ['.bg-image[data-bg-src]', '[data-bg-src]'],
            detection: 'auto'
        }]
    ]),
    cache: new Map(),
    metrics: {
        loadTimes: new Map(),
        initTimes: new Map(),
        instanceCounts: new Map()
    }
};

/**
 * UI Component Handler
 */
class UIComponentHandler {
    constructor(manager) {
        this.manager = manager;
        this.observers = new Map();
        this.instances = new Map();
        this.registry = null;
        this.moduleLoader = null;
    }

    /**
     * Set registry reference
     */
    setRegistry(registry, moduleLoader) {
        this.registry = registry;
        this.moduleLoader = moduleLoader;
        return this;
    }

    /**
     * Initialize a component
     */
    async initializeComponent(componentId, config, elements) {
        const startTime = Date.now();

        try {
            // Try to load from module loader if available
            let ComponentClass;

            if (this.moduleLoader && this.moduleLoader.hasModule(componentId)) {
                ComponentClass = await this.moduleLoader.loadSingleModule(componentId, {
                    manager: this.manager,
                    pageInfo: this.registry?.pageInfo
                });
            } else {
                // Fallback to direct loading
                ComponentClass = await this.loadComponentClass(componentId, config);
            }

            if (!ComponentClass) {
                throw new Error(`Component class not found for: ${componentId}`);
            }

            // Create instances
            const instances = await this.createComponentInstances(
                componentId,
                ComponentClass,
                elements,
                config
            );

            // Setup observers
            this.setupObservers(componentId, instances);

            // Update metrics
            UI_COMPONENTS.metrics.instanceCounts.set(componentId, instances.length);
            UI_COMPONENTS.metrics.initTimes.set(componentId, Date.now() - startTime);

            return instances;

        } catch (error) {
            // console.error(`Failed to initialize component ${componentId}:`, error);
            return [];
        }
    }

    /**
     * Load component class
     */
    async loadComponentClass(componentId, config) {
        try {
            const module = await config.loader();

            // Try different ways to extract the component class
            if (module.default && typeof module.default === 'function') {
                return module.default;
            }

            if (config.className && module[config.className]) {
                return module[config.className];
            }

            // Look for any function that might be the component
            for (const key in module) {
                const value = module[key];
                if (typeof value === 'function' &&
                    (key.includes('Component') || key.includes('Manager') || key.includes('Init'))) {
                    return value;
                }
            }

            return null;

        } catch (error) {
            console.error(`Failed to load component ${componentId}:`, error);
            return null;
        }
    }

    /**
     * Create component instances
     */
    async createComponentInstances(componentId, ComponentClass, elements, config) {
        const instances = [];
        const initPromises = [];

        for (const element of elements) {
            const promise = (async () => {
                try {
                    const context = {
                        element,
                        componentId,
                        manager: this.manager,
                        registry: this.registry,
                        config: config
                    };

                    // Create instance
                    const instance = new ComponentClass(context);

                    // Initialize if method exists
                    if (typeof instance.init === 'function') {
                        await instance.init();
                    } else if (typeof instance.initialize === 'function') {
                        await instance.initialize();
                    }

                    instances.push(instance);

                    this.manager.dispatch('component:created', {
                        componentId,
                        instance,
                        element,
                        timestamp: Date.now()
                    });

                    return instance;
                } catch (error) {
                    console.error(`Failed to create ${componentId} instance:`, error);
                    return null;
                }
            })();

            initPromises.push(promise);
        }

        await Promise.allSettled(initPromises);
        return instances.filter(instance => instance !== null);
    }

    /**
     * Setup observers for instances
     */
    setupObservers(componentId, instances) {
        for (const instance of instances) {
            this.setupResizeObserver(instance);
            this.setupIntersectionObserver(instance);
        }
    }

    /**
     * Setup resize observer
     */
    setupResizeObserver(instance) {
        if (typeof ResizeObserver === 'undefined' || !instance.element) return;

        const resizeHandler = () => {
            if (typeof instance.onResize === 'function') {
                instance.onResize();
            } else if (typeof instance.handleResize === 'function') {
                instance.handleResize();
            }
        };

        const observer = new ResizeObserver(resizeHandler);
        observer.observe(instance.element);
        this.observers.set(instance, observer);
    }

    /**
     * Setup intersection observer
     */
    setupIntersectionObserver(instance) {
        if (typeof IntersectionObserver === 'undefined' || !instance.element) return;

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    if (typeof instance.onVisible === 'function') {
                        instance.onVisible();
                    }
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });

        observer.observe(instance.element);
    }

    /**
     * Destroy component instances
     */
    async destroyComponentInstances(componentId) {
        const instances = this.getComponentInstances(componentId);

        if (!instances || instances.length === 0) return 0;

        const destroyPromises = instances.map(instance => {
            // Cleanup observers
            const observer = this.observers.get(instance);
            if (observer) {
                observer.disconnect();
                this.observers.delete(instance);
            }

            // Call destroy method if exists
            if (typeof instance.destroy === 'function') {
                return instance.destroy().catch(error => {
                    console.error(`Error destroying instance:`, error);
                });
            }

            return Promise.resolve();
        });

        await Promise.allSettled(destroyPromises);
        this.instances.delete(componentId);
        UI_COMPONENTS.metrics.instanceCounts.delete(componentId);

        return destroyPromises.length;
    }

    /**
     * Get component instances
     */
    getComponentInstances(componentId) {
        return this.instances.get(componentId) || [];
    }

    /**
     * Set component instances
     */
    setComponentInstances(componentId, instances) {
        this.instances.set(componentId, instances);
        return this;
    }

    /**
     * Refresh component instances
     */
    async refreshComponentInstances(componentId) {
        const instances = this.getComponentInstances(componentId);

        if (!instances) return 0;

        const refreshPromises = instances.map(instance => {
            if (typeof instance.refresh === 'function') {
                return instance.refresh();
            }
            return Promise.resolve();
        });

        await Promise.allSettled(refreshPromises);
        return refreshPromises.length;
    }
}

/**
 * Enhanced UI Manager - Integrated with Unified Registry
 */
export class UIManager extends BaseManager {
    constructor(config = {}) {
        super({
            autoInit: true,
            debug: config.debug || false,
            performanceTracking: config.performanceTracking || false,
            autoDetectComponents: config.autoDetectComponents !== false,
            lazyLoadComponents: config.lazyLoadComponents || false,
            observerEnabled: config.observerEnabled !== false,
            batchInitialize: config.batchInitialize || true,
            maxBatchSize: config.maxBatchSize || 5,
            ...config
        });

        // Component handler
        this.componentHandler = new UIComponentHandler(this);

        // Registry references
        this.registry = null;
        this.moduleLoader = null;

        // DOM state
        this.domReady = document.readyState === 'complete' ||
            document.readyState === 'interactive';

        // Observer for dynamic content
        this.mutationObserver = null;

        // Performance metrics
        this.performance = {
            initializationTime: 0,
            componentLoadTimes: new Map(),
            totalInstances: 0
        };
    }

    /**
     * Initialize with registry integration
     */
    async init(app, registry = null) {
        if (this.initialized) {
            this.log('UI Manager already initialized');
            return this;
        }

        this.startLoading();
        const startTime = Date.now();

        this.log('🎨 Initializing Enhanced UI Manager...');

        try {
            // Set registry reference
            if (registry) {
                this.registry = registry;
                this.moduleLoader = registry.moduleLoader;
                this.componentHandler.setRegistry(registry, registry.moduleLoader);
            }

            // Wait for DOM if needed
            if (!this.domReady) {
                await this.waitForDOM();
            }

            // Register components with module loader
            if (this.moduleLoader) {
                await this.registerComponentsWithLoader();
            }

            // Initialize components
            if (this.config.autoDetectComponents) {
                await this.initComponents();
            }

            // Setup mutation observer for dynamic content
            if (this.config.observerEnabled) {
                this.setupMutationObserver();
            }

            this.initialized = true;
            this.performance.initializationTime = Date.now() - startTime;

            this.log(`✅ UI Manager initialized in ${this.performance.initializationTime}ms`);
            this.logStatistics();

            this.dispatch('initialized', this.getManagerState());

        } catch (error) {
            this.handleError(error, 'ui-manager-init');
        } finally {
            this.stopLoading();
        }

        return this;
    }

    /**
     * Wait for DOM to be ready
     */
    waitForDOM() {
        return new Promise((resolve) => {
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => {
                    this.domReady = true;
                    resolve();
                });
            } else {
                this.domReady = true;
                resolve();
            }
        });
    }

    /**
     * Register components with module loader
     */
    async registerComponentsWithLoader() {
        if (!this.moduleLoader) return;

        this.log('📝 Registering components with module loader...');

        for (const [componentId, config] of UI_COMPONENTS.definitions) {
            if (config.enabled !== false) {
                // Convert loader to async function for module loader
                const loader = async () => {
                    try {
                        const module = await config.loader();
                        const ComponentClass = this.componentHandler.loadComponentClass(componentId, config);
                        return { default: ComponentClass };
                    } catch (error) {
                        throw new Error(`Failed to load component ${componentId}: ${error.message}`);
                    }
                };

                // Register with module loader
                this.moduleLoader.registerModule(componentId, {
                    loader,
                    name: config.name,
                    priority: config.priority,
                    alwaysLoad: false,
                    dependencies: config.dependencies,
                    condition: config.condition,
                    onLoad: async (instance, context) => {
                        // Initialize component after module load
                        await this.initializeLoadedComponent(componentId, instance, context);
                    }
                });

                this.log(`   → ${componentId} registered`);
            }
        }
    }

    /**
     * Initialize a loaded component
     */
    async initializeLoadedComponent(componentId, ComponentClass, context) {
        try {
            // Get elements for this component
            const elements = await this.getComponentElements(componentId);

            if (elements.length > 0) {
                const instances = await this.componentHandler.initializeComponent(
                    componentId,
                    UI_COMPONENTS.definitions.get(componentId),
                    elements
                );

                if (instances.length > 0) {
                    this.log(`🎯 Initialized ${componentId} from module loader`);
                    this.dispatch('component:loaded', {
                        componentId,
                        instances,
                        source: 'module-loader'
                    });
                }
            }
        } catch (error) {
            this.handleError(error, `load-component-${componentId}`);
        }
    }

    /**
     * Initialize all components
     */
    async initComponents() {
        this.log('🔧 Initializing UI components...');

        // Detect components that should be loaded
        const componentsToLoad = await this.detectComponents();

        if (componentsToLoad.length === 0) {
            this.log('ℹ️ No UI components detected');
            return;
        }

        this.log(`📋 Found ${componentsToLoad.length} component(s) to load`);

        // Load components based on configuration
        if (this.config.batchInitialize) {
            await this.loadComponentsInBatches(componentsToLoad);
        } else {
            await this.loadComponentsSequentially(componentsToLoad);
        }
    }

    /**
     * Detect components to load
     */
    async detectComponents() {
        const detected = [];

        for (const [componentId, config] of UI_COMPONENTS.definitions) {
            // Check if component should be loaded
            const shouldLoad = await this.shouldLoadComponent(componentId, config);

            if (shouldLoad) {
                // Get elements for this component
                const elements = await this.getComponentElements(componentId, config);

                if (elements.length > 0) {
                    detected.push({
                        id: componentId,
                        config,
                        elements,
                        priority: config.priority || 1000
                    });
                }
            }
        }

        // Sort by priority
        detected.sort((a, b) => a.priority - b.priority);
        return detected;
    }

    /**
     * Check if component should be loaded
     */
    async shouldLoadComponent(componentId, config) {
        // Check if disabled in config
        if (this.config.components?.[componentId]?.enabled === false) {
            return false;
        }

        // Check auto-init setting
        if (config.autoInit === false) {
            return false;
        }

        // Check custom condition
        if (config.condition && typeof config.condition === 'function') {
            if (!config.condition()) {
                return false;
            }
        }

        // Check for required dependencies
        if (config.dependencies && config.dependencies.length > 0) {
            const missingDeps = config.dependencies.filter(dep =>
                !this.componentHandler.getComponentInstances(dep)?.length
            );

            if (missingDeps.length > 0) {
                this.log(`⏭️ ${componentId} waiting for dependencies: ${missingDeps.join(', ')}`);
                return false;
            }
        }

        return true;
    }

    /**
     * Get DOM elements for component
     */
    async getComponentElements(componentId, config = null) {
        const componentConfig = config || UI_COMPONENTS.definitions.get(componentId);
        const elements = [];

        if (componentConfig?.selectors) {
            for (const selector of componentConfig.selectors) {
                try {
                    const found = document.querySelectorAll(selector);
                    if (found.length > 0) {
                        elements.push(...found);
                    }
                } catch (error) {
                    console.error(`Invalid selector for ${componentId}: ${selector}`, error);
                }
            }
        }

        // Remove duplicates
        const uniqueElements = [...new Set(elements)];
        return Array.from(uniqueElements);
    }

    /**
     * Load components in batches
     */
    async loadComponentsInBatches(components) {
        const batchSize = this.config.maxBatchSize;

        for (let i = 0; i < components.length; i += batchSize) {
            const batch = components.slice(i, i + batchSize);
            await this.loadComponentBatch(batch);

            // Small delay between batches to avoid blocking
            if (i + batchSize < components.length) {
                await new Promise(resolve => setTimeout(resolve, 50));
            }
        }
    }

    /**
     * Load a batch of components
     */
    async loadComponentBatch(batch) {
        const loadPromises = batch.map(async (component) => {
            try {
                const instances = await this.loadComponent(
                    component.id,
                    component.config,
                    component.elements
                );

                return { component: component.id, success: true, instances };
            } catch (error) {
                return { component: component.id, success: false, error: error.message };
            }
        });

        const results = await Promise.allSettled(loadPromises);

        // Process results
        results.forEach((result, index) => {
            if (result.status === 'fulfilled') {
                const { component, success, instances, error } = result.value;

                if (success) {
                    this.log(`✅ Loaded ${component} (${instances?.length || 0} instances)`);
                } else {
                    this.log(`⚠️ Failed to load ${component}: ${error}`);
                }
            }
        });
    }

    /**
     * Load components sequentially
     */
    async loadComponentsSequentially(components) {
        const loaded = new Set();

        while (components.length > 0) {
            const component = components.shift();

            // Check dependencies
            const depsLoaded = this.checkDependencies(component.config.dependencies, loaded);

            if (depsLoaded) {
                try {
                    await this.loadComponent(
                        component.id,
                        component.config,
                        component.elements
                    );
                    loaded.add(component.id);
                } catch (error) {
                    this.log(`⚠️ Failed to load ${component.id}:`, error.message);
                }
            } else {
                // Move to end of queue
                components.push(component);
            }
        }
    }

    /**
     * Check component dependencies
     */
    checkDependencies(dependencies, loaded) {
        if (!dependencies || dependencies.length === 0) return true;
        return dependencies.every(dep => loaded.has(dep));
    }

    /**
     * Load a single component
     */
    async loadComponent(componentId, config, elements) {
        const startTime = Date.now();

        try {
            this.log(`📥 Loading component: ${componentId}...`);

            // Use module loader if available
            let instances;
            if (this.moduleLoader && this.moduleLoader.hasModule(componentId)) {
                const ComponentClass = await this.moduleLoader.getModule(componentId, {
                    manager: this,
                    registry: this.registry
                });

                instances = await this.componentHandler.initializeComponent(
                    componentId,
                    config,
                    elements
                );
            } else {
                // Direct loading
                instances = await this.componentHandler.initializeComponent(
                    componentId,
                    config,
                    elements
                );
            }

            // Store performance metric
            this.performance.componentLoadTimes.set(componentId, Date.now() - startTime);
            this.performance.totalInstances += instances.length;

            // Dispatch event
            this.dispatch('component:loaded', {
                componentId,
                instances,
                loadTime: this.performance.componentLoadTimes.get(componentId)
            });

            return instances;

        } catch (error) {
            this.performance.componentLoadTimes.set(componentId, -1); // Mark as failed
            throw error;
        }
    }

    /**
     * Setup mutation observer for dynamic content
     */
    setupMutationObserver() {
        if (typeof MutationObserver === 'undefined') return;

        this.mutationObserver = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    this.handleNewNodes(mutation.addedNodes);
                }
            });
        });

        this.mutationObserver.observe(document.body, {
            childList: true,
            subtree: true
        });

        this.log('👀 Mutation observer enabled');
    }

    /**
     * Handle new DOM nodes
     */
    async handleNewNodes(nodes) {
        for (const node of nodes) {
            if (node.nodeType === Node.ELEMENT_NODE) {
                await this.checkForNewComponents(node);
            }
        }
    }

    /**
     * Check for new components in element
     */
    async checkForNewComponents(element) {
        for (const [componentId, config] of UI_COMPONENTS.definitions) {
            if (config.autoInit === false) continue;

            // Check if element matches component selectors
            const matches = this.elementMatchesSelectors(element, config.selectors);
            if (matches) {
                await this.loadComponent(componentId, config, [element]);
            }

            // Check child elements
            if (config.selectors) {
                for (const selector of config.selectors) {
                    const childElements = element.querySelectorAll(selector);
                    if (childElements.length > 0) {
                        await this.loadComponent(componentId, config, Array.from(childElements));
                    }
                }
            }
        }
    }

    /**
     * Check if element matches any selector
     */
    elementMatchesSelectors(element, selectors) {
        if (!selectors || !element.matches) return false;

        return selectors.some(selector => {
            try {
                return element.matches(selector);
            } catch (error) {
                return false;
            }
        });
    }

    /**
     * COMPONENT MANAGEMENT
     */

    /**
     * Get component instances
     */
    getComponent(componentId) {
        return this.componentHandler.getComponentInstances(componentId);
    }

    /**
     * Get component info
     */
    getComponentInfo(componentId) {
        const config = UI_COMPONENTS.definitions.get(componentId);
        const instances = this.getComponent(componentId);

        return {
            id: componentId,
            config,
            instances,
            instanceCount: instances?.length || 0
        };
    }

    /**
     * Get all components
     */
    getAllComponents() {
        const result = {};

        for (const [componentId] of UI_COMPONENTS.definitions) {
            const info = this.getComponentInfo(componentId);
            if (info.instances?.length > 0) {
                result[componentId] = info;
            }
        }

        return result;
    }

    /**
     * Register a new component
     */
    async registerComponent(componentId, config, elements = []) {
        try {
            // Add to registry
            UI_COMPONENTS.definitions.set(componentId, {
                name: config.name || componentId,
                loader: config.loader,
                className: config.className || componentId,
                autoInit: config.autoInit !== false,
                priority: config.priority || 1000,
                dependencies: config.dependencies || [],
                selectors: config.selectors || [],
                detection: config.detection || 'auto',
                condition: config.condition
            });

            // Register with module loader if available
            if (this.moduleLoader) {
                await this.moduleLoader.registerModule(componentId, {
                    loader: config.loader,
                    name: config.name || componentId,
                    priority: config.priority || 1000,
                    dependencies: config.dependencies || []
                });
            }

            // Load if elements provided
            if (elements.length > 0) {
                await this.loadComponent(componentId, UI_COMPONENTS.definitions.get(componentId), elements);
            }

            this.log(`✅ Component registered: ${componentId}`);

            return true;

        } catch (error) {
            this.handleError(error, `register-component-${componentId}`);
            return false;
        }
    }

    /**
     * Refresh a component
     */
    async refreshComponent(componentId) {
        const refreshed = await this.componentHandler.refreshComponentInstances(componentId);

        if (refreshed > 0) {
            this.log(`♻️ Refreshed ${componentId} (${refreshed} instances)`);
            this.dispatch('component:refreshed', { componentId, instanceCount: refreshed });
            return true;
        }

        return false;
    }

    /**
     * Refresh all components
     */
    async refreshAll() {
        let totalRefreshed = 0;
        const refreshPromises = [];

        for (const [componentId] of UI_COMPONENTS.definitions) {
            const instances = this.getComponent(componentId);
            if (instances?.length > 0) {
                instances.forEach(instance => {
                    if (typeof instance.refresh === 'function') {
                        refreshPromises.push(
                            instance.refresh().then(() => {
                                totalRefreshed++;
                            }).catch(console.error)
                        );
                    }
                });
            }
        }

        await Promise.allSettled(refreshPromises);

        if (totalRefreshed > 0) {
            this.log(`♻️ Refreshed ${totalRefreshed} component instance(s)`);
            this.dispatch('components:refreshed', { instanceCount: totalRefreshed });
        }

        return totalRefreshed;
    }

    /**
     * Destroy a component
     */
    async destroyComponent(componentId) {
        try {
            const destroyed = await this.componentHandler.destroyComponentInstances(componentId);

            if (destroyed > 0) {
                this.log(`🗑️ Destroyed ${componentId} (${destroyed} instances)`);
                this.dispatch('component:destroyed', { componentId, instanceCount: destroyed });
                return true;
            }

            return false;

        } catch (error) {
            this.handleError(error, `destroy-component-${componentId}`);
            return false;
        }
    }

    /**
     * UTILITY METHODS
     */

    /**
     * Show loading indicator
     */
    showLoading(selector = '#loading, .loading, [data-loading]') {
        const elements = document.querySelectorAll(selector);
        elements.forEach(el => {
            el.style.display = 'block';
            el.style.opacity = '1';
        });

        this.dispatch('loading:show');
    }

    /**
     * Hide loading indicator
     */
    hideLoading(selector = '#loading, .loading, [data-loading]') {
        const elements = document.querySelectorAll(selector);
        elements.forEach(el => {
            el.style.opacity = '0';
            setTimeout(() => {
                el.style.display = 'none';
            }, 300);
        });

        this.dispatch('loading:hide');
    }

    /**
     * Show element
     */
    showElement(selector, display = 'block') {
        const element = document.querySelector(selector);
        if (element) {
            element.style.display = display;
            this.dispatch('element:show', { selector, display });
        }
        return element;
    }

    /**
     * Hide element
     */
    hideElement(selector) {
        const element = document.querySelector(selector);
        if (element) {
            element.style.display = 'none';
            this.dispatch('element:hide', { selector });
        }
        return element;
    }

    /**
     * Toggle element visibility
     */
    toggleElement(selector, display = 'block') {
        const element = document.querySelector(selector);
        if (element) {
            if (element.style.display === 'none' || !element.style.display) {
                element.style.display = display;
                this.dispatch('element:show', { selector, display });
            } else {
                element.style.display = 'none';
                this.dispatch('element:hide', { selector });
            }
        }
        return element;
    }

    /**
     * Get manager state
     */
    getManagerState() {
        return {
            initialized: this.initialized,
            domReady: this.domReady,
            registryConnected: !!this.registry,
            moduleLoaderConnected: !!this.moduleLoader,
            performance: {
                initializationTime: this.performance.initializationTime,
                totalInstances: this.performance.totalInstances,
                componentLoadTimes: Object.fromEntries(this.performance.componentLoadTimes)
            },
            components: Object.keys(this.getAllComponents()),
            config: this.config
        };
    }

    /**
     * Log statistics
     */
    logStatistics() {
        if (!this.config.debug) return;

        const state = this.getManagerState();
        const components = this.getAllComponents();
        const totalInstances = Object.values(components).reduce(
            (sum, comp) => sum + (comp.instanceCount || 0), 0
        );

        this.log('📊 UI Manager Statistics:');
        this.log(`  Components: ${Object.keys(components).length} active`);
        this.log(`  Instances: ${totalInstances} total`);
        this.log(`  DOM Ready: ${state.domReady ? '✅' : '⏳'}`);
        this.log(`  Registry: ${state.registryConnected ? '✅' : '❌'}`);
        this.log(`  Module Loader: ${state.moduleLoaderConnected ? '✅' : '❌'}`);
        this.log(`  Load Time: ${state.performance.initializationTime}ms`);

        if (this.config.debug > 1) {
            console.table(
                Object.entries(components).map(([id, comp]) => ({
                    Component: id,
                    Instances: comp.instanceCount || 0,
                    'Load Time': state.performance.componentLoadTimes[id] || 'N/A'
                }))
            );
        }
    }

    /**
     * Clean up
     */
    async destroy() {
        this.log('🧹 Cleaning up UI Manager...');

        // Disconnect mutation observer
        if (this.mutationObserver) {
            this.mutationObserver.disconnect();
        }

        // Destroy all components
        const destroyPromises = [];

        for (const [componentId] of UI_COMPONENTS.definitions) {
            destroyPromises.push(
                this.destroyComponent(componentId).catch(error => {
                    this.log(`Error destroying ${componentId}:`, error);
                })
            );
        }

        await Promise.allSettled(destroyPromises);

        // Clear collections
        UI_COMPONENTS.cache.clear();

        // Clear metrics
        UI_COMPONENTS.metrics.loadTimes.clear();
        UI_COMPONENTS.metrics.initTimes.clear();
        UI_COMPONENTS.metrics.instanceCounts.clear();

        // Call parent destroy
        await super.destroy();

        this.log('✅ UI Manager cleaned up');
    }
}

// Create singleton instance
export const uiManager = new UIManager();

// Auto-initialize on DOM ready (can be disabled by window.autoInitializeUI)
if (typeof window !== 'undefined') {
    const initUI = () => {
        if (window.autoInitializeUI !== false) {
            uiManager.init().catch(console.error);
        }
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initUI);
    } else {
        setTimeout(initUI, 0);
    }
}

// Export for global access
if (typeof window !== 'undefined') {
    window.UIManager = UIManager;
    window.uiManager = uiManager;
    window.UI_COMPONENTS = UI_COMPONENTS;
}

export default uiManager;
