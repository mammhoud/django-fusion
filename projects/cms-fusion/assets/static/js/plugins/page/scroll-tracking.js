/**
 * @file plugins/scroll-tracking.js
 * Scroll Tracking Plugin for Navigation Tracker
 */

export class ScrollTrackingPlugin {
    constructor(tracker, options = {}) {
        this.tracker = tracker;
        this.options = {
            trackElements: true,
            trackPages: true,
            trackSections: true,
            restoreScroll: true,
            sectionSelector: '[data-section]',
            elementSelector: '[data-track-scroll]',
            scrollThreshold: 50,
            debounceDelay: 100,
            throttleDelay: 50,
            storageKey: 'scroll_positions',
            maxStoredPositions: 50,
            debug: false,
            ...options
        };
        
        this.positions = new Map();
        this.observedElements = new Set();
        this.observers = [];
        this.sectionObserver = null;
        this.lastScrollTime = 0;
        
        // Bind methods
        this.handleScroll = this.debounce(this._handleScroll.bind(this), this.options.debounceDelay);
        this.updateScrollPosition = this.throttle(this._updateScrollPosition.bind(this), this.options.throttleDelay);
    }
    
    async init() {
        // Load saved positions
        this.loadPositions();
        
        // Setup scroll listener
        window.addEventListener('scroll', this.handleScroll, { passive: true });
        
        // Setup intersection observer for sections
        if (this.options.trackSections) {
            this.setupSectionObserver();
        }
        
        // Setup element tracking
        if (this.options.trackElements) {
            this.setupElementTracking();
        }
        
        // Listen to navigation events
        this.tracker.on('navigation:page-changed', (detail) => {
            this.handlePageChange(detail);
        });
        
        this.tracker.on('navigation:url-changed', (detail) => {
            this.handleURLChange(detail);
        });
        
        // console.log('📜 ScrollTrackingPlugin initialized');
        return this;
    }
    
    setupSectionObserver() {
        this.sectionObserver = new IntersectionObserver(
            (entries) => {
                entries.forEach(entry => {
                    this.handleSectionVisibility(entry);
                });
            },
            {
                root: null,
                rootMargin: '0px',
                threshold: 0.1
            }
        );
        
        // Observe all sections
        document.querySelectorAll(this.options.sectionSelector).forEach(section => {
            this.sectionObserver.observe(section);
        });
    }
    
