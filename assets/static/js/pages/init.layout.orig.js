// # not used
/**
 * @file pages/init.layout.js
 * Unified Page & Layout Management System
 *
 * Combines:
 * - PagesManager: URL tracking, parameters, page info
 * - BaseLayout: Core layout functionality
 * - LayoutManager: Layout detection and initialization
 */

import { BaseManager } from '../utility/base.manager.js';
import { DOM } from '../utility/dom.js';
import { Utils } from '../utility/helpers.js';

// ============================================================================
// PART 1: PAGES MANAGER
// URL tracking, parameter management, and page information
// ============================================================================

export class PagesManager {
    constructor(options = {}) {
        this.options = {
            // URL Tracking options
            trackQueryParams: false,
            trackHash: true,
            trackPageInfo: true,
            maxHistory: 50,
            storageKey: 'pages_manager_state',
            persistState: true,
            debounceDelay: 250,

            // URL Parameters options
            syncOnChange: true,
            persistParams: false,
            paramsStorageKey: 'url_params_cache',
            excludeParams: ['utm_', 'fbclid', 'gclid', 'ref', 'source'],
            includeParams: [],
            defaultValues: {},
            autoUpdateForms: true,
            formSelector: 'form[data-url-params]',
            autoSyncLinks: true,
            linkSelector: 'a[data-params]',

            // Page Info options
            extractOnInit: true,
            watchMetaChanges: true,
            watchTitleChanges: true,

            // General
            debug: false,
            ...options
        };

        // Core state
        this.state = {
            currentUrl: window.location.href,
            currentPath: window.location.pathname,
            currentHash: window.location.hash,
            currentSearch: '',
            previousUrl: null,
            urlHistory: [],
            pageHistory: [],
            currentPage: null,
            previousPage: null,
            params: new Map(),
            formElements: new Set(),
            linkElements: new Set(),
            observers: [],
            initialized: false
        };

        this.handlers = new Map();
        this.cleanupFns = [];
        this.lastUrl = window.location.href;
        this.lastPath = window.location.pathname;

        this.handleURLChange = Utils.debounce(
            this._handleURLChange.bind(this),
            this.options.debounceDelay
        );

        this.log = (...args) => {
            if (this.options.debug) console.log('[PagesManager]', ...args);
        };
    }

    async initialize() {
        if (this.state.initialized) return this;

        try {
            if (this.options.persistState) await this.loadState();

            this.setupURLTracking();
            this.setupHistoryMethods();

            if (this.options.trackPageInfo || this.options.extractOnInit) {
                await this.extractPageInfo();
            }

            this.loadParametersFromURL();

            if (this.options.autoUpdateForms) this.discoverForms();
            if (this.options.autoSyncLinks) this.discoverLinks();

            this.setupParameterListeners();

            this.state.initialized = true;
            this.log('✅ Pages Manager initialized');
            this.dispatchEvent('pages:initialized', { state: this.getState() });

        } catch (error) {
            console.error('Failed to initialize PagesManager:', error);
            throw error;
        }

        return this;
    }

    // URL Tracking
    setupURLTracking() {
        const urlObserver = new MutationObserver(() => {
            const currentUrl = window.location.href;
            if (currentUrl !== this.lastUrl) {
                this.handleURLChange(currentUrl, 'mutation');
            }
        });

        const titleElement = document.querySelector('title');
        if (titleElement) {
            urlObserver.observe(titleElement, { childList: true, subtree: true });
        }

        urlObserver.observe(document.body, {
            attributes: true,
            attributeFilter: ['data-page', 'data-layout', 'data-section'],
            childList: true,
            subtree: false
        });

        this.state.observers.push(urlObserver);
        this.cleanupFns.push(() => urlObserver.disconnect());

        if (this.options.trackHash) {
            const hashchangeHandler = () => this.handleHashChange();
            window.addEventListener('hashchange', hashchangeHandler);
            this.cleanupFns.push(() => window.removeEventListener('hashchange', hashchangeHandler));
        }

        const popstateHandler = () => {
            setTimeout(() => this.handleURLChange(window.location.href, 'popstate'), 0);
        };
        window.addEventListener('popstate', popstateHandler);
        this.cleanupFns.push(() => window.removeEventListener('popstate', popstateHandler));
    }

    setupHistoryMethods() {
        const originalPushState = history.pushState;
        const originalReplaceState = history.replaceState;

        const createPatchedMethod = (original, methodName) => {
            return function (...args) {
                const result = original.apply(this, args);
                setTimeout(() => {
                    this._handleURLChange(window.location.href, methodName);
                }, 0);
                return result;
            }.bind(this);
        };

        history.pushState = createPatchedMethod(originalPushState, 'pushState');
        history.replaceState = createPatchedMethod(originalReplaceState, 'replaceState');

        this.originalPushState = originalPushState;
        this.originalReplaceState = originalReplaceState;

        this.cleanupFns.push(() => {
            history.pushState = originalPushState;
            history.replaceState = originalReplaceState;
        });
    }

    handleHashChange() {
        const previousHash = this.state.currentHash;
        this.state.currentHash = window.location.hash;
        this.dispatchEvent('pages:hash-changed', {
            previousHash,
            currentHash: this.state.currentHash,
            timestamp: Date.now()
        });
    }

    _handleURLChange(url, source) {
        const previousUrl = this.lastUrl;
        const previousPath = this.lastPath;

        this.lastUrl = url;
        this.lastPath = new URL(url, window.location.origin).pathname;

        this.state.previousUrl = this.state.currentUrl;
        this.state.currentUrl = url;
        this.state.currentPath = this.lastPath;
        this.state.currentHash = window.location.hash;
        this.state.currentSearch = '';

        this.addToUrlHistory({
            previousUrl,
            currentUrl: url,
            previousPath,
            currentPath: this.state.currentPath,
            source,
            timestamp: Date.now()
        });

        this.loadParametersFromURL();
        this.syncForms();
        this.syncLinks();

        if (this.options.trackPageInfo) this.extractPageInfo();

        this.dispatchEvent('pages:url-changed', {
            previousUrl,
            currentUrl: url,
            previousPath,
            currentPath: this.state.currentPath,
            source,
            timestamp: Date.now()
        });

        this.dispatchEvent('pages:parameters-changed', {
            params: this.getAllParameters(),
            source: 'url-change',
            timestamp: Date.now()
        });

        if (this.options.persistState) this.saveState();
    }

