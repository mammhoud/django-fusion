import { BaseManager } from '../lib/base-manager.js';

// ── Component registry ────────────────────────────────────────
export const UI_COMPONENTS = {
    definitions: new Map([

        // ── Highest priority: preloader ───────────────────────
        ['preloader', {
            name: 'Preloader',
            loader: () => import('./effects/preloader.js'),
            autoInit: true,
            priority: 5,
            dependencies: [],
            selectors: ['[data-preloader]'],
            detection: 'auto',
        }],

        // ── Animations (bg images, counters, progress, scroll) ─
        ['animations', {
            name: 'Animations',
            loader: () => import('./effects/animations.js'),
            className: 'Animations',
            autoInit: true,
            priority: 15,
            dependencies: [],
            selectors: ['body', '[data-animate]', '.counter', '.animated-progress'],
            detection: 'auto',
        }],

        // ── Media ─────────────────────────────────────────────
        ['sliders', {
            name: 'Sliders',
            loader: () => import('./media/sliders.js'),
            className: 'Sliders',
            autoInit: true,
            priority: 10,
            dependencies: [],
            selectors: ['[data-slider]', '.swiper'],
            detection: 'auto',
        }],
        ['lightbox', {
            name: 'Lightbox',
            loader: () => import('./media/lightbox.js'),
            autoInit: true,
            priority: 100,
            dependencies: [],
            selectors: ['.lightbox-image-link', '[data-video-url]', '.gallery-wrapper'],
            detection: 'auto',
        }],

        // ── vResume UI ──────────────────────────────────────────
        ['accordion', {
            name: 'Accordion',
            loader: () => import('./core/accordion.js'),
            className: 'Accordion',
            autoInit: true,
            priority: 40,
            dependencies: [],
            selectors: ['[data-accordion]', '.accordion', '.faq-accordion'],
            detection: 'auto',
        }],
        ['progress', {
            name: 'Progress',
            loader: () => import('./core/progress.js'),
            className: 'Progress',
            autoInit: true,
            priority: 70,
            dependencies: [],
            selectors: ['[data-progress]', '.progress-bar', '.animated-progress'],
            detection: 'auto',
        }],
        ['tabs', {
            name: 'Tabs',
            loader: () => import('./core/tabs.js'),
            className: 'Tabs',
            autoInit: true,
            priority: 90,
            dependencies: [],
            selectors: ['[data-tabs]', '.nav-tabs', '.tab-content'],
            detection: 'auto',
        }],
        ['sidebar', {
            name: 'Sidebar',
            loader: () => import('./core/sidebar.js'),
            className: 'SidebarComponent',
            autoInit: true,
            priority: 10,
            selectors: ['[data-sidebar]', '.sidebar'],
            detection: 'auto',
        }],
        ['contactForm', {
            name: 'ContactForm',
            loader: () => import('./forms/contact-form.js'),
            className: 'ContactFormComponent',
            autoInit: true,
            priority: 60,
            selectors: ['[data-contact-form]', '.contact-form'],
            detection: 'auto',
        }],
        ['unifiedModal', {
            name: 'UnifiedModal',
            loader: () => import('./modals/unified-modal.js'),
            className: 'UnifiedModal',
            autoInit: true,
            priority: 5,
            selectors: ['#unified-modal-overlay', '[data-modal-overlay]', '[data-modal-trigger]', '[data-htmx-modal]'],
            detection: 'auto',
        }],
        ['testimonials', {
            name: 'Testimonials',
            loader: () => import('./misc/testimonials.js'),
            className: 'TestimonialsComponent',
            autoInit: true,
            priority: 80,
            selectors: ['[data-testimonials]', '.testimonials-carousel'],
            detection: 'auto',
        }],
        ['skillsCounter', {
            name: 'Counter',
            loader: () => import('./misc/counter.js'),
            className: 'CounterComponent',
            autoInit: true,
            priority: 75,
            selectors: ['.count', '[data-skill-level]', '.counter'],
            detection: 'auto',
        }],
        ['images', {
            name: 'BackgroundImages',
            loader: () => import('./media/images.js'),
            className: 'BackgroundImages',
            autoInit: true,
            priority: 20,
            selectors: ['[data-bg-image]'],
            detection: 'auto',
        }],
        ['contentFilter', {
            name: 'ContentFilter',
            loader: () => import('./misc/content-filter.js'),
            className: 'ContentFilterComponent',
            autoInit: true,
            priority: 50,
            dependencies: [],
            selectors: ['[data-filter-btn]', '[data-filter-item]', '[data-select]'],
            detection: 'auto',
        }],
        ['tagFilter', {
            name: 'TagFilter',
            loader: () => import('./filters/tag-filter.js'),
            className: 'TagFilterComponent',
            autoInit: true,
            priority: 55,
            dependencies: [],
            selectors: ['[data-tag-filter]', '[data-tags]'],
            detection: 'auto',
        }],
    ]),

    cache:   new Map(),
    metrics: {
        loadTimes:      new Map(),
        initTimes:      new Map(),
        instanceCounts: new Map(),
    },
};

