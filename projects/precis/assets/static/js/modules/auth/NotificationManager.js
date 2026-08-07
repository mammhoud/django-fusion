/**
 * @file NotificationManager.js
 * Toast notification system for auth pages
 * 
 * Features:
 * - Success, error, warning, info notification types
 * - Auto-dismiss with configurable duration
 * - Notification stacking without overlap
 * - Slide in/out animations
 */

export class NotificationManager {
    constructor(options = {}) {
        this.options = {
            position: options.position || 'top-right',
            duration: options.duration || 5000,
            maxNotifications: options.maxNotifications || 5,
            animationDuration: options.animationDuration || 300,
            containerClass: options.containerClass || 'notification-container',
            ...options
        };

        this.notifications = [];
        this.container = null;
        this.init();
    }

    /**
     * Initialize notification container
     */
    init() {
        // Create container if it doesn't exist
        this.container = document.querySelector(`.${this.options.containerClass}`);
        
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.className = `${this.options.containerClass} notification-${this.options.position}`;
            this.container.setAttribute('role', 'alert');
            this.container.setAttribute('aria-live', 'polite');
            document.body.appendChild(this.container);
        }

        // Add styles if not already present
        this._injectStyles();
    }

    /**
     * Show a notification
     * @param {string} message - Notification message
     * @param {string} type - Notification type (success, error, warning, info)
     * @param {Object} options - Additional options
     * @returns {string} Notification ID
     */
    show(message, type = 'info', options = {}) {
        const id = this._generateId();
        const duration = options.duration ?? this.options.duration;
        const dismissible = options.dismissible ?? true;

        // Remove oldest notification if at max
        if (this.notifications.length >= this.options.maxNotifications) {
            this.dismiss(this.notifications[0].id);
        }

        // Create notification element
        const notification = this._createNotificationElement(id, message, type, dismissible);
        
        // Add to container
        this.container.appendChild(notification);

        // Track notification
        const notificationData = {
            id,
            element: notification,
            type,
            message,
            createdAt: Date.now()
        };
        this.notifications.push(notificationData);

        // Trigger animation
        requestAnimationFrame(() => {
            notification.classList.add('notification-visible');
        });

        // Auto-dismiss
        if (duration > 0) {
            notificationData.timeout = setTimeout(() => {
                this.dismiss(id);
            }, duration);
        }

        // Dispatch event
        this._dispatchEvent('notification:show', { id, type, message });

        return id;
    }

    /**
     * Show success notification
     */
    success(message, options = {}) {
        return this.show(message, 'success', options);
    }

    /**
     * Show error notification
     */
    error(message, options = {}) {
        return this.show(message, 'error', { duration: 8000, ...options });
    }

    /**
     * Show warning notification
     */
    warning(message, options = {}) {
        return this.show(message, 'warning', options);
    }

    /**
     * Show info notification
     */
    info(message, options = {}) {
        return this.show(message, 'info', options);
    }

    /**
     * Dismiss a specific notification
     * @param {string} id - Notification ID
     */
    dismiss(id) {
        const index = this.notifications.findIndex(n => n.id === id);
        if (index === -1) return;

        const notification = this.notifications[index];
        
        // Clear timeout
        if (notification.timeout) {
            clearTimeout(notification.timeout);
        }

        // Animate out
        notification.element.classList.remove('notification-visible');
        notification.element.classList.add('notification-hiding');

        // Remove after animation
        setTimeout(() => {
            notification.element.remove();
            this.notifications.splice(index, 1);
            this._dispatchEvent('notification:dismiss', { id });
        }, this.options.animationDuration);
    }

    /**
     * Dismiss all notifications
     */
    dismissAll() {
        [...this.notifications].forEach(n => this.dismiss(n.id));
    }

    /**
     * Create notification DOM element
     */
    _createNotificationElement(id, message, type, dismissible) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.setAttribute('data-notification-id', id);
        notification.setAttribute('role', 'alert');

        const icon = this._getIcon(type);
        
        notification.innerHTML = `
            <div class="notification-icon">${icon}</div>
            <div class="notification-content">
                <p class="notification-message">${this._escapeHtml(message)}</p>
            </div>
            ${dismissible ? `
                <button class="notification-close" aria-label="Dismiss notification">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </button>
            ` : ''}
        `;

        // Add close handler
        if (dismissible) {
            const closeBtn = notification.querySelector('.notification-close');
            closeBtn.addEventListener('click', () => this.dismiss(id));
        }

        return notification;
    }

    /**
     * Get icon SVG for notification type
     */
    _getIcon(type) {
        const icons = {
            success: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                <polyline points="22 4 12 14.01 9 11.01"></polyline>
            </svg>`,
            error: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="15" y1="9" x2="9" y2="15"></line>
                <line x1="9" y1="9" x2="15" y2="15"></line>
            </svg>`,
            warning: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                <line x1="12" y1="9" x2="12" y2="13"></line>
                <line x1="12" y1="17" x2="12.01" y2="17"></line>
            </svg>`,
            info: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="16" x2="12" y2="12"></line>
                <line x1="12" y1="8" x2="12.01" y2="8"></line>
            </svg>`
        };
        return icons[type] || icons.info;
    }

    /**
     * Generate unique notification ID
     */
    _generateId() {
        return `notification-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    }

    /**
     * Escape HTML to prevent XSS
     */
    _escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Dispatch custom event
     */
    _dispatchEvent(name, detail) {
        document.dispatchEvent(new CustomEvent(name, { detail }));
    }

    /**
     * Inject notification styles
     */
    _injectStyles() {
        if (document.getElementById('notification-manager-styles')) return;

        const styles = document.createElement('style');
        styles.id = 'notification-manager-styles';
        styles.textContent = `
            .notification-container {
                position: fixed;
                z-index: 9999;
                display: flex;
                flex-direction: column;
                gap: 0.75rem;
                max-width: 400px;
                width: calc(100% - 2rem);
                pointer-events: none;
            }

            .notification-top-right {
                top: 1rem;
                right: 1rem;
            }

            .notification-top-left {
                top: 1rem;
                left: 1rem;
            }

            .notification-bottom-right {
                bottom: 1rem;
                right: 1rem;
            }

            .notification-bottom-left {
                bottom: 1rem;
                left: 1rem;
            }

            .notification-top-center {
                top: 1rem;
                left: 50%;
                transform: translateX(-50%);
            }

            .notification {
                display: flex;
                align-items: flex-start;
                gap: 0.75rem;
                padding: 1rem;
                border-radius: 0.5rem;
                background: #ffffff;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                pointer-events: auto;
                opacity: 0;
                transform: translateX(100%);
                transition: all 0.3s ease;
            }

            .notification-top-left .notification,
            .notification-bottom-left .notification {
                transform: translateX(-100%);
            }

            .notification-top-center .notification {
                transform: translateY(-100%);
            }

            .notification-visible {
                opacity: 1;
                transform: translateX(0) translateY(0);
            }

            .notification-hiding {
                opacity: 0;
                transform: translateX(100%);
            }

            .notification-icon {
                flex-shrink: 0;
                display: flex;
                align-items: center;
                justify-content: center;
            }

            .notification-content {
                flex: 1;
                min-width: 0;
            }

            .notification-message {
                margin: 0;
                font-size: 0.875rem;
                line-height: 1.5;
                color: #333;
            }

            .notification-close {
                flex-shrink: 0;
                padding: 0.25rem;
                background: none;
                border: none;
                cursor: pointer;
                color: #666;
                opacity: 0.7;
                transition: opacity 0.2s;
            }

            .notification-close:hover {
                opacity: 1;
            }

            /* Type-specific styles */
            .notification-success {
                border-left: 4px solid #10B981;
            }

            .notification-success .notification-icon {
                color: #10B981;
            }

            .notification-error {
                border-left: 4px solid #EF4444;
            }

            .notification-error .notification-icon {
                color: #EF4444;
            }

            .notification-warning {
                border-left: 4px solid #F59E0B;
            }

            .notification-warning .notification-icon {
                color: #F59E0B;
            }

            .notification-info {
                border-left: 4px solid #3B82F6;
            }

            .notification-info .notification-icon {
                color: #3B82F6;
            }

            /* Dark mode support */
            @media (prefers-color-scheme: dark) {
                .notification {
                    background: #1f2937;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
                }

                .notification-message {
                    color: #f3f4f6;
                }

                .notification-close {
                    color: #9ca3af;
                }
            }

            /* Mobile adjustments */
            @media (max-width: 480px) {
                .notification-container {
                    left: 0.5rem;
                    right: 0.5rem;
                    width: auto;
                    max-width: none;
                }

                .notification-top-center {
                    transform: none;
                }
            }
        `;
        document.head.appendChild(styles);
    }

    /**
     * Destroy notification manager
     */
    destroy() {
        this.dismissAll();
        if (this.container) {
            this.container.remove();
        }
    }
}

// Export singleton instance
export const notificationManager = new NotificationManager();

export default NotificationManager;
