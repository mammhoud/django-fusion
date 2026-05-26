/**
 * @file layouts/notifications/plugins/htmx-sse-notifications.js
 * Unified HTMX & SSE Integration for Notifications
 * Supports: HTMX responses, SSE, WebSocket (Django Channels), Real-time notifications
 */

import { debounce, Utils, DOM } from '../../utility/index.js';

/**
 * Unified SSE Handler with HTMX Integration
 */
export class HTMXSSENotifications {
    constructor(options = {}) {
        this.options = {
            autoProcess: true,
            parseHeaders: true,
            debug: false,
            enableSSE: true,
            enableWebSocket: false,
            enableChannels: false,
            channelPath: '/ws/notifications/',
            ssePath: '/notifications/',
            maxConnections: 5,
            maxReconnectAttempts: 5,
            reconnectDelay: 3000,
            ...options
        };

        // Connection management
        this.connections = new Map();
        this.reconnectAttempts = new Map();
        this.heartbeatIntervals = new Map();
        this.connectionTimeouts = new Map();

        // HTMX integration
        this.htmxTriggers = new Set(['showNotification', 'notification', 'notify']);
        this.htmxResponseQueue = [];
        this.htmxEventListeners = new Map();

        // Status tracking
        this.status = {
            totalConnections: 0,
            activeConnections: 0,
            failedConnections: 0,
            reconnections: 0,
            htmxNotifications: 0,
            sseMessages: 0,
            webSocketMessages: 0
        };

        // Event system
        this.events = new EventTarget();

        // Notification system reference
        this.notificationSystem = null;

        console.log('🔌 HTMX+SSE Notifications initialized');
    }

    /**
     * Initialize with notification system
     */
    install(notificationSystem, options = {}) {
        this.notificationSystem = notificationSystem;
        this.options = { ...this.options, ...options };

        // Initialize HTMX integration
        this.initializeHTMXIntegration();

        // Initialize SSE if enabled
        if (this.options.enableSSE) {
            this.initializeSSE();
        }

        // Setup global handler
        this.setupGlobalHandler();

        console.log('✅ HTMX+SSE Notifications installed');
        return this;
    }

    /**
     * Initialize HTMX integration
     */
    initializeHTMXIntegration() {
        if (typeof htmx === 'undefined') {
            console.warn('HTMX not loaded, skipping HTMX integration');
            return;
        }

        // Remove any existing listeners
        this.removeHTMXListeners();

        // Setup HTMX event listeners
        this.setupHTMXListeners();

        // Scan for existing triggers
        this.scanForHTMXTriggers();

        console.log('✅ HTMX integration initialized');
    }

    /**
     * Setup HTMX event listeners
     */
    setupHTMXListeners() {
        // Handle HTMX responses
        const handleAfterSwap = (event) => {
            this.processHTMXResponse(event.detail.xhr, event.detail.target);
        };

        // Handle HTMX triggers
        const handleBeforeOnLoad = (event) => {
            if (this.options.parseHeaders) {
                this.processHTMXHeaders(event.detail.xhr);
            }
        };

        // Handle HTMX errors
        const handleResponseError = (event) => {
            this.handleHTMXError(event.detail);
        };

        // Handle HTMX triggers
        const handleTrigger = (event) => {
            this.processHTMXTrigger(event.detail);
        };

        // Store listeners for cleanup
        this.htmxEventListeners.set('htmx:afterSwap', handleAfterSwap);
        this.htmxEventListeners.set('htmx:beforeOnLoad', handleBeforeOnLoad);
        this.htmxEventListeners.set('htmx:responseError', handleResponseError);
        this.htmxEventListeners.set('htmx:trigger', handleTrigger);

        // Add listeners
        this.htmxEventListeners.forEach((handler, event) => {
            document.addEventListener(event, handler);
        });
    }

    /**
     * Remove HTMX event listeners
     */
    removeHTMXListeners() {
        this.htmxEventListeners.forEach((handler, event) => {
            document.removeEventListener(event, handler);
        });
        this.htmxEventListeners.clear();
    }

