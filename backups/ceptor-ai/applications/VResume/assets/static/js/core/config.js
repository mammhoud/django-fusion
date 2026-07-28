// ── Environment detection ──────────────────────────────────────

const isDevelopment = typeof process !== 'undefined' && process.env?.NODE_ENV === 'development';
const isProduction  = typeof process !== 'undefined' && process.env?.NODE_ENV === 'production';

// ── Layout types ──────────────────────────────────────────────

export const LAYOUT_TYPES = {
    VCARD: 'vcard',
    LANDING: 'landing',
};

// ── Layout configuration ──────────────────────────────────────

export const LAYOUT_CONFIG = {
    [LAYOUT_TYPES.VCARD]: {
        name: 'vResume Layout',
        description: 'Portfolio vResume with sidebar + tab navigation',
        requiredModules: ['utility', 'navigation', 'components'],
        optionalModules: ['forms', 'animations'],
        cssClass: 'layout-vcard',
        autoInitialize: true,
        dependencies: [],
        priority: 1,
        pageTypes: {
            ABOUT:     'about',
            RESUME:    'resume',
            PORTFOLIO: 'portfolio',
            BLOG:      'blog',
            CONTACT:   'contact',
        },
    },
    [LAYOUT_TYPES.LANDING]: {
        name: 'Landing Layout',
        description: 'Public landing / marketing pages',
        requiredModules: ['utility', 'navigation'],
        optionalModules: ['components', 'animations'],
        cssClass: 'layout-landing',
        autoInitialize: true,
        dependencies: [],
        priority: 2,
        pageTypes: {
            HOME:    'home',
            CONTACT: 'contact',
            ABOUT:   'about',
            BLOG:    'blog',
        },
    },
};

// ── vResume tab sub-types ───────────────────────────────────────

export const VCARD_SUB_TYPES = {
    '/about':     'about',
    '/resume':    'resume',
    '/portfolio': 'portfolio',
    '/blog':      'blog',
    '/contact':   'contact',
};



export const DEFAULT_LAYOUT = LAYOUT_TYPES.VCARD;

// ── ConfigHelpers ─────────────────────────────────────────────

export const ConfigHelpers = {
    isDevelopment: () => isDevelopment,
    isProduction:  () => isProduction,

    getCookieConfig: (options = {}) => ({
        path: '/',
        secure: isProduction,
        sameSite: 'Lax',
        maxAge: 31536000,
        ...options,
    }),

    getCSRFConfig: () => ({
        tokenName:      'csrftoken',
        headerName:     'X-CSRFToken',
        metaName:       'csrf-token',
        cookiePath:     '/',
        cookieSecure:   isProduction,
        cookieSameSite: 'Lax',
    }),

    /** Detect layout type from URL path */
    detectLayoutFromURL: (path = window.location.pathname) => {
        for (const [pattern, layout] of Object.entries(LAYOUT_CONFIG)) {
            if (pattern === path) return layout;
            if (pattern.includes('.*')) {
                if (new RegExp(`^${pattern}`).test(path)) return layout;
            }
        }
        return DEFAULT_LAYOUT;
    },

    /** Detect vResume tab sub-type from URL path */
    detectSubTypeFromURL: (path = window.location.pathname) => {
        for (const [subPath, subType] of Object.entries(VCARD_SUB_TYPES)) {
            if (path.startsWith(subPath)) return subType;
        }
        const segments = path.split('/').filter(Boolean);
        return segments.length > 0 ? segments[0] : null;
    },

    getLayoutConfig: (layout = DEFAULT_LAYOUT) =>
        LAYOUT_CONFIG[layout] || LAYOUT_CONFIG[DEFAULT_LAYOUT],

    getPageType: (layout = DEFAULT_LAYOUT, subType = null) => {
        const config = ConfigHelpers.getLayoutConfig(layout);
        if (subType && config.pageTypes?.[subType.toUpperCase()]) {
            return config.pageTypes[subType.toUpperCase()];
        }
        return layout;
    },

    /** Apply layout CSS classes to <body> */
    applyLayoutClasses: (layout = DEFAULT_LAYOUT, subType = null, prefix = 'layout-') => {
        const body = document.body;
        body.classList.forEach(cls => {
            if (cls.startsWith(prefix)) body.classList.remove(cls);
        });
        if (layout)  body.classList.add(`${prefix}${layout}`);
        if (subType) body.classList.add(`${prefix}${subType}`);
        document.dispatchEvent(new CustomEvent('layout:changed', { detail: { layout, subType } }));
    },

    /** Detect which vResume components are present in the DOM */
    detectPageComponents: () => {
        const selectors = {
            sidebar:       '[data-sidebar]',
            navbar:        '[data-vcard-nav]',
            portfolio:     '[data-portfolio], .portfolio-grid',
            portfolioFilter: '[data-filter-btn]',
            contactForm:   '[data-form]',
            testimonials:  '[data-testimonials-item]',
            accordion:     '.accordion, [data-accordion]',
            tabs:          '[data-tabs], .nav-tabs',
            modal:         '[data-modal], .modal-container',
            progress:      '.progress-bar, .animated-progress',
            masonry:       '.masonry, [data-masonry]',
            slider:        '[data-swiper], .swiper',
            counter:       '[data-counter]',
        };

        const components = new Set();
        const elements   = new Map();

        for (const [name, selector] of Object.entries(selectors)) {
            const found = document.querySelectorAll(selector);
            if (found.length > 0) {
                components.add(name);
                elements.set(name, Array.from(found));
            }
        }

        return { components, elements };
    },

    determinePageType: () => {
        const path   = window.location.pathname;
        const layout  = ConfigHelpers.detectLayoutFromURL(path);
        const subType = ConfigHelpers.detectSubTypeFromURL(path);
        return ConfigHelpers.getPageType(layout, subType);
    },

    getCurrentBreakpoint: () => {
        const w = window.innerWidth;
        if (w >= 1400) return 'xxl';
        if (w >= 1200) return 'xl';
        if (w >= 992)  return 'lg';
        if (w >= 768)  return 'md';
        if (w >= 576)  return 'sm';
        return 'xs';
    },

    getRequiredModulesForLayout: (layout = DEFAULT_LAYOUT) =>
        ConfigHelpers.getLayoutConfig(layout)?.requiredModules || [],

    getOptionalModulesForLayout: (layout = DEFAULT_LAYOUT) =>
        ConfigHelpers.getLayoutConfig(layout)?.optionalModules || [],

    shouldLoadModule: (moduleName, layout = DEFAULT_LAYOUT) => {
        const required = ConfigHelpers.getRequiredModulesForLayout(layout);
        const optional = ConfigHelpers.getOptionalModulesForLayout(layout);
        return required.includes(moduleName) || optional.includes(moduleName);
    },

    initializeLayoutSystem: (options = {}) => {
        const { enabled = true, autoApplyClasses = true, bodyClassPrefix = 'layout-' } = options;
        if (!enabled) return null;

        const layout  = ConfigHelpers.detectLayoutFromURL();
        const subType = ConfigHelpers.detectSubTypeFromURL();

        if (autoApplyClasses) {
            ConfigHelpers.applyLayoutClasses(layout, subType, bodyClassPrefix);
        }

        return { layout, subType, config: ConfigHelpers.getLayoutConfig(layout) };
    },
};

