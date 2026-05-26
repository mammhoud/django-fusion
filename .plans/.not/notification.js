/**
 * Enhanced Notification System with SSE Integration
 * Integrates with SSEManager for connection handling
 */

import { SSEHandler } from './handler.js';
import { debounce, Utils, DOM } from '../utility/index.js';

export class NotificationSystem {
    constructor() {
        // SSEManager instance
        this.sseManager = window.SSEManager || new SSEHandler();
        
        // Notification UI properties
        this.toastContainer = null;
        this.alertContainer = null;
        this.notifications = new Map();
        this.maxNotifications = 5;
        this.defaultDuration = 5000;
        
        // Bootstrap Toast instance map
        this.toastInstances = new Map();
        
        // Django messages processing
        this.messagesProcessed = false;
        
        // SSE connection ID
        this.sseConnectionId = null;
        this.notificationConnectionId = null;
        
        // Configuration
        this.config = {
            useSSE: true,
            useChannels: false,
            autoConnect: true,
            reconnect: true,
            maxReconnectAttempts: 5,
            paths: ['/profile/', '/auth/','/courses/']
        };
        
        this.initialize();
    }
    
    /**
     * Initialize notification system
     */
    initialize() {
        console.log('🔔 Initializing enhanced notification system...');
        
        this.setupContainers();
        this.setupGlobalMethods();
        this.setupEventListeners();
        this.setupHTMXIntegration();
        
        // Process Django messages
        this.processDjangoMessages();
        
        // Setup SSE connection for notifications
        this.setupSSEConnection();
        
        return this;
    }
    
    /**
     * Setup notification containers
     */
    setupContainers() {
        // Get toast container
        this.toastContainer = document.getElementById('toast-container');
        if (!this.toastContainer) {
            console.warn('Toast container not found. Creating one...');
            this.toastContainer = DOM.create('div', {
                id: 'toast-container',
                class: 'toast-container position-fixed p-3'
            });
            this.toastContainer.style.cssText = 'z-index: 1055; top: 20px; right: 20px;';
            this.toastContainer.setAttribute('aria-live', 'polite');
            this.toastContainer.setAttribute('aria-atomic', 'true');
            document.body.appendChild(this.toastContainer);
        }
        
        // Get alert container
        this.alertContainer = document.getElementById('alert-container');
        
        // Create templates if they don't exist
        this.createTemplates();
    }
    
    /**
     * Create notification templates
     */
    createTemplates() {
        // Toast template
        if (!document.getElementById('toast-template')) {
            const toastTemplate = DOM.create('template', { id: 'toast-template' });
            toastTemplate.innerHTML = `
                <div class="toast" role="alert" aria-live="assertive" aria-atomic="true" data-bs-delay="5000">
                    <div class="toast-header bg-{{ level }} text-white">
                        <i class="{{ icon }} me-2"></i>
                        <strong class="me-auto">{{ title }}</strong>
                        <small class="text-white-50">{{ time }}</small>
                        <button type="button" class="btn-close btn-close-white ms-2" data-bs-dismiss="toast" aria-label="Close"></button>
                    </div>
                    <div class="toast-body">
                        {{ message }}
                    </div>
                </div>
            `;
            document.body.appendChild(toastTemplate);
        }
        
        // Alert template
        if (!document.getElementById('alert-template')) {
            const alertTemplate = DOM.create('template', { id: 'alert-template' });
            alertTemplate.innerHTML = `
                <div class="alert alert-{{ level }} alert-dismissible fade show" role="alert">
                    {% if icon %}<i class="{{ icon }} me-2"></i>{% endif %}
                    <strong>{{ title }}</strong>
                    <span class="ms-2">{{ message }}</span>
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                </div>
            `;
            document.body.appendChild(alertTemplate);
        }
    }
    
    /**
     * Clear all notifications
     */
    clear() {
        // Clear toasts
        this.toastInstances.forEach((toast, id) => {
            toast.hide();
        });
        this.toastInstances.clear();
        
        // Clear alerts
        const alerts = document.querySelectorAll('.alert-dismissible');
        alerts.forEach(alert => {
            const closeBtn = alert.querySelector('.btn-close');
            if (closeBtn) closeBtn.click();
        });
    }
    
