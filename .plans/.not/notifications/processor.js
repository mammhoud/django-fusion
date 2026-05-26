
/**
 * Message Processor for Notifications
 */
export const MessageProcessor = {
    /**
     * Process notification message
     */
    process(message) {
        if (typeof message === 'string') {
            try {
                message = JSON.parse(message);
            } catch (error) {
                return this.processStringMessage(message);
            }
        }
        
        return this.processObjectMessage(message);
    },
    
    /**
     * Process string message
     */
    processStringMessage(message) {
        // Simple string processing
        if (message.toLowerCase().includes('error')) {
            return {
                type: 'error',
                message: message,
                title: 'Error'
            };
        } else if (message.toLowerCase().includes('success')) {
            return {
                type: 'success',
                message: message,
                title: 'Success'
            };
        } else if (message.toLowerCase().includes('warning')) {
            return {
                type: 'warning',
                message: message,
                title: 'Warning'
            };
        } else {
            return {
                type: 'info',
                message: message,
                title: 'Information'
            };
        }
    },
    
    /**
     * Process object message
     */
    processObjectMessage(message) {
        const defaults = {
            type: 'info',
            title: '',
            message: '',
            duration: 5000,
            closable: true
        };
        
        return { ...defaults, ...message };
    },
    
    /**
     * Validate message format
     */
    validate(message) {
        if (!message) return false;
        
        const processed = this.process(message);
        
        // Check required fields
        if (!processed.message || typeof processed.message !== 'string') {
            return false;
        }
        
        // Check valid type
        const validTypes = ['success', 'error', 'warning', 'info'];
        if (!validTypes.includes(processed.type)) {
            processed.type = 'info';
        }
        
        // Check duration
        if (processed.duration && (typeof processed.duration !== 'number' || processed.duration < 0)) {
            processed.duration = 5000;
        }
        
        return processed;
    },
    
    /**
     * Format timestamp for display
     */
    formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;
        
        // Less than a minute
        if (diff < 60000) {
            return 'Just now';
        }
        
        // Less than an hour
        if (diff < 3600000) {
            const minutes = Math.floor(diff / 60000);
            return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
        }
        
        // Less than a day
        if (diff < 86400000) {
            const hours = Math.floor(diff / 3600000);
            return `${hours} hour${hours > 1 ? 's' : ''} ago`;
        }
        
        // More than a day
        return date.toLocaleDateString();
    },
    
    /**
     * Truncate long messages
     */
    truncate(message, maxLength = 200) {
        if (message.length <= maxLength) return message;
        
        return message.substring(0, maxLength) + '...';
    },
    
    /**
     * Extract links from message
     */
    extractLinks(message) {
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        const matches = message.match(urlRegex);
        
        if (!matches) return { message, links: [] };
        
        let processedMessage = message;
        const links = [];
        
        matches.forEach((url, index) => {
            const placeholder = `[LINK_${index}]`;
            processedMessage = processedMessage.replace(url, placeholder);
            links.push({ placeholder, url });
        });
        
        return { message: processedMessage, links };
    },
    
    /**
     * Sanitize message HTML
     */
    sanitize(message) {
        const div = document.createElement('div');
        div.textContent = message;
        return div.innerHTML;
    },
    
    /**
     * Parse notification action
     */
    parseAction(action) {
        if (typeof action === 'string') {
            try {
                action = JSON.parse(action);
            } catch (error) {
                return null;
            }
        }
        
        if (typeof action !== 'object') return null;
        
        const validAction = {
            text: action.text || 'Action',
            url: action.url || null,
            callback: action.callback || null
        };
        
        return validAction;
    }
};

/**
 * Fixed Notification Handler for HTMX Trigger Processing
 * This script should be included AFTER HTMX but BEFORE your main notification system
 */
class HTMXNotificationHandler {
    constructor() {
        this.initialized = false;
        this.notificationQueue = [];
        this.debug = true;
        this.initialize();
    }
    
    initialize() {
        if (this.initialized) return;
        
        console.log('🔔 Initializing HTMX Notification Handler...');
        
        // Listen for HTMX responses
        this.setupHTMXListener();
        
        // Listen for SSE messages if using HTMX SSE extension
        this.setupSSEListener();
        
        // Process any queued notifications
        this.processQueue();
        
        this.initialized = true;
        
        console.log('✅ HTMX Notification Handler initialized');
    }
    
