/**
 * @file config.helpers.js
 * Configuration Helpers and Layout Constants
 * Provides utility functions for layout detection, page type determination, and configuration management
 */

// Environment detection
const isDevelopment = typeof process !== 'undefined' && process.env?.NODE_ENV === 'development';
const isProduction = typeof process !== 'undefined' && process.env?.NODE_ENV === 'production';

/**
 * Layout Types
 */
export const LAYOUT_TYPES = {
    LANDING: 'landing',
    APP: 'app',
    FORMS: 'forms',
    NOTIFICATIONS: 'notifications'
};

/**
 * Layout Configuration
 */
export const LAYOUT_CONFIG = {
    [LAYOUT_TYPES.LANDING]: {
        name: 'Landing Layout',
        description: 'Public website layout with marketing pages',
        requiredModules: ['utility', 'styling', 'navigation'],
        optionalModules: ['components', 'modal', 'animations'],
        cssClass: 'layout-landing',
        autoInitialize: true,
        dependencies: [],
        priority: 1,
        pageTypes: {
            HOME: 'home-page',
            CONTACT: 'contact-page',
            ABOUT: 'about-page',
            PRICING: 'pricing-page',
            FEATURES: 'features-page'
        }
    },
    [LAYOUT_TYPES.APP]: {
        name: 'App Layout',
        description: 'Main application interface with navigation and panels',
        requiredModules: ['utility', 'styling', 'navigation', 'components'],
        optionalModules: ['modal', 'forms', 'charts', 'widgets'],
        cssClass: 'layout-app',
        autoInitialize: true,
        dependencies: [],
        priority: 2,
        pageTypes: {
            DASHBOARD: 'dashboard',
            PROFILE: 'profile',
            SETTINGS: 'settings',
            REPORTS: 'reports',
            ANALYTICS: 'analytics'
        }
    },
    [LAYOUT_TYPES.FORMS]: {
        name: 'Forms Layout',
        description: 'Form-intensive pages with validation and steps',
        requiredModules: ['utility', 'styling', 'forms', 'validation'],
        optionalModules: ['modal', 'components', 'wizard'],
        cssClass: 'layout-forms',
        autoInitialize: true,
        dependencies: [],
        priority: 3,
        pageTypes: {
            REGISTRATION: 'registration',
            CHECKOUT: 'checkout',
            APPLICATION: 'application',
            SURVEY: 'survey',
            FEEDBACK: 'feedback'
        }
    },
    [LAYOUT_TYPES.NOTIFICATIONS]: {
        name: 'Notifications Layout',
        description: 'Notification and alert management pages',
        requiredModules: ['utility', 'styling', 'notifications'],
        optionalModules: ['modal', 'components', 'real-time'],
        cssClass: 'layout-notifications',
        autoInitialize: true,
        dependencies: [],
        priority: 4,
        pageTypes: {
            INBOX: 'inbox',
            ALERTS: 'alerts',
            ANNOUNCEMENTS: 'announcements',
            MESSAGES: 'messages',
            ACTIVITY: 'activity'
        }
    }
};

/**
 * Page Type to Layout Mappings
 */
export const PAGE_TYPE_MAPPINGS = {
    // Landing pages
    '/': LAYOUT_TYPES.LANDING,
    '/home': LAYOUT_TYPES.LANDING,
    '/index': LAYOUT_TYPES.LANDING,
    '/contact': LAYOUT_TYPES.LANDING,
    '/about': LAYOUT_TYPES.LANDING,
    '/pricing': LAYOUT_TYPES.LANDING,
    '/features': LAYOUT_TYPES.LANDING,
    '/blog': LAYOUT_TYPES.LANDING,
    '/faq': LAYOUT_TYPES.LANDING,
    
    // App pages
    '/dashboard': LAYOUT_TYPES.APP,
    '/app': LAYOUT_TYPES.APP,
    '/app/.*': LAYOUT_TYPES.APP,
    '/profile': LAYOUT_TYPES.APP,
    '/settings': LAYOUT_TYPES.APP,
    '/reports': LAYOUT_TYPES.APP,
    '/analytics': LAYOUT_TYPES.APP,
    '/admin': LAYOUT_TYPES.APP,
    
    // Form pages
    '/forms': LAYOUT_TYPES.FORMS,
    '/form/.*': LAYOUT_TYPES.FORMS,
    '/register': LAYOUT_TYPES.FORMS,
    '/signup': LAYOUT_TYPES.FORMS,
    '/checkout': LAYOUT_TYPES.FORMS,
    '/apply': LAYOUT_TYPES.FORMS,
    '/survey': LAYOUT_TYPES.FORMS,
    '/feedback': LAYOUT_TYPES.FORMS,
    
    // Notification pages
    '/notifications': LAYOUT_TYPES.NOTIFICATIONS,
    '/alerts': LAYOUT_TYPES.NOTIFICATIONS,
    '/inbox': LAYOUT_TYPES.NOTIFICATIONS,
    '/messages': LAYOUT_TYPES.NOTIFICATIONS,
    '/announcements': LAYOUT_TYPES.NOTIFICATIONS
};