    addToUrlHistory(entry) {
        this.state.urlHistory.unshift(entry);
        if (this.state.urlHistory.length > this.options.maxHistory) {
            this.state.urlHistory.pop();
        }
    }

    // URL Parameters
    loadParametersFromURL() {
        const url = new URL(this.state.currentUrl);
        const newParams = new Map();

        url.searchParams.forEach((value, key) => {
            if (!this.shouldExcludeParam(key)) {
                newParams.set(key, value);
            }
        });

        if (!this.areMapsEqual(this.state.params, newParams)) {
            this.state.params = newParams;
            this.log('Loaded parameters from URL:', Object.fromEntries(newParams));

            this.dispatchEvent('pages:parameters-changed', {
                params: this.getAllParameters(),
                source: 'url-load',
                timestamp: Date.now()
            });

            if (this.options.persistParams) this.saveParametersToStorage();
        }
    }

    shouldExcludeParam(key) {
        for (const pattern of this.options.excludeParams) {
            if (key.startsWith(pattern)) return true;
        }
        if (this.options.includeParams.length > 0) {
            return !this.options.includeParams.some(pattern => key.startsWith(pattern));
        }
        return false;
    }

    setupParameterListeners() {
        document.addEventListener('submit', (e) => {
            if (e.target.matches(this.options.formSelector)) {
                this.handleFormSubmit(e.target);
            }
        });

        document.addEventListener('click', (e) => {
            const link = e.target.closest(this.options.linkSelector);
            if (link) this.handleLinkClick(link, e);
        });
    }

