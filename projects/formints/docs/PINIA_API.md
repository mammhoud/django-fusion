# Pinia / Frontend API Integration

> **Purpose:** Document how to connect Vue.js (Pinia) or React frontend to the Robyn sidecar API  
> **Last Updated:** 9 August 2026

---

## 1. Store Architecture

```
src/stores/
├── index.ts              # Barrel exports + initialization
├── client.ts             # Base API client (fetch + auth + WS)
├── products.ts           # Product CRUD store
├── sales.ts              # Sales store
├── customers.ts          # Customer store
├── nodes.ts              # Node registry + WebSocket stream
├── sync.ts               # Sync status + config + log
├── approvals.ts          # Approval queue + WebSocket events
├── config.ts             # Device/Master/Cloud config CRUD
├── auth.ts               # Device token auth
└── events.ts             # Node event history
```

---

## 2. Base API Client

```typescript
// src/stores/client.ts
// Full-featured HTTP + WebSocket client for POS sidecar

type WsHandler = (data: any) => void;

interface ApiResponse<T> {
  data: T | null;
  error: string | null;
  ok: boolean;
  status: number;
  pagination?: {
    page: number;
    per_page: number;
    total: number;
    total_pages: number;
  };
}

class PosClient {
  private baseUrl: string;
  private token: string | null = null;
  private wsManager = new WsManager();

  constructor(baseUrl?: string) {
    this.baseUrl = baseUrl || localStorage.getItem('pos_sidecar_url')
      || 'http://127.0.0.1:8766';
  }

  // ── Auth ──

  setToken(token: string | null) {
    this.token = token;
    if (token) localStorage.setItem('pos_device_token', token);
    else localStorage.removeItem('pos_device_token');
  }

  private headers(): Record<string, string> {
    const h: Record<string, string> = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };
    if (this.token) h['Authorization'] = `Bearer ${this.token}`;
    return h;
  }

  // ── HTTP Methods ──

  async get<T>(path: string): Promise<ApiResponse<T>> {
    return this.request<T>('GET', path);
  }

  async post<T>(path: string, body?: unknown): Promise<ApiResponse<T>> {
    return this.request<T>('POST', path, body);
  }

  async patch<T>(path: string, body?: unknown): Promise<ApiResponse<T>> {
    return this.request<T>('PATCH', path, body);
  }

  async delete(path: string): Promise<ApiResponse<void>> {
    return this.request<void>('DELETE', path);
  }

  private async request<T>(
    method: string,
    path: string,
    body?: unknown,
  ): Promise<ApiResponse<T>> {
    try {
      const url = `${this.baseUrl}${path}`;
      const opts: RequestInit = {
        method,
        headers: this.headers(),
      };
      if (body && method !== 'GET' && method !== 'DELETE') {
        opts.body = JSON.stringify(body);
      }

      const resp = await fetch(url, opts);
      const json = await resp.json();

      return {
        data: json,
        error: json.error || null,
        ok: resp.ok,
        status: resp.status,
        pagination: json.pagination,
      };
    } catch (err) {
      return { data: null, error: String(err), ok: false, status: 0 };
    }
  }

  // ── Health ──

  async healthCheck(): Promise<boolean> {
    const { ok } = await this.get('/health');
    return ok;
  }

  // ── Auth Endpoints ──

  async login(deviceId: string, role = 'manager'): Promise<string | null> {
    const { data, error } = await this.post<{ token: string }>('/auth/token', {
      device_id: deviceId,
      role,
    });
    if (data?.token) {
      this.setToken(data.token);
      return data.token;
    }
    console.error('Login failed:', error);
    return null;
  }

  async refreshToken(): Promise<string | null> {
    const { data, error } = await this.post<{ token: string }>('/auth/refresh');
    if (data?.token) {
      this.setToken(data.token);
      return data.token;
    }
    console.error('Token refresh failed:', error);
    return null;
  }

  // ── WebSocket ──

  connectWs(
    path: string,
    onMessage: WsHandler,
    onStateChange?: (state: 'connected' | 'disconnected' | 'reconnecting') => void,
    filters?: Record<string, any>,
  ): string {
    const url = this.baseUrl.replace(/^http/, 'ws') + path;
    return this.wsManager.connect(url, onMessage, onStateChange, filters);
  }

  disconnectWs(id: string) {
    this.wsManager.disconnect(id);
  }

  updateWsFilter(id: string, filters: Record<string, any>) {
    this.wsManager.updateFilter(id, filters);
  }
}

// ── WebSocket Manager ──

class WsManager {
  private connections = new Map<string, {
    ws: WebSocket;
    url: string;
    handlers: Set<WsHandler>;
    stateChange?: (state: string) => void;
    filters: Record<string, any>;
    retries: number;
    timer?: ReturnType<typeof setTimeout>;
  }>();

  private nextId = 0;

  connect(
    url: string,
    onMessage: WsHandler,
    onStateChange?: (state: string) => void,
    filters?: Record<string, any>,
  ): string {
    const id = `ws_${++this.nextId}`;
    this.createConnection(id, url, onMessage, onStateChange, filters || {});
    return id;
  }

  private createConnection(
    id: string,
    url: string,
    handler: WsHandler,
    stateChange?: (state: string) => void,
    filters?: Record<string, any>,
  ) {
    const ws = new WebSocket(url);
    const entry = { ws, url, handlers: new Set([handler]), stateChange, filters: filters || {}, retries: 0 };
    this.connections.set(id, entry);

    ws.onopen = () => {
      entry.retries = 0;
      entry.stateChange?.('connected');
      // Send initial filter
      if (Object.keys(entry.filters).length > 0) {
        ws.send(JSON.stringify({ filter: entry.filters }));
      }
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        entry.handlers.forEach(h => h(data));
      } catch { /* ignore */ }
    };

    ws.onclose = () => {
      entry.stateChange?.('disconnected');
      this.reconnect(id);
    };

    ws.onerror = () => {
      ws.close();
    };
  }

  private reconnect(id: string) {
    const entry = this.connections.get(id);
    if (!entry || entry.retries >= 5) return;

    entry.retries++;
    entry.stateChange?.('reconnecting');
    const delay = Math.min(1000 * Math.pow(2, entry.retries), 30000);

    entry.timer = setTimeout(() => {
      this.createConnection(
        id, entry.url, entry.handlers.values().next().value!,
        entry.stateChange, entry.filters,
      );
    }, delay);
  }

  disconnect(id: string) {
    const entry = this.connections.get(id);
    if (!entry) return;
    clearTimeout(entry.timer);
    entry.ws.close();
    this.connections.delete(id);
  }

  updateFilter(id: string, filters: Record<string, any>) {
    const entry = this.connections.get(id);
    if (!entry) return;
    entry.filters = filters;
    if (entry.ws.readyState === WebSocket.OPEN) {
      entry.ws.send(JSON.stringify({ filter: filters }));
    }
  }
}

export const posClient = new PosClient();
export type { ApiResponse, WsHandler };
```