/**
 * App Sub-Types for more specific page identification
 */
export const APP_SUB_TYPES = {
    '/profile': 'profile',
    '/profile/settings': 'profile-settings',
    '/profile/dashboard': 'profile-dashboard',
    '/dashboard': 'dashboard',
    '/settings': 'settings'
};

/**
 * Default Layout
 */
export const DEFAULT_LAYOUT = LAYOUT_TYPES.LANDING;

/**
 * Configuration Helpers Object
 * Provides utility functions for configuration management
 */
export const ConfigHelpers = {
    /**
     * Check if running in development mode
     */
    isDevelopment: () => isDevelopment,
    
    /**
     * Check if running in production mode
     */
    isProduction: () => isProduction,
    
    /**
     * Get cookie configuration
     */
    getCookieConfig: (options = {}) => ({
        path: '/',
        secure: isProduction,
        sameSite: 'Lax',
        maxAge: 31536000, // 1 year
        ...options
    }),
    
    /**
     * Get CSRF configuration
     */
    getCSRFConfig: () => ({
        tokenName: 'csrftoken',
        headerName: 'X-CSRFToken',
        metaName: 'csrf-token',
        cookiePath: '/',
        cookieSecure: isProduction,
        cookieSameSite: 'Lax'
    }),
    
    /**
     * Check if a feature is enabled
     */
    isFeatureEnabled: (featureName, config) => {
        if (config?.features?.[featureName] === undefined) {
            return true; // Default to enabled
        }
        return config.features[featureName];
    },
    
    /**
     * Detect layout type from URL path
     */
    detectLayoutFromURL: (path = window.location.pathname) => {
        // Check exact matches first
        for (const [pattern, layout] of Object.entries(PAGE_TYPE_MAPPINGS)) {
            if (pattern === path) {
                return layout;
            }
            // Check regex patterns
            if (pattern.includes('.*')) {
                const regex = new RegExp(`^${pattern}`);
                if (regex.test(path)) {
                    return layout;
                }
            }
        }
        
        // Check app sub-types
        for (const [subPath] of Object.entries(APP_SUB_TYPES)) {
            if (path.startsWith(subPath)) {
                return LAYOUT_TYPES.APP;
            }
        }
        
        return DEFAULT_LAYOUT;
    },
    
    /**
     * Detect sub-type from URL path
     */
    detectSubTypeFromURL: (path = window.location.pathname) => {
        for (const [subPath, subType] of Object.entries(APP_SUB_TYPES)) {
            if (path.startsWith(subPath)) {
                return subType;
            }
        }
        
        // Extract from path segments
        const segments = path.split('/').filter(s => s);
        return segments.length > 1 ? segments[1] : null;
    },
    
    /**
     * Get layout configuration
     */
    getLayoutConfig: (layout = DEFAULT_LAYOUT) => {
        return LAYOUT_CONFIG[layout] || LAYOUT_CONFIG[DEFAULT_LAYOUT];
    },
    
    /**
     * Get page type based on layout and sub-type
     */
    getPageType: (layout = DEFAULT_LAYOUT, subType = null) => {
        const config = ConfigHelpers.getLayoutConfig(layout);
        
        if (subType && config.pageTypes && config.pageTypes[subType.toUpperCase()]) {
            return config.pageTypes[subType.toUpperCase()];
        }
        
        return layout;
    },
    
    /**
     * Apply layout classes to body element
     */
    applyLayoutClasses: (layout = DEFAULT_LAYOUT, subType = null, prefix = 'layout-') => {
        if (!layout) return;
        
        const body = document.body;
        
        // Remove existing layout classes
        body.classList.forEach(className => {
            if (className.startsWith(prefix)) {
                body.classList.remove(className);
            }
        });
        
        // Add new layout classes
        if (layout) {
            body.classList.add(`${prefix}${layout}`);
        }
        
        if (subType) {
            body.classList.add(`${prefix}${subType}`);
        }
        
        // Dispatch event
        document.dispatchEvent(new CustomEvent('layout:changed', {
            detail: { layout, subType }
        }));
    },
    
    /**
     * Detect page components
     */
    detectPageComponents: () => {
        const selectors = {
            header: '.header, [data-header]',
            menu: '.header-menu, .navbar',
            slider: '.owl-carousel, .swiper, [data-swiper], .carousel',
            masonry: '.masonry, .masonry-grid, [data-masonry]',
            portfolio: '.portfolio-grid, [data-portfolio]',
            accordion: '.accordion, .faq-accordion, [data-accordion]',
            countdown: '.countdown, [data-countdown]',
            counter: '.counter, [data-counter]',
            progress: '.progress-bar, .animated-progress',
            maps: '.gmap, [data-map]',
            forms: 'form[data-validate], [data-form]',
            contactForm: '#contact-form, .contact-form',
            tabs: '.nav-tabs, [data-tabs]',
            modal: '[data-modal], [data-bs-toggle="modal"]'
        };
        
        const components = new Set();
        const elements = new Map();
        
        for (const [name, selector] of Object.entries(selectors)) {
            const found = document.querySelectorAll(selector);
            if (found.length > 0) {
                components.add(name);
                elements.set(name, Array.from(found));
            }
        }
        
        return { components, elements };
    },
    
    /**
     * Determine page type from current URL
     */
    determinePageType: () => {
        const path = window.location.pathname;
        const layout = ConfigHelpers.detectLayoutFromURL(path);
        const subType = ConfigHelpers.detectSubTypeFromURL(path);
        return ConfigHelpers.getPageType(layout, subType);
    },
    
    /**
     * Get current breakpoint
     */
    getCurrentBreakpoint: () => {
        const width = window.innerWidth;
        if (width >= 1400) return 'xxl';
        if (width >= 1200) return 'xl';
        if (width >= 992) return 'lg';
        if (width >= 768) return 'md';
        if (width >= 576) return 'sm';
        return 'xs';
    },
    
    /**
     * Get required modules for a layout
     */
    getRequiredModulesForLayout: (layout = DEFAULT_LAYOUT) => {
        const config = ConfigHelpers.getLayoutConfig(layout);
        return config?.requiredModules || [];
    },
    
    /**
     * Get optional modules for a layout
     */
    getOptionalModulesForLayout: (layout = DEFAULT_LAYOUT) => {
        const config = ConfigHelpers.getLayoutConfig(layout);
        return config?.optionalModules || [];
    },
    
    /**
     * Check if a module should be loaded for a layout
     */
    shouldLoadModule: (moduleName, layout = DEFAULT_LAYOUT) => {
        const required = ConfigHelpers.getRequiredModulesForLayout(layout);
        const optional = ConfigHelpers.getOptionalModulesForLayout(layout);
        return required.includes(moduleName) || optional.includes(moduleName);
    },
    
    /**
     * Initialize layout system
     */
    initializeLayoutSystem: (options = {}) => {
        const {
            enabled = true,
            autoApplyClasses = true,
            bodyClassPrefix = 'layout-'
        } = options;
        
        if (!enabled) return null;
        
        const layout = ConfigHelpers.detectLayoutFromURL();
        const subType = ConfigHelpers.detectSubTypeFromURL();
        
        if (autoApplyClasses) {
            ConfigHelpers.applyLayoutClasses(layout, subType, bodyClassPrefix);
        }
        
        console.log(`🎨 Layout detected: ${layout}${subType ? ` (${subType})` : ''}`);
        
        return {
            layout,
            subType,
            config: ConfigHelpers.getLayoutConfig(layout)
        };
    }
};

export default ConfigHelpers;
