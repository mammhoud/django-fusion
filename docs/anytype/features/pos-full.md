---
# yaml-language-server: $schema=schemas/page.schema.json
Object type:
    - Page
Creation date: "2026-07-24T19:54:39Z"
Created by:
    - mammhoud
id: bafyreig6bzb7l2b2mizpn66u2xgk5k6vy5uujb5phbd7ox54s4buxf7un4
---
# pos-full — Edition Features   
**Type:** Feature ✨
**Tags:** `#pos-full` `#frontend` `#backend` `#sidecar` `#sync` `#database` `#payments`
**Status:** Complete
**Edition:** Full   
 --- 
## Stack   
```
React 19 ←→ Tauri Rust ←→ SQLite (local cache)
                │
           HTTPS / WSS
                │
           Cloud API (Django + DRF)
                │
           PostgreSQL (central)
                │
           Robyn Sidecar (Python)

```
 --- 
## Key Differences from pos-solo   
|         Area   <br> |      pos-solo   <br> |               pos-full   <br> |
|:--------------------|:---------------------|:------------------------------|
|         Sync   <br> |      LAN only   <br> |            LAN + Cloud   <br> |
|     Database   <br> |     2× SQLite   <br> |    SQLite + PostgreSQL   <br> |
|    Dashboard   <br> |  Sidecar only   <br> |  Sidecar + Cloud admin   <br> |
| Multi-branch   <br> | Single master   <br> | Multi-branch hierarchy   <br> |
|     Payments   <br> |         Local   <br> |  Cloud payment gateway   <br> |

 --- 
## Cloud Sync Flow   
```
┌──────────┐     HTTPS      ┌─────────────┐     PostgreSQL
│ pos-full  │ ──────────→  │ Cloud API    │ ───→ [master]
│ Terminal  │ ←──────────  │ (Django DRF) │ ←─── [branch: id]
└──────────┘               └─────────────┘
     │                            │
     │ Local SQLite               │ Central DB
     │ (offline queue)            │ (source of truth)
     ▼                            ▼
  SyncQueue → retry          Conflict Resolution

```
 --- 
## Enterprise Models   
```
# node.py
class Node(models.Model):
    name = models.CharField(max_length=200)
    device_id = models.CharField(max_length=200, unique=True)
    branch_id = models.ForeignKey(Branch, on_delete=models.CASCADE)
    last_seen = models.DateTimeField(auto_now=True)
    is_master = models.BooleanField(default=False)

# sync.py
class SyncQueue(models.Model):
    node = models.ForeignKey(Node, on_delete=models.CASCADE)
    table_name = models.CharField(max_length=200)
    record_id = models.CharField(max_length=200)
    action = models.CharField(max_length=20)  # create|update|delete
    payload = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    synced_at = models.DateTimeField(null=True)

```
 --- 
## Cloud Admin Dashboard   
```
/admin/           → Django admin interface
/api/sync/       → REST sync endpoints
/api/payments/   → Payment processing
/api/config/     → Remote configuration
/api/analytics/  → Cross-branch analytics

```
 --- 
## Related Docs   
- → `architecture/editions-overview.md` — Compare with other editions   
- → `architecture/sync-architecture.md` — Cloud sync design   
- → `references/sidecar-api.md` — API reference   
- → `guides/setup.md` — Full setup guide   
[pos-full — Edition Features](pos-full-edition-features.md)    