---

## 3. Example Pinia Stores

### 3.1 Node Store

```typescript
// src/stores/nodes.ts
import { defineStore } from 'pinia';
import { posClient } from './client';

interface Node {
  node_id: string;
  hostname: string;
  status: 'online' | 'offline';
  node_type: string;
  version: string;
  last_seen: string | null;
  product_count: number;
  transaction_count: number;
}

export const useNodeStore = defineStore('nodes', {
  state: () => ({
    nodes: [] as Node[],
    loading: false,
    error: null as string | null,
    wsId: null as string | null,
    wsConnected: false,
  }),

  getters: {
    onlineNodes: (state) => state.nodes.filter(n => n.status === 'online'),
    offlineNodes: (state) => state.nodes.filter(n => n.status === 'offline'),
    byId: (state) => {
      const map = new Map(state.nodes.map(n => [n.node_id, n]));
      return (id: string) => map.get(id);
    },
  },

  actions: {
    async fetchAll() {
      this.loading = true;
      const { data, error } = await posClient.get<{ data: Node[] }>('/nodes');
      if (data?.data) this.nodes = data.data;
      if (error) this.error = error;
      this.loading = false;
    },

    async register(data: Partial<Node>) {
      const resp = await posClient.post<{ node: Node }>('/nodes/register', data);
      if (resp.data?.node) {
        const idx = this.nodes.findIndex(n => n.node_id === resp.data!.node.node_id);
        if (idx >= 0) this.nodes[idx] = resp.data.node;
        else this.nodes.push(resp.data.node);
      }
      return resp;
    },

    async heartbeat(nodeId: string) {
      return posClient.post('/nodes/heartbeat', { node_id: nodeId });
    },

    async delete(nodeId: string) {
      await posClient.delete(`/nodes/${nodeId}`);
      this.nodes = this.nodes.filter(n => n.node_id !== nodeId);
    },

    subscribeToEvents() {
      if (this.wsId) return;

      this.wsId = posClient.connectWs('/ws/nodes', (msg: any) => {
        if (msg.type !== 'node_event') return;
        const { event, node_id, data } = msg;

        switch (event) {
          case 'registered':
            if (!this.nodes.find(n => n.node_id === node_id)) {
              this.nodes.push(data);
            }
            break;
          case 'heartbeat':
            const idx = this.nodes.findIndex(n => n.node_id === node_id);
            if (idx >= 0) this.nodes[idx] = { ...this.nodes[idx], ...data };
            break;
          case 'deleted':
            this.nodes = this.nodes.filter(n => n.node_id !== node_id);
            break;
        }
      }, (state) => { this.wsConnected = state === 'connected'; });
    },

    unsubscribe() {
      if (this.wsId) {
        posClient.disconnectWs(this.wsId);
        this.wsId = null;
        this.wsConnected = false;
      }
    },
  },
});
```