// ── UIComponentHandler ────────────────────────────────────────

class UIComponentHandler {
    constructor(manager) {
        this.manager   = manager;
        this.observers = new Map();
        this.instances = new Map();
        this.registry  = null;
        this.moduleLoader = null;
    }

    setRegistry(registry, moduleLoader) {
        this.registry     = registry;
        this.moduleLoader = moduleLoader;
        return this;
    }

    async initializeComponent(componentId, config, elements) {
        const t0 = Date.now();
        try {
            const ComponentClass = await this._loadClass(componentId, config);
            if (!ComponentClass) throw new Error(`Class not found: ${componentId}`);

            const instances = await this._createInstances(componentId, ComponentClass, elements, config);
            this._setupObservers(componentId, instances);

            UI_COMPONENTS.metrics.instanceCounts.set(componentId, instances.length);
            UI_COMPONENTS.metrics.initTimes.set(componentId, Date.now() - t0);
            return instances;
        } catch {
            return [];
        }
    }

    async _loadClass(componentId, config) {
        try {
            const mod = await config.loader();
            if (mod.default && typeof mod.default === 'function') return mod.default;
            if (config.className && mod[config.className]) return mod[config.className];
            return Object.values(mod).find(v => typeof v === 'function' && v.prototype) || null;
        } catch {
            return null;
        }
    }

    async _createInstances(componentId, Cls, elements, config) {
        const instances = [];
        await Promise.allSettled(elements.map(async (element) => {
            // Dedup guard: skip if this element already has a live instance for this component
            const marker = `data-${componentId}-init`;
            if (element.hasAttribute(marker)) return;
            element.setAttribute(marker, 'true');

            try {
                const instance = new Cls({ element, componentId, manager: this.manager, config });
                if (typeof instance.init === 'function')       await instance.init();
                else if (typeof instance.initialize === 'function') await instance.initialize();
                instances.push(instance);
                this.manager.dispatch('component:created', { componentId, instance, element });
            } catch { /* skip broken instance */ }
        }));
        return instances;
    }

    _setupObservers(componentId, instances) {
        instances.forEach(instance => {
            if (!instance.element) return;

            // ResizeObserver
            if (typeof ResizeObserver !== 'undefined') {
                const ro = new ResizeObserver(() => {
                    (instance.onResize || instance.handleResize)?.call(instance);
                });
                ro.observe(instance.element);
                this.observers.set(instance, ro);
            }

            // IntersectionObserver (lazy visible callback)
            if (typeof IntersectionObserver !== 'undefined' && typeof instance.onVisible === 'function') {
                const io = new IntersectionObserver((entries) => {
                    entries.forEach(e => { if (e.isIntersecting) { instance.onVisible(); io.unobserve(e.target); } });
                }, { threshold: 0.1 });
                io.observe(instance.element);
            }
        });
    }

    async destroyComponentInstances(componentId) {
        const instances = this.instances.get(componentId) || [];
        await Promise.allSettled(instances.map(async (inst) => {
            this.observers.get(inst)?.disconnect();
            this.observers.delete(inst);
            await inst.destroy?.();
        }));
        this.instances.delete(componentId);
        UI_COMPONENTS.metrics.instanceCounts.delete(componentId);
        return instances.length;
    }

    async refreshComponentInstances(componentId) {
        const instances = this.instances.get(componentId) || [];
        await Promise.allSettled(instances.map(inst => inst.refresh?.()));
        return instances.length;
    }

