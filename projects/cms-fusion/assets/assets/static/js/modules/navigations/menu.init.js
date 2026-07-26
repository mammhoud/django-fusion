/**
 * @file navigations/core/index.js
 * Unified Navigation System - Core components only
 * Tracks active navigation links and header menu functionality
 */

import { DOM } from '../../utility/dom.js';
import { Utils } from '../../utility/helpers.js';

/**
 * Navigation Tracker
 * Tracks active navigation links
 */
class NavigationTracker {
    constructor(options = {}) {
        this.options = {
            // Navigation selectors
            navSelectors: [
                'a[href]',
                '[hx-get]',
                '[data-nav]',
                '[data-track-nav]',
                '.nav-link',
                '.sidebar-link',
                '.menu-item a',
                '.profile-tab',
                '.tab-link',
                '[data-profile-tab]'
            ],

            // Active state classes
            activeClass: 'active',
            parentActiveClass: 'active-parent',
            exactActiveClass: 'exact-active',

            // Tracking options
            trackHash: true,
            throttleDelay: 100,
            debug: false,

            ...options
        };

        // Core state
        this.state = {
            currentPath: window.location.pathname,
            currentHash: window.location.hash,
            activeLinks: new Set(),
            activeElements: new Map(),
            observers: [],
            initialized: false
        };

        // Event system
        this.handlers = new Map();
        this.cleanupFns = [];

        // Performance utilities
        this.updateNavigationState = Utils.throttle(
            this._updateNavigationState.bind(this),
            this.options.throttleDelay
        );

        this.log = (...args) => {
            if (this.options.debug) console.log('[NavigationTracker]', ...args);
        };
    }

    async initialize() {
        if (this.state.initialized) {
            this.log('Already initialized');
            return this;
        }

        try {
            this.setupEventListeners();
            this.setupDOMObserver();
            this.updateNavigationState();

            this.state.initialized = true;
            this.log('✅ Initialized');
            this.dispatchEvent('navigation:initialized', {
                state: this.getState()
            });

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
            const hashchangeHandler = this.handleHashChange.bind(this);
            window.addEventListener('hashchange', hashchangeHandler);
            this.cleanupFns.push(() => window.removeEventListener('hashchange', hashchangeHandler));
        }

        this.setupHTMXListeners();
    }

    setupHTMXListeners() {
        if (typeof htmx === 'undefined') return;

        const handleHTMXSwap = (event) => {
            const target = event.detail.target;
            const isContentUpdate = target && (
                target.id === 'main-content' ||
                target.id === 'panel-content' ||
                target.matches('[data-page-content]')
            );

            if (isContentUpdate) {
                setTimeout(() => {
                    this.updateNavigationState();
                }, 100);
            }
        };

        const events = ['htmx:afterSwap', 'htmx:historyRestore', 'htmx:beforeSwap'];
        events.forEach(eventName => {
            const handler = DOM.on(document, eventName, handleHTMXSwap);
            this.cleanupFns.push(handler);
        });
    }

    setupDOMObserver() {
        const observer = new MutationObserver((mutations) => {
            let shouldUpdate = false;

            mutations.forEach((mutation) => {
                if (mutation.type === 'childList') {
                    const hasNavElements = Array.from(mutation.addedNodes).some(node => {
                        if (node.nodeType === Node.ELEMENT_NODE) {
                            return node.matches(this.options.navSelectors.join(',')) ||
                                node.querySelector(this.options.navSelectors.join(','));
                        }
                        return false;
                    });
                    if (hasNavElements) shouldUpdate = true;
                }
            });

            if (shouldUpdate) {
                this.updateNavigationState();
            }
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ['data-nav']
        });

        this.state.observers.push(observer);
        this.cleanupFns.push(() => observer.disconnect());
    }

    handleClick(event) {
        const link = this.findClosestNavLink(event.target);
        if (!link) return;

        const href = this.getLinkTarget(link);
        if (!href || href.startsWith('javascript:')) return;

        if (href.startsWith('#')) {
            if (this.options.trackHash) {
                this.handleHashLink(href, link);
            }
            return;
        }

        if (link.hasAttribute('hx-get') || link.hasAttribute('hx-post')) {
            event.preventDefault();
        }

        this.handleNavigation(href, {
            source: 'click',
            element: link,
            event,
            isHX: link.hasAttribute('hx-get') || link.hasAttribute('hx-post')
        });
    }

