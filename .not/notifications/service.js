/**
 * @file layouts/services/notifications-service.js
 * Enhanced Notifications Service for Layout Integration
 */

export class NotificationsService {
    constructor(layout) {
        this.layout = layout;
        this.initialized = false;
        this.notifications = new Map();
        this.categories = new Map();
        this.filters = {
            unread: false,
            category: null,
            dateRange: null,
            priority: null
        };
        this.selectedNotifications = new Set();
        this.realTimeConnection = null;
        this.unreadCount = 0;
        this.refreshTimer = null;
        
        // Stats
        this.notificationStats = {
            total: 0,
            unread: 0,
            read: 0,
            archived: 0
        };
        
        this.log = (...args) => this.layout.log(...args);
    }

    // ===============================================
    // LIFECYCLE METHODS
    // ===============================================
    
    async init() {
        if (this.initialized) return this;
        
        this.log('🔔 Initializing Notifications Service...');
        
        // Initialize notifications
        await this.initNotifications();
        
        // Initialize real-time updates
        await this.initRealTimeUpdates();
        
        // Initialize auto-refresh
        await this.initAutoRefresh();
        
        // Initialize analytics
        await this.initNotificationAnalytics();
        
        this.initialized = true;
        this.log('✅ Notifications Service initialized');
        
        return this;
    }

    async destroy() {
        this.log('Destroying Notifications Service...');
        
        // Close real-time connection
        if (this.realTimeConnection) {
            if (this.realTimeConnection.close) {
                this.realTimeConnection.close();
            }
            this.realTimeConnection = null;
        }
        
        // Clear auto-refresh timer
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
            this.refreshTimer = null;
        }
        
        // Clear notifications
        this.notifications.clear();
        this.categories.clear();
        this.selectedNotifications.clear();
        
        this.initialized = false;
        this.log('✅ Notifications Service destroyed');
        