    getComponentInstances(componentId) { return this.instances.get(componentId) || []; }
    setComponentInstances(componentId, instances) { this.instances.set(componentId, instances); }
}

// ── UIManager ─────────────────────────────────────────────────

export class UIManager extends BaseManager {
    constructor(config = {}) {
        super({
            autoInit:             true,
            debug:                config.debug || false,
            autoDetectComponents: config.autoDetectComponents !== false,
            observerEnabled:      config.observerEnabled !== false,
            batchInitialize:      true,
            maxBatchSize:         5,
            ...config,
        });

        this.componentHandler = new UIComponentHandler(this);
        this.registry         = null;
        this.moduleLoader     = null;
        this.mutationObserver = null;
        this.domReady         = document.readyState !== 'loading';
        this.performance      = {
            initializationTime:   0,
            componentLoadTimes:   new Map(),
            totalInstances:       0,
        };
    }

    async init(app, registry = null) {
        if (this.initialized) return this;

        this.startLoading();
        const t0 = Date.now();
        this.log('🎨 Initializing UI Manager...');

        try {
            if (registry) {
                this.registry     = registry;
                this.moduleLoader = registry.moduleLoader;
                this.componentHandler.setRegistry(registry, registry.moduleLoader);
            }

            if (!this.domReady) await this._waitForDOM();

            if (this.config.autoDetectComponents) await this._initComponents();
            if (this.config.observerEnabled)      this._setupMutationObserver();

            this.initialized = true;
            this.performance.initializationTime = Date.now() - t0;
            this.log(`✅ UI Manager ready in ${this.performance.initializationTime}ms`);
            this.dispatch('initialized', this.getManagerState());

        } catch (error) {
            this.handleError(error, 'ui-manager-init');
        } finally {
            this.stopLoading();
        }

        return this;
    }

    _waitForDOM() {
        return new Promise(resolve => {
            document.addEventListener('DOMContentLoaded', () => { this.domReady = true; resolve(); });
        });
    }

    async _initComponents() {
        const toLoad = await this._detectComponents();
        if (!toLoad.length) return;

        this.log(`📋 ${toLoad.length} component(s) detected`);

        const batchSize = this.config.maxBatchSize;
        for (let i = 0; i < toLoad.length; i += batchSize) {
            await this._loadBatch(toLoad.slice(i, i + batchSize));
            if (i + batchSize < toLoad.length) await new Promise(r => setTimeout(r, 50));
        }
    }

    async _detectComponents() {
        const detected = [];
        for (const [id, config] of UI_COMPONENTS.definitions) {
            if (!await this._shouldLoad(id, config)) continue;
            const elements = await this._getElements(id, config);
            if (elements.length) detected.push({ id, config, elements, priority: config.priority || 1000 });
        }
        return detected.sort((a, b) => a.priority - b.priority);
    }

    async _shouldLoad(id, config) {
        if (this.config.components?.[id]?.enabled === false) return false;
        if (config.autoInit === false) return false;
        if (config.condition && !config.condition()) return false;
        return true;
    }

    async _getElements(id, config) {
        const found = new Set();
        for (const sel of (config.selectors || [])) {
            try { document.querySelectorAll(sel).forEach(el => found.add(el)); } catch { /* bad selector */ }
        }
        return [...found];
    }

    async _loadBatch(batch) {
        await Promise.allSettled(batch.map(async ({ id, config, elements }) => {
            try {
                const instances = await this.componentHandler.initializeComponent(id, config, elements);
                this.performance.componentLoadTimes.set(id, Date.now());
                this.performance.totalInstances += instances.length;
                this.dispatch('component:loaded', { componentId: id, instances });
                this.log(`✅ ${id} (${instances.length} instances)`);
            } catch (err) {
                this.log(`⚠️ ${id} failed: ${err.message}`);
            }
        }));
    }

    _setupMutationObserver() {
        if (typeof MutationObserver === 'undefined') return;
        this.mutationObserver = new MutationObserver((mutations) => {
            mutations.forEach(m => {
                if (m.type === 'childList') m.addedNodes.forEach(n => {
                    if (n.nodeType === Node.ELEMENT_NODE) this._checkNewNode(n);
                });
            });
        });
        this.mutationObserver.observe(document.body, { childList: true, subtree: true });
    }

