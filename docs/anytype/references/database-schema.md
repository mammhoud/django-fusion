# Reference — Database Schema

**Type:** Reference 📚
**Tags:** `#pos-mini` `#pos-solo` `#pos-full` `#database`
**Status:** Published
**Category:** Database

---

## pos-mini (SQLite — Rust)

```
products(id, name, price, unit, category_id, is_active, created_at)
categories(id, name)
sales(id, total_amount, currency, order_type, status, table_number, employee_id, created_at)
sale_items(id, sale_id, product_name, price, quantity, unit)
settings(id, restaurant_name, address, phone, email, currency, tax_rate, ...)
employees(id, name, phone, email, employee_type_id, salary, is_active, created_at)
employee_types(id, name, description)
ingredients(id, name, unit, stock, reorder_level, cost_per_unit, is_active)
inventory_transactions(id, ingredient_id, quantity_change, type, note, created_at)
recipes(id, product_id, type, yield_quantity)
recipe_ingredients(id, recipe_id, ingredient_id, quantity, unit)
roles(id, name, permissions, is_active, created_at)
user_roles(user_id, role_id)
```

## pos-solo / pos-full (Sidecar — Django + SQLite)

```python
# pos.py — Core POS models
class Product(models.Model):
    name, price, unit, category, image, border_color, is_active, created_at

class Category(models.Model):
    name, is_active

class Sale(models.Model):
    total_amount, currency, order_type, status, table_number, employee
    delivery_type, delivery_address, created_at

class SaleItem(models.Model):
    sale, product_name, price, quantity, unit

# extra.py — Extended models
class Role(models.Model):
    name, permissions(JSONField), is_active

class Employee(models.Model):
    user(FK), role(FK), phone, salary, is_active

# sync.py — Sync models
class SyncQueue(models.Model):
    node, table_name, record_id, action, payload(JSONField), created_at, synced_at

class Node(models.Model):
    name, device_id(unique), branch(FK), last_seen, is_master

# hr.py — Payroll
class Payroll(models.Model):
    employee(FK), period_start, period_end, regular_hours, overtime_hours
    total_pay, status, created_at
```

---

## Key Relationships

```
Category ──→ Product ←── SaleItem ←── Sale
               │
               └── Recipe ←── RecipeIngredient ←── Ingredient

Employee ←── Sale
Role ──→ Employee
Node ──→ SyncQueue
```

---

## Related Docs
- → `architecture/editions-overview.md` — Edition comparison
- → `features/pos-mini.md` — Rust models
- → `features/pos-solo.md` — Django models
- → `references/tauri-commands.md` — Commands that access these tables