        return this;
    }

    // ===============================================
    // NOTIFICATION MANAGEMENT
    // ===============================================
    
    async initNotifications() {
        const containers = document.querySelectorAll('.notifications-container, [data-notifications]');
        
        containers.forEach((container, index) => {
            const containerId = container.id || `notifications-${index}`;
            this.registerComponent(`container-${containerId}`, {
                element: container,
                destroy: () => {}
            });
        });
        
        // Initialize notification items
        await this.initNotificationItems();
        
        this.updateNotificationStats();
        this.log(`Found ${this.notifications.size} notifications`);
    }

    async initNotificationItems() {
        const items = document.querySelectorAll('.notification-item, [data-notification]');
        
        items.forEach((item, index) => {
            const notificationId = item.id || `notification-${index}`;
            const notificationData = this.extractNotificationData(item);
            
            this.notifications.set(notificationId, {
                element: item,
                id: notificationId,
                data: notificationData,
                read: item.classList.contains('read'),
                selected: false,
                archived: item.classList.contains('archived')
            });
            
            this.initNotificationItemHandlers(item, notificationId);
        });
    }

    extractNotificationData(item) {
        return {
            id: item.id,
            title: item.querySelector('.notification-title')?.textContent || '',
            message: item.querySelector('.notification-message')?.textContent || '',
            time: item.querySelector('.notification-time')?.textContent || '',
            category: item.getAttribute('data-category') || 'general',
            priority: item.getAttribute('data-priority') || 'normal',
            read: item.classList.contains('read'),
            archived: item.classList.contains('archived'),
            actions: []
        };
    }

    initNotificationItemHandlers(item, notificationId) {
        // Click to mark as read
        item.addEventListener('click', (e) => {
            if (!e.target.closest('.notification-action') && 
                !e.target.closest('.notification-checkbox')) {
                this.markAsRead(notificationId);
            }
        });
        
        // Checkbox for selection
        const checkbox = item.querySelector('.notification-checkbox');
        if (checkbox) {
            checkbox.addEventListener('change', (e) => {
                this.toggleNotificationSelection(notificationId, e.target.checked);
            });
        }
        
        // Action buttons
        const actionButtons = item.querySelectorAll('.notification-action');
        actionButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.stopPropagation();
                const actionType = button.getAttribute('data-action-type');
                this.handleNotificationAction(notificationId, actionType);
            });
        });
    }

    // ===============================================
    // REAL-TIME UPDATES
    // ===============================================
    
    async initRealTimeUpdates() {
        this.log('Initializing real-time updates...');
        
        if (typeof WebSocket !== 'undefined') {
            this.initWebSocketConnection();
        } else if (typeof EventSource !== 'undefined') {
            this.initSSEConnection();
        } else {
            this.log('Real-time updates not supported in this browser');
        }
    }

    initWebSocketConnection() {
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const host = window.location.host;
            const wsUrl = `${protocol}//${host}/ws/notifications/`;
            
            this.realTimeConnection = new WebSocket(wsUrl);
            
            this.realTimeConnection.onopen = () => {
                this.log('WebSocket connection established');
                this.layout.dispatchEvent('notifications:realtime-connected');
            };
            
            this.realTimeConnection.onmessage = (event) => {
                this.handleRealTimeMessage(JSON.parse(event.data));
            };
            
            this.realTimeConnection.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.layout.dispatchEvent('notifications:realtime-error', { error });
            };
            
            this.realTimeConnection.onclose = () => {
                this.log('WebSocket connection closed');
                this.layout.dispatchEvent('notifications:realtime-disconnected');
                
                // Attempt reconnect
                setTimeout(() => {
                    if (this.initialized) {
                        this.initWebSocketConnection();
                    }
                }, 5000);
            };
            
        } catch (error) {
            console.error('Failed to establish WebSocket connection:', error);
        }
    }

    initSSEConnection() {
        try {
            const sseUrl = '/api/notifications/events/';
            this.realTimeConnection = new EventSource(sseUrl);
            
            this.realTimeConnection.onopen = () => {
                this.log('SSE connection established');
                this.layout.dispatchEvent('notifications:realtime-connected');
            };
            
            this.realTimeConnection.onmessage = (event) => {
                this.handleRealTimeMessage(JSON.parse(event.data));
            };
            
            this.realTimeConnection.onerror = (error) => {
                console.error('SSE error:', error);
                this.realTimeConnection.close();
                this.layout.dispatchEvent('notifications:realtime-error', { error });
                
                setTimeout(() => {
                    if (this.initialized) {
                        this.initSSEConnection();
                    }
                }, 5000);
            };
            
        } catch (error) {
            console.error('Failed to establish SSE connection:', error);
        }
    }

    handleRealTimeMessage(data) {
        switch (data.type) {
            case 'new_notification':
                this.addNewNotification(data.notification);
                break;
            case 'notification_update':
                this.updateNotification(data.notification);
                break;
            case 'notification_delete':
                this.deleteNotification(data.notification_id);
                break;
        }
        
        this.layout.dispatchEvent('notifications:realtime-message', {
            type: data.type,
            data,
            timestamp: Date.now()
        });
    }

    // ===============================================
    // NOTIFICATION OPERATIONS
    // ===============================================
    
    markAsRead(notificationId) {
        const notification = this.notifications.get(notificationId);
        if (!notification || notification.read) return;
        
        notification.read = true;
        if (notification.element) {
            notification.element.classList.remove('unread');
            notification.element.classList.add('read');
        }
        
        this.updateUnreadCount();
        
        this.layout.dispatchEvent('notifications:marked-read', {
            notificationId,
            timestamp: Date.now()
        });
        
        return true;
    }

    markAllAsRead() {
        let count = 0;
        this.notifications.forEach(notification => {
            if (!notification.read) {
                notification.read = true;
                if (notification.element) {
                    notification.element.classList.remove('unread');
                    notification.element.classList.add('read');
                }
                count++;
            }
        });
        
        this.updateUnreadCount();
        
        this.layout.dispatchEvent('notifications:all-marked-read', {
            count,
            timestamp: Date.now()
        });
        
        return count;
    }

    deleteNotification(notificationId) {
        const notification = this.notifications.get(notificationId);
        if (!notification) return false;
        
        if (notification.element?.parentNode) {
            notification.element.parentNode.removeChild(notification.element);
        }
        
        this.notifications.delete(notificationId);
        this.selectedNotifications.delete(notificationId);
        
        this.updateNotificationStats();
        
        this.layout.dispatchEvent('notifications:deleted', {
            notificationId,
            timestamp: Date.now()
        });
        
        return true;
    }

    archiveNotification(notificationId) {
        const notification = this.notifications.get(notificationId);
        if (!notification) return false;
        
        notification.archived = true;
        if (notification.element) {
            notification.element.classList.add('archived');
            notification.element.style.display = 'none';
        }
        
        this.updateNotificationStats();
        
        this.layout.dispatchEvent('notifications:archived', {
            notificationId,
            timestamp: Date.now()
        });
        
        return true;
    }

    handleNotificationAction(notificationId, actionType) {
        switch (actionType) {
            case 'view':
                this.viewNotification(notificationId);
                break;
            case 'reply':
                this.replyToNotification(notificationId);
                break;
            case 'forward':
                this.forwardNotification(notificationId);
                break;
            case 'save':
                this.saveNotification(notificationId);
                break;
            default:
                this.log(`Unknown action: ${actionType}`);
        }
    }

    viewNotification(notificationId) {
        const notification = this.notifications.get(notificationId);
        if (!notification) return;
        
        if (!notification.read) {
            this.markAsRead(notificationId);
        }
        
        this.showNotificationDetails(notification);
        
        this.layout.dispatchEvent('notifications:viewed', {
            notificationId,
            timestamp: Date.now()
        });
    }

    showNotificationDetails(notification) {
        let modal = document.querySelector('#notification-details-modal');
        
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'notification-details-modal';
            modal.className = 'notification-modal';
            modal.style.cssText = `
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.15);
                z-index: 9999;
                max-width: 600px;
                width: 90%;
                max-height: 80vh;
                overflow-y: auto;
            `;
            document.body.appendChild(modal);
        }
        
        modal.innerHTML = `
            <div class="modal-header">
                <h3>${notification.data.title}</h3>
                <button class="modal-close">&times;</button>
            </div>
            <div class="modal-body">
                <div class="notification-meta">
                    <span class="notification-category">${notification.data.category}</span>
                    <span class="notification-time">${notification.data.time}</span>
                </div>
                <div class="notification-content-detail">
                    ${notification.data.message}
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" data-action="close">Close</button>
            </div>
        `;
        
        modal.style.display = 'block';
        
        // Close handlers
        modal.querySelector('.modal-close').addEventListener('click', () => {
            modal.style.display = 'none';
        });
        
        modal.querySelector('[data-action="close"]').addEventListener('click', () => {
            modal.style.display = 'none';
        });
    }

    addNewNotification(notificationData) {
        const notificationId = notificationData.id || `new-${Date.now()}`;
        
        const notification = {
            element: null,
            id: notificationId,
            data: notificationData,
            read: false,
            selected: false,
            archived: false
        };
        
        this.notifications.set(notificationId, notification);
        
        const container = document.querySelector('.notifications-list, [data-notifications-list]');
        if (container) {
            const element = this.createNotificationElement(notification);
            container.insertBefore(element, container.firstChild);
            notification.element = element;
            this.initNotificationItemHandlers(element, notificationId);
            
            element.classList.add('new-notification');
            setTimeout(() => {
                element.classList.remove('new-notification');
            }, 3000);
        }
        
        this.updateNotificationStats();
        this.showNewNotificationBadge(notificationData);
        
        this.layout.dispatchEvent('notifications:new', {
            notification: notificationData,
            timestamp: Date.now()
        });
    }

    createNotificationElement(notification) {
        const element = document.createElement('div');
        element.className = `notification-item ${notification.read ? 'read' : 'unread'}`;
        element.id = notification.id;
        element.setAttribute('data-category', notification.data.category);
        element.setAttribute('data-priority', notification.data.priority);
        
        element.innerHTML = `
            <div class="notification-checkbox">
                <input type="checkbox">
            </div>
            <div class="notification-content">
                <div class="notification-header">
                    <h4 class="notification-title">${notification.data.title}</h4>
                    <span class="notification-time">${notification.data.time}</span>
                </div>
                <div class="notification-body">
                    <p class="notification-message">${notification.data.message}</p>
                </div>
            </div>
        `;
        
        return element;
    }

    // ===============================================
    // FILTERS & SELECTION
    // ===============================================
    
    toggleUnreadFilter() {
        this.filters.unread = !this.filters.unread;
        this.renderNotifications();
        
        this.layout.dispatchEvent('notifications:filter-changed', {
            filter: 'unread',
            value: this.filters.unread,
            timestamp: Date.now()
        });
    }

    filterByCategory(categoryId) {
        this.filters.category = this.filters.category === categoryId ? null : categoryId;
        this.renderNotifications();
        
        this.layout.dispatchEvent('notifications:filter-changed', {
            filter: 'category',
            value: this.filters.category,
            timestamp: Date.now()
        });
    }

    toggleNotificationSelection(notificationId, selected) {
        const notification = this.notifications.get(notificationId);
        if (!notification) return;
        
        notification.selected = selected;
        if (selected) {
            this.selectedNotifications.add(notificationId);
        } else {
            this.selectedNotifications.delete(notificationId);
        }
        
        this.updateSelectAllCheckbox();
        
        this.layout.dispatchEvent('notifications:selection-changed', {
            notificationId,
            selected,
            totalSelected: this.selectedNotifications.size
        });
    }

    // ===============================================
    // BULK ACTIONS
    // ===============================================
    
    bulkMarkAsRead() {
        let count = 0;
        this.selectedNotifications.forEach(notificationId => {
            if (this.markAsRead(notificationId)) {
                count++;
            }
        });
        
        this.clearSelection();
        
        this.layout.dispatchEvent('notifications:bulk-action', {
            action: 'mark-read',
            count
        });
        
        return count;
    }

    bulkDelete() {
        let count = 0;
        this.selectedNotifications.forEach(notificationId => {
            if (this.deleteNotification(notificationId)) {
                count++;
            }
        });
        
        this.clearSelection();
        
        this.layout.dispatchEvent('notifications:bulk-action', {
            action: 'delete',
            count
        });
        
        return count;
    }

    bulkArchive() {
        let count = 0;
        this.selectedNotifications.forEach(notificationId => {
            if (this.archiveNotification(notificationId)) {
                count++;
            }
        });
        
        this.clearSelection();
        
        this.layout.dispatchEvent('notifications:bulk-action', {
            action: 'archive',
            count
        });
        
        return count;
    }

    clearSelection() {
        this.selectedNotifications.clear();
        this.notifications.forEach(notification => {
            notification.selected = false;
            if (notification.element) {
                const checkbox = notification.element.querySelector('.notification-checkbox input');
                if (checkbox) {
                    checkbox.checked = false;
                }
            }
        });
        this.updateSelectAllCheckbox();
    }

    // ===============================================
    // AUTO-REFRESH
    // ===============================================
    
    async initAutoRefresh() {
        this.refreshTimer = setInterval(() => {
            this.refreshNotifications();
        }, 30000); // 30 seconds
        
        this.layout.cleanupFunctions.push(() => {
            if (this.refreshTimer) {
                clearInterval(this.refreshTimer);
            }
        });
    }

    async refreshNotifications() {
        this.log('Refreshing notifications...');
        
        // Simulate API call
        try {
            const response = await fetch('/api/notifications/');
            if (response.ok) {
                const data = await response.json();
                this.processLoadedNotifications(data.notifications || []);
            }
        } catch (error) {
            console.error('Failed to refresh notifications:', error);
        }
        
        this.layout.dispatchEvent('notifications:refreshed', {
            timestamp: Date.now()
        });
    }

    processLoadedNotifications(notifications) {
        // Update existing notifications
        notifications.forEach(notificationData => {
            const existing = this.notifications.get(notificationData.id);
            if (existing) {
                existing.data = { ...existing.data, ...notificationData };
                if (existing.element) {
                    // Update DOM
                    const titleEl = existing.element.querySelector('.notification-title');
                    const messageEl = existing.element.querySelector('.notification-message');
                    const timeEl = existing.element.querySelector('.notification-time');
                    
                    if (titleEl) titleEl.textContent = notificationData.title || existing.data.title;
                    if (messageEl) messageEl.textContent = notificationData.message || existing.data.message;
                    if (timeEl) timeEl.textContent = notificationData.time || existing.data.time;
                }
            } else {
                // Add new notification
                this.addNewNotification(notificationData);
            }
        });
        
        this.updateNotificationStats();
    }

    renderNotifications() {
        const container = document.querySelector('.notifications-list, [data-notifications-list]');
        if (!container) return;
        
        const filteredNotifications = this.getFilteredNotifications();
        container.innerHTML = '';
        
        filteredNotifications.forEach(notification => {
            const element = this.createNotificationElement(notification);
            container.appendChild(element);
            notification.element = element;
            this.initNotificationItemHandlers(element, notification.id);
        });
    }

    getFilteredNotifications() {
        let filtered = Array.from(this.notifications.values());
        
        if (this.filters.unread) {
            filtered = filtered.filter(n => !n.read);
        }
        
        if (this.filters.category) {
            filtered = filtered.filter(n => n.data.category === this.filters.category);
        }
        
        if (this.filters.priority) {
            filtered = filtered.filter(n => n.data.priority === this.filters.priority);
        }
        
        return filtered;
    }

    // ===============================================
    // STATS & ANALYTICS
    // ===============================================
    
    updateNotificationStats() {
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
        
        this.notificationStats = { total, unread, read, archived };
        this.unreadCount = unread;
        
        this.updateStatsUI();
    }

    updateStatsUI() {
        // Update total count
        document.querySelectorAll('.notification-total, [data-notification-total]').forEach(el => {
            el.textContent = this.notificationStats.total;
        });
        
        // Update unread count
        document.querySelectorAll('.notification-unread, [data-notification-unread]').forEach(el => {
            el.textContent = this.notificationStats.unread;
        });
        
        // Update badge
        const badge = document.querySelector('.notification-badge, [data-notification-badge]');
        if (badge) {
            badge.textContent = this.notificationStats.unread;
            badge.style.display = this.notificationStats.unread > 0 ? 'inline-block' : 'none';
        }
    }

    updateUnreadCount() {
        let unread = 0;
        this.notifications.forEach(notification => {
            if (!notification.read) unread++;
        });
        
        this.unreadCount = unread;
        this.notificationStats.unread = unread;
        this.updateStatsUI();
    }

    updateSelectAllCheckbox() {
        const selectAllCheckbox = document.querySelector('.select-all, [data-select-all]');
        if (!selectAllCheckbox) return;
        
        const total = this.notifications.size;
        const selected = this.selectedNotifications.size;
        
        if (selected === 0) {
            selectAllCheckbox.checked = false;
            selectAllCheckbox.indeterminate = false;
        } else if (selected === total) {
            selectAllCheckbox.checked = true;
            selectAllCheckbox.indeterminate = false;
        } else {
            selectAllCheckbox.checked = false;
            selectAllCheckbox.indeterminate = true;
        }
    }

    // ===============================================
    // NOTIFICATION ANALYTICS
    // ===============================================
    
    async initNotificationAnalytics() {
        // Track notification interactions
        document.addEventListener('click', (e) => {
            const notificationItem = e.target.closest('.notification-item');
            if (notificationItem) {
                this.trackNotificationClick(notificationItem);
            }
        });
        
        // Track notification reads
        this.layout.on('notifications:marked-read', (data) => {
            this.trackNotificationRead(data.detail);
        });
    }

    trackNotificationClick(notificationElement) {
        const notificationId = notificationElement.id;
        const notification = this.notifications.get(notificationId);
        
        if (notification) {
            this.layout.dispatchEvent('notifications:click-tracked', {
                notificationId,
                category: notification.data.category,
                read: notification.read
            });
        }
    }

    trackNotificationRead(data) {
        this.layout.dispatchEvent('notifications:read-tracked', {
            ...data,
            unreadCount: this.unreadCount
        });
    }

    // ===============================================
    // UI UTILITIES
    // ===============================================
    
    showNewNotificationBadge(notification) {
        let badge = document.querySelector('.new-notification-badge');
        
        if (!badge) {
            badge = document.createElement('div');
            badge.className = 'new-notification-badge';
            badge.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: #dc3545;
                color: white;
                padding: 10px 20px;
                border-radius: 20px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                z-index: 9998;
                animation: slideInRight 0.3s ease;
            `;
            document.body.appendChild(badge);
        }
        
        badge.innerHTML = `
            <strong>${notification.title}</strong>
            <p style="margin: 5px 0 0 0; font-size: 12px;">${notification.message}</p>
        `;
        
        setTimeout(() => {
            if (badge.parentNode) {
                badge.parentNode.removeChild(badge);
            }
        }, 5000);
    }

    showNotificationToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `notification-toast toast-${type}`;
        toast.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            padding: 12px 24px;
            border-radius: 4px;
            color: white;
            z-index: 9999;
            animation: slideInUp 0.3s ease;
        `;
        
        const colors = {
            info: '#17a2b8',
            success: '#28a745',
            warning: '#ffc107',
            error: '#dc3545'
        };
        
        toast.style.backgroundColor = colors[type] || colors.info;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 5000);
    }

    // ===============================================
    // HELPER METHODS
    // ===============================================
    
    registerComponent(name, component) {
        this.layout.registerComponent(name, component);
    }

    getNotificationStats() {
        return { ...this.notificationStats };
    }

    getUnreadCount() {
        return this.unreadCount;
    }

    getNotifications(filter = null) {
        let notifications = Array.from(this.notifications.values());
        if (filter) {
            notifications = notifications.filter(filter);
        }
        return notifications;
    }

    getSelectedNotifications() {
        return Array.from(this.selectedNotifications);
    }

    getFilterState() {
        return { ...this.filters };
    }
}

export default NotificationsService;