/**
 * Application State Management
 * Centralized state management for the application
 */

// ============================================
// APPLICATION STATE
// ============================================

export class AppState {
    // ============================================
    // STATIC PROPERTIES - Application State
    // ============================================
    
    // Core state
    static initialized = false;
    static windowWidth = window.innerWidth;
    static windowHeight = window.innerHeight;
    static scrollPosition = window.pageYOffset || document.documentElement.scrollTop;
    
    // Device detection (will be initialized in init() based on CONFIG or defaults)
    static isMobile = false;
    static isTablet = false;
    static isDesktop = false;
    
    // UI state
    static headerScroll = {
        current: 0,
        previous: 0,
        direction: 'down'
    };
    
    // Module management
    static activeModules = new Set();
    static initializedModules = new Map();
    
    // External library instances
    static swiperInstances = new Map();
    static owlCarouselInstances = new Map(); // Changed from Array to Map for consistency
    static glightboxInstance = null;
    
    // SSE connections
    static sseConnections = new Set();
    static activeSSEConnections = new Set();
    static sseManager = null;
    static notificationSystem = null;
    
    // DOM cache
    static domCache = new Map();
    
    // Error tracking
    static errors = [];
    
    // User session
    static user = {
        isAuthenticated: false,
        username: null,
        permissions: []
    };
    
    // Page state
    static page = {
        title: document.title,
        url: window.location.href,
        referrer: document.referrer
    };
    
    // Performance tracking
    static performance = {
        loadTime: null,
        lastResize: Date.now(),
        lastScroll: Date.now(),
        eventCounts: new Map()
    };
    
    // ============================================
    // INITIALIZATION METHODS
    // ============================================
    
    /**
     * Initialize application state
     */
    static init(config = null) {
        if (this.initialized) {
            console.warn('AppState already initialized');
            return;
        }
        
        console.log('📊 Initializing application state...');
        
        // Use provided config or defaults
        const breakpoints = config?.breakpoints || {
            md: 768,
            lg: 1024
        };
        
        // Update initial state
        this.updateWindowSize();
        this.detectDevice(breakpoints);
        this.updateScrollPosition();
        
        // Initialize performance tracking
        this.performance.loadTime = Date.now();
        
        // Setup event listeners
        this.setupEventListeners();
        
        this.initialized = true;
        console.log('✅ Application state initialized');
    }
    
