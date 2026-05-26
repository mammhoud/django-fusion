/**
 * @file layouts/notifications.layout.js
 * Notifications Layout with Integrated Notification System
 */

import { BaseLayout } from './base.layout.js';
import { NotificationsService } from './notifications/service.js';

export class NotificationsLayout extends BaseLayout {
    constructor(options = {}) {
        super({
            layoutId: 'notifications',
            layoutType: 'notifications',
            pageId: options.pageId || 'notifications',
            debug: options.debug || false,
            enableRealTime: options.enableRealTime !== false,
            enableCategories: options.enableCategories !== false,
            enableFilters: options.enableFilters !== false,
            enableBulkActions: options.enableBulkActions !== false,
            autoRefresh: options.autoRefresh || false,
            ...options
        });

        // Notifications service
        this.notificationsService = new NotificationsService(this);
        
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
    }

    async initComponents() {
        this.log('🔔 Initializing notifications components...');
        
        // Initialize notifications service
        await this.notificationsService.init();
        
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
        
        this.log('✅ Notifications components initialized');
    }

    async applyContent() {
        this.log('Applying notifications layout content...');
        
        // Detect notification type from URL
        this.detectNotificationTypeFromURL();
        
        // Apply notification type specific content
        await this.applyNotificationTypeContent();
        
        // Update notification UI
        this.updateNotificationUI();
    }

    detectNotificationTypeFromURL(url = window.location.pathname) {
        const typeMap = {
            '/notifications': this.notificationTypes.INBOX,
            '/alerts': this.notificationTypes.ALERTS,
            '/messages': this.notificationTypes.MESSAGES,
            '/announcements': this.notificationTypes.ANNOUNCEMENTS,
            '/activity': this.notificationTypes.ACTIVITY,
            '/updates': this.notificationTypes.UPDATES
        };
        
        if (typeMap[url]) {
            this.currentNotificationType = typeMap[url];
        } else {
            const segments = url.split('/').filter(s => s);
            this.currentNotificationType = segments[0] || 'inbox';
        }
        
        this.options.notificationType = this.currentNotificationType;
        this.log(`Notification type detected: ${this.currentNotificationType}`);
        
        return this.currentNotificationType;
    }

    async applyNotificationTypeContent() {
        this.log(`Applying content for notification type: ${this.currentNotificationType}`);
        
        // Add notification type class
        document.body.classList.add(`notifications-${this.currentNotificationType}`);
        
        // Apply notification type specific transformations
        switch (this.currentNotificationType) {
            case this.notificationTypes.INBOX:
                await this.applyInboxContent();
                break;
            case this.notificationTypes.ALERTS:
                await this.applyAlertsContent();
                break;
            case this.notificationTypes.MESSAGES:
                await this.applyMessagesContent();
                break;
            case this.notificationTypes.ANNOUNCEMENTS:
                await this.applyAnnouncementsContent();
                break;
            case this.notificationTypes.ACTIVITY:
                await this.applyActivityContent();
                break;
        }
        
        this.dispatchEvent('notifications:type-content-applied', {
            notificationType: this.currentNotificationType,
            timestamp: Date.now()
        });
    }

