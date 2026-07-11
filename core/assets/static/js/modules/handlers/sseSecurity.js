export class SSESecurityHandler {
    constructor() {
        this.connections = new Map();
        this.reconnectAttempts = 3;
        this.reconnectDelay = 5000;
        console.log('🔐 SSE security handler created');
    }

    init() {
        console.log('🔐 SSE security initialized');
        return Promise.resolve();
    }

    async createConnection(url, options = {}) {
        const connectionId = `sse_${Date.now()}`;
        
        try {
            const eventSource = new EventSource(url);
            
            eventSource.onopen = () => {
                console.log(`📡 SSE connection opened: ${connectionId}`);
                if (options.onOpen) options.onOpen(connectionId);
            };
            
            eventSource.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    if (options.onMessage) options.onMessage(data);
                    
                    document.dispatchEvent(new CustomEvent('sse:message', {
                        detail: { connectionId, data }
                    }));
                } catch (error) {
                    console.error('Failed to parse SSE message:', error);
                }
            };
            
            eventSource.onerror = (error) => {
                console.error(`SSE connection error (${connectionId}):`, error);
                
                if (options.onError) options.onError(error);
                
                if (eventSource.readyState === EventSource.CLOSED) {
                    this.handleReconnection(connectionId, url, options);
                }
            };
            
            this.connections.set(connectionId, {
                eventSource,
                url,
                options,
                reconnectCount: 0
            });
            
            return connectionId;
            
        } catch (error) {
            console.error(`Failed to create SSE connection (${connectionId}):`, error);
            throw error;
        }
    }

    async handleReconnection(connectionId, url, options) {
        const connection = this.connections.get(connectionId);
        
        if (!connection || connection.reconnectCount >= this.reconnectAttempts) {
            console.log(`Max reconnection attempts reached for ${connectionId}`);
            this.connections.delete(connectionId);
            return;
        }
        
        connection.reconnectCount++;
        
        console.log(`Reconnecting (${connection.reconnectCount}/${this.reconnectAttempts})...`);
        
        setTimeout(async () => {
            try {
                await this.createConnection(url, options);
                console.log(`✅ Reconnected: ${connectionId}`);
            } catch (error) {
                console.error(`Reconnection failed for ${connectionId}:`, error);
            }
        }, this.reconnectDelay);
    }

    closeConnection(connectionId) {
        const connection = this.connections.get(connectionId);
        
        if (connection && connection.eventSource) {
            connection.eventSource.close();
            this.connections.delete(connectionId);
            console.log(`🔌 SSE connection closed: ${connectionId}`);
            return true;
        }
        
        return false;
    }

    closeAll() {
        this.connections.forEach((connection, connectionId) => {
            this.closeConnection(connectionId);
        });
        
        console.log('🔌 All SSE connections closed');
    }

    getStatus(connectionId) {
        const connection = this.connections.get(connectionId);
        
        if (!connection) return 'closed';
        
        const readyState = connection.eventSource.readyState;
        
        switch (readyState) {
            case EventSource.CONNECTING:
                return 'connecting';
            case EventSource.OPEN:
                return 'open';
            case EventSource.CLOSED:
                return 'closed';
            default:
                return 'unknown';
        }
    }

    getAllConnections() {
        const connections = {};
        
        this.connections.forEach((connection, connectionId) => {
            connections[connectionId] = {
                url: connection.url,
                status: this.getStatus(connectionId),
                reconnectCount: connection.reconnectCount
            };
        });
        
        return connections;
    }

    async sendMessage(connectionId, data) {
        const connection = this.connections.get(connectionId);
        
        if (!connection || !connection.options.sendUrl) {
            console.warn('Send URL not configured for this connection');
            return false;
        }
        
        try {
            const response = await fetch(connection.options.sendUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            return response.ok;
        } catch (error) {
            console.error('Failed to send SSE message:', error);
            return false;
        }
    }
}