    /**
     * Setup event listeners for state updates
     */
    static setupEventListeners() {
        // Update on resize
        window.addEventListener('resize', () => {
            this.updateWindowSize();
        });
        
        // Update on scroll
        window.addEventListener('scroll', () => {
            this.updateScrollPosition();
        });
        
        // Handle page visibility changes
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                this.updateWindowSize();
            }
        });
        
        // Performance monitoring
        if (performance.memory) {
            setInterval(() => {
                this.trackEvent('memory_check');
            }, 60000); // Every minute
        }
    }
    
    // ============================================
    // STATE MANAGEMENT METHODS
    // ============================================
    
    /**
     * Update window size
     */
    static updateWindowSize() {
        this.windowWidth = window.innerWidth;
        this.windowHeight = window.innerHeight;
        this.performance.lastResize = Date.now();
        
        // Detect device type if breakpoints are available
        this.detectDevice();
    }
    
    /**
     * Detect device type based on breakpoints
     */
    static detectDevice(breakpoints = null) {
        const bp = breakpoints || {
            md: 768,
            lg: 1024
        };
        
        this.isMobile = this.windowWidth <= bp.md;
        this.isTablet = this.windowWidth > bp.md && this.windowWidth <= bp.lg;
        this.isDesktop = this.windowWidth > bp.lg;
    }
    
    /**
     * Update scroll position
     */
    static updateScrollPosition() {
        const newPosition = window.pageYOffset || document.documentElement.scrollTop;
        
        // Update header scroll tracking
        this.headerScroll.previous = this.headerScroll.current;
        this.headerScroll.current = newPosition;
        this.headerScroll.direction = newPosition > this.headerScroll.previous ? 'down' : 'up';
        
        this.scrollPosition = newPosition;
        this.performance.lastScroll = Date.now();
    }
    
    /**
     * Track event count
     */
    static trackEvent(eventName) {
        const count = this.performance.eventCounts.get(eventName) || 0;
        this.performance.eventCounts.set(eventName, count + 1);
    }
    
    // ============================================
    // MODULE MANAGEMENT METHODS
    // ============================================
    
    /**
     * Register module
     */
    static registerModule(name, module = null) {
        this.activeModules.add(name);
        if (module) {
            this.initializedModules.set(name, module);
        }
    }
    
    /**
     * Unregister module
     */
    static unregisterModule(name) {
        this.activeModules.delete(name);
        this.initializedModules.delete(name);
    }
    
    /**
     * Check if module is active
     */
    static hasModule(name) {
        return this.activeModules.has(name);
    }
    
    /**
     * Get module instance
     */
    static getModule(name) {
        return this.initializedModules.get(name);
    }
    
    /**
     * Add active module (alias for registerModule)
     */
    static addModule(name) {
        this.registerModule(name);
    }
    
    /**
     * Remove active module (alias for unregisterModule)
     */
    static removeModule(name) {
        this.unregisterModule(name);
    }
    
    // ============================================
    // USER SESSION MANAGEMENT
    // ============================================
    
    /**
     * Set user information
     */
    static setUser(userData) {
        this.user = { ...this.user, ...userData };
    }
    
    /**
     * Clear user information
     */
    static clearUser() {
        this.user = {
            isAuthenticated: false,
            username: null,
            permissions: []
        };
    }
    
    // ============================================
    // PAGE STATE MANAGEMENT
    // ============================================
    
    /**
     * Update page state
     */
    static updatePageState(state) {
        this.page = { ...this.page, ...state };
    }
    
    // ============================================
    // ERROR MANAGEMENT METHODS
    // ============================================
    
    /**
     * Add error to state
     */
    static addError(error, context = {}) {
        const errorData = {
            message: error.message || String(error),
            stack: error.stack,
            timestamp: new Date().toISOString(),
            url: window.location.href,
            userAgent: navigator.userAgent,
            ...context
        };
        
        this.errors.push(errorData);
        
        // Keep only last 50 errors
        if (this.errors.length > 50) {
            this.errors.shift();
        }
        
        // Log error in development
        if (process.env.NODE_ENV === 'development') {
            console.error('AppState Error:', errorData);
        }
        
        return errorData;
    }
    
    /**
     * Get errors
     */
    static getErrors(limit = 10) {
        return this.errors.slice(-limit);
    }
    
    /**
     * Clear errors
     */
    static clearErrors() {
        this.errors = [];
    }
    
    // ============================================
    // SSE MANAGEMENT METHODS
    // ============================================
    
    /**
     * Add SSE connection
     */
    static addSSEConnection(connectionId) {
        this.sseConnections.add(connectionId);
        this.activeSSEConnections.add(connectionId);
    }
    
    /**
     * Remove SSE connection
     */
    static removeSSEConnection(connectionId) {
        this.activeSSEConnections.delete(connectionId);
    }
    
    /**
     * Check if SSE connection is active
     */
    static hasSSEConnection(connectionId = null) {
        if (connectionId) {
            return this.activeSSEConnections.has(connectionId);
        }
        return this.activeSSEConnections.size > 0;
    }
    
    // ============================================
    // INSTANCE MANAGEMENT METHODS
    // ============================================
    
    /**
     * Add Swiper instance
     */
    static addSwiperInstance(id, instance) {
        this.swiperInstances.set(id, instance);
    }
    
    /**
     * Remove Swiper instance
     */
    static removeSwiperInstance(id) {
        this.swiperInstances.delete(id);
    }
    
    /**
     * Get Swiper instance
     */
    static getSwiperInstance(id) {
        return this.swiperInstances.get(id);
    }
    
    /**
     * Get all Swiper instances
     */
    static getSwiperInstances() {
        return Array.from(this.swiperInstances.entries());
    }
    
    /**
     * Add Owl Carousel instance
     */
    static addOwlCarouselInstance(id, instance) {
        this.owlCarouselInstances.set(id, instance);
    }
    
    /**
     * Remove Owl Carousel instance
     */
    static removeOwlCarouselInstance(id) {
        this.owlCarouselInstances.delete(id);
    }
    
    /**
     * Get Owl Carousel instance
     */
    static getOwlCarouselInstance(id) {
        return this.owlCarouselInstances.get(id);
    }
    
    /**
     * Set Glightbox instance
     */
    static setGlightboxInstance(instance) {
        this.glightboxInstance = instance;
    }
    
    // ============================================
    // DOM CACHE METHODS
    // ============================================
    
    /**
     * Get DOM element from cache or query
     */
    static getElement(selector, context = document) {
        // Always query fresh if no cache support
        return context.querySelector(selector);
    }
    
    /**
     * Get all DOM elements
     */
    static getElements(selector, context = document) {
        return Array.from(context.querySelectorAll(selector));
    }
    
    /**
     * Clear DOM cache
     */
    static clearDOMCache() {
        this.domCache.clear();
    }
    
    /**
     * Invalidate cache entry
     */
    static invalidateCacheEntry(selector, context = document) {
        const cacheKey = `${selector}_${context === document ? 'doc' : context.id || 'ctx'}`;
        this.domCache.delete(cacheKey);
    }
    
    // ============================================
    // RESET AND CLEANUP METHODS
    // ============================================
    
    /**
     * Reset application state
     */
    static reset() {
        // Clear collections
        this.activeModules.clear();
        this.initializedModules.clear();
        this.sseConnections.clear();
        this.activeSSEConnections.clear();
        this.swiperInstances.clear();
        this.owlCarouselInstances.clear();
        this.errors = [];
        this.domCache.clear();
        this.performance.eventCounts.clear();
        
        // Reset instance references
        this.glightboxInstance = null;
        this.sseManager = null;
        this.notificationSystem = null;
        
        // Clear user data
        this.clearUser();
        
        // Keep window size detection
        this.updateWindowSize();
        
        // Keep scroll position
        this.updateScrollPosition();
        
        console.log('🔄 Application state reset');
    }
    
    /**
     * Get state snapshot
     */
    static getSnapshot() {
        return {
            initialized: this.initialized,
            windowSize: {
                width: this.windowWidth,
                height: this.windowHeight,
                isMobile: this.isMobile,
                isTablet: this.isTablet,
                isDesktop: this.isDesktop
            },
            scroll: {
                position: this.scrollPosition,
                headerDirection: this.headerScroll.direction
            },
            connections: {
                sse: Array.from(this.sseConnections),
                activeSSE: Array.from(this.activeSSEConnections)
            },
            modules: Array.from(this.activeModules),
            user: { ...this.user },
            page: { ...this.page },
            instances: {
                swiper: this.swiperInstances.size,
                owlCarousel: this.owlCarouselInstances.size,
                hasGlightbox: !!this.glightboxInstance
            },
            errors: this.errors.length,
            performance: this.getPerformanceStats()
        };
    }
    
    // ============================================
    // STATISTICS AND DEBUGGING METHODS
    // ============================================
    
    /**
     * Get performance statistics
     */
    static getPerformanceStats() {
        const now = Date.now();
        const loadTime = this.performance.loadTime ? now - this.performance.loadTime : null;
        
        return {
            loadTime: loadTime,
            lastResize: this.performance.lastResize,
            lastScroll: this.performance.lastScroll,
            eventCounts: Object.fromEntries(this.performance.eventCounts),
            domCacheSize: this.domCache.size,
            memory: performance.memory ? {
                usedJSHeapSize: Math.round(performance.memory.usedJSHeapSize / 1048576) + ' MB',
                totalJSHeapSize: Math.round(performance.memory.totalJSHeapSize / 1048576) + ' MB',
                jsHeapSizeLimit: Math.round(performance.memory.jsHeapSizeLimit / 1048576) + ' MB'
            } : null
        };
    }
    
    /**
     * Get complete state statistics
     */
    static getStats() {
        const perfStats = this.getPerformanceStats();
        
        return {
            app: {
                initialized: this.initialized,
                environment: process.env.NODE_ENV || 'development'
            },
            window: {
                width: this.windowWidth,
                height: this.windowHeight
            },
            device: {
                isMobile: this.isMobile,
                isTablet: this.isTablet,
                isDesktop: this.isDesktop
            },
            scroll: {
                position: this.scrollPosition,
                direction: this.headerScroll.direction,
                lastUpdate: perfStats.lastScroll
            },
            modules: {
                active: Array.from(this.activeModules),
                total: this.activeModules.size
            },
            connections: {
                sse: this.activeSSEConnections.size,
                total: this.sseConnections.size
            },
            instances: {
                swiper: this.swiperInstances.size,
                owlCarousel: this.owlCarouselInstances.size,
                glightbox: this.glightboxInstance ? 1 : 0
            },
            errors: this.errors.length,
            performance: perfStats
        };
    }
    
    /**
     * Get state as JSON for debugging
     */
    static toJSON() {
        return {
            ...this.getStats(),
            modules: Array.from(this.activeModules),
            sseConnections: Array.from(this.sseConnections),
            activeSSEConnections: Array.from(this.activeSSEConnections),
            recentErrors: this.errors.slice(-5), // Last 5 errors only
            user: this.user,
            page: this.page
        };
    }
    
    /**
     * Log state summary
     */
    static logSummary() {
        const stats = this.getStats();
        console.group('📊 Application State Summary');
        console.log('Initialized:', stats.app.initialized);
        console.log('Environment:', stats.app.environment);
        console.log('Window Size:', `${stats.window.width} x ${stats.window.height}`);
        console.log('Device:', stats.device.isMobile ? 'Mobile' : stats.device.isTablet ? 'Tablet' : 'Desktop');
        console.log('Scroll Position:', stats.scroll.position);
        console.log('Active Modules:', stats.modules.total);
        console.log('SSE Connections:', stats.connections.sse);
        console.log('Swiper Instances:', stats.instances.swiper);
        console.log('Errors:', stats.errors);
        console.log('Performance:');
        console.log('  - Load Time:', stats.performance.loadTime ? stats.performance.loadTime + 'ms' : 'N/A');
        console.log('  - DOM Cache Size:', stats.performance.domCacheSize);
        console.groupEnd();
    }
    
    /**
     * Export state for debugging
     */
    static export() {
        return {
            snapshot: this.getSnapshot(),
            stats: this.getStats(),
            details: this.toJSON()
        };
    }
}

// Auto-initialize AppState when DOM is ready if not already initialized
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        if (!AppState.initialized) {
            AppState.init();
        }
    });
} else if (!AppState.initialized) {
    AppState.init();
}

// Make AppState globally available for debugging
if (process.env.NODE_ENV === 'development' || window.location.search.includes('debug=state')) {
    window.AppState = AppState;
    console.log('🔧 AppState available globally for debugging');
}

export default AppState;