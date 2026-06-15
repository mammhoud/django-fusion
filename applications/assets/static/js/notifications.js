/**
 * Notifications System
 * Unified notification display across all sites
 * 
 * Supports:
 * - Toasts (auto-dismiss)
 * - Alerts (persistent)
 * - Popups (modal-style)
 */

(function() {
    'use strict';

    // Ensure app namespace exists
    window.app = window.app || {};

    // Configuration
    const DEFAULT_TIMEOUT = 5000; // 5 seconds
    const ICONS = {
        success: 'bi-check-circle-fill',
        danger: 'bi-x-circle-fill',
        warning: 'bi-exclamation-triangle-fill',
        info: 'bi-info-circle-fill'
    };

    // Ensure containers exist
    function ensureContainers() {
        if (!document.getElementById('notification-container')) {
            const container = document.createElement('div');
            container.id = 'notification-container';
            container.className = 'notification-container position-fixed top-0 end-0 p-3';
            document.body.appendChild(container);
        }

        if (!document.getElementById('alert-container')) {
            const container = document.createElement('div');
            container.id = 'alert-container';
            container.className = 'alert-container';
            document.body.appendChild(container);
        }

        if (!document.getElementById('popup-container')) {
            const container = document.createElement('div');
            container.id = 'popup-container';
            container.className = 'modal-container';
            document.body.appendChild(container);
        }
    }

    /**
     * Show a toast notification (auto-dismissing)
     */
    function showNotification(options = {}) {
        ensureContainers();

        const {
            title = 'Notification',
            message = '',
            level = 'info',
            icon = null,
            duration = DEFAULT_TIMEOUT,
            onclick = null
        } = options;

        const iconClass = icon || ICONS[level] || ICONS.info;
        const id = `toast-${Date.now()}`;

        // Create toast element
        const toast = document.createElement('div');
        toast.id = id;
        toast.className = `toast show alert alert-${level} alert-dismissible fade`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex align-items-start">
                <i class="bi ${iconClass} me-2 flex-shrink-0 mt-1"></i>
                <div class="flex-grow-1">
                    <strong>${escapeHtml(title)}</strong>
                    ${message ? `<div>${escapeHtml(message)}</div>` : ''}
                </div>
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;

        // Add to container
        document.getElementById('notification-container').appendChild(toast);

        // Handle click
        if (onclick) {
            toast.style.cursor = 'pointer';
            toast.addEventListener('click', onclick);
        }

        // Auto-dismiss
        if (duration > 0) {
            setTimeout(() => {
                const toastElement = document.getElementById(id);
                if (toastElement) {
                    const bsToast = bootstrap.Toast.getInstance(toastElement) || new bootstrap.Toast(toastElement);
                    bsToast.hide();
                    setTimeout(() => toastElement.remove(), 300);
                }
            }, duration);
        }

        return toast;
    }

    /**
     * Show a persistent alert
     */
    function showAlert(options = {}) {
        ensureContainers();

        const {
            title = 'Alert',
            message = '',
            level = 'warning',
            icon = null,
            badge = null,
            details = null
        } = options;

        const iconClass = icon || ICONS[level] || ICONS.warning;
        const id = `alert-${Date.now()}`;

        // Create alert element
        const alert = document.createElement('div');
        alert.id = id;
        alert.className = `alert alert-${level} alert-dismissible fade show`;
        alert.setAttribute('role', 'alert');
        alert.innerHTML = `
            <div class="d-flex align-items-start">
                <i class="bi ${iconClass} me-2 flex-shrink-0 mt-1"></i>
                <div class="flex-grow-1">
                    <div>
                        <strong>${escapeHtml(title)}</strong>
                        ${badge ? `<span class="badge bg-secondary ms-2">${escapeHtml(badge)}</span>` : ''}
                    </div>
                    <p class="mb-0">${escapeHtml(message)}</p>
                    ${details ? `
                        <details class="small mt-2">
                            <summary>More details</summary>
                            <div class="mt-2">${details}</div>
                        </details>
                    ` : ''}
                </div>
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;

        // Add to container
        document.getElementById('alert-container').appendChild(alert);

        return alert;
    }

    /**
     * Show a modal popup
     */
    function showPopup(options = {}) {
        ensureContainers();

        const {
            title = 'Confirmation',
            message = '',
            level = 'warning',
            size = 'modal-md',
            showCancel = true,
            actions = ''
        } = options;

        const id = `popup-${Date.now()}`;
        const levels = {
            success: { color: 'success', icon: 'bi-check-circle' },
            danger: { color: 'danger', icon: 'bi-x-circle' },
            warning: { color: 'warning', icon: 'bi-exclamation-triangle' },
            info: { color: 'info', icon: 'bi-info-circle' }
        };

        const levelConfig = levels[level] || levels.warning;

        // Create modal
        const modal = document.createElement('div');
        modal.id = id;
        modal.className = 'modal fade';
        modal.setAttribute('tabindex', '-1');
        modal.innerHTML = `
            <div class="modal-dialog ${size}">
                <div class="modal-content">
                    <div class="modal-header border-${levelConfig.color}">
                        <h5 class="modal-title">
                            <i class="bi ${levelConfig.icon} text-${levelConfig.color} me-2"></i>
                            ${escapeHtml(title)}
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        ${message}
                    </div>
                    <div class="modal-footer">
                        ${showCancel ? '<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>' : ''}
                        ${actions}
                    </div>
                </div>
            </div>
        `;

        // Add to container
        document.getElementById('popup-container').appendChild(modal);

        // Show modal
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();

        // Remove modal after hide
        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
        });

        return modal;
    }

    /**
     * Escape HTML to prevent XSS
     */
    function escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }

    // Export functions
    window.app.showNotification = showNotification;
    window.app.showAlert = showAlert;
    window.app.showPopup = showPopup;

    // Listen for Django messages and display as notifications
    document.addEventListener('app:ready', () => {
        const messages = document.querySelectorAll('.django-message');
        messages.forEach(msg => {
            const level = msg.dataset.level || 'info';
            const text = msg.textContent;
            showNotification({
                title: level.charAt(0).toUpperCase() + level.slice(1),
                message: text,
                level: level,
                duration: level === 'error' ? 10000 : DEFAULT_TIMEOUT
            });
        });
    });

    console.log('✓ Notifications system loaded');

})();