    discoverForms() {
        document.querySelectorAll(this.options.formSelector).forEach(form => {
            this.registerForm(form);
        });

        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList') {
                    mutation.addedNodes.forEach((node) => {
                        if (node.nodeType === Node.ELEMENT_NODE) {
                            if (node.matches(this.options.formSelector)) {
                                this.registerForm(node);
                            }
                            node.querySelectorAll(this.options.formSelector).forEach(form => {
                                this.registerForm(form);
                            });
                        }
                    });
                }
            });
        });

        observer.observe(document.body, { childList: true, subtree: true });
        this.state.observers.push(observer);
    }

    discoverLinks() {
        document.querySelectorAll(this.options.linkSelector).forEach(link => {
            this.registerLink(link);
        });

        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList') {
                    mutation.addedNodes.forEach((node) => {
                        if (node.nodeType === Node.ELEMENT_NODE) {
                            if (node.matches(this.options.linkSelector)) {
                                this.registerLink(node);
                            }
                            node.querySelectorAll(this.options.linkSelector).forEach(link => {
                                this.registerLink(link);
                            });
                        }
                    });
                }
            });
        });

        observer.observe(document.body, { childList: true, subtree: true });
        this.state.observers.push(observer);
    }

    registerForm(form) {
        if (!this.state.formElements.has(form)) {
            this.state.formElements.add(form);
            this.syncForm(form);

            const observer = new MutationObserver(() => this.syncForm(form));
            observer.observe(form, { attributes: true, childList: true, subtree: true });
            this.state.observers.push({ form, observer });
        }
    }

    registerLink(link) {
        if (!this.state.linkElements.has(link)) {
            this.state.linkElements.add(link);
            this.syncLink(link);
        }
    }

    syncForms() {
        this.state.formElements.forEach(form => this.syncForm(form));
    }

    syncLinks() {
        this.state.linkElements.forEach(link => this.syncLink(link));
    }

    syncForm(form) {
        const elements = form.elements;

        for (let i = 0; i < elements.length; i++) {
            const element = elements[i];
            const paramName = element.getAttribute('data-param') || element.name;

            if (paramName && this.state.params.has(paramName)) {
                const value = this.state.params.get(paramName);

                switch (element.type) {
                    case 'checkbox':
                        element.checked = value === 'true' || value === 'on' || value === '1';
                        break;
                    case 'radio':
                        if (element.value === value) element.checked = true;
                        break;
                    case 'select-multiple':
                        const values = value.split(',');
                        Array.from(element.options).forEach(option => {
                            option.selected = values.includes(option.value);
                        });
                        break;
                    default:
                        if (element.value !== value) {
                            element.value = value;
                            element.dispatchEvent(new Event('change', { bubbles: true }));
                        }
                }
            }
        }
    }

    syncLink(link) {
        const paramsData = link.getAttribute('data-params');
        if (!paramsData) return;

        try {
            const params = JSON.parse(paramsData);
            let href = link.getAttribute('href') || '';
            const urlParts = href.split('?');
            const baseUrl = urlParts[0];
            const mergedParams = new URLSearchParams();

            if (urlParts[1]) {
                new URLSearchParams(urlParts[1]).forEach((value, key) => {
                    if (!this.shouldExcludeParam(key)) mergedParams.set(key, value);
                });
            }

            this.state.params.forEach((value, key) => {
                if (!params[key] && !this.shouldExcludeParam(key)) {
                    mergedParams.set(key, value);
                }
            });

            Object.entries(params).forEach(([key, value]) => {
                if (!this.shouldExcludeParam(key)) mergedParams.set(key, value);
            });

            const queryString = mergedParams.toString();
            const newHref = queryString ? `${baseUrl}?${queryString}` : baseUrl;

            if (href !== newHref) {
                link.setAttribute('href', newHref);
                link.setAttribute('data-params-synced', 'true');
            }
        } catch (error) {
            console.warn('Failed to sync link parameters:', error);
        }
    }

    handleFormSubmit(form) {
        const formData = new FormData(form);
        const newParams = new Map();

        for (const [key, value] of formData.entries()) {
            if (key && !this.shouldExcludeParam(key)) {
                newParams.set(key, value);
            }
        }

        this.updateParameters(newParams);

        if (form.hasAttribute('data-update-url')) this.updateURL();
    }

    handleLinkClick(link, event) {
        const updateOnly = link.hasAttribute('data-params-update-only');

        if (updateOnly) {
            event.preventDefault();
            const paramsData = link.getAttribute('data-params');

            if (paramsData) {
                try {
                    const params = JSON.parse(paramsData);
                    const newParams = new Map(Object.entries(params));
                    this.updateParameters(newParams, { updateURL: true });
                } catch (error) {
                    console.warn('Failed to parse link parameters:', error);
                }
            }
        }
    }

    updateParameters(newParams, options = {}) {
        const oldParams = new Map(this.state.params);

        if (options.replace) this.state.params.clear();

        newParams.forEach((value, key) => this.state.params.set(key, value));

        if (options.remove) {
            options.remove.forEach(key => this.state.params.delete(key));
        }

        if (!this.areMapsEqual(oldParams, this.state.params)) {
            this.syncForms();
            this.syncLinks();

            this.dispatchEvent('pages:parameters-changed', {
                params: this.getAllParameters(),
                oldParams: Object.fromEntries(oldParams),
                source: options.source || 'update',
                timestamp: Date.now()
            });

            if (options.updateURL !== false) this.updateURL(options);
            if (this.options.persistParams) this.saveParametersToStorage();

            this.log('Parameters updated:', Object.fromEntries(this.state.params));
        }
    }

    updateURL(options = {}) {
        const url = new URL(window.location.href);
        const paramsChanged = new Set();

        this.state.params.forEach((value, key) => paramsChanged.add(key));

        url.searchParams.forEach((value, key) => {
            if (!this.shouldExcludeParam(key) && !paramsChanged.has(key)) {
                url.searchParams.delete(key);
            }
        });

        this.state.params.forEach((value, key) => url.searchParams.set(key, value));

        const method = options.replace ? 'replaceState' : 'pushState';
        window.history[method]({}, '', url);

        this._handleURLChange(url.href, 'parameters');
        this.log('URL updated:', url.toString());
    }

    // Parameter API
    getParameter(key, defaultValue = null) {
        if (this.state.params.has(key)) return this.state.params.get(key);
        if (this.options.defaultValues[key] !== undefined) return this.options.defaultValues[key];
        return defaultValue;
    }

    setParameter(key, value, options = {}) {
        const newParams = new Map();
        newParams.set(key, value);
        this.updateParameters(newParams, options);
    }

    deleteParameter(key, options = {}) {
        this.updateParameters(new Map(), { ...options, remove: [key] });
    }

    getAllParameters() {
        return Object.fromEntries(this.state.params);
    }

    hasParameter(key) {
        return this.state.params.has(key);
    }

    clearParameters(options = {}) {
        this.state.params.clear();
        this.syncForms();
        this.syncLinks();

        this.dispatchEvent('pages:parameters-changed', {
            params: {},
            source: 'clear',
            timestamp: Date.now()
        });

        if (options.updateURL !== false) this.updateURL(options);
        if (this.options.persistParams) localStorage.removeItem(this.options.paramsStorageKey);

        this.log('Parameters cleared');
    }

    async loadParametersFromStorage() {
        try {
            const stored = localStorage.getItem(this.options.paramsStorageKey);
            if (stored) {
                const data = JSON.parse(stored);
                if (data.params && data.timestamp) {
                    const staleTime = 24 * 60 * 60 * 1000;
                    if (Date.now() - data.timestamp < staleTime) {
                        this.state.params = new Map(Object.entries(data.params || {}));
                        this.syncForms();
                        this.syncLinks();
                        this.log('Loaded parameters from storage');
                    } else {
                        localStorage.removeItem(this.options.paramsStorageKey);
                    }
                }
            }
        } catch (error) {
            console.warn('Failed to load parameters from storage:', error);
        }
    }

    saveParametersToStorage() {
        try {
            const data = {
                params: Object.fromEntries(this.state.params),
                timestamp: Date.now()
            };
            localStorage.setItem(this.options.paramsStorageKey, JSON.stringify(data));
        } catch (error) {
            console.warn('Failed to save parameters to storage:', error);
        }
    }

    areMapsEqual(map1, map2) {
        if (map1.size !== map2.size) return false;
        for (const [key, value] of map1) {
            if (value !== map2.get(key)) return false;
        }
        return true;
    }

    // Page Info
    async extractPageInfo() {
        const pageInfo = this.extractPageMetadata();

        if (!pageInfo.id) pageInfo.id = this.generatePageId(pageInfo);

        const pageChanged = !this.state.currentPage ||
            this.state.currentPage.id !== pageInfo.id ||
            this.state.currentPage.url !== pageInfo.url;

        if (pageChanged) {
            this.state.previousPage = this.state.currentPage;
            this.state.currentPage = pageInfo;

            this.addToPageHistory(pageInfo);

            if (this.options.watchMetaChanges || this.options.watchTitleChanges) {
                this.setupPageObservers();
            }

            this.dispatchEvent('pages:page-info-extracted', {
                previousPage: this.state.previousPage,
                currentPage: this.state.currentPage,
                pageChanged,
                timestamp: Date.now()
            });

            if (this.options.persistState) this.saveState();
        }

        return pageInfo;
    }

    extractPageMetadata() {
        const url = this.state.currentUrl;
        const urlObj = new URL(url);

        const data = {
            id: document.documentElement.getAttribute('data-page'),
            url: urlObj.href.split('?')[0],
            path: urlObj.pathname,
            hash: urlObj.hash,
            search: urlObj.search,
            title: document.title,
            timestamp: Date.now(),
            meta: {}
        };

        const standardMeta = [
            'description', 'keywords', 'author', 'viewport',
            'robots', 'og:title', 'og:description', 'og:image',
            'twitter:title', 'twitter:description', 'twitter:image'
        ];

        standardMeta.forEach(name => {
            const element = document.querySelector(`meta[name="${name}"], meta[property="${name}"]`);
            if (element) data.meta[name] = element.getAttribute('content');
        });

        const pageMetaTags = document.querySelectorAll('meta[name^="page:"]');
        pageMetaTags.forEach(tag => {
            const name = tag.getAttribute('name').replace('page:', '');
            data.meta[name] = tag.getAttribute('content');
        });

        const pageElement = DOM.$('[data-page-data]');
        if (pageElement) {
            try {
                const pageData = JSON.parse(DOM.attr(pageElement, 'data-page-data') || '{}');
                Object.assign(data, pageData);
            } catch (error) {
                console.warn('Failed to parse page data:', error);
            }
        }

        const structuredData = this.extractStructuredData();
        if (structuredData) data.structuredData = structuredData;

        return data;
    }

    extractStructuredData() {
        const scripts = document.querySelectorAll('script[type="application/ld+json"]');
        if (scripts.length === 0) return null;

        try {
            const structuredData = [];
            scripts.forEach(script => {
                const content = script.textContent.trim();
                if (content) structuredData.push(JSON.parse(content));
            });
            return structuredData.length > 0 ? structuredData : null;
        } catch (error) {
            console.warn('Failed to parse structured data:', error);
            return null;
        }
    }

    generatePageId(pageData) {
        const base = pageData.path
            .replace(/\//g, '_')
            .replace(/[^\w-]/g, '')
            .replace(/^_+|_+$/g, '') || 'home';

        const hash = pageData.hash ? '_' + pageData.hash.replace('#', '') : '';
        return base + hash;
    }

    setupPageObservers() {
        const pageObservers = this.state.observers.filter(obs =>
            obs._type === 'page' || (obs.observer && obs._type === 'page')
        );

        pageObservers.forEach(obs => {
            if (obs.disconnect) obs.disconnect();
            else if (obs.observer) obs.observer.disconnect();
        });

        this.state.observers = this.state.observers.filter(obs =>
            !(obs._type === 'page' || (obs.observer && obs._type === 'page'))
        );

        if (this.options.watchTitleChanges) {
            const titleObserver = new MutationObserver(() => this.handleTitleChange());
            const titleElement = document.querySelector('title');
            if (titleElement) {
                titleObserver.observe(titleElement, { childList: true, subtree: true });
                titleObserver._type = 'page';
                this.state.observers.push(titleObserver);
            }
        }

        if (this.options.watchMetaChanges) {
            const metaObserver = new MutationObserver((mutations) => {
                let shouldUpdate = false;
                mutations.forEach((mutation) => {
                    if (mutation.type === 'attributes') {
                        const attrName = mutation.attributeName;
                        if (attrName === 'content' || attrName === 'name' || attrName === 'property') {
                            shouldUpdate = true;
                        }
                    }
                });
                if (shouldUpdate) this.handleMetaChange();
            });

            const headElement = document.head;
            if (headElement) {
                metaObserver.observe(headElement, {
                    attributes: true,
                    attributeFilter: ['content', 'name', 'property'],
                    subtree: true
                });
                metaObserver._type = 'page';
                this.state.observers.push(metaObserver);
            }
        }
    }

    handleTitleChange() {
        this.dispatchEvent('pages:title-changed', {
            previousTitle: this.state.currentPage?.title,
            currentTitle: document.title,
            timestamp: Date.now()
        });

        if (this.state.currentPage && this.state.currentPage.title !== document.title) {
            this.extractPageInfo();
        }
    }

    handleMetaChange() {
        this.dispatchEvent('pages:meta-changed', { timestamp: Date.now() });
        this.extractPageInfo();
    }

    addToPageHistory(pageInfo) {
        this.state.pageHistory.unshift({ ...pageInfo });
        if (this.state.pageHistory.length > this.options.maxHistory) {
            this.state.pageHistory.pop();
        }
    }

    // State Management
    async saveState() {
        try {
            const state = {
                urlHistory: this.state.urlHistory.slice(0, 10),
                pageHistory: this.state.pageHistory.slice(0, 10),
                currentPage: this.state.currentPage,
                params: Object.fromEntries(this.state.params),
                timestamp: Date.now()
            };
            localStorage.setItem(this.options.storageKey, JSON.stringify(state));
        } catch (error) {
            console.warn('Failed to save pages manager state:', error);
        }
    }

    async loadState() {
        try {
            const saved = localStorage.getItem(this.options.storageKey);
            if (saved) {
                const state = JSON.parse(saved);
                this.state.urlHistory = state.urlHistory || [];
                this.state.pageHistory = state.pageHistory || [];
                this.state.currentPage = state.currentPage || null;

                if (state.params) {
                    this.state.params = new Map(Object.entries(state.params));
                }
            }
        } catch (error) {
            console.warn('Failed to load pages manager state:', error);
        }
    }

    // Public API
    getCurrentUrl() { return this.state.currentUrl; }
    getCurrentPath() { return this.state.currentPath; }
    getCurrentHash() { return this.state.currentHash; }
    getUrlHistory(limit = 10) { return this.state.urlHistory.slice(0, limit); }
    getCurrentPage() { return this.state.currentPage; }
    getPreviousPage() { return this.state.previousPage; }
    getPageHistory(limit = 10) { return this.state.pageHistory.slice(0, limit); }
    getMetaValue(key) { return this.state.currentPage?.meta?.[key] || null; }

    navigateTo(url, options = {}) {
        const { replace = false, state = {}, title = '' } = options;
        try {
            if (replace) {
                window.history.replaceState(state, title, url);
            } else {
                window.history.pushState(state, title, url);
            }
            this._handleURLChange(url, 'programmatic');
            return true;
        } catch (error) {
            console.error('Navigation failed:', error);
            return false;
        }
    }

    goBack() {
        if (this.state.urlHistory.length > 1) {
            const previous = this.state.urlHistory[1];
            if (previous && previous.currentUrl) {
                window.history.back();
                return true;
            }
        }
        return false;
    }

    refresh() {
        this._handleURLChange(window.location.href, 'refresh');
    }

    getState() {
        return {
            currentUrl: this.state.currentUrl,
            currentPath: this.state.currentPath,
            currentHash: this.state.currentHash,
            currentSearch: this.state.currentSearch,
            previousUrl: this.state.previousUrl,
            urlHistory: [...this.state.urlHistory],
            currentPage: this.state.currentPage,
            previousPage: this.state.previousPage,
            pageHistory: [...this.state.pageHistory],
            params: this.getAllParameters(),
            initialized: this.state.initialized
        };
    }

    // Event System
    dispatchEvent(eventName, detail = {}) {
        const event = new CustomEvent(eventName, {
            detail: { ...detail, manager: this },
            bubbles: true,
            cancelable: true
        });
        document.dispatchEvent(event);
    }

    on(event, callback) {
        const handler = (e) => {
            if (e.detail && e.detail.manager === this) callback(e.detail);
        };
        this.handlers.set(callback, handler);
        document.addEventListener(event, handler);
        return this;
    }

    off(event, callback) {
        const handler = this.handlers.get(callback);
        if (handler) {
            document.removeEventListener(event, handler);
            this.handlers.delete(callback);
        }
        return this;
    }

    // Cleanup
    destroy() {
        this.state.observers.forEach(observer => {
            if (observer.disconnect) observer.disconnect();
            else if (observer.observer) observer.observer.disconnect();
        });
        this.state.observers = [];

        this.cleanupFns.forEach(cleanup => cleanup());
        this.cleanupFns = [];
        this.handlers.clear();

        if (this.originalPushState) history.pushState = this.originalPushState;
        if (this.originalReplaceState) history.replaceState = this.originalReplaceState;

        this.state.formElements.clear();
        this.state.linkElements.clear();
        this.state.params.clear();
        this.state.urlHistory = [];
        this.state.pageHistory = [];
        this.state.currentPage = null;
        this.state.previousPage = null;
        this.state.initialized = false;

        this.dispatchEvent('pages:destroyed');
        this.log('Pages Manager destroyed');
    }
}

