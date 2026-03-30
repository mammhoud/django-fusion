/**
 * @file layouts/notifications/core/notifications.js
 * Unified Notification System with SSE, HTMX, and UI components
 */

export class NotificationSystem {
    constructor(options = {}) {
        this.options = {
            // Display options
            maxNotifications: 5,
            defaultDuration: 5000,
            position: 'top-right',
            useBootstrap: typeof bootstrap !== 'undefined',

            // Real-time options
            useSSE: true,
            useWebSocket: false,
            reconnectAttempts: 5,
            reconnectDelay: 5000,

            // Integration options
            enableHTMX: true,
            enableDjangoMessages: true,

            // UI options
            enableToasts: true,
            enableAlerts: true,
            enableBadges: true,
            enableSounds: false,

            // Debug
            debug: false,

            ...options
        };

        // State
        this.notifications = new Map();
        this.toastInstances = new Map();
        this.unreadCount = 0;
        this.connections = new Map();
        this.handlers = new Map();
        this.queue = [];
        this.initialized = false;

        // Stats
        this.stats = {
            total: 0,
            unread: 0,
            read: 0,
            archived: 0,
            shown: 0,
            clicked: 0
        };

        // Templates
        this.templates = {
            toast: null,
            alert: null,
            badge: null
        };

        this.log = (...args) => {
            if (this.options.debug) console.log('[Notifications]', ...args);
        };
    }

    /* ============================================================
     * INITIALIZATION
     * =========================================================== */

    async init() {
        if (this.initialized) return this;

        this.log('Initializing notification system...');

        try {
            // Setup containers
            this.setupContainers();

            // Setup event listeners
            this.setupEventListeners();

            // Setup templates
            this.setupTemplates();

            // Setup global methods
            this.setupGlobalMethods();

            // Setup integrations
            await this.setupIntegrations();

            // Process existing notifications
            this.processExistingNotifications();

            this.initialized = true;
            this.log('✅ Notification system initialized');

            this.dispatchEvent('notifications:initialized');

        } catch (error) {
            console.error('Failed to initialize notification system:', error);
            throw error;
        }

        return this;
    }

    setupContainers() {
        // Toast container
        if (this.options.enableToasts) {
            let container = document.getElementById('toast-container');
            if (!container) {
                container = document.createElement('div');
                container.id = 'toast-container';
                container.className = 'toast-container position-fixed p-3';
                container.style.cssText = `
                    z-index: 1055;
                    ${this.getPositionStyle(this.options.position)};
                    display: flex;
                    flex-direction: column;
                    gap: 0.5rem;
                `;
                container.setAttribute('aria-live', 'polite');
                container.setAttribute('aria-atomic', 'true');
                document.body.appendChild(container);
            }
            this.containers = { toast: container };
        }

        // Alert container
        if (this.options.enableAlerts) {
            const alertContainer = document.getElementById('alert-container') ||
                document.querySelector('[data-alerts]');
            if (alertContainer) {
                this.containers = { ...this.containers, alert: alertContainer };
            }
        }
    }

    getPositionStyle(position) {
        const positions = {
            'top-right': 'top: 1rem; right: 1rem;',
            'top-left': 'top: 1rem; left: 1rem;',
            'bottom-right': 'bottom: 1rem; right: 1rem;',
            'bottom-left': 'bottom: 1rem; left: 1rem;',
            'top-center': 'top: 1rem; left: 50%; transform: translateX(-50%);',
            'bottom-center': 'bottom: 1rem; left: 50%; transform: translateX(-50%);'
        };
        return positions[position] || positions['top-right'];
    }