    /**
     * Setup global handler for direct calls
     */
    setupGlobalHandler() {
        // Global handler for direct calls
        window.htmxNotifications = {
            // Show notification
            show: (message, options) => this.showNotification(message, options),
            success: (message, options) => this.showNotification(message, { ...options, type: 'success' }),
            error: (message, options) => this.showNotification(message, { ...options, type: 'error' }),
            warning: (message, options) => this.showNotification(message, { ...options, type: 'warning' }),
            info: (message, options) => this.showNotification(message, { ...options, type: 'info' }),

            // Connection management
            createConnection: (url, options) => this.createConnection(url, options),
            closeConnection: (id) => this.closeConnection(id),
            closeAll: () => this.closeAllConnections(),

            // Status
            getStatus: () => this.getStatus(),
            getConnections: () => this.getAllConnections(),

            // HTMX triggers
            registerTrigger: (trigger) => this.registerHTMXTrigger(trigger),
            unregisterTrigger: (trigger) => this.unregisterHTMXTrigger(trigger),
            getTriggers: () => this.getHTMXTriggers()
        };
    }

    /**
     * Initialize SSE connections
     */
    initializeSSE() {
        // Auto-connect to default SSE endpoint
        if (this.options.ssePath) {
            this.createConnection(this.options.ssePath, {
                name: 'default',
                autoReconnect: true,
                onMessage: (data) => this.handleSSEMessage(data)
            }).catch(error => {
                console.warn('Failed to create default SSE connection:', error);
            });
        }

        // Enable Django Channels if configured
        if (this.options.enableChannels) {
            this.enableChannels(this.options.channelPath);
        }
    }

    // ==================== HTMX PROCESSING ====================

    /**
     * Process HTMX response
     */
    processHTMXResponse(xhr, target) {
        if (!xhr) return;

        // Check for notification headers
        const headers = ['HX-Trigger', 'HX-Trigger-After-Settle', 'HX-Trigger-After-Swap'];

        headers.forEach(header => {
            const value = xhr.getResponseHeader(header);
            if (value) {
                this.parseHTMXTriggerHeader(value);
            }
        });

        // Check response body for notifications
        try {
            const response = JSON.parse(xhr.responseText);
            if (response.notifications) {
                this.processResponseNotifications(response.notifications);
            }
        } catch (error) {
            // Not JSON, try HTML parsing
            if (xhr.responseText) {
                this.extractNotificationFromHTML(xhr.responseText, target);
            }
        }
    }

    /**
     * Process HTMX headers
     */
    processHTMXHeaders(xhr) {
        // Early header processing for debugging
        const triggerHeader = xhr.getResponseHeader('HX-Trigger');
        if (triggerHeader && this.options.debug) {
            console.log('HTMX trigger header:', triggerHeader);
        }
    }

    /**
     * Parse HTMX trigger header
     */
    parseHTMXTriggerHeader(headerValue) {
        try {
            const triggers = JSON.parse(headerValue);

            Object.entries(triggers).forEach(([key, value]) => {
                if (key === 'showNotification' || key === 'notification') {
                    this.showNotification(value);
                }

                // Auto-process common trigger patterns
                if (key.startsWith('notify_')) {
                    const type = key.replace('notify_', '');
                    this.showNotification({
                        message: value.message || value,
                        type: ['success', 'error', 'warning', 'info'].includes(type) ? type : 'info'
                    });
                }
            });
        } catch (error) {
            console.error('Failed to parse HTMX trigger:', error);

            // Try simple trigger names
            if (typeof headerValue === 'string') {
                const simpleTriggers = headerValue.split(',').map(t => t.trim());
                simpleTriggers.forEach(triggerName => {
                    if (this.htmxTriggers.has(triggerName)) {
                        this.showNotification({ message: triggerName, type: 'info' });
                    }
                });
            }
        }
    }

