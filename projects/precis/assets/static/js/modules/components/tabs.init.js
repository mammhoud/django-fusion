/**
 * @file tab-manager.js
 * @description Generic Tab Manager for handling tab navigation and content switching
 */

import { DOM } from '../../utility/dom.js';

export class Tabs {
    /**
     * @param {Object} options - Configuration options
     * @param {string} options.tabSelector - CSS selector for tab elements
     * @param {string} options.contentSelector - CSS selector for content elements
     * @param {string} options.activeClass - CSS class for active state
     * @param {boolean} options.updateURL - Whether to update URL hash
     * @param {boolean} options.saveToStorage - Whether to save active tab to localStorage
     * @param {string} options.storageKey - Key for localStorage
     * @param {Function} options.onTabChange - Callback when tab changes
     * @param {Function} options.onTabLoad - Callback when tab content loads
     * @param {boolean} options.lazyLoad - Whether to load content lazily
     * @param {Object} options.loadingConfig - Loading indicator configuration
     */
    constructor(options = {}) {
        this.options = {
            tabSelector: '[role="tab"], [data-tab], .nav-tabs .nav-link',
            contentSelector: '[role="tabpanel"], [data-tab-content], .tab-pane',
            activeClass: 'active',
            updateURL: true,
            saveToStorage: false,
            storageKey: 'last_active_tab',
            onTabChange: null,
            onTabLoad: null,
            lazyLoad: false,
            loadingConfig: {
                show: true,
                selector: '.tab-loading',
                message: 'Loading...'
            },
            ...options
        };

        this.tabs = new Map();
        this.currentTab = null;
        this.initialized = false;
        this.observers = [];

        this.log = this.log.bind(this);
        this.debug = options.debug || false;
    }

    /**
     * Initialize the tab manager
     */
    init() {
        if (this.initialized) {
            this.log('TabManager already initialized');
            return this;
        }

        this.setupTabs();
        this.setupObservers();
        this.restoreActiveTab();

        this.initialized = true;
        this.log('TabManager initialized');
        return this;
    }

    /**
     * Setup tabs and content
     */
    setupTabs() {
        const tabElements = DOM.$$(this.options.tabSelector);

        tabElements.forEach(tab => {
            const tabId = this.getTabId(tab);
            if (!tabId) return;

            const content = this.getTabContent(tabId);

            this.tabs.set(tabId, {
                element: tab,
                content: content,
                active: DOM.hasClass(tab, this.options.activeClass),
                loaded: content && content.hasChildNodes()
            });

            // Add click handler
            DOM.on(tab, 'click', (event) => {
                event.preventDefault();
                this.switchTab(tabId, { source: 'click', element: tab });
            });
        });

        // Set initial active tab
        this.updateCurrentTab();
    }

    /**
     * Get tab ID from element
     */
    getTabId(tabElement) {
        return (
            tabElement.getAttribute('href')?.substring(1) ||
            tabElement.getAttribute('data-tab') ||
            tabElement.getAttribute('aria-controls') ||
            tabElement.id
        );
    }

    /**
     * Get content element for tab
     */
    getTabContent(tabId) {
        return (
            document.getElementById(tabId) ||
            DOM.$(`[data-tab-content="${tabId}"]`) ||
            DOM.$(`[aria-labelledby="${tabId}"]`)
        );
    }

    /**
     * Switch to a specific tab
     */
    async switchTab(tabId, context = {}) {
        const tab = this.tabs.get(tabId);
        if (!tab) {
            this.log(`Tab not found: ${tabId}`, 'warn');
            return;
        }

        if (this.currentTab === tabId) {
            this.log(`Tab already active: ${tabId}`);
            return;
        }

        // Deactivate current tab
        if (this.currentTab) {
            this.deactivateTab(this.currentTab);
        }

        // Activate new tab
        await this.activateTab(tabId, context);

        // Update URL hash if enabled
        if (this.options.updateURL) {
            window.location.hash = tabId;
        }

        // Save to storage if enabled
        if (this.options.saveToStorage) {
            this.saveActiveTab(tabId);
        }

        // Call callback
        if (this.options.onTabChange) {
            this.options.onTabChange(tabId, tab, context);
        }

        this.dispatchEvent('tab:switched', {
            tabId,
            tab,
            context,
            timestamp: Date.now()
        });

        this.log(`Switched to tab: ${tabId}`, context);
    }