// ============================================================================
// PART 2: BASE LAYOUT
// Core layout functionality with notification and navigation integration
// ============================================================================

export class BaseLayout {
    constructor(options = {}) {
        this.options = {
            layoutId: 'base',
            layoutType: 'unknown',
            pageId: 'unknown',
            pageType: 'unknown',
            subType: null,
            debug: false,
            autoInit: true,
            enableNotifications: true,
            notification: null,
            notificationConfig: {
                position: 'top-right',
                maxNotifications: 5,
                duration: 5000,
                ...options.notificationConfig
            },
            navigation: options.navigation || null,
            trackNavigation: true,
            updateNavigation: true,
            headerMenu: options.headerMenu || null,
            enableHeader: true,
            components: new Map(),
            autoDestroyComponents: true,
            emitEvents: true,
            ...options
        };

        this.navigation = this.options.navigation;
        this.headerMenu = this.options.headerMenu;
        this.notification = this.options.notification;
        this.notificationSystem = null;
        this.initialized = false;
        this.destroyed = false;
        this.components = new Map();
        this.eventHandlers = new Map();
        this.cleanupFunctions = [];
        this.metrics = { initTime: 0, applyTime: 0, componentCount: 0, lastUpdate: 0 };

        this.log(`📐 ${this.options.layoutType} layout created`);
    }

