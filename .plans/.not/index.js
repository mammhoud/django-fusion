/**
 * Notification System Module Exports
 */

export { default as SSEHandler } from './handler.js';
export { default as NotificationSystem } from './notification.js';
export { default as HTMXNotificationHandler } from './processor.js';

// Auto-initialize notification system
(async () => {
  try {
    const { default: NotificationSystem } = await import('./notification.js');
    const { default: SSEManager } = await import('./handler.js');
    
    // Create global instances
    window.SSEManager = SSEManager;
    window.NotificationSystem = new NotificationSystem();
    window.notificationSystem = window.NotificationSystem;
    
    // Expose global methods
    window.showNotification = window.NotificationSystem.show.bind(window.NotificationSystem);
    window.showSuccess = window.NotificationSystem.success.bind(window.NotificationSystem);
    window.showError = window.NotificationSystem.error.bind(window.NotificationSystem);
    window.showWarning = window.NotificationSystem.warning.bind(window.NotificationSystem);
    window.showInfo = window.NotificationSystem.info.bind(window.NotificationSystem);
    
    console.log('✅ Notification system initialized globally');
    
  } catch (error) {
    console.warn('⚠️ Notification system failed to load:', error);
  }
})();