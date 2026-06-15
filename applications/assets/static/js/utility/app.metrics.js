/**
 * @file app.metrics.js
 * Metrics and Analytics System for Application
 * 
 * Usage:
 * import { MetricsCollector } from './app.metrics.js';
 * 
 * // Initialize metrics collector
 * const metrics = new MetricsCollector(app, {
 *   analytics: {
 *     enabled: true,
 *     provider: 'google-analytics', // or 'matomo', 'custom'
 *     trackingId: 'UA-XXXXX-Y'
 *   },
 *   errorTracking: true,
 *   performanceTracking: true,
 *   userTracking: true
 * });
 * 
 * await metrics.init();
 * 
 * // Track events
 * metrics.track('purchase', { amount: 99.99, currency: 'USD' });
 * metrics.pageView('/products');
 * metrics.error(new Error('Something went wrong'));
 */

export class MetricsCollector {
    constructor(app, config = {}) {
        this.app = app;
        this.config = {
            analytics: {
                enabled: config.analytics?.enabled || false,
                provider: config.analytics?.provider || 'custom',
                trackingId: config.analytics?.trackingId,
                ...config.analytics
            },
            errorTracking: config.errorTracking !== false,
            performanceTracking: config.performanceTracking !== false,
            userTracking: config.userTracking !== false,
            sessionTracking: config.sessionTracking !== false,
            debug: config.debug || false,
            ...config
        };

        this.metrics = {
            events: [],
            errors: [],
            pageViews: [],
            sessions: [],
            performance: [],
            users: new Map()
        };

        this.sessionId = this.generateSessionId();
        this.userId = this.getUserId();
    }

    async init() {
        console.log('📊 Metrics collector initializing...');

        // Setup analytics provider
        if (this.config.analytics.enabled) {
            await this.setupAnalyticsProvider();
        }

        // Setup error tracking
        if (this.config.errorTracking) {
            this.setupErrorTracking();
        }

        // Setup performance tracking
        if (this.config.performanceTracking) {
            this.setupPerformanceTracking();
        }

        // Setup user tracking
        if (this.config.userTracking) {
            this.setupUserTracking();
        }

        // Setup session tracking
        if (this.config.sessionTracking) {
            this.setupSessionTracking();
        }

        // Listen to app events
        this.setupAppListeners();

        console.log('✅ Metrics collector initialized');
    }

    setupAnalyticsProvider() {
        switch (this.config.analytics.provider) {
            case 'google-analytics':
                this.setupGoogleAnalytics();
                break;
            case 'matomo':
                this.setupMatomo();
                break;
            case 'custom':
                // Custom provider - override in child class
                break;
            default:
                console.warn(`Unknown analytics provider: ${this.config.analytics.provider}`);
        }
    }

    setupGoogleAnalytics() {
        if (!this.config.analytics.trackingId) {
            console.warn('Google Analytics tracking ID not provided');
            return;
        }

        // Load Google Analytics script
        const script = document.createElement('script');
        script.async = true;
        script.src = `https://www.googletagmanager.com/gtag/js?id=${this.config.analytics.trackingId}`;
        document.head.appendChild(script);

        // Initialize gtag
        window.dataLayer = window.dataLayer || [];
        window.gtag = function() { dataLayer.push(arguments); };
        window.gtag('js', new Date());
        window.gtag('config', this.config.analytics.trackingId, {
            page_path: window.location.pathname,
            user_id: this.userId,
            session_id: this.sessionId
        });

        this.gtag = window.gtag;
        console.log('✅ Google Analytics initialized');
    }

    setupMatomo() {
        // Matomo implementation
        console.log('📊 Matomo analytics would be initialized here');
    }

    setupErrorTracking() {
        window.addEventListener('error', (event) => {
            this.trackError(event.error || event);
        });

        window.addEventListener('unhandledrejection', (event) => {
            this.trackError(event.reason, 'unhandled_promise_rejection');
        });

        console.log('⚠️ Error tracking enabled');
    }

