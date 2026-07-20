# Pinia ↔ Sidecar API Integration Guide

> **Version:** 1.0.0 — **Last Updated:** 20 July 2026
> **Applies to:** pos-solo (port 8765), pos-full (port 8766)

Complete guide for wiring Vue/Pinia stores to the Robyn sidecar REST + WebSocket APIs.

---

## 1. Quick Start

```typescript
// src/stores/sidecar.ts — base HTTP + WebSocket client
import { defineStore } from 'pinia'

export const useSidecar = defineStore('sidecar', {
  state: () => ({
    baseUrl: 'http://localhost:8765',
    token: null as string | null,
    wsConnected: false,
  }),

  getters: {
    headers(): Record<string, string> {
      const h: Record<string, string> = {
        'Content-Type': 'application/json',
        Accept: 'application/json',
      }
      if (this.token) h['Authorization'] = `Bearer ${this.token}`
      return h
    },
  },

  actions: {
    setToken(t: string | null) {
      this.token = t
      localStorage.setItem('pos_token', t || '')
    },

    async get<T>(path: string): Promise<{ data: T | null; error: string | null }> {
      try {
        const r = await fetch(`${this.baseUrl}${path}`, { headers: this.headers })
        if (!r.ok) return { data: null, error: `HTTP ${r.status}` }
        return { data: await r.json(), error: null }
      } catch (e) {
        return { data: null, error: String(e) }
      }
    },

    async post<T>(path: string, body: unknown) {
      const r = await fetch(`${this.baseUrl}${path}`, {
        method: 'POST', headers: this.headers, body: JSON.stringify(body),
      })
      return { data: r.ok ? await r.json() : null, error: r.ok ? null : `HTTP ${r.status}` }
    },

    async patch<T>(path: string, body: unknown) {
      const r = await fetch(`${this.baseUrl}${path}`, {
        method: 'PATCH', headers: this.headers, body: JSON.stringify(body),
      })
      return { data: r.ok ? await r.json() : null, error: r.ok ? null : `HTTP ${r.status}` }
    },

    async del(path: string) {
      const r = await fetch(`${this.baseUrl}${path}`, {
        method: 'DELETE', headers: this.headers,
      })
      return { ok: r.ok, error: r.ok ? null : `HTTP ${r.status}` }
    },

    async healthCheck(): Promise<boolean> {
      const { data } = await this.get('/health')
      return data?.status === 'ok'
    },
  },
})
```

---

## 2. Endpoint → Store Map

### 2.1 Products Store

```typescript
// src/stores/products.ts
import { defineStore } from 'pinia'
import { useSidecar } from './sidecar'

interface Product {
  id: number; name: string; price: number; sku?: string
  category_id?: number; stock_quantity: number
  is_active: boolean; created_at: string; updated_at: string
}

export const useProductStore = defineStore('products', {
  state: () => ({
    items: [] as Product[],
    loading: false,
    pagination: { page: 1, per_page: 50, total: 0, total_pages: 0 },
  }),

  actions: {
    async fetchAll(page = 1) {
      this.loading = true
      const { data } = await useSidecar().get(`/products?page=${page}&per_page=50`)
      if (data) {
        this.items = data.data
        this.pagination = data.pagination
      }
      this.loading = false
    },

    async getById(id: number) {
      return (await useSidecar().get<Product>(`/products/${id}`)).data
    },

    async create(product: Partial<Product>) {
      return useSidecar().post('/products', product)
    },

    async update(id: number, product: Partial<Product>) {
      return useSidecar().patch(`/products/${id}`, product)
    },

    async remove(id: number) {
      return useSidecar().del(`/products/${id}`)
    },
  },
})
```

| Store Method | HTTP | Endpoint |
|-------------|------|----------|
| `fetchAll()` | GET | `/products?page=1&per_page=50` |
| `getById(id)` | GET | `/products/:id` |
| `create(p)` | POST | `/products` |
| `update(id, p)` | PATCH | `/products/:id` |
| `remove(id)` | DELETE | `/products/:id` |