    async applyInboxContent() {
        this.log('Applying inbox content...');
        
        // Initialize inbox-specific features
        await this.initInboxFilters();
        await this.initMessageThreads();
        
        // Setup refresh button
        const refreshBtn = document.querySelector('.refresh-notifications');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.notificationsService.refreshNotifications();
            });
        }
    }

    async applyAlertsContent() {
        this.log('Applying alerts content...');
        
        // Initialize alerts-specific features
        await this.initAlertPriorities();
        await this.initAlertActions();
        
        // Setup alert sound if available
        if (this.options.enableSounds) {
            await this.initAlertSounds();
        }
    }

    async applyMessagesContent() {
        this.log('Applying messages content...');
        
        // Initialize messages-specific features
        await this.initMessageComposer();
        await this.initConversationView();
        
        // Setup message search
        const searchInput = document.querySelector('.message-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchMessages(e.target.value);
            });
        }
    }

    async initCategories() {
        const categoryElements = document.querySelectorAll('.notification-category, [data-category]');
        
        categoryElements.forEach(element => {
            const categoryId = element.dataset.category || element.textContent.toLowerCase();
            element.addEventListener('click', () => {
                this.notificationsService.filterByCategory(categoryId);
            });
        });
    }

    async initFilters() {
        // Unread filter
        const unreadFilter = document.querySelector('.filter-unread, [data-filter="unread"]');
        if (unreadFilter) {
            unreadFilter.addEventListener('click', () => {
                this.notificationsService.toggleUnreadFilter();
            });
        }
        
        // Date filter
        const dateFilter = document.querySelector('.filter-date, [data-filter="date"]');
        if (dateFilter) {
            dateFilter.addEventListener('change', (e) => {
                this.notificationsService.filterByDateRange(e.target.value);
            });
        }
        
        // Clear filters
        const clearFilters = document.querySelector('.clear-filters, [data-clear-filters]');
        if (clearFilters) {
            clearFilters.addEventListener('click', () => {
                this.clearFilters();
            });
        }
    }

    async initBulkActions() {
        // Select all
        const selectAll = document.querySelector('.select-all, [data-select-all]');
        if (selectAll) {
            selectAll.addEventListener('change', (e) => {
                this.toggleSelectAll(e.target.checked);
            });
        }
        
        // Mark as read
        const markRead = document.querySelector('.bulk-mark-read, [data-bulk-action="mark-read"]');
        if (markRead) {
            markRead.addEventListener('click', () => {
                this.notificationsService.bulkMarkAsRead();
            });
        }
        
        // Delete
        const deleteBtn = document.querySelector('.bulk-delete, [data-bulk-action="delete"]');
        if (deleteBtn) {
            deleteBtn.addEventListener('click', () => {
                if (confirm('Delete selected notifications?')) {
                    this.notificationsService.bulkDelete();
                }
            });
        }
        
        // Archive
        const archiveBtn = document.querySelector('.bulk-archive, [data-bulk-action="archive"]');
        if (archiveBtn) {
            archiveBtn.addEventListener('click', () => {
                this.notificationsService.bulkArchive();
            });
        }
    }

    toggleSelectAll(selected) {
        if (selected) {
            this.notificationsService.notifications.forEach((notification, id) => {
                this.notificationsService.toggleNotificationSelection(id, true);
            });
        } else {
            this.notificationsService.clearSelection();
        }
    }

    clearFilters() {
        this.notificationsService.filters = {
            unread: false,
            category: null,
            dateRange: null,
            priority: null
        };
        
        document.querySelectorAll('[data-filter]').forEach(el => {
            el.classList.remove('active');
        });
        
        document.querySelectorAll('select.filter-select').forEach(select => {
            select.value = '';
        });
        
        this.notificationsService.renderNotifications();
        
        this.dispatchEvent('notifications:filters-cleared');
    }

    // Notification type specific initialization methods
    async initInboxFilters() {
        // Additional inbox filter initialization
        const priorityFilter = document.querySelector('.filter-priority');
        if (priorityFilter) {
            priorityFilter.addEventListener('change', (e) => {
                this.notificationsService.filterByPriority(e.target.value);
            });
        }
    }

    async initMessageThreads() {
        const threads = document.querySelectorAll('.message-thread');
        threads.forEach(thread => {
            thread.addEventListener('click', () => {
                const threadId = thread.dataset.threadId;
                this.loadThreadMessages(threadId);
            });
        });
    }

    async initAlertPriorities() {
        const priorityBadges = document.querySelectorAll('.priority-badge');
        priorityBadges.forEach(badge => {
            const priority = badge.dataset.priority;
            badge.style.backgroundColor = 
                priority === 'high' ? '#dc3545' :
                priority === 'medium' ? '#ffc107' : '#17a2b8';
        });
    }

    async initAlertActions() {
        const alertActions = document.querySelectorAll('.alert-action');
        alertActions.forEach(action => {
            action.addEventListener('click', (e) => {
                e.stopPropagation();
                const alertId = action.closest('.alert-item')?.dataset.alertId;
                const actionType = action.dataset.actionType;
                
                if (alertId) {
                    this.handleAlertAction(alertId, actionType);
                }
            });
        });
    }

    async initMessageComposer() {
        const composer = document.querySelector('.message-composer');
        if (composer) {
            const form = composer.querySelector('form');
            if (form) {
                form.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    await this.sendMessage(form);
                });
            }
        }
    }

    async initConversationView() {
        // Setup conversation scrolling
        const conversation = document.querySelector('.conversation-view');
        if (conversation) {
            conversation.scrollTop = conversation.scrollHeight;
            
            // Auto-scroll to new messages
            const observer = new MutationObserver(() => {
                conversation.scrollTop = conversation.scrollHeight;
            });
            
            observer.observe(conversation, { childList: true });
            
            this.cleanupFunctions.push(() => observer.disconnect());
        }
    }

    // Helper methods
    async loadThreadMessages(threadId) {
        try {
            const response = await fetch(`/api/messages/thread/${threadId}/`);
            if (response.ok) {
                const messages = await response.json();
                this.renderThreadMessages(messages);
            }
        } catch (error) {
            console.error('Failed to load thread messages:', error);
        }
    }

    renderThreadMessages(messages) {
        const container = document.querySelector('.conversation-messages');
        if (!container) return;
        
        container.innerHTML = '';
        
        messages.forEach(message => {
            const messageEl = document.createElement('div');
            messageEl.className = `message ${message.sender === 'user' ? 'sent' : 'received'}`;
            messageEl.innerHTML = `
                <div class="message-content">${message.content}</div>
                <div class="message-time">${message.time}</div>
            `;
            container.appendChild(messageEl);
        });
    }

    async sendMessage(form) {
        const formData = new FormData(form);
        
        try {
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                form.reset();
                this.showToast('Message sent', 'success');
            } else {
                throw new Error('Failed to send message');
            }
        } catch (error) {
            console.error('Failed to send message:', error);
            this.showToast('Failed to send message', 'error');
        }
    }

    handleAlertAction(alertId, actionType) {
        switch (actionType) {
            case 'acknowledge':
                this.acknowledgeAlert(alertId);
                break;
            case 'dismiss':
                this.dismissAlert(alertId);
                break;
            case 'escalate':
                this.escalateAlert(alertId);
                break;
        }
    }

    async acknowledgeAlert(alertId) {
        try {
            await fetch(`/api/alerts/${alertId}/acknowledge/`, { method: 'POST' });
            this.showToast('Alert acknowledged', 'success');
        } catch (error) {
            console.error('Failed to acknowledge alert:', error);
        }
    }

    searchMessages(query) {
        const messages = document.querySelectorAll('.message-item');
        messages.forEach(message => {
            const text = message.textContent.toLowerCase();
            message.style.display = text.includes(query.toLowerCase()) ? '' : 'none';
        });
    }

    showToast(message, type = 'info') {
        this.notificationsService.showNotificationToast(message, type);
    }

    updateNotificationUI() {
        // Update notification type indicators
        document.querySelectorAll('[data-notification-type]').forEach(element => {
            element.classList.toggle('active', 
                element.dataset.notificationType === this.currentNotificationType);
        });
        
        // Update notification status
        this.updateNotificationStatus();
    }

    updateNotificationStatus() {
        const lastRefresh = document.querySelector('.last-refresh, [data-last-refresh]');
        if (lastRefresh) {
            lastRefresh.textContent = 'Last updated: just now';
        }
        
        const connectionStatus = document.querySelector('.connection-status, [data-connection-status]');
        if (connectionStatus) {
            const connected = this.notificationsService.realTimeConnection?.readyState === 1;
            connectionStatus.textContent = connected ? 'Connected' : 'Disconnected';
            connectionStatus.classList.toggle('connected', connected);
            connectionStatus.classList.toggle('disconnected', !connected);
        }
    }

    // Public API through notifications service
    showNotification(message, type = 'info') {
        this.notificationsService.showNotificationToast(message, type);
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showWarning(message) {
        this.showNotification(message, 'warning');
    }

    showInfo(message) {
        this.showNotification(message, 'info');
    }

    markAsRead(notificationId) {
        return this.notificationsService.markAsRead(notificationId);
    }

    markAllAsRead() {
        return this.notificationsService.markAllAsRead();
    }

    getNotificationStats() {
        return this.notificationsService.getNotificationStats();
    }

    getUnreadCount() {
        return this.notificationsService.getUnreadCount();
    }

    getNotifications(filter = null) {
        return this.notificationsService.getNotifications(filter);
    }

    refreshNow() {
        return this.notificationsService.refreshNotifications();
    }

    // Cleanup
    async destroy() {
        // Destroy notifications service
        await this.notificationsService.destroy();
        
        // Call parent destroy
        await super.destroy();
    }
}

export default NotificationsLayout;