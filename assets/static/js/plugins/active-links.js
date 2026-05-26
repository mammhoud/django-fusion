/**
 * @file plugins/active-links.js
 * Active Links Plugin for Navigation Tracker
 */

export class ActiveLinksPlugin {
    constructor(tracker, options = {}) {
        this.tracker = tracker;
        this.options = {
            activeClass: 'active',
            exactActiveClass: 'exact-active',
            parentActiveClass: 'active-parent',
            autoUpdate: true,
            excludeSelectors: ['[data-no-activate]', '.disabled'],
            includeSelectors: ['[href]', '[hx-get]', '[data-href]'],
            ...options
        };
        
        this.observer = null;
        this.links = new Set();
    }
    
    async init() {
        // Initial link discovery
        this.discoverLinks();
        
        // Setup mutation observer
        this.setupObserver();
        
        // Listen to navigation events
        this.tracker.on('navigation:updated', () => this.updateActiveLinks());
        this.tracker.on('navigation:url-changed', () => this.updateActiveLinks());
        
        // console.log('🔗 ActiveLinksPlugin initialized');
        return this;
    }
    
    discoverLinks() {
        const selector = this.options.includeSelectors.join(',');
        const excludeSelector = this.options.excludeSelectors.join(',');
        
        document.querySelectorAll(selector).forEach(link => {
            if (!link.matches(excludeSelector)) {
                this.links.add(link);
            }
        });
    }
    
    setupObserver() {
        if (!this.options.autoUpdate) return;
        
        this.observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList') {
                    mutation.addedNodes.forEach((node) => {
                        if (node.nodeType === Node.ELEMENT_NODE) {
                            this.discoverLinks();
                        }
                    });
                }
            });
        });
        
        this.observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
    
    updateActiveLinks() {
        const currentPath = this.tracker.state.currentPath;
        const currentHash = this.tracker.state.currentHash;
        
        this.links.forEach(link => {
            this.updateLinkState(link, currentPath, currentHash);
        });
    }
    
    updateLinkState(link, currentPath, currentHash) {
        const href = this.getLinkHref(link);
        if (!href) return;
        
        // Remove existing active classes
        link.classList.remove(this.options.activeClass);
        link.classList.remove(this.options.exactActiveClass);
        link.removeAttribute('aria-current');
        
        // Check if link is active
        const isActive = this.isLinkActive(link, href, currentPath, currentHash);
        const isExact = this.isExactMatch(href, currentPath);
        
        if (isActive) {
            link.classList.add(this.options.activeClass);
            if (isExact) {
                link.classList.add(this.options.exactActiveClass);
                link.setAttribute('aria-current', 'page');
            }
            
            // Activate parent elements
            this.activateParent(link);
        } else {
            // Deactivate parent elements
            this.deactivateParent(link);
        }
    }
    
    getLinkHref(link) {
        return link.getAttribute('href') ||
               link.getAttribute('hx-get') ||
               link.getAttribute('data-href');
    }
    
    isLinkActive(link, href, currentPath, currentHash) {
        if (!href) return false;
        
        // Handle hash links
        if (href.startsWith('#')) {
            return href === currentHash;
        }
        
        try {
            const linkUrl = new URL(href, window.location.origin);
            const linkPath = linkUrl.pathname;
            
            // Check exact match
            if (linkPath === currentPath) return true;
            
            // Check prefix match
            if (currentPath.startsWith(linkPath) && linkPath !== '/') {
                return true;
            }
            
            // Check custom match rules
            const matchType = link.getAttribute('data-match') ||
                             link.getAttribute('data-nav-match');
            
            switch (matchType) {
                case 'prefix':
                    return currentPath.startsWith(linkPath);
                case 'contains':
                    return currentPath.includes(linkPath);
                case 'regex':
                    const pattern = link.getAttribute('data-pattern');
                    if (pattern) {
                        const regex = new RegExp(pattern);
                        return regex.test(currentPath);
                    }
                    return false;
                default:
                    return false;
            }
        } catch {
            // Handle relative URLs
            if (href === currentPath) return true;
            if (currentPath.startsWith(href) && href !== '/') return true;
            return false;
        }
    }
    
    isExactMatch(href, currentPath) {
        try {
            const linkUrl = new URL(href, window.location.origin);
            return linkUrl.pathname === currentPath;
        } catch {
            return href === currentPath;
        }
    }
    
    activateParent(link) {
        let parent = link.parentElement;
        while (parent && parent !== document.body) {
            if (parent.matches('.nav-item, .menu-item, [data-nav-item], .tab-item')) {
                parent.classList.add(this.options.activeClass);
                parent.classList.add(this.options.parentActiveClass);
            }
            parent = parent.parentElement;
        }
    }
    
    deactivateParent(link) {
        let parent = link.parentElement;
        while (parent && parent !== document.body) {
            if (parent.matches('.nav-item, .menu-item, [data-nav-item], .tab-item')) {
                parent.classList.remove(this.options.activeClass);
                parent.classList.remove(this.options.parentActiveClass);
            }
            parent = parent.parentElement;
        }
    }
    
    addLink(link) {
        this.links.add(link);
        this.updateLinkState(link, 
            this.tracker.state.currentPath, 
            this.tracker.state.currentHash);
    }
    
    removeLink(link) {
        this.links.delete(link);
        this.deactivateParent(link);
    }
    
    refresh() {
        this.links.clear();
        this.discoverLinks();
        this.updateActiveLinks();
    }
    
    destroy() {
        if (this.observer) {
            this.observer.disconnect();
        }
        
        // Remove all active classes
        this.links.forEach(link => {
            link.classList.remove(this.options.activeClass);
            link.classList.remove(this.options.exactActiveClass);
            link.removeAttribute('aria-current');
            this.deactivateParent(link);
        });
        
        this.links.clear();
        console.log('🔗 ActiveLinksPlugin destroyed');
    }
}

export default ActiveLinksPlugin;