### 2.2 Sales Store

```typescript
// src/stores/sales.ts
interface Sale {
  id: number; customer_id?: number; sale_date: string
  subtotal: number; tax_amount: number; discount_amount: number
  total: number; payment_method: string; status: string
}

interface SaleItem {
  id: number; sale_id: number; product_name: string
  quantity: number; unit_price: number; line_total: number
}

export const useSaleStore = defineStore('sales', {
  state: () => ({
    sales: [] as Sale[],
    loading: false,
  }),

  actions: {
    async fetchAll(page = 1) {
      this.loading = true
      const { data } = await useSidecar().get(`/sales?page=${page}`)
      if (data) this.sales = data.data
      this.loading = false
    },

    async createWithItems(sale: Partial<Sale>, items: Partial<SaleItem>[]) {
      return useSidecar().post('/sales/with-items', { ...sale, items })
    },

    async getById(id: number) {
      return (await useSidecar().get<Sale>(`/sales/${id}`)).data
    },

    async refund(id: number) {
      return useSidecar().patch(`/sales/${id}`, { status: 'refunded' })
    },
  },
})
```

| Store Method | HTTP | Endpoint |
|-------------|------|----------|
| `fetchAll()` | GET | `/sales?page=1` |
| `createWithItems()` | POST | `/sales/with-items` |
| `getById(id)` | GET | `/sales/:id` |
| `refund(id)` | PATCH | `/sales/:id` |

### 2.3 Customers Store

```typescript
// src/stores/customers.ts
interface Customer {
  id: number; first_name: string; last_name: string
  email?: string; phone: string; loyalty_points: number
  total_spent: number; is_active: boolean
}

export const useCustomerStore = defineStore('customers', {
  state: () => ({ items: [] as Customer[], loading: false }),

  actions: {
    async fetchAll(page = 1) {
      this.loading = true
      const { data } = await useSidecar().get(`/customers?page=${page}`)
      if (data) this.items = data.data
      this.loading = false
    },
    async create(c: Partial<Customer>) { return useSidecar().post('/customers', c) },
    async update(id: number, c: Partial<Customer>) { return useSidecar().patch(`/customers/${id}`, c) },
    async remove(id: number) { return useSidecar().del(`/customers/${id}`) },
  },
})
```

### 2.4 Inventory Store

```typescript
// src/stores/inventory.ts
interface InventoryTransaction {
  id: number; product_id: number; transaction_type: 'in' | 'out' | 'adjustment' | 'return'
  quantity: number; reference: string; notes: string
}

export const useInventoryStore = defineStore('inventory', {
  state: () => ({ transactions: [] as InventoryTransaction[], loading: false }),

  actions: {
    async fetchAll(page = 1) {
      const { data } = await useSidecar().get(`/inventory?page=${page}`)
      if (data) this.transactions = data.data
    },
    async stockIn(productId: number, qty: number, ref = '') {
      return useSidecar().post('/inventory', {
        product_id: productId, transaction_type: 'in', quantity: qty, reference: ref,
      })
    },
    async stockOut(productId: number, qty: number, ref = '') {
      return useSidecar().post('/inventory', {
        product_id: productId, transaction_type: 'out', quantity: qty, reference: ref,
      })
    },
  },
})
```

| Store Method | HTTP | Endpoint |
|-------------|------|----------|
| `fetchAll()` | GET | `/inventory?page=1` |
| `stockIn()` | POST | `/inventory` |
| `stockOut()` | POST | `/inventory` |

### 2.5 Employees Store

```typescript
// src/stores/employees.ts
interface Employee {
  id: number; first_name: string; last_name: string
  email?: string; phone: string; role: string
  pin_code: string; is_active: boolean; hourly_rate: number
}

export const useEmployeeStore = defineStore('employees', {
  state: () => ({ items: [] as Employee[] }),
  actions: {
    async fetchAll() {
      const { data } = await useSidecar().get('/employees')
      if (data) this.items = data.data
    },
    async create(e: Partial<Employee>) { return useSidecar().post('/employees', e) },
    async deactivate(id: number) { return useSidecar().patch(`/employees/${id}`, { is_active: false }) },
    async remove(id: number) { return useSidecar().del(`/employees/${id}`) },
  },
})
```