    /**
     * Process HTMX trigger
     */
    processHTMXTrigger(triggerDetail) {
        if (!triggerDetail || !triggerDetail.name) return;

        if (this.htmxTriggers.has(triggerDetail.name)) {
            this.handleHTMXNotificationTrigger(
                triggerDetail.name,
                triggerDetail.detail || {},
                'immediate'
            );
        }
    }

    /**
     * Handle HTMX notification trigger
     */
    handleHTMXNotificationTrigger(triggerName, triggerData, timing) {
        if (this.options.debug) {
            console.log(`📨 HTMX notification trigger: ${triggerName}`, triggerData);
        }

        // Update status
        this.status.htmxNotifications++;
        this.updateStatus();

        // Normalize notification data
        const notificationData = this.normalizeNotificationData(triggerData);

        // Dispatch events
        this.events.dispatchEvent(new CustomEvent('htmx:notification', {
            detail: {
                trigger: triggerName,
                data: notificationData,
                timing: timing,
                source: 'htmx'
            }
        }));

        // Show notification
        this.showNotification(notificationData);
    }

    /**
     * Extract notification from HTML response
     */
    extractNotificationFromHTML(html, target) {
        try {
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = html;

            // Look for notification elements
            const notificationElements = tempDiv.querySelectorAll(
                '[data-notification], [data-notify], .notification, .alert, .toast, [class*="notification"], [class*="alert"]'
            );

            notificationElements.forEach(element => {
                const notificationData = this.extractNotificationFromElement(element);
                if (notificationData) {
                    this.showNotification(notificationData);
                }
            });

            // Look for data attributes
            const notificationAttrs = tempDiv.querySelectorAll('[data-notification-message]');
            notificationAttrs.forEach(element => {
                const message = element.getAttribute('data-notification-message');
                const type = element.getAttribute('data-notification-type') || 'info';
                const title = element.getAttribute('data-notification-title') || '';
                const duration = parseInt(element.getAttribute('data-notification-duration')) || 5000;

                this.showNotification({ message, type, title, duration });
            });

        } catch (error) {
            console.error('Error extracting notification from HTML:', error);
        }
    }

    /**
     * Extract notification data from element
     */
    extractNotificationFromElement(element) {
        const data = {};

        // Get message
        data.message = element.textContent?.trim() ||
            element.getAttribute('data-message') ||
            element.getAttribute('title') ||
            element.getAttribute('aria-label') ||
            '';

        if (!data.message) return null;

        // Get type/level
        data.type = element.getAttribute('data-type') ||
            element.getAttribute('data-level') ||
            this.extractTypeFromClasses(element.className) ||
            'info';

        // Get title
        data.title = element.getAttribute('data-title') ||
            element.querySelector('strong, b, .title, .header')?.textContent?.trim() || '';

        // Get duration
        const durationAttr = element.getAttribute('data-duration');
        data.duration = durationAttr ? parseInt(durationAttr) : 5000;

        // Get icon
        data.icon = element.getAttribute('data-icon') || '';

        // Get actions
        const actionElements = element.querySelectorAll('[data-action]');
        if (actionElements.length > 0) {
            data.actions = Array.from(actionElements).map(el => ({
                label: el.textContent.trim(),
                action: el.getAttribute('data-action'),
                url: el.getAttribute('href')
            }));
        }

        return data;
    }

    /**
     * Extract type from CSS classes
     */
    extractTypeFromClasses(className) {
        if (!className) return 'info';

        const classStr = className.toLowerCase();
        if (classStr.includes('success')) return 'success';
        if (classStr.includes('error') || classStr.includes('danger')) return 'error';
        if (classStr.includes('warning')) return 'warning';
        if (classStr.includes('info')) return 'info';

        return 'info';
    }

    /**
     * Process response notifications array
     */
    processResponseNotifications(notifications) {
        if (Array.isArray(notifications)) {
            notifications.forEach(notification => {
                this.showNotification(notification);
            });
        } else if (notifications && typeof notifications === 'object') {
            this.showNotification(notifications);
        }
    }

