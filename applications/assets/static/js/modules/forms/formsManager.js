/**
 * 🚀 Enhanced Unified Forms Manager
 * Comprehensive form management with URL tracking, analytics, 
 * automatic reinitialization, and lifecycle management
 */
import { ValidationUtils } from './validationUtils.js';
// import { SSEHandler } from '../plugins/hx-sse-notify.js';
import { UnifiedFormHandler } from './formHandler.js';
import { AuthFormsHandler } from './authHandler.js';
import { ContactFormHandler } from './contactHandler.js';

export class FormsManager {
   constructor(options = {}) {
        this.options = {
            debug: false,
            autoInitialize: true,
            trackAnalytics: false,
            handleURLChanges: true,
            supportSPA: false,
            enableSSE: true,
            formHandlers: {
                'default': UnifiedFormHandler,
                'auth': AuthFormsHandler,
                'contact': ContactFormHandler
            },
            sseEndpoint: null,
            ...options
        };

        // Core state
        this.initialized = false;
        this.formInstances = new Map();
        this.handlerRegistry = new Map();
        this.urlTrackers = new Map();
        this.mutationObservers = new Map();
        this.eventListeners = new Map();
        this.reinitQueue = new Set();

        // Page tracking
        this.pageId = null;
        this.pageType = null;
        this.currentUrl = null;
        this.previousUrl = null;
        this.navigationHistory = [];
        this.spaFramework = null;

        // Analytics
        this.analytics = {
            submissions: new Map(),
            validations: new Map(),
            errors: new Map(),
            urlChanges: 0,
            dynamicInjects: 0,
            reinitializations: 0
        };

        // Form registry - ADD 'uninitialized' HERE
        this.formRegistry = {
            byId: new Map(),
            byType: new Map(),
            byPage: new Map(),
            byState: {
                uninitialized: new Set(), // ADD THIS LINE
                active: new Set(),
                inactive: new Set(),
                hidden: new Set(),
                destroyed: new Set()
            }
        };

        // Performance tracking
        this.performance = {
            initTime: null,
            lastReinit: null,
            avgInitTime: 0,
            handlerStats: new Map()
        };

        // History methods for SPA tracking
        this.originalHistoryMethods = {
            pushState: window.history.pushState,
            replaceState: window.history.replaceState
        };

        // Logging
        this.logger = {
            debug: this.options.debug ? console.debug.bind(console, '[FormsManager]') : () => { },
            info: console.info.bind(console, '[FormsManager] 📝'),
            warn: console.warn.bind(console, '[FormsManager] ⚠️'),
            error: console.error.bind(console, '[FormsManager] ❌')
        };
    }

    // ==================== LIFECYCLE MANAGEMENT ====================

    async initialize() {
        if (this.initialized) {
            this.logger.debug('Already initialized');
            return this;
        }

        this.performance.initTime = Date.now();
        this.logger.info('Initializing Enhanced Forms Manager...');

        try {
            // Setup core systems
            await this.setupCoreSystems();

            // Setup URL tracking if enabled
            if (this.options.handleURLChanges) {
                this.setupURLTracking();
            }

            // Initialize all forms
            if (this.options.autoInitialize) {
                await this.initializeAllForms();
            }

            // Setup global event handlers
            this.setupGlobalEventHandlers();

            // Setup performance monitoring
            this.setupPerformanceMonitoring();

            this.initialized = true;
            this.performance.initTime = Date.now() - this.performance.initTime;
            this.logger.info(`✅ Initialized in ${this.performance.initTime}ms`);

            // Dispatch initialization event
            this.dispatchEvent('initialized', {
                manager: this,
                stats: this.getStats()
            });

        } catch (error) {
            this.logger.error('Initialization failed:', error);
            throw error;
        }

        return this;
    }

    async destroy() {
        this.logger.info('Destroying Forms Manager...');

        // Destroy all form instances
        this.destroyAllForms();

        // Cleanup URL tracking
        this.cleanupURLTracking();

        // Cleanup mutation observers
        this.cleanupObservers();

        // Remove event listeners
        this.cleanupEventListeners();

        // Restore original history methods
        this.restoreHistoryMethods();

        // Clear all data structures
        this.formInstances.clear();
        this.handlerRegistry.clear();
        this.urlTrackers.clear();
        this.mutationObservers.clear();
        this.eventListeners.clear();
        this.reinitQueue.clear();
        this.formRegistry.byId.clear();
        this.formRegistry.byType.clear();
        this.formRegistry.byPage.clear();

        this.initialized = false;

        this.logger.info('✅ Successfully destroyed');

        return this;
    }

    async reinitialize(options = {}) {
        this.logger.info('Reinitializing Forms Manager...');

        // Update options if provided
        this.options = { ...this.options, ...options };

        // Destroy existing state
        await this.destroy();

        // Reinitialize
        await this.initialize();

        this.analytics.reinitializations++;
        this.performance.lastReinit = Date.now();

        this.dispatchEvent('reinitialized', {
            manager: this,
            stats: this.getStats()
        });

        return this;
    }

    // ==================== CORE SYSTEMS SETUP ====================

