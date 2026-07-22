# DataToken Sync-Tagging System

## Overview

**DataToken** is a lightweight sync-tagging system in `django-fusion` that marks
database rows for ordered synchronisation to an upstream master (e.g. pos-cloud).

Instead of scanning entire tables for changes, DataToken acts as a **tag** on
individual rows — the sync engine queries `DataToken.objects.unsynced().for_node("solo-001")`
and gets an ordered, structured batch instantly.

## Architecture (v2 — Abstract Base)

```
  AbstractDataToken (django-fusion, abstract=True)
  ├── Status enum   (pending / syncing / synced / failed)
  ├── AppType enum  (pos-solo / pos-full / pos-mini / cloud)
  ├── sync_status   (CharField, db_index=True)
  ├── app_type      (CharField, db_index=True)
  ├── metadata      (JSONField)
  ├── created_at
  └── updated_at
       │
       ├── DataToken (concrete — CI app)
       │   ├── + token         (unique lookup key)
       │   ├── + node_id       (device scoping)
       │   ├── + content_type  (GenericFK — tags ANY DB row)
       │   ├── + object_id
       │   ├── + parent        (self-FK tree: invoice → items)
       │   ├── + sync_order
       │   ├── + retry_count
       │   ├── + error_message
       │   ├── + synced_at
       │   └── DataTokenManager / DataTokenQuerySet / DataTokenMixin
       │
       └── DeviceToken (concrete — pos-full / pos-solo / pos-cloud)
           ├── + device_id
           ├── + token_hash
           ├── + token_prefix
           ├── + node_id_link
           ├── + role
           ├── + node_type
           ├── + capabilities
           ├── + allowed_entities
           ├── + issued_at / expires_at / last_used_at
           ├── + last_synced_at  (device-level, not per-row)
           └── + is_active
```

**Key insight**: Both sync-tagging (DataToken) and device auth (DeviceToken)
share the same sync state machine via `AbstractDataToken`.  This eliminates
duplicate field definitions and ensures `sync_status` + `app_type` are
consistent across the entire token system.

```
┌──────────────────────────────────────────────────────────┐
│  POS Device (pos-solo / pos-full)                        │
│                                                          │
│  Invoice #42                                             │
│    ├── DataToken("inv_42", node="solo-001", order=1)     │
│    ├── DataToken("inv_42_item_1", parent=↑, order=2)    │
│    └── DataToken("inv_42_item_2", parent=↑, order=2)    │
│                                                          │
│  DeviceToken → app_type="pos-solo"                       │
│    sync_status="syncing" → scheduler pushes batch        │
│    → pos-cloud confirms → mark_data_synced()             │
│       └── Cascades to linked DataTokens ✅               │
└──────────────────────────────────────────────────────────┘
```

## Benefits

| Benefit | Without DataToken | With DataToken |
|---------|-------------------|----------------|
| **Sync speed** | Full table scan + dedup | Ordered batch query (indexed) |
| **Data integrity** | No ordering guarantees | Parent→child tree ensures invoice before items |
| **Retry control** | Manual tracking | Built-in `retry_count` + `error_message` |
| **Audit trail** | Lost on delete | Tokens marked `synced` (preserved) |
| **Multi-node** | Single-queue bottleneck | Per-node scoping (`node_id` index) |
| **UUID PK support** | N/A | `CharField` object_id supports any PK type |
| **Cross-model consistency** | Duplicate field definitions | Shared `AbstractDataToken` base |
| **App-type filtering** | N/A | `app_type` field scopes sync by POS edition |

## Key Features

### 1. AbstractDataToken Base

All token models inherit shared fields from `AbstractDataToken`:

| Field | Source | Shared By |
|-------|--------|-----------|
| `sync_status` | AbstractDataToken | DataToken, DeviceToken |
| `app_type` | AbstractDataToken | DataToken, DeviceToken |
| `metadata` | AbstractDataToken | DataToken, DeviceToken |
| `created_at` | AbstractDataToken | DataToken, DeviceToken |
| `updated_at` | AbstractDataToken | DataToken, DeviceToken |

```python
from django_fusion.core.models import AbstractDataToken

class DeviceToken(AbstractDataToken):
    device_id = models.CharField(...)
    token_hash = models.CharField(...)
    # sync_status, app_type, metadata inherited — no duplication!
```

### 2. Primary Lookup — `token` Field
The `token` field is the **first lookup key**. Query by token to find any tagged row instantly:
```python
dt = DataToken.objects.get(token="inv_42_node_abc")
print(dt.content_object)  # → the actual Invoice instance
print(dt.app_type)         # → "pos-solo" (inherited from AbstractDataToken)
```

### 3. Parent/Child Tree Ordering
Related rows (e.g. invoice → line items) form a tree. Parents are synced first:
```python
# Get ordered sync batch (roots only)
batch = DataToken.objects.sync_batch(node_id="solo-001", limit=100)

for token in batch:
    push(token.content_object)         # Push the invoice
    for child in token.get_sync_tree():  # Push its items (depth-first)
        push(child.content_object)
    token.mark_synced()                # Cascade marks children too
```