### 3.2 Sync Store

```typescript
// src/stores/sync.ts
import { defineStore } from 'pinia';
import { posClient } from './client';

interface SyncConfig {
  enabled: boolean;
  cloud_url: string;
  status: string;
  last_sync: string | null;
  items_synced: number;
  errors: number;
}

interface SyncLogEntry {
  id: number;
  node_id: string;
  entity_type: string;
  status: string;
  created_at: string;
}

export const useSyncStore = defineStore('sync', {
  state: () => ({
    config: null as SyncConfig | null,
    log: [] as SyncLogEntry[],
    loading: false,
    wsId: null as string | null,
  }),

  actions: {
    async fetchStatus() {
      const { data } = await posClient.get<{
        config: SyncConfig;
        local_logs: any;
        cloud_crm: any;
      }>('/sync/status');
      if (data) this.config = data.config;
    },

    async fetchLog() {
      const { data } = await posClient.get<{ entries: SyncLogEntry[] }>('/sync/log');
      if (data) this.log = data.entries;
    },

    async trigger() {
      return posClient.post('/sync/trigger');
    },

    async updateConfig(config: Partial<SyncConfig>) {
      await posClient.patch('/sync/config', config);
      await this.fetchStatus();
    },

    subscribeToConfig() {
      if (this.wsId) return;
      this.wsId = posClient.connectWs('/ws/config', (msg: any) => {
        if (msg.type === 'config_event') {
          // Refresh status when config changes
          this.fetchStatus();
        }
      });
    },

    unsubscribe() {
      if (this.wsId) {
        posClient.disconnectWs(this.wsId);
        this.wsId = null;
      }
    },
  },
});
```

### 3.3 Approval Store

```typescript
// src/stores/approvals.ts
import { defineStore } from 'pinia';

interface Approval {
  id: number;
  entity_type: string;
  status: string;
  payload: Record<string, any>;
  created_at: string;
}

export const useApprovalStore = defineStore('approvals', {
  state: () => ({
    pending: [] as Approval[],
    stats: { pending: 0, approved: 0, rejected: 0, applied: 0, failed: 0 },
    loading: false,
  }),

  actions: {
    async fetchPending() {
      this.loading = true;
      const { data } = await posClient.get<{ pending: Approval[] }>('/approvals/pending');
      if (data) this.pending = data.pending;
      this.loading = false;
    },

    async fetchStats() {
      const { data } = await posClient.get('/approvals/stats');
      if (data) this.stats = data as any;
    },

    async approve(id: number, reviewer = '') {
      const resp = await posClient.post(`/approvals/${id}/approve`, { reviewer });
      if (resp.ok) {
        this.pending = this.pending.filter(a => a.id !== id);
        await this.fetchStats();
      }
      return resp;
    },

    async reject(id: number, reviewer = '', notes = '') {
      const resp = await posClient.post(`/approvals/${id}/reject`, { reviewer, notes });
      if (resp.ok) {
        this.pending = this.pending.filter(a => a.id !== id);
        await this.fetchStats();
      }
      return resp;
    },
  },
});
```

### 3.4 Config Store

```typescript
// src/stores/config.ts
import { defineStore } from 'pinia';

export const useConfigStore = defineStore('config', {
  state: () => ({
    devices: [] as any[],
    masters: [] as any[],
    cloudLinks: [] as any[],
    selectedNodeId: null as string | null,
    nodeConfigs: {} as Record<string, Record<string, any>>,
  }),

  actions: {
    async fetchAll() {
      await Promise.all([
        this.fetchDevices(),
        this.fetchMasters(),
        this.fetchCloudLinks(),
      ]);
    },

    async fetchDevices() {
      const { data } = await posClient.get<{ data: any[] }>('/config/devices');
      if (data) this.devices = data.data || [];
    },

    async fetchMasters() {
      const { data } = await posClient.get<{ data: any[] }>('/config/master');
      if (data) this.masters = data.data || [];
    },

    async fetchCloudLinks() {
      const { data } = await posClient.get<{ data: any[] }>('/config/cloud-links');
      if (data) this.cloudLinks = data.data || [];
    },

    async fetchNodeConfig(nodeId: string) {
      const { data } = await posClient.get<{ configs: Record<string, any> }>(
        `/nodes/${nodeId}/config`,
      );
      if (data) this.nodeConfigs[nodeId] = data.configs;
    },

    async setNodeConfig(nodeId: string, key: string, value: any) {
      await posClient.post(`/nodes/${nodeId}/config`, {
        config_key: key,
        config_value: value,
      });
      await this.fetchNodeConfig(nodeId);
    },

    async deleteNodeConfig(nodeId: string, key: string) {
      await posClient.delete(`/nodes/${nodeId}/config/${key}`);
      await this.fetchNodeConfig(nodeId);
    },

    async testCloudLink(id: number) {
      return posClient.post(`/config/cloud-links/${id}/test`);
    },

    async syncMasterConfig(id: number) {
      return posClient.post(`/config/master/${id}/sync`);
    },
  },
});
```

