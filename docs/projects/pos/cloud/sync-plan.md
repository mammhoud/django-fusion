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
| Real-time WebSocket sync | ❌ Planned | Full |
| Conflict resolution | ❌ Planned | Full |
| Offline queue | ❌ Planned | All |
| Multi-store dashboard | ❌ Planned | Cloud |
| REST API for all entities | 🟡 Partial | Solo/Full |

---

## Implementation Phases

### Phase 1: Complete REST API (Q3 2026)

Add REST endpoints for ALL 29 tables currently only accessible via Rust invoke:

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

### Phase 2: Real-time Sync (Q4 2026)

```
┌──────────────┐                    ┌──────────────┐
│  Terminal A  │ ←─── WebSocket ──→ │  Cloud CRM   │
│  (pos-solo)   │                    │  (pos-full)   │
└──────────────┘                    └──────┬───────┘
                                           │
┌──────────────┐                    ┌──────▼───────┐
│  Terminal B  │ ←─── WebSocket ──→ │  PostgreSQL  │
│  (pos-solo)   │                    │  (new)        │
└──────────────┘                    └──────────────┘
```

### Phase 3: Django Ninja Extra APIs (Q4 2026)

Replace Sanic with Django Ninja Extra for all API endpoints:

- Auto-generated OpenAPI docs at `/api/docs`
- Pydantic validation for all endpoints
- Async support for real-time sync
- Built-in auth with JWT tokens

### Phase 4: Multi-Store Dashboard (Q1 2027)

Web dashboard accessible at `https://cloud.structa.cloud`:

- All stores overview
- Per-store drill-down
- Consolidated reporting
- Employee management across stores
- Inventory tracking across warehouses

---

## API Plan (Django Ninja Extra)

### Auth Endpoints

```python
POST   /api/auth/login          # JWT login
POST   /api/auth/refresh        # Refresh token
POST   /api/auth/logout         # Invalidate token
```

### Product Endpoints

```python
GET    /api/products             # List (with filtering, pagination)
POST   /api/products             # Create
GET    /api/products/{id}        # Detail
PUT    /api/products/{id}        # Update
DELETE /api/products/{id}        # Soft delete
```

### Order Endpoints

```python
GET    /api/orders               # List (filter by date, status)
POST   /api/orders               # Create (with items)
GET    /api/orders/{id}          # Detail with items
PUT    /api/orders/{id}/status   # Update status
GET    /api/orders/{id}/invoice  # Generate PDF invoice
```

### Sync Endpoints

```python
GET    /api/sync/status          # Sync health
POST   /api/sync/trigger         # Force full sync
POST   /api/sync/push            # Push entities (Solo → Cloud)
GET    /api/sync/log             # Sync history
```

### CRM Endpoints (Cloud Only)

```python
GET    /api/crm/contacts         # List contacts
POST   /api/crm/contacts         # Create contact
GET    /api/crm/companies        # List companies
GET    /api/crm/deals            # List deals
POST   /api/crm/deals            # Create deal
GET    /api/crm/dashboard        # CRM statistics
```

### Report Endpoints

```python
GET    /api/reports/sales        # Sales report (by date range)
GET    /api/reports/inventory    # Inventory report
GET    /api/reports/employees    # Employee performance
GET    /api/reports/taxes        # Tax summary
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
| Django Ninja plan | [`../sidecar/django-ninja-plan.md`](../sidecar/django-ninja-plan.md) |
| Sidecar overview | [`../sidecar/README.md`](../sidecar/README.md) |
| POS infrastructure | [`../infrastructure.md`](../infrastructure.md) |