### 4. Progress Tracking
Every token tracks its lifecycle:
| Field | Purpose |
|-------|---------|
| `sync_status` | `pending` → `syncing` → `synced` / `failed` |
| `retry_count` | Incremented on each `mark_failed()` |
| `error_message` | Last error from the upstream push |
| `synced_at` | Timestamp of confirmed sync (DataToken only) |
| `last_synced_at` | Device-level sync timestamp (DeviceToken only) |
| `app_type` | POS edition scope (pos-solo/pos-full/pos-mini/cloud) |
| `metadata` | Arbitrary JSON (e.g. invoice total, customer name) |

### 5. DeviceToken ↔ DataToken Cascade
When `DeviceToken.mark_data_synced()` is called, it cascades to all linked
`DataToken` rows matching the device's `node_id_link`:
```python
# DeviceToken.mark_data_synced() triggers:
DataToken.objects.filter(
    node_id=self.node_id_link,
    sync_status__in=["pending", "syncing"],
).update(sync_status="synced", synced_at=now)
```

### 6. Auto-Untag on Sync Success
Connect the built-in handler to your project's `SyncLog` model:
```python
# In AppConfig.ready():
from django_fusion.core.models import sync_log_success_handler
from django.db.models.signals import post_save
post_save.connect(sync_log_success_handler, sender=SyncLog)
```
When a `SyncLog` flips to `status="success"`, matching DataTokens are automatically
marked as synced — **no manual cleanup needed**.

### 7. DataTokenMixin — Drop-in for Any Model
```python
from django_fusion.core.models import DataTokenMixin

class Invoice(DataTokenMixin, models.Model):
    customer = models.CharField(max_length=100)
    total = models.DecimalField(max_digits=10, decimal_places=2)

invoice = Invoice.objects.first()
invoice.tag_for_sync(
    token="inv_42", node_id="solo-001",
    sync_order=5, app_type="pos-solo",
)
print(invoice.is_tagged_for_sync)  # True
invoice.mark_synced()              # Preserves audit trail
```

## Integration with pos-solo / pos-full

### Step 1: Tag rows after creation (with app_type)
```python
from django_fusion.core.models import DataToken, AbstractDataToken

invoice = Invoice.objects.create(customer="Acme", total=99.99)
DataToken.objects.tag_row(
    model_instance=invoice,
    token=f"inv_{invoice.id}_{node_id}",
    node_id=current_node_id,
    sync_order=0,
    app_type=AbstractDataToken.AppType.POS_SOLO,
)

for item in items:
    item_instance = InvoiceItem.objects.create(invoice=invoice, ...)
    DataToken.objects.tag_row(
        model_instance=item_instance,
        token=f"inv_item_{item_instance.id}_{node_id}",
        node_id=current_node_id,
        sync_order=1,
        parent_token=DataToken.objects.get(token=f"inv_{invoice.id}_{node_id}"),
        metadata={"product_sku": item.sku, "quantity": item.qty},
    )
```

### Step 2: Sync batch in the scheduler (with app_type filter)
```python
from django_fusion.core.models import DataToken

# Filter by app_type as well as node_id
batch = DataToken.objects.sync_batch(node_id=self.node_id, limit=50).filter(
    app_type=self.device_token.app_type,
)
for token in batch:
    try:
        payload = serialize(token.content_object)
        result = await sync_client.push(payload)
        if result.get("status") == "received":
            token.mark_synced()
        else:
            token.mark_failed(str(result))
    except Exception as exc:
        token.mark_failed(str(exc))
```

### Step 3: DeviceToken cascade on sync confirm
```python
# When pos-cloud confirms receipt:
device_token = DeviceToken.objects.get(node_id_link=node_id)
device_token.mark_data_synced()
# → Cascades to all pending DataTokens with matching node_id
```

## Database Indexes
Four composite indexes ensure query performance at scale:
- `(node_id, sync_status, sync_order)` — for `sync_batch()` queries
- `(content_type, object_id)` — for `untag_by_entity()` lookups
- `(sync_status, created_at)` — for global unsynced scans
- `(app_type, sync_status)` — for per-edition scoping (new in v2)

## Migrations

### CI App (DataToken)
```bash
python manage.py makemigrations CI
# → 0001_initial.py    — ci_datatoken, ci_integration, ci_call, ci_notification
# → 0002_datatoken_app_type  — adds app_type field + [app_type, sync_status] index
python manage.py migrate
```

### Core App (DeviceToken)
```bash
python manage.py makemigrations core
# → 0002_devicetoken.py  — cloud_device_tokens with app_type, last_synced_at, sync_status
# → 0003_alter_devicetoken  — fields now inherited from AbstractDataToken
python manage.py migrate
```

The `ci_datatoken` table is created under `app_label = "CI"` (consistent with
`Integration`, `Call`, and `Notification` models).

## File Layout

```
libs/django-fusion/src/django_fusion/
├── core/models/datatoken.py     # AbstractDataToken + DataToken + Mixin + signals
├── core/models/__init__.py      # Exports AbstractDataToken
├── ci/apps.py                   # CIIntegrationConfig (label="CI")
├── ci/models.py                 # Re-exports DataToken for migration autodetector
└── ci/migrations/               # CI app migrations

projects/pos/
├── pos-full/sidecar/models/token.py   # DeviceToken(AbstractDataToken)
├── pos-solo/sidecar/models/token.py   # DeviceToken(AbstractDataToken)
└── pos-cloud/core/models.py           # DeviceToken(AbstractDataToken)
```