    setupHTMXListener() {
        // Listen for HTMX responses - using 'htmx:afterSwap' instead of 'htmx:beforeSwap'
        document.addEventListener('htmx:afterSwap', (event) => {
            this.handleHTMXResponse(event);
        });
        
        // Also listen for 'htmx:beforeOnLoad' to catch response headers
        document.addEventListener('htmx:beforeOnLoad', (event) => {
            this.handleHTMXResponseHeaders(event);
        });
        
        // Listen for 'htmx:beforeRequest' to track requests
        document.addEventListener('htmx:beforeRequest', (event) => {
            if (this.debug) {
                console.log('📤 HTMX Request:', event.detail);
            }
        });
    }
    
    handleHTMXResponse(event) {
        const xhr = event.detail.xhr;
        if (!xhr) return;
        
        // Check for HX-Trigger header
        const triggerHeader = xhr.getResponseHeader('HX-Trigger');
        if (triggerHeader) {
            this.processTriggerHeader(triggerHeader);
        }
        
        // Check for HX-Trigger-After-Settle header
        const settleHeader = xhr.getResponseHeader('HX-Trigger-After-Settle');
        if (settleHeader) {
            setTimeout(() => this.processTriggerHeader(settleHeader), 100);
        }
        
        // Check for HX-Trigger-After-Swap header
        const swapHeader = xhr.getResponseHeader('HX-Trigger-After-Swap');
        if (swapHeader) {
            this.processTriggerHeader(swapHeader);
        }
    }
    
    handleHTMXResponseHeaders(event) {
        const xhr = event.detail.xhr;
        if (!xhr) return;
        
        // Check headers early
        const triggerHeader = xhr.getResponseHeader('HX-Trigger');
        if (triggerHeader && this.debug) {
            console.log('📨 HX-Trigger header found:', triggerHeader);
        }
    }
    
    processTriggerHeader(headerValue) {
        if (!headerValue) return;
        
        try {
            const triggers = JSON.parse(headerValue);
            
            if (this.debug) {
                console.log('📋 Parsed triggers:', triggers);
            }
            
            // Handle showNotification trigger
            if (triggers.showNotification) {
                const notification = triggers.showNotification;
                
                if (this.debug) {
                    console.log('🔔 Processing notification:', notification);
                }
                
                this.showNotification(notification);
            }
            
            // Handle multiple triggers
            Object.keys(triggers).forEach(key => {
                if (key !== 'showNotification' && triggers[key]) {
                    if (this.debug) {
                        console.log('🔧 Additional trigger:', key, triggers[key]);
                    }
                    
                    // You can handle other trigger types here
                    if (key === 'refresh') {
                        // Handle refresh trigger
                        setTimeout(() => {
                            if (triggers[key] === true) {
                                window.location.reload();
                            }
                        }, 100);
                    }
                }
            });
            
        } catch (error) {
            console.error('❌ Failed to parse HX-Trigger:', error, 'Header value:', headerValue);
        }
    }
    
    showNotification(data) {
        // Validate notification data
        if (!data.message) {
            console.warn('⚠️ Notification missing message:', data);
            return;
        }
        
        const notification = {
            message: data.message,
            level: data.level || 'info',
            title: data.title || this.getDefaultTitle(data.level),
            duration: data.duration || 5000,
            icon: data.icon || this.getIconForLevel(data.level),
            dismissible: data.dismissible !== false,
            position: data.position || 'top-right'
        };
        
        // Queue notification if system isn't ready yet
        if (!window.NotificationSystem && !window.showNotification) {
            this.notificationQueue.push(notification);
            console.log('📥 Queued notification:', notification.message);
            return;
        }
        
        // Show notification using available system
        this.displayNotification(notification);
    }
    
    displayNotification(notification) {
        // Try window.NotificationSystem first (your main system)
        if (window.NotificationSystem && typeof window.NotificationSystem.show === 'function') {
            window.NotificationSystem.show(notification.message, {
                type: notification.level,
                title: notification.title,
                duration: notification.duration,
                displayType: 'toast'
            });
            return;
        }
        
        // Try window.showNotification (global method)
        if (window.showNotification && typeof window.showNotification === 'function') {
            window.showNotification(notification.message, {
                type: notification.level,
                title: notification.title,
                duration: notification.duration
            });
            return;
        }
        
        // Fallback: Show with Bootstrap toast if available
        this.showBootstrapToast(notification);
    }
    
