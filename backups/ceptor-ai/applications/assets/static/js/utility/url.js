/**
 * URL Tracker Mixin - Tracks URL changes and navigation events
 * Can be mixed into any class that needs URL tracking capabilities
 */

import { debounce } from './helpers.js';

export const URLTrackerMixin = (BaseClass) => class extends BaseClass {
    constructor(options = {}) {
        super(options);

        this.urlState = {
            currentPath: window.location.pathname,
            currentHash: window.location.hash,
            currentUrl: window.location.href,
            previousUrl: null,
            previousPath: null,
            previousHash: null,
            historyState: window.history.state,
            referrer: document.referrer,
            timestamp: Date.now()
        };

        this.urlEvents = new Map();
        this.urlListeners = new Map();
        this.isURLTracking = false;
        this.pendingUpdates = new Set();

        // URL change detection methods
        this.urlDetectionMethods = {
            history: true,
            hash: true,
            popstate: true,
            htmx: typeof htmx !== 'undefined',
            fetch: typeof fetch !== 'undefined'
        };

        // Performance tracking
        this.metrics = {
            urlChanges: 0,
            lastChange: null,
            averageUpdateTime: 0
        };
    }

    /**
     * Initialize URL tracking
     */
    initURLTracking(options = {}) {
        if (this.isURLTracking) return;

        // Merge options
        Object.assign(this.urlDetectionMethods, options);

        // Setup all listeners
        this.setupHistoryTracking();
        this.setupHashTracking();
        this.setupPopStateTracking();

        if (this.urlDetectionMethods.htmx) {
            this.setupHTMXTracking();
        }

        if (this.urlDetectionMethods.fetch) {
            this.setupFetchTracking();
        }

        this.setupPerformanceTracking();

        this.isURLTracking = true;

        this.log('URL tracking initialized', {
            methods: Object.keys(this.urlDetectionMethods).filter(k => this.urlDetectionMethods[k]),
            initialUrl: this.urlState.currentUrl
        });

        return this;
    }

    /**
     * Setup History API tracking
     */
    setupHistoryTracking() {
        const originalPushState = history.pushState;
        const originalReplaceState = history.replaceState;

        // Track pushState
        history.pushState = (...args) => {
            this.urlState.previousUrl = this.urlState.currentUrl;
            this.urlState.previousPath = this.urlState.currentPath;
            this.urlState.previousHash = this.urlState.currentHash;

            const result = originalPushState.apply(history, args);

            this.updateURLState();
            this.handleURLChange('pushState', args);

            return result;
        };

        // Track replaceState
        history.replaceState = (...args) => {
            this.urlState.previousUrl = this.urlState.currentUrl;
            this.urlState.previousPath = this.urlState.currentPath;
            this.urlState.previousHash = this.urlState.currentHash;

            const result = originalReplaceState.apply(history, args);

            this.updateURLState();
            this.handleURLChange('replaceState', args);

            return result;
        };

        this.urlListeners.set('history', { originalPushState, originalReplaceState });
    }

    /**
     * Setup hash change tracking
     */
    setupHashTracking() {
        const hashHandler = debounce((event) => {
            this.handleHashChange(event);
        }, 50);

        window.addEventListener('hashchange', hashHandler);
        this.urlListeners.set('hashchange', hashHandler);
    }

    /**
     * Setup popstate tracking
     */
    setupPopStateTracking() {
        const popStateHandler = (event) => {
            this.handlePopState(event);
        };

        window.addEventListener('popstate', popStateHandler);
        this.urlListeners.set('popstate', popStateHandler);
    }

    /**
     * Setup HTMX tracking
     */
    setupHTMXTracking() {
        const htmxEvents = [
            'htmx:beforeSwap',
            'htmx:afterSwap',
            'htmx:historyRestore',
            'htmx:beforeHistoryUpdate'
        ];

        htmxEvents.forEach(eventName => {
            const handler = (event) => {
                this.handleHTMXEvent(eventName, event);
            };
            document.addEventListener(eventName, handler);
            this.urlListeners.set(`htmx:${eventName}`, handler);
        });
    }

    /**
     * Setup fetch tracking
     */
    setupFetchTracking() {
        const originalFetch = window.fetch;

        window.fetch = async (...args) => {
            const startTime = performance.now();
            const url = typeof args[0] === 'string' ? args[0] : args[0]?.url;

            try {
                const response = await originalFetch(...args);
                const endTime = performance.now();

                if (url && url.startsWith(window.location.origin)) {
                    this.trackFetch(url, endTime - startTime, response.status);
                }

                return response;
            } catch (error) {
                this.trackFetchError(url, error);
                throw error;
            }
        };

        this.urlListeners.set('fetch', originalFetch);
    }

    /**
     * Setup performance tracking
     */
    setupPerformanceTracking() {
        // Track navigation timing
        if (window.performance?.getEntriesByType) {
            const navEntries = performance.getEntriesByType('navigation');
            if (navEntries.length > 0) {
                const nav = navEntries[0];
                this.metrics.pageLoadTime = nav.loadEventEnd - nav.startTime;
                this.metrics.domContentLoaded = nav.domContentLoadedEventEnd - nav.startTime;
            }
        }
    }

    /**
     * Handle popstate event
     */
    handlePopState(event) {
        const startTime = performance.now();

        this.updateURLState();

        this.dispatchURLEvent('url:popstate', {
            state: event.state,
            previousUrl: this.urlState.previousUrl,
            currentUrl: this.urlState.currentUrl,
            previousPath: this.urlState.previousPath,
            currentPath: this.urlState.currentPath
        });

        this.updateMetrics(performance.now() - startTime);
    }

    /**
     * Handle hash change
     */
    handleHashChange(event) {
        const startTime = performance.now();

        this.urlState.previousHash = this.urlState.currentHash;
        this.urlState.currentHash = window.location.hash;

        this.dispatchURLEvent('url:hashchange', {
            oldURL: event.oldURL,
            newURL: event.newURL,
            oldHash: new URL(event.oldURL).hash,
            newHash: new URL(event.newURL).hash,
            previousHash: this.urlState.previousHash,
            currentHash: this.urlState.currentHash
        });

        this.updateMetrics(performance.now() - startTime);
    }

    /**
     * Handle URL change from History API
     */
    handleURLChange(source, args) {
        const startTime = performance.now();

        this.dispatchURLEvent('url:changed', {
            source,
            args,
            previousUrl: this.urlState.previousUrl,
            currentUrl: this.urlState.currentUrl,
            previousPath: this.urlState.previousPath,
            currentPath: this.urlState.currentPath,
            previousHash: this.urlState.previousHash,
            currentHash: this.urlState.currentHash,
            timestamp: this.urlState.timestamp
        });

        this.updateMetrics(performance.now() - startTime);
    }

    /**
     * Handle HTMX events
     */
    handleHTMXEvent(eventName, event) {
        const url = event.detail?.requestConfig?.url ||
            event.detail?.target?.getAttribute?.('hx-get') ||
            event.detail?.path || window.location.href;

        this.updateURLState();

        this.dispatchURLEvent(`url:${eventName}`, {
            eventName,
            url,
            target: event.detail?.target,
            path: this.urlState.currentPath,
            requestConfig: event.detail?.requestConfig,
            xhr: event.detail?.xhr
        });
    }

    /**
     * Track fetch requests
     */
    trackFetch(url, duration, status) {
        if (!this.metrics.fetchRequests) {
            this.metrics.fetchRequests = [];
        }

        this.metrics.fetchRequests.push({
            url,
            duration,
            status,
            timestamp: Date.now()
        });

        // Keep only last 100 requests
        if (this.metrics.fetchRequests.length > 100) {
            this.metrics.fetchRequests.shift();
        }
    }

    /**
     * Track fetch errors
     */
    trackFetchError(url, error) {
        if (!this.metrics.fetchErrors) {
            this.metrics.fetchErrors = [];
        }

        this.metrics.fetchErrors.push({
            url,
            error: error.message,
            timestamp: Date.now()
        });
    }

    /**
     * Update URL state from current location
     */
    updateURLState() {
        this.urlState.previousUrl = this.urlState.currentUrl;
        this.urlState.previousPath = this.urlState.currentPath;
        this.urlState.previousHash = this.urlState.currentHash;

        this.urlState.currentUrl = window.location.href;
        this.urlState.currentPath = window.location.pathname;
        this.urlState.currentHash = window.location.hash;
        this.urlState.historyState = window.history.state;
        this.urlState.timestamp = Date.now();
        this.urlState.queryParams = Object.fromEntries(
            new URLSearchParams(window.location.search)
        );
    }

    /**
     * Update performance metrics
     */
    updateMetrics(updateTime) {
        this.metrics.urlChanges++;
        this.metrics.lastChange = Date.now();

        // Update average update time
        if (this.metrics.averageUpdateTime === 0) {
            this.metrics.averageUpdateTime = updateTime;
        } else {
            this.metrics.averageUpdateTime =
                (this.metrics.averageUpdateTime * 0.7) + (updateTime * 0.3);
        }
    }

    /**
     * Register URL event handler
     */
    onURLEvent(eventName, handler, options = {}) {
        if (!this.urlEvents.has(eventName)) {
            this.urlEvents.set(eventName, new Set());
        }

        const handlers = this.urlEvents.get(eventName);
        handlers.add(handler);

        // Return unsubscribe function
        return () => {
            const handlers = this.urlEvents.get(eventName);
            if (handlers) {
                handlers.delete(handler);
                if (handlers.size === 0) {
                    this.urlEvents.delete(eventName);
                }
            }
        };
    }

    /**
     * Remove URL event handler
     */
    offURLEvent(eventName, handler) {
        const handlers = this.urlEvents.get(eventName);
        if (handlers) {
            handlers.delete(handler);
            if (handlers.size === 0) {
                this.urlEvents.delete(eventName);
            }
        }
    }

    /**
     * Dispatch URL event
     */
    dispatchURLEvent(eventName, detail = {}) {
        const startTime = performance.now();

        // Call registered handlers
        const handlers = this.urlEvents.get(eventName);
        if (handlers) {
            handlers.forEach(handler => {
                try {
                    handler({
                        ...detail,
                        tracker: this,
                        urlState: { ...this.urlState }
                    });
                } catch (error) {
                    console.error(`Error in ${eventName} handler:`, error);
                }
            });
        }

        // Dispatch as custom event on window
        const event = new CustomEvent(eventName, {
            detail: {
                ...detail,
                tracker: this,
                urlState: { ...this.urlState },
                dispatchTime: performance.now() - startTime
            },
            bubbles: true,
            cancelable: true
        });

        window.dispatchEvent(event);
    }

    /**
     * Navigate to URL programmatically
     */
    navigateTo(url, options = {}) {
        const {
            state = {},
            title = '',
            replace = false,
            scroll = true,
            smooth = true
        } = options;

        const startTime = performance.now();
        const previousUrl = this.urlState.currentUrl;

        try {
            if (replace) {
                history.replaceState(state, title, url);
            } else {
                history.pushState(state, title, url);
            }

            this.updateURLState();

            // Handle scroll behavior
            if (scroll) {
                if (smooth) {
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                } else {
                    window.scrollTo(0, 0);
                }
            }

            this.dispatchURLEvent('url:navigated', {
                url,
                state,
                title,
                replace,
                previousUrl,
                currentUrl: this.urlState.currentUrl,
                navigationTime: performance.now() - startTime,
                options
            });

            return true;
        } catch (error) {
            console.error('Navigation failed:', error);
            this.dispatchURLEvent('url:navigation-error', {
                url,
                error,
                previousUrl,
                navigationTime: performance.now() - startTime
            });
            return false;
        }
    }

    /**
     * Get current URL state
     */
    getURLState() {
        return { ...this.urlState };
    }

    /**
     * Get performance metrics
     */
    getMetrics() {
        return { ...this.metrics };
    }

    /**
     * Check if URL matches pattern
     */
    isURLActive(url, options = {}) {
        const {
            exact = false,
            ignoreHash = false,
            ignoreSearch = false
        } = options;

        let current = this.urlState.currentUrl;
        let target = url;

        // Normalize URLs
        if (ignoreHash) {
            current = current.split('#')[0];
            target = target.split('#')[0];
        }

        if (ignoreSearch) {
            current = current.split('?')[0];
            target = target.split('?')[0];
        }

        if (exact) {
            return current === target ||
                this.urlState.currentPath === target;
        }

        return current.includes(target) ||
            this.urlState.currentPath.includes(target);
    }

    /**
     * Parse URL into components
     */
    parseURL(url) {
        try {
            const urlObj = new URL(url, window.location.origin);
            return {
                href: urlObj.href,
                origin: urlObj.origin,
                protocol: urlObj.protocol,
                host: urlObj.host,
                hostname: urlObj.hostname,
                port: urlObj.port,
                pathname: urlObj.pathname,
                search: urlObj.search,
                searchParams: Object.fromEntries(urlObj.searchParams),
                hash: urlObj.hash,
                username: urlObj.username,
                password: urlObj.password
            };
        } catch {
            return null;
        }
    }

    /**
     * Compare two URLs
     */
    compareURLs(url1, url2, options = {}) {
        const {
            ignoreProtocol = false,
            ignoreHost = false,
            ignorePort = false,
            ignoreHash = false,
            ignoreSearch = false
        } = options;

        const parsed1 = this.parseURL(url1);
        const parsed2 = this.parseURL(url2);

        if (!parsed1 || !parsed2) return false;

        let compare1 = parsed1.href;
        let compare2 = parsed2.href;

        if (ignoreProtocol) {
            compare1 = compare1.replace(/^https?:\/\//, '//');
            compare2 = compare2.replace(/^https?:\/\//, '//');
        }

        if (ignoreHost) {
            compare1 = compare1.replace(/^\/\/[^\/]+/, '');
            compare2 = compare2.replace(/^\/\/[^\/]+/, '');
        }

        if (ignoreHash) {
            compare1 = compare1.split('#')[0];
            compare2 = compare2.split('#')[0];
        }

        if (ignoreSearch) {
            compare1 = compare1.split('?')[0];
            compare2 = compare2.split('?')[0];
        }

        return compare1 === compare2;
    }

    /**
     * Get query parameter
     */
    getQueryParam(name, url = null) {
        const urlObj = url ? new URL(url, window.location.origin) : window.location;
        return urlObj.searchParams.get(name);
    }

    /**
     * Set query parameter
     */
    setQueryParam(name, value, options = {}) {
        const {
            replace = true,
            multiple = false
        } = options;

        const url = new URL(window.location.href);

        if (value === null || value === undefined) {
            url.searchParams.delete(name);
        } else if (multiple && Array.isArray(value)) {
            url.searchParams.delete(name);
            value.forEach(v => url.searchParams.append(name, v));
        } else {
            if (replace) {
                url.searchParams.set(name, value);
            } else {
                url.searchParams.append(name, value);
            }
        }

        return this.navigateTo(url.href, { replace: true });
    }

    /**
     * Get all query parameters
     */
    getAllQueryParams() {
        return Object.fromEntries(new URLSearchParams(window.location.search));
    }

    /**
     * Destroy URL tracking
     */
    destroyURLTracking() {
        // Remove event listeners
        this.urlListeners.forEach((handler, key) => {
            if (key === 'history') {
                // Restore original History API methods
                if (handler.originalPushState) {
                    history.pushState = handler.originalPushState;
                }
                if (handler.originalReplaceState) {
                    history.replaceState = handler.originalReplaceState;
                }
            } else if (key === 'fetch') {
                // Restore original fetch
                window.fetch = handler;
            } else if (key.startsWith('htmx:')) {
                document.removeEventListener(key.replace('htmx:', ''), handler);
            } else {
                window.removeEventListener(key, handler);
            }
        });

        this.urlListeners.clear();
        this.urlEvents.clear();
        this.pendingUpdates.clear();
        this.isURLTracking = false;

        this.log('URL tracking destroyed');
    }

    /**
     * Log message
     */
    log(...args) {
        if (this.options?.debug) {
            console.log('[URLTracker]', ...args);
        }
    }
};