    /**
     * Handle HTMX error
     */
    handleHTMXError(detail) {
        if (detail.xhr?.status >= 400) {
            let message = 'An error occurred';

            try {
                const response = JSON.parse(detail.xhr.responseText);
                message = response.message || response.error || detail.xhr.responseText.substring(0, 100);
            } catch {
                message = detail.xhr.responseText || `Error ${detail.xhr.status}`;
            }

            this.showNotification({
                message,
                type: 'error',
                title: `Error ${detail.xhr.status}`,
                duration: 10000
            });
        }
    }

    // ==================== SSE/WEB SOCKET CONNECTIONS ====================

    /**
     * Create SSE/WebSocket connection
     */
    async createConnection(url, options = {}) {
        // Check connection limit
        if (this.connections.size >= this.options.maxConnections) {
            throw new Error(`Maximum connection limit reached (${this.options.maxConnections})`);
        }

        const connectionId = Utils.generateId('conn');
        const config = this.normalizeConfig(url, options);

        try {
            // Determine connection type
            const useWebSocket = this.shouldUseWebSocket(config);

            if (useWebSocket) {
                return await this.createWebSocketConnection(connectionId, config);
            } else {
                return await this.createSSEConnection(connectionId, config);
            }
        } catch (error) {
            console.error(`Failed to create connection ${connectionId}:`, error);
            this.events.dispatchEvent(new CustomEvent('connection:error', {
                detail: { connectionId, error }
            }));
            throw error;
        }
    }

    /**
     * Create SSE connection
     */
    async createSSEConnection(connectionId, config) {
        return new Promise((resolve, reject) => {
            try {
                const eventSource = new EventSource(config.url, {
                    withCredentials: true
                });

                const connection = {
                    id: connectionId,
                    type: 'sse',
                    eventSource,
                    config,
                    createdAt: Date.now(),
                    lastActivity: Date.now(),
                    status: 'connecting'
                };

                // Setup event handlers
                let connectionEstablished = false;

                eventSource.onopen = () => {
                    connection.status = 'open';
                    connectionEstablished = true;

                    this.events.dispatchEvent(new CustomEvent('connection:open', {
                        detail: { connectionId, type: 'sse' }
                    }));

                    resolve(connectionId);
                };

                eventSource.onmessage = (event) => {
                    connection.lastActivity = Date.now();

                    if (!connectionEstablished) {
                        connection.status = 'open';
                        connectionEstablished = true;
                        resolve(connectionId);
                    }

                    try {
                        const data = JSON.parse(event.data);
                        this.handleIncomingMessage(connectionId, data);
                    } catch (error) {
                        console.error('Failed to parse SSE message:', error);
                    }
                };

                eventSource.onerror = (error) => {
                    if (!connectionEstablished) {
                        connection.status = 'error';
                        reject(new Error('SSE connection failed'));
                    } else {
                        this.handleConnectionError(connectionId, error);
                    }
                };

                // Store connection
                this.connections.set(connectionId, connection);
                this.reconnectAttempts.set(connectionId, 0);

                // Start monitoring
                this.startConnectionMonitoring(connectionId);

                this.events.dispatchEvent(new CustomEvent('connection:created', {
                    detail: { connectionId, type: 'sse', config }
                }));

                // Connection timeout
                setTimeout(() => {
                    if (connection.status === 'connecting') {
                        this.handleConnectionError(connectionId, new Error('Connection timeout'));
                        reject(new Error('Connection timeout'));
                    }
                }, 10000);

            } catch (error) {
                reject(new Error(`SSE connection failed: ${error.message}`));
            }
        });
    }

