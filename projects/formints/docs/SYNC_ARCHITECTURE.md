# POS Sync Architecture

> **Version:** 1.0.0  
> **Last Updated:** 24 July 2026  
> **Editions:** pos-mini (none), pos-solo (LAN), pos-full (Cloud), pos-cloud (SaaS)  
> **Related:** [Role System](ROLE_SYSTEM.md), [Architecture Overview](POS_ARCHITECTURE.md)

---

## 1. Three-Tier Sync Model

```
Tier 1: pos-mini ───→ Air-Gapped Standalone (No Sync)
Tier 2: pos-solo ───→ LAN Branch-to-Master Sync  (NEW)
Tier 3: pos-full ───→ Cloud-Synced Enterprise     (Existing + Enhancements)
```

---

## 2. Tier 1: pos-mini — Air-Gapped Standalone

### Design Principle
Single-device POS for small shops, food trucks, kiosks. **No sync capability** — all data stays local.

### What Exists
- Full database export/import via Settings → Database tab
- SQLite file-based storage
- Backup scheduling (planned)

### Future Enhancements
- USB/SD card bulk data transfer (file exchange)
- Print-based reporting (no digital sync)
- Backup reminders in Settings

---

## 3. Tier 2: pos-solo — LAN Branch-to-Master Sync

### Architecture

```
┌───────────────────┐     LAN/WiFi      ┌──────────────────────┐
│  pos-solo (Slave) │ ◄──────────────►  │  pos-solo (Master)   │
│  Branch Kitchen   │    HTTP REST      │  Branch Office       │
│  Orders & Sales   │                   │  Admin Dashboard     │
└───────────────────┘                   │  Aggregated Reports  │
        ↑                               └──────────────────────┘
        │ LAN/WiFi
┌───────────────────┐
│  pos-solo (Slave) │
│  Branch Bar       │
│  Orders & Sales   │
└───────────────────┘
```

### Sync Flow

```
┌──────────┐         ┌──────────┐
│  Slave    │         │  Master  │
│  Device   │         │  Device  │
└────┬─────┘         └────┬─────┘
     │                     │
     │  1. Register        │
     ├── POST /sync/register ──►│
     │   { device_id, type }    │── Create/Update Node
     │◄── { token, config } ───┤
     │                     │
     │  2. Push Sales      │
     ├── POST /sync/push/sales ──►│
     │   { sales: [...],          │── SyncLog.create()
     │     device_id }            │── broadcast WS event
     │◄── { received, id } ──────┤
     │                     │
     │  3. Pull Products   │
     │◄── GET /sync/pull/products ─┤
     │   { products: [...],       │── Query master products
     │     categories: [...] }    │
     │                     │
     │  4. Heartbeat       │
     ├── POST /sync/heartbeat ───►│
     │   { device_id, status }    │── Update Node.last_seen
     │◄── { ok } ────────────────┤
```

### What to Build

#### Backend — Slave Client (`services/sync_slave.py`)
- HTTP client that pushes local data to master
- Sync state machine: `idle → connecting → syncing → success/failed`
- Auto-retry with exponential backoff (1s, 2s, 4s, 8s, 16s, max 60s)
- Offline queue for when master is unreachable

#### Backend — Master Handler (`services/sync_master.py`)
- REST endpoints that receive data from slaves
- Conflict resolution:
  - Product catalog: master wins
  - Sales data: append-only (no conflict)
  - Inventory: latest timestamp wins
  - Settings: master pushes to slaves
- Node registry (reuses existing `Node` model)
- Sync state tracking per slave

#### Backend — Device Discovery (`services/discovery.py`)
- mDNS/Zeroconf for automatic LAN discovery
- Fallback: manual IP entry in Settings

#### Frontend — Sync UI
- Sync status indicator (🟢 Connected / 🟡 Syncing / 🔴 Disconnected)
- Pending items count
- Last sync timestamp
- Manual "Sync Now" button
- Network topology view (master + connected slaves)
- Sync health dashboard for master

### Route Map

```
# Slave → Master
POST   /sync/register         — Register device, get token
POST   /sync/push/sales       — Push sales data
POST   /sync/push/products    — Push local products
POST   /sync/push/inventory   — Push inventory changes
POST   /sync/push/customers   — Push customer data
POST   /sync/heartbeat        — Send heartbeat

# Master → Slave  
GET    /sync/pull/products    — Pull product catalog
GET    /sync/pull/config      — Pull device configuration
GET    /sync/pull/settings    — Pull branch settings

# Status
GET    /sync/status           — Sync health and stats
GET    /sync/peers            — List connected slaves
```

---

## 4. Tier 3: pos-full — Cloud-Synced Enterprise

### Architecture

```
┌──────────────────────┐  HTTPS   ┌──────────────────────┐
│  pos-full (Master)   │ ◄──────► │  POS Cloud (SaaS)    │
│  Branch Office       │  Batched │  Multi-tenant        │
│  Admin Dashboard     │  + WS    │  Analytics           │
└──────────────────────┘          │  Global Dashboard    │
        ↕ LAN                     └──────────────────────┘
┌──────────────────────┐
│  pos-solo (Slave)    │
│  Branch Kitchen      │
└──────────────────────┘
```

### What Already Exists ✅

