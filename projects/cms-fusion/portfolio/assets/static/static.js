// ═══════════════════════════════════════════════════════════════
// CORE LIBRARIES
// ═══════════════════════════════════════════════════════════════

import $ from 'jquery';
window.jQuery = $;
window.$ = $;

import 'bootstrap/dist/js/bootstrap.bundle.min.js';

// ═══════════════════════════════════════════════════════════════
// HTMX & EXTENSIONS (Shared across all bundles)
// ═══════════════════════════════════════════════════════════════

import 'htmx.org';
import 'htmx-ext-sse';

// ═══════════════════════════════════════════════════════════════
// REACTIVE FRAMEWORK
// ═══════════════════════════════════════════════════════════════

import 'alpinejs';

// ═══════════════════════════════════════════════════════════════
// UI LIBRARIES
// ═══════════════════════════════════════════════════════════════

import AOS from 'aos';
import GLightbox from 'glightbox';
import Swiper from 'swiper/bundle';

// Attach to window for global access
window.AOS = AOS;
window.GLightbox = GLightbox;
window.Swiper = Swiper;

// ═══════════════════════════════════════════════════════════════
// VRESUME APPLICATION (All modules, components, services)
// ═══════════════════════════════════════════════════════════════

import {
  app,
  CONFIG,
  ConfigHelpers,
  Application,
  RegistryManager,
  registry,
  BaseManager,
  DOM,
  Utils,
  URLTrackerMixin,
  CookieManagerHandler,
  EventManagerHandler,
  SSEHandler,
  NotificationSystem,
  UIManager,
  NavigationTracker,
  moduleManager
} from './js/index.js';

// Expose to window for debugging
if (CONFIG.debug) {
  window.APP_CONFIG = CONFIG;
  window.VResume = {
    app,
    CONFIG,
    ConfigHelpers,
    registry,
    DOM,
    Utils,
    moduleManager,
    UIManager
  };
}

// ═══════════════════════════════════════════════════════════════
// INITIALIZATION
// ═══════════════════════════════════════════════════════════════

async function initialize() {
  try {
    console.log('🚀 Initializing Static Bundle...');

    // Initialize cookie manager first (for theme detection)
    const cookieManager = new CookieManagerHandler();
    await cookieManager.init();
    console.log('🍪 Cookie Manager initialized');

    // Initialize application
    await app.init();
    console.log('✅ Static Bundle Ready');
  } catch (error) {
    console.error('❌ Initialization Error:', error);
  }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initialize);
} else {
  initialize();
}

// ═══════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════

export {
  app,
  CONFIG,
  ConfigHelpers,
  Application,
  RegistryManager,
  registry,
  BaseManager,
  DOM,
  Utils,
  URLTrackerMixin,
  CookieManagerHandler,
  EventManagerHandler,
  SSEHandler,
  NotificationSystem,
  UIManager,
  NavigationTracker,
  moduleManager
};

export default { app, CONFIG };
