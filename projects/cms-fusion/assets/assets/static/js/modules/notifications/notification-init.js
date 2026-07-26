/**
 * @file notification-init.js
 * Notification system initialization and container setup
 * Ensures notification containers are created before the system initializes
 */

/**
 * Initialize notification containers in the DOM
 * This should be called as early as possible in the page load
 */
export function initializeNotificationContainers() {
    // Create toast container if it doesn't exist
    if (!document.getElementById('toast-container')) {
        const toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'toast-container position-fixed p-3';
        toastContainer.setAttribute('aria-live', 'polite');
        toastContainer.setAttribute('aria-atomic', 'true');
        toastContainer.style.cssText = `
            z-index: 1055;
            top: 1rem;
            right: 1rem;
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        `;
        document.body.appendChild(toastContainer);
    }

    // Create alert container if it doesn't exist
    if (!document.getElementById('alert-container')) {
        const alertContainer = document.createElement('div');
        alertContainer.id = 'alert-container';
        alertContainer.className = 'alert-container';
        alertContainer.setAttribute('role', 'region');
        alertContainer.setAttribute('aria-live', 'polite');
        alertContainer.style.cssText = `
            position: relative;
            z-index: 1050;
        `;

        // Insert at the beginning of main or body
        const main = document.querySelector('main');
        if (main) {
            main.insertBefore(alertContainer, main.firstChild);
        } else {
            document.body.insertBefore(alertContainer, document.body.firstChild);
        }
    }

    // Create notification list container if it doesn't exist
    if (!document.querySelector('.notifications-list, [data-notifications]')) {
        const notificationList = document.createElement('div');
        notificationList.className = 'notifications-list';
        notificationList.setAttribute('data-notifications', 'true');
        notificationList.style.cssText = `
            display: none;
        `;
        document.body.appendChild(notificationList);
    }
}

/**
 * Auto-initialize containers on DOM ready
 */
if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeNotificationContainers);
    } else {
        // DOM is already loaded
        initializeNotificationContainers();
    }
}

export default initializeNotificationContainers;
