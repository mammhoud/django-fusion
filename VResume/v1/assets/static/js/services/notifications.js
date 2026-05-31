export class NotificationSystem {
    constructor(options = {}) {
        this.options = {
            maxNotifications: 5,
            defaultDuration: 5000,
            position: 'top-right',
            useBootstrap: typeof bootstrap !== 'undefined',
            enableHTMX: true,
            enableDjangoMessages: true,
            debug: false,
            ...options
        };

        this.notifications = new Map();
        this.toastInstances = new Map();
        this.unreadCount = 0;
        this.handlers = new Map();
        this.initialized = false;
        this.containers = {};

        this.log = (...args) => {
            if (this.options.debug) console.log('[Notifications]', ...args);
        };
    }

    async init() {
        if (this.initialized) return this;

        this.log('Initializing notification system...');

        try {
            this.setupContainers();
            this.setupEventListeners();
            this.setupGlobalMethods();

            if (this.options.enableHTMX && typeof htmx !== 'undefined') {
                this.setupHTMXIntegration();
            }

            if (this.options.enableDjangoMessages) {
                this.processDjangoMessages();
            }

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
        this.containers.toast = container;

        const alertContainer = document.getElementById('alert-container') ||
            document.querySelector('[data-alerts]');
        if (alertContainer) {
            this.containers.alert = alertContainer;
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

    setupEventListeners() {
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseAllTimers();
            } else {
                this.resumeAllTimers();
            }
        });

        document.addEventListener('notification:show', (e) => {
            if (e.detail && !e.detail.processed) {
                this.show(e.detail.message, e.detail.options);
            }
        });

        window.addEventListener('beforeunload', () => {
            this.cleanup();
        });
    }

    setupGlobalMethods() {
        window.showNotification = this.show.bind(this);
        window.showToast = this.showToast.bind(this);
        window.showAlert = this.showAlert.bind(this);
        window.clearNotifications = this.clear.bind(this);
        window.showSuccess = (msg, opts) => this.show(msg, { ...opts, type: 'success' });
        window.showError = (msg, opts) => this.show(msg, { ...opts, type: 'error' });
        window.showWarning = (msg, opts) => this.show(msg, { ...opts, type: 'warning' });
        window.showInfo = (msg, opts) => this.show(msg, { ...opts, type: 'info' });
        window.notificationSystem = this;
    }

    show(message, options = {}) {
        const config = {
            type: 'info',
            title: '',
            duration: this.options.defaultDuration,
            closable: true,
            display: 'toast',
            id: `notif_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            ...options
        };

        if (!message) {
            console.warn('Notification message is required');
            return null;
        }

        const notification = {
            id: config.id,
            message: typeof message === 'string' ? message : message.message || '',
            type: config.type,
            title: config.title || this.getDefaultTitle(config.type),
            duration: config.duration,
            display: config.display,
            timestamp: Date.now(),
            read: false
        };

        this.notifications.set(notification.id, notification);

        switch (config.display) {
            case 'toast':
                return this.showToast(notification);
            case 'alert':
                return this.showAlert(notification);
            default:
                return this.showToast(notification);
        }
    }

    showToast(notification) {
        const toastId = `toast_${notification.id}`;
        const html = `
            <div class="toast" role="alert" aria-live="assertive" aria-atomic="true" data-bs-delay="${notification.duration}">
                <div class="toast-header bg-${notification.type} text-white">
                    <i class="${this.getIconForType(notification.type)} me-2"></i>
                    <strong class="me-auto">${notification.title}</strong>
                    <small class="text-white-50">${new Date(notification.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</small>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
                <div class="toast-body">${notification.message}</div>
            </div>
        `;

        const toastEl = this.createElementFromHTML(html);
        toastEl.id = toastId;

        if (this.containers.toast) {
            this.containers.toast.appendChild(toastEl);
            const toasts = this.containers.toast.querySelectorAll('.toast');
            if (toasts.length > this.options.maxNotifications) {
                toasts[0].remove();
            }
        } else {
            document.body.appendChild(toastEl);
        }

        if (this.options.useBootstrap && bootstrap?.Toast) {
            const toast = new bootstrap.Toast(toastEl, {
                delay: notification.duration,
                autohide: notification.duration > 0
            });

            this.toastInstances.set(toastId, toast);
            toast.show();

            toastEl.addEventListener('hidden.bs.toast', () => {
                toastEl.remove();
                this.toastInstances.delete(toastId);
                this.markAsRead(notification.id);
            });
        } else {
            if (notification.duration > 0) {
                setTimeout(() => {
                    if (toastEl.parentNode) toastEl.remove();
                    this.markAsRead(notification.id);
                }, notification.duration);
            }

            const closeBtn = toastEl.querySelector('.btn-close');
            if (closeBtn) {
                closeBtn.addEventListener('click', () => {
                    toastEl.remove();
                    this.markAsRead(notification.id);
                });
            }
        }

        this.dispatchEvent('notification:shown', { notification });
        return notification.id;
    }

    showAlert(notification) {
        const alertId = `alert_${notification.id}`;
        const html = `
            <div class="alert alert-${notification.type} alert-dismissible fade show" role="alert">
                <i class="${this.getIconForType(notification.type)} me-2"></i>
                <strong>${notification.title}</strong>
                <span class="ms-2">${notification.message}</span>
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;

        const alertEl = this.createElementFromHTML(html);
        alertEl.id = alertId;

        if (this.containers.alert) {
            this.containers.alert.appendChild(alertEl);
        } else {
            const container = document.createElement('div');
            container.className = 'alert-container mb-3';
            container.appendChild(alertEl);
            const main = document.querySelector('main') || document.body;
            main.insertBefore(container, main.firstChild);
        }

        if (notification.duration > 0) {
            setTimeout(() => {
                if (alertEl.parentNode) {
                    alertEl.remove();
                    this.markAsRead(notification.id);
                }
            }, notification.duration);
        }

        const closeBtn = alertEl.querySelector('.btn-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                alertEl.remove();
                this.markAsRead(notification.id);
            });
        }

        return alertId;
    }

    markAsRead(id) {
        const notification = this.notifications.get(id);
        if (!notification || notification.read) return false;

        notification.read = true;
        notification.readAt = Date.now();
        this.unreadCount--;

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

        const element = document.querySelector(`[data-notification-id="${id}"]`);
        if (element) element.remove();

        const toastId = `toast_${id}`;
        const toastEl = document.getElementById(toastId);
        if (toastEl) toastEl.remove();

        this.toastInstances.delete(toastId);
        this.notifications.delete(id);

        this.dispatchEvent('notification:dismissed', { id });
        return true;
    }

    dismissAll() {
        const ids = Array.from(this.notifications.keys());
        ids.forEach(id => this.dismiss(id));

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

    setupHTMXIntegration() {
        document.addEventListener('htmx:afterSwap', (event) => {
            const xhr = event.detail.xhr;
            if (!xhr) return;

            const headers = ['HX-Trigger', 'HX-Trigger-After-Swap', 'HX-Trigger-After-Settle'];
            headers.forEach(header => {
                const value = xhr.getResponseHeader(header);
                if (value) {
                    try {
                        const triggers = JSON.parse(value);
                        Object.entries(triggers).forEach(([key, value]) => {
                            if (key === 'showNotification' || key === 'Notification') {
                                this.show(value.message, {
                                    type: value.level || value.type || 'info',
                                    title: value.title || '',
                                    duration: value.duration || this.options.defaultDuration,
                                    display: value.display || 'toast'
                                });
                            }
                        });
                    } catch (error) {
                        this.log('Failed to parse trigger header:', error);
                    }
                }
            });
        });
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
     * UTILITIES
     * =========================================================== */

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

    createElementFromHTML(html) {
        const div = document.createElement('div');
        div.innerHTML = html.trim();
        return div.firstChild;
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
        this.toastInstances.forEach(toast => {
            if (toast._timeout) clearTimeout(toast._timeout);
        });
    }

    resumeAllTimers() {
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
        }

        this.dispatchEvent('notification:action', { notificationId, action });
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
        return { total: this.notifications.size, unread: this.unreadCount };
    }

    getUnreadCount() {
        return this.unreadCount;
    }

    clear() {
        this.dismissAll();
    }

    refresh() {
        this.dispatchEvent('notifications:refreshed');
    }

    configure(options) {
        this.options = { ...this.options, ...options };
        this.dispatchEvent('notifications:configured', { options });
    }

    cleanup() {
        if (this.containers.toast) {
            this.containers.toast.innerHTML = '';
        }
        this.toastInstances.clear();
        this.handlers.clear();
        this.initialized = false;
        this.log('Notification system cleaned up');
    }

    destroy() {
        this.cleanup();
        this.notifications.clear();
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
