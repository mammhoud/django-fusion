# DataToken Sync-Tagging System

## Overview

**DataToken** is a lightweight sync-tagging system in `django-fusion` that marks
database rows for ordered synchronisation to an upstream master (e.g. pos-cloud).

Instead of scanning entire tables for changes, DataToken acts as a **tag** on
individual rows — the sync engine queries `DataToken.objects.unsynced().for_node("solo-001")`
and gets an ordered, structured batch instantly.

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│  POS Device (pos-solo / pos-full)                        │
│                                                          │
│  Invoice #42                                             │
│    ├── DataToken("inv_42", node="solo-001", order=1)     │
│    ├── DataToken("inv_42_item_1", parent=↑, order=2)    │
│    └── DataToken("inv_42_item_2", parent=↑, order=2)    │
│                                                          │
│  SyncClient.push(token.content_object)                   │
│    └── POST /api/sync/push/products → pos-cloud          │
│         └── 200 OK → token.mark_synced()                 │
│              └── Auto-untag via signal on SyncLog        │
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

## Key Features

### 1. Primary Lookup — `token` Field
The `token` field is the **first lookup key**. Query by token to find any tagged row instantly:
```python
dt = DataToken.objects.get(token="inv_42_node_abc")
print(dt.content_object)  # → the actual Invoice instance
```

### 2. Parent/Child Tree Ordering
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

### 3. Progress Tracking
Every token tracks its lifecycle:
| Field | Purpose |
|-------|---------|
| `sync_status` | `pending` → `syncing` → `synced` / `failed` |
| `retry_count` | Incremented on each `mark_failed()` |
| `error_message` | Last error from the upstream push |
| `synced_at` | Timestamp of confirmed sync |
| `metadata` | Arbitrary JSON (e.g. invoice total, customer name) |

### 4. Auto-Untag on Sync Success
Connect the built-in handler to your project's `SyncLog` model:
```python
# In AppConfig.ready():
from django_fusion.core.models import sync_log_success_handler
from django.db.models.signals import post_save
post_save.connect(sync_log_success_handler, sender=SyncLog)
```
When a `SyncLog` flips to `status="success"`, matching DataTokens are automatically
marked as synced — **no manual cleanup needed**.

### 5. DataTokenMixin — Drop-in for Any Model
```python
from django_fusion.core.models import DataTokenMixin

class Invoice(DataTokenMixin, models.Model):
    customer = models.CharField(max_length=100)
    total = models.DecimalField(max_digits=10, decimal_places=2)

invoice = Invoice.objects.first()
invoice.tag_for_sync(token="inv_42", node_id="solo-001", sync_order=5)
print(invoice.is_tagged_for_sync)  # True
invoice.mark_synced()              # Preserves audit trail
invoice.untag_for_sync()           # Hard-delete with force_delete=True
```

## Integration with pos-solo / pos-full

### Step 1: Tag rows after creation
```python
# In your CRUD handler after creating an invoice:
from django_fusion.core.models import DataToken

invoice = Invoice.objects.create(customer="Acme", total=99.99)
DataToken.objects.tag_row(
    model_instance=invoice,
    token=f"inv_{invoice.id}_{node_id}",
    node_id=current_node_id,
    sync_order=0,
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

### Step 2: Sync batch in the scheduler
```python
# In BranchSyncScheduler._sync_cycle():
from django_fusion.core.models import DataToken

batch = DataToken.objects.sync_batch(node_id=self.node_id, limit=50)
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

### Step 3: Auto-cleanup via SyncLog signal
Once connected, sync logs marked `success` automatically untag the corresponding
DataTokens. No manual token deletion needed — the audit trail stays intact.

## Database Indexes
Three composite indexes ensure query performance at scale:
- `(node_id, sync_status, sync_order)` — for `sync_batch()` queries
- `(content_type, object_id)` — for `untag_by_entity()` lookups
- `(sync_status, created_at)` — for global unsynced scans

## Migration
After adding DataToken to your `INSTALLED_APPS`, run:
```bash
python manage.py makemigrations
python manage.py migrate
```
The model uses `app_label = "CI"` (consistent with `Integration`) and creates a
`ci_datatoken` table.