| Store Method | HTTP | Endpoint |
|-------------|------|----------|
| `fetchAll()` | GET | `/employees` |
| `create(e)` | POST | `/employees` |
| `deactivate(id)` | PATCH | `/employees/:id` |
| `remove(id)` | DELETE | `/employees/:id` |

### 2.6 Categories Store

| Store Method | HTTP | Endpoint |
|-------------|------|----------|
| `fetchAll()` | GET | `/categories` |
| `create(c)` | POST | `/categories` |
| `update(id, c)` | PATCH | `/categories/:id` |
| `remove(id)` | DELETE | `/categories/:id` |

### 2.7 Node Registry Store

```typescript
// src/stores/nodes.ts
interface Node {
  node_id: string; hostname: string; node_type: string
  version: string; status: string; is_active: boolean
  product_count: number; transaction_count: number
  ip_address?: string; port?: number
  first_seen: string; last_seen: string; last_synced_at?: string
}

export const useNodeStore = defineStore('nodes', {
  state: () => ({
    nodes: [] as Node[],
    events: [] as any[],
    wsConnected: false,
    ws: null as WebSocket | null,
  }),

  getters: {
    online: (s) => s.nodes.filter((n) => n.status === 'online'),
    offline: (s) => s.nodes.filter((n) => n.status === 'offline'),
    count: (s) => s.nodes.length,
  },

  actions: {
    async fetchAll(page = 1) {
      const { data } = await useSidecar().get(`/nodes?page=${page}`)
      if (data) this.nodes = data.data
    },

    async register(node: Partial<Node>) {
      return useSidecar().post('/nodes/register', node)
    },

    async heartbeat(nodeId: string) {
      return useSidecar().post('/nodes/heartbeat', { node_id: nodeId })
    },

    async update(nodeId: string, updates: Partial<Node>) {
      return useSidecar().patch(`/nodes/${nodeId}`, updates)
    },

    async remove(nodeId: string) {
      return useSidecar().del(`/nodes/${nodeId}`)
    },

    async getHistory(nodeId: string) {
      return (await useSidecar().get(`/nodes/${nodeId}/history`)).data
    },

    // WebSocket (pos-full only)
    connectNodeStream(filters?: { node_id?: string; event_type?: string }) {
      const url = `${useSidecar().baseUrl.replace('http', 'ws')}/ws/nodes`
      this.ws = new WebSocket(url)
      this.ws.onopen = () => { this.wsConnected = true }
      this.ws.onmessage = (e) => {
        const msg = JSON.parse(e.data)
        if (msg.type === 'node_event') {
          const idx = this.nodes.findIndex((n) => n.node_id === msg.node_id)
          if (idx >= 0) Object.assign(this.nodes[idx], msg.data)
          else if (msg.event === 'registered') this.nodes.push(msg.data)
          this.events.push(msg)
        }
      }
      this.ws.onclose = () => { this.wsConnected = false }
      if (filters) this.ws.send(JSON.stringify({ filter: filters }))
    },

    disconnectStream() { this.ws?.close() },
  },
})
```

| Store Method | HTTP/WS | Endpoint |
|-------------|---------|----------|
| `fetchAll()` | GET | `/nodes` |
| `register(node)` | POST | `/nodes/register` |
| `heartbeat(id)` | POST | `/nodes/heartbeat` |
| `update(id, u)` | PATCH | `/nodes/:node_id` |
| `remove(id)` | DELETE | `/nodes/:node_id` |
| `getHistory(id)` | GET | `/nodes/:node_id/history` |
| `connectNodeStream()` | WS | `/ws/nodes` (Full only) |

### 2.8 Configuration Store