- **`BranchSyncScheduler`** — Background sync to cloud with configurable interval
- **`ProductSyncEngine`** — Catalog sync with master/slave direction
- **`Node`, `Heartbeat`, `NodeEvent`** — Full device registry
- **`DeviceConfig`, `MasterDevice`, `CloudLink`** — Device management
- **`SyncLog`** — Sync audit log with status tracking
- **`SyncApproval`** — Approval workflow for synced changes
- **`sync_signals.py`** — Auto-flag model changes for sync
- **`SyncClient`** — HTTP client for cloud push
- **`_sync_via_datatoken()`** — Indexed batch sync via DataToken
- **Sync API endpoints** — `/sync/status`, `/sync/trigger`, `/sync/log`, etc.

### What's Missing ❌

| Feature | Priority | Description |
|---------|:--------:|-------------|
| **WebSocket real-time sync** | High | Live push of changes as they happen |
| **Bidirectional sync** | High | Pull FROM cloud TO branch |
| **Data deduplication** | High | Prevent duplicate records on reconnect |
| **Sync dashboard UI** | Medium | Frontend admin panel for sync health |
| **Sync analytics** | Medium | Volume, latency, error rate tracking |
| **Cloud disconnect handling** | Medium | Offline queue → replay on reconnect |
| **Cross-branch settings** | Low | Propagate settings from cloud to all branches |

### Enhancement Plan

#### Phase 3.1 — Real-Time Sync via WebSocket
```
Client connects to /ws/sync on cloud
─────────────────────────────────────────
1. Client sends auth token
2. Server validates and registers for entity events
3. On local model change (via signal), server pushes to client
4. Client acknowledges receipt
5. Server marks as synced
```

#### Phase 3.2 — Bidirectional Sync
```
Cloud → Branch (pull):
1. Scheduler: every N minutes, check cloud for pending pushes
2. Cloud returns: { products: [...], settings: {...}, commands: [...] }
3. Branch applies changes locally
4. Branch acknowledges

Branch → Cloud (push - already exists):
1. Scheduler: push unsynced local data to cloud
2. Cloud deduplicates by (branch_id, local_id)
3. Cloud marks as received
```

#### Phase 3.3 — Sync Dashboard
```
/enterprise/sync
├── Overview: Total branches, online/offline, last global sync
├── Per-branch: Status, last sync, pending, failed count
├── Sync log: Searchable, filterable, exportable
├── Queue depth: Items pending per entity type
└── Analytics: Sync volume chart, error rate, latency
```

---

## 5. Data Model Reference

### Node Model

```python
class Node(models.Model):
    node_id = CharField(unique=True)        # Unique device identifier
    hostname = CharField()                   # Device hostname
    node_type = CharField(choices=NODE_TYPES) # pos-mini/solo/full/custom
    version = CharField()                    # Software version
    status = CharField(choices=STATUS)       # online/offline/degraded
    is_active = BooleanField()
    ip_address = GenericIPAddressField()
    port = IntegerField()
    capabilities = JSONField()               # Feature flags
    metadata = JSONField()                   # Extra device info
    product_count = IntegerField()
    transaction_count = IntegerField()
    customer_count = IntegerField()
    first_seen = DateTimeField()
    last_seen = DateTimeField()
    last_synced_at = DateTimeField()
```

### SyncLog Model

```python
class SyncLog(models.Model):
    node_id = CharField(db_index=True)
    entity_type = CharField()    # product/sale/inventory/customer
    entity_id = CharField()
    direction = CharField()      # push/pull
    status = CharField()         # pending/in_progress/success/failed
    payload_size = IntegerField()
    duration_ms = IntegerField()
    error_message = TextField()
    retry_count = IntegerField()
```

### SyncApproval Model

```python
class SyncApproval(models.Model):
    node_id = CharField(db_index=True)
    entity_type = CharField()    # product/sale/inventory/sync/other
    entity_id = CharField()
    change_data = JSONField()    # The data to be approved
    change_summary = TextField()
    direction = CharField()      # push/pull/sync
    status = CharField()         # pending/approved/rejected/applied
    reviewer = CharField()
    reviewed_at = DateTimeField()
    notes = TextField()
```

---

## 6. Conflict Resolution

| Entity | Strategy | Rationale |
|--------|----------|-----------|
| **Products** | Master wins | Product catalog is centralized |
| **Categories** | Master wins | Categories are managed centrally |
| **Sales** | Append-only | Sales are immutable records |
| **Customers** | Latest timestamp wins | Customer data can be updated at any terminal |
| **Inventory** | Latest timestamp wins | Stock changes are time-sensitive |
| **Employees** | Master wins | Employee records are managed centrally |
| **Settings** | Master wins | Settings cascade from master to slaves |

---

## 7. Security

### Authentication
- **Slave → Master**: Device token (JWT-like, SHA-256 signed)
- **Master → Cloud**: API key + device token
- **Token issuance**: POST `/sync/register` with device secret

### Authorization
- Slaves can only push data, not pull other slaves' data
- Master can push/pull all data
- Cloud can push/pull all data across all branches

### Network Security
- LAN: Optional mTLS for slave-to-master
- Cloud: HTTPS + API key
- mDNS: Local network only (not routable)

---

## 8. Offline Behavior

| State | Can Do | Cannot Do |
|-------|--------|-----------|
| **Online (connected to master/cloud)** | All operations, real-time sync | — |
| **Online (no master/cloud)** | All local operations | Sync, cross-branch reports |
| **Offline** | All local operations | Sync, cross-branch reports |

Offline queue stores up to 10,000 pending sync items per entity type. On reconnection, queue replays in order with deduplication.