    async setupCoreSystems() {
        // Register default handlers
        this.registerDefaultHandlers();

        // // Setup form registry
        this.setupFormRegistry();

        // // Setup mutation observer for dynamic forms
        this.setupMutationObserver();

        // // Setup periodic cleanup
        // this.setupPeriodicCleanup();

        // Setup SSE if enabled
        if (this.options.enableSSE && this.options.sseEndpoint) {
            this.setupSSE();
        }
    }

    registerDefaultHandlers() {
        Object.entries(this.options.formHandlers).forEach(([type, handlerClass]) => {
            this.registerHandler(type, handlerClass);
        });

        // Register custom handlers from data attributes
        document.querySelectorAll('[data-handler-class]').forEach(el => {
            const handlerName = el.dataset.handlerClass;
            if (window[handlerName]) {
                this.registerHandler(handlerName.toLowerCase(), window[handlerName]);
            }
        });
    }

    registerHandler(type, handlerClass) {
        if (this.handlerRegistry.has(type)) {
            this.logger.warn(`Handler type "${type}" already registered, overwriting`);
        }

        this.handlerRegistry.set(type, handlerClass);
        this.logger.debug(`Registered handler: ${type}`);

        this.dispatchEvent('handler:registered', { type, handlerClass });

        return this;
    }

    unregisterHandler(type) {
        const handler = this.handlerRegistry.get(type);
        if (handler) {
            this.handlerRegistry.delete(type);
            this.logger.debug(`Unregistered handler: ${type}`);
            this.dispatchEvent('handler:unregistered', { type });
        }
        return this;
    }

    setupFormRegistry() {
        // Initial scan of existing forms
        this.scanForms();

        // Index forms by various criteria
        this.indexForms();
    }

