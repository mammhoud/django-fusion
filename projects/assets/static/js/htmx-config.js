/**
 * HTMX Configuration
 * Unified HTMX setup across all sites
 * 
 * Provides:
 * - Global configuration
 * - Custom headers
 * - Request/response interceptors
 * - Error handling
 */

(function() {
    'use strict';

    // Only run if HTMX is loaded
    if (!window.htmx) {
        console.warn('HTMX not loaded, skipping configuration');
        return;
    }

    window.app = window.app || {};

    // Configure HTMX
    htmx.config.historyCacheSize = 0;  // Disable history cache to prevent stale content
    htmx.config.refreshOnHistoryMiss = true;  // Refresh on browser back if not in cache
    htmx.config.inlineScriptNonce = '';
    htmx.config.timeout = 10000;  // 10 second timeout
    htmx.config.defaultIndicatorStyle = 'spinner';
    htmx.config.defaultSwapStyle = 'innerHTML';

    /**
     * Get CSRF token from cookies
     */
    function getCsrfToken() {
        return window.app?.getCookie?.('csrftoken') || '';
    }

    /**
     * Setup request headers
     */
    function setupRequestHeaders(xhr) {
        const csrfToken = getCsrfToken();
        if (csrfToken) {
            xhr.setRequestHeader('X-CSRFToken', csrfToken);
        }

        // Add custom headers
        xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
        xhr.setRequestHeader('X-HTMX-Request', 'true');

        // Add application version
        xhr.setRequestHeader('X-App-Version', '1.0.0');

        return xhr;
    }

    /**
     * Handle HTMX errors
     */
    function handleHTMXError(evt) {
        const { xhr, detail } = evt;
        const status = xhr?.status;
        const url = xhr?.responseURL;

        console.error(`HTMX Error: ${status} at ${url}`, detail);

        // Handle specific status codes
        switch (status) {
            case 401:  // Unauthorized
                if (window.app?.showNotification) {
                    window.app.showNotification({
                        title: 'Authentication Required',
                        message: 'Your session has expired. Please log in again.',
                        level: 'warning',
                        duration: 5000
                    });
                }
                // Redirect to login
                setTimeout(() => {
                    window.location.href = '/accounts/login/';
                }, 2000);
                break;

            case 403:  // Forbidden
                if (window.app?.showNotification) {
                    window.app.showNotification({
                        title: 'Access Denied',
                        message: 'You do not have permission to perform this action.',
                        level: 'danger'
                    });
                }
                break;

            case 404:  // Not Found
                if (window.app?.showNotification) {
                    window.app.showNotification({
                        title: 'Not Found',
                        message: 'The requested resource was not found.',
                        level: 'warning'
                    });
                }
                break;

            case 500:  // Server Error
                if (window.app?.showNotification) {
                    window.app.showNotification({
                        title: 'Server Error',
                        message: 'An error occurred on the server. Please try again later.',
                        level: 'danger'
                    });
                }
                break;

            case 0:    // Network error
                if (window.app?.showNotification) {
                    window.app.showNotification({
                        title: 'Connection Error',
                        message: 'Unable to connect to the server. Check your internet connection.',
                        level: 'danger'
                    });
                }
                break;
        }

        // Prevent default error handling to avoid multiple notifications
        evt.preventDefault();
    }

    /**
     * Handle HTMX send event
     */
    function handleHTMXBeforeSend(evt) {
        const xhr = evt.detail.xhr;
        setupRequestHeaders(xhr);
    }

    /**
     * Handle HTMX response event
     */
    function handleHTMXAfterSwap(evt) {
        // Reinitialize Bootstrap components on newly loaded content
        if (window.bootstrap) {
            // Re-initialize tooltips
            document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
                new bootstrap.Tooltip(el);
            });

            // Re-initialize popovers
            document.querySelectorAll('[data-bs-toggle="popover"]').forEach(el => {
                new bootstrap.Popover(el);
            });
        }
    }

    /**
     * Setup default request header configurer
     */
    if (htmx.config.onBeforeSend) {
        const originalOnBeforeSend = htmx.config.onBeforeSend;
        htmx.config.onBeforeSend = (xhr, parameters, element) => {
            originalOnBeforeSend(xhr, parameters, element);
            setupRequestHeaders(xhr);
        };
    } else {
        htmx.config.onBeforeSend = setupRequestHeaders;
    }

    // Setup event listeners
    document.addEventListener('htmx:beforeRequest', handleHTMXBeforeSend);
    document.addEventListener('htmx:responseError', handleHTMXError);
    document.addEventListener('htmx:sendError', handleHTMXError);
    document.addEventListener('htmx:afterSwap', handleHTMXAfterSwap);

    /**
     * Add request logging in development
     */
    if (document.body.classList.contains('debug-mode') || window.DEBUG) {
        document.addEventListener('htmx:beforeRequest', (evt) => {
            const { detail } = evt;
            console.log(
                `%c🔄 HTMX ${detail.verb}%c ${detail.path}`,
                'color: #007bff; font-weight: bold;',
                'color: #666;'
            );
        });

        document.addEventListener('htmx:afterSwap', (evt) => {
            const { detail } = evt;
            console.log(
                `%c✓ Response${detail.xhr.status !== 200 ? ' ' + detail.xhr.status : ''}%c ${detail.xhr.responseURL}`,
                'color: #28a745; font-weight: bold;',
                'color: #666;'
            );
        });

        document.addEventListener('htmx:responseError', (evt) => {
            const { detail } = evt;
            console.error(
                `%c✗ Error ${detail.xhr.status}%c ${detail.xhr.responseURL}`,
                'color: #dc3545; font-weight: bold;',
                'color: #666;'
            );
        });
    }

    // Export HTMX API
    window.app.htmx = htmx;
    window.app.setupRequestHeaders = setupRequestHeaders;

    console.log('✓ HTMX configuration loaded');

})();