    /**
     * Activate a tab
     */
    async activateTab(tabId, context = {}) {
        const tab = this.tabs.get(tabId);
        if (!tab) return;

        // Show loading if lazy loading
        if (this.options.lazyLoad && !tab.loaded) {
            this.showTabLoading(tabId);
        }

        // Activate tab element
        DOM.addClass(tab.element, this.options.activeClass);
        tab.element.setAttribute('aria-selected', 'true');
        tab.element.setAttribute('tabindex', '0');

        // Activate content
        if (tab.content) {
            DOM.addClass(tab.content, this.options.activeClass, 'show');
            tab.content.setAttribute('aria-hidden', 'false');

            // Load content if needed
            if (this.options.lazyLoad && !tab.loaded) {
                await this.loadTabContent(tabId);
                tab.loaded = true;
            }
        }

        tab.active = true;
        this.currentTab = tabId;

        // Hide loading
        if (this.options.lazyLoad) {
            this.hideTabLoading(tabId);
        }

        // Call load callback
        if (this.options.onTabLoad && tab.loaded) {
            this.options.onTabLoad(tabId, tab);
        }

        this.dispatchEvent('tab:activated', { tabId, tab, context });
    }

    /**
     * Deactivate a tab
     */
    deactivateTab(tabId) {
        const tab = this.tabs.get(tabId);
        if (!tab) return;

        DOM.removeClass(tab.element, this.options.activeClass);
        tab.element.setAttribute('aria-selected', 'false');
        tab.element.setAttribute('tabindex', '-1');

        if (tab.content) {
            DOM.removeClass(tab.content, this.options.activeClass, 'show');
            tab.content.setAttribute('aria-hidden', 'true');
        }

        tab.active = false;

        this.dispatchEvent('tab:deactivated', { tabId, tab });
    }