    scanForms() {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            this.registerForm(form);
        });

        this.logger.debug(`Scanned ${forms.length} forms`);
    }

    registerForm(form) {
        if (!form.id) {
            form.id = `form_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        }

        const formData = {
            id: form.id,
            element: form,
            type: this.detectFormType(form),
            pageId: this.pageId,
            url: this.currentUrl,
            state: 'uninitialized',
            metadata: this.extractFormMetadata(form),
            createdAt: Date.now(),
            lastUpdated: Date.now()
        };

        this.formRegistry.byId.set(form.id, formData);
        this.formRegistry.byState.uninitialized.add(form.id);

        // Add to type index
        if (!this.formRegistry.byType.has(formData.type)) {
            this.formRegistry.byType.set(formData.type, new Set());
        }
        this.formRegistry.byType.get(formData.type).add(form.id);

        // Add to page index
        if (!this.formRegistry.byPage.has(this.pageId)) {
            this.formRegistry.byPage.set(this.pageId, new Set());
        }
        this.formRegistry.byPage.get(this.pageId).add(form.id);

        this.logger.debug(`Registered form: ${form.id} (${formData.type})`);

        return formData;
    }

    detectFormType(form) {
        // Check data attribute first
        if (form.dataset.formType) {
            return form.dataset.formType;
        }

        // Auto-detect based on form characteristics
        const attributes = {
            hasPassword: form.querySelector('input[type="password"]'),
            hasEmail: form.querySelector('input[type="email"]'),
            hasFile: form.querySelector('input[type="file"]'),
            hasMessage: form.querySelector('textarea[name="message"]'),
            actionContainsAuth: form.action && /auth|login|register|sign/i.test(form.action),
            hasRecaptcha: form.querySelector('.g-recaptcha'),
            hasPrivacy: form.querySelector('[name="privacy_consent"]')
        };

        if (attributes.actionContainsAuth || attributes.hasPassword) {
            return 'auth';
        } else if (attributes.hasMessage || attributes.hasFile) {
            return 'contact';
        } else if (attributes.hasEmail) {
            return 'newsletter';
        }

        return 'default';
    }

    extractFormMetadata(form) {
        const metadata = {
            fields: Array.from(form.elements).map(el => ({
                name: el.name,
                type: el.type,
                required: el.required,
                placeholder: el.placeholder
            })),
            action: form.action,
            method: form.method,
            classes: form.className,
            dataAttributes: { ...form.dataset }
        };

        return metadata;
    }

    indexForms() {
        // Reindex all forms
        this.formRegistry.byType.clear();
        this.formRegistry.byPage.clear();

        this.formRegistry.byId.forEach((formData, formId) => {
            // Index by type
            if (!this.formRegistry.byType.has(formData.type)) {
                this.formRegistry.byType.set(formData.type, new Set());
            }
            this.formRegistry.byType.get(formData.type).add(formId);

            // Index by page
            if (!this.formRegistry.byPage.has(formData.pageId)) {
                this.formRegistry.byPage.set(formData.pageId, new Set());
            }
            this.formRegistry.byPage.get(formData.pageId).add(formId);
        });
    }

    // ==================== FORM INSTANCE MANAGEMENT ====================

    async initializeAllForms() {
        this.logger.info('Initializing all forms...');

        const forms = Array.from(this.formRegistry.byId.values())
            .filter(form => form.state === 'uninitialized');

        const results = await Promise.allSettled(
            forms.map(form => this.initializeForm(form.id))
        );

        const successCount = results.filter(r => r.status === 'fulfilled').length;
        const failureCount = results.filter(r => r.status === 'rejected').length;

        this.logger.info(`✅ Initialized ${successCount} forms, ${failureCount} failed`);

        return results;
    }

    async initializeForm(formId, options = {}) {
        const formData = this.formRegistry.byId.get(formId);
        if (!formData) {
            throw new Error(`Form not found: ${formId}`);
        }

        if (formData.state === 'initialized') {
            this.logger.debug(`Form ${formId} already initialized`);
            return this.formInstances.get(formId);
        }

        const startTime = Date.now();

        try {
            // Get handler class
            const handlerType = formData.type;
            const HandlerClass = this.handlerRegistry.get(handlerType) ||
                this.handlerRegistry.get('default');

            if (!HandlerClass) {
                throw new Error(`No handler found for type: ${handlerType}`);
            }

            // Create handler instance
            const handlerOptions = {
                ...this.getDefaultOptions(handlerType),
                ...formData.metadata.dataAttributes,
                ...options,
                url: this.currentUrl // Pass current URL to handler
            };

            const handler = new HandlerClass(formId, handlerOptions);

            // Store instance
            this.formInstances.set(formId, handler);

            // Update form state
            formData.state = 'initialized';
            formData.handler = handler;
            formData.lastUpdated = Date.now();
            formData.initializedAt = Date.now();

            // Update state registry
            this.formRegistry.byState.uninitialized.delete(formId);
            this.formRegistry.byState.active.add(formId);

            // Track performance
            const initTime = Date.now() - startTime;
            this.performance.handlerStats.set(formId, {
                initTime,
                initCount: 1,
                lastInit: Date.now()
            });

            this.logger.debug(`Initialized form ${formId} in ${initTime}ms`);

            // Dispatch event
            this.dispatchEvent('form:initialized', {
                formId,
                handler,
                formData,
                initTime
            });

            return handler;

        } catch (error) {
            this.logger.error(`Failed to initialize form ${formId}:`, error);

            // Update form state
            formData.state = 'failed';
            formData.error = error;
            this.formRegistry.byState.uninitialized.delete(formId);
            this.formRegistry.byState.inactive.add(formId);

            this.dispatchEvent('form:initFailed', {
                formId,
                error,
                formData
            });

            throw error;
        }
    }

    getDefaultOptions(handlerType) {
        const defaults = {
            debug: this.options.debug,
            trackAnalytics: this.options.trackAnalytics
        };

        switch (handlerType) {
            case 'auth':
                return {
                    ...defaults,
                    enablePasswordStrength: true,
                    enablePasswordToggle: true,
                    enableRememberMe: true
                };
            case 'contact':
                return {
                    ...defaults,
                    enableFileUpload: true,
                    requirePrivacyConsent: true
                };
            case 'newsletter':
                return {
                    ...defaults,
                    responseType: 'json',
                    replaceOnSuccess: true
                };
            default:
                return defaults;
        }
    }

    destroyForm(formId) {
        const handler = this.formInstances.get(formId);
        if (!handler) {
            this.logger.debug(`No handler found for form: ${formId}`);
            return false;
        }

        try {
            // Destroy handler
            if (typeof handler.destroy === 'function') {
                handler.destroy();
            }

            // Remove from instances
            this.formInstances.delete(formId);

            // Update form state
            const formData = this.formRegistry.byId.get(formId);
            if (formData) {
                formData.state = 'destroyed';
                formData.destroyedAt = Date.now();
                this.formRegistry.byState.active.delete(formId);
                this.formRegistry.byState.destroyed.add(formId);
            }

            // Remove performance stats
            this.performance.handlerStats.delete(formId);

            this.logger.debug(`Destroyed form: ${formId}`);

            this.dispatchEvent('form:destroyed', { formId, formData });

            return true;

        } catch (error) {
            this.logger.error(`Failed to destroy form ${formId}:`, error);
            return false;
        }
    }

    destroyAllForms() {
        this.logger.info('Destroying all forms...');

        const formIds = Array.from(this.formInstances.keys());
        const results = formIds.map(formId => this.destroyForm(formId));

        const successCount = results.filter(r => r).length;

        this.logger.info(`✅ Destroyed ${successCount} forms`);

        return successCount;
    }

    reinitializeForm(formId) {
        const handler = this.formInstances.get(formId);
        if (!handler) {
            this.logger.warn(`Cannot reinitialize non-existent form: ${formId}`);
            return null;
        }

        const formData = this.formRegistry.byId.get(formId);
        if (!formData) {
            this.logger.warn(`No form data found for: ${formId}`);
            return null;
        }

        this.logger.debug(`Reinitializing form: ${formId}`);

        // Destroy existing handler
        this.destroyForm(formId);

        // Reinitialize with same options
        const options = { ...formData.metadata.dataAttributes, url: this.currentUrl };
        const newHandler = this.initializeForm(formId, options);

        return newHandler;
    }

    getForm(formId) {
        return this.formInstances.get(formId);
    }

    getFormData(formId) {
        const handler = this.getForm(formId);
        if (handler && typeof handler.getData === 'function') {
            return handler.getData();
        }
        return null;
    }

    setFormData(formId, data) {
        const handler = this.getForm(formId);
        if (handler && typeof handler.setData === 'function') {
            handler.setData(data);
            return true;
        }
        return false;
    }

    submitForm(formId) {
        const handler = this.getForm(formId);
        if (handler && typeof handler.submit === 'function') {
            return handler.submit();
        }
        return false;
    }

    validateForm(formId) {
        const handler = this.getForm(formId);
        if (handler && typeof handler.validateForm === 'function') {
            return handler.validateForm();
        }
        return false;
    }

    // ==================== URL TRACKING & NAVIGATION ====================

    setupURLTracking() {
        this.currentUrl = window.location.href;
        this.previousUrl = null;
        this.pageId = this.generatePageId();
        this.pageType = this.detectPageType();

        // Setup history state tracking
        this.wrapHistoryMethods();

        // Setup popstate listener
        this.setupPopStateListener();

        // Setup hashchange listener
        this.setupHashChangeListener();

        // Setup visibility change listener
        this.setupVisibilityListener();

        this.logger.info('URL tracking initialized', {
            pageId: this.pageId,
            pageType: this.pageType,
            url: this.currentUrl
        });

        this.dispatchEvent('url:tracking:initialized', {
            pageId: this.pageId,
            pageType: this.pageType,
            url: this.currentUrl
        });
    }

    generatePageId() {
        const url = new URL(window.location.href);
        const idParts = [
            url.pathname.replace(/[^a-z0-9]/gi, '_'),
            url.search.length > 1 ? '_' + url.search.slice(1).replace(/[^a-z0-9]/gi, '_') : '',
            url.hash.length > 1 ? '_' + url.hash.slice(1).replace(/[^a-z0-9]/gi, '_') : ''
        ];

        return idParts.join('') || 'root';
    }

    detectPageType() {
        const path = window.location.pathname;
        const url = window.location.href.toLowerCase();

        // Authentication pages
        const authPatterns = [
            /\/login(?:\/|$)/i,
            /\/register(?:\/|$)/i,
            /\/sign(?:in|up)(?:\/|$)/i,
            /\/auth(?:\/|$)/i,
            /\/password-(?:reset|change|forgot)(?:\/|$)/i,
            /\/verify-(?:email|account)(?:\/|$)/i
        ];

        if (authPatterns.some(pattern => pattern.test(path))) {
            return 'auth';
        }

        // Form-heavy pages
        const formCount = document.querySelectorAll('form').length;
        const hasComplexForms = document.querySelectorAll('form[data-form-type]').length > 0;

        if (formCount > 2 || hasComplexForms) {
            return 'forms';
        }

        // Check for form-related content
        const formKeywords = ['contact', 'signup', 'subscribe', 'newsletter', 'feedback', 'survey'];
        const bodyText = document.body.textContent.toLowerCase();
        const hasFormContent = formKeywords.some(keyword =>
            bodyText.includes(keyword) || path.includes(keyword)
        );

        if (hasFormContent) {
            return 'forms';
        }

        return 'regular';
    }

    wrapHistoryMethods() {
        const self = this;

        // Wrap pushState
        window.history.pushState = new Proxy(this.originalHistoryMethods.pushState, {
            apply(target, thisArg, args) {
                const result = target.apply(thisArg, args);
                self.handleHistoryChange('pushState', args[2]);
                return result;
            }
        });

        // Wrap replaceState
        window.history.replaceState = new Proxy(this.originalHistoryMethods.replaceState, {
            apply(target, thisArg, args) {
                const result = target.apply(thisArg, args);
                self.handleHistoryChange('replaceState', args[2]);
                return result;
            }
        });

        this.logger.debug('History methods wrapped');
    }

    setupPopStateListener() {
        const handler = (event) => {
            this.handleHistoryChange('popstate', event.state);
        };

        window.addEventListener('popstate', handler);
        this.urlTrackers.set('popstate', handler);
    }

    setupHashChangeListener() {
        const handler = () => {
            this.handleHistoryChange('hashchange', { hash: window.location.hash });
        };

        window.addEventListener('hashchange', handler);
        this.urlTrackers.set('hashchange', handler);
    }

    setupVisibilityListener() {
        const handler = () => {
            if (document.visibilityState === 'visible') {
                this.handlePageVisibilityChange();
            }
        };

        document.addEventListener('visibilitychange', handler);
        this.urlTrackers.set('visibilitychange', handler);
    }

    handleHistoryChange(type, state) {
        const oldUrl = this.currentUrl;
        const newUrl = window.location.href;

        if (oldUrl === newUrl) return;

        this.previousUrl = oldUrl;
        this.currentUrl = newUrl;
        this.analytics.urlChanges++;

        // Add to navigation history
        this.navigationHistory.push({
            type,
            from: oldUrl,
            to: newUrl,
            state,
            timestamp: Date.now()
        });

        // Keep history size manageable
        if (this.navigationHistory.length > 50) {
            this.navigationHistory.shift();
        }

        // Detect page type change
        const oldPageId = this.pageId;
        const oldPageType = this.pageType;

        this.pageId = this.generatePageId();
        this.pageType = this.detectPageType();

        const pageChanged = oldPageId !== this.pageId;
        const typeChanged = oldPageType !== this.pageType;

        this.logger.debug('URL changed', {
            type,
            from: oldUrl,
            to: newUrl,
            pageChanged,
            typeChanged
        });

        // Dispatch event
        this.dispatchEvent('url:changed', {
            type,
            oldUrl,
            newUrl,
            oldPageId,
            newPageId: this.pageId,
            oldPageType,
            newPageType: this.pageType,
            state
        });

        // Handle form reinitialization if needed
        if (pageChanged || typeChanged) {
            this.handlePageTransition(oldPageType, this.pageType);
        }

        // Update all form handlers with new URL
        this.updateFormHandlersUrl(newUrl);
    }

    updateFormHandlersUrl(url) {
        this.formInstances.forEach((handler, formId) => {
            if (handler && typeof handler.updateUrl === 'function') {
                handler.updateUrl(url);
            }
        });
    }

    handlePageVisibilityChange() {
        const currentPageId = this.generatePageId();
        if (currentPageId !== this.pageId) {
            this.logger.info('Page changed while tab was hidden, reinitializing...');
            this.handlePageTransition(this.pageType, this.detectPageType());
        }
    }

    handlePageTransition(oldPageType, newPageType) {
        const transitionType = this.determineTransitionType(oldPageType, newPageType);

        this.logger.info(`Page transition: ${oldPageType} → ${newPageType} (${transitionType})`);

        switch (transitionType) {
            case 'auth_to_auth':
            case 'forms_to_forms':
                // Reinitialize forms on same page type
                this.reinitializeFormsOnPage();
                break;

            case 'auth_to_regular':
            case 'forms_to_regular':
                // Cleanup specialized forms
                this.cleanupSpecializedForms(oldPageType);
                break;

            case 'regular_to_auth':
            case 'regular_to_forms':
                // Initialize new forms
                this.initializePageForms();
                break;

            default:
                // Full reinitialization
                this.queueReinitialization('page_transition');
        }
    }

    determineTransitionType(oldType, newType) {
        if (oldType === newType) {
            return `${oldType}_to_${newType}`;
        }
        return `${oldType}_to_${newType}`;
    }

    cleanupURLTracking() {
        // Remove event listeners
        this.urlTrackers.forEach((handler, type) => {
            if (type === 'popstate' || type === 'hashchange') {
                window.removeEventListener(type, handler);
            } else if (type === 'visibilitychange') {
                document.removeEventListener(type, handler);
            }
        });

        this.urlTrackers.clear();

        this.logger.debug('URL tracking cleaned up');
    }

    restoreHistoryMethods() {
        if (this.originalHistoryMethods) {
            window.history.pushState = this.originalHistoryMethods.pushState;
            window.history.replaceState = this.originalHistoryMethods.replaceState;
        }
    }

    // ==================== MUTATION OBSERVER ====================

    setupMutationObserver() {
        const observer = new MutationObserver((mutations) => {
            this.handleDOMChanges(mutations);
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ['id', 'class', 'data-form-type', 'data-form', 'style']
        });

        this.mutationObservers.set('main', observer);

        this.logger.debug('Mutation observer setup');
    }

    handleDOMChanges(mutations) {
        let formsAdded = [];
        let formsRemoved = [];
        let formsChanged = [];

        mutations.forEach((mutation) => {
            // Check for added forms
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === 1) { // Element node
                        if (node.tagName === 'FORM') {
                            formsAdded.push(node);
                        } else {
                            const forms = node.querySelectorAll?.('form') || [];
                            formsAdded.push(...forms);
                        }
                    }
                });

                // Check for removed forms
                mutation.removedNodes.forEach((node) => {
                    if (node.nodeType === 1) {
                        if (node.tagName === 'FORM' && node.id) {
                            formsRemoved.push(node.id);
                        } else {
                            const forms = node.querySelectorAll?.('form') || [];
                            formsRemoved.push(...Array.from(forms).map(f => f.id).filter(id => id));
                        }
                    }
                });
            }

            // Check for attribute changes on forms
            if (mutation.type === 'attributes' && mutation.target.tagName === 'FORM') {
                formsChanged.push(mutation.target);
            }
        });

        // Handle added forms
        formsAdded.forEach(form => {
            if (!this.formRegistry.byId.has(form.id)) {
                this.registerForm(form);
                this.initializeForm(form.id);
                this.analytics.dynamicInjects++;
            }
        });

        // Handle removed forms
        formsRemoved.forEach(formId => {
            if (this.formRegistry.byId.has(formId)) {
                this.destroyForm(formId);
            }
        });

        // Handle changed forms
        formsChanged.forEach(form => {
            if (this.formRegistry.byId.has(form.id)) {
                this.updateFormMetadata(form.id);
            }
        });

        if (formsAdded.length > 0 || formsRemoved.length > 0 || formsChanged.length > 0) {
            this.logger.debug('DOM changes processed', {
                added: formsAdded.length,
                removed: formsRemoved.length,
                changed: formsChanged.length
            });
        }
    }

    cleanupObservers() {
        this.mutationObservers.forEach(observer => {
            observer.disconnect();
        });
        this.mutationObservers.clear();
    }

    // ==================== REINITIALIZATION QUEUE ====================

    queueReinitialization(reason) {
        this.reinitQueue.add(reason);

        // Debounce reinitialization
        clearTimeout(this.reinitTimeout);
        this.reinitTimeout = setTimeout(() => {
            this.processReinitializationQueue();
        }, 300);
    }

    processReinitializationQueue() {
        if (this.reinitQueue.size === 0) return;

        this.logger.debug('Processing reinitialization queue', {
            reasons: Array.from(this.reinitQueue)
        });

        // Determine reinitialization strategy
        const reasons = Array.from(this.reinitQueue);
        const needsFullReinit = reasons.some(reason =>
            reason === 'page_transition'
        );

        if (needsFullReinit) {
            this.reinitializeForms();
        } else {
            this.reinitializeAffectedForms(reasons);
        }

        this.reinitQueue.clear();
    }

    reinitializeForms() {
        this.logger.info('Reinitializing all forms');

        // Destroy all handlers
        this.destroyAllForms();

        // Reinitialize forms on current page
        this.initializePageForms();

        this.dispatchEvent('forms:reinitialized', {
            type: 'full',
            timestamp: Date.now()
        });
    }

    reinitializeAffectedForms(reasons) {
        this.logger.debug('Reinitializing affected forms', { reasons });

        // Determine which forms need reinitialization
        const formsToReinit = new Set();

        reasons.forEach(reason => {
            switch (reason) {
                case 'dynamic_content':
                    // Reinitialize forms that were dynamically added
                    Array.from(this.formRegistry.byState.active)
                        .forEach(formId => {
                            const formData = this.formRegistry.byId.get(formId);
                            if (formData && Date.now() - formData.createdAt < 5000) {
                                formsToReinit.add(formId);
                            }
                        });
                    break;

                case 'url_hash_change':
                    // Reinitialize forms affected by hash
                    const hash = window.location.hash;
                    if (hash) {
                        this.formRegistry.byId.forEach((formData, formId) => {
                            if (formData.element.id === hash.replace('#', '') ||
                                formData.element.classList.contains(hash.replace('#', ''))) {
                                formsToReinit.add(formId);
                            }
                        });
                    }
                    break;

                default:
                    // Reinitialize all active forms for other reasons
                    Array.from(this.formRegistry.byState.active)
                        .forEach(formId => formsToReinit.add(formId));
            }
        });

        // Reinitialize each form
        formsToReinit.forEach(formId => {
            this.reinitializeForm(formId);
        });

        this.dispatchEvent('forms:reinitialized', {
            type: 'partial',
            count: formsToReinit.size,
            reasons
        });
    }

    reinitializeFormsOnPage() {
        const pageForms = this.formRegistry.byPage.get(this.pageId) || new Set();
        pageForms.forEach(formId => {
            if (this.formRegistry.byState.active.has(formId)) {
                this.reinitializeForm(formId);
            }
        });
    }

    cleanupSpecializedForms(pageType) {
        const formsToDestroy = [];

        this.formRegistry.byType.forEach((formIds, type) => {
            if (type === pageType) {
                formIds.forEach(formId => {
                    if (this.formRegistry.byState.active.has(formId)) {
                        formsToDestroy.push(formId);
                    }
                });
            }
        });

        formsToDestroy.forEach(formId => {
            this.destroyForm(formId);
        });
    }

    initializePageForms() {
        const formsOnPage = document.querySelectorAll('form');
        formsOnPage.forEach(form => {
            if (!this.formRegistry.byId.has(form.id)) {
                this.registerForm(form);
                this.initializeForm(form.id);
            }
        });
    }

    // ==================== EVENT SYSTEM ====================

    setupGlobalEventHandlers() {
        // Form lifecycle events
        const events = [
            'form:initialized',
            'form:destroyed',
            'form:submit',
            'form:success',
            'form:error',
            'form:validate',
            'url:changed'
        ];

        events.forEach(event => {
            const handler = (e) => this.handleGlobalEvent(event, e);
            document.addEventListener(event, handler);
            this.eventListeners.set(event, handler);
        });
    }

    handleGlobalEvent(event, detail) {
        // Log important events in debug mode
        if (this.options.debug) {
            this.logger.debug(`Global event: ${event}`, detail);
        }

        // Update analytics based on event
        switch (event) {
            case 'form:success':
                const formId = detail.formId || detail.form?.id;
                if (formId) {
                    if (!this.analytics.submissions.has(formId)) {
                        this.analytics.submissions.set(formId, []);
                    }
                    this.analytics.submissions.get(formId).push({
                        timestamp: Date.now(),
                        success: detail.success !== false,
                        data: detail.result
                    });
                }
                break;
            case 'form:error':
                const errorFormId = detail.formId || detail.form?.id;
                if (errorFormId) {
                    if (!this.analytics.errors.has(errorFormId)) {
                        this.analytics.errors.set(errorFormId, []);
                    }
                    this.analytics.errors.get(errorFormId).push({
                        timestamp: Date.now(),
                        error: detail.error,
                        message: detail.message
                    });
                }
                break;
            case 'form:validate':
                const validateFormId = detail.formId || detail.form?.id;
                if (validateFormId) {
                    if (!this.analytics.validations.has(validateFormId)) {
                        this.analytics.validations.set(validateFormId, []);
                    }
                    this.analytics.validations.get(validateFormId).push({
                        timestamp: Date.now(),
                        valid: detail.isValid,
                        invalidFields: detail.invalidFields?.length || 0
                    });
                }
                break;
        }
    }

    cleanupEventListeners() {
        this.eventListeners.forEach((handler, event) => {
            document.removeEventListener(event, handler);
        });
        this.eventListeners.clear();
    }

    dispatchEvent(event, detail = {}) {
        const customEvent = new CustomEvent(event, {
            detail: { ...detail, manager: this },
            bubbles: true,
            cancelable: true
        });

        document.dispatchEvent(customEvent);

        // Also dispatch to manager-specific namespace
        const managerEvent = new CustomEvent(`formsmanager:${event}`, {
            detail: { ...detail, manager: this },
            bubbles: true,
            cancelable: true
        });

        document.dispatchEvent(managerEvent);
    }

    on(event, callback) {
        const handler = (e) => {
            if (e.detail?.manager === this) {
                callback(e.detail);
            }
        };

        document.addEventListener(`formsmanager:${event}`, handler);

        // Store for cleanup
        if (!this.customEventHandlers) {
            this.customEventHandlers = new Map();
        }

        this.customEventHandlers.set(callback, { event: `formsmanager:${event}`, handler });

        return this;
    }

    off(event, callback) {
        if (!this.customEventHandlers) return;

        const handlerInfo = this.customEventHandlers.get(callback);
        if (handlerInfo && handlerInfo.event === `formsmanager:${event}`) {
            document.removeEventListener(handlerInfo.event, handlerInfo.handler);
            this.customEventHandlers.delete(callback);
        }

        return this;
    }

    // ==================== UTILITY METHODS ====================

    getStats() {
        return {
            initialized: this.initialized,
            forms: {
                total: this.formRegistry.byId.size,
                active: this.formRegistry.byState.active.size,
                inactive: this.formRegistry.byState.inactive.size,
                destroyed: this.formRegistry.byState.destroyed.size
            },
            handlers: {
                registered: this.handlerRegistry.size,
                instances: this.formInstances.size
            },
            page: {
                id: this.pageId,
                type: this.pageType,
                url: this.currentUrl
            },
            analytics: this.getAnalyticsData(),
            performance: {
                initTime: this.performance.initTime,
                avgInitTime: this.performance.avgInitTime,
                lastReinit: this.performance.lastReinit
            }
        };
    }

    getAnalyticsData() {
        return {
            timestamp: Date.now(),
            pageId: this.pageId,
            pageType: this.pageType,
            url: this.currentUrl,
            forms: {
                total: this.formRegistry.byId.size,
                active: this.formRegistry.byState.active.size,
                byType: Object.fromEntries(
                    Array.from(this.formRegistry.byType.entries()).map(([type, set]) => [type, set.size])
                )
            },
            submissions: Object.fromEntries(
                Array.from(this.analytics.submissions.entries()).map(([formId, submissions]) => [
                    formId,
                    {
                        count: submissions.length,
                        last: submissions[submissions.length - 1]
                    }
                ])
            ),
            validations: Object.fromEntries(
                Array.from(this.analytics.validations.entries()).map(([formId, validations]) => [
                    formId,
                    {
                        count: validations.length,
                        successRate: validations.filter(v => v.valid).length / validations.length
                    }
                ])
            ),
            errors: Object.fromEntries(
                Array.from(this.analytics.errors.entries()).map(([formId, errors]) => [
                    formId,
                    {
                        count: errors.length,
                        recent: errors.slice(-5)
                    }
                ])
            ),
            system: {
                urlChanges: this.analytics.urlChanges,
                dynamicInjects: this.analytics.dynamicInjects,
                reinitializations: this.analytics.reinitializations
            },
            performance: {
                avgInitTime: this.performance.avgInitTime,
                handlerStats: Object.fromEntries(this.performance.handlerStats.entries())
            }
        };
    }

    logStats() {
        this.logger.info('Manager Statistics:', this.getStats());
    }

    getFormById(formId) {
        return this.formRegistry.byId.get(formId);
    }

    getFormsByType(type) {
        const formIds = this.formRegistry.byType.get(type) || new Set();
        return Array.from(formIds).map(id => this.formRegistry.byId.get(id));
    }

    getFormsByPage(pageId = this.pageId) {
        const formIds = this.formRegistry.byPage.get(pageId) || new Set();
        return Array.from(formIds).map(id => this.formRegistry.byId.get(id));
    }

    getActiveForms() {
        return Array.from(this.formRegistry.byState.active)
            .map(id => this.formRegistry.byId.get(id));
    }

    updateFormMetadata(formId) {
        const formData = this.formRegistry.byId.get(formId);
        if (!formData) return;

        formData.metadata = this.extractFormMetadata(formData.element);
        formData.lastUpdated = Date.now();

        this.dispatchEvent('form:metadata:updated', { formId, formData });
    }

    setupPerformanceMonitoring() {
        // Monitor handler performance
        this.performanceMonitor = setInterval(() => {
            this.updatePerformanceStats();
        }, 30000); // Every 30 seconds
    }

    updatePerformanceStats() {
        // Calculate average init time
        const initTimes = Array.from(this.performance.handlerStats.values())
            .map(stats => stats.initTime)
            .filter(time => time > 0);

        if (initTimes.length > 0) {
            this.performance.avgInitTime =
                initTimes.reduce((sum, time) => sum + time, 0) / initTimes.length;
        }
    }

    // ==================== SSE SUPPORT ====================

    setupSSE() {
        if (!this.options.sseEndpoint) return;

        try {
            this.sseConnection = new EventSource(this.options.sseEndpoint);

            this.sseConnection.onopen = () => {
                this.logger.info('SSE connection established');
                this.dispatchEvent('sse:connected');
            };

            this.sseConnection.onmessage = (event) => {
                this.handleSSEMessage(event.data);
            };

            this.sseConnection.onerror = (error) => {
                this.logger.error('SSE connection error:', error);
                this.dispatchEvent('sse:error', { error });
            };

        } catch (error) {
            this.logger.error('Failed to setup SSE:', error);
        }
    }

    handleSSEMessage(data) {
        try {
            const message = JSON.parse(data);

            switch (message.type) {
                case 'form_update':
                    this.handleFormUpdate(message);
                    break;
                case 'validation':
                    this.handleRemoteValidation(message);
                    break;
                case 'notification':
                    window.showNotification(message);
                    break;
                default:
                    this.dispatchEvent('sse:message', { message });
            }
        } catch (error) {
            this.logger.error('Failed to parse SSE message:', error);
        }
    }

    handleFormUpdate(message) {
        const { formId, field, value } = message;
        this.setFormData(formId, { [field]: value });
    }

    handleRemoteValidation(message) {
        const { formId, field, valid, message: validationMessage } = message;

        const handler = this.getForm(formId);
        if (handler && handler.validateField) {
            const fieldElement = document.querySelector(`[name="${field}"]`);
            if (fieldElement) {
                if (valid) {
                    handler.clearFieldError(fieldElement);
                } else {
                    handler.showFieldError(fieldElement, validationMessage);
                }
            }
        }
    }

    // ==================== PUBLIC API ====================

    getFormHandler(formId) {
        return this.getForm(formId);
    }

    getAllForms() {
        return Array.from(this.formInstances.values());
    }

    getFormCount() {
        return this.formRegistry.byId.size;
    }

    isFormActive(formId) {
        return this.formRegistry.byState.active.has(formId);
    }

    hasForm(formId) {
        return this.formRegistry.byId.has(formId);
    }

    getFormTypes() {
        return Array.from(this.formRegistry.byType.keys());
    }

    getPageForms() {
        return this.getFormsByPage();
    }

    exportFormData(formId, format = 'json') {
        const handler = this.getForm(formId);
        if (!handler?.getData) return null;

        const data = handler.getData();

        switch (format.toLowerCase()) {
            case 'json':
                return JSON.stringify(data, null, 2);
            case 'csv':
                return this.convertToCSV(data);
            case 'formdata':
                return new FormData(data);
            default:
                return data;
        }
    }

    convertToCSV(data) {
        const headers = Object.keys(data);
        const values = Object.values(data).map(value =>
            typeof value === 'string' ? `"${value.replace(/"/g, '""')}"` : value
        );

        return `${headers.join(',')}\n${values.join(',')}`;
    }

    printForm(formId) {
        const form = document.getElementById(formId);
        if (!form) return;

        const printWindow = window.open('', '_blank');
        printWindow.document.write(`
            <html>
            <head>
                <title>Print Form - ${formId}</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    .form-print { border: 1px solid #ddd; padding: 20px; }
                    h2 { color: #333; }
                    .form-field { margin-bottom: 15px; }
                    label { font-weight: bold; display: block; margin-bottom: 5px; }
                    .value { padding: 8px; background: #f5f5f5; border-radius: 4px; }
                </style>
            </head>
            <body>
                <div class="form-print">
                    <h2>Form: ${formId}</h2>
                    <div id="form-content"></div>
                </div>
                <script>window.onload = () => window.print();</script>
            </body>
            </html>
        `);

        const handler = this.getForm(formId);
        if (handler?.getData) {
            const data = handler.getData();
            const content = Object.entries(data).map(([key, value]) => `
                <div class="form-field">
                    <label>${key}:</label>
                    <div class="value">${value || '(empty)'}</div>
                </div>
            `).join('');
            printWindow.document.getElementById('form-content').innerHTML = content;
        }
    }

    // Cleanup method for periodic cleanup
    setupPeriodicCleanup() {
        // Cleanup destroyed forms periodically
        this.cleanupInterval = setInterval(() => {
            this.cleanupOldForms();
        }, 300000); // Every 5 minutes
    }

    cleanupOldForms() {
        const now = Date.now();
        const formsToRemove = [];

        this.formRegistry.byId.forEach((formData, formId) => {
            if (formData.state === 'destroyed' &&
                now - formData.destroyedAt > 3600000) { // 1 hour
                formsToRemove.push(formId);
            }
        });

        formsToRemove.forEach(formId => {
            this.formRegistry.byId.delete(formId);
            this.formRegistry.byState.destroyed.delete(formId);
        });

        if (formsToRemove.length > 0) {
            this.logger.debug(`Cleaned up ${formsToRemove.length} old forms`);
        }
    }
}

export default FormsManager;