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

| Area | pos-mini | pos-solo |
|------|----------|----------|
| Backend | Rust only | Rust + Django |
| Sidecar | None | Robyn Python server |
| Sync | None | LAN branch-to-master |
| Roles | Rust struct | Django Role model |
| DB | SQLite | SQLite (x2) |
| Dashboard | None | Sidecar admin |

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

```python
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
