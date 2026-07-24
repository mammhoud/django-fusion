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

| Area | pos-solo | pos-full |
|------|----------|----------|
| Sync | LAN only | LAN + Cloud |
| Database | 2× SQLite | SQLite + PostgreSQL |
| Dashboard | Sidecar only | Sidecar + Cloud admin |
| Multi-branch | Single master | Multi-branch hierarchy |
| Payments | Local | Cloud payment gateway |

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

```python
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
