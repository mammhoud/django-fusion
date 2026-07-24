---
# yaml-language-server: $schema=schemas/page.schema.json
Object type:
    - Page
Creation date: "2026-07-24T19:54:39Z"
Created by:
    - mammhoud
id: bafyreicrzhmtyfturw3qaqsvndxnu3d2fwe7qt7hdrkbc3uigqi2drmize
---
# Reference — Sidecar API   
**Type:** Reference 📚
T**ags: **#`sidecar `#`pos-solo `#`pos-full `#`backend
`S**tatus: **Published
C**ategory: **API   
 --- 
## Base URL   
```
http://localhost:8766

```
 --- 
## Routes   
### Authentication   
```
POST   /api/auth/login       → { email, password } → { token }
POST   /api/auth/register    → { email, password, name } → { token }
POST   /api/auth/verify      → { token } → { user }

```
### Sync   
```
POST   /api/sync/push        → { table, records[] } → { synced_count }
GET    /api/sync/poll        → ?since={timestamp} → { changes[] }
POST   /api/sync/branch/register → { device_id, name } → { node }

```
### Config   
```
GET    /api/config           → { settings }
POST   /api/config           → { settings } → { success }

```
### Admin   
```
/admin/                      → Django admin dashboard
GET    /admin/analytics/     → { revenue, orders, ... }

```
### Nodes (pos-full)   
```
GET    /api/nodes            → Node[]
POST   /api/nodes            → Create node
PUT    /api/nodes/:id        → Update node
DELETE /api/nodes/:id        → Deactivate node

```
### Scheduler   
```
Routes:
  POST /api/scheduler/sync   → Trigger sync
  GET  /api/scheduler/status  → { last_sync, pending_count, errors }

```
 --- 
## Request/Response Format   
```
// All responses:
{ "status": "success"|"error", "data": { ... }, "message": "..." }

// Pagination:
{ "data": [...], "page": 1, "total_pages": 5, "total": 100 }

```
 --- 
## Related Docs   
- → `architecture/sync-architecture.md` — Sync design   
- → `features/pos-solo.md` — pos-solo sidecar features   
- → `features/pos-full.md` — pos-full sidecar features   
[Reference — Sidecar API](reference-sidecar-api.md)    
