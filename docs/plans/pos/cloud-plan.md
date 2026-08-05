# Cloud Server Plan — POS Multi-Branch Integration
> **Tags:** #pos #cloud #infrastructure

> **Status:** Planning Phase  
> **Target Version:** 3.0.0  
> **Server Port:** 8767  
> **API ownership:** Cloud-only. django-bolt may be evaluated or used here as the cloud transport adapter; it must not be added to local Formint, django-fusion, POS Solo, or Forge plans.

---

## 1. Vision

A unified **Cloud Server** that links all POS editions (Solo, Full, Minimal) through token-authenticated, bidirectional data streaming. This enables:

- **Multi-branch management** — One dashboard for all locations
- **Cross-branch sync** — Products, configs, and approvals shared across branches
- **Offline-first** — Each branch works offline, syncs when connected
- **Centralized monitoring** — Health, analytics, and alerts for all devices

---

## 2. Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                       Cloud Server (8767)                          │
│                                                                    │
│  ┌──────────┐ ┌───────────┐ ┌──────────┐ ┌────────────┐         │
│  │  Auth    │ │  Branch   │ │  Sync    │ │  Monitor   │         │
│  │  Gateway │ │  Router   │ │  Broker  │ │  Dashboard │         │
│  │  • JWT   │ │  • Route  │ │  • WS    │ │  • Health  │         │
│  │  • RBAC  │ │  • Multi- │ │  • Queue │ │  • Stats   │         │
│  │  • Keys  │ │    tenant │ │  • Retry  │ │  • Alerts  │         │
│  └────┬─────┘ └─────┬─────┘ └────┬─────┘ └──────┬─────┘         │
│       │             │            │               │               │
│       └─────────────┴────────────┴───────────────┘               │
│                             │                                    │
│                    Django ORM (cloud.db)                          │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Branch, DeviceConfig, SyncLog, Approval, Token, Alert   │  │
│  └───────────────────────────────────────────────────────────┘  │
└──────────────────────────┬───────────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
    ┌─────▼──────┐  ┌─────▼──────┐  ┌─────▼──────┐
    │ POS Solo   │  │ POS Full   │  │ Remote     │
    │ (8765)     │  │ (8766)     │  │ Browser UI │
    │ 1 branch   │  │ N branches │  │ (Web app)  │
    └────────────┘  └────────────┘  └────────────┘
```

---

## 3. API Types

The cloud plan is the sole POS planning document allowed to define a django-bolt
transport. Keep the transport behind a cloud adapter so the domain event
contract remains portable and local Formint can use its own Django/HTMX/data
endpoints. The cloud API owns tenant/branch authentication, streaming, sync
broker operations, webhooks, and central analytics; it does not own local POS
layout, skeletons, or business UI components.

### Cloud django-bolt boundary

- **Allowed here:** a cloud-side `BoltAPI` adapter for high-throughput branch sync, WebSocket streaming, authentication, and cloud-only OpenAPI exposure.
- **Not allowed here:** importing the removed `django_fusion.plugins.bolt` package, adding django-bolt to Formint local dependencies, or coupling local Astro/HTMX rendering to Bolt.
- **Contract:** branch clients communicate through versioned envelopes with stable IDs, event versions, idempotency keys, request IDs, scopes, retries, conflict records, and audit references.
- **Fallback:** retain standard Django URL/view handlers for health, administration, migrations, and an operational fallback path when the cloud Bolt adapter is unavailable.

| Type | Transport | Format | Use Case |
|------|-----------|--------|----------|
| **REST CRUD** | HTTP | JSON | Standard create/read/update/delete |
| **REST Action** | HTTP | JSON | Custom operations (approve, sync, test) |
| **WebSocket Event** | WS | JSON (server→client) | Real-time event streaming |
| **WebSocket Command** | WS | JSON (client→server) | Client filters and commands |
| **Webhook** | HTTP | JSON (server→server) | Signal-triggered callbacks |
| **Sync Push** | HTTP | JSON (server→server) | Data synchronization |
| **Streaming Sync** | WS | JSON (bidirectional) | Live cross-bridge sync |
| **Health Check** | HTTP | JSON | Service availability |

---

## 4. Cloud Server Models

```python
# Proposed cloud server models

class CloudBranch(models.Model):
    """Registered POS branch connected to cloud."""
    branch_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    edition = models.CharField(max_length=20)  # solo, full, minimal
    device_id = models.CharField(max_length=100)
    status = models.CharField(max_length=20, default="offline")
    last_seen = models.DateTimeField(null=True)
    version = models.CharField(max_length=50)
    config = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