// ── Global Application Configuration ───────────────────────────

const isDev = ConfigHelpers.isDevelopment();

/**
 * Global Application Configuration
 * @type {Object}
 */
export const CONFIG = {
    version:     '1.0.0',
    debug:       isDev,
    basePath:    '/',
    environment: isDev ? 'development' : 'production',

    // ── Layout ────────────────────────────────────────────────
    layout: {
        enabled:          true,
        autoDetect:       true,
        autoApplyClasses: true,
        defaultLayout:    DEFAULT_LAYOUT,
        currentLayout:    null,
        subType:          null,
        bodyClassPrefix:  'layout-',
        vcardSubTypes:    VCARD_SUB_TYPES,
    },

    // ── Security / CSRF ───────────────────────────────────────
    security: {
        csrf: {
            tokenName:      'csrftoken',
            headerName:     'X-CSRFToken',
            metaName:       'csrf-token',
            cookiePath:     '/',
            cookieSecure:   !isDev,
            cookieSameSite: 'Lax',
        },
        cookies: {
            language: 'language',
            theme:    'theme',
            consent:  'cookie_consent',
            session:  'sessionid',
            path:     '/',
            maxAge:   31536000,
            secure:   !isDev,
            sameSite: 'Lax',
        },
    },

    // ── SSE — real-time notifications ─────────────────────────
    // Only active on pages that have a notification endpoint
    sse: {
        enabled:              true,
        channelPath:          '/sse/notifications/',
        maxReconnectAttempts: 5,
        reconnectDelay:       3000,
        heartbeatInterval:    30000,
        connectionTimeout:    3600000,
        autoConnect:          false,   // connect only when explicitly requested
    },

    // ── Notification system ───────────────────────────────────
    notifications: {
        defaultDuration:     5000,
        maxNotifications:    5,
        enableSSE:           true,
        enableHTMX:          true,
        showConnectionStatus: false,
        containerId:         'notification-container',
        position:            'top-right',
    },

    // ── Module loader ─────────────────────────────────────────
    modules: {
        autoInitialize: true,
        lazyLoad:       true,
        loadOrder:      ['utility', 'navigation', 'components', 'forms'],
        dependencies: {
            portfolio:  ['utility'],
            masonry:    ['utility'],
            accordion:  ['utility'],
            forms:      ['utility'],
            navigation: ['utility'],
        },
    },

    // ── Preloader ─────────────────────────────────────────────
    preloader: {
        types:   ['1', '2', '3'],
        autoHide: true,
        delay:    500,
    },

    // ── Runtime page state (populated on DOMContentLoaded) ────
    page: {
        type:       null,
        components: new Set(),
        elements:   new Map(),
        has:        () => false,
    },
};

// Populate runtime page state on DOM ready
if (typeof window !== 'undefined') {
    window.addEventListener('DOMContentLoaded', () => {
        const pageData = ConfigHelpers.detectPageComponents();
        CONFIG.page.type       = ConfigHelpers.determinePageType();
        CONFIG.page.components = pageData.components;
        CONFIG.page.elements   = pageData.elements;
        CONFIG.page.has        = (c) => pageData.components.has(c);
    });
}

export default { CONFIG, ConfigHelpers };