    async init() {
        if (this.initialized || this.destroyed) return this;

        const startTime = performance.now();

        try {
            await this.initCoreSystems();
            if (this.options.enableNotifications) await this.initNotificationSystem();
            await this.setupEventSystem();
            await this.initComponents();

            this.initialized = true;
            this.metrics.initTime = performance.now() - startTime;

            this.log(`✅ Layout initialized in ${this.metrics.initTime.toFixed(2)}ms`);

            this.dispatchEvent('layout:initialized', {
                layoutType: this.options.layoutType,
                pageType: this.options.pageType,
                subType: this.options.subType,
                metrics: this.metrics
            });

        } catch (error) {
            console.error(`Failed to initialize ${this.options.layoutType} layout:`, error);
            this.handleError(error, 'layout-init');
            throw error;
        }

        return this;
    }

    async initCoreSystems() {
        if (this.navigation && !this.navigation.initialized) {
            try {
                await this.navigation.init();
                this.log('🧭 Navigation system initialized');
            } catch (error) {
                console.warn('Failed to initialize navigation:', error);
            }
        }

        if (this.headerMenu && !this.headerMenu.initialized) {
            try {
                await this.headerMenu.init();
                this.log('🍔 Header menu initialized');
            } catch (error) {
                console.warn('Failed to initialize header menu:', error);
            }
        }

        this.setupErrorHandling();
    }

    async initNotificationSystem() {
        if (this.notification) {
            this.notificationSystem = this.notification;
            return;
        }
        if (window.notificationSystem) {
            this.notificationSystem = window.notificationSystem;
            return;
        }
        if (window.layoutManager?.notification) {
            this.notificationSystem = window.layoutManager.notification;
            return;
        }
        this.notificationSystem = this.createFallbackNotificationSystem();
    }

    createFallbackNotificationSystem() {
        return {
            show: (message, options = {}) => {
                const type = options.type || 'info';
                console.log(`[${type.toUpperCase()}] ${message}`);
            },
            success: (message) => { this.showNotification(message, 'success'); return true; },
            error: (message) => { this.showNotification(message, 'error'); return false; },
            warning: (message) => { this.showNotification(message, 'warning'); return false; },
            info: (message) => { this.showNotification(message, 'info'); return false; },
            on: () => { },
            off: () => { },
            use: () => { }
        };
    }

    async setupEventSystem() {
        this.setupGlobalEvents();
        this.setupLayoutEvents();
        this.setupKeyboardShortcuts();
    }

    setupErrorHandling() {
        window.addEventListener('error', (event) => {
            if (event.target && event.target.baseURI === window.location.href) {
                this.handleError(event.error || event, 'window-error');
            }
        });

        window.addEventListener('unhandledrejection', (event) => {
            this.handleError(event.reason, 'unhandled-rejection');
        });
    }

    showNotification(message, type = 'info', options = {}) {
        if (this.notificationSystem && this.notificationSystem.show) {
            return this.notificationSystem.show(message, { type, ...options });
        }
        console.log(`[${type.toUpperCase()}] ${message}`);
        this.showToast(message, type);
        return null;
    }

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `layout-toast toast-${type}`;
        toast.style.cssText = `
            position: fixed; top: 20px; right: 20px; padding: 12px 24px;
            border-radius: 4px; color: white; font-weight: 500; z-index: 9999;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15); animation: slideIn 0.3s ease;
        `;