    showBootstrapToast(notification) {
        // Create toast element
        const toastId = 'toast-' + Date.now();
        const toastEl = document.createElement('div');
        toastEl.className = 'toast';
        toastEl.id = toastId;
        toastEl.setAttribute('role', 'alert');
        toastEl.setAttribute('aria-live', 'assertive');
        toastEl.setAttribute('aria-atomic', 'true');
        toastEl.setAttribute('data-bs-delay', notification.duration);
        
        // Map level to Bootstrap class
        const levelMap = {
            'success': 'success',
            'error': 'danger',
            'warning': 'warning',
            'info': 'info'
        };
        
        const bgClass = levelMap[notification.level] || 'info';
        
        // Get current time
        const now = new Date();
        const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        // Build toast HTML
        toastEl.innerHTML = `
            <div class="toast-header bg-${bgClass} text-white">
                <i class="${notification.icon} me-2"></i>
                <strong class="me-auto">${notification.title}</strong>
                <small class="text-white-50">${timeStr}</small>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${this.escapeHtml(notification.message)}
            </div>
        `;
        
        // Get or create toast container
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed p-3';
            container.style.cssText = 'z-index: 1055; top: 20px; right: 20px;';
            document.body.appendChild(container);
        }
        
        // Add toast to container
        container.appendChild(toastEl);
        
        // Initialize Bootstrap toast
        if (typeof bootstrap !== 'undefined' && bootstrap.Toast) {
            const bsToast = new bootstrap.Toast(toastEl, {
                delay: notification.duration,
                autohide: true
            });
            bsToast.show();
            
            // Clean up after toast is hidden
            toastEl.addEventListener('hidden.bs.toast', () => {
                toastEl.remove();
            });
        } else {
            // Fallback: auto-remove after duration
            setTimeout(() => {
                if (toastEl.parentNode) {
                    toastEl.remove();
                }
            }, notification.duration);
            
            // Add close button functionality
            const closeBtn = toastEl.querySelector('.btn-close');
            if (closeBtn) {
                closeBtn.addEventListener('click', () => {
                    toastEl.remove();
                });
            }
        }
        
        console.log('✅ Notification shown via fallback:', notification.message);
    }
    
    setupSSEListener() {
        // Listen for SSE messages if using HTMX SSE extension
        document.addEventListener('htmx:sseMessage', (event) => {
            if (event.detail && event.detail.data) {
                try {
                    const data = JSON.parse(event.detail.data);
                    if (data.type === 'notification') {
                        this.showNotification(data);
                    }
                } catch (error) {
                    console.error('❌ Failed to parse SSE message:', error);
                }
            }
        });
    }
    
    processQueue() {
        if (this.notificationQueue.length > 0) {
            console.log(`📋 Processing ${this.notificationQueue.length} queued notifications`);
            this.notificationQueue.forEach(notification => {
                this.displayNotification(notification);
            });
            this.notificationQueue = [];
        }
    }
    
    getDefaultTitle(level) {
        const titles = {
            'success': 'Success',
            'error': 'Error',
            'warning': 'Warning',
            'info': 'Information'
        };
        return titles[level] || 'Notification';
    }
    
    getIconForLevel(level) {
        const icons = {
            'success': 'bi-check-circle-fill',
            'error': 'bi-exclamation-triangle-fill',
            'warning': 'bi-exclamation-circle-fill',
            'info': 'bi-info-circle-fill'
        };
        return icons[level] || 'bi-bell-fill';
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    // Public method to manually trigger a notification
    trigger(notification) {
        this.showNotification(notification);
    }
    
    // Debug method to test the handler
    test() {
        this.showNotification({
            message: 'HTMX Notification Handler test successful!',
            level: 'success',
            title: 'Test Notification',
            duration: 3000
        });
    }
}

// Initialize immediately
const htmxNotificationHandler = new HTMXNotificationHandler();

// Export for module usage
export default htmxNotificationHandler;