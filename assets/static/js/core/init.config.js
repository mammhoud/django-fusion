/**
 * @file init.config.js
 * @description Centralized Application Configuration with Page Detection & Layout Management.
 * This file contains core settings used by the App, ModuleManager, and UI components.
 */

import {
  ConfigHelpers,
  DEFAULT_LAYOUT,
  LAYOUT_TYPES,
} from '../utility/config.helpers.js';

// Re-export so any consumer can import from @core or @utility
export {
  ConfigHelpers,
  DEFAULT_LAYOUT,
  PAGE_TYPE_MAPPINGS,
  APP_SUB_TYPES,
  LAYOUT_TYPES,
} from '../utility/config.helpers.js';

// Environment detection
const isDev = ConfigHelpers.isDevelopment();

/**
 * Global Application Configuration Object
 * @type {Object}
 */
export const CONFIG = {
  /** @type {string} Application version */
  version: '1.0.0',

  /** @type {boolean} Enable debug logging and global access */
  debug: isDev,

  /** @type {string} Base path for the application */
  basePath: '/',

  /** @type {string} Current environment (development|production) */
  environment: isDev ? 'development' : 'production',

  /**
   * Layout & Page State Settings
   * @description Integrated with ConfigHelpers for automatic page and layout detection.
   */
  layout: {
    enabled: true,
    autoDetect: true,
    autoApplyClasses: true,
    defaultLayout: DEFAULT_LAYOUT,
    currentLayout: null,
    subType: null,
    bodyClassPrefix: 'layout-',
    mappings: PAGE_TYPE_MAPPINGS,
    appSubTypes: APP_SUB_TYPES
  },

  /**
   * Security & Session Settings
   * @description Used for CSRF token handling and cookie management.
   */
  security: {
    csrf: {
      tokenName: 'csrftoken',
      headerName: 'X-CSRFToken',
      metaName: 'csrf-token',
      cookiePath: '/',
      cookieSecure: !isDev,
      cookieSameSite: 'Lax'
    },
    cookies: {
      language: 'language',
      theme: 'theme',
      consent: 'cookie_consent',
      session: 'sessionid',
      path: '/',
      maxAge: 31536000,
      secure: !isDev,
      sameSite: 'Lax'
    }
  },

  /**
   * Server-Sent Events (SSE) Settings
   * @description Used by the notification system for real-time updates.
   */
  sse: {
    enabled: true,
    useChannels: false,
    channelPath: '/ws/notifications/',
    maxConnections: 5,
    maxReconnectAttempts: 5,
    reconnectDelay: 3000,
    heartbeatInterval: 30000,
    connectionTimeout: 3600000,
    paths: ['/profile/', '/auth/', '/dashboard/'],
    autoConnect: true
  },

  /**
   * Notification System Settings
   * @description Implemented in modules/notifications/
   */
  notifications: {
    defaultDuration: 5000,
    maxNotifications: 5,
    autoConnect: true,
    enableSSE: true,
    enableHTMX: true,
    showConnectionStatus: true,
    paths: ['/profile/', '/auth/', '/dashboard/'],
    containerId: 'notification-container',
    position: 'top-right'
  },

  /**
   * Module Loader Configuration
   * @description Managed by ModuleManager (modules/manager.init.js)
   */
  modules: {
    autoInitialize: true,
    lazyLoad: true,
    observerEnabled: true,
    dynamicLoading: true,
    loadOrder: ['utility', 'styling', 'navigation', 'components', 'forms', 'pages'],
    dependencies: {
      sliders: ['utility'],
      masonry: ['utility'],
      portfolio: ['masonry'],
      accordion: ['utility'],
      forms: ['utility'],
      navigation: ['utility'],
      pages: ['utility', 'navigation']
    }
  },

  /**
   * Preloader Configuration
   * @description Implemented in modules/components/partials/preloader.init.js
   */
  preloader: {
    /** @type {string[]} Available preloader types */
    types: ['1', '2', '3'],
    /** @type {boolean} Automatically hide when page is ready */
    autoHide: true,
    /** @type {number} Delay before hiding (ms) */
    delay: 500
  },

  /**
   * Runtime Page State
   * @description Populated during DOMContentLoaded by ConfigHelpers.
   */
  page: {
    /** @type {string|null} Detected page type */
    type: null,
    /** @type {Set<string>} Set of detected components on the page */
    components: new Set(),
    /** @type {Map<string, HTMLElement[]>} Map of component names to their DOM elements */
    elements: new Map(),
    /** @type {function(string): boolean} Presence check helper */
    has: () => false
  }
};

/* ---------- runtime initialisations ---------- */
if (typeof window !== 'undefined') {
  window.addEventListener('DOMContentLoaded', () => {
    // Perform automatic detection of page components and type
    const pageData = ConfigHelpers.detectPageComponents();
    CONFIG.page.type = ConfigHelpers.determinePageType();
    CONFIG.page.components = pageData.components;
    CONFIG.page.elements = pageData.elements;
    CONFIG.page.has = (c) => pageData.components.has(c);
  });
}

export default { CONFIG, ConfigHelpers };
