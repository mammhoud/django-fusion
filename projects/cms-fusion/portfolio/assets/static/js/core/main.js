"use strict";

// ── Core ──────────────────────────────────────────────────────
import $ from 'jquery';
window.jQuery = $;
window.$ = $;

import 'bootstrap/dist/js/bootstrap.bundle.min.js';

// ── Bootbox (modal dialogs + cookie consent, built on Bootstrap) ──
import bootbox from 'shared/js/utility/bootbox-shim.js';
window.bootbox = bootbox;
import { showCookieConsent, showPolicyModal } from './bootbox-modals.js';

// ── HTMX ──────────────────────────────────────────────────────
import 'htmx.org';
import 'htmx-ext-sse';

// ── Alpine.js ─────────────────────────────────────────────────
// CRITICAL: Register ALL Alpine.data() components BEFORE Alpine.start()
// Alpine evaluates x-data expressions immediately on start(), so any
// component referenced in HTML must already be registered here.
import Alpine from 'alpinejs';
window.Alpine = Alpine;

import { filterableList } from '../components/search/filterable-list.js';
Alpine.data('filterableList', filterableList);

// ── UI Libraries ──────────────────────────────────────────────
import AOS from 'aos';
import GLightbox from 'glightbox';
import Swiper from 'swiper/bundle';
import 'swiper/css/bundle';

window.AOS       = AOS;
window.GLightbox = GLightbox;
window.Swiper    = Swiper;

// ── Application ───────────────────────────────────────────────
import { CONFIG } from './config.js';
import { app } from './app.js';
import { uiManager } from '../components/index.js';

if (CONFIG.debug) {
    window.APP_CONFIG = CONFIG;
}

// ==========================================
// VRESUME COMPONENT INITIALIZATION
// ==========================================




function initializeVResume() {
    try {
        uiManager.init();
        if (window.APP_CONFIG?.debug) {
            window.uiManager = uiManager;
        }
    } catch (error) {
        console.error('❌ Failed to initialize VResume components:', error);
    }
}



// Cookie consent & policy helpers moved to core/bootbox-modals.js

// ==========================================
// THEME MANAGEMENT
// ==========================================

const THEME_VARIANTS = {
    'classic-light': { family: 'classic', mode: 'light' },
    'classic-dark':  { family: 'classic', mode: 'dark'  },
    'ocean-light':   { family: 'ocean',   mode: 'light' },
    'ocean-dark':    { family: 'ocean',   mode: 'dark'  },
};