    async _checkNewNode(element) {
        for (const [id, config] of UI_COMPONENTS.definitions) {
            if (config.autoInit === false) continue;
            const matches = (config.selectors || []).some(sel => {
                try { return element.matches(sel) || element.querySelector(sel); } catch { return false; }
            });
            if (matches) {
                const elements = await this._getElements(id, config);
                if (elements.length) await this._loadBatch([{ id, config, elements }]);
            }
        }
    }

    // ── Public API ────────────────────────────────────────────

    getComponent(id)     { return this.componentHandler.getComponentInstances(id); }
    getAllComponents()    {
        const out = {};
        for (const [id] of UI_COMPONENTS.definitions) {
            const inst = this.getComponent(id);
            if (inst?.length) out[id] = { id, instances: inst, instanceCount: inst.length };
        }
        return out;
    }

    async registerComponent(id, config, elements = []) {
        UI_COMPONENTS.definitions.set(id, {
            name: config.name || id,
            loader: config.loader,
            className: config.className || id,
            autoInit: config.autoInit !== false,
            priority: config.priority || 1000,
            dependencies: config.dependencies || [],
            selectors: config.selectors || [],
            detection: config.detection || 'auto',
            condition: config.condition,
        });
        if (elements.length) await this._loadBatch([{ id, config: UI_COMPONENTS.definitions.get(id), elements }]);
        return true;
    }

    async refreshComponent(id) {
        const n = await this.componentHandler.refreshComponentInstances(id);
        if (n) this.dispatch('component:refreshed', { componentId: id, instanceCount: n });
        return n > 0;
    }

    async refreshAll() {
        let total = 0;
        await Promise.allSettled(
            [...UI_COMPONENTS.definitions.keys()].map(async id => {
                const n = await this.componentHandler.refreshComponentInstances(id);
                total += n;
            })
        );
        if (total) this.dispatch('components:refreshed', { instanceCount: total });
        return total;
    }

    async destroyComponent(id) {
        const n = await this.componentHandler.destroyComponentInstances(id);
        if (n) this.dispatch('component:destroyed', { componentId: id, instanceCount: n });
        return n > 0;
    }

    showLoading(selector = '[data-loading]') {
        document.querySelectorAll(selector).forEach(el => { el.style.display = 'block'; el.style.opacity = '1'; });
    }
    hideLoading(selector = '[data-loading]') {
        document.querySelectorAll(selector).forEach(el => {
            el.style.opacity = '0';
            setTimeout(() => { el.style.display = 'none'; }, 300);
        });
    }
    showElement(selector, display = 'block') {
        const el = document.querySelector(selector);
        if (el) el.style.display = display;
        return el;
    }
    hideElement(selector) {
        const el = document.querySelector(selector);
        if (el) el.style.display = 'none';
        return el;
    }
    toggleElement(selector, display = 'block') {
        const el = document.querySelector(selector);
        if (el) el.style.display = (el.style.display === 'none' || !el.style.display) ? display : 'none';
        return el;
    }
    getPageType() { return document.body.dataset.page || 'unknown'; }

    getManagerState() {
        return {
            initialized:  this.initialized,
            domReady:     this.domReady,
            components:   Object.keys(this.getAllComponents()),
            performance:  {
                initializationTime: this.performance.initializationTime,
                totalInstances:     this.performance.totalInstances,
            },
        };
    }

    async destroy() {
        this.mutationObserver?.disconnect();
        await Promise.allSettled(
            [...UI_COMPONENTS.definitions.keys()].map(id => this.destroyComponent(id).catch(() => {}))
        );
        UI_COMPONENTS.cache.clear();
        UI_COMPONENTS.metrics.loadTimes.clear();
        UI_COMPONENTS.metrics.initTimes.clear();
        UI_COMPONENTS.metrics.instanceCounts.clear();
        await super.destroy();
    }
}

// ── Singleton ─────────────────────────────────────────────────

export const uiManager = new UIManager();

if (typeof window !== 'undefined') {
    const initUI = () => {
        if (window.autoInitializeUI !== false) uiManager.init().catch(console.error);
    };
    document.readyState === 'loading'
        ? document.addEventListener('DOMContentLoaded', initUI)
        : setTimeout(initUI, 0);

    window.UIManager    = UIManager;
    window.uiManager    = uiManager;
    window.UI_COMPONENTS = UI_COMPONENTS;
}

export default uiManager;
