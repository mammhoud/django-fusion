/**
 * SSE Connection Manager with Django Channels & HTMX Integration
 */

import { debounce, Utils, DOM } from '../utility/index.js';

export class SSEHandler {
  constructor() {
    // Connection pool
    this.connections = new Map();
    this.reconnectAttempts = new Map();
    this.maxConnections = 5;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 3000;
    this.initialReconnectDelay = 5000;
    
    // Connection monitoring
    this.heartbeatIntervals = new Map();
    this.connectionTimeouts = new Map();
    this.maxConnectionTime = 3600000; // 1 hour
    
    // Django Channels support
    this.useChannels = false;
    this.channelPath = '/ws/notifications/';
    this.ssePath = '/notifications/';
    
    // HTMX Integration
    this.htmxTriggers = new Set(['showNotification', 'notification']);
    this.htmxResponseQueue = [];
    
    // Status tracking
    this.status = {
      totalConnections: 0,
      activeConnections: 0,
      failedConnections: 0,
      reconnections: 0,
      htmxNotifications: 0
    };
    
    // Initialize event system
    this.events = new EventTarget();
    
    console.log('🔌 SSE Manager initialized');
  }
  
  /**
   * Initialize HTMX integration
   */
  initializeHTMXIntegration() {
    if (typeof htmx === 'undefined') {
      console.warn('HTMX not loaded, skipping HTMX integration');
      return;
    }
    
    // Listen for HTMX responses
    document.addEventListener('htmx:beforeSwap', (event) => {
      this.processHTMXResponse(event.detail.xhr, event.detail.target);
    });
    
    // Listen for HTMX triggers
    document.addEventListener('htmx:trigger', (event) => {
      this.processHTMXTrigger(event.detail);
    });
    
    // Scan for existing triggers
    this.scanForHTMXTriggers();
    
    console.log('✅ HTMX integration initialized');
  }
  
  /**
   * Process HTMX response
   */
  processHTMXResponse(xhr, target) {
    try {
      // Check for HX-Trigger headers
      const triggerHeader = xhr.getResponseHeader('HX-Trigger');
      if (triggerHeader) {
        this.parseHTMXTriggerHeader(triggerHeader);
      }
      
      // Check for other trigger headers
      const afterSettleHeader = xhr.getResponseHeader('HX-Trigger-After-Settle');
      if (afterSettleHeader) {
        this.parseHTMXTriggerHeader(afterSettleHeader, 'after-settle');
      }
      
      const afterSwapHeader = xhr.getResponseHeader('HX-Trigger-After-Swap');
      if (afterSwapHeader) {
        this.parseHTMXTriggerHeader(afterSwapHeader, 'after-swap');
      }
      
      // Check response body
      const responseText = xhr.responseText;
      if (responseText && this.containsNotificationData(responseText)) {
        this.extractNotificationFromResponse(responseText, target);
      }
      
    } catch (error) {
      console.error('Error processing HTMX response:', error);
    }
  }
  
  /**
   * Parse HTMX trigger header
   */
  parseHTMXTriggerHeader(header, timing = 'immediate') {
    try {
      const triggers = JSON.parse(header);
      
      Object.entries(triggers).forEach(([triggerName, triggerData]) => {
        if (this.htmxTriggers.has(triggerName)) {
          this.handleHTMXNotificationTrigger(triggerName, triggerData, timing);
        }
      });
      
    } catch (error) {
      console.error('Error parsing HTMX trigger header:', error);
      
      // Try simple trigger names
      if (typeof header === 'string') {
        const simpleTriggers = header.split(',').map(t => t.trim());
        simpleTriggers.forEach(triggerName => {
          if (this.htmxTriggers.has(triggerName)) {
            this.handleHTMXNotificationTrigger(triggerName, {}, timing);
          }
        });
      }
    }
  }
  