```typescript
// src/stores/config.ts
interface DeviceConfig {
  id: number; node_id: string; config_key: string
  config_value: any; category: string; version: number
}

interface CloudLink {
  id: number; name: string; cloud_url: string
  status: string; is_primary: boolean; sync_interval: number
  last_sync_at?: string
}

export const useConfigStore = defineStore('config', {
  state: () => ({
    devices: [] as DeviceConfig[],
    masters: [] as any[],
    cloudLinks: [] as CloudLink[],
    wsConnected: false,
    ws: null as WebSocket | null,
  }),

  actions: {
    async fetchDevices() {
      const { data } = await useSidecar().get('/config/devices')
      if (data) this.devices = data.data
    },

    async getNodeConfig(nodeId: string) {
      return (await useSidecar().get(`/nodes/${nodeId}/config`)).data
    },

    async setNodeConfig(nodeId: string, key: string, value: any) {
      return useSidecar().post(`/nodes/${nodeId}/config`, { config_key: key, config_value: value })
    },

    async deleteNodeConfig(nodeId: string, key: string) {
      return useSidecar().del(`/nodes/${nodeId}/config/${key}`)
    },

    async fetchCloudLinks() {
      const { data } = await useSidecar().get('/config/cloud-links')
      if (data) this.cloudLinks = data.data
    },

    async testCloudLink(id: number) {
      return useSidecar().post(`/config/cloud-links/${id}/test`, {})
    },

    // WebSocket config stream (both editions)
    connectConfigStream() {
      const url = `${useSidecar().baseUrl.replace('http', 'ws')}/ws/config`
      this.ws = new WebSocket(url)
      this.ws.onopen = () => { this.wsConnected = true }
      this.ws.onmessage = (e) => {
        const msg = JSON.parse(e.data)
        if (msg.type === 'config_event') {
          // Re-fetch affected configs
          if (msg.event === 'config_changed') this.fetchDevices()
          if (msg.event === 'cloud_link_changed') this.fetchCloudLinks()
        }
      }
      this.ws.onclose = () => { this.wsConnected = false }
    },
  },
})
```

| Store Method | HTTP/WS | Endpoint |
|-------------|---------|----------|
| `fetchDevices()` | GET | `/config/devices` |
| `getNodeConfig(id)` | GET | `/nodes/:node_id/config` |
| `setNodeConfig(id, k, v)` | POST | `/nodes/:node_id/config` |
| `deleteNodeConfig(id, k)` | DELETE | `/nodes/:node_id/config/:key` |
| `fetchCloudLinks()` | GET | `/config/cloud-links` |
| `testCloudLink(id)` | POST | `/config/cloud-links/:id/test` |
| `connectConfigStream()` | WS | `/ws/config` |

### 2.9 Sync Store

```typescript
// src/stores/sync.ts
export const useSyncStore = defineStore('sync', {
  state: () => ({
    status: 'idle' as string,
    enabled: true,
    cloudUrl: '',
    lastSync: null as string | null,
    itemsSynced: 0,
    errors: 0,
    log: [] as any[],
  }),

  actions: {
    async fetchStatus() {
      const { data } = await useSidecar().get('/sync/status')
      if (data) Object.assign(this, data)
    },

    async triggerSync() {
      return useSidecar().post('/sync/trigger', {})
    },

    async fetchLog(page = 1) {
      const { data } = await useSidecar().get(`/sync/log?page=${page}`)
      if (data) this.log = data.data
    },

    async updateConfig(config: { enabled?: boolean; cloud_url?: string; api_key?: string }) {
      return useSidecar().patch('/sync/config', config)
    },

    async pushToCloud(entityType: string, payload: any) {
      return useSidecar().post(`/cloud/push/${entityType}`, payload)
    },
  },
})
```

| Store Method | HTTP | Endpoint |
|-------------|------|----------|
| `fetchStatus()` | GET | `/sync/status` |
| `triggerSync()` | POST | `/sync/trigger` |
| `fetchLog()` | GET | `/sync/log` |
| `updateConfig(c)` | PATCH | `/sync/config` |
| `pushToCloud(t, p)` | POST | `/cloud/push/:type` |