    /**
     * Create WebSocket connection
     */
    async createWebSocketConnection(connectionId, config) {
        return new Promise((resolve, reject) => {
            try {
                const wsUrl = this.getWebSocketURL(config.url);
                const websocket = new WebSocket(wsUrl);

                const connection = {
                    id: connectionId,
                    type: 'websocket',
                    websocket,
                    config,
                    createdAt: Date.now(),
                    lastActivity: Date.now(),
                    status: 'connecting'
                };

                // Connection timeout
                const connectionTimeout = setTimeout(() => {
                    if (connection.status === 'connecting') {
                        websocket.close();
                        reject(new Error('WebSocket connection timeout'));
                    }
                }, 10000);

                websocket.onopen = () => {
                    clearTimeout(connectionTimeout);
                    connection.status = 'open';

                    // Authenticate if needed
                    if (config.authToken) {
                        this.authenticateWebSocket(connectionId, config);
                    }

                    this.events.dispatchEvent(new CustomEvent('connection:open', {
                        detail: { connectionId, type: 'websocket' }
                    }));

                    resolve(connectionId);
                };

                websocket.onmessage = (event) => {
                    connection.lastActivity = Date.now();

                    try {
                        const data = JSON.parse(event.data);
                        this.handleIncomingMessage(connectionId, data);
                    } catch (error) {
                        console.error('Failed to parse WebSocket message:', error);
                    }
                };

                websocket.onerror = (error) => {
                    clearTimeout(connectionTimeout);
                    this.handleConnectionError(connectionId, error);
                    reject(error);
                };

                websocket.onclose = (event) => {
                    clearTimeout(connectionTimeout);
                    connection.status = 'closed';

                    this.events.dispatchEvent(new CustomEvent('connection:close', {
                        detail: { connectionId, type: 'websocket', code: event.code, reason: event.reason }
                    }));

                    // Attempt reconnection
                    if (config.autoReconnect && event.code !== 1000) {
                        this.handleReconnection(connectionId, config.url, config);
                    }
                };

                // Store connection
                this.connections.set(connectionId, connection);
                this.reconnectAttempts.set(connectionId, 0);

                // Start monitoring
                this.startConnectionMonitoring(connectionId);

            } catch (error) {
                reject(new Error(`WebSocket connection failed: ${error.message}`));
            }
        });
    }

    /**
     * Handle incoming message
     */
    handleIncomingMessage(connectionId, data) {
        const connection = this.connections.get(connectionId);
        if (!connection) return;

        // Update message count
        if (connection.type === 'sse') {
            this.status.sseMessages++;
        } else if (connection.type === 'websocket') {
            this.status.webSocketMessages++;
        }
        this.updateStatus();

        // Dispatch message event
        this.events.dispatchEvent(new CustomEvent('message', {
            detail: { connectionId, data, type: connection.type }
        }));

        // Call user-defined callback
        if (connection.config.onMessage) {
            try {
                connection.config.onMessage(data, connectionId);
            } catch (error) {
                console.error('Error in user message handler:', error);
            }
        }

        // Process notification messages
        if (data.type === 'notification' || data.event === 'notification') {
            this.processNotificationMessage(data);
        }
    }

    /**
     * Process notification message
     */
    processNotificationMessage(data) {
        const notificationData = this.normalizeNotificationData(data.data || data);

        this.events.dispatchEvent(new CustomEvent('sse:notification', {
            detail: {
                data: notificationData,
                source: 'sse',
                original: data
            }
        }));

        this.showNotification(notificationData);
    }

    /**
     * Handle connection error
     */
    handleConnectionError(connectionId, error) {
        const connection = this.connections.get(connectionId);
        if (!connection) return;

        connection.status = 'error';
        connection.lastError = error;

        // Call user error callback
        if (connection.config.onError) {
            try {
                connection.config.onError(error, connectionId);
            } catch (e) {
                console.error('Error in user error handler:', e);
            }
        }

        // Update status
        this.status.failedConnections++;
        this.updateStatus();

        // Attempt reconnection
        if (connection.config.autoReconnect) {
            this.handleReconnection(connectionId, connection.config.url, connection.config);
        }
    }