---

## 4. App Initialization

```typescript
// src/App.vue (or React equivalent)
import { posClient } from './stores/client';
import { useNodeStore } from './stores/nodes';
import { useSyncStore } from './stores/sync';
import { useApprovalStore } from './stores/approvals';
import { useConfigStore } from './stores/config';
import { useAuthStore } from './stores/auth';

export default {
  async mounted() {
    const auth = useAuthStore();

    // 1. Check health / auto-login
    const healthy = await posClient.healthCheck();
    if (!healthy) {
      console.warn('Sidecar not running - some features unavailable');
      return;
    }

    // 2. Auto-login if token stored
    const stored = localStorage.getItem('pos_device_token');
    if (stored) {
      posClient.setToken(stored);
      const { ok } = await posClient.get('/auth/verify');
      if (!ok) {
        // Token expired — try refresh
        const refreshed = await posClient.refreshToken();
        if (!refreshed) {
          // Need manual login
          auth.needsReauth = true;
        }
      }
    }

    // 3. Fetch initial data in parallel
    const nodes = useNodeStore();
    const sync = useSyncStore();
    const approvals = useApprovalStore();
    const config = useConfigStore();

    await Promise.all([
      nodes.fetchAll(),
      sync.fetchStatus(),
      sync.fetchLog(),
      approvals.fetchPending(),
      approvals.fetchStats(),
      config.fetchAll(),
    ]);

    // 4. Subscribe to real-time streams
    nodes.subscribeToEvents();
    sync.subscribeToConfig();
  },

  beforeUnmount() {
    const nodes = useNodeStore();
    const sync = useSyncStore();
    nodes.unsubscribe();
    sync.unsubscribe();
  },
};
```

---

## 5. React Hooks Version

For React (instead of Pinia), wrap stores as hooks:

```typescript
// src/hooks/useStores.ts
import { useState, useEffect, useCallback } from 'react';
import { posClient } from '../stores/client';

// Hook for node store
export function useNodes() {
  const [nodes, setNodes] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchAll = useCallback(async () => {
    setLoading(true);
    const { data } = await posClient.get('/nodes');
    if (data?.data) setNodes(data.data);
    setLoading(false);
  }, []);

  const register = useCallback(async (nodeData: any) => {
    return posClient.post('/nodes/register', nodeData);
  }, []);

  // WebSocket subscription
  useEffect(() => {
    const wsId = posClient.connectWs('/ws/nodes', (msg: any) => {
      if (msg.type === 'node_event') {
        // Update state
      }
    });
    return () => posClient.disconnectWs(wsId);
  }, []);

  return { nodes, loading, fetchAll, register };
}
```

---

## 6. API Endpoint Summary

| Store | HTTP Endpoints | WS Stream |
|-------|---------------|-----------|
| Nodes | `GET /nodes`, `POST /nodes/register`, `POST /nodes/heartbeat`, `PATCH/DELETE /nodes/:id` | `/ws/nodes` |
| Sync | `GET /sync/status`, `GET /sync/log`, `POST /sync/trigger`, `PATCH /sync/config` | `/ws/config` |
| Approvals | `GET /approvals/pending`, `GET /approvals/stats`, `POST /approvals/:id/approve\|reject` | `/ws/config` |
| Config | `GET/POST/PATCH/DELETE /config/devices\|master\|cloud-links`, `GET/POST/DELETE /nodes/:id/config` | `/ws/config` |
| Products | `GET/POST/PATCH/DELETE /products` | — |
| Sales | `GET/POST/PATCH/DELETE /sales`, `POST /sales/with-items` | — |
| Customers | `GET/POST/PATCH/DELETE /customers` | — |
| Auth | `POST /auth/token\|refresh`, `GET /auth/verify` | — |
| Events | `GET /events` | `/ws/nodes` |