    handleHashLink(hash, link) {
        const previousHash = this.state.currentHash;
        this.state.currentHash = hash;
        this.dispatchEvent('navigation:hash-changed', {
            previousHash,
            currentHash: hash,
            element: link,
            timestamp: Date.now()
        });
        this.updateNavigationState({ hashChanged: true });
    }

    handleHashChange() {
        this.state.currentHash = window.location.hash;
        this.updateNavigationState({ hashChanged: true });
    }

    handleNavigation(target, context = {}) {
        const previousPath = this.state.currentPath;

        try {
            const newUrl = new URL(target, window.location.origin);
            this.state.currentPath = newUrl.pathname;
            this.state.currentHash = newUrl.hash;

            this.dispatchEvent('navigation:navigated', {
                previousPath,
                currentPath: this.state.currentPath,
                target,
                url: newUrl.href,
                hash: newUrl.hash,
                context,
                timestamp: Date.now()
            });
        } catch (error) {
            console.warn('Invalid navigation target:', target);
        }
    }

    _updateNavigationState(context = {}) {
        this.clearActiveStates();
        const navLinks = DOM.$$(this.options.navSelectors.join(','));

        navLinks.forEach(link => {
            if (this.isLinkActive(link)) {
                this.activateLink(link, context);
                this.state.activeLinks.add(link);
                this.state.activeElements.set(link, {
                    href: this.getLinkTarget(link),
                    text: DOM.text(link).trim(),
                    isActive: true,
                    activatedAt: Date.now(),
                    context
                });
            }
        });

        this.dispatchEvent('navigation:updated', {
            activeLinks: this.state.activeLinks.size,
            currentPath: this.state.currentPath,
            currentHash: this.state.currentHash,
            context,
            timestamp: Date.now()
        });
    }

    isLinkActive(link) {
        const href = this.getLinkTarget(link);
        if (!href) return false;

        if (href.startsWith('#')) {
            return this.options.trackHash && href === this.state.currentHash;
        }

        try {
            const linkUrl = new URL(href, window.location.origin);
            const linkPath = linkUrl.pathname;

            if (linkPath === this.state.currentPath) {
                return true;
            }

            if (this.state.currentPath.startsWith(linkPath) && linkPath !== '/') {
                return true;
            }

            const matchType = DOM.attr(link, 'data-nav-match');
            if (matchType === 'prefix') {
                return this.state.currentPath.startsWith(linkPath);
            }
            if (matchType === 'contains') {
                return this.state.currentPath.includes(linkPath);
            }
            if (matchType === 'regex') {
                const pattern = DOM.attr(link, 'data-nav-pattern');
                if (pattern) {
                    const regex = new RegExp(pattern);
                    return regex.test(this.state.currentPath);
                }
            }

            return false;
        } catch (error) {
            if (href === this.state.currentPath) return true;
            if (this.state.currentPath.startsWith(href) && href !== '/') return true;
            return false;
        }
    }

    activateLink(link, context = {}) {
        DOM.addClass(link, this.options.activeClass);
        DOM.attr(link, 'aria-current', 'page');

        const href = this.getLinkTarget(link);
        if (href && !href.startsWith('#') && href === window.location.pathname) {
            DOM.addClass(link, this.options.exactActiveClass);
        }

        let parent = link.parentElement;
        while (parent && parent !== document.body) {
            if (DOM.matches(parent, '.nav-item, .menu-item, [data-nav-item], .tab-item, .sidebar-item')) {
                DOM.addClass(parent, this.options.activeClass);
                DOM.addClass(parent, this.options.parentActiveClass);
            }
            parent = parent.parentElement;
        }

        this.dispatchEvent('navigation:link-activated', {
            link,
            context,
            timestamp: Date.now()
        });
    }

    clearActiveStates() {
        this.state.activeLinks.forEach(link => {
            DOM.removeClass(link, this.options.activeClass);
            DOM.removeClass(link, this.options.exactActiveClass);
            DOM.removeAttr(link, 'aria-current');

            let parent = link.parentElement;
            while (parent && parent !== document.body) {
                if (DOM.matches(parent, '.nav-item, .menu-item, [data-nav-item], .tab-item, .sidebar-item')) {
                    DOM.removeClass(parent, this.options.activeClass);
                    DOM.removeClass(parent, this.options.parentActiveClass);
                }
                parent = parent.parentElement;
            }
        });

        this.state.activeLinks.clear();
        this.state.activeElements.clear();
    }

