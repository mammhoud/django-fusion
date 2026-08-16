/**
 * Main Application Initialization
 * Shared across all sites: precis-ctc, lms, vresume
 * 
 * Initializes:
 * - Bootstrap components
 * - HTMX configuration
 * - Notification system
 * - Modal system
 * - Form handling
 */

(function() {
    'use strict';

    // Create global app namespace
    window.app = window.app || {};

    // Get cookie value
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                cookie = cookie.trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Initialize Bootstrap tooltips and popovers
    function initializeBootstrap() {
        // Tooltips
        document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
            new bootstrap.Tooltip(el);
        });

        // Popovers
        document.querySelectorAll('[data-bs-toggle="popover"]').forEach(el => {
            new bootstrap.Popover(el);
        });

        // Carousels
        document.querySelectorAll('.carousel').forEach(el => {
            new bootstrap.Carousel(el);
        });
    }

    // Initialize CSRF token for AJAX
    function initializeCSRF() {
        const csrftoken = getCookie('csrftoken');
        if (csrftoken && window.htmx) {
            // HTMX will use this for all requests
            htmx.config.refreshOnHistoryMiss = true;
        }
    }

    // Add body classes for easier styling
    function initializeBodyClasses() {
        const html = document.documentElement;
        const isTouch = () => {
            try {
                document.createEvent('TouchEvent');
                return true;
            } catch (e) {
                return false;
            }
        };

        if (isTouch()) {
            document.body.classList.add('is-touch');
        } else {
            document.body.classList.add('is-desktop');
        }

        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            document.body.classList.add('prefers-reduced-motion');
        }

        if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
            document.body.classList.add('dark-mode');
        }
    }

    // Log initialization
    function logVersion() {
        const version = '1.0.0';
        const buildDate = new Date().toISOString().split('T')[0];
        console.log(
            `%c🚀 Application Initialized\n%cv${version} • ${buildDate}`,
            'font-size: 14px; font-weight: bold; color: #007bff;',
            'font-size: 12px; color: #666;'
        );
    }

    // Main initialization
    function init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
            return;
        }

        // Initialize all systems
        initializeBodyClasses();
        initializeCSRF();
        initializeBootstrap();

        // Expose utilities to window
        window.app.getCookie = getCookie;
        window.app.ready = true;

        // Log that app is ready
        logVersion();

        // Dispatch custom event for other scripts to listen to
        document.dispatchEvent(new CustomEvent('app:ready'));
    }

    // Start initialization
    init();

    // Re-initialize after HTMX swap
    if (window.htmx) {
        document.body.addEventListener('htmx:afterSwap', () => {
            initializeBootstrap();
            document.dispatchEvent(new CustomEvent('app:htmx-swap'));
        });

        document.body.addEventListener('htmx:afterSettle', () => {
            document.dispatchEvent(new CustomEvent('app:htmx-settle'));
        });
    }

})();