### 2.10 Approvals Store

```typescript
// src/stores/approvals.ts
interface Approval {
  id: number; entity_type: string; entity_id: string
  status: 'pending' | 'approved' | 'rejected' | 'applied'
  reviewer?: string; notes?: string; created_at: string
}

export const useApprovalStore = defineStore('approvals', {
  state: () => ({
    pending: [] as Approval[],
    stats: { pending: 0, approved: 0, rejected: 0, applied: 0 },
  }),

  actions: {
    async fetchPending() {
      const { data } = await useSidecar().get('/approvals/pending')
      if (data) this.pending = data
    },

    async fetchStats() {
      const { data } = await useSidecar().get('/approvals/stats')
      if (data) this.stats = data
    },

    async approve(id: number, reviewer = 'manager', notes = '') {
      return useSidecar().post(`/approvals/${id}/approve`, { reviewer, notes })
    },

    async reject(id: number, reviewer = 'manager', notes = '') {
      return useSidecar().post(`/approvals/${id}/reject`, { reviewer, notes })
    },

    async all() {
      const { data } = await useSidecar().get('/approvals')
      return data?.data || []
    },
  },
})
```

| Store Method | HTTP | Endpoint |
|-------------|------|----------|
| `fetchPending()` | GET | `/approvals/pending` |
| `fetchStats()` | GET | `/approvals/stats` |
| `approve(id)` | POST | `/approvals/:id/approve` |
| `reject(id)` | POST | `/approvals/:id/reject` |
| `all()` | GET | `/approvals` |

### 2.11 Auth Store

```typescript
// src/stores/auth.ts
export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: null as string | null,
    deviceId: null as string | null,
    role: 'cashier' as string,
    isAuthenticated: false,
  }),

  actions: {
    async login(deviceId: string, role = 'cashier') {
      const { data } = await useSidecar().post('/auth/token', { device_id: deviceId, role })
      if (data?.token) {
        this.token = data.token
        this.deviceId = deviceId
        this.role = role
        this.isAuthenticated = true
        useSidecar().setToken(data.token)
      }
      return data
    },

    async refresh() {
      if (!this.token) return
      const { data } = await useSidecar().post('/auth/refresh', { token: this.token })
      if (data?.token) {
        this.token = data.token
        useSidecar().setToken(data.token)
      }
    },

    async verify() {
      const { data } = await useSidecar().get('/auth/verify')
      return data?.valid === true
    },

    logout() {
      this.token = null
      this.isAuthenticated = false
      useSidecar().setToken(null)
    },
  },
})
```

| Store Method | HTTP | Endpoint |
|-------------|------|----------|
| `login(id, role)` | POST | `/auth/token` |
| `refresh()` | POST | `/auth/refresh` |
| `verify()` | GET | `/auth/verify` |
| `logout()` | — | Local only |

### 2.12 Dashboard / Stats Store

```typescript
// src/stores/dashboard.ts
export const useDashboardStore = defineStore('dashboard', {
  state: () => ({
    stats: null as any,
    health: null as any,
    serviceInfo: null as any,
  }),

  actions: {
    async fetchAll() {
      const [info, health, stats] = await Promise.all([
        useSidecar().get('/'),
        useSidecar().get('/health'),
        useSidecar().get('/stats'),
      ])
      this.serviceInfo = info.data
      this.health = health.data
      this.stats = stats.data
    },
  },
})
```

| Store Method | HTTP | Endpoint |
|-------------|------|----------|
| `fetchAll()` | GET | `/`, `/health`, `/stats` |

---

## 3. WebSocket Connection Lifecycle

```
Pinia Store                    Sidecar WS
     │                              │
     ├── connectNodeStream() ──────►│  new WebSocket(url)
     │                              │
     │◄── onopen ──────────────────┤  wsConnected = true
     │                              │
     ├── send({ filter }) ─────────►│  _ws_filters[id] = filter
     │◄── { type: "filter_updated" }─┤
     │                              │
     │      ... event occurs ...     │
     │◄── { type: "node_event",    ─┤  _broadcast_node_event()
     │      event, node_id, data,    │
     │      timestamp }              │
     │                              │
     ├── disconnectStream() ───────►│  ws.close()
     │◄── onclose ─────────────────┤  wsConnected = false
```