    setupPerformanceTracking() {
        // Performance monitoring setup
        if (window.performance && window.performance.getEntriesByType) {
            const observer = new PerformanceObserver((list) => {
                list.getEntries().forEach(entry => {
                    this.metrics.performance.push({
                        type: entry.entryType,
                        name: entry.name,
                        duration: entry.duration,
                        startTime: entry.startTime,
                        timestamp: Date.now()
                    });
                });
            });

            observer.observe({ entryTypes: ['navigation', 'resource', 'paint', 'longtask'] });
            this.performanceObserver = observer;
        }

        console.log('📈 Performance tracking enabled');
    }

    setupUserTracking() {
        // Generate or retrieve user ID
        if (!this.userId) {
            this.userId = this.generateUserId();
            localStorage.setItem('metrics_user_id', this.userId);
        }

        // Track user properties
        this.metrics.users.set(this.userId, {
            id: this.userId,
            firstSeen: Date.now(),
            lastSeen: Date.now(),
            userAgent: navigator.userAgent,
            language: navigator.language,
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
        });

        console.log('👤 User tracking enabled');
    }

    setupSessionTracking() {
        this.sessionStart = Date.now();

        // Track session start
        this.metrics.sessions.push({
            id: this.sessionId,
            start: this.sessionStart,
            userId: this.userId,
            entryUrl: window.location.href,
            referrer: document.referrer
        });

        // Update session on visibility change
        document.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'hidden') {
                this.updateSessionEnd();
            }
        });

        // Update session on page unload
        window.addEventListener('beforeunload', () => {
            this.updateSessionEnd();
        });

        console.log('🕒 Session tracking enabled');
    }

    setupAppListeners() {
        // Listen to app events
        this.app.on('app:page:changed', (data) => {
            this.pageView(data.urlState.currentPath);
        });

        this.app.on('app:error', (data) => {
            this.trackError(data.error);
        });

        this.app.on('app:resize', (data) => {
            this.track('viewport_change', {
                width: data.width,
                height: data.height,
                breakpoint: data.breakpoint
            });
        });
    }

    /**
     * Track custom event
     */
    track(event, data = {}) {
        const eventData = {
            event,
            data,
            timestamp: Date.now(),
            userId: this.userId,
            sessionId: this.sessionId,
            url: window.location.href
        };

        // Store locally
        this.metrics.events.push(eventData);

        // Send to analytics provider
        if (this.config.analytics.enabled) {
            this.sendToAnalytics(event, data);
        }

        // Emit metrics event
        this.app.emit('metrics:track', eventData);

        if (this.config.debug) {
            console.log(`📊 Track: ${event}`, data);
        }

        return eventData;
    }

    /**
     * Track page view
     */
    pageView(page, data = {}) {
        const pageViewData = {
            page,
            data,
            timestamp: Date.now(),
            userId: this.userId,
            sessionId: this.sessionId,
            referrer: document.referrer
        };

        this.metrics.pageViews.push(pageViewData);

        // Send to analytics
        if (this.gtag) {
            this.gtag('config', this.config.analytics.trackingId, {
                page_path: page,
                page_title: document.title
            });
        }

        this.app.emit('metrics:pageView', pageViewData);

        return pageViewData;
    }

    /**
     * Track error
     */
    trackError(error, type = 'error') {
        const errorData = {
            type,
            error: error instanceof Error ? {
                message: error.message,
                stack: error.stack,
                name: error.name
            } : error,
            timestamp: Date.now(),
            userId: this.userId,
            sessionId: this.sessionId,
            url: window.location.href
        };

        this.metrics.errors.push(errorData);

        // Send to error tracking service
        this.sendErrorToService(errorData);

        this.app.emit('metrics:error', errorData);

        return errorData;
    }

    sendToAnalytics(event, data) {
        // Send to configured analytics provider
        switch (this.config.analytics.provider) {
            case 'google-analytics':
                if (this.gtag) {
                    this.gtag('event', event, data);
                }
                break;
            case 'matomo':
                // Matomo tracking
                if (window._paq) {
                    window._paq.push(['trackEvent', event, JSON.stringify(data)]);
                }
                break;
            case 'custom':
                // Custom tracking implementation
                break;
        }
    }

    sendErrorToService(errorData) {
        // Send errors to error tracking service (e.g., Sentry, Bugsnag)
        // Implementation depends on the service used
        console.log('Error tracked:', errorData);
    }

    generateSessionId() {
        return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    }

    generateUserId() {
        return `user_${Math.random().toString(36).substr(2, 9)}`;
    }

    getUserId() {
        return localStorage.getItem('metrics_user_id') || this.generateUserId();
    }

    updateSessionEnd() {
        const session = this.metrics.sessions[this.metrics.sessions.length - 1];
        if (session && !session.end) {
            session.end = Date.now();
            session.duration = session.end - session.start;
            this.app.emit('metrics:sessionEnd', session);
        }
    }

    getMetrics() {
        return {
            ...this.metrics,
            sessionId: this.sessionId,
            userId: this.userId,
            totals: {
                events: this.metrics.events.length,
                errors: this.metrics.errors.length,
                pageViews: this.metrics.pageViews.length,
                sessions: this.metrics.sessions.length,
                users: this.metrics.users.size
            }
        };
    }

    destroy() {
        // Cleanup observers
        if (this.performanceObserver) {
            this.performanceObserver.disconnect();
        }

        // Update final session
        this.updateSessionEnd();

        console.log('✅ Metrics collector destroyed');
    }
}// Add these comments to your main app.js where functionality was removed:

