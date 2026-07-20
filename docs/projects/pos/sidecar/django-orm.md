# 🐍 Django ORM — Sidecar Integration

> How the POS sidecar uses Django ORM to mirror the Rust/SQLite database, enabling Django Admin, fixtures, and complex queries.

---

## Overview

Both Solo and Full sidecars now use **Django ORM** with Robyn servers. Models are organized into packages rather than flat files:

| Edition | Model Files | Tables Managed |
|---------|-------------|---------------|
| **Solo** | `models/pos.py, menu.py, node.py, config.py, sync.py` | 17 tables (all managed=True) |
| **Full** | `models/node.py, config.py, sync.py` + `posapp/models.py` | 7 registry tables (managed=True) + 30+ Rust-backed (managed=False) |

**Key principle**: 
- For **managed=True** models (registry, config, sync): The Robyn server creates and manages these tables via `schema_editor.create_model()`
- For **managed=False** models (posapp): The Rust backend is the **source of truth** for writes. Django ORM is **read-optimized**

---

## Model Organization (Package Structure)

### Solo Edition (`pos-solo/sidecar/models/`)

```python
# models/__init__.py — re-exports all models as package
from models.pos import Category, Product, Customer, Sale, SaleItem, ...
from models.menu import MenuItem, Menu, MenuItemAssignment
from models.node import Node, Heartbeat, NodeEvent
from models.config import DeviceConfig, MasterDevice, CloudLink
from models.sync import SyncLog
```

Each file contains a logical group of models:

| Module | Models | `app_label` | `db_table` prefix |
|--------|--------|-------------|------------------|
| `pos.py` | Category, Product, Customer, Sale, SaleItem, InventoryTransaction, Employee | `pos_unified` | `unified_` |
| `menu.py` | MenuItem, Menu, MenuItemAssignment | `pos_unified` | `unified_` |
| `node.py` | Node, Heartbeat, NodeEvent | `pos_unified` | `unified_` |
| `config.py` | DeviceConfig, MasterDevice, CloudLink | `pos_unified` | `unified_` |
| `sync.py` | SyncLog | `pos_unified` | `unified_` |

### Full Edition (`pos-full/sidecar/models/`)

| Module | Models | `app_label` | `db_table` prefix |
|--------|--------|-------------|------------------|
| `node.py` | Node, Heartbeat, NodeEvent | `pos_full_registry` | `full_` |
| `config.py` | DeviceConfig, MasterDevice, CloudLink | `pos_full_registry` | `full_` |
| `sync.py` | SyncLog | `pos_full_registry` | `full_` |
| `posapp/models.py` | 30+ Rust-backed tables | `posapp` | (same as Rust) |

### Shared Models (`shared/models/`)

| Module | Models | `app_label` | `db_table` |
|--------|--------|-------------|-----------|
| `audit.py` | SignalEvent | `pos_signals` | `pos_signal_events` |
| `approval.py` | SyncApproval | `pos_approval` | `pos_sync_approvals` |
| `token.py` | DeviceToken | `cloud_auth` | `cloud_device_tokens` |

---

## Settings Configuration

```python
# sidecar/settings.py
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': str(BASE_DIR / 'solo_portal.db'),  # or full_portal.db
    }
}

INSTALLED_APPS = [
    'django.contrib.contenttypes',   # Minimal — no auth/sessions needed
]
```

---

## Use Cases

### 1. CRUD via Robyn (`_register_crud`)

```python
from shared.api.crud import _register_crud

_register_crud(app, "products", Product, "Product")
_register_crud(app, "customers", Customer, "Customer")
```

### 2. Complex Queries via sync_to_async

```python
from asgiref.sync import sync_to_async

@sync_to_async
def get_stats():
    return {
        "products": Product.objects.count(),
        "sales": Sale.objects.count(),
        "revenue": Sale.objects.aggregate(total=Sum("total"))["total"],
    }
```

### 3. Django Portal Pages

The Django portal (`manage.py runserver`) uses django-fusion viewsets defined in `shared/portal_viewsets.py`.


---

## Related

| Topic | Path |
|-------|------|
| Sidecar overview | [`README.md`](README.md) |
| Django Ninja plan | [`django-ninja-plan.md`](django-ninja-plan.md) |
| Sidecar API | [`sidecar-api.md`](sidecar-api.md) |
| POS database schema | [`../backend/rust-database.md`](../backend/rust-database.md) |
| Cloud data sync | [`../cloud/README.md`](../cloud/README.md) |
