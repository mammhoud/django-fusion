/**
 * @file layouts/notifications.layout.js
 * Notifications Layout with Integrated Notification System
 */

import { BaseLayout } from './init.layout.js';

export class NotificationsLayout extends BaseLayout {
    constructor(options = {}) {
        super({
            layoutId: 'notifications',
            layoutType: 'notifications',
            pageId: 'notifications',
            debug: options.debug || false,
            
            // Notification-specific options
            enableRealTime: options.enableRealTime !== false,
            enableCategories: options.enableCategories !== false,
            enableFilters: options.enableFilters !== false,
            enableBulkActions: options.enableBulkActions !== false,
            autoRefresh: options.autoRefresh || false,
            
            // Notification system is inherited from BaseLayout
            enableNotifications: true,
            notificationConfig: {
                position: 'top-right',
                maxNotifications: 5,
                duration: 5000,
                showProgress: true,
                ...options.notificationConfig
            },
            
            ...options
        });

        // Notification types
        this.notificationTypes = {
            INBOX: 'inbox',
            ALERTS: 'alerts',
            MESSAGES: 'messages',
            ANNOUNCEMENTS: 'announcements',
            ACTIVITY: 'activity',
            UPDATES: 'updates'
        };
        
        this.currentNotificationType = null;
        
        // Store for notification data
        this.notifications = {
            inbox: [],
            alerts: [],
            messages: [],
            announcements: [],
            activity: [],
            updates: []
        };
        
        this.selectedNotifications = new Set();
        this.realTimeConnection = null;
    }

    async initComponents() {
        this.log('🔔 Initializing notifications components...');
        
        // Use notification system from BaseLayout
        this.setupNotificationHandlers();
        
        // Initialize categories
        if (this.options.enableCategories) {
            await this.initCategories();
        }
        
        // Initialize filters
        if (this.options.enableFilters) {
            await this.initFilters();
        }
        
        // Initialize bulk actions
        if (this.options.enableBulkActions) {
            await this.initBulkActions();
        }
        
        // Initialize real-time updates if enabled
        if (this.options.enableRealTime) {
            await this.initRealTimeUpdates();
        }
        
        // Load initial notifications
        await this.loadNotifications();
        
        this.log('✅ Notifications components initialized');
    }

    setupNotificationHandlers() {
        // Setup notification event handlers if notification system is available
        if (this.notificationSystem && this.notificationSystem.on) {
            this.notificationSystem.on('notification:click', (notification) => {
                this.handleNotificationClick(notification);
            });
            
            this.notificationSystem.on('notification:close', (notification) => {
                this.handleNotificationClose(notification);
            });
        }
    }

    async applyContent() {
        this.log('Applying notifications layout content...');
        
        // Detect notification type from URL
        this.detectNotificationTypeFromURL();
        
        // Apply notification type specific content
        await this.applyNotificationTypeContent();
        
        // Update notification UI
        this.updateNotificationUI();
        
        this.dispatchEvent('notifications:content-applied', {
            notificationType: this.currentNotificationType,
            timestamp: Date.now()
        });
    }

    // ... (Rest of the NotificationsLayout methods remain the same as in the original file)
    // The methods like detectNotificationTypeFromURL, applyNotificationTypeContent, 
    // loadNotifications, renderNotifications, etc. remain unchanged
}

export default NotificationsLayout;