    /**
     * Load tab content dynamically
     */
    async loadTabContent(tabId) {
        const tab = this.tabs.get(tabId);
        if (!tab || !tab.content) return;

        const dataUrl = tab.content.getAttribute('data-url') ||
            tab.element.getAttribute('data-load-url');

        if (!dataUrl) {
            this.log(`No data URL found for tab: ${tabId}`);
            return;
        }

        try {
            const response = await fetch(dataUrl, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });

            if (response.ok) {
                const content = await response.text();
                tab.content.innerHTML = content;
                this.dispatchEvent('tab:contentLoaded', { tabId, content });
            }
        } catch (error) {
            console.error(`Failed to load tab content: ${tabId}`, error);
            tab.content.innerHTML = `<div class="alert alert-danger">Failed to load content</div>`;
        }
    }

    /**
     * Show loading indicator for tab
     */
    showTabLoading(tabId) {
        const tab = this.tabs.get(tabId);
        if (!tab || !tab.content || !this.options.loadingConfig.show) return;

        const loadingElement = tab.content.querySelector(this.options.loadingConfig.selector);
        if (loadingElement) {
            DOM.removeClass(loadingElement, 'd-none');
        } else {
            const loader = document.createElement('div');
            loader.className = 'tab-loading text-center py-5';
            loader.innerHTML = `
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">${this.options.loadingConfig.message}</span>
                </div>
            `;
            tab.content.appendChild(loader);
        }
    }

    /**
     * Hide loading indicator for tab
     */
    hideTabLoading(tabId) {
        const tab = this.tabs.get(tabId);
        if (!tab || !tab.content) return;

        const loadingElement = tab.content.querySelector(this.options.loadingConfig.selector);
        if (loadingElement) {
            DOM.addClass(loadingElement, 'd-none');
        } else {
            const loader = tab.content.querySelector('.tab-loading');
            if (loader) {
                loader.remove();
            }
        }
    }

    /**
     * Setup mutation observers
     */
    setupObservers() {
        // Observe for new tabs added dynamically
        const tabObserver = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList') {
                    mutation.addedNodes.forEach(node => {
                        if (node.nodeType === Node.ELEMENT_NODE) {
                            if (node.matches(this.options.tabSelector)) {
                                this.setupTabs();
                            }
                        }
                    });
                }
            });
        });

        // Observe tab container
        const tabContainer = DOM.$('[data-tab-container], .nav-tabs');
        if (tabContainer) {
            tabObserver.observe(tabContainer, { childList: true, subtree: true });
            this.observers.push(tabObserver);
        }
    }

    /**
     * Restore active tab from URL or storage
     */
    restoreActiveTab() {
        let tabId = null;

        // Try URL hash first
        if (this.options.updateURL && window.location.hash) {
            tabId = window.location.hash.substring(1);
        }

        // Try localStorage
        if (!tabId && this.options.saveToStorage) {
            tabId = localStorage.getItem(this.options.storageKey);
        }

        // Find first active tab
        if (!tabId) {
            const activeTab = DOM.$(`${this.options.tabSelector}.${this.options.activeClass}`);
            if (activeTab) {
                tabId = this.getTabId(activeTab);
            }
        }

        // Switch to tab if found
        if (tabId && this.tabs.has(tabId)) {
            this.switchTab(tabId, { source: 'restore' });
        }
    }

    /**
     * Save active tab to storage
     */
    saveActiveTab(tabId) {
        if (!this.options.saveToStorage) return;

        try {
            localStorage.setItem(this.options.storageKey, tabId);
        } catch (error) {
            console.warn('Failed to save tab to localStorage:', error);
        }
    }

    /**
     * Update current tab from DOM
     */
    updateCurrentTab() {
        const activeTab = DOM.$(`${this.options.tabSelector}.${this.options.activeClass}`);
        if (activeTab) {
            const tabId = this.getTabId(activeTab);
            if (tabId && this.tabs.has(tabId)) {
                this.currentTab = tabId;
            }
        }
    }

    /**
     * Get current active tab
     */
    getCurrentTab() {
        return this.currentTab;
    }

    /**
     * Get all tabs
     */
    getTabs() {
        return new Map(this.tabs);
    }

    /**
     * Get tab by ID
     */
    getTab(tabId) {
        return this.tabs.get(tabId);
    }

    /**
     * Add new tab dynamically
     */
    addTab(tabElement, contentElement = null) {
        const tabId = this.getTabId(tabElement);
        if (!tabId) return null;

        this.tabs.set(tabId, {
            element: tabElement,
            content: contentElement,
            active: false,
            loaded: contentElement && contentElement.hasChildNodes()
        });

        // Setup click handler
        DOM.on(tabElement, 'click', (event) => {
            event.preventDefault();
            this.switchTab(tabId, { source: 'click', element: tabElement });
        });

        this.dispatchEvent('tab:added', { tabId, tabElement, contentElement });
        return tabId;
    }

    /**
     * Remove tab
     */
    removeTab(tabId) {
        if (this.currentTab === tabId) {
            // Find another tab to switch to
            const otherTabs = Array.from(this.tabs.keys()).filter(id => id !== tabId);
            if (otherTabs.length > 0) {
                this.switchTab(otherTabs[0], { source: 'removal' });
            }
        }

        this.tabs.delete(tabId);
        this.dispatchEvent('tab:removed', { tabId });
    }

    /**
     * Dispatch custom event
     */
    dispatchEvent(eventName, detail = {}) {
        const event = new CustomEvent(eventName, {
            detail: { ...detail, instance: this }
        });
        document.dispatchEvent(event);
    }

    /**
     * Log messages
     */
    log(message, data = null) {
        if (!this.debug) return;

        if (data) {
            console.log(`[TabManager] ${message}`, data);
        } else {
            console.log(`[TabManager] ${message}`);
        }
    }

    /**
     * Cleanup
     */
    destroy() {
        this.observers.forEach(observer => observer.disconnect());
        this.observers = [];

        // Remove event listeners
        this.tabs.forEach(tab => {
            if (tab.element) {
                const newElement = tab.element.cloneNode(true);
                tab.element.parentNode.replaceChild(newElement, tab.element);
            }
        });

        this.tabs.clear();
        this.currentTab = null;
        this.initialized = false;

        this.log('TabManager destroyed');
    }
}

export default Tabs;