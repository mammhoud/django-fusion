/**
 * @file main.js
 * Simplified Main Application Entry Point
 * Loads core libraries and initializes the application
 */

"use strict";

// ===============================================
// OPTIONAL CORE LIBRARIES
// ===============================================

// // Load jQuery if not already loaded
// if (typeof jQuery === 'undefined') {
//     import('jquery').then($ => {
//         window.jQuery = $;
//         window.$ = $;
//         console.log('✅ jQuery loaded');
//     }).catch(() => {
//         console.warn('⚠️ jQuery failed to load');
//     });
// }

// // Load Bootstrap if needed
// if (typeof bootstrap === 'undefined') {
//     import('bootstrap/dist/js/bootstrap.bundle.min.js').then(() => {
//         console.log('✅ Bootstrap loaded');
//     }).catch(() => {
//         console.warn('⚠️ Bootstrap failed to load');
//     });
// }

// // Load HTMX
// if (typeof htmx === 'undefined') {
//     import('htmx.org').then(() => {
//         console.log('✅ HTMX loaded');
//         // Load SSE extension if needed
//         if (typeof htmx !== 'undefined') {
//             import('htmx-ext-sse').then(() => {
//                 console.log('✅ HTMX SSE extension loaded');
//             });
//         }
//     }).catch(() => {
//         console.warn('⚠️ HTMX failed to load');
//     });
// }
import $ from 'jquery';
window.jQuery = $;
window.$ = $;

import "htmx.org";
import "htmx-ext-sse";
// HTMX component lifecycle bridge (re-initializes sliders, forms, notifications after swaps)
import './htmx-bridge.js';
import { loadThemeVendorPackages } from '../theme/vendor-packages.js';

// Application configuration
import { CONFIG } from './init.config.js';
// Theme system (usecases, plugins, vendors)
import '../theme/index.js';
// Main app instance
import { app } from './app.js';

const themeVendorPackagesReady = loadThemeVendorPackages({ debug: CONFIG.debug });

// Global configuration
if (CONFIG.debug) {
    window.APP_CONFIG = CONFIG;
    console.log('🔧 App config:', CONFIG);
}

// Initialize function
async function initialize() {
    // console.log('🚀 Starting application...');

    try {
        // Load optional libraries
        // await loadOptionalLibraries();

        // Initialize app with config after package-backed theme vendors are available.
        await themeVendorPackagesReady;
        await app.init();

        // console.log('🎉 Application ready!');

        // Dispatch global ready event
        document.dispatchEvent(new Event('app:ready'));

    } catch (error) {
        console.error('❌ Application initialization failed:', error);

        // Dispatch error event
        document.dispatchEvent(new CustomEvent('app:init:failed', {
            detail: { error }
        }));

        // Try to show user-friendly error
        showInitError(error);
    }
}

// Show user-friendly initialization error
function showInitError(error) {
    const errorDiv = document.createElement('div');
    errorDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #dc3545;
        color: white;
        padding: 15px;
        border-radius: 5px;
        z-index: 9999;
        max-width: 400px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    `;

    errorDiv.innerHTML = `
        <strong>Application Error</strong>
        <p>Failed to initialize: ${error.message || 'Unknown error'}</p>
        <small>Check console for details</small>
        <button style="margin-top: 10px; padding: 5px 10px; background: white; color: #dc3545; border: none; border-radius: 3px; cursor: pointer;">
            Dismiss
        </button>
    `;

    document.body.appendChild(errorDiv);

    // Add dismiss button handler
    errorDiv.querySelector('button').addEventListener('click', () => {
        errorDiv.remove();
    });

    // Auto-dismiss after 10 seconds
    setTimeout(() => {
        if (errorDiv.parentNode) {
            errorDiv.remove();
        }
    }, 10000);
}

// Auto-initialize
if (!window.App?.initialized) {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            setTimeout(initialize, 100);
        });
    } else {
        setTimeout(initialize, 100);
    }
}

// Export for module usage
export { app as App, CONFIG };

// Export initialization function for manual control
export function initApp(config = {}) {
    return app.init(config);
}

// Export destroy function for cleanup
export function destroyApp() {
    return app.destroy();
}

// Make app available globally for debugging
if (CONFIG.debug) {
    window.app = app;
}
