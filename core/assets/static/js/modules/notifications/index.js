/**
 * @file layouts/notifications/index.js
 * Main notification system exports
 */

import { NotificationSystem } from './notification.js';


// Global instance (will be set when initialized)
export let notificationSystem = null;

// Application loader integration
export const NotificationModule = {
  /**
   * Initialize the notification system
   * @param {Object} config - Configuration object
   * @param {HTMLElement} container - Optional container element
   * @returns {Promise<NotificationSystem>}
   */
  async initialize(config = {}, container = null) {
    try {
      // Find container if not provided
      const targetContainer = container || document.querySelector('.notifications-init');

      if (!targetContainer && !config.autoInit) {
        console.warn('⚠️ Notification system: No container found and autoInit is false');
        return null;
      }

      // Merge container config with provided config
      let mergedConfig = { ...config };
      if (targetContainer && targetContainer.dataset.notificationsInit) {
        try {
          const containerConfig = JSON.parse(targetContainer.dataset.notificationsInit);
          mergedConfig = { ...mergedConfig, ...containerConfig };
        } catch (e) {
          console.warn('⚠️ Notification system: Invalid JSON in data-notifications-init');
        }
      }

      // Create and initialize system
      const system = new NotificationSystem(mergedConfig);
      await system.init();

      // Store globally for backward compatibility
      window.NotificationSystem = NotificationSystem;
      // window.SSEHandler = SSEHandler;
      window.notificationSystem = system;

      // Expose convenience methods
      window.showNotification = system.show.bind(system);
      // window.showSuccess = system.success.bind(system);
      // window.showError = system.error.bind(system);
      // window.showWarning = system.warning.bind(system);
      // window.showInfo = system.info.bind(system);

      // Update the exported instance
      notificationSystem = system;

      console.log('✅ Notification system initialized');
      return system;
    } catch (error) {
      console.error('❌ Notification system failed to initialize:', error);
      throw error;
    }
  },

  /**
   * Get the current notification system instance
   * @returns {NotificationSystem|null}
   */
  getInstance() {
    return window.notificationSystem || notificationSystem;
  },

  /**
   * Quick notification methods (if system is initialized)
   */
  show(message, options = {}) {
    const system = this.getInstance();
    if (system) {
      return system.show(message, options);
    }
    console.warn('Notification system not initialized');
    return null;
  },

  success(message, options = {}) {
    const system = this.getInstance();
    if (system) {
      return system.success(message, options);
    }
    console.warn('Notification system not initialized');
    return null;
  },

  error(message, options = {}) {
    const system = this.getInstance();
    if (system) {
      return system.error(message, options);
    }
    console.warn('Notification system not initialized');
    return null;
  },

  warning(message, options = {}) {
    const system = this.getInstance();
    if (system) {
      return system.warning(message, options);
    }
    console.warn('Notification system not initialized');
    return null;
  },

  info(message, options = {}) {
    const system = this.getInstance();
    if (system) {
      return system.info(message, options);
    }
    console.warn('Notification system not initialized');
    return null;
  }
};

// Default export for convenience
export default {
  // SSEHandler,
  NotificationSystem,
  NotificationModule,

  // Convenience getter
  get notificationSystem() {
    return window.notificationSystem || notificationSystem;
  }
};
