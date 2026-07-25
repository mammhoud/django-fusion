---
# yaml-language-server: $schema=schemas/page.schema.json
Object type:
    - Page
Creation date: "2026-07-24T19:54:39Z"
Created by:
    - mammhoud
id: bafyreigkb4rjn4fniwgieauwflfmsgbflhv3sap447jkf6sj5woicwq7mu
---
# pos-solo — Edition Features   
**Type:** Feature ✨
**Tags:** `#pos-solo` `#frontend` `#backend` `#sidecar` `#sync` `#database`
**Status:** Complete
**Edition:** Solo   
 --- 
## Stack   
```
React 19 ←→ Tauri Rust ←→ SQLite (POS DB)
                │
           HTTP API
                │
           Robyn Sidecar (Python)
                │
           Django ORM ←→ SQLite (Sidecar DB)

```
 --- 
## Key Differences from pos-mini   
|      Area   <br> |    pos-mini   <br> |             pos-solo   <br> |
|:-----------------|:-------------------|:----------------------------|
|   Backend   <br> |   Rust only   <br> |        Rust + Django   <br> |
|   Sidecar   <br> |        None   <br> |  Robyn Python server   <br> |
|      Sync   <br> |        None   <br> | LAN branch-to-master   <br> |
|     Roles   <br> | Rust struct   <br> |    Django Role model   <br> |
|        DB   <br> |      SQLite   <br> |          SQLite (x2)   <br> |
| Dashboard   <br> |        None   <br> |        Sidecar admin   <br> |

 --- 
## Sidecar Features   
```
Django Admin ──→ /admin/   (full CMS)
Sync API     ──→ /api/sync/ (push + poll)
Auth API     ──→ /api/auth/ (login, register)
Config API   ──→ /api/config/ (settings)

```
 --- 
## Sidecar Server Flow   
```
uv run python3 server.py
      │
      ▼
  Robyn HTTP Server :8766
      │
      ├─ /api/sync/push  → POST → SyncQueue.create()
      ├─ /api/sync/poll  → GET  → SyncQueue.filter(since=ts)
      ├─ /api/auth/*     → JWT token management
      └─ /admin/*        → Django admin panel

```
 --- 
## Models (Django)   
```
# extra.py
class Role(models.Model):
    name = models.CharField(max_length=100)
    permissions = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)

# pos.py
class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50)
    category = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL)

# sync.py  
class SyncQueue(models.Model):
    table_name = models.CharField(max_length=200)
    record_id = models.CharField(max_length=200)
    action = models.CharField(max_length=20)
    payload = models.JSONField()

```
 --- 
## Related Docs   
- → `architecture/editions-overview.md` — Edition comparison   
- → `architecture/sync-architecture.md` — LAN sync design   
- → `references/sidecar-api.md` — Sidecar API reference   
- → `guides/setup.md` — Sidecar + uv setup   
[pos-solo — Edition Features](pos-solo-edition-features.md)    