    /**
     * Setup global methods
     */
    setupGlobalMethods() {
        // Notification methods
        window.showNotification = this.show.bind(this);
        window.showToast = this.showToast.bind(this);
        window.showAlert = this.showAlert.bind(this);
        window.showSuccess = this.success.bind(this);
        window.showError = this.error.bind(this);
        window.showWarning = this.warning.bind(this);
        window.showInfo = this.info.bind(this);
        window.showSSE = this.showSSENotification.bind(this);
        window.clearNotifications = this.clear.bind(this);
        
        // SSE methods - Use SSEManager methods
        window.createSSEConnection = this.sseManager.createConnection.bind(this.sseManager);
        window.closeSSEConnection = this.sseManager.closeConnection.bind(this.sseManager);
        window.getSSEStatus = this.sseManager.getConnectionStatus.bind(this.sseManager);
        window.closeAllSSEConnections = this.sseManager.closeAllConnections.bind(this.sseManager);
        
        // Expose manager instance
        window.notificationSystem = this;
    }
    
    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Page visibility changes
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseAllNotificationTimers();
            } else {
                this.resumeAllNotificationTimers();
            }
        });
        
        // Custom notification events
        document.addEventListener('notification:show', (event) => {
            if (event.detail && !event.detail.processed) {
                const { message, options } = event.detail;
                this.show(message, options);
            }
        });
        
        // HTMX events
        document.addEventListener('htmx:afterSwap', (event) => {
            // Process new Django messages after HTMX swap
            setTimeout(() => this.processDjangoMessages(), 100);
        });
        
        // SSE events from SSEManager
        this.sseManager.on('notification', (event) => {
            this.handleSSEMessage(event.detail.data, event.detail.connectionId);
        });
        
        this.sseManager.on('session:update', (event) => {
            this.handleSessionUpdate(event.detail.data);
        });
    }
    
    /**
     * Setup HTMX integration
     */
    setupHTMXIntegration() {
        // Add notification support for HTMX responses
        document.addEventListener('htmx:beforeSwap', (event) => {
            const response = event.detail.xhr.response;
            
            // Check for HX-Trigger header with notifications
            const triggerHeader = event.detail.xhr.getResponseHeader('HX-Trigger');
            if (triggerHeader) {
                try {
                    const triggers = JSON.parse(triggerHeader);
                    if (triggers.showNotification) {
                        const { message, level, title, duration } = triggers.showNotification;
                        this.show(message, {
                            type: level || 'info',
                            title: title || 'Notification',
                            duration: duration || 5000
                        });
                    }
                } catch (e) {
                    console.error('Failed to parse HX-Trigger:', e);
                }
            }
        });
    }
    
    // ===============================================
    // DJANGO MESSAGES PROCESSING
    // ===============================================
    
    /**
     * Process Django messages from template
     */
    processDjangoMessages() {
        const messagesContainer = document.getElementById('django-messages');
        if (!messagesContainer || this.messagesProcessed) return;
        
        const messages = messagesContainer.querySelectorAll('.django-message');
        messages.forEach(messageEl => {
            const level = messageEl.getAttribute('data-level') || 'info';
            const message = messageEl.getAttribute('data-message') || messageEl.textContent;
            const tags = messageEl.getAttribute('data-tags') || '';
            
            // Map Django message levels to notification types
            const levelMap = {
                'debug': 'info',
                'info': 'info',
                'success': 'success',
                'warning': 'warning',
                'error': 'error'
            };
            
            const type = levelMap[level] || 'info';
            
            // Show notification
            this.show(message, {
                type: type,
                title: this.getTitleFromLevel(level),
                duration: 5000,
                metadata: { source: 'django', tags: tags }
            });
        });
        
        // Mark as processed
        messagesContainer.setAttribute('data-processed', 'true');
        this.messagesProcessed = true;
    }
    
    /**
     * Get title from Django message level
     */
    getTitleFromLevel(level) {
        const titleMap = {
            'debug': 'Debug',
            'info': 'Information',
            'success': 'Success',
            'warning': 'Warning',
            'error': 'Error'
        };
        return titleMap[level] || 'Notification';
    }
    
    /**
     * Setup SSE connection for notifications
     */
    setupSSEConnection() {
        if (!this.config.useSSE) {
            console.log('SSE notifications disabled');
            return;
        }
        
        const currentPath = window.location.pathname;
        const shouldConnect = this.config.paths.some(path => currentPath.includes(path));
        
        if (shouldConnect) {
            this.createNotificationConnection();
        }
    }
    
    /**
     * Create notification SSE connection
     */
    async createNotificationConnection() {
        try {
            // Determine connection URL
            const sseElement = document.getElementById('sse-connection');
            let sseUrl = '/notifications/';
            
            if (sseElement) {
                const sseConnect = sseElement.getAttribute('sse-connect');
                if (sseConnect && sseConnect !== '/') {
                    sseUrl = sseConnect;
                }
            }
            
            // Check if connection already exists
            const existingConnections = this.sseManager.getAllConnections();
            const existingNotificationConn = Object.values(existingConnections)
                .find(conn => conn.name === 'notifications');
            
            if (existingNotificationConn) {
                console.log('Using existing notification connection');
                this.notificationConnectionId = Object.keys(existingConnections)
                    .find(key => existingConnections[key] === existingNotificationConn);
                return;
            }
            
            // Create new connection
            this.notificationConnectionId = await this.sseManager.createConnection(sseUrl, {
                name: 'notifications',
                onOpen: (connectionId) => {
                    console.log(`📡 Notification connection opened: ${connectionId}`);
                    this.show('Real-time notifications enabled', {
                        type: 'info',
                        title: 'SSE Connected',
                        duration: 3000
                    });
                },
                onMessage: (data, connectionId) => {
                    this.handleSSEMessage(data, connectionId);
                },
                onError: (error, connectionId) => {
                    console.error(`Notification connection error:`, error);
                    this.handleConnectionError(error);
                }
            });
            
            console.log('✅ Notification SSE connection created');
            
        } catch (error) {
            console.error('Failed to create notification connection:', error);
            
            // Retry after delay if auto-reconnect is enabled
            if (this.config.reconnect) {
                setTimeout(() => this.createNotificationConnection(), 10000);
            }
        }
    }
    
    /**
     * Handle SSE message
     */
    handleSSEMessage(data, connectionId) {
        const messageType = data.type || data.event;
        
        switch (messageType) {
            case 'notification':
                this.handleNotification(data.data || data);
                break;
                
            case 'session_update':
                this.handleSessionUpdate(data.data || data);
                break;
                
            case 'system_alert':
                this.handleSystemAlert(data.data || data);
                break;
                
            case 'ping':
                // Just acknowledge ping
                break;
                
            default:
                // Default to notification if message or title exists
                if (data.message || data.title) {
                    this.handleNotification(data);
                }
        }
    }
    
    /**
     * Handle notification from SSE
     */
    handleNotification(data) {
        const { 
            type = 'info', 
            title, 
            message, 
            duration = 5000, 
            source = 'server',
            display = 'toast',
            actions = []
        } = data;
        
        if (!message && !title) return;
        
        const notificationId = this.show(message || title, {
            type: type,
            title: title || `Server Notification (${source})`,
            duration,
            displayType: display,
            actions: actions.map(action => ({
                text: action.text,
                type: action.type || 'default',
                callback: () => {
                    if (action.url) {
                        window.location.href = action.url;
                    } else if (action.callback) {
                        try {
                            const fn = new Function(action.callback);
                            fn();
                        } catch (e) {
                            console.error('Failed to execute callback:', e);
                        }
                    }
                }
            })),
            metadata: {
                source: 'sse',
                timestamp: new Date().toISOString()
            }
        });
        
        // Dispatch event
        DOM.trigger(document, 'notification:sse:show', { 
            id: notificationId, 
            data,
            type: 'sse' 
        });
        
        return notificationId;
    }
    
    /**
     * Handle session updates
     */
    handleSessionUpdate(data) {
        const { action, reason, user } = data;
        
        switch (action) {
            case 'logout':
                this.handleLogout(reason, user);
                break;
                
            case 'refresh':
                this.handleRefresh();
                break;
                
            case 'expire_warning':
                this.handleExpireWarning(data.timeLeft);
                break;
                
            case 'multiple_sessions':
                this.handleMultipleSessions(data);
                break;
        }
    }
    
    /**
     * Handle logout notification
     */
    handleLogout(reason = 'Session expired', user = null) {
        const username = user ? `${user} - ` : '';
        
        this.warning(`${username}${reason}`, {
            title: 'Session Ended',
            duration: 10000,
            displayType: 'alert',
            actions: [
                {
                    text: 'Re-login',
                    type: 'primary',
                    callback: () => {
                        window.location.href = '/auth/login/';
                    }
                }
            ]
        });
        
        // Auto-redirect after delay
        setTimeout(() => {
            if (window.location.pathname.includes('/auth/')) return;
            window.location.href = '/auth/login/';
        }, 10000);
    }
    
    /**
     * Handle session refresh
     */
    handleRefresh() {
        this.info('Your session has been refreshed', {
            title: 'Session Refreshed',
            duration: 3000
        });
    }
    
    /**
     * Handle session expire warning
     */
    handleExpireWarning(timeLeft) {
        const minutes = Math.ceil(timeLeft / 60);
        const seconds = timeLeft % 60;
        
        let timeText = '';
        if (minutes > 0) {
            timeText = `${minutes} minute${minutes > 1 ? 's' : ''}`;
            if (seconds > 0) {
                timeText += ` ${seconds} second${seconds > 1 ? 's' : ''}`;
            }
        } else {
            timeText = `${seconds} second${seconds > 1 ? 's' : ''}`;
        }
        
        this.warning(`Your session will expire in ${timeText}.`, {
            title: 'Session Expiring Soon',
            duration: 10000,
            displayType: 'alert',
            actions: [
                {
                    text: 'Extend Session',
                    type: 'primary',
                    callback: () => {
                        this.extendSession();
                    }
                }
            ]
        });
    }
    
    /**
     * Handle multiple sessions
     */
    handleMultipleSessions(data) {
        const { location, device, time } = data;
        
        this.warning(`New login detected from ${location} (${device}) at ${new Date(time).toLocaleTimeString()}`, {
            title: 'Security Alert',
            duration: 15000,
            displayType: 'alert',
            actions: [
                {
                    text: 'View Sessions',
                    type: 'primary',
                    callback: () => {
                        window.location.href = '/profile/settings/#sessions';
                    }
                },
                {
                    text: 'Logout All',
                    callback: () => {
                        this.logoutAllSessions();
                    }
                }
            ]
        });
    }
    
    /**
     * Handle system alerts
     */
    handleSystemAlert(data) {
        const { level = 'info', title, message, actions = [] } = data;
        
        this[level](message, {
            title: title || 'System Alert',
            duration: 10000,
            displayType: 'alert',
            actions: actions.map(action => ({
                text: action.text,
                type: action.type || 'default',
                callback: () => {
                    if (action.url) {
                        window.location.href = action.url;
                    }
                }
            }))
        });
    }
    
    /**
     * Handle connection error
     */
    handleConnectionError(error) {
        this.error('Real-time notifications disconnected', {
            title: 'Connection Error',
            duration: 5000
        });
    }
    
    // ===============================================
    // SESSION MANAGEMENT
    // ===============================================
    
    /**
     * Extend session
     */
    async extendSession() {
        try {
            this.info('Extending session...', {
                title: 'Please wait',
                duration: 3000
            });
            
            const response = await fetch('/api/session/extend/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            
            if (response.ok) {
                this.success('Session extended successfully', {
                    duration: 3000
                });
            } else {
                throw new Error('Failed to extend session');
            }
        } catch (error) {
            this.error('Failed to extend session. Please login again.', {
                duration: 5000
            });
        }
    }
    
    /**
     * Logout all sessions
     */
    async logoutAllSessions() {
        try {
            await fetch('/api/sessions/logout-all/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            
            this.success('All other sessions have been logged out', {
                duration: 3000
            });
        } catch (error) {
            this.error('Failed to logout all sessions', {
                duration: 3000
            });
        }
    }
    
    // ===============================================
    // CONFIGURATION
    // ===============================================
    
    /**
     * Configure notification system
     */
    configure(config) {
        this.config = { ...this.config, ...config };
        
        // Update SSE manager if max connections changed
        if (config.maxConnections) {
            this.sseManager.setMaxConnections(config.maxConnections);
        }
        
        // Enable/disable Channels
        if (config.useChannels !== undefined) {
            if (config.useChannels) {
                this.sseManager.enableChannels(config.channelPath);
            } else {
                this.sseManager.disableChannels();
            }
        }
        
        console.log('🔔 Notification system reconfigured');
    }
    
    /**
     * Get SSE connection status
     */
    getSSEStatus() {
        if (!this.notificationConnectionId) {
            return 'disconnected';
        }
        
        return this.sseManager.getConnectionStatus(this.notificationConnectionId);
    }
    
    /**
     * Get all SSE connections
     */
    getAllSSEConnections() {
        return this.sseManager.getAllConnections();
    }
    
    /**
     * Reconnect SSE
     */
    async reconnectSSE() {
        if (this.notificationConnectionId) {
            this.sseManager.closeConnection(this.notificationConnectionId);
        }
        
        await this.createNotificationConnection();
    }
    
    /**
     * Show SSE notification
     */
    showSSENotification(data) {
        const { 
            type = 'info', 
            title, 
            message, 
            duration = 5000, 
            source = 'server',
            display = 'toast' // 'toast' or 'alert'
        } = data;
        
        if (!message && !title) return;
        
        const notificationId = this.show(message || title, {
            type: type,
            title: title || `Server Notification (${source})`,
            duration,
            displayType: display,
            metadata: {
                source: 'sse',
                timestamp: new Date().toISOString(),
                originalData: data
            }
        });
        
        // Dispatch event
        DOM.trigger(document, 'notification:sse:show', { 
            id: notificationId, 
            data,
            type: 'sse' 
        });
        
        return notificationId;
    }
    
    // ===============================================
    // NOTIFICATION DISPLAY METHODS
    // ===============================================
    
    /**
     * Show notification (auto-chooses between toast and alert)
     */
    show(message, options = {}) {
        const config = {
            type: 'info',
            title: '',
            duration: this.defaultDuration,
            closable: true,
            actions: [],
            metadata: {},
            ...options
        };
        
        // Determine display type based on context
        const displayType = options.displayType || this.determineDisplayType();
        
        if (displayType === 'toast') {
            return this.showToast(message, config);
        } else {
            return this.showAlert(message, config);
        }
    }
    
    /**
     * Determine display type based on context
     */
    determineDisplayType() {
        // Use alert for inline content, toast for global notifications
        if (this.alertContainer && document.activeElement?.closest('[hx-target]')) {
            return 'alert';
        }
        return 'toast';
    }
    
    /**
     * Show Bootstrap toast notification
     */
    showToast(message, options = {}) {
        const id = `toast_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        
        const config = {
            type: 'info',
            title: '',
            duration: 5000,
            icon: 'info',
            ...options
        };
        
        // Create toast element
        const toastEl = document.createElement('div');
        toastEl.className = 'toast';
        toastEl.id = id;
        toastEl.setAttribute('role', 'alert');
        toastEl.setAttribute('aria-live', 'assertive');
        toastEl.setAttribute('aria-atomic', 'true');
        toastEl.setAttribute('data-bs-delay', config.duration);
        
        // Map notification type to Bootstrap background
        const bgMap = {
            'success': 'success',
            'error': 'danger',
            'warning': 'warning',
            'info': 'info',
            'sse': 'primary'
        };
        
        const bgClass = bgMap[config.type] || 'info';
        
        const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        toastEl.innerHTML = `
            <div class="toast-header bg-${bgClass} text-white">
                <i class="${config.icon} me-2"></i>
                <strong class="me-auto">${config.title || this.getTitleFromType(config.type)}</strong>
                <small class="text-white-50">${time}</small>
                <button type="button" class="btn-close btn-close-white ms-2" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${this.escapeHtml(message)}
            </div>
        `;
        
        // Add to container
        this.toastContainer.appendChild(toastEl);
        
        // Initialize Bootstrap toast
        if (typeof bootstrap !== 'undefined' && bootstrap.Toast) {
            const toast = new bootstrap.Toast(toastEl, {
                delay: config.duration,
                autohide: true
            });
            
            // Store instance
            this.toastInstances.set(id, toast);
            
            // Show toast
            toast.show();
            
            // Handle toast hidden event
            toastEl.addEventListener('hidden.bs.toast', () => {
                toastEl.remove();
                this.toastInstances.delete(id);
            });
        } else {
            // Fallback: auto-remove after duration
            setTimeout(() => {
                if (toastEl.parentNode) {
                    toastEl.remove();
                }
            }, config.duration);
        }
        
        return id;
    }
    
    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    /**
     * Show Bootstrap alert notification
     */
    showAlert(message, options = {}) {
        const id = `alert_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        
        const config = {
            type: 'info',
            title: '',
            duration: options.duration || null, // Alerts don't auto-dismiss by default
            icon: 'info',
            ...options
        };
        
        // Create alert element
        const alertEl = document.createElement('div');
        alertEl.className = `alert alert-${config.type} alert-dismissible fade show`;
        alertEl.id = id;
        alertEl.setAttribute('role', 'alert');
        
        alertEl.innerHTML = `
            ${config.icon ? `<i class="${config.icon} me-2"></i>` : ''}
            <strong>${config.title || this.getTitleFromType(config.type)}</strong>
            <span class="ms-2">${this.escapeHtml(message)}</span>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        // Add to appropriate container
        if (this.alertContainer) {
            this.alertContainer.appendChild(alertEl);
        } else {
            // Create temporary container
            const container = document.createElement('div');
            container.className = 'alert-container mb-3';
            container.appendChild(alertEl);
            
            // Insert after main content or at the top of the page
            const main = document.querySelector('main') || document.body;
            main.insertBefore(container, main.firstChild);
        }
        
        // Auto-remove if duration is set
        if (config.duration) {
            setTimeout(() => {
                if (alertEl.parentNode) {
                    // Use Bootstrap's dismiss method if available
                    if (typeof bootstrap !== 'undefined' && alertEl.classList.contains('show')) {
                        const closeBtn = alertEl.querySelector('.btn-close');
                        if (closeBtn) closeBtn.click();
                    } else {
                        alertEl.remove();
                    }
                }
            }, config.duration);
        }
        
        // Dispatch event
        DOM.trigger(document, 'notification:show', { 
            id, 
            message, 
            config,
            type: 'alert'
        });
        
        return id;
    }
    
    /**
     * Get title from notification type
     */
    getTitleFromType(type) {
        const titles = {
            'success': 'Success',
            'error': 'Error',
            'warning': 'Warning',
            'info': 'Information',
            'sse': 'Real-time Notification'
        };
        return titles[type] || 'Notification';
    }
    
    /**
     * Show success notification
     */
    success(message, options = {}) {
        return this.show(message, { ...options, type: 'success' });
    }
    
    /**
     * Show error notification
     */
    error(message, options = {}) {
        return this.show(message, { ...options, type: 'error' });
    }
    
    /**
     * Show warning notification
     */
    warning(message, options = {}) {
        return this.show(message, { ...options, type: 'warning' });
    }
    
    /**
     * Show info notification
     */
    info(message, options = {}) {
        return this.show(message, { ...options, type: 'info' });
    }
    
    /**
     * Pause all notification timers
     */
    pauseAllNotificationTimers() {
        // Bootstrap handles this automatically
    }
    
    /**
     * Resume all notification timers
     */
    resumeAllNotificationTimers() {
        // Bootstrap handles this automatically
    }
    
    /**
     * Get CSRF token
     */
    getCSRFToken() {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        return csrfToken ? csrfToken.value : '';
    }
    
    /**
     * Destroy notification system
     */
    destroy() {
        // Close SSE connection
        if (this.notificationConnectionId) {
            this.sseManager.closeConnection(this.notificationConnectionId);
        }
        
        // Clear all notifications
        this.clear();
        
        console.log('🔔 Notification system destroyed');
    }
}

// Global instance
window.NotificationSystem = new NotificationSystem();
export default NotificationSystem;