    /**
     * Handle reconnection
     */
    async handleReconnection(connectionId, url, config) {
        const reconnectCount = this.reconnectAttempts.get(connectionId) || 0;

        if (reconnectCount >= this.options.maxReconnectAttempts) {
            console.log(`Max reconnection attempts reached for ${connectionId}`);
            this.closeConnection(connectionId);
            return;
        }

        // Update reconnect count
        const newCount = reconnectCount + 1;
        this.reconnectAttempts.set(connectionId, newCount);

        // Calculate delay with exponential backoff
        const delay = this.options.reconnectDelay * Math.pow(1.5, newCount - 1);

        setTimeout(async () => {
            try {
                // Close old connection
                this.cleanupConnection(connectionId);

                // Create new connection
                await this.createConnection(url, config);

                this.status.reconnections++;
                this.updateStatus();

            } catch (error) {
                console.error(`Reconnection failed for ${connectionId}:`, error);
            }
        }, delay);
    }

    /**
     * Close connection
     */
    closeConnection(connectionId, reason = 'User initiated') {
        const connection = this.connections.get(connectionId);

        if (connection) {
            this.cleanupConnection(connectionId);

            this.connections.delete(connectionId);
            this.reconnectAttempts.delete(connectionId);

            this.updateStatus();

            this.events.dispatchEvent(new CustomEvent('connection:closed', {
                detail: { connectionId, reason, type: connection.type }
            }));

            return true;
        }

        return false;
    }

    /**
     * Close all connections
     */
    closeAllConnections(reason = 'Application shutdown') {
        this.connections.forEach((connection, connectionId) => {
            this.closeConnection(connectionId, reason);
        });
    }

    /**
     * Cleanup connection resources
     */
    cleanupConnection(connectionId) {
        const connection = this.connections.get(connectionId);
        if (!connection) return;

        // Stop monitoring
        this.stopConnectionMonitoring(connectionId);

        // Close connection
        if (connection.type === 'sse' && connection.eventSource) {
            connection.eventSource.close();
        } else if (connection.type === 'websocket' && connection.websocket) {
            if (connection.websocket.readyState === WebSocket.OPEN) {
                connection.websocket.close(1000, 'Normal closure');
            }
        }
    }

    /**
     * Start connection monitoring
     */
    startConnectionMonitoring(connectionId) {
        const connection = this.connections.get(connectionId);
        if (!connection) return;

        // Clear existing interval
        this.stopConnectionMonitoring(connectionId);

        // Heartbeat for WebSocket
        if (connection.type === 'websocket') {
            const interval = setInterval(() => {
                this.sendHeartbeat(connectionId);
            }, 30000);

            this.heartbeatIntervals.set(connectionId, interval);
        }

        // Connection timeout (1 hour)
        const timeout = setTimeout(() => {
            this.closeConnection(connectionId, 'Maximum connection time reached');
        }, 3600000);

        this.connectionTimeouts.set(connectionId, timeout);
    }

    /**
     * Stop connection monitoring
     */
    stopConnectionMonitoring(connectionId) {
        const interval = this.heartbeatIntervals.get(connectionId);
        if (interval) {
            clearInterval(interval);
            this.heartbeatIntervals.delete(connectionId);
        }

        const timeout = this.connectionTimeouts.get(connectionId);
        if (timeout) {
            clearTimeout(timeout);
            this.connectionTimeouts.delete(connectionId);
        }
    }

    /**
     * Send heartbeat
     */
    sendHeartbeat(connectionId) {
        const connection = this.connections.get(connectionId);
        if (!connection || connection.type !== 'websocket') return;

        if (connection.websocket.readyState === WebSocket.OPEN) {
            connection.websocket.send(JSON.stringify({ type: 'ping', timestamp: Date.now() }));
        }
    }

    // ==================== UTILITY METHODS ====================

