# Pro ↔ Cloud Sync Contract

> **Editions:** `formint/` (Pro) → `formint-cloud/` (Cloud)  
> **Last updated:** 2026-08-10  
> **Related docs:** [Editions](editions.md) · [Server v2](../SERVER_V2.md) · [Sync Architecture](../SYNC_ARCHITECTURE.md)

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Sync Paths (Dual-Transport)](#2-sync-paths-dual-transport)
3. [Terminal Registration & Identity](#3-terminal-registration--identity)
4. [REST Sync Push Endpoints (Pro → Cloud)](#4-rest-sync-push-endpoints-pro--cloud)
5. [WebSocket Protocol (Bidirectional)](#5-websocket-protocol-bidirectional)
6. [Data Shapes — Full Payload Schemas](#6-data-shapes--full-payload-schemas)
7. [Conflict Resolution Engine](#7-conflict-resolution-engine)
8. [Sync Queue & Delivery Guarantees](#8-sync-queue--delivery-guarantees)
9. [Error Handling](#9-error-handling)
10. [Sync Dashboard API](#10-sync-dashboard-api)
11. [Testing & Parity Contract](#11-testing--parity-contract)

---

## 1. Architecture Overview

```
┌──────────────────────────────────────┐       ┌─────────────────────────────────────────┐
│  formint/  (Pro — Desktop Terminal)  │       │  formint-cloud/  (Hosted SaaS Master)   │
│                                      │       │                                         │
│  Robyn Server :8766                 │       │  Django ASGI (daphne) :8767             │
│  ┌────────────────────────────────┐  │       │  ┌───────────────────────────────────┐  │
│  │ SyncClient (HTTP)              │──┼─ POST ─▶│ sync_api.py                        │  │
│  │  /sync/push/branch-data         │  │       │  /api/sync/receive/{products,        │  │
│  │  /sync/push/products|configs    │  │       │   sales, inventory, heartbeat}       │  │
│  │  /cloud/push/:entity_type       │  │       │  └──────────────┬────────────────────┘  │
│  └────────────────────────────────┘  │       │                 │                       │
│                                      │       │  ┌──────────────▼────────────────────┐  │
│  ┌────────────────────────────────┐  │       │  │ SyncQueue + SyncBroker           │  │
│  │ CloudSyncClient (WebSocket)    │──┼─ WSS ─▶│  │ Enqueue → Deliver → Retry        │  │
│  │  identify(branch_code,node_id)  │  │       │  │ Push to branch via broker         │  │
│  │  sync_push events               │  │       │  └──────────────┬────────────────────┘  │
│  │  ← broker_message (config/cat) │◀─┼─ WSS ──│                 │                       │
│  └────────────────────────────────┘  │       │  ┌──────────────▼────────────────────┐  │
│                                      │       │  │ ConflictResolutionEngine          │  │
│  ┌────────────────────────────────┐  │       │  │ LWW | TimestampVector | Manual    │  │
│  │ ProductSyncEngine              │  │       │  │ SyncConflict model                │  │
│  │  Approval workflow              │  │       │  └───────────────────────────────────┘  │
│  │  SyncLog audit trail            │  │       │                                         │
│  └────────────────────────────────┘  │       │  ┌───────────────────────────────────┐  │
│                                      │       │  │ SyncEventConsumer (Channels)       │  │
│  sync_state.json (config)           │       │  │  /ws/sync-events/                   │  │
│  ┌────────────────────────────────┐  │       │  │  Per-branch groups                 │  │
│  │ enabled, cloud_url, api_key,    │  │       │  │  sync_event → dashboards           │  │
│  │ last_sync, items_synced, errors │  │       │  │  broker_message → terminals        │  │
│  └────────────────────────────────┘  │       │  └───────────────────────────────────┘  │
└──────────────────────────────────────┘       └─────────────────────────────────────────┘
```

**Dual-transport design**: The Pro terminal uses two channels to talk to Cloud:

| Transport | Direction | Purpose |
|-----------|-----------|---------|
| **REST (HTTP POST)** | Pro → Cloud | Bulk data push — products, sales, inventory, heartbeats |
| **WebSocket (WSS)** | Pro ↔ Cloud | Real-time bidirectional — entity CRUD events, broker messages, config push-back |

---

## 2. Sync Paths (Dual-Transport)

### 2.1 REST Path (Pro → Cloud)

The Pro server's `SyncClient` (`routes/state.py`) wraps `httpx` to POST to the Cloud REST receivers. It is used for:

- **Scheduled bulk sync** — `POST /sync/push/branch-data` batches products, sales, inventory + heartbeat
- **On-demand cloud push** — `POST /cloud/push/:entity_type` for individual entity types
- **Product/config sync** — `POST /sync/push/products`, `POST /sync/push/configs`

### 2.2 WebSocket Path (Pro ↔ Cloud, Bidirectional)

The Pro server's `CloudSyncClient` (`ws_client.py`) maintains a persistent WebSocket to `/ws/sync-events/`. It:

- **Identifies** with `{type: "identify", payload: {branch_code, node_id}}`
- **Pushes** real-time entity CRUD events as `{type: "sync_push", payload: {entity_type, action, node_id, branch_code, timestamp, data, count}}`
- **Receives** broker messages pushed back from Cloud to this terminal's branch

The Cloud `SyncEventConsumer` (`handlers/consumers.py`) handles these connections.

---

## 3. Terminal Registration & Identity

### 3.1 Node Registration (REST)

A Pro terminal registers with Cloud by posting its node metadata.

**Pro side** (`routes/nodes.py`):
```
POST /nodes/register
```

**Request:**
```json
{
  "node_id": "pos-full-node-abc123",
  "hostname": "store-1-terminal",
  "node_type": "pos-full",
  "version": "0.1.0",
  "capabilities": {"sync": true, "kds": true, "inventory": true},
  "port": 8766
}
```

**Response (200):**
```json
{
  "status": "registered",
  "node_id": "pos-full-node-abc123",
  "first_seen": "2026-08-10T12:00:00+00:00"
}
```

### 3.2 Cloud Branch Matching

The Cloud sync receivers look up a `Branch` by `node_id`:

```python
# cloud/apps/handlers/sync_api.py
branch = Branch.objects.filter(node_id=node_id, is_active=True).first()
if not branch:
    return JsonResponse({"error": f"No active branch found for node_id={node_id}"}, status=404)
```

So a `Branch` must be pre-registered in Cloud with a matching `node_id` before sync data is accepted.

### 3.3 WebSocket Identity Handshake

On WebSocket connect, the Pro terminal identifies:

```
Pro → Cloud:
{
  "type": "identify",
  "payload": {
    "branch_code": "BR001",
    "node_id": "pos-full-node-abc123"
  }
}

Cloud → Pro:
{
  "type": "identify_ack",
  "branch_code": "BR001",
  "node_id": "pos-full-node-abc123",
  "status": "registered"
}
```

On receipt, the Cloud consumer:
1. Joins the `branch_{branch_code}` channel group for targeted pushes
2. Registers the connection with `SyncBroker` for health tracking
3. Broadcasts a `terminal_connected` sync_event to all dashboards

---

## 4. REST Sync Push Endpoints (Pro → Cloud)

All Cloud receivers are at `apps/handlers/sync_api.py`. They are `@csrf_exempt` and accept JSON `POST`.

### 4.1 Products

```
POST /api/sync/receive/products
```

**Request:**
```json
{
  "node_id": "pos-full-node-abc123",
  "products": [
    {
      "id": "prod-001",
      "name": "Espresso",
      "price": 3.50,
      "sku": "ESP-001",
      "category_name": "Hot Drinks",
      "stock_quantity": 250,
      "description": "Single shot espresso",
      "is_active": true
    }
  ]
}
```

**Response (200):**
```json
{
  "status": "received",
  "synced": 1,
  "branch": "Downtown Store"
}
```

**Behavior:**
- Looks up `Branch` by `node_id` → 404 if no active branch
- `BranchProduct.objects.update_or_create(branch, source_id)` per product
- Creates `BranchSyncLog(status="processed")`
- Broadcasts `sync_event` to dashboard group + `broker_message` to branch group

### 4.2 Sales

```
POST /api/sync/receive/sales
```

**Request:**
```json
{
  "node_id": "pos-full-node-abc123",
  "sales": [
    {
      "id": "sale-500",
      "customer_name": "Jane Doe",
      "total_amount": 24.50,
      "payment_method": "card",
      "sale_date": "2026-08-10T11:30:00Z",
      "item_count": 3,
      "items": [
        {"product_name": "Latte", "quantity": 2, "unit_price": 4.50},
        {"product_name": "Muffin", "quantity": 1, "unit_price": 3.50}
      ]
    }
  ]
}
```

**Response (200):**
```json
{
  "status": "received",
  "synced": 1,
  "branch": "Downtown Store"
}
```

**Field mapping:** `source_id` ← `sale.id`, `customer_name`, `total_amount`, `payment_method` (default `"cash"`), `sale_date` (default `now()`), `item_count`, `items` (raw JSON array).

### 4.3 Inventory

```
POST /api/sync/receive/inventory
```

**Request:**
```json
{
  "node_id": "pos-full-node-abc123",
  "transactions": [
    {
      "id": "inv-tx-100",
      "product_name": "Coffee Beans",
      "transaction_type": "addition",
      "quantity": 50,
      "notes": "Weekly restock",
      "transaction_date": "2026-08-10T08:00:00Z"
    }
  ]
}
```

**Field mapping:** `source_id` ← `tx.id`, `product_name`, `transaction_type` (default `"addition"`), `quantity` (default 0), `notes`, `transaction_date` (default `now()`).

### 4.4 Heartbeat

```
POST /api/sync/receive/heartbeat
```

**Request:**
```json
{
  "node_id": "pos-full-node-abc123",
  "status": "online",
  "product_count": 45,
  "sales_count": 128
}
```

**Response (200):**
```json
{
  "status": "received",
  "branch": "Downtown Store"
}
```

### 4.5 Bulk Branch Data (Pro composite endpoint)

The Pro server composites multiple pushes into one call:

```
POST /sync/push/branch-data
```

**Request:**
```json
{
  "node_id": "pos-full-node-abc123",
  "status": "online",
  "products": [...],
  "sales": [...],
  "inventory": [...]
}
```

Internally calls the Cloud receivers for each entity type sequentially.

### 4.6 Cloud Push Proxy

```
POST /cloud/push/:entity_type
```

Valid `entity_type` values: `nodes`, `heartbeats`, `events`, `products`, `sales`, `customers`, `inventory`.

Proxies to the configured Cloud CRM URL.

---

## 5. WebSocket Protocol (Bidirectional)

### 5.1 Endpoint

```
ws://<cloud-host>:8767/ws/sync-events/
```

Served by Daphne via `configs/asgi.py` → `SyncEventConsumer`.

### 5.2 Frame Types

#### Client → Cloud

| Frame `type` | Purpose |
|---|---|
| `identify` | Register with branch code + node ID |
| `sync_push` | Real-time entity CRUD event |
| `heartbeat` | Liveness ping |
| `ack` | Acknowledge receipt of a broker message |
| `custom:*` | Custom-namespaced message (e.g. `custom:inventory-check`) |

**sync_push frame:**
```json
{
  "type": "sync_push",
  "payload": {
    "entity_type": "products",
    "action": "create",
    "node_id": "pos-full-node-abc123",
    "branch_code": "BR001",
    "timestamp": "2026-08-10T12:00:00Z",
    "data": { "id": 42, "name": "Espresso", "price": 3.50 },
    "count": 1
  }
}
```

#### Cloud → Client

| Frame `type` | Purpose |
|---|---|
| `identify_ack` | Acknowledge client identity |
| `sync_event` | Dashboard broadcast (entity synced, terminal connected/disconnected) |
| `broker_message` | Targeted branch push (catalog update, config change, approval) |
| `error` | Error response |

**sync_event frame (dashboard broadcast):**
```json
{
  "entity_type": "products",
  "synced": 5,
  "branch": "Downtown Store",
  "node_id": "pos-full-node-abc123",
  "timestamp": "2026-08-10T12:00:00Z"
}
```

**broker_message frame (branch-targeted):**
```json
{
  "type": "broker_message",
  "message": {
    "type": "broker_message",
    "subtype": "entity_event",
    "payload": {
      "entity_type": "products",
      "action": "sync",
      "count": 5,
      "data": { "count": 5 }
    },
    "source_node_id": "cloud-server",
    "target_branch_code": "BR001",
    "message_id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2026-08-10T12:00:00Z"
  }
}
```

### 5.3 Channel Groups

| Group | Members | Purpose |
|-------|---------|---------|
| `sync_events` | All dashboard clients | Receives `sync_event` broadcasts (terminal connections, entity sync counts) |
| `sync_broadcast` | All connected clients | Global system messages |
| `branch_{code}` | All terminals of a branch | Targeted broker messages (catalog push, config, approvals) |

### 5.4 Echo Suppression

The `CloudSyncClient` on the Pro side checks `origin_node_id` in incoming messages and drops frames originating from itself, preventing echo loops.

---

## 6. Data Shapes — Full Payload Schemas

### 6.1 Pro-Side Models (Source)

#### Node (`full_nodes`)
| Field | Type | Notes |
|-------|------|-------|
| `node_id` | `str(100)` | Unique, required |
| `hostname` | `str(255)` | |
| `node_type` | `enum` | `pos-minimal`, `pos-solo`, `pos-full`, `custom` |
| `status` | `enum` | `online`, `offline`, `degraded`, `maintenance`, `unknown` |
| `version` | `str(50)` | |
| `is_active` | `bool` | Indexed |
| `product_count` | `int` | |
| `transaction_count` | `int` | |
| `customer_count` | `int` | |
| `capabilities` | `JSON` | |
| `metadata` | `JSON` | |
| `last_synced_at` | `datetime` | |

#### Heartbeat (`full_heartbeats`)
| Field | Type | Notes |
|-------|------|-------|
| `node_id` | `str(100)` | Indexed |
| `status` | `str(20)` | |
| `payload` | `JSON` | |
| `latency_ms` | `float` | |
| `received_at` | `datetime` | Indexed |
| `is_synced` | `bool` | For cloud sync tracking |

#### SyncLog (`full_sync_logs`)
| Field | Type | Notes |
|-------|------|-------|
| `node_id` | `str(100)` | Indexed |
| `entity_type` | `str(50)` | |
| `direction` | `enum` | `push`, `pull` |
| `status` | `enum` | `pending`, `in_progress`, `success`, `failed` |
| `payload_size` | `int` | |
| `error_message` | `text` | |
| `retry_count` | `int` | |

#### SyncApproval (`pos_sync_approvals`)
| Field | Type | Notes |
|-------|------|-------|
| `node_id` | `str(100)` | Indexed |
| `entity_type` | `enum` | `sale`, `product`, `config`, `report`, `inventory`, `customer`, `employee`, `category`, `sync`, `other` |
| `change_data` | `JSON` | Full payload |
| `status` | `enum` | `pending`, `approved`, `rejected`, `applied`, `failed` |
| `reviewed_by` | `str(100)` | |
| `review_notes` | `text` | |
| `direction` | `enum` | `push`, `pull`, `sync` |

### 6.2 Cloud-Side Models (Target)

#### BranchProduct (`pos_cloud.db`)
| Field | Type | Indexed |
|-------|------|---------|
| `branch` | FK→Branch | ✓ |
| `source_id` | `str` | ✓ (composite with branch) |
| `name` | `str` | |
| `price` | `decimal` | |
| `sku` | `str` | |
| `category_name` | `str` | |
| `stock_quantity` | `int` | |
| `is_active` | `bool` | |

#### BranchSale (`pos_cloud.db`)
| Field | Type |
|-------|------|
| `branch` | FK→Branch |
| `source_id` | `str` |
| `customer_name` | `str` |
| `total_amount` | `decimal` |
| `payment_method` | `str` |
| `sale_date` | `datetime` |
| `item_count` | `int` |
| `items` | `JSON` |

#### BranchInventory (`pos_cloud.db`)
| Field | Type |
|-------|------|
| `branch` | FK→Branch |
| `source_id` | `str` |
| `product_name` | `str` |
| `transaction_type` | `str` (`addition`/`removal`/`adjustment`/`transfer`) |
| `quantity` | `int` |
| `notes` | `str` |
| `transaction_date` | `datetime` |

#### BranchSyncLog (`pos_cloud.db`)
| Field | Type |
|-------|------|
| `branch` | FK→Branch |
| `node_id` | `str` |
| `entity_type` | `str` |
| `entity_count` | `int` |
| `status` | `str` (`received`, `processed`, `failed`) |
| `payload` | `JSON` |
| `received_at` | `datetime` (auto) |

#### SyncConflict (`pos_cloud.db`)
| Field | Type |
|-------|------|
| `branch` | FK→Branch |
| `entity_type` | `str` |
| `entity_id` | `str` |
| `local_data` | `JSON` |
| `remote_data` | `JSON` |
| `conflict_fields` | `JSON` |
| `resolver_used` | `str` |
| `resolution` | `str` (`use_local`, `use_remote`, `merge`, `manual`) |
| `resolved_at` | `datetime` |

#### SyncQueueItem (`pos_cloud.db`)
| Field | Type |
|-------|------|
| `branch` | FK→Branch |
| `entity_type` | `str` |
| `operation` | `str` (`create`, `update`, `delete`) |
| `payload` | `JSON` |
| `idempotency_key` | `str(64)` |
| `status` | `enum` (`pending`, `delivering`, `delivered`, `failed`, `cancelled`) |
| `attempt_count` | `int` |
| `max_attempts` | `int` (default 5) |
| `next_retry_at` | `datetime` |
| `last_error` | `str` |

---

## 7. Conflict Resolution Engine

### 7.1 Resolution Strategies

| Strategy | Class | Behavior |
|----------|-------|----------|
| **Last-Write-Wins** | `LastWriteWinsResolver` | Most recent `updated_at` wins. Default for most entities. |
| **Timestamp Vector** | `TimestampVectorResolver` | Lamport vectors detect true causal conflicts. Field-level merge. |
| **Manual** | `ManualResolver` | Always flags for human review. Never auto-resolves. |

### 7.2 Per-Entity Strategy Assignments

```python
# conflict_resolver.py — singleton defaults
{
    "products":   LastWriteWinsResolver(),   # Most recent catalog wins
    "sales":      LastWriteWinsResolver(),   # Immutable after creation
    "customers":  LastWriteWinsResolver(),
    "employees":  LastWriteWinsResolver(),
    "categories": LastWriteWinsResolver(),
    "inventory":  TimestampVectorResolver(), # Preserve concurrent adjustments
    "config":     ManualResolver(),          # Must be reviewed
    "prices":     ManualResolver(),          # Must be reviewed
}
```

### 7.3 Resolution Actions

| Action | Meaning |
|--------|---------|
| `use_local` | Keep cloud version, discard branch |
| `use_remote` | Accept branch version, update cloud |
| `merge` | Field-level merge with conflict list |
| `flag_manual` | Persist to `SyncConflict`, wait for human |

### 7.4 Conflict Flow

```
Branch A pushes Product #42  ──►  Cloud detects version mismatch
Branch B pushes Product #42  ──►
                                      │
                              ┌───────▼────────┐
                              │ Conflict Engine │
                              │ resolve(local,  │
                              │   remote)       │
                              └───────┬────────┘
                                      │
                         ┌────────────┼────────────┐
                         │            │            │
                    use_remote    merge       flag_manual
                         │            │            │
                   Update DB    Apply merge   Create SyncConflict
                                List conflicts  Show in dashboard
```

---

## 8. Sync Queue & Delivery Guarantees

### 8.1 At-Least-Once Delivery

The `SyncQueue` (`domain/sync_queue.py`) provides durable at-least-once delivery for cloud→branch operations.

### 8.2 Idempotency

Each queue item has an `idempotency_key = sha256(branch_id|operation|entity_type|json(payload))`. Duplicate enqueues with the same key are silently ignored.

### 8.3 Exponential Backoff

| Attempt | Delay |
|---------|-------|
| 1 | 5s |
| 2 | 10s |
| 3 | 20s |
| 4 | 40s |
| 5 | 80s |
| Exceeded | Status → `failed` |

### 8.4 Delivery Flow

```
enqueue(item)
    │
    ▼
┌──────────┐    branch online?    ┌───────────┐
│ PENDING  │─────────────────────▶│ DELIVERING │
└──────────┘   broker.push_to_    └─────┬─────┘
       ▲          branch()             │
       │                               │
       │ retry (backoff)          ┌────▼────┐
       │                         │ DELIVERED│
       │                         └─────────┘
       │
       │ max_attempts exceeded
       ▼
   ┌────────┐
   │ FAILED │
   └────────┘
       │
       │ manual retry via
       │ sync_queue.retry_item(id)
       ▼
   PENDING (reset)
```

### 8.5 Serial Processing

`select_for_update(skip_locked=True)` ensures per-branch sequential processing. No two workers process the same queue item.

### 8.6 WebSocket Fast-Path

If the target branch has an active WebSocket, items are delivered immediately via `broker.push_to_branch()`. Otherwise they wait for the next polling cycle (`process_pending_items`).

---

## 9. Error Handling

### 9.1 HTTP Status Codes

| Status | Condition |
|--------|-----------|
| `200` | Sync data received and processed |
| `400` | Invalid JSON body (malformed) |
| `404` | No active `Branch` found for the given `node_id` |
| `500` | Unhandled server error (logged) |

### 9.2 Sync State on Pro

Pro maintains `sync_state.json`:

```json
{
  "enabled": true,
  "cloud_url": "http://<cloud>:8767",
  "api_key": "",
  "last_sync": "2026-08-10T12:00:00+00:00",
  "status": "idle",
  "items_synced": 245,
  "errors": 3,
  "last_error": "All connection attempts failed"
}
```

This is read at startup, updated on every sync, and surfaced at `GET /sync/status`.

### 9.3 Error Recovery Patterns

1. **HTTP push fails** → SyncLog created with `status=failed` + `error_message`. Retry on next scheduler cycle.
2. **WebSocket disconnect** → `CloudSyncClient` reconnects with exponential backoff (max 60s). Offline queue buffers up to 1000 messages.
3. **Branch not found (404)** → Pro logs the error. Sync for that node is skipped. Admin must register the branch in Cloud.
4. **Queue item exhausted** → Status → `failed`. Surfaced in sync dashboard. Manual retry via `POST /api/dashboard/queue/retry/{id}`.

### 9.4 WebSocket Error Frame

```json
{
  "type": "error",
  "payload": {
    "message": "Missing branch_code in identify message"
  }
}
```

---

## 10. Sync Dashboard API

The Cloud sync dashboard (`apps/handlers/sync_dashboard.py`) exposes:

### 10.1 Branch Health

```
GET /api/dashboard/branches/health
```

```json
{
  "branches": [
    {
      "name": "Downtown Store",
      "code": "BR001",
      "node_id": "pos-full-node-abc123",
      "online": true,
      "connected_terminals": 2,
      "pos_type": "formint-pos",
      "is_active": true
    }
  ]
}
```

### 10.2 Queue Summary

```
GET /api/dashboard/queue/summary
```

```json
{
  "pending": 5,
  "failed": 1,
  "delivered": 120,
  "cancelled": 0,
  "estimated_backlog_seconds": 25
}
```

### 10.3 Queue Management

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/queue/by-branch` | GET | Queue items grouped by branch |
| `/queue/list/{status}` | GET | Filter by status |
| `/queue/retry/{id}` | POST | Reset failed item to pending |
| `/queue/cancel/{id}` | POST | Cancel pending item |

### 10.4 Conflict Management

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/conflicts` | GET | List pending conflicts |
| `/conflicts/stats` | GET | Count by entity type |
| `/conflicts/{id}/resolve` | POST | Resolve with `{resolution: "use_local"|"use_remote"|"merge"}` |
| `/conflicts/{id}/dismiss` | POST | Dismiss (no action) |

### 10.5 Recent Activity

```
GET /api/dashboard/activity?limit=50
```

Returns recent `BranchSyncLog` entries sorted by `received_at`.

---

## 11. Testing & Parity Contract

### 11.1 Backend Parity Tests

**Cloud side:** `backend/apps/test_ws_parity_contract.py`

Pins the exact WebSocket frame shapes:
- `identify_ack` — exact key set `{type, branch_code, node_id, status}`
- `sync_event` — raw payload shape `{entity_type, synced, branch, node_id, timestamp}`
- `broker_message` — outer envelope `{type, message}` wrapping `BrokerMessage.to_dict()`
- `error` frame — `{type, payload: {message}}`

### 11.2 Live Stack Verification

```
make verify-stack    # from formint-cloud/
```

Boots both Django roads (`:8767` daphne, `:8082` runserver), sweeps all ~60 endpoints, runs full WS frame-exchange parity (connect → identify → push → assert shapes).

### 11.3 Pro-Side Sync Tests

**Pro side:** `server/tests/test_data_sync.py`
- `TestModelParity` (6 tests) — validates data model alignment
- `TestRealCrossORM` (12 tests, skipped without Rust DB) — end-to-end cross-ORM validation

### 11.4 Contract Test Checklist

When modifying the sync contract, update:

- [ ] Cloud receiver request/response handlers (`sync_api.py`)
- [ ] Pro side sync push code (`routes/sync.py`, `ws_client.py`)
- [ ] WebSocket consumer frame handlers (`consumers.py`)
- [ ] Parity contract tests (`test_ws_parity_contract.py`)
- [ ] Stack verification script (`verify-stack.mjs`)
- [ ] This document (pro-cloud-sync-contract.md)
- [ ] editions.md (if adding new model fields)