        const typeStyles = {
            success: 'background: #10b981;',
            error: 'background: #ef4444;',
            warning: 'background: #f59e0b;',
            info: 'background: #3b82f6;'
        };

        toast.style.cssText += typeStyles[type] || typeStyles.info;
        toast.textContent = message;
        document.body.appendChild(toast);

        setTimeout(() => {
            if (toast.parentNode) {
                toast.style.animation = 'slideOut 0.3s ease';
                setTimeout(() => toast.parentNode?.removeChild(toast), 300);
            }
        }, 5000);

        if (!document.querySelector('#toast-animations')) {
            const style = document.createElement('style');
            style.id = 'toast-animations';
            style.textContent = `
                @keyframes slideIn { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
                @keyframes slideOut { from { transform: translateX(0); opacity: 1; } to { transform: translateX(100%); opacity: 0; } }
            `;
            document.head.appendChild(style);
        }
    }

    showSuccess(message) { return this.showNotification(message, 'success'); }
    showError(message) { return this.showNotification(message, 'error'); }
    showWarning(message) { return this.showNotification(message, 'warning'); }
    showInfo(message) { return this.showNotification(message, 'info'); }

    async apply(layoutType, layoutData = {}) {
        if (!this.initialized) await this.init();

        const startTime = performance.now();
        this.log(`Applying layout: ${layoutType}`);

        this.options.layoutType = layoutType;
        this.options.pageType = layoutData.pageType || layoutType;
        this.options.subType = layoutData.subType || null;

        this.layoutData = {
            type: layoutType,
            pageType: this.options.pageType,
            subType: this.options.subType,
            data: layoutData,
            timestamp: Date.now(),
            ...layoutData
        };

        try {
            this.updateLayoutClasses();
            this.applyDataAttributes();

            if (this.navigation && this.options.updateNavigation) this.updateNavigationState();
            if (this.headerMenu && this.options.enableHeader) this.updateHeaderMenu();

            await this.applyContent();
            await this.applyComponents();

            this.metrics.applyTime = performance.now() - startTime;
            this.metrics.lastUpdate = Date.now();

            this.log(`✅ Layout applied in ${this.metrics.applyTime.toFixed(2)}ms`);

            this.dispatchEvent('layout:applied', {
                layoutType,
                pageType: this.options.pageType,
                subType: this.options.subType,
                layoutData: this.layoutData,
                metrics: this.metrics
            });

        } catch (error) {
            this.handleError(error, 'layout-apply');
        }

        return this;
    }

    async destroy() {
        if (this.destroyed) return;

        this.log('🗑️ Destroying layout...');

        try {
            if (this.options.autoDestroyComponents) await this.destroyComponents();
            this.cleanupEventListeners();
            this.removeLayoutClasses();
            this.removeDataAttributes();

            this.destroyed = true;
            this.initialized = false;

            this.dispatchEvent('layout:destroyed', {
                layoutType: this.options.layoutType,
                metrics: this.metrics
            });

            this.log('✅ Layout destroyed');

        } catch (error) {
            this.handleError(error, 'layout-destroy');
        }
    }

    async initComponents() { }
    async applyContent() { }

    async applyComponents() {
        for (const [name, component] of this.components) {
            if (component && typeof component.init === 'function') {
                try {
                    await component.init();
                    this.log(`Component initialized: ${name}`);
                } catch (error) {
                    // console.error(`Failed to initialize component ${name}:`, error);
                }
            }
        }
    }

    async destroyComponents() {
        for (const [name, component] of this.components) {
            if (component && typeof component.destroy === 'function') {
                try {
                    await component.destroy();
                } catch (error) {
                    console.error(`Failed to destroy component ${name}:`, error);
                }
            }
        }
        this.components.clear();
    }

    registerComponent(name, component) {
        this.components.set(name, component);
        this.metrics.componentCount = this.components.size;
        return this;
    }

    getComponent(name) { return this.components.get(name); }

    onNavigationEvent(event, handler) {
        if (!this.navigation) return () => { };
        return this.navigation.on(event, (data) => handler.call(this, data));
    }

    updateNavigationState() {
        if (!this.navigation) return;
        this.log('🧭 Navigation state updated');
    }

    updateHeaderMenu() { }

    updateLayoutClasses() {
        const layoutClasses = Array.from(document.body.classList)
            .filter(c => c.startsWith('layout-') || c.startsWith('page-'));
        document.body.classList.remove(...layoutClasses);

        document.body.classList.add(`layout-${this.options.layoutType}`);
        if (this.options.pageType) document.body.classList.add(`page-${this.options.pageType}`);
        if (this.options.subType) document.body.classList.add(`page-${this.options.layoutType}-${this.options.subType}`);
    }

    removeLayoutClasses() {
        document.body.classList.remove(
            `layout-${this.options.layoutType}`,
            `page-${this.options.pageType}`
        );
        if (this.options.subType) {
            document.body.classList.remove(`page-${this.options.layoutType}-${this.options.subType}`);
        }
    }

    applyDataAttributes() {
        document.body.setAttribute('data-layout', this.options.layoutType);
        document.body.setAttribute('data-page-type', this.options.pageType);
        if (this.options.subType) document.body.setAttribute('data-sub-type', this.options.subType);
        if (this.layoutData?.timestamp) document.body.setAttribute('data-layout-loaded', this.layoutData.timestamp);
    }

    removeDataAttributes() {
        document.body.removeAttribute('data-layout');
        document.body.removeAttribute('data-page-type');
        document.body.removeAttribute('data-sub-type');
        document.body.removeAttribute('data-layout-loaded');
    }

    setupGlobalEvents() {
        const clickHandler = (e) => this.handleGlobalClick(e);
        document.addEventListener('click', clickHandler);
        this.cleanupFunctions.push(() => document.removeEventListener('click', clickHandler));

        const keydownHandler = (e) => this.handleGlobalKeydown(e);
        document.addEventListener('keydown', keydownHandler);
        this.cleanupFunctions.push(() => document.removeEventListener('keydown', keydownHandler));

        const resizeHandler = () => this.handleResize();
        window.addEventListener('resize', resizeHandler);
        this.cleanupFunctions.push(() => window.removeEventListener('resize', resizeHandler));
    }

    setupLayoutEvents() { }

    setupKeyboardShortcuts() {
        this.keyboardShortcuts = {
            'Escape': () => this.handleEscapeKey(),
            'F5': (e) => { e.preventDefault(); this.refresh(); },
            'r': (e) => { if (e.ctrlKey) { e.preventDefault(); this.refresh(); } }
        };
    }

    handleGlobalClick(event) { }

    handleGlobalKeydown(event) {
        const shortcut = this.keyboardShortcuts?.[event.key];
        if (shortcut) shortcut(event);
    }

    handleEscapeKey() { this.dispatchEvent('layout:escape-pressed'); }

    handleResize() {
        this.dispatchEvent('layout:resized', { width: window.innerWidth, height: window.innerHeight });
    }

    on(event, handler) {
        if (!this.eventHandlers.has(event)) this.eventHandlers.set(event, []);
        this.eventHandlers.get(event).push(handler);

        const domHandler = (e) => {
            if (e.detail?.layout === this) handler(e.detail);
        };
        document.addEventListener(event, domHandler);
        this.cleanupFunctions.push(() => document.removeEventListener(event, domHandler));

        return () => this.off(event, handler);
    }

    off(event, handler) {
        if (!this.eventHandlers.has(event)) return;
        const handlers = this.eventHandlers.get(event);
        const index = handlers.indexOf(handler);
        if (index > -1) handlers.splice(index, 1);
    }

    dispatchEvent(eventName, detail = {}) {
        if (!this.options.emitEvents) return;

        const event = new CustomEvent(eventName, {
            detail: {
                ...detail,
                layout: this,
                layoutType: this.options.layoutType,
                pageType: this.options.pageType,
                timestamp: Date.now()
            },
            bubbles: true,
            cancelable: true
        });

        document.dispatchEvent(event);
    }

    log(...args) {
        if (this.options.debug) console.log(`[${this.options.layoutType}]`, ...args);
    }

    handleError(error, context = 'unknown') {
        console.error(`[${this.options.layoutType}] Error in ${context}:`, error);

        this.dispatchEvent('layout:error', {
            error: error.message || error,
            context,
            stack: error.stack
        });

        this.showError(error.message || 'An error occurred');
    }

    cleanupEventListeners() {
        this.cleanupFunctions.forEach(fn => fn());
        this.cleanupFunctions = [];
        this.eventHandlers.clear();
    }

    getState() {
        return {
            layoutType: this.options.layoutType,
            pageType: this.options.pageType,
            subType: this.options.subType,
            initialized: this.initialized,
            destroyed: this.destroyed,
            components: Array.from(this.components.keys()),
            metrics: this.metrics,
            notificationSystem: !!this.notificationSystem
        };
    }

    async refresh() {
        this.log('Refreshing layout...');
        await this.destroyComponents();
        await this.initComponents();
        await this.applyContent();
        this.dispatchEvent('layout:refreshed', { timestamp: Date.now() });
        return this;
    }
}