    /**
     * Show notification
     */
    showNotification(data, options = {}) {
        if (!data || (!data.message && !data.title)) return;

        const notificationData = this.normalizeNotificationData(data);

        // Use notification system if available
        if (this.notificationSystem && this.notificationSystem.show) {
            this.notificationSystem.show(notificationData.message, {
                type: notificationData.type || 'info',
                title: notificationData.title,
                duration: notificationData.duration || 5000,
                icon: notificationData.icon,
                actions: notificationData.actions,
                ...options
            });
        } else {
            // Fallback to console
            console.log(`[Notification: ${notificationData.type}] ${notificationData.title}: ${notificationData.message}`);
        }

        // Dispatch event
        this.events.dispatchEvent(new CustomEvent('notification:shown', {
            detail: notificationData
        }));

        return notificationData;
    }

    /**
     * Normalize notification data
     */
    normalizeNotificationData(data) {
        if (typeof data === 'string') {
            return {
                message: data,
                type: 'info',
                title: '',
                duration: 5000
            };
        }

        if (data && typeof data === 'object') {
            return {
                message: data.message || data.text || data.content || 'Notification',
                type: data.type || data.level || 'info',
                title: data.title || data.heading || '',
                duration: data.duration || data.timeout || 5000,
                icon: data.icon || '',
                actions: data.actions || [],
                metadata: data.metadata || {},
                ...data
            };
        }

        return {
            message: 'Notification',
            type: 'info',
            duration: 5000
        };
    }

    /**
     * Scan for HTMX triggers
     */
    scanForHTMXTriggers() {
        // Look for elements with hx-trigger attributes
        const hxTriggerElements = document.querySelectorAll('[hx-trigger]');

        hxTriggerElements.forEach(element => {
            const triggers = element.getAttribute('hx-trigger');
            if (triggers) {
                this.parseHTMXTriggerAttribute(triggers, element);
            }
        });
    }

    /**
     * Parse HTMX trigger attribute
     */
    parseHTMXTriggerAttribute(triggers, element) {
        const triggerList = triggers.split(',').map(t => t.trim());

        triggerList.forEach(trigger => {
            if (this.htmxTriggers.has(trigger)) {
                element.addEventListener('click', () => {
                    const data = {
                        message: element.getAttribute('data-notification-message') ||
                            element.textContent ||
                            'Notification triggered',
                        type: element.getAttribute('data-notification-type') || 'info'
                    };
                    this.handleHTMXNotificationTrigger(trigger, data, 'immediate');
                });
            }
        });
    }

    /**
     * Register HTMX trigger
     */
    registerHTMXTrigger(triggerName) {
        this.htmxTriggers.add(triggerName);
        return this;
    }

    /**
     * Unregister HTMX trigger
     */
    unregisterHTMXTrigger(triggerName) {
        this.htmxTriggers.delete(triggerName);
        return this;
    }

    /**
     * Get HTMX triggers
     */
    getHTMXTriggers() {
        return Array.from(this.htmxTriggers);
    }

    /**
     * Normalize connection config
     */
    normalizeConfig(url, options) {
        return {
            url,
            name: options.name || 'unnamed',
            onOpen: options.onOpen,
            onMessage: options.onMessage,
            onError: options.onError,
            onClose: options.onClose,
            autoReconnect: options.autoReconnect !== false,
            authToken: options.authToken,
            ...options
        };
    }

    /**
     * Determine if WebSocket should be used
     */
    shouldUseWebSocket(config) {
        const supportsWebSocket = 'WebSocket' in window || 'MozWebSocket' in window;
        const isWebSocketUrl = config.url.startsWith('ws://') || config.url.startsWith('wss://');

        return supportsWebSocket && (this.options.enableWebSocket || isWebSocketUrl);
    }

    /**
     * Convert URL to WebSocket URL
     */
    getWebSocketURL(url) {
        if (url.startsWith('ws://') || url.startsWith('wss://')) {
            return url;
        }

        if (url.startsWith('http')) {
            return url.replace(/^http/, 'ws');
        }

        // Relative URL
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        return `${protocol}//${window.location.host}${url.startsWith('/') ? url : '/' + url}`;
    }