function initTheme() {
    const stored      = localStorage.getItem('vresume_theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const theme       = (stored && THEME_VARIANTS[stored]) ? stored
                      : (prefersDark ? 'classic-dark' : 'classic-light');
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('vresume_theme', theme);
}

function setupThemeFamilySwitcher() {
    document.querySelectorAll('[data-theme-family]').forEach(sw => {
        sw.addEventListener('click', e => {
            e.preventDefault();
            sw.classList.add('active');
            setTimeout(() => sw.classList.remove('active'), 500);
            const family   = sw.getAttribute('data-theme-family');
            const current  = localStorage.getItem('vresume_theme') || 'classic-dark';
            const mode     = THEME_VARIANTS[current]?.mode || 'dark';
            const newTheme = `${family}-${mode}`;
            if (THEME_VARIANTS[newTheme]) {
                localStorage.setItem('vresume_theme', newTheme);
                document.documentElement.setAttribute('data-theme', newTheme);
            }
        });
    });
}

function setupThemeModeSwitcher() {
    document.querySelectorAll('[data-theme-mode]').forEach(sw => {
        sw.addEventListener('click', e => {
            e.preventDefault();
            sw.classList.add('active');
            setTimeout(() => sw.classList.remove('active'), 500);
            const mode     = sw.getAttribute('data-theme-mode');
            const current  = localStorage.getItem('vresume_theme') || 'classic-dark';
            const family   = THEME_VARIANTS[current]?.family || 'classic';
            const newTheme = `${family}-${mode}`;
            if (THEME_VARIANTS[newTheme]) {
                localStorage.setItem('vresume_theme', newTheme);
                document.documentElement.setAttribute('data-theme', newTheme);
            }
        });
    });
}

// ==========================================
// APPLICATION INITIALIZATION
// ==========================================

async function initialize() {
    try {
        // 1. Theme first — sets data-theme before any render
        initTheme();
        setupThemeFamilySwitcher();
        setupThemeModeSwitcher();

        // 2. Start Alpine — all Alpine.data() already registered at module top
        Alpine.start();

        // 3. Main app
        await app.init();

        // 4. VResume components
        initializeVResume();

        // 5. Cookie consent dialog
        showCookieConsent();

        document.dispatchEvent(new Event('app:ready'));
    } catch (error) {
        console.error('❌ Application initialization failed:', error);
        document.dispatchEvent(new CustomEvent('app:init:failed', { detail: { error } }));
        showInitError(error);
    }
}

function showInitError(error) {
    const div = document.createElement('div');
    div.style.cssText = 'position:fixed;top:20px;right:20px;background:#dc3545;color:#fff;padding:15px;border-radius:5px;z-index:9999;max-width:400px;box-shadow:0 2px 10px rgba(0,0,0,.2)';
    div.innerHTML = `<strong>Application Error</strong><p>Failed to initialize: ${error.message || 'Unknown error'}</p><small>Check console for details</small><button style="margin-top:10px;padding:5px 10px;background:#fff;color:#dc3545;border:none;border-radius:3px;cursor:pointer;">Dismiss</button>`;
    document.body.appendChild(div);
    div.querySelector('button').addEventListener('click', () => div.remove());
    setTimeout(() => { if (div.parentNode) div.remove(); }, 10000);
}

// ==========================================
// HTMX INTEGRATION
// ==========================================

// Handle HTMX response errors
document.addEventListener('htmx:responseError', (event) => {
    const xhr = event.detail?.xhr || {};
    const status = xhr.status || 'unknown';
    const statusText = xhr.statusText || 'No status text available';
    const responseURL = xhr.responseURL || window.location.href;

    // Skip error notification for modal-targeted requests (handled by unified modal)
    const target = event.detail?.target;
    if (target && (target.id === 'unified-modal-container' || target.closest?.('#unified-modal-container'))) {
        console.debug('ℹ️ HTMX modal error (handled by unified-modal):', { status, responseURL });
        return;
    }

    console.error('❌ HTMX response error:', {
        status,
        statusText,
        responseURL,
        requestConfig: event.detail?.requestConfig,
    });

    // Show user-friendly error message
    if (status === 502 || status === 503) {
        app.showError('Server unavailable: please try again in a moment.');
    } else if (status >= 500) {
        app.showError('Server error: please try again later.');
    } else if (status >= 400) {
        app.showError('Request error: invalid request or unauthorized.');
    }
});

// Re-initialize VResume components after every HTMX content swap
// (tab navigation, pagination, search results, etc.)
// Using htmx:afterSettle (not afterSwap) ensures DOM is fully settled before component init
document.addEventListener('htmx:afterSettle', (event) => {
    const targetElement = event.detail.target;

    // 0. Clear DOM selector cache to avoid stale references
    if (typeof window.DOM?.clearCache === 'function') {
        window.DOM.clearCache();
    }

    // 1. Initialize any Alpine.js components loaded via HTMX
    if (typeof Alpine?.initTree === 'function') {
        Alpine.initTree(targetElement);
    }

    // Unified modal swaps are handled by the unified-modal component
    // (components/modals/unified-modal.js) — do not convert to Bootbox here.

    // 2. Generic component re-init (sliders, forms, lightbox, etc.)
    console.log('[HTMX] afterSettle → Re-initializing VResume components');
    initializeVResume();

    const landedOnHome = targetElement?.matches?.('[data-page="home"], .home') || targetElement?.querySelector?.('[data-page="home"], .home');
    if (landedOnHome) {
        setTimeout(async () => {
            try {
                if (window.appSliders?.refreshAll) {
                    await window.appSliders.refreshAll();
                    return;
                }
                if (window.uiManager?.refreshComponent) {
                    await window.uiManager.refreshComponent('sliders');
                }
            } catch (error) {
                console.warn('⚠️ Home slider refresh after HTMX swap failed:', error);
            }
        }, 100);
    }
});

// ==========================================
// STARTUP
// ==========================================

if (!window.App?.initialized) {
    document.readyState === 'loading'
        ? document.addEventListener('DOMContentLoaded', () => setTimeout(initialize, 100))
        : setTimeout(initialize, 100);
}

export { app as App, CONFIG };
export function initApp(config = {}) { return app.init(config); }
export function destroyApp()         { return app.destroy(); }

if (CONFIG.debug) window.app = app;
