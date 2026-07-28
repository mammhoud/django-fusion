import { DOM } from '../lib/dom.js';
import { Utils } from '../lib/helpers.js';

/**
 * NavigationTracker
 * Tracks active navigation links and updates their active state.
 */
export class NavigationTracker {
    constructor(options = {}) {
        this.options = {
            navSelectors: [
                'a[href]',
                '[hx-get]',
                '[data-nav-link]',
                '.navigator__link',
                '[data-navigator]',
            ],
            activeClass:       'active',
            parentActiveClass: 'active-parent',
            exactActiveClass:  'exact-active',
            trackHash:         true,
            throttleDelay:     100,
            debug:             false,
            ...options,
        };

        this.state = {
            currentPath:    window.location.pathname,
            currentHash:    window.location.hash,
            activeLinks:    new Set(),
            activeElements: new Map(),
            observers:      [],
            initialized:    false,
        };

        this.handlers  = new Map();
        this.cleanupFns = [];

        this.updateNavigationState = Utils.throttle(
            this._updateNavigationState.bind(this),
            this.options.throttleDelay
        );

        this.log = (...args) => {
            if (this.options.debug) console.log('[NavigationTracker]', ...args);
        };
    }

    async initialize() {
        if (this.state.initialized) return this;

        try {
            this.setupEventListeners();
            this.setupDOMObserver();
            this.updateNavigationState();
            this.state.initialized = true;
            this.log('✅ Initialized');
            this._dispatch('navigation:initialized', { state: this.getState() });
        } catch (error) {
            console.error('Failed to initialize NavigationTracker:', error);
            throw error;
        }

        return this;
    }

    setupEventListeners() {
        const clickHandler = this.handleClick.bind(this);
        DOM.on(document, 'click', clickHandler, true);
        this.cleanupFns.push(() => DOM.off(document, 'click', clickHandler));

        if (this.options.trackHash) {
            const hashHandler = this.handleHashChange.bind(this);
            window.addEventListener('hashchange', hashHandler);
            this.cleanupFns.push(() => window.removeEventListener('hashchange', hashHandler));
        }

        // Re-update after HTMX content swaps (tab navigation)
        const htmxHandler = (event) => {
            const target = event.detail?.target;
            if (target && (
                target.id === 'main-content' ||
                target.id === 'panel-content' ||
                target.matches?.('[data-page-content]')
            )) {
                setTimeout(() => this.updateNavigationState(), 100);
            }
        };
        ['htmx:afterSwap', 'htmx:historyRestore'].forEach(name => {
            DOM.on(document, name, htmxHandler);
            this.cleanupFns.push(() => document.removeEventListener(name, htmxHandler));
        });
    }

    setupDOMObserver() {
        const selector = this.options.navSelectors.join(',');
        const observer = new MutationObserver((mutations) => {
            const hasNavElements = mutations.some(m =>
                m.type === 'childList' &&
                Array.from(m.addedNodes).some(node =>
                    node.nodeType === Node.ELEMENT_NODE &&
                    (node.matches(selector) || node.querySelector(selector))
                )
            );
            if (hasNavElements) this.updateNavigationState();
        });

        observer.observe(document.body, {
            childList:       true,
            subtree:         true,
            attributes:      true,
            // Only observe attributes we actually change to reduce noisy mutations
            attributeFilter: ['data-nav-link', 'aria-current'],
        });

        this.state.observers.push(observer);
        this.cleanupFns.push(() => observer.disconnect());
    }

    handleClick(event) {
        const link = DOM.closest(event.target, this.options.navSelectors.join(','));
        if (!link) return;

        const href = this._getLinkTarget(link);
        if (!href || href.startsWith('javascript:')) return;

        if (href.startsWith('#') && this.options.trackHash) {
            this._handleHashLink(href, link);
            return;
        }

        this._handleNavigation(href, { source: 'click', element: link, event });
    }

    handleHashChange() {
        this.state.currentHash = window.location.hash;
        this.updateNavigationState({ hashChanged: true });
    }

    _handleHashLink(hash, link) {
        const prev = this.state.currentHash;
        this.state.currentHash = hash;
        this._dispatch('navigation:hash-changed', { previousHash: prev, currentHash: hash });
        this.updateNavigationState({ hashChanged: true });
    }

    _handleNavigation(target, context = {}) {
        const prev = this.state.currentPath;
        try {
            const url = new URL(target, window.location.origin);
            this.state.currentPath = url.pathname;
            this.state.currentHash = url.hash;
            this._dispatch('navigation:navigated', {
                previousPath: prev,
                currentPath:  this.state.currentPath,
                target,
                context,
            });
        } catch {
            console.warn('Invalid navigation target:', target);
        }
    }