    /**
     * Authenticate WebSocket
     */
    authenticateWebSocket(connectionId, config) {
        const connection = this.connections.get(connectionId);
        if (!connection || connection.type !== 'websocket') return;

        const authMessage = {
            type: 'authenticate',
            token: config.authToken || Utils.getCSRFToken()
        };

        connection.websocket.send(JSON.stringify(authMessage));
    }

    /**
     * Enable Django Channels
     */
    enableChannels(channelPath = '/ws/notifications/') {
        this.options.enableChannels = true;
        this.options.channelPath = channelPath;
        this.options.enableWebSocket = true;
        return this;
    }

    /**
     * Disable Django Channels
     */
    disableChannels() {
        this.options.enableChannels = false;
        this.options.enableWebSocket = false;
        return this;
    }

    /**
     * Get connection status
     */
    getConnectionStatus(connectionId) {
        const connection = this.connections.get(connectionId);
        if (!connection) return 'closed';

        if (connection.type === 'sse' && connection.eventSource) {
            const state = connection.eventSource.readyState;
            return state === EventSource.OPEN ? 'open' :
                state === EventSource.CONNECTING ? 'connecting' : 'closed';
        } else if (connection.type === 'websocket' && connection.websocket) {
            const state = connection.websocket.readyState;
            return state === WebSocket.OPEN ? 'open' :
                state === WebSocket.CONNECTING ? 'connecting' : 'closed';
        }

        return connection.status || 'unknown';
    }

    /**
     * Get all connections
     */
    getAllConnections() {
        const connections = {};

        this.connections.forEach((connection, connectionId) => {
            connections[connectionId] = {
                id: connectionId,
                type: connection.type,
                url: connection.config.url,
                status: this.getConnectionStatus(connectionId),
                name: connection.config.name,
                createdAt: connection.createdAt,
                lastActivity: connection.lastActivity
            };
        });

        return connections;
    }

    /**
     * Get status
     */
    getStatus() {
        return {
            ...this.status,
            connections: this.getAllConnections(),
            htmxTriggers: this.getHTMXTriggers()
        };
    }

    /**
     * Update status
     */
    updateStatus() {
        this.status.totalConnections = this.connections.size;
        this.status.activeConnections = Array.from(this.connections.values())
            .filter(conn => this.getConnectionStatus(conn.id) === 'open').length;

        this.events.dispatchEvent(new CustomEvent('status:update', {
            detail: { ...this.status }
        }));
    }

    /**
     * Add event listener
     */
    on(event, callback) {
        this.events.addEventListener(event, callback);
        return this;
    }

    /**
     * Remove event listener
     */
    off(event, callback) {
        this.events.removeEventListener(event, callback);
        return this;
    }

    /**
     * Destroy
     */
    destroy() {
        // Close all connections
        this.closeAllConnections('Manager destroyed');

        // Clear all intervals and timeouts
        this.heartbeatIntervals.forEach(interval => clearInterval(interval));
        this.connectionTimeouts.forEach(timeout => clearTimeout(timeout));

        // Clear data
        this.connections.clear();
        this.reconnectAttempts.clear();
        this.heartbeatIntervals.clear();
        this.connectionTimeouts.clear();
        this.htmxResponseQueue.length = 0;

        // Remove HTMX listeners
        this.removeHTMXListeners();

        // Remove global handler
        delete window.htmxNotifications;

        console.log('🔌 HTMX+SSE Notifications destroyed');
    }
}

// Global instance
window.HTMXSSENotifications = HTMXSSENotifications;

// Default export
export default HTMXSSENotifications;

/**
 * Plugin wrapper for compatibility
 */
export const htmxNotificationsPlugin = {
    name: 'htmx-sse-notifications',

    install(notificationSystem, options = {}) {
        const instance = new HTMXSSENotifications(options);
        return instance.install(notificationSystem, options);
    }
};