    setupElementTracking() {
        // Initial discovery
        this.discoverTrackedElements();
        
        // Mutation observer for dynamic elements
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList') {
                    mutation.addedNodes.forEach((node) => {
                        if (node.nodeType === Node.ELEMENT_NODE) {
                            this.discoverTrackedElements();
                        }
                    });
                }
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        this.observers.push(observer);
    }
    
    discoverTrackedElements() {
        document.querySelectorAll(this.options.elementSelector).forEach(element => {
            if (!this.observedElements.has(element)) {
                this.observedElements.add(element);
                this.setupElementObserver(element);
            }
        });
    }
    
    setupElementObserver(element) {
        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach(entry => {
                    this.handleElementVisibility(element, entry);
                });
            },
            {
                root: null,
                rootMargin: '0px',
                threshold: [0, 0.25, 0.5, 0.75, 1]
            }
        );
        
        observer.observe(element);
        this.observers.push(observer);
    }
    
    handlePageChange(detail) {
        const { from, to } = detail;
        
        // Save scroll position for previous page
        if (from && from.url) {
            this.savePagePosition(from.url);
        }
        
        // Restore scroll position for new page if enabled
        if (this.options.restoreScroll && to && to.url) {
            setTimeout(() => {
                this.restorePagePosition(to.url);
            }, 100);
        }
        
        this.log('Page change handled:', { from: from?.url, to: to?.url });
    }
    
    handleURLChange(detail) {
        const { previousUrl, currentUrl } = detail;
        
        // Save position for previous URL
        if (previousUrl) {
            this.savePagePosition(previousUrl);
        }
        
        // Update current URL position
        this.updateCurrentPosition(currentUrl);
        
        this.log('URL change handled:', { previousUrl, currentUrl });
    }
    
    _handleScroll() {
        const currentUrl = window.location.href;
        this.updateScrollPosition(currentUrl);
        
        // Track visible sections
        if (this.options.trackSections) {
            this.updateVisibleSections();
        }
    }
    
    _updateScrollPosition(url) {
        const position = {
            x: window.scrollX,
            y: window.scrollY,
            timestamp: Date.now(),
            viewport: {
                width: window.innerWidth,
                height: window.innerHeight
            },
            document: {
                width: document.documentElement.scrollWidth,
                height: document.documentElement.scrollHeight
            }
        };
        
        this.positions.set(url, position);
        this.savePositions();
        
        this.dispatchEvent('scroll:position-updated', {
            url,
            position,
            plugin: this
        });
    }
    
    updateVisibleSections() {
        const visibleSections = [];
        const viewportHeight = window.innerHeight;
        const scrollY = window.scrollY;
        
        document.querySelectorAll(this.options.sectionSelector).forEach(section => {
            const rect = section.getBoundingClientRect();
            const isVisible = (
                rect.top >= 0 &&
                rect.left >= 0 &&
                rect.bottom <= viewportHeight &&
                rect.right <= window.innerWidth
            );
            
            const isPartiallyVisible = (
                rect.top < viewportHeight &&
                rect.bottom > 0
            );
            
            if (isPartiallyVisible) {
                const visibility = Math.min(
                    100,
                    Math.max(0, 
                        ((Math.min(rect.bottom, viewportHeight) - Math.max(rect.top, 0)) / 
                         rect.height) * 100
                    )
                ).toFixed(0);
                
                visibleSections.push({
                    id: section.id,
                    dataset: section.dataset,
                    visibility: parseInt(visibility),
                    rect: {
                        top: rect.top,
                        bottom: rect.bottom,
                        height: rect.height
                    }
                });
            }
        });
        
        // Sort by visibility
        visibleSections.sort((a, b) => b.visibility - a.visibility);
        
        if (visibleSections.length > 0) {
            this.dispatchEvent('scroll:section-visible', {
                sections: visibleSections,
                primarySection: visibleSections[0],
                scrollY,
                timestamp: Date.now()
            });
        }
    }
    
    handleSectionVisibility(entry) {
        const section = entry.target;
        const isVisible = entry.isIntersecting;
        const visibility = Math.floor(entry.intersectionRatio * 100);
        
        this.dispatchEvent('scroll:section-changed', {
            section: {
                id: section.id,
                dataset: section.dataset,
                element: section
            },
            isVisible,
            visibility,
            entry,
            timestamp: Date.now()
        });
        
        this.log(`Section ${section.id} visibility: ${visibility}%`);
    }
    
    handleElementVisibility(element, entry) {
        const visibility = Math.floor(entry.intersectionRatio * 100);
        
        this.dispatchEvent('scroll:element-visible', {
            element,
            visibility,
            entry,
            timestamp: Date.now()
        });
        
        // Update element data attribute
        element.dataset.scrollVisibility = visibility;
        
        if (visibility >= this.options.scrollThreshold) {
            element.dataset.scrollSeen = 'true';
            this.dispatchEvent('scroll:element-threshold', {
                element,
                visibility,
                timestamp: Date.now()
            });
        }
    }
    
    savePagePosition(url) {
        const position = {
            x: window.scrollX,
            y: window.scrollY,
            timestamp: Date.now()
        };
        
        this.positions.set(url, position);
        this.savePositions();
        
        return position;
    }
    
    restorePagePosition(url) {
        const position = this.positions.get(url);
        
        if (position && this.options.restoreScroll) {
            setTimeout(() => {
                window.scrollTo(position.x, position.y);
                
                this.dispatchEvent('scroll:position-restored', {
                    url,
                    position,
                    timestamp: Date.now()
                });
                
                this.log(`Scroll position restored for ${url}:`, position);
            }, 50);
            
            return true;
        }
        
        return false;
    }
    
    updateCurrentPosition(url) {
        const position = {
            x: window.scrollX,
            y: window.scrollY,
            timestamp: Date.now()
        };
        
        this.positions.set(url, position);
        return position;
    }
    
    getPosition(url = window.location.href) {
        return this.positions.get(url);
    }
    
    getAllPositions() {
        return Object.fromEntries(this.positions);
    }
    
    savePositions() {
        try {
            const data = {
                positions: Array.from(this.positions.entries()).slice(0, this.options.maxStoredPositions),
                timestamp: Date.now()
            };
            localStorage.setItem(this.options.storageKey, JSON.stringify(data));
        } catch (error) {
            console.warn('Failed to save scroll positions:', error);
        }
    }
    
    loadPositions() {
        try {
            const stored = localStorage.getItem(this.options.storageKey);
            if (stored) {
                const data = JSON.parse(stored);
                this.positions = new Map(data.positions || []);
                this.log('Loaded scroll positions:', this.positions.size);
            }
        } catch (error) {
            console.warn('Failed to load scroll positions:', error);
        }
    }
    
    clearPositions() {
        this.positions.clear();
        localStorage.removeItem(this.options.storageKey);
        this.dispatchEvent('scroll:positions-cleared');
        this.log('Scroll positions cleared');
    }
    
    scrollToElement(selectorOrElement, options = {}) {
        const element = typeof selectorOrElement === 'string' 
            ? document.querySelector(selectorOrElement)
            : selectorOrElement;
        
        if (!element) return false;
        
        const scrollOptions = {
            behavior: 'smooth',
            block: 'start',
            inline: 'nearest',
            ...options
        };
        
        element.scrollIntoView(scrollOptions);
        
        this.dispatchEvent('scroll:to-element', {
            element,
            options: scrollOptions,
            timestamp: Date.now()
        });
        
        return true;
    }
    
    scrollToTop(options = {}) {
        window.scrollTo({
            top: 0,
            behavior: 'smooth',
            ...options
        });
        
        this.dispatchEvent('scroll:to-top', {
            timestamp: Date.now()
        });
    }
    
    scrollToBottom(options = {}) {
        window.scrollTo({
            top: document.documentElement.scrollHeight,
            behavior: 'smooth',
            ...options
        });
        
        this.dispatchEvent('scroll:to-bottom', {
            timestamp: Date.now()
        });
    }
    
    dispatchEvent(eventName, detail = {}) {
        const event = new CustomEvent(eventName, {
            detail: { ...detail, plugin: this },
            bubbles: true
        });
        document.dispatchEvent(event);
    }
    
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    throttle(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
    
    log(...args) {
        if (this.options.debug) {
            console.log('[ScrollTrackingPlugin]', ...args);
        }
    }
    
    destroy() {
        // Remove event listeners
        window.removeEventListener('scroll', this.handleScroll);
        
        // Disconnect observers
        if (this.sectionObserver) {
            this.sectionObserver.disconnect();
        }
        
        this.observers.forEach(observer => observer.disconnect());
        this.observers = [];
        
        // Clear collections
        this.observedElements.clear();
        this.positions.clear();
        
        console.log('📜 ScrollTrackingPlugin destroyed');
    }
}

export default ScrollTrackingPlugin;