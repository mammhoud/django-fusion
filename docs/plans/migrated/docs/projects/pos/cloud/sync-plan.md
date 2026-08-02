# 🔄 Cloud Sync — Implementation Plan

> Full implementation plan for cloud sync, APIs, and multi-store data synchronization across POS editions.

---

## Current State

| Component | Status | Phase | Edition |
|-----------|--------|-------|---------|
| REST API for all entities | ✅ Implemented (django-bolt) | Phase 1 | Solo/Full |
| Cloud CRM server | ✅ Implemented | Phase 1 | Full |
| Solo → Cloud sync client | ✅ Implemented | Phase 2 | Solo |
| Sync proxy (accept pushes) | ✅ Implemented | Phase 2 | Full |
| Webhook receiver | ✅ Implemented | Phase 2 | Full |
| Webhook sender | ✅ Implemented | Phase 2 | Solo |
| Real-time WebSocket sync | ✅ Implemented | Phase 2 | Full |
| Conflict resolution | ❌ Planned | Phase 2 | Full |
| Offline queue | 🟡 In-memory queue implemented; durable queue planned | Phase 2 | All |
| Multi-store dashboard | 🟡 In progress | Phase 3 | Cloud |

---

## Implementation Phases

### Phase 1: django-bolt REST API & Sidecar Runtimes ✅

REST endpoints for all 29 tables previously only accessible via Rust invoke are now exposed through the high-performance django-bolt API.

**Full Edition (django-bolt):**
- Rust-powered async handlers (60k+ RPS)
- Auto-generated OpenAPI docs at `/bolt/docs`
- Built-in JWT + API key authentication
- Pydantic validation via `django_bolt.pydantic`
- Native WebSocket for real-time sync

**Solo Extended (Robyn sidecar):**
- Rust-powered async runtime alongside the existing Robyn runtime
- Auto-generated OpenAPI at `/bolt/docs`
- Pydantic validation integration
- SSE streaming support

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

See also:
- [django-bolt integration plan](../sidecar/django-bolt-integration.md)
- [Robyn migration plan](../sidecar/robyn-migration.md)

### Phase 2: Real-time Sync (Q4 2026) 🟡

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

### Phase 3: Multi-Store Dashboard (Q1 2027) 🟡

Work has started on the cloud dashboard infrastructure in `pos-cloud`: the Unfold
admin dashboard, the `/apis/` analytics dashboard, and the branch sync dashboard
(`core/sync_dashboard.py`). The public multi-store dashboard will be accessible
at `https://cloud.structa.cloud`.

- All stores overview
- Per-store drill-down
- Consolidated reporting
- Employee management across stores
- Inventory tracking across warehouses

---

## API Plan

The detailed django-bolt endpoint reference is maintained separately in
[api-plan.md](api-plan.md).

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
| API plan | [`api-plan.md`](api-plan.md) |
| Cloud CRM overview | [`README.md`](README.md) |
| django-bolt integration | [`../sidecar/django-bolt-integration.md`](../sidecar/django-bolt-integration.md) |
| Sidecar overview | [`../sidecar/README.md`](../sidecar/README.md) |
| POS infrastructure | [`../infrastructure.md`](../infrastructure.md) |