    findClosestNavLink(element) {
        return DOM.closest(element, this.options.navSelectors.join(','));
    }

    getLinkTarget(link) {
        return DOM.attr(link, 'href') ||
            DOM.attr(link, 'hx-get') ||
            DOM.attr(link, 'data-href') ||
            DOM.attr(link, 'data-target');
    }

    getState() {
        return {
            currentPath: this.state.currentPath,
            currentHash: this.state.currentHash,
            activeLinks: Array.from(this.state.activeLinks),
            activeElements: Array.from(this.state.activeElements.entries()).map(([element, data]) => ({
                element,
                ...data
            })),
            initialized: this.state.initialized
        };
    }

    getCurrentPath() { return this.state.currentPath; }
    getCurrentHash() { return this.state.currentHash; }
    getActiveLinks() { return Array.from(this.state.activeLinks); }
    getActiveElements() { return Array.from(this.state.activeElements.entries()); }

    refresh() {
        this.updateNavigationState({ source: 'refresh' });
    }

    dispatchEvent(eventName, detail = {}) {
        const event = new CustomEvent(eventName, {
            detail: { ...detail, tracker: this },
            bubbles: true,
            cancelable: true
        });
        document.dispatchEvent(event);
    }

    on(event, callback) {
        const handler = (e) => {
            if (e.detail && e.detail.tracker === this) {
                callback(e.detail);
            }
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

    destroy() {
        this.clearActiveStates();
        this.state.observers.forEach(observer => observer.disconnect());
        this.state.observers = [];
        this.cleanupFns.forEach(cleanup => cleanup());
        this.cleanupFns = [];

        this.handlers.clear();
        this.state.initialized = false;

        this.dispatchEvent('navigation:destroyed');
    }
}

/**
 * Header Menu
 * Enhanced header menu with navigation integration
 */
class HeaderMenu {
    constructor(options = {}) {
        this.options = {
            headerSelector: '.header',
            menuSelector: '.header-menu',
            toggleSelector: '.header-toggle',
            closeSelector: '.sidebar-close',
            dropdownsSelector: '.header-menu .dropdown',
            dropdownTogglesSelector: '.header-menu .dropdown-toggle',
            stickyEnabled: true,
            autoHideEnabled: true,
            transparentEnabled: true,
            mobileBreakpoint: 991,
            stickyClass: 'sticky-active',
            hideClass: 'hide',
            transparentClass: 'transparent',
            menuOpenClass: 'menu-open',
            toggleCloseClass: 'toggle-close',
            showClass: 'show',
            stickyThreshold: 10,
            autoHideThreshold: 100,
            transparencyThreshold: 10,
            scrollDebounceDelay: 100,
            resizeDebounceDelay: 250,
            dropdownHoverDelay: 200,
            dropdownCloseDelay: 300,
            navigation: null,
            debug: false,
            ...options
        };

        this.header = null;
        this.menu = null;
        this.toggle = null;
        this.isSticky = false;
        this.isMenuOpen = false;
        this.lastScrollTop = 0;
        this.scrolling = false;
        this.cleanupFns = [];
        this.navigation = this.options.navigation || null;

        this.log = (...args) => {
            if (this.options.debug) console.log('[HeaderMenu]', ...args);
        };
    }

    async init() {
        try {
            this.log('Initializing HeaderMenu...');
            this.findElements();

            if (!this.header) {
                console.warn('Header element not found');
                return this;
            }

            if (this.navigation && typeof this.navigation.init === 'function') {
                await this.navigation.init();
            }

            this.initStickyHeader();
            this.initTransparency();
            this.initMobileToggle();
            this.initDropdowns();
            this.initEventListeners();
            this.updateAccessibility();

            this.log('✅ HeaderMenu initialized');
            this.dispatchEvent('header-menu:initialized', {
                header: this.header,
                menu: this.menu
            });

        } catch (error) {
            console.error('Failed to initialize HeaderMenu:', error);
            throw error;
        }

        return this;
    }

    findElements() {
        this.header = document.querySelector(this.options.headerSelector);
        this.menu = this.header ? this.header.querySelector(this.options.menuSelector) : null;
        this.toggle = this.header ? this.header.querySelector(this.options.toggleSelector) : null;
        this.closeBtn = this.menu ? this.menu.querySelector(this.options.closeSelector) : null;
        this.log(`Found elements: header=${!!this.header}, menu=${!!this.menu}, toggle=${!!this.toggle}, closeBtn=${!!this.closeBtn}`);
    }

    initStickyHeader() {
        if (!this.options.stickyEnabled) return;

        const isAutoHide = this.header.classList.contains('sticky-autohide');
        const handleScroll = () => {
            if (this.scrolling) return;
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;

            if (isAutoHide && this.options.autoHideEnabled) {
                if (scrollTop > this.lastScrollTop && scrollTop > this.options.autoHideThreshold) {
                    if (!this.isMenuOpen) {
                        this.header.classList.add(this.options.hideClass);
                    }
                } else {
                    this.header.classList.remove(this.options.hideClass);
                }
            }

            if (scrollTop > this.options.stickyThreshold) {
                this.header.classList.add(this.options.stickyClass);
                this.isSticky = true;
            } else {
                this.header.classList.remove(this.options.stickyClass);
                this.isSticky = false;
            }

            this.lastScrollTop = scrollTop;
            this.dispatchEvent('header:scroll', {
                scrollTop,
                isSticky: this.isSticky,
                isHidden: this.header.classList.contains(this.options.hideClass)
            });
        };

        const debouncedScroll = Utils.debounce(handleScroll, this.options.scrollDebounceDelay);
        window.addEventListener('scroll', debouncedScroll);
        this.cleanupFns.push(() => window.removeEventListener('scroll', debouncedScroll));
        handleScroll();
    }

    initTransparency() {
        if (!this.options.transparentEnabled) return;
        const hasTransparency = this.header.classList.contains('transparent-light') ||
            this.header.classList.contains('transparent-dark');
        if (!hasTransparency) return;

        const updateTransparency = () => {
            const scrollTop = window.pageYOffset;
            if (scrollTop > this.options.transparencyThreshold) {
                this.header.classList.remove('transparent-light', 'transparent-dark');
            } else {
                if (this.header.classList.contains('transparent-light')) {
                    this.header.classList.add('transparent-light');
                }
                if (this.header.classList.contains('transparent-dark')) {
                    this.header.classList.add('transparent-dark');
                }
            }
        };

        const debouncedUpdate = Utils.debounce(updateTransparency, 100);
        window.addEventListener('scroll', debouncedUpdate);
        this.cleanupFns.push(() => window.removeEventListener('scroll', debouncedUpdate));
        updateTransparency();
    }

    initMobileToggle() {
        if (!this.toggle || !this.menu) return;

        this.toggle.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.toggleMobileMenu();
        });

        if (this.closeBtn) {
            this.closeBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.closeMobileMenu();
            });
        }

        document.addEventListener('click', (e) => {
            if (this.menu && !this.menu.contains(e.target) && !this.toggle.contains(e.target)) {
                this.closeMobileMenu();
            }
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isMenuOpen) {
                this.closeMobileMenu();
            }
        });
    }

    toggleMobileMenu() {
        this.menu.classList.toggle(this.options.showClass);
        this.toggle.classList.toggle(this.options.toggleCloseClass);
        document.body.classList.toggle(this.options.menuOpenClass);
        this.isMenuOpen = !this.isMenuOpen;
        this.toggle.setAttribute('aria-expanded', this.isMenuOpen);
        this.menu.setAttribute('aria-hidden', !this.isMenuOpen);
        this.dispatchEvent('header-menu:toggled', {
            isOpen: this.isMenuOpen
        });
    }

    closeMobileMenu() {
        if (this.isMenuOpen) {
            this.menu.classList.remove(this.options.showClass);
            this.toggle.classList.remove(this.options.toggleCloseClass);
            document.body.classList.remove(this.options.menuOpenClass);
            this.isMenuOpen = false;
            this.toggle.setAttribute('aria-expanded', 'false');
            this.menu.setAttribute('aria-hidden', 'true');
            this.dispatchEvent('header-menu:closed');
        }
    }

    updateAccessibility() {
        if (!this.toggle || !this.menu) return;
        if (!this.toggle.hasAttribute('aria-label')) {
            this.toggle.setAttribute('aria-label', 'Toggle navigation menu');
        }
        if (!this.menu.id) {
            this.menu.id = 'header-menu';
        }
        this.toggle.setAttribute('aria-controls', this.menu.id);
        this.toggle.setAttribute('aria-expanded', this.isMenuOpen);
        this.menu.setAttribute('aria-label', 'Main navigation');
        this.menu.setAttribute('aria-hidden', !this.isMenuOpen);
    }

    initDropdowns() {
        const dropdowns = this.header ?
            Array.from(this.header.querySelectorAll(this.options.dropdownsSelector)) : [];
        const toggles = this.header ?
            Array.from(this.header.querySelectorAll(this.options.dropdownTogglesSelector)) : [];

        toggles.forEach(toggle => {
            const dropdown = toggle.nextElementSibling;
            if (!dropdown) return;

            toggle.setAttribute('aria-haspopup', 'true');
            toggle.setAttribute('aria-expanded', 'false');

            toggle.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                const isOpen = dropdown.classList.contains(this.options.showClass);
                this.closeAllDropdowns();
                if (!isOpen) {
                    this.openDropdown(toggle, dropdown);
                }
            });

            if (!this.isMobile()) {
                let hoverTimeout;
                toggle.addEventListener('mouseenter', () => {
                    clearTimeout(hoverTimeout);
                    hoverTimeout = setTimeout(() => {
                        this.closeAllDropdowns();
                        this.openDropdown(toggle, dropdown);
                    }, this.options.dropdownHoverDelay);
                });

                dropdown.addEventListener('mouseleave', () => {
                    hoverTimeout = setTimeout(() => {
                        this.closeDropdown(toggle, dropdown);
                    }, this.options.dropdownCloseDelay);
                });
            }
        });

        document.addEventListener('click', (e) => {
            if (!e.target.closest(this.options.dropdownsSelector) &&
                !e.target.closest(this.options.dropdownTogglesSelector)) {
                this.closeAllDropdowns();
            }
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeAllDropdowns();
            }
        });
    }

    openDropdown(toggle, dropdown) {
        dropdown.classList.add(this.options.showClass);
        toggle.setAttribute('aria-expanded', 'true');
        this.positionDropdown(dropdown);
        this.dispatchEvent('header-dropdown:opened', {
            dropdown,
            toggle
        });
    }

    closeDropdown(toggle, dropdown) {
        dropdown.classList.remove(this.options.showClass);
        if (toggle) {
            toggle.setAttribute('aria-expanded', 'false');
        }
        this.dispatchEvent('header-dropdown:closed', {
            dropdown,
            toggle
        });
    }

    closeAllDropdowns() {
        const dropdowns = this.header ?
            Array.from(this.header.querySelectorAll(`${this.options.dropdownsSelector}.${this.options.showClass}`)) : [];
        const toggles = this.header ?
            Array.from(this.header.querySelectorAll(`${this.options.dropdownTogglesSelector}[aria-expanded="true"]`)) : [];

        dropdowns.forEach(dropdown => dropdown.classList.remove(this.options.showClass));
        toggles.forEach(toggle => toggle.setAttribute('aria-expanded', 'false'));
    }

    positionDropdown(dropdown) {
        const rect = dropdown.getBoundingClientRect();
        const viewportWidth = window.innerWidth;
        if (rect.right > viewportWidth) {
            dropdown.classList.add('dropdown-menu-end');
        }
        const viewportHeight = window.innerHeight;
        if (rect.bottom > viewportHeight) {
            dropdown.classList.add('dropdown-menu-bottom');
        }
    }

    initEventListeners() {
        const resizeHandler = Utils.debounce(() => this.handleResize(), this.options.resizeDebounceDelay);
        window.addEventListener('resize', resizeHandler);
        this.cleanupFns.push(() => window.removeEventListener('resize', resizeHandler));

        if (this.navigation) {
            this.navigation.on('navigation:updated', (data) => {
                this.handleNavigationUpdate(data);
            });
        }
    }

    handleResize() {
        if (!this.isMobile() && this.isMenuOpen) {
            this.closeMobileMenu();
        }

        const dropdowns = this.header ?
            Array.from(this.header.querySelectorAll(`${this.options.dropdownsSelector}.${this.options.showClass}`)) : [];
        dropdowns.forEach(dropdown => this.positionDropdown(dropdown));

        this.dispatchEvent('header:resized', {
            isMobile: this.isMobile(),
            headerHeight: this.header?.offsetHeight || 0
        });
    }

    handleNavigationUpdate(data) {
        const hasActiveLinks = this.navigation.getActiveLinks().some(link =>
            this.header?.contains(link)
        );
        this.header.classList.toggle('has-active-link', hasActiveLinks);
    }

    isMobile() {
        return window.innerWidth <= this.options.mobileBreakpoint;
    }

    dispatchEvent(eventName, detail = {}) {
        const event = new CustomEvent(eventName, {
            detail: { ...detail, headerMenu: this },
            bubbles: true,
            cancelable: true
        });
        document.dispatchEvent(event);
    }

    getState() {
        return {
            isSticky: this.isSticky,
            isMenuOpen: this.isMenuOpen,
            isMobile: this.isMobile(),
            headerHeight: this.header?.offsetHeight || 0
        };
    }

    refresh() {
        if (this.navigation) {
            this.navigation.refresh();
        }
        this.updateAccessibility();
        this.log('Header refreshed');
    }

    destroy() {
        this.closeMobileMenu();
        this.closeAllDropdowns();
        this.cleanupFns.forEach(fn => fn());
        this.cleanupFns = [];

        if (this.header) {
            this.header.classList.remove(
                this.options.stickyClass,
                this.options.hideClass,
                'transparent-light',
                'transparent-dark',
                'has-active-link',
                'on-dashboard',
                'on-profile',
                'on-settings'
            );
        }

        document.body.classList.remove(this.options.menuOpenClass);
        this.log('HeaderMenu destroyed');
    }
}