    setupTemplates() {
        // Toast template
        this.templates.toast = `
            <div class="toast" role="alert" aria-live="assertive" aria-atomic="true" data-bs-delay="{{ duration }}">
                <div class="toast-header bg-{{ type }} text-white">
                    <i class="{{ icon }} me-2"></i>
                    <strong class="me-auto">{{ title }}</strong>
                    <small class="text-white-50">{{ time }}</small>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
                <div class="toast-body">
                    {{ message }}
                    {{#if actions}}
                    <div class="mt-2 d-flex gap-2">
                        {{#each actions}}
                        <button type="button" class="btn btn-sm btn-outline-light" data-action="{{ action }}" data-notification-id="{{ ../id }}">
                            {{ text }}
                        </button>
                        {{/each}}
                    </div>
                    {{/if}}
                </div>
            </div>
        `;

        // Alert template
        this.templates.alert = `
            <div class="alert alert-{{ type }} alert-dismissible fade show" role="alert">
                <i class="{{ icon }} me-2"></i>
                <strong>{{ title }}</strong>
                <span class="ms-2">{{ message }}</span>
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
    }

    setupEventListeners() {
        // Page visibility
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseAllTimers();
            } else {
                this.resumeAllTimers();
            }
        });

        // Custom events
        document.addEventListener('notification:show', (e) => {
            if (e.detail && !e.detail.processed) {
                this.show(e.detail.message, e.detail.options);
            }
        });

        // Cleanup on page unload
        window.addEventListener('beforeunload', () => {
            this.cleanup();
        });
    }

    setupGlobalMethods() {
        // Notification methods
        window.showNotification = this.show.bind(this);
        window.showToast = this.showToast.bind(this);
        window.showAlert = this.showAlert.bind(this);
        window.clearNotifications = this.clear.bind(this);
        // window.Notification = this.showToast.bind(this);

        // Quick methods
        window.showSuccess = (msg, opts) => this.show(msg, { ...opts, type: 'success' });
        window.showError = (msg, opts) => this.show(msg, { ...opts, type: 'error' });
        window.showWarning = (msg, opts) => this.show(msg, { ...opts, type: 'warning' });
        window.showInfo = (msg, opts) => this.show(msg, { ...opts, type: 'info' });

        // Stats
        window.getNotificationStats = this.getStats.bind(this);
        window.getUnreadCount = this.getUnreadCount.bind(this);

        // Expose instance
        window.notificationSystem = this;
    }

    async setupIntegrations() {
        // HTMX integration
        if (this.options.enableHTMX && typeof htmx !== 'undefined') {
            this.setupHTMXIntegration();
        }

        // Django messages
        if (this.options.enableDjangoMessages) {
            this.processDjangoMessages();
        }

        // Real-time connections
        if (this.options.useSSE) {
            await this.setupSSEConnection();
        }

        if (this.options.useWebSocket) {
            await this.setupWebSocketConnection();
        }
    }

    /* ============================================================
     * NOTIFICATION DISPLAY
     * =========================================================== */

    show(message, options = {}) {
        const config = {
            type: 'info',
            title: '',
            duration: this.options.defaultDuration,
            closable: true,
            display: 'toast',
            actions: [],
            metadata: {},
            id: `notif_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            ...options
        };

        // Validate message
        if (!message) {
            console.warn('Notification message is required');
            return null;
        }

        // Process message
        const processed = this.processMessage(message);

        // Store notification
        const notification = {
            id: config.id,
            message: processed.message,
            type: config.type,
            title: config.title || this.getDefaultTitle(config.type),
            duration: config.duration,
            display: config.display,
            actions: config.actions,
            metadata: config.metadata,
            timestamp: Date.now(),
            read: false,
            shown: false
        };

        this.notifications.set(notification.id, notification);
        this.updateStats();