// ============================================================================
// PART 3: LAYOUT MANAGER
// Layout detection and auto-initialization
// ============================================================================

export class LayoutManager extends BaseManager {
    constructor(config = {}) {
        super({
            layouts: config.layouts || {},
            defaultLayout: config.defaultLayout || 'default',
            autoDetect: config.autoDetect !== false,
            layoutOptions: {
                applyClasses: true,
                bodyClassPrefix: 'layout-',
                pageClassPrefix: 'page-',
                ...config.layoutOptions
            },
            cacheLayouts: true,
            lazyLoad: true,
            ...config
        });

        this.currentLayout = null;
        this.layoutInstances = new Map();
        this.layoutClasses = new Map();
        this.pageData = {};
    }

    async initialize(app) {
        if (this.initialized) return this;

        this.startLoading();
        this.log('🏗️ Initializing Layout Manager...');

        try {
            this.app = app;

            if (this.config.autoDetect) {
                await this.detectLayout();
            } else {
                this.currentLayout = this.config.defaultLayout;
            }

            if (this.currentLayout) {
                await this.loadLayout(this.currentLayout);
            }

            this.initialized = true;
            this.log(`✅ Layout Manager initialized with "${this.currentLayout}" layout`);

            this.dispatch('initialized', {
                layout: this.currentLayout,
                layoutInstance: this.getLayoutInstance(),
                metrics: this.getMetrics()
            });

        } catch (error) {
            this.handleError(error, 'init');
        } finally {
            this.stopLoading();
        }

        return this;
    }

    async detectLayout() {
        let detectedLayout = this.config.defaultLayout;

        const layoutAttr = document.body.getAttribute('data-layout');
        if (layoutAttr) {
            this.currentLayout = layoutAttr;
            this.log(`Detected layout (attribute): ${layoutAttr}`);
            return layoutAttr;
        }

        const path = window.location.pathname;
        if (path.includes('/profile') || path.includes('/user')) {
            detectedLayout = 'profile';
        } else if (path.includes('/app') || path.includes('/dashboard')) {
            detectedLayout = 'app';
        } else if (path.includes('/blog') || path.includes('/article')) {
            detectedLayout = 'blog';
        } else if (path.includes('/portfolio') || path.includes('/project')) {
            detectedLayout = 'portfolio';
        } else if (path.includes('/admin')) {
            detectedLayout = 'admin';
        } else if (path === '/' || path === '/index.html') {
            detectedLayout = 'home';
        }

        if (this.pageData.layout) detectedLayout = this.pageData.layout;

        const bodyClasses = Array.from(document.body.classList);
        const layoutClass = bodyClasses.find(cls => cls.startsWith('layout-'));
        if (layoutClass) detectedLayout = layoutClass.replace('layout-', '');

        this.currentLayout = detectedLayout;
        this.log(`Detected layout: ${detectedLayout}`);

        return detectedLayout;
    }