/**
 * Unified Navigation System
 * Manages both NavigationTracker and HeaderMenu together
 */
class UnifiedNavigationSystem {
    constructor(options = {}) {
        this.options = {
            navigation: {},
            headerMenu: {},
            debug: false,
            ...options
        };

        this.navigation = null;
        this.headerMenu = null;
        this.initialized = false;

        this.log = (...args) => {
            if (this.options.debug) console.log('[UnifiedNavigationSystem]', ...args);
        };
    }

    async initialize() {
        if (this.initialized) {
            this.log('Already initialized');
            return this;
        }

        try {
            this.log('Initializing Unified Navigation System...');
            this.navigation = new NavigationTracker({
                debug: this.options.debug,
                ...this.options.navigation
            });

            this.headerMenu = new HeaderMenu({
                navigation: this.navigation,
                debug: this.options.debug,
                ...this.options.headerMenu
            });

            await this.navigation.initialize();
            await this.headerMenu.init();
            this.setupEventDelegation();
            this.initialized = true;
            this.log('✅ Unified Navigation System initialized');

            this.dispatchEvent('unified-navigation:initialized', {
                navigation: this.navigation,
                headerMenu: this.headerMenu
            });

        } catch (error) {
            console.error('Failed to initialize UnifiedNavigationSystem:', error);
            throw error;
        }

        return this;
    }