        // Show based on display type
        switch (config.display) {
            case 'toast':
                return this.showToast(notification);
            case 'alert':
                return this.showAlert(notification);
            case 'inline':
                return this.showInline(notification);
            default:
                return this.showToast(notification);
        }
    }

    processMessage(message) {
        if (typeof message === 'string') {
            try {
                message = JSON.parse(message);
            } catch {
                return {
                    message: message,
                    links: [],
                    sanitized: this.sanitize(message)
                };
            }
        }

        // Process object message
        return {
            message: message.message || message.text || '',
            title: message.title,
            type: message.type || 'info',
            links: this.extractLinks(message.message || ''),
            sanitized: this.sanitize(message.message || '')
        };
    }

    showToast(notification) {
        if (!this.options.enableToasts) return null;

        const toastId = `toast_${notification.id}`;

        // Prepare data
        const data = {
            ...notification,
            icon: this.getIconForType(notification.type),
            time: new Date(notification.timestamp).toLocaleTimeString([], {
                hour: '2-digit',
                minute: '2-digit'
            }),
            duration: notification.duration
        };

        // Render template
        const html = this.renderTemplate(this.templates.toast, data);
        const toastEl = this.createElementFromHTML(html);
        toastEl.id = toastId;

        // Add to container
        if (this.containers.toast) {
            this.containers.toast.appendChild(toastEl);

            // Limit number of toasts
            const toasts = this.containers.toast.querySelectorAll('.toast');
            if (toasts.length > this.options.maxNotifications) {
                toasts[0].remove();
            }
        } else {
            document.body.appendChild(toastEl);
        }

        // Initialize Bootstrap toast if available
        if (this.options.useBootstrap && bootstrap && bootstrap.Toast) {
            const toast = new bootstrap.Toast(toastEl, {
                delay: notification.duration,
                autohide: notification.duration > 0
            });

            this.toastInstances.set(toastId, toast);
            toast.show();

            // Handle hidden event
            toastEl.addEventListener('hidden.bs.toast', () => {
                toastEl.remove();
                this.toastInstances.delete(toastId);
                this.markAsRead(notification.id);
            });
        } else {
            // Fallback: auto-remove
            if (notification.duration > 0) {
                setTimeout(() => {
                    toastEl.remove();
                    this.markAsRead(notification.id);
                }, notification.duration);
            }

            // Add close button handler
            const closeBtn = toastEl.querySelector('.btn-close');
            if (closeBtn) {
                closeBtn.addEventListener('click', () => {
                    toastEl.remove();
                    this.markAsRead(notification.id);
                });
            }
        }

        // Handle action buttons
        const actionBtns = toastEl.querySelectorAll('[data-action]');
        actionBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const action = btn.dataset.action;
                this.handleAction(notification.id, action);
            });
        });

        // Mark as shown
        notification.shown = true;
        this.stats.shown++;

        // Dispatch event
        this.dispatchEvent('notification:shown', { notification });

        return notification.id;
    }

    showAlert(notification) {
        const alertId = `alert_${notification.id}`;

        const data = {
            ...notification,
            icon: this.getIconForType(notification.type)
        };

        const html = this.renderTemplate(this.templates.alert, data);
        const alertEl = this.createElementFromHTML(html);
        alertEl.id = alertId;

        // Add to appropriate container
        if (this.containers.alert) {
            this.containers.alert.appendChild(alertEl);
        } else {
            const container = document.createElement('div');
            container.className = 'alert-container mb-3';
            container.appendChild(alertEl);

            const main = document.querySelector('main') || document.body;
            main.insertBefore(container, main.firstChild);
        }

        // Auto-remove if duration is set
        if (notification.duration > 0) {
            setTimeout(() => {
                if (alertEl.parentNode) {
                    alertEl.remove();
                    this.markAsRead(notification.id);
                }
            }, notification.duration);
        }

        // Handle close button
        const closeBtn = alertEl.querySelector('.btn-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                alertEl.remove();
                this.markAsRead(notification.id);
            });
        }

        return alertId;
    }

    showInline(notification) {
        // For notification lists
        const listItem = document.createElement('div');
        listItem.className = `notification-item ${notification.type} ${notification.read ? 'read' : 'unread'}`;
        listItem.dataset.notificationId = notification.id;

        listItem.innerHTML = `
            <div class="notification-content">
                <div class="notification-header">
                    <h5 class="notification-title">${notification.title}</h5>
                    <small class="notification-time">${this.formatTime(notification.timestamp)}</small>
                </div>
                <p class="notification-message">${notification.message}</p>
            </div>
            <div class="notification-actions">
                <button class="btn btn-sm btn-outline-secondary" data-action="mark-read">
                    Mark Read
                </button>
                <button class="btn btn-sm btn-outline-danger" data-action="dismiss">
                    Dismiss
                </button>
            </div>
        `;

        // Add to notification list
        const list = document.querySelector('.notifications-list, [data-notifications]');
        if (list) {
            list.appendChild(listItem);
        }

        return notification.id;
    }

    /* ============================================================
     * NOTIFICATION MANAGEMENT
     * =========================================================== */

    markAsRead(id) {
        const notification = this.notifications.get(id);
        if (!notification || notification.read) return false;

        notification.read = true;
        notification.readAt = Date.now();
        this.unreadCount--;

        this.updateStats();

        // Update UI if visible
        const element = document.querySelector(`[data-notification-id="${id}"]`);
        if (element) {
            element.classList.remove('unread');
            element.classList.add('read');
        }

        this.dispatchEvent('notification:read', { id });
        return true;
    }

    markAllAsRead() {
        let count = 0;
        this.notifications.forEach(notification => {
            if (!notification.read) {
                notification.read = true;
                notification.readAt = Date.now();
                count++;
            }
        });

        this.unreadCount = 0;
        this.updateStats();

        // Update all UI elements
        document.querySelectorAll('.notification-item.unread').forEach(el => {
            el.classList.remove('unread');
            el.classList.add('read');
        });

        this.dispatchEvent('notifications:all-read', { count });
        return count;
    }

    dismiss(id) {
        const notification = this.notifications.get(id);
        if (!notification) return false;

        // Remove from UI
        const element = document.querySelector(`[data-notification-id="${id}"]`);
        if (element) {
            element.remove();
        }

        // Remove toast if exists
        const toastId = `toast_${id}`;
        const toastEl = document.getElementById(toastId);
        if (toastEl) toastEl.remove();

        // Remove from instances
        this.toastInstances.delete(toastId);
        this.notifications.delete(id);

        this.updateStats();
        this.dispatchEvent('notification:dismissed', { id });

        return true;
    }

    dismissAll() {
        const ids = Array.from(this.notifications.keys());
        ids.forEach(id => this.dismiss(id));

        // Clear all toasts
        if (this.containers.toast) {
            this.containers.toast.innerHTML = '';
        }

        this.toastInstances.clear();
        this.dispatchEvent('notifications:all-dismissed');
    }

    getNotification(id) {
        return this.notifications.get(id);
    }

    getNotifications(filter = {}) {
        let notifications = Array.from(this.notifications.values());

        if (filter.type) {
            notifications = notifications.filter(n => n.type === filter.type);
        }

        if (filter.read !== undefined) {
            notifications = notifications.filter(n => n.read === filter.read);
        }

        if (filter.since) {
            notifications = notifications.filter(n => n.timestamp > filter.since);
        }

        return notifications;
    }

    /* ============================================================
     * INTEGRATIONS
     * =========================================================== */

    setupHTMXIntegration() {
        // Handle HTMX responses
        document.addEventListener('htmx:afterSwap', (event) => {
            this.processHTMXResponse(event.detail.xhr);
        });

        // Custom HTMX trigger
        document.addEventListener('notification:htmx', (event) => {
            this.show(event.detail.message, event.detail.options);
        });
    }

    processHTMXResponse(xhr) {
        if (!xhr) return;

        // Check all trigger headers
        const headers = ['HX-Trigger', 'HX-Trigger-After-Swap', 'HX-Trigger-After-Settle'];

        headers.forEach(header => {
            const value = xhr.getResponseHeader(header);
            if (value) {
                this.processTriggerHeader(value);
            }
        });
    }

    // processHTMXHeaders is removed as it's merged into processHTMXResponse

    processTriggerHeader(headerValue) {
        try {
            const triggers = JSON.parse(headerValue);

            Object.entries(triggers).forEach(([key, value]) => {
                if ((key === 'showNotification') || (key === 'Notification') || (key === 'showMessage')) {
                    this.show(value.message, {
                        type: value.level || value.type || 'info',
                        title: value.title || '',
                        duration: value.duration || this.options.defaultDuration,
                        icon: value.icon || '',
                        display: value.display || 'toast',
                        metadata: {
                            source: value.source || 'htmx',
                            id: value.id,
                            timestamp: value.timestamp
                        }
                    });
                }
                // Add other trigger types as needed
            });
        } catch (error) {
            this.log('Failed to parse trigger header:', error);
        }
    }

    processDjangoMessages() {
        const container = document.getElementById('django-messages');
        if (!container) return;

        const messages = container.querySelectorAll('.alert');
        messages.forEach(alert => {
            const type = alert.classList.contains('alert-success') ? 'success' :
                alert.classList.contains('alert-danger') ? 'error' :
                    alert.classList.contains('alert-warning') ? 'warning' : 'info';

            const message = alert.textContent.trim();

            this.show(message, {
                type,
                display: 'alert',
                duration: 5000
            });

            // Auto-dismiss Django alerts
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.remove();
                }
            }, 5000);
        });
    }

    /* ============================================================
     * REAL-TIME CONNECTIONS
     * =========================================================== */

    async setupSSEConnection() {
        if (typeof EventSource === 'undefined') {
            this.log('SSE not supported in this browser');
            return;
        }

        try {
            const sseUrl = '/notifications/';
            const eventSource = new EventSource(sseUrl);

            eventSource.onopen = () => {
                this.log('SSE connection opened');
                this.dispatchEvent('sse:connected');
            };

            eventSource.onmessage = (event) => {
                this.handleSSEMessage(event.data);
            };

            eventSource.onerror = (error) => {
                console.error('SSE connection error:', error);
                eventSource.close();
                this.dispatchEvent('sse:error', { error });

                // Reconnect after delay
                setTimeout(() => {
                    if (this.initialized) {
                        this.setupSSEConnection();
                    }
                }, this.options.reconnectDelay);
            };

            this.connections.set('sse', eventSource);

        } catch (error) {
            console.error('Failed to establish SSE connection:', error);
        }
    }

    async setupWebSocketConnection() {
        if (typeof WebSocket === 'undefined') {
            this.log('WebSocket not supported in this browser');
            return;
        }

        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const host = window.location.host;
            const wsUrl = `${protocol}//${host}/ws/notifications/`;

            const socket = new WebSocket(wsUrl);

            socket.onopen = () => {
                this.log('WebSocket connection opened');
                this.dispatchEvent('websocket:connected');
            };

            socket.onmessage = (event) => {
                this.handleWebSocketMessage(event.data);
            };

            socket.onerror = (error) => {
                console.error('WebSocket connection error:', error);
                this.dispatchEvent('websocket:error', { error });
            };

            socket.onclose = () => {
                this.log('WebSocket connection closed');
                this.dispatchEvent('websocket:disconnected');

                // Reconnect after delay
                setTimeout(() => {
                    if (this.initialized) {
                        this.setupWebSocketConnection();
                    }
                }, this.options.reconnectDelay);
            };

            this.connections.set('websocket', socket);

        } catch (error) {
            console.error('Failed to establish WebSocket connection:', error);
        }
    }

    handleSSEMessage(data) {
        try {
            const message = JSON.parse(data);

            switch (message.type) {
                case 'form_update':
                    this.handleFormUpdate(message);
                    break;
                case 'validation':
                    this.handleRemoteValidation(message);
                    break;
                case 'notification':
                case 'message':
                    this.show(message.message || message.data?.message, {
                        type: message.level || message.data?.level || 'info',
                        title: message.title || message.data?.title || '',
                        duration: message.duration || message.data?.duration || this.options.defaultDuration,
                        metadata: { source: 'sse' }
                    });
                    break;
                default:
                    this.dispatchEvent('sse:message', { message });
            }
        } catch (error) {
            this.logger.error('Failed to parse SSE message:', error);
        }
    }

    handleWebSocketMessage(data) {
        try {
            const message = JSON.parse(data);
            this.processRealTimeMessage(message);
        } catch (error) {
            console.error('Failed to parse WebSocket message:', error);
        }
    }

    processRealTimeMessage(message) {
        const { type, data, notification } = message;

        switch (type) {
            case 'notification':
                this.show(data.message || notification.message, {
                    type: data.type || notification.type || 'info',
                    title: data.title || notification.title,
                    duration: data.duration || 5000
                });
                break;

            case 'session_update':
                this.handleSessionUpdate(data);
                break;

            case 'ping':
                // Acknowledge ping
                break;

            default:
                // Try to show as notification
                if (data?.message || message.message) {
                    this.show(data?.message || message.message, {
                        type: data?.type || message.type || 'info'
                    });
                }
        }

        this.dispatchEvent('realtime:message', { type, data });
    }

    handleSessionUpdate(data) {
        const { action, reason } = data;

        switch (action) {
            case 'logout':
                this.showWarning('Your session has ended. Please login again.', {
                    title: 'Session Expired',
                    duration: 10000,
                    actions: [{
                        text: 'Login',
                        action: 'redirect',
                        url: '/auth/login/'
                    }]
                });
                break;

            case 'refresh':
                this.showInfo('Your session has been refreshed.', {
                    duration: 3000
                });
                break;

            case 'expire_warning':
                const minutes = Math.ceil(data.timeLeft / 60);
                this.showWarning(`Your session will expire in ${minutes} minutes.`, {
                    title: 'Session Expiring Soon',
                    duration: 10000,
                    actions: [{
                        text: 'Extend Session',
                        action: 'extend_session'
                    }]
                });
                break;
        }
    }

    /* ============================================================
     * UTILITIES
     * =========================================================== */

    processExistingNotifications() {
        // Process existing notification elements
        const elements = document.querySelectorAll('.notification-item, [data-notification]');
        elements.forEach((el, index) => {
            const id = el.id || `existing_${index}`;
            const notification = {
                id,
                message: el.querySelector('.notification-message')?.textContent || '',
                type: el.dataset.type || 'info',
                title: el.querySelector('.notification-title')?.textContent || '',
                timestamp: el.dataset.timestamp || Date.now(),
                read: el.classList.contains('read'),
                element: el
            };

            this.notifications.set(id, notification);
        });

        this.updateStats();
    }

    updateStats() {
        let total = 0, unread = 0, read = 0, archived = 0;

        this.notifications.forEach(notification => {
            total++;
            if (notification.read) {
                read++;
            } else {
                unread++;
            }
            if (notification.archived) {
                archived++;
            }
        });

        this.stats = { total, unread, read, archived };
        this.unreadCount = unread;

        this.updateUIStats();
    }

    updateUIStats() {
        // Update badge
        const badge = document.querySelector('.notification-badge, [data-notification-badge]');
        if (badge) {
            badge.textContent = this.unreadCount;
            badge.style.display = this.unreadCount > 0 ? 'inline-block' : 'none';
        }

        // Update counters
        document.querySelectorAll('[data-notification-total]').forEach(el => {
            el.textContent = this.stats.total;
        });

        document.querySelectorAll('[data-notification-unread]').forEach(el => {
            el.textContent = this.stats.unread;
        });
    }

    getDefaultTitle(type) {
        const titles = {
            success: 'Success',
            error: 'Error',
            warning: 'Warning',
            info: 'Information'
        };
        return titles[type] || 'Notification';
    }

    getIconForType(type) {
        const icons = {
            success: 'bi-check-circle-fill',
            error: 'bi-exclamation-triangle-fill',
            warning: 'bi-exclamation-circle-fill',
            info: 'bi-info-circle-fill'
        };
        return icons[type] || 'bi-bell-fill';
    }

    renderTemplate(template, data) {
        return template.replace(/\{\{(\w+)\}\}/g, (match, key) => {
            return data[key] || '';
        });
    }

    createElementFromHTML(html) {
        const div = document.createElement('div');
        div.innerHTML = html.trim();
        return div.firstChild;
    }

    sanitize(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    extractLinks(text) {
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        return text.match(urlRegex) || [];
    }

    formatTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;

        if (diff < 60000) return 'Just now';
        if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
        if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
        return date.toLocaleDateString();
    }

    pauseAllTimers() {
        // Pause auto-dismiss timers
        this.toastInstances.forEach(toast => {
            if (toast._timeout) {
                clearTimeout(toast._timeout);
            }
        });
    }

    resumeAllTimers() {
        // Resume auto-dismiss timers
        this.toastInstances.forEach(toast => {
            if (toast._config && toast._config.delay) {
                toast._timeout = setTimeout(() => {
                    toast.hide();
                }, toast._config.delay);
            }
        });
    }

    handleAction(notificationId, action) {
        const notification = this.notifications.get(notificationId);
        if (!notification) return;

        switch (action) {
            case 'mark-read':
                this.markAsRead(notificationId);
                break;

            case 'dismiss':
                this.dismiss(notificationId);
                break;

            case 'redirect':
                if (notification.metadata?.url) {
                    window.location.href = notification.metadata.url;
                }
                break;

            case 'extend_session':
                this.extendSession();
                break;

            default:
                // Custom action
                if (notification.actions) {
                    const customAction = notification.actions.find(a => a.action === action);
                    if (customAction?.callback) {
                        customAction.callback(notification);
                    }
                }
        }

        this.dispatchEvent('notification:action', { notificationId, action });
    }

    async extendSession() {
        try {
            const response = await fetch('/api/session/extend/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                this.showSuccess('Session extended successfully');
            }
        } catch (error) {
            this.showError('Failed to extend session');
        }
    }

    getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }

    /* ============================================================
     * EVENT SYSTEM
     * =========================================================== */

    on(event, callback) {
        if (!this.handlers.has(event)) {
            this.handlers.set(event, []);
        }
        this.handlers.get(event).push(callback);

        return () => {
            const handlers = this.handlers.get(event);
            const index = handlers.indexOf(callback);
            if (index > -1) handlers.splice(index, 1);
        };
    }

    off(event, callback) {
        if (!this.handlers.has(event)) return;
        const handlers = this.handlers.get(event);
        const index = handlers.indexOf(callback);
        if (index > -1) handlers.splice(index, 1);
    }

    dispatchEvent(event, detail = {}) {
        const customEvent = new CustomEvent(event, {
            detail: { ...detail, system: this }
        });
        document.dispatchEvent(customEvent);
    }

    /* ============================================================
     * PUBLIC API
     * =========================================================== */

    getStats() {
        return { ...this.stats };
    }

    getUnreadCount() {
        return this.unreadCount;
    }

    clear() {
        this.dismissAll();
    }

    refresh() {
        this.updateStats();
        this.updateUIStats();
        this.dispatchEvent('notifications:refreshed');
    }

    configure(options) {
        this.options = { ...this.options, ...options };
        this.dispatchEvent('notifications:configured', { options });
    }

    cleanup() {
        // Close connections
        this.connections.forEach((connection, key) => {
            if (connection.close) connection.close();
            if (connection.readyState === WebSocket.OPEN) connection.close();
        });
        this.connections.clear();

        // Clear toasts
        if (this.containers.toast) {
            this.containers.toast.innerHTML = '';
        }

        // Clear instances
        this.toastInstances.clear();
        this.handlers.clear();

        this.initialized = false;
        this.log('Notification system cleaned up');
    }

    destroy() {
        this.cleanup();
        this.notifications.clear();
        this.queue = [];

        // Remove global methods
        delete window.showNotification;
        delete window.notificationSystem;

        this.log('Notification system destroyed');
    }
}

// Global instance
export const notificationSystem = new NotificationSystem();

// Auto-initialize
if (typeof document !== 'undefined') {
    document.addEventListener('DOMContentLoaded', () => {
        if (document.querySelector('[data-notifications]')) {
            notificationSystem.init();
        }
    });
}

export default NotificationSystem;