/**
 * Note: Performance monitoring has been moved to a separate module.
 * To enable performance monitoring:
 * 
 * 1. Import the PerformanceMonitor:
 *    import { PerformanceMonitor } from './app.performance.js';
 * 
 * 2. Initialize it with your app:
 *    const performanceMonitor = new PerformanceMonitor(app);
 *    await performanceMonitor.init({
 *      enabled: true,
 *      trackResources: true,
 *      trackLongTasks: true
 *    });
 * 
 * 3. Access metrics:
 *    const metrics = performanceMonitor.getMetrics();
 */

/**
 * Note: Event Bus system has been moved to a separate module.
 * To enable the event bus:
 * 
 * 1. Import the EventBus:
 *    import { EventBus } from './app.events.js';
 * 
 * 2. Create and register the event bus:
 *    const eventBus = new EventBus({ debug: true });
 *    app.managers.services.register('events', eventBus);
 * 
 * 3. Use it in your application:
 *    const events = app.getService('events');
 *    events.subscribe('user:action', (data) => { ... });
 *    events.publish('user:action', { action: 'click' });
 */

/**
 * Note: Metrics and Analytics have been moved to a separate module.
 * To enable metrics collection:
 * 
 * 1. Import the MetricsCollector:
 *    import { MetricsCollector } from './app.metrics.js';
 * 
 * 2. Initialize it with your app:
 *    const metricsCollector = new MetricsCollector(app, {
 *      analytics: {
 *        enabled: true,
 *        provider: 'google-analytics',
 *        trackingId: 'UA-XXXXX-Y'
 *      },
 *      errorTracking: true
 *    });
 *    await metricsCollector.init();
 * 
 * 3. Track events:
 *    metricsCollector.track('purchase', { amount: 99.99 });
 *    metricsCollector.pageView('/products');
 */

// Add this in the setupCoreListeners method:
// Commented out performance monitoring - moved to separate module
// if (this.config.performance) {
//   this.setupPerformanceMonitoring(); // See app.performance.js for implementation
// }

// Add this in the init method:
// Commented out event system setup - moved to separate module
// this.setupEventSystem(); // See app.events.js for implementation