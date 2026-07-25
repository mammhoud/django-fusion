# 🔄 Cloud Sync — Implementation Plan

> Full implementation plan for cloud sync, APIs, and multi-store data synchronization across POS editions.

---

## Current State

| Component | Status | Edition |
|-----------|--------|---------|
| Solo → Cloud sync client | ✅ Implemented | Solo |
| Cloud CRM server | ✅ Implemented | Full |
| Sync proxy (accept pushes) | ✅ Implemented | Full |
| Webhook receiver | ✅ Implemented | Full |
| Webhook sender | ✅ Implemented | Solo |
| Real-time WebSocket sync | ✅ Implemented | Full |
| Conflict resolution | ❌ Planned | Full |
| Offline queue | 🟡 In-memory queue implemented; durable queue planned | All |
| Multi-store dashboard | ❌ Planned | Cloud |
| REST API for all entities | ✅ Implemented (django-bolt) | Solo/Full |

---

## Implementation Phases

### Phase 1: Complete REST API ✅

REST endpoints for all 29 tables currently only accessible via Rust invoke are now exposed through the high-performance django-bolt API:

```python
# New API endpoints to add
/products/{id}/variants      # Product variants CRUD
/inventory/{product_id}      # Stock levels per warehouse
/inventory/movements         # Stock movement history
/suppliers                   # Supplier CRUD
/purchase-orders             # Purchase order CRUD
/registers/{id}/sessions     # Register session history
/tax-rates                   # Tax rate CRUD
/discounts                   # Discount CRUD
/reports/sales               # Sales reports
/reports/inventory           # Inventory reports
/reports/employees           # Employee performance reports
```

### Phase 2: Real-time Sync (Q4 2026) ✅

```
┌──────────────┐                    ┌──────────────
│  Terminal A  │ ←─── WebSocket ──→ │  Cloud CRM   │
│  (pos-solo)   │                    │  (pos-full)   │
└──────────────┘                    └──────┬───────┘
                                           │
┌──────────────┐                    ┌──────▼───────┐
│  Terminal B  │ ←─── WebSocket ──→ │  PostgreSQL  │
│  (pos-solo)   │                    │  (new)        │
└──────────────┘                    └──────────────┘
```

**Implementation:**
- `pos-solo/sidecar/ws_client.py` — persistent asyncio WebSocket client with exponential-backoff reconnection and offline queue.
- `pos-solo/sidecar/ws_sync_signals.py` — Django `post_save`/`post_delete` receivers that push local entity CRUD events to the cloud.
- `pos-cloud/core/sync_api.py` — targeted branch broadcasts via `SyncBroker` so terminals receive echo/confirmation events in real time.
- Messages use the existing `identify`/`sync_push`/`broker_message` protocol consumed by `SyncEventConsumer`.

### Phase 3: django-bolt + Robyn APIs (Q4 2026)

**Full Edition:** Replace Django views with django-bolt for all API endpoints:
- Rust-powered async handlers (60k+ RPS)
- Auto-generated OpenAPI docs at `/bolt/docs`
- Built-in JWT + API key authentication
- Pydantic validation via `django_bolt.pydantic`
- Native WebSocket for real-time sync

**Solo Extended:** Optional django-bolt sidecar API alongside the Robyn runtime:
- Rust-powered async runtime (django-bolt / Robyn)
- Auto-generated OpenAPI at `/bolt/docs`
- Pydantic validation integration
- SSE streaming support

See also:
- [django-bolt integration plan](../sidecar/django-bolt-integration.md)
- [Robyn migration plan](../sidecar/robyn-migration.md)

### Phase 4: Multi-Store Dashboard (Q1 2027)

Web dashboard accessible at `https://cloud.structa.cloud`:

- All stores overview
- Per-store drill-down
- Consolidated reporting
- Employee management across stores
- Inventory tracking across warehouses

---

## API Plan (django-bolt)

### Auth Endpoints

```python
POST   /bolt/auth/login          # JWT login
POST   /bolt/auth/refresh        # Refresh token
POST   /bolt/auth/logout         # Invalidate token
```

### Product Endpoints

```python
GET    /bolt/products             # List (with filtering, pagination)
POST   /bolt/products             # Create
GET    /bolt/products/{id}       # Detail
PUT    /bolt/products/{id}        # Update
DELETE /bolt/products/{id}       # Soft delete
```

### Order Endpoints

```python
GET    /bolt/orders              # List (filter by date, status)
POST   /bolt/orders              # Create (with items)
GET    /bolt/orders/{id}         # Detail with items
PUT    /bolt/orders/{id}/status  # Update status
GET    /bolt/orders/{id}/invoice # Generate PDF invoice
```

### Sync Endpoints

```python
GET    /bolt/sync/status         # Sync health
POST   /bolt/sync/trigger        # Force full sync
POST   /bolt/sync/push           # Push entities (Solo → Cloud)
GET    /bolt/sync/log            # Sync history
```

### CRM Endpoints (Cloud Only)

```python
GET    /bolt/crm/contacts        # List contacts
POST   /bolt/crm/contacts        # Create contact
GET    /bolt/crm/companies       # List companies
GET    /bolt/crm/deals           # List deals
POST   /bolt/crm/deals           # Create deal
GET    /bolt/crm/dashboard       # CRM statistics
```

### Report Endpoints

```python
GET    /bolt/reports/sales       # Sales report (by date range)
GET    /bolt/reports/inventory   # Inventory report
GET    /bolt/reports/employees   # Employee performance
GET    /bolt/reports/taxes       # Tax summary
```

---

## Data Sync Rules

| Entity | Sync Direction | Frequency | Conflict Strategy |
|--------|:---:|-----------|-------------------|
| Products | Solo → Cloud | Real-time | Last-write-wins |
| Categories | Solo → Cloud | Real-time | Last-write-wins |
| Orders | Solo → Cloud | Real-time | Never conflicts (immutable) |
| Customers | Solo → Cloud | Real-time | Last-write-wins |
| Inventory | Solo → Cloud | Every 5 min | Server authoritative |
| Settings | Cloud → Solo | On change | Cloud authoritative |
| Tax Rates | Cloud → Solo | On change | Cloud authoritative |
| Discounts | Cloud → Solo | On change | Cloud authoritative |
| Users/Roles | Cloud → Solo | On change | Cloud authoritative |

---

## Conflict Resolution Algorithm

```python
def resolve_conflict(cloud_entity, terminal_entity):
    """Last-Write-Wins with merge for non-conflicting fields."""
    if cloud_entity.updated_at > terminal_entity.updated_at:
        # Cloud is newer — keep cloud version
        return cloud_entity
    elif terminal_entity.updated_at > cloud_entity.updated_at:
        # Terminal is newer — update cloud
        return terminal_entity
    else:
        # Same timestamp — merge non-conflicting fields
        merged = cloud_entity.copy()
        for field in terminal_entity.changed_fields:
            if field not in cloud_entity.changed_fields:
                merged[field] = terminal_entity[field]
        return merged
```

---

## Related

| Topic | Path |
|-------|------|
| Cloud CRM overview | [`README.md`](README.md) |
| django-bolt integration | [`../sidecar/django-bolt-integration.md`](../sidecar/django-bolt-integration.md) |
| Sidecar overview | [`../sidecar/README.md`](../sidecar/README.md) |
| POS infrastructure | [`../infrastructure.md`](../infrastructure.md) |