  /**
   * Handle HTMX notification trigger
   */
  handleHTMXNotificationTrigger(triggerName, triggerData, timing) {
    console.log(`📨 HTMX notification trigger: ${triggerName}`, triggerData);
    
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
        timing: timing
      }
    }));
    
    this.events.dispatchEvent(new CustomEvent('notification', {
      detail: {
        connectionId: 'htmx',
        data: notificationData,
        source: 'htmx'
      }
    }));
  }
  
  /**
   * Normalize notification data
   */
  normalizeNotificationData(data) {
    if (typeof data === 'string') {
      return {
        message: data,
        type: 'info',
        title: 'Notification',
        duration: 5000
      };
    }
    
    if (data && typeof data === 'object') {
      return {
        message: data.message || data.text || 'Notification',
        type: data.type || data.level || 'info',
        title: data.title || '',
        duration: data.duration || 5000,
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
   * Check if response contains notification data
   */
  containsNotificationData(responseText) {
    if (!responseText) return false;
    
    const lowerText = responseText.toLowerCase();
    return (
      lowerText.includes('notification') ||
      lowerText.includes('notify') ||
      lowerText.includes('alert') ||
      lowerText.includes('toast') ||
      lowerText.includes('message')
    );
  }
  
  /**
   * Extract notification from HTML response
   */
  extractNotificationFromResponse(responseText, target) {
    try {
      const tempDiv = document.createElement('div');
      tempDiv.innerHTML = responseText;
      
      // Look for notification elements
      const notificationElements = tempDiv.querySelectorAll(
        '[data-notification], [data-notify], .notification, .alert, .toast'
      );
      
      notificationElements.forEach(element => {
        const notificationData = this.extractNotificationFromElement(element);
        if (notificationData) {
          this.handleHTMXNotificationTrigger(
            'showNotification',
            notificationData,
            'after-swap'
          );
        }
      });
      
      // Look for data attributes
      const notificationAttrs = tempDiv.querySelectorAll('[data-notification-message]');
      notificationAttrs.forEach(element => {
        const message = element.getAttribute('data-notification-message');
        const type = element.getAttribute('data-notification-type') || 'info';
        const title = element.getAttribute('data-notification-title') || '';
        const duration = parseInt(element.getAttribute('data-notification-duration')) || 5000;
        
        this.handleHTMXNotificationTrigger('showNotification', {
          message,
          type,
          title,
          duration
        }, 'after-swap');
      });
      
    } catch (error) {
      console.error('Error extracting notification from response:', error);
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
                  '';
    
    if (!data.message) return null;
    
    // Get type/level
    data.type = element.getAttribute('data-type') ||
               element.getAttribute('data-level') ||
               element.getAttribute('class')?.match(/alert-(success|danger|warning|info)/)?.[1] ||
               'info';
    
    // Get title
    data.title = element.getAttribute('data-title') || '';
    
    // Get duration
    const durationAttr = element.getAttribute('data-duration');
    data.duration = durationAttr ? parseInt(durationAttr) : 5000;
    
    // Get icon
    data.icon = element.getAttribute('data-icon') || '';
    
    return data;
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
    
    // Look for data-hx-trigger
    const dataHxTriggerElements = document.querySelectorAll('[data-hx-trigger]');
    dataHxTriggerElements.forEach(element => {
      const triggers = element.getAttribute('data-hx-trigger');
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
        const eventName = trigger.replace(/^show/, '').toLowerCase();
        element.addEventListener(eventName, (e) => {
          this.handleElementTrigger(trigger, element, e);
        });
      }
    });
  }
  
  /**
   * Handle element trigger
   */
  handleElementTrigger(triggerName, element, event) {
    const notificationData = {
      message: element.getAttribute('data-notification-message') || 
              element.textContent ||
              'Notification triggered',
      type: element.getAttribute('data-notification-type') || 'info',
      title: element.getAttribute('data-notification-title') || '',
      duration: parseInt(element.getAttribute('data-notification-duration')) || 5000
    };
    
    this.handleHTMXNotificationTrigger(triggerName, notificationData, 'immediate');
  }
  
  /**
   * Register HTMX trigger
   */
  registerHTMXTrigger(triggerName) {
    this.htmxTriggers.add(triggerName);
    console.log(`✅ Registered HTMX trigger: ${triggerName}`);
  }
  
  /**
   * Unregister HTMX trigger
   */
  unregisterHTMXTrigger(triggerName) {
    this.htmxTriggers.delete(triggerName);
    console.log(`🗑️ Unregistered HTMX trigger: ${triggerName}`);
  }
  
  /**
   * Get HTMX triggers
   */
  getHTMXTriggers() {
    return Array.from(this.htmxTriggers);
  }
  
  /**
   * Create SSE connection
   */
  async createConnection(url, options = {}) {
    // Check connection limit
    if (this.connections.size >= this.maxConnections) {
      console.warn(`Maximum connection limit reached (${this.maxConnections})`);
      
      // Try to close oldest inactive connection
      const oldestConnection = this.findOldestInactiveConnection();
      if (oldestConnection) {
        this.closeConnection(oldestConnection.id, 'Making room for new connection');
      } else {
        throw new Error(`Maximum connection limit reached (${this.maxConnections})`);
      }
    }
    
    const connectionId = Utils.generateId('sse');
    const config = this.normalizeConfig(url, options);
    
    try {
      // Check if we should use WebSocket
      const useWebSocket = this.shouldUseWebSocket(config);
      
      if (useWebSocket && this.useChannels) {
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
   * Find oldest inactive connection
   */
  findOldestInactiveConnection() {
    let oldestConnection = null;
    let oldestTime = Date.now();
    
    this.connections.forEach((connection, connectionId) => {
      const status = this.getConnectionStatus(connectionId);
      if (status !== 'open' && connection.createdAt < oldestTime) {
        oldestConnection = connection;
        oldestTime = connection.createdAt;
      }
    });
    
    return oldestConnection;
  }
  
  /**
   * Create SSE connection
   */
  async createSSEConnection(connectionId, config) {
    return new Promise((resolve, reject) => {
      try {
        // Add CSRF token to headers
        const headers = this.getHeaders();
        
        // Create EventSource
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
        this.setupSSEEventHandlers(connectionId, connection, resolve, reject);
        
        // Store connection
        this.connections.set(connectionId, connection);
        this.reconnectAttempts.set(connectionId, 0);
        
        // Update status
        this.updateStatus();
        
        // Start monitoring
        this.startHeartbeatMonitor(connectionId);
        this.startConnectionTimeout(connectionId);
        
        this.events.dispatchEvent(new CustomEvent('connection:created', {
          detail: { connectionId, type: 'sse', config }
        }));
        
        console.log(`📡 SSE connection created: ${connectionId}`);
        
        // Connection timeout
        setTimeout(() => {
          if (connection.status === 'connecting') {
            console.warn(`SSE connection ${connectionId} timeout`);
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
   * Setup SSE event handlers
   */
  setupSSEEventHandlers(connectionId, connection, resolve, reject) {
    let connectionEstablished = false;
    
    connection.eventSource.onopen = () => {
      connection.status = 'open';
      connectionEstablished = true;
      console.log(`📡 SSE connection opened: ${connectionId}`);
      
      this.events.dispatchEvent(new CustomEvent('connection:open', {
        detail: { connectionId, type: 'sse' }
      }));
      
      resolve(connectionId);
    };
    
    connection.eventSource.onmessage = (event) => {
      connection.lastActivity = Date.now();
      
      // If first message, consider connection established
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
    
    connection.eventSource.onerror = (error) => {
      if (!connectionEstablished) {
        connection.status = 'error';
        reject(new Error('SSE connection failed'));
      } else {
        this.handleConnectionError(connectionId, error);
      }
    };
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
            console.warn(`WebSocket connection ${connectionId} timeout`);
            websocket.close();
            reject(new Error('WebSocket connection timeout'));
          }
        }, 10000);
        
        websocket.onopen = () => {
          clearTimeout(connectionTimeout);
          connection.status = 'open';
          console.log(`📡 WebSocket connection opened: ${connectionId}`);
          
          // Authenticate with Django Channels
          this.authenticateWebSocket(connectionId, config);
          
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
          console.error(`WebSocket error (${connectionId}):`, error);
          this.handleConnectionError(connectionId, error);
          reject(error);
        };
        
        websocket.onclose = (event) => {
          clearTimeout(connectionTimeout);
          connection.status = 'closed';
          console.log(`📡 WebSocket connection closed: ${connectionId}`, event.code, event.reason);
          
          this.events.dispatchEvent(new CustomEvent('connection:close', {
            detail: { connectionId, type: 'websocket', code: event.code, reason: event.reason }
          }));
          
          // Attempt reconnection
          if (event.code !== 1000) {
            this.handleReconnection(connectionId, config.url, config);
          }
        };
        
        // Store connection
        this.connections.set(connectionId, connection);
        this.reconnectAttempts.set(connectionId, 0);
        
        // Start monitoring
        this.startHeartbeatMonitor(connectionId);
        this.startConnectionTimeout(connectionId);
        
      } catch (error) {
        reject(new Error(`WebSocket connection failed: ${error.message}`));
      }
    });
  }
  
  /**
   * Authenticate WebSocket
   */
  authenticateWebSocket(connectionId, config) {
    const connection = this.connections.get(connectionId);
    if (!connection || connection.type !== 'websocket') return;
    
    const authMessage = {
      type: 'authenticate',
      data: {
        token: Utils.getCSRFToken(),
        user: config.user || 'anonymous'
      }
    };
    
    connection.websocket.send(JSON.stringify(authMessage));
  }
  
  /**
   * Start heartbeat monitor
   */
  startHeartbeatMonitor(connectionId) {
    const connection = this.connections.get(connectionId);
    if (!connection) return;
    
    // Clear existing interval
    this.stopHeartbeatMonitor(connectionId);
    
    // Create heartbeat interval for WebSocket
    if (connection.type === 'websocket') {
      const interval = setInterval(() => {
        this.sendHeartbeat(connectionId);
      }, 30000);
      
      this.heartbeatIntervals.set(connectionId, interval);
    }
    
    // Monitor for inactivity
    const checkInterval = setInterval(() => {
      const conn = this.connections.get(connectionId);
      if (conn && Date.now() - conn.lastActivity > 120000) {
        console.warn(`Connection ${connectionId} inactive for 2 minutes`);
        this.sendHeartbeat(connectionId);
        
        // Close if still inactive
        setTimeout(() => {
          const stillConn = this.connections.get(connectionId);
          if (stillConn && Date.now() - stillConn.lastActivity > 180000) {
            console.warn(`Closing inactive connection: ${connectionId}`);
            this.closeConnection(connectionId, 'Inactive for too long');
          }
        }, 60000);
      }
    }, 60000);
    
    this.heartbeatIntervals.set(connectionId + '_inactivity', checkInterval);
  }
  
  /**
   * Send heartbeat
   */
  sendHeartbeat(connectionId) {
    const connection = this.connections.get(connectionId);
    if (!connection) return;
    
    const heartbeat = {
      type: 'ping',
      timestamp: Date.now()
    };
    
    if (connection.type === 'websocket' && connection.websocket.readyState === WebSocket.OPEN) {
      connection.websocket.send(JSON.stringify(heartbeat));
    }
  }
  
  /**
   * Stop heartbeat monitor
   */
  stopHeartbeatMonitor(connectionId) {
    const interval = this.heartbeatIntervals.get(connectionId);
    if (interval) {
      clearInterval(interval);
      this.heartbeatIntervals.delete(connectionId);
    }
    
    const inactivityInterval = this.heartbeatIntervals.get(connectionId + '_inactivity');
    if (inactivityInterval) {
      clearInterval(inactivityInterval);
      this.heartbeatIntervals.delete(connectionId + '_inactivity');
    }
  }
  
  /**
   * Start connection timeout
   */
  startConnectionTimeout(connectionId) {
    this.stopConnectionTimeout(connectionId);
    
    const timeout = setTimeout(() => {
      console.warn(`Connection ${connectionId} reached maximum time limit`);
      this.closeConnection(connectionId, 'Maximum connection time reached');
    }, this.maxConnectionTime);
    
    this.connectionTimeouts.set(connectionId, timeout);
  }
  
  /**
   * Stop connection timeout
   */
  stopConnectionTimeout(connectionId) {
    const timeout = this.connectionTimeouts.get(connectionId);
    if (timeout) {
      clearTimeout(timeout);
      this.connectionTimeouts.delete(connectionId);
    }
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
    
    // Attempt reconnection if closed
    if (connection.type === 'sse' && connection.eventSource.readyState === EventSource.CLOSED) {
      this.handleReconnection(connectionId, connection.config.url, connection.config);
    }
    
    // Update status
    this.status.failedConnections++;
    this.updateStatus();
    
    // Dispatch error event
    this.events.dispatchEvent(new CustomEvent('connection:error', {
      detail: { connectionId, error }
    }));
  }
  
  /**
   * Handle reconnection
   */
  async handleReconnection(connectionId, url, config) {
    const connection = this.connections.get(connectionId);
    
    if (!connection) {
      console.log(`No connection found for ${connectionId}`);
      return;
    }
    
    const reconnectCount = this.reconnectAttempts.get(connectionId) || 0;
    
    if (reconnectCount >= this.maxReconnectAttempts) {
      console.log(`Max reconnection attempts reached for ${connectionId}`);
      
      // Remove connection
      this.closeConnection(connectionId);
      
      // Dispatch final failure event
      this.events.dispatchEvent(new CustomEvent('connection:failed', {
        detail: { connectionId, reconnectCount }
      }));
      
      return;
    }
    
    // Update reconnect count
    const newCount = reconnectCount + 1;
    this.reconnectAttempts.set(connectionId, newCount);
    
    console.log(`🔄 Reconnecting (${newCount}/${this.maxReconnectAttempts})...`);
    
    // Calculate delay with exponential backoff
    const delay = newCount === 1 
      ? this.initialReconnectDelay 
      : this.reconnectDelay * Math.pow(1.5, newCount - 1);
    
    // Add jitter
    const jitter = Math.random() * 1000;
    const totalDelay = delay + jitter;
    
    setTimeout(async () => {
      try {
        // Close old connection
        this.cleanupConnection(connectionId);
        
        // Create new connection
        const newConnectionId = await this.createConnection(url, {
          ...config,
          onOpen: (id) => {
            if (config.onOpen) config.onOpen(id);
            console.log(`✅ Reconnected: ${id}`);
            
            // Update status
            this.status.reconnections++;
            this.updateStatus();
            
            // Dispatch reconnection event
            this.events.dispatchEvent(new CustomEvent('connection:reconnected', {
              detail: { connectionId: id, reconnectCount: newCount }
            }));
          }
        });
        
        console.log(`Reconnected with new ID: ${newConnectionId}`);
        
      } catch (error) {
        console.error(`Reconnection failed for ${connectionId}:`, error);
      }
    }, totalDelay);
  }
  
  /**
   * Close connection
   */
  closeConnection(connectionId, reason = 'User initiated') {
    const connection = this.connections.get(connectionId);
    
    if (connection) {
      // Cleanup connection
      this.cleanupConnection(connectionId);
      
      // Remove from maps
      this.connections.delete(connectionId);
      this.reconnectAttempts.delete(connectionId);
      
      // Update status
      this.updateStatus();
      
      console.log(`🔌 Connection closed: ${connectionId} (${reason})`);
      
      this.events.dispatchEvent(new CustomEvent('connection:closed', {
        detail: { connectionId, reason, type: connection.type }
      }));
      
      return true;
    }
    
    return false;
  }
  
  /**
   * Cleanup connection resources
   */
  cleanupConnection(connectionId) {
    const connection = this.connections.get(connectionId);
    if (!connection) return;
    
    // Stop monitoring
    this.stopHeartbeatMonitor(connectionId);
    this.stopConnectionTimeout(connectionId);
    
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
   * Close all connections
   */
  closeAllConnections(reason = 'Application shutdown') {
    this.connections.forEach((connection, connectionId) => {
      this.closeConnection(connectionId, reason);
    });
    
    console.log('🔌 All connections closed');
  }
  
  /**
   * Get connection status
   */
  getConnectionStatus(connectionId) {
    const connection = this.connections.get(connectionId);
    
    if (!connection) {
      return 'closed';
    }
    
    if (connection.type === 'sse' && connection.eventSource) {
      const readyState = connection.eventSource.readyState;
      return readyState === EventSource.OPEN ? 'open' : 
             readyState === EventSource.CONNECTING ? 'connecting' : 'closed';
    } else if (connection.type === 'websocket' && connection.websocket) {
      const readyState = connection.websocket.readyState;
      return readyState === WebSocket.OPEN ? 'open' :
             readyState === WebSocket.CONNECTING ? 'connecting' : 'closed';
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
        type: connection.type,
        url: connection.config.url,
        status: this.getConnectionStatus(connectionId),
        reconnectCount: this.reconnectAttempts.get(connectionId) || 0,
        createdAt: connection.createdAt,
        lastActivity: connection.lastActivity,
        name: connection.config.name || 'unnamed',
        config: connection.config
      };
    });
    
    return connections;
  }
  
  /**
   * Update status
   */
  updateStatus() {
    this.status.totalConnections = this.connections.size;
    this.status.activeConnections = Array.from(this.connections.values())
      .filter(conn => this.getConnectionStatus(conn.id) === 'open').length;
    
    // Dispatch status update event
    this.events.dispatchEvent(new CustomEvent('status:update', {
      detail: { ...this.status }
    }));
  }
  
  /**
   * Handle incoming message
   */
  handleIncomingMessage(connectionId, data) {
    const connection = this.connections.get(connectionId);
    if (!connection) return;
    
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
    
    // Handle specific message types
    this.processMessageType(connectionId, data);
  }
  
  /**
   * Process message type
   */
  processMessageType(connectionId, data) {
    const messageType = data.type || data.event;
    
    switch (messageType) {
      case 'ping':
        this.handlePing(connectionId, data);
        break;
        
      case 'heartbeat':
        this.handleHeartbeat(connectionId, data);
        break;
        
      case 'notification':
        this.handleNotification(connectionId, data);
        break;
        
      case 'session_update':
        this.handleSessionUpdate(connectionId, data);
        break;
        
      default:
        // Dispatch generic message event
        this.events.dispatchEvent(new CustomEvent('message:' + (messageType || 'unknown'), {
          detail: { connectionId, data }
        }));
    }
  }
  
  /**
   * Handle ping
   */
  handlePing(connectionId, data) {
    const connection = this.connections.get(connectionId);
    if (connection) {
      connection.lastActivity = Date.now();
    }
    
    this.events.dispatchEvent(new CustomEvent('ping', {
      detail: { connectionId, data }
    }));
  }
  
  /**
   * Handle heartbeat
   */
  handleHeartbeat(connectionId, data) {
    const connection = this.connections.get(connectionId);
    if (connection) {
      connection.lastActivity = Date.now();
    }
  }
  
  /**
   * Handle notification
   */
  handleNotification(connectionId, data) {
    const notificationData = this.normalizeNotificationData(data.data || data);
    
    this.events.dispatchEvent(new CustomEvent('notification', {
      detail: { connectionId, data: notificationData }
    }));
  }
  
  /**
   * Handle session update
   */
  handleSessionUpdate(connectionId, data) {
    this.events.dispatchEvent(new CustomEvent('session:update', {
      detail: { connectionId, data }
    }));
  }
  
  /**
   * Send message
   */
  async sendMessage(connectionId, data) {
    const connection = this.connections.get(connectionId);
    
    if (!connection) {
      throw new Error(`Connection ${connectionId} not found`);
    }
    
    if (connection.type === 'websocket') {
      if (connection.websocket.readyState === WebSocket.OPEN) {
        connection.websocket.send(JSON.stringify(data));
        return true;
      } else {
        throw new Error('WebSocket is not open');
      }
    } else if (connection.type === 'sse' && connection.config.sendUrl) {
      // SSE connections are read-only, use HTTP POST
      return await this.sendHTTPMessage(connection.config.sendUrl, data);
    }
    
    return false;
  }
  
  /**
   * Send HTTP message
   */
  async sendHTTPMessage(url, data) {
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': Utils.getCSRFToken()
        },
        body: JSON.stringify(data)
      });
      
      return response.ok;
    } catch (error) {
      console.error('Failed to send HTTP message:', error);
      return false;
    }
  }
  
  /**
   * Normalize configuration
   */
  normalizeConfig(url, options) {
    return {
      url,
      name: options.name || 'unnamed',
      onOpen: options.onOpen,
      onMessage: options.onMessage,
      onError: options.onError,
      onClose: options.onClose,
      sendUrl: options.sendUrl,
      user: options.user,
      maxReconnectAttempts: options.maxReconnectAttempts || this.maxReconnectAttempts,
      ...options
    };
  }
  
  /**
   * Determine if WebSocket should be used
   */
  shouldUseWebSocket(config) {
    const supportsWebSocket = 'WebSocket' in window || 'MozWebSocket' in window;
    const isDjangoChannelUrl = config.url.includes('/ws/') || config.useWebSocket;
    
    return supportsWebSocket && (this.useChannels || isDjangoChannelUrl);
  }
  
  /**
   * Convert SSE URL to WebSocket URL
   */
  getWebSocketURL(url) {
    if (url.startsWith('http')) {
      return url.replace(/^http/, 'ws') + 'ws/';
    }
    return `ws://${window.location.host}${this.channelPath}`;
  }
  
  /**
   * Get request headers
   */
  getHeaders() {
    const headers = {};
    const csrfToken = Utils.getCSRFToken();
    
    if (csrfToken) {
      headers['X-CSRFToken'] = csrfToken;
    }
    
    return headers;
  }
  
  /**
   * Enable Django Channels
   */
  enableChannels(channelPath = '/ws/notifications/') {
    this.useChannels = true;
    this.channelPath = channelPath;
    console.log('🔌 Django Channels support enabled');
  }
  
  /**
   * Disable Django Channels
   */
  disableChannels() {
    this.useChannels = false;
    console.log('🔌 Django Channels support disabled');
  }
  
  /**
   * Set maximum connections
   */
  setMaxConnections(max) {
    this.maxConnections = Math.max(1, max);
    console.log(`🔌 Maximum connections set to ${this.maxConnections}`);
  }
  
  /**
   * Get current status
   */
  getStatus() {
    return { ...this.status };
  }
  
  /**
   * Get HTMX statistics
   */
  getHTMXStats() {
    return {
      triggersRegistered: this.htmxTriggers.size,
      notificationsProcessed: this.status.htmxNotifications,
      queueLength: this.htmxResponseQueue.length
    };
  }
  
  /**
   * Add event listener
   */
  on(event, callback) {
    this.events.addEventListener(event, callback);
  }
  
  /**
   * Remove event listener
   */
  off(event, callback) {
    this.events.removeEventListener(event, callback);
  }
  
  /**
   * Destroy manager
   */
  destroy() {
    // Close all connections
    this.closeAllConnections('Manager destroyed');
    
    // Clear all intervals and timeouts
    this.heartbeatIntervals.forEach(interval => clearInterval(interval));
    this.connectionTimeouts.forEach(timeout => clearTimeout(timeout));
    
    // Clear maps
    this.connections.clear();
    this.reconnectAttempts.clear();
    this.heartbeatIntervals.clear();
    this.connectionTimeouts.clear();
    this.htmxResponseQueue.length = 0;
    
    // Remove HTMX event listeners
    if (typeof htmx !== 'undefined') {
      document.removeEventListener('htmx:beforeSwap', this.processHTMXResponse);
      document.removeEventListener('htmx:trigger', this.processHTMXTrigger);
    }
    
    console.log('🔌 SSE Manager destroyed');
  }
}

// Global SSE Manager instance
window.SSEManager = new SSEHandler();
export default SSEHandler;