    setupEventDelegation() {
        this.navigation.on('navigation:updated', (data) => {
            this.headerMenu.handleNavigationUpdate(data);
        });

        this.headerMenu.on('header-menu:closed', () => {
            this.navigation.refresh();
        });
    }

    on(event, callback) {
        if (event.startsWith('navigation:')) {
            return this.navigation.on(event, callback);
        } else if (event.startsWith('header-menu:')) {
            return this.headerMenu.on(event, callback);
        } else if (event.startsWith('unified-navigation:')) {
            const handler = (e) => {
                if (e.detail && e.detail.system === this) {
                    callback(e.detail);
                }
            };
            document.addEventListener(event, handler);
            return this;
        }
        console.warn(`Unknown event prefix: ${event}`);
        return this;
    }

    getState() {
        return {
            navigation: this.navigation.getState(),
            headerMenu: this.headerMenu.getState(),
            initialized: this.initialized
        };
    }

    refresh() {
        this.navigation.refresh();
        this.headerMenu.refresh();
        this.log('Unified navigation refreshed');
    }

    destroy() {
        if (this.navigation) this.navigation.destroy();
        if (this.headerMenu) this.headerMenu.destroy();
        this.initialized = false;
        this.log('Unified Navigation System destroyed');
        this.dispatchEvent('unified-navigation:destroyed');
    }

    dispatchEvent(eventName, detail = {}) {
        const event = new CustomEvent(eventName, {
            detail: { ...detail, system: this },
            bubbles: true,
            cancelable: true
        });
        document.dispatchEvent(event);
    }
}

// Create singleton instances
const navigationTracker = new NavigationTracker();
const unifiedNavigation = new UnifiedNavigationSystem();

// Export everything
export {
    NavigationTracker,
    navigationTracker,
    HeaderMenu,
    UnifiedNavigationSystem,
    unifiedNavigation,
};

// Default export
export default UnifiedNavigationSystem;
