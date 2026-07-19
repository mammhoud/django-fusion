# 🐍 Django ORM — Sidecar Integration

> How the POS sidecar uses Django ORM to mirror the Rust/SQLite database, enabling Django Admin, fixtures, and complex queries.

---

## Overview

The Full edition sidecar (`pos-full/sidecar/posapp/`) includes Django ORM models that **mirror** the Rust/Diesel SQLite schema. The Solo edition includes a subset for cloud sync.

**Key principle**: The Rust backend is the **source of truth** for writes. Django ORM is **read-optimized** and used for:
- Django Admin dashboard
- Complex reporting queries
- Seed data (fixtures)
- Cloud CRM data export

---

## Model Mirroring Pattern

### Rust Side (Source of Truth)

```rust
// src-tauri/src/db/models.rs
#[derive(Queryable, Insertable, Serialize)]
#[diesel(table_name = products)]
pub struct Product {
    pub id: i32,
    pub name: String,
    pub sku: Option<String>,
    pub price: f64,
    pub category_id: i32,
}
```

### Django Side (Read Mirror)

```python
# sidecar/posapp/models.py
from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)

    class Meta:
        db_table = 'products'       # ← Same SQLite table
        managed = False             # ← Django won't create/alter this table
```

The `managed = False` + `db_table = 'products'` tells Django: "this table already exists in SQLite, don't touch its schema."

---

## Settings Configuration

```python
# sidecar/settings.py
import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(os.path.dirname(__file__), '..', 'restaurant.db'),
        # ↑ Same SQLite file the Rust backend uses
    }
}

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'posapp',           # Django ORM mirror models
    'shared',           # Shared portal models
    'cloud',            # Cloud CRM models (Full only)
]
```

---

## 30 Mirror Models (Full Edition)

| Model | Table | Rust Source |
|-------|-------|------------|
| `Product` | `products` | `db/models.rs` |
| `Category` | `categories` | `db/models.rs` |
| `ProductVariant` | `product_variants` | `db/models.rs` |
| `Inventory` | `inventory` | `db/models.rs` |
| `Order` | `orders` | `db/models.rs` |
| `OrderItem` | `order_items` | `db/models.rs` |
| `Customer` | `customers` | `db/models.rs` |
| `Payment` | `payments` | `db/models.rs` |
| `PaymentMethod` | `payment_methods` | `db/models.rs` |
| `Refund` | `refunds` | `db/models.rs` |
| `Warehouse` | `warehouses` | `db/models.rs` |
| `StockMovement` | `stock_movements` | `db/models.rs` |
| `Supplier` | `suppliers` | `db/models.rs` |
| `PurchaseOrder` | `purchase_orders` | `db/models.rs` |
| `Register` | `registers` | `db/models.rs` |
| `RegisterSession` | `register_sessions` | `db/models.rs` |
| `Setting` | `settings` | `db/models.rs` |
| `TaxRate` | `tax_rates` | `db/models.rs` |
| `Discount` | `discounts` | `db/models.rs` |
| `User` | `users` | `db/models.rs` |
| `Role` | `roles` | `db/models.rs` |
| `UserRole` | `user_roles` | `db/models.rs` |

Plus 8 cloud CRM models in `cloud/models.py` (Full only).

---

## Use Cases

### 1. Django Admin Dashboard

```python
# sidecar/portal/admin.py
from django.contrib import admin
from posapp.models import Product, Order, Customer

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'price', 'category']
    search_fields = ['name', 'sku']
    list_filter = ['category', 'is_active']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer', 'grand_total', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    readonly_fields = ['created_at', 'completed_at']
```

Access at `http://localhost:8765/admin/` when sidecar is running.

### 2. Seed Data (Fixtures)

```bash
# Load seed data into the SQLite database via Django
cd projects/pos/pos-full/sidecar
python manage.py loaddata posapp/fixtures/seed_data.json
```

### 3. Complex Reports

```python
# Use Django ORM for queries that are hard in Rust/Diesel
from posapp.models import Order, OrderItem
from django.db.models import Sum, Count, Q
from django.utils import timezone

def daily_sales_report(date=None):
    if date is None:
        date = timezone.now().date()

    return Order.objects.filter(
        created_at__date=date,
        status='completed'
    ).aggregate(
        total_sales=Sum('grand_total'),
        order_count=Count('id'),
        avg_order=Avg('grand_total'),
    )
```

### 4. Cloud CRM Export

```python
# Export POS data to Cloud CRM via Django ORM
def export_to_cloud_crm():
    products = list(Product.objects.values())
    customers = list(Customer.objects.values())
    orders = list(Order.objects.filter(
        status='completed'
    ).values())

    return {
        'products': products,
        'customers': customers,
        'orders': orders,
    }
```

---

## Minimal Edition: Sanic + Django ORM (No Rust ORM)

For the Minimal edition, you can skip the Rust/Diesel ORM entirely and use:

```
┌──────────────────────┐
│   Vue 3 Frontend     │
│   (Tauri invoke)     │
└──────────┬───────────┘
           │ HTTP (not invoke)
┌──────────▼───────────┐
│   Sanic Server        │
│   port 8765           │
│   + Django ORM        │
└──────────┬───────────┘
           │
┌──────────▼───────────┐
│      SQLite           │
│   (restaurant.db)     │
└──────────────────────┘
```

In this configuration:
- The Vue frontend calls the Sanic API directly (HTTP) instead of Tauri `invoke()`
- Django ORM handles ALL database operations (no Rust ORM)
- The Rust layer just spawns the sidecar — no database operations in Rust
- Ideal for rapid prototyping or when Django expertise > Rust expertise

See [`django-ninja-plan.md`](django-ninja-plan.md) for using Django Ninja Extra instead of Sanic.

---

## Related

| Topic | Path |
|-------|------|
| Sidecar overview | [`README.md`](README.md) |
| Django Ninja plan | [`django-ninja-plan.md`](django-ninja-plan.md) |
| Sidecar API | [`sidecar-api.md`](sidecar-api.md) |
| POS database schema | [`../backend/rust-database.md`](../backend/rust-database.md) |
| Cloud data sync | [`../cloud/README.md`](../cloud/README.md) |