    _updateNavigationState(context = {}) {
        this._clearActiveStates();
        const selector = this.options.navSelectors.join(',');

        document.querySelectorAll(selector).forEach(link => {
            if (this._isLinkActive(link)) {
                this._activateLink(link, context);
                this.state.activeLinks.add(link);
                this.state.activeElements.set(link, {
                    href:        this._getLinkTarget(link),
                    text:        link.textContent.trim(),
                    isActive:    true,
                    activatedAt: Date.now(),
                    context,
                });
            }
        });

        this._dispatch('navigation:updated', {
            activeLinks:  this.state.activeLinks.size,
            currentPath:  this.state.currentPath,
            currentHash:  this.state.currentHash,
            context,
        });
    }

    _isLinkActive(link) {
        const href = this._getLinkTarget(link);
        if (!href) return false;

        if (href.startsWith('#')) {
            return this.options.trackHash && href === this.state.currentHash;
        }

        try {
            const linkPath = new URL(href, window.location.origin).pathname;
            if (linkPath === this.state.currentPath) return true;
            if (this.state.currentPath.startsWith(linkPath) && linkPath !== '/') return true;

            const matchType = link.getAttribute('data-nav-match');
            if (matchType === 'prefix')  return this.state.currentPath.startsWith(linkPath);
            if (matchType === 'contains') return this.state.currentPath.includes(linkPath);
            if (matchType === 'regex') {
                const pattern = link.getAttribute('data-nav-pattern');
                return pattern ? new RegExp(pattern).test(this.state.currentPath) : false;
            }
        } catch {
            if (href === this.state.currentPath) return true;
            if (this.state.currentPath.startsWith(href) && href !== '/') return true;
        }

        return false;
    }

    _activateLink(link, context = {}) {
        link.classList.add(this.options.activeClass);
        link.setAttribute('aria-current', 'page');

        const href = this._getLinkTarget(link);
        if (href && !href.startsWith('#') && href === window.location.pathname) {
            link.classList.add(this.options.exactActiveClass);
        }

        let parent = link.parentElement;
        while (parent && parent !== document.body) {
            if (parent.matches('.nav-item, .menu-item, [data-nav-item], .tab-item, .sidebar-item')) {
                parent.classList.add(this.options.activeClass, this.options.parentActiveClass);
            }
            parent = parent.parentElement;
        }

        this._dispatch('navigation:link-activated', { link, context });
    }

    _clearActiveStates() {
        this.state.activeLinks.forEach(link => {
            link.classList.remove(
                this.options.activeClass,
                this.options.exactActiveClass
            );
            link.removeAttribute('aria-current');

            let parent = link.parentElement;
            while (parent && parent !== document.body) {
                if (parent.matches('.nav-item, .menu-item, [data-nav-item], .tab-item, .sidebar-item')) {
                    parent.classList.remove(this.options.activeClass, this.options.parentActiveClass);
                }
                parent = parent.parentElement;
            }
        });

        this.state.activeLinks.clear();
        this.state.activeElements.clear();
    }

    _getLinkTarget(link) {
        return link.getAttribute('href')
            || link.getAttribute('hx-get')
            || link.getAttribute('data-href')
            || link.getAttribute('data-target')
            || null;
    }

    _dispatch(eventName, detail = {}) {
        document.dispatchEvent(new CustomEvent(eventName, {
            detail: { ...detail, tracker: this },
            bubbles: true,
            cancelable: true,
        }));
    }

    // ── Public API ────────────────────────────────────────────

    on(event, callback) {
        const handler = (e) => {
            if (e.detail?.tracker === this) callback(e.detail);
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

    refresh() {
        this.updateNavigationState({ source: 'refresh' });
    }

    getState() {
        return {
            currentPath:    this.state.currentPath,
            currentHash:    this.state.currentHash,
            activeLinks:    Array.from(this.state.activeLinks),
            initialized:    this.state.initialized,
        };
    }

    getCurrentPath()  { return this.state.currentPath; }
    getCurrentHash()  { return this.state.currentHash; }
    getActiveLinks()  { return Array.from(this.state.activeLinks); }

    destroy() {
        this._clearActiveStates();
        this.state.observers.forEach(o => o.disconnect());
        this.state.observers = [];
        this.cleanupFns.forEach(fn => fn());
        this.cleanupFns = [];
        this.handlers.clear();
        this.state.initialized = false;
        this._dispatch('navigation:destroyed');
    }
}

// ── Singleton ─────────────────────────────────────────────────

export const navigationTracker = new NavigationTracker();
export default navigationTracker;
