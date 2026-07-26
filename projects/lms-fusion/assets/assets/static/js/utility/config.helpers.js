/**
 * @file utility/config.helpers.js
 * Configuration Helpers, Layout Constants, and Page Detection.
 * Single source of truth used by core/init.config.js and registry.js.
 */

const isDevelopment = typeof process !== 'undefined' && process.env?.NODE_ENV !== 'production';
const isProduction  = !isDevelopment;

// ─────────────────────────────────────────────────────────────────────────────
// CONSTANTS
// ─────────────────────────────────────────────────────────────────────────────

export const LAYOUT_TYPES = {
  LANDING:       'landing',
  APP:           'app',
  AUTH:          'auth',
  FORMS:         'forms',
  NOTIFICATIONS: 'notifications',
  PROFILE:       'profile',
};

export const DEFAULT_LAYOUT = LAYOUT_TYPES.LANDING;

/** URL-path prefix → layout type */
export const PAGE_TYPE_MAPPINGS = {
  '/':              LAYOUT_TYPES.LANDING,
  '/home':          LAYOUT_TYPES.LANDING,
  '/contact':       LAYOUT_TYPES.LANDING,
  '/about':         LAYOUT_TYPES.LANDING,
  '/pricing':       LAYOUT_TYPES.LANDING,
  '/features':      LAYOUT_TYPES.LANDING,
  '/blog':          LAYOUT_TYPES.LANDING,
  '/faq':           LAYOUT_TYPES.LANDING,
  '/dashboard':     LAYOUT_TYPES.APP,
  '/app':           LAYOUT_TYPES.APP,
  '/app/.*':        LAYOUT_TYPES.APP,
  '/profile':       LAYOUT_TYPES.PROFILE,
  '/settings':      LAYOUT_TYPES.APP,
  '/reports':       LAYOUT_TYPES.APP,
  '/analytics':     LAYOUT_TYPES.APP,
  '/admin':         LAYOUT_TYPES.APP,
  '/auth':          LAYOUT_TYPES.AUTH,
  '/login':         LAYOUT_TYPES.AUTH,
  '/register':      LAYOUT_TYPES.AUTH,
  '/signup':        LAYOUT_TYPES.AUTH,
  '/forms':         LAYOUT_TYPES.FORMS,
  '/form/.*':       LAYOUT_TYPES.FORMS,
  '/checkout':      LAYOUT_TYPES.FORMS,
  '/notifications': LAYOUT_TYPES.NOTIFICATIONS,
  '/alerts':        LAYOUT_TYPES.NOTIFICATIONS,
  '/inbox':         LAYOUT_TYPES.NOTIFICATIONS,
  '/messages':      LAYOUT_TYPES.NOTIFICATIONS,
};

/** More-specific sub-type paths inside APP / PROFILE layouts */
export const APP_SUB_TYPES = {
  '/profile':           'profile',
  '/profile/settings':  'profile-settings',
  '/profile/dashboard': 'profile-dashboard',
  '/dashboard':         'dashboard',
  '/settings':          'settings',
};

// ─────────────────────────────────────────────────────────────────────────────
// HELPERS
// ─────────────────────────────────────────────────────────────────────────────

export const ConfigHelpers = {
  isDevelopment: () => isDevelopment,
  isProduction:  () => isProduction,

  detectLayoutFromURL(path = window.location.pathname) {
    for (const [pattern, layout] of Object.entries(PAGE_TYPE_MAPPINGS)) {
      if (pattern === path) return layout;
      if (pattern.includes('.*') && new RegExp(`^${pattern}`).test(path)) return layout;
    }
    for (const subPath of Object.keys(APP_SUB_TYPES)) {
      if (path.startsWith(subPath)) return LAYOUT_TYPES.APP;
    }
    return DEFAULT_LAYOUT;
  },

  detectSubTypeFromURL(path = window.location.pathname) {
    for (const [subPath, subType] of Object.entries(APP_SUB_TYPES)) {
      if (path.startsWith(subPath)) return subType;
    }
    const segments = path.split('/').filter(Boolean);
    return segments.length > 1 ? segments[1] : null;
  },

  determinePageType() {
    const path   = window.location.pathname;
    const layout = this.detectLayoutFromURL(path);
    const sub    = this.detectSubTypeFromURL(path);
    return sub ? `${layout}-${sub}` : layout;
  },

  applyLayoutClasses(layout = DEFAULT_LAYOUT, subType = null, prefix = 'layout-') {
    const body = document.body;
    [...body.classList].filter(c => c.startsWith(prefix)).forEach(c => body.classList.remove(c));
    if (layout)  body.classList.add(`${prefix}${layout}`);
    if (subType) body.classList.add(`${prefix}${subType}`);
    document.dispatchEvent(new CustomEvent('layout:changed', { detail: { layout, subType } }));
  },

  detectPageComponents() {
    const selectors = {
      header:      '.header, [data-header]',
      menu:        '.header-menu, .navbar',
      slider:      '.swiper, [data-swiper], .carousel, .owl-carousel',
      masonry:     '.masonry, [data-masonry]',
      portfolio:   '.portfolio-grid, [data-portfolio]',
      accordion:   '.accordion, [data-accordion]',
      countdown:   '[data-countdown]',
      counter:     '[data-counter]',
      progress:    '.progress-bar, .animated-progress',
      maps:        '.gmap, [data-map]',
      forms:       'form[data-validate], [data-form]',
      contactForm: '#contact-form, .contact-form',
      tabs:        '.nav-tabs, [data-tabs]',
      modal:       '[data-modal], [data-bs-toggle="modal"]',
    };
    const components = new Set();
    const elements   = new Map();
    for (const [name, selector] of Object.entries(selectors)) {
      const found = document.querySelectorAll(selector);
      if (found.length > 0) { components.add(name); elements.set(name, Array.from(found)); }
    }
    return { components, elements };
  },

  getCookieConfig: (options = {}) => ({ path: '/', secure: isProduction, sameSite: 'Lax', maxAge: 31536000, ...options }),
  getCSRFConfig: () => ({ tokenName: 'csrftoken', headerName: 'X-CSRFToken', metaName: 'csrf-token', cookiePath: '/', cookieSecure: isProduction, cookieSameSite: 'Lax' }),
};

export default ConfigHelpers;