class CrossBranchApproval(models.Model):
    """Approval request that can be reviewed from any branch."""
    source_branch = models.ForeignKey(CloudBranch, on_delete=CASCADE)
    target_branches = models.JSONField(default=list)  # [] = all
    entity_type = models.CharField(max_length=50)
    entity_id = models.CharField(max_length=100)
    payload = models.JSONField()
    status = models.CharField(max_length=20, default="pending")
    reviewed_by = models.CharField(max_length=100, blank=True)
    reviewed_at = models.DateTimeField(null=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class SyncQueue(models.Model):
    """Queued sync operations between branches."""
    source_branch = models.ForeignKey(CloudBranch, on_delete=CASCADE, related_name="sync_out")
    target_branch = models.ForeignKey(CloudBranch, on_delete=CASCADE, related_name="sync_in")
    entity_type = models.CharField(max_length=50)
    payload = models.JSONField()
    status = models.CharField(max_length=20, default="pending")  # pending, delivered, failed
    retry_count = models.IntegerField(default=0)
    error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True)
```

---

## 5. Streaming Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                      Streaming Pipeline                           │
│                                                                    │
│  Branch A (Solo)              Cloud Server              Branch B  │
│       │                           │                       │       │
│       ├── WS Connect /ws/broker ──►│                       │       │
│       │                           │── WS /ws/broker ──────►│       │
│       │                           │   (forwards events)    │       │
│       │                           │                       │       │
│       │  Sale created             │                       │       │
│       ├── POST /sync/push/sale ──►│                       │       │
│       │                           │── WS event ──────────►│       │
│       │                           │   {type: "sale", ...} │       │
│       │                           │                       │       │
│       │  Config changed           │                       │       │
│       │◄── WS event ──────────────┤                       │       │
│       │   {type: "config", ...}   │── WS event ──────────►│       │
│       │                           │                       │       │
│       │  Approval needed          │                       │       │
│       │◄── WS event ──────────────┤                       │       │
│       │   {type: "approval", ...} │── WS event ──────────►│       │
│       │                           │   (notifies manager)  │       │
└──────────────────────────────────────────────────────────────────┘
```

---

## 6. Offline-First Strategy

```
Normal Operation:
┌──────────┐    WS/HTTP    ┌────────────┐
│  Branch  │◄─────────────►│  Cloud     │
│  (local) │               │  Server    │
└──────────┘               └────────────┘

Offline:
┌──────────┐               ┌────────────┐
│  Branch  │    LOCAL       │  Cloud     │
│  (ops)   │──────────────►│  (down)    │
│  Queue   │               └────────────┘
└────┬─────┘
     │
     ▼
┌────────────────┐
│  sync_state.json│
│  unsynced: [    │
│    {sale: ...}, │
│    {inventory}  │
│  ]              │
└────────────────┘

Reconnect:
┌──────────┐               ┌────────────┐
│  Branch  │── batch ─────►│  Cloud     │
│  Flush   │   POST /sync/ │  Server    │
│  Queue   │   batch       │            │
└──────────┘               └────────────┘
```

---

## 7. Implementation Plan

### Phase 1: Foundation (Week 1-2)
- [ ] Create `projects/pos/cloud-server/` directory
- [ ] Bootstrap Robyn + Django ORM (port 8767)
- [ ] Create CloudBranch, SyncQueue, CrossBranchApproval models
- [ ] Create base CRUD endpoints
- [ ] Add token-based auth (reuse shared middleware)

### Phase 2: Branch Registration (Week 2-3)
- [ ] Branch register endpoint
- [ ] Health check + status tracking
- [ ] Token issuance per branch
- [ ] Branch list + detail views

### Phase 3: Sync Broker (Week 3-4)
- [ ] Select and isolate the cloud transport adapter (`django-bolt` only if benchmarks and operational review justify it)
- [ ] WebSocket broker endpoint `/ws/broker`
- [ ] Bidirectional event forwarding
- [ ] Sync queue with retry logic
- [ ] Offline batch sync endpoint

### Phase 4: Cross-Branch Approvals (Week 4-5)
- [ ] Cross-branch approval creation
- [ ] Approval notification via WS
- [ ] Approve/reject from any branch
- [ ] Approval dashboard (django-fusion)

### Phase 5: Monitoring (Week 5-6)
- [ ] Cluster health dashboard
- [ ] Branch status page
- [ ] Sync analytics
- [ ] Alert configuration
- [ ] Email/push notifications

---

## 8. Port & Connection Map

Local Formint remains independent of this cloud transport. Its local Django,
Astro, HTMX, SQLite, and Tauri paths must continue to work without port 8767,
WebSocket access, or django-bolt installed.

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| POS Solo | 8765 | HTTP + WS | Standalone node |
| POS Full | 8766 | HTTP + WS | Cloud master |
| Cloud Server | 8767 | HTTP + WS | Multi-branch cloud |
| Cloud CRM | 8082 | HTTP | Upstream CRM (legacy) |
| Tauri Dev | 1420 | HTTP | Frontend dev server |

### Connection Rules
- **Solo → Full**: Client push (sync data)
- **Solo → Cloud**: Direct (WebSocket bridge)
- **Full → Cloud**: Bidirectional (sync broker)
- **Cloud → All**: Event streaming (config, approvals)