**Reconnection strategy:**

```typescript
// src/utils/wsManager.ts
class WsManager {
  private conns = new Map<string, { ws: WebSocket; retries: number }>()

  connect(url: string, onMessage: (data: any) => void, maxRetries = 5) {
    const ws = new WebSocket(url)
    this.conns.set(url, { ws, retries: 0 })

    ws.onmessage = (e) => { try { onMessage(JSON.parse(e.data)) } catch {} }

    ws.onclose = () => {
      const entry = this.conns.get(url)
      if (entry && entry.retries < maxRetries) {
        entry.retries++
        const delay = Math.min(1000 * 2 ** entry.retries, 30000)
        setTimeout(() => this.connect(url, onMessage, maxRetries), delay)
      }
    }
    return ws
  }

  disconnect(url: string) {
    this.conns.get(url)?.ws.close()
    this.conns.delete(url)
  }
}

export const wsManager = new WsManager()
```

---

## 4. Auth Flow

```
1. Device starts → POST /auth/token { device_id, role }
2. Receives { token: "abc123...", expires_at, device_id, role }
3. Stores token in Pinia + localStorage
4. All subsequent requests: Authorization: Bearer abc123...
5. Before expiry: POST /auth/refresh { token }
6. On 401: re-login via /auth/token
```

**Token structure (from DeviceToken model):**

```typescript
interface DeviceToken {
  token_hash: string    // SHA-256 of raw token
  device_id: string     // e.g., "POS-REG-001"
  role: string          // admin | manager | cashier | viewer
  is_active: boolean
  expires_at: string    // ISO 8601
  last_used_at: string
  created_at: string
}
```

**Role permissions:**

| Role | Products | Sales | Config | Nodes | Approvals | Admin |
|------|----------|-------|--------|-------|-----------|-------|
| admin | RW | RW | RW | RW | RW | RW |
| manager | RW | RW | R | R | RW | — |
| cashier | R | RW | — | — | — | — |
| viewer | R | R | R | R | — | — |

---

## 5. Complete Store Index

```typescript
// src/stores/index.ts
export { useSidecar } from './sidecar'
export { useProductStore } from './products'
export { useSaleStore } from './sales'
export { useCustomerStore } from './customers'
export { useInventoryStore } from './inventory'
export { useEmployeeStore } from './employees'
export { useNodeStore } from './nodes'
export { useConfigStore } from './config'
export { useSyncStore } from './sync'
export { useApprovalStore } from './approvals'
export { useAuthStore } from './auth'
export { useDashboardStore } from './dashboard'
export { wsManager } from '../utils/wsManager'
```

---

## 6. App Initialization

```typescript
// src/App.vue or main.ts
import { useSidecar, useAuthStore, useNodeStore, useConfigStore } from '@/stores'

async function initializeApp() {
  const sidecar = useSidecar()

  // 1. Health check
  const healthy = await sidecar.healthCheck()
  if (!healthy) { console.error('Sidecar unreachable'); return }

  // 2. Auth (if token exists, verify; otherwise login)
  const auth = useAuthStore()
  const savedToken = localStorage.getItem('pos_token')
  if (savedToken) {
    sidecar.setToken(savedToken)
    const valid = await auth.verify()
    if (!valid) await auth.login('DEVICE-001', 'cashier')
  } else {
    await auth.login('DEVICE-001', 'cashier')
  }

  // 3. Connect WebSocket streams
  const nodes = useNodeStore()
  nodes.connectNodeStream()  // Full edition only

  const config = useConfigStore()
  config.connectConfigStream()

  // 4. Fetch initial data
  await Promise.all([
    nodes.fetchAll(),
    config.fetchDevices(),
    config.fetchCloudLinks(),
  ])
}
```