    async loadLayout(layoutName) {
        if (this.layoutInstances.has(layoutName)) {
            this.log(`🔄 Loading layout "${layoutName}" from cache`);
            const instance = this.layoutInstances.get(layoutName);
            if (typeof instance.apply === 'function') await instance.apply(layoutName);
            return instance;
        }

        try {
            this.log(`📥 Loading layout: ${layoutName}...`);

            let LayoutClass;

            if (layoutName === 'profile') {
                const module = await import('./profile.layout.js');
                LayoutClass = module.ProfileLayout || module.default;
            } else if (layoutName === 'app' || layoutName === 'dashboard') {
                const module = await import('./app.layout.js');
                LayoutClass = module.AppLayout || module.default;
            } else {
                try {
                    const layoutConfig = this.config.layouts[layoutName] || `./${layoutName}.layout.js`;
                    const layoutModule = await import(layoutConfig);
                    LayoutClass = layoutModule.default || layoutModule.Layout;
                } catch (e) {
                    console.warn(`Could not load specific layout file for ${layoutName}, falling back to BaseLayout`);
                    LayoutClass = BaseLayout;
                }
            }

            if (!LayoutClass) throw new Error(`Layout class not found for: ${layoutName}`);

            const layoutInstance = new LayoutClass({
                name: layoutName,
                manager: this,
                config: this.config,
                debug: document.body.hasAttribute('data-debug') || false,
                enableNavigation: true,
                enableHeader: true,
                enableSidebar: true
            });

            if (typeof layoutInstance.init === 'function') await layoutInstance.init();
            if (typeof layoutInstance.apply === 'function') await layoutInstance.apply(layoutName);

            this.layoutInstances.set(layoutName, layoutInstance);

            if (this.config.layoutOptions.applyClasses) this.applyLayoutClasses(layoutName);

            this.log(`✅ Layout "${layoutName}" loaded and initialized`);

            window.currentLayout = layoutInstance;
            if (layoutName === 'profile') window.profileLayout = layoutInstance;
            if (layoutName === 'app') window.appLayout = layoutInstance;

            return layoutInstance;

        } catch (error) {
            this.handleError(error, `load-layout-${layoutName}`);

            if (layoutName !== this.config.defaultLayout) {
                this.log(`⚠️ Falling back to default layout`);
                return this.loadLayout(this.config.defaultLayout);
            }

            return null;
        }
    }

    async switchLayout(layoutName, pageData = {}) {
        if (layoutName === this.currentLayout) {
            this.log(`Already on layout "${layoutName}"`);
            return this.getLayoutInstance();
        }

        this.log(`🔄 Switching layout: ${this.currentLayout} → ${layoutName}`);

        try {
            await this.unloadLayout(this.currentLayout);
            this.pageData = { ...this.pageData, ...pageData };
            const layoutInstance = await this.loadLayout(layoutName);
            this.currentLayout = layoutName;

            this.dispatch('layout:changed', {
                previous: this.currentLayout,
                current: layoutName,
                layoutInstance,
                pageData: this.pageData
            });

            this.log(`✅ Switched to layout "${layoutName}"`);
            return layoutInstance;

        } catch (error) {
            this.handleError(error, `switch-layout-${layoutName}`);
            return null;
        }
    }

    async unloadLayout(layoutName) {
        const layoutInstance = this.layoutInstances.get(layoutName);

        if (layoutInstance && typeof layoutInstance.destroy === 'function') {
            try {
                await layoutInstance.destroy();
                this.log(`🗑️ Unloaded layout: ${layoutName}`);
            } catch (error) {
                this.log(`Error unloading layout ${layoutName}:`, error);
            }
        }

        if (this.layoutClasses.has(layoutName)) {
            const classes = this.layoutClasses.get(layoutName);
            classes.forEach(className => document.body.classList.remove(className));
            this.layoutClasses.delete(layoutName);
        }
    }

    applyLayoutClasses(layoutName) {
        this.layoutClasses.forEach(classes => {
            classes.forEach(className => document.body.classList.remove(className));
        });
        this.layoutClasses.clear();

        const classes = [];

        if (this.config.layoutOptions.bodyClassPrefix) {
            const layoutClass = `${this.config.layoutOptions.bodyClassPrefix}${layoutName}`;
            document.body.classList.add(layoutClass);
            classes.push(layoutClass);
        }

        if (this.pageData.type && this.config.layoutOptions.pageClassPrefix) {
            const pageClass = `${this.config.layoutOptions.pageClassPrefix}${this.pageData.type}`;
            document.body.classList.add(pageClass);
            classes.push(pageClass);
        }

        this.layoutClasses.set(layoutName, classes);
    }

    getCurrentLayout() { return this.currentLayout; }
    getLayoutInstance() { return this.layoutInstances.get(this.currentLayout); }
    getLayout(layoutName) { return this.layoutInstances.get(layoutName); }
    hasLayout(layoutName) { return this.layoutInstances.has(layoutName) || this.config.layouts.hasOwnProperty(layoutName); }

    registerLayout(layoutName, layoutClass) {
        this.layoutInstances.set(layoutName, layoutClass);
        this.log(`✅ Layout registered: ${layoutName}`);
        return this;
    }

    updatePageData(pageData) {
        this.pageData = { ...this.pageData, ...pageData };
        this.dispatch('page:data:updated', { pageData: this.pageData });
        return this;
    }

    async destroy() {
        await super.destroy();

        const unloadPromises = Array.from(this.layoutInstances.keys()).map(
            layoutName => this.unloadLayout(layoutName)
        );

        await Promise.allSettled(unloadPromises);
        this.layoutInstances.clear();
        this.layoutClasses.clear();

        this.currentLayout = null;
        this.pageData = {};

        this.log('✅ Layout Manager destroyed');
    }
}

// ============================================================================
// EXPORTS & AUTO-INITIALIZATION
// ============================================================================

// Singleton instances
export const pagesManager = new PagesManager();
export const layoutManager = new LayoutManager();

// Auto-initialize on DOM ready
if (typeof document !== 'undefined') {
    const initAll = async () => {
        try {
            await pagesManager.initialize();
            await layoutManager.initialize(window.App);
        } catch (error) {
            console.error('Failed to initialize page/layout managers:', error);
        }
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => setTimeout(initAll, 50));
    } else {
        setTimeout(initAll, 50);
    }
}

export default BaseLayout;
