# Table & Column Name Comparison Across POS Editions

> **Purpose:** Identify which table names and column names are **identical** across editions vs. those that differ, so migration scripts and shared frontend code can target the common subset.

## Edition Key

| Edition | DB Layer | Table Names | Prefix |
|---------|----------|------------|--------|
| **Minimal** | Diesel ORM (Rust) | Raw SQLite | *(no prefix)* |
| **Solo** | Django ORM (Python server) | Managed by Django | `full_` for core, `pos_crm_` for CRM, `pos_sync_` / `pos_signal_` for system |
| **Full** | Django ORM (Python server) | Managed by Django | Same as Solo, plus additional CRM tables |

---

## 1. Tables With Identical Names Across All Three Editions

No tables have *identical* names across all three editions because the Django server uses the `full_` prefix. However, these tables are **semantically equivalent**:

| Minimal (Diesel) | Solo (Django) | Full (Django) | Match |
|:----------------|:--------------|:--------------|:------|
| `products` | `full_products` | `full_products` | ⚠️ diff prefix only |
| `categories` | `full_categories` | `full_categories` | ⚠️ diff prefix only |
| `sales` | `full_sales` | `full_sales` | ⚠️ diff prefix only |
| `sale_items` | `full_sale_items` | `full_sale_items` | ⚠️ diff prefix only |
| `customers` | `full_customers` | `full_customers` | ⚠️ diff prefix only |
| `employees` | `full_employees` | `full_employees` | ⚠️ diff prefix only |
| `ingredients` | `full_ingredients` | `full_ingredients` | ⚠️ diff prefix only |
| `recipes` | `full_recipes` | `full_recipes` | ⚠️ diff prefix only |
| `suppliers` | `full_suppliers` | `full_suppliers` | ⚠️ diff prefix only |
| `purchase_orders` | `full_purchase_orders` | `full_purchase_orders` | ⚠️ diff prefix only |
| `purchase_order_items` | `full_purchase_order_items` | `full_purchase_order_items` | ⚠️ diff prefix only |
| `kitchen_tickets` | `full_kitchen_tickets` | `full_kitchen_tickets` | ⚠️ diff prefix only |
| `receipt_templates` | `full_receipt_templates` | `full_receipt_templates` | ⚠️ diff prefix only |
| `inventory_transactions` | `full_inventory` | `full_inventory` | ❌ name completely changed |
| `inventory_adjustments` | `full_inventory_adjustments` | `full_inventory_adjustments` | ⚠️ diff prefix only |
| `roles` | `full_roles` | `full_roles` | ⚠️ diff prefix only |
| `payrolls` | `full_payroll` | `full_payroll` | ⚠️ diff singular vs plural |
| `employee_schedules` | `full_employee_schedules` | `full_employee_schedules` | ⚠️ diff prefix only |
| `tax_reports` | `full_tax_reports` | `full_tax_reports` | ⚠️ diff prefix only |

---

## 2. Tables Unique to Minimal (No Django Equivalent)

These Diesel tables have **no counterpart** in the Solo/Full Django server. Data from these tables must be either dropped, merged, or transformed during migration:

| Minimal Table | Status | What Happens to the Data |
|:-------------|:-------|:------------------------|
| `settings` | ❌ No direct Django equivalent | Transformed into `DeviceConfig` KV pairs |
| `delivery_types` | ❌ No Django model | Data preserved in Diesel backup (not migrated) |
| `employee_types` | ❌ No Django model | Mapped to Employee.role CharField (int → string) |
| `recipe_types` | ❌ No Django model | Data preserved in Diesel backup (not migrated) |
| `recipe_ingredients` | 🟡 Merged | Merged into Recipe model (instructions field) |
| `inventory_alerts` | ❌ No Django model | Data preserved in Diesel backup (not migrated) |
| `report_metadata` | ❌ No Django model | Data preserved in Diesel backup (not migrated) |
| `users` | ⚠️ Replaced | Replaced by django-allauth User model |
| `user_roles` | ⚠️ Replaced | Replaced by allauth Group assignments |
| `loyalty_transactions` | 🟡 Integrated | Aggregated into Customer.loyalty_points |
| `sale_items.subtotal` | 🟡 Computed | Diesel uses `GENERATED ALWAYS AS (price * quantity)`, Django stores explicitly |

---

## 3. Tables Unique to Solo/Full (No Diesel Equivalent)

These exist only in the server's Django ORM. They don't need migration from Minimal:

| Django Table | Model | Purpose | Present In |
|:-------------|:------|:--------|:-----------|
| `full_menu_items` | `MenuItem` | Menu item catalog | Solo + Full |
| `full_menus` | `Menu` | Named menu collections | Solo + Full |
| `full_menu_assignments` | `MenuItemAssignment` | Menu-item link table | Solo + Full |
| `full_nodes` | `Node` | Registered POS nodes | Solo + Full |
| `full_heartbeats` | `Heartbeat` | Node heartbeat log | Solo + Full |
| `full_node_events` | `NodeEvent` | Node lifecycle events | Solo + Full |
| `full_device_configs` | `DeviceConfig` | Device configuration KV | Solo + Full |
| `full_master_devices` | `MasterDevice` | Master device registry | Solo + Full |
| `full_cloud_links` | `CloudLink` | Cloud connection config | Solo + Full |
| `full_sync_logs` | `SyncLog` | Data sync audit log | Solo + Full |
| `full_notes` | `Note` | User notes with draft | Solo + Full |
| `full_support_tickets` | `SupportTicket` | Support ticket system | Solo + Full |
| `pos_crm_companies` | `Company` | CRM company records | Solo + Full (models exist in both; routes may be edition-gated) |
| `pos_crm_pipelines` | `Pipeline` | CRM pipeline stages | Solo + Full |
| `pos_crm_stages` | `Stage` | CRM pipeline stages | Solo + Full |
| `pos_crm_contacts` | `Contact` | CRM contact records | Solo + Full |
| `pos_crm_deals` | `Deal` | CRM deal tracking | Solo + Full |
| `pos_crm_activities` | `Activity` | CRM activity log | Solo + Full |
| `pos_crm_notes` | `CRMNote` | CRM note records | Solo + Full |
| `pos_sync_approvals` | `SyncApproval` | Moderation/approval workflow | **Full only** |
| `pos_signal_events` | `SignalEvent` | Audit trail for signals | Solo + Full |
| `cloud_device_tokens` | `DeviceToken` | Device auth tokens | Solo + Full (via django-fusion) |

---

## 4. Column Name Comparison — Identical Names

These **column names are identical** across all editions where the table exists:

| Table | Column Name | Minimal (Diesel) | Solo (Django) | Full (Django) |
|:------|:------------|:-----------------|:--------------|:--------------|
| *all* | `id` | ✅ `INTEGER PK` | ✅ `BigAutoField PK` | ✅ `BigAutoField PK` |
| *all* | `created_at` | ✅ `TIMESTAMP` | ✅ `DateTimeField` | ✅ `DateTimeField` |
| *all* | `updated_at` | ✅ `TIMESTAMP` | ✅ `DateTimeField` | ✅ `DateTimeField` |
| `products` | `name` | ✅ `TEXT NOT NULL` | ✅ `CharField(200)` | ✅ `CharField(200)` |
| `products` | `price` | ✅ `REAL` | ✅ `DecimalField(10,2)` | ✅ `DecimalField(10,2)` |
| `products` | `border_color` | ✅ `TEXT (nullable)` | ✅ `CharField(7)` | ✅ `CharField(7)` |
| `categories` | `name` | ✅ `TEXT UNIQUE` | ✅ `CharField(200)` | ✅ `CharField(200)` |
| `categories` | `id` | ✅ | ✅ | ✅ |
| `customers` | `phone` | ✅ `TEXT (nullable)` | ✅ `CharField(20)` | ✅ `CharField(20)` |
| `customers` | `email` | ✅ `TEXT (nullable)` | ✅ `EmailField` | ✅ `EmailField` |
| `customers` | `loyalty_points` | ✅ `REAL` | ✅ `IntegerField` | ✅ `IntegerField` |
| `customers` | `notes` | ✅ `TEXT (nullable)` | ✅ `TextField` | ✅ `TextField` |
| `employees` | `phone` | ✅ `TEXT (nullable)` | ✅ `CharField(20)` | ✅ `CharField(20)` |
| `employees` | `email` | ✅ `TEXT (nullable)` | ✅ `EmailField` | ✅ `EmailField` |
| `employees` | `is_active` | ✅ `BOOLEAN` | ✅ `BooleanField` | ✅ `BooleanField` |
| `sale_items` | `product_name` | ✅ `TEXT` | ✅ `CharField(200)` | ✅ `CharField(200)` |
| `sale_items` | `quantity` | ✅ `REAL` (can be fraction) | ✅ `IntegerField` | ✅ `IntegerField` |

| `ingredients` | `name` | ✅ `TEXT UNIQUE` | ✅ `CharField(200)` | ✅ `CharField(200)` |
| `ingredients` | `unit` | ✅ `TEXT` | ✅ `CharField(50)` | ✅ `CharField(50)` |
| `ingredients` | `current_quantity` | ✅ `REAL` | ✅ `DecimalField(12,3)` | ✅ `DecimalField(12,3)` |
| `ingredients` | `reorder_level` | ✅ `REAL` | ✅ `DecimalField(12,3)` | ✅ `DecimalField(12,3)` |
| `ingredients` | `reorder_quantity` | ✅ `REAL` | ✅ `DecimalField(12,3)` | ✅ `DecimalField(12,3)` |
| `ingredients` | `cost_per_unit` | ✅ `REAL` | ✅ `DecimalField(10,2)` | ✅ `DecimalField(10,2)` |
| `ingredients` | `is_active` | ✅ `BOOLEAN` | ✅ `BooleanField` | ✅ `BooleanField` |
| `suppliers` | `name` | ✅ `TEXT` | ✅ `CharField(200)` | ✅ `CharField(200)` |
| `suppliers` | `contact_name` | ✅ `TEXT (nullable)` | ✅ `CharField(200)` | ✅ `CharField(200)` |
| `suppliers` | `email` | ✅ `TEXT (nullable)` | ✅ `EmailField` | ✅ `EmailField` |
| `suppliers` | `phone` | ✅ `TEXT (nullable)` | ✅ `CharField(50)` | ✅ `CharField(50)` |
| `suppliers` | `is_active` | ✅ `BOOLEAN` | ✅ `BooleanField` | ✅ `BooleanField` |
| `kitchen_tickets` | `status` | ✅ `TEXT` | ✅ `CharField(20)` | ✅ `CharField(20)` |
| `kitchen_tickets` | `priority` | ✅ `INTEGER` | ✅ `IntegerField` | ✅ `IntegerField` |
| `kitchen_tickets` | `notes` | ✅ `TEXT (nullable)` | ✅ `TextField` | ✅ `TextField` |
| `kitchen_tickets` | `completed_at` | ✅ `TIMESTAMP (nullable)` | ✅ `DateTimeField (null)` | ✅ `DateTimeField (null)` |

---

## 5. Column Name Comparison — Different Names

These columns have **different names** or **different types** across editions:

| Table | Minimal Column | Type | Django Column | Type | Issue |
|:------|:---------------|:-----|:--------------|:-----|:------|
| `products` | `category_id` | `INTEGER FK` | `category` | `ForeignKey` | Different FK field name |
| `products` | `image` | `TEXT (nullable)` | `image_url` | `URLField` | Renamed + type change |
| `products` | `uploaded` | `BOOLEAN` | *(none)* | — | No sync flag in Diesel style |
| `products` | `unit` | `TEXT` | *(none)* | — | Dropped in Django |
| `products` | `product_type` | `TEXT` | *(none)* | — | Dropped in Django |
| `products` | *(none)* | — | `sku` | `CharField(50)` | New in Django |
| `products` | *(none)* | — | `cost_price` | `DecimalField(10,2)` | New in Django |
| `products` | *(none)* | — | `tax_rate` | `CharField(20)` | New in Django |
| `products` | *(none)* | — | `barcode` | `CharField(100)` | New in Django |
| `products` | *(none)* | — | `stock_quantity` | `IntegerField` | New in Django |
| `products` | *(none)* | — | `description` | `TextField` | New in Django |
| `categories` | *(none)* | — | `slug` | `SlugField` | New in Django |
| `categories` | *(none)* | — | `description` | `TextField` | New in Django |
| `categories` | *(none)* | — | `display_order` | `IntegerField` | New in Django |
| `categories` | *(none)* | — | `is_active` | `BooleanField` | New in Django |
| `sales` | `total_amount` | `REAL` | `total` | `DecimalField` | Renamed |
| `sales` | `date` | `TEXT (date)` | `sale_date` | `DateTimeField` | Combined into one |
| `sales` | `time` | `TEXT (time)` | *(merged)* | — | Merged into sale_date |
| `sales` | `currency` | `TEXT` | *(none)* | — | Dropped in Django |
| `sales` | `order_type` | `TEXT` | *(none)* | — | Dropped in Django |
| `sales` | `table_number` | `INTEGER (nullable)` | *(none)* | — | Dropped in Django |
| `sales` | `delivery_type_id` | `INTEGER FK (nullable)` | *(none)* | — | Dropped in Django |
| `sales` | `delivery_address` | `TEXT (nullable)` | *(none)* | — | Dropped in Django |
| `sales` | `employee_id` | `INTEGER FK (nullable)` | *(none)* | — | Dropped in Django |
| `sales` | `uploaded` | `BOOLEAN` | *(none)* | — | No sync flag |
| `sales` | `customer_id` | `INTEGER FK (nullable)` | `customer` | `ForeignKey` | Different FK field name |
| `sales` | *(none)* | — | `subtotal` | `DecimalField(12,2)` | New in Django |
| `sales` | *(none)* | — | `tax_amount` | `DecimalField(10,2)` | New in Django |
| `sales` | *(none)* | — | `discount_amount` | `DecimalField(10,2)` | New in Django |
| `sales` | *(none)* | — | `payment_method` | `CharField(20)` | New in Django |
| `sales` | *(none)* | — | `cashback_amount` | `DecimalField(10,2)` | New in Django |
| `sale_items` | `price` | `REAL` | `unit_price` | `DecimalField(10,2)` | Renamed |
| `sale_items` | `subtotal` | `GENERATED COLUMN` | `line_total` | `DecimalField(12,2)` | Renamed |
| `sale_items` | `unit` | `TEXT` | *(none)* | — | Dropped in Django |
| `sale_items` | `sale_id` | `INTEGER FK` | `sale` | `ForeignKey` | Different FK field name |
| `sale_items` | *(none)* | — | `product` | `ForeignKey` | New FK in Django |
| `sale_items` | *(none)* | — | `notes` | `CharField(255)` | New in Django |
| `customers` | `name` | `TEXT` | `first_name` / `last_name` | `CharField(100)` | Split into two |
| `customers` | *(none)* | — | `first_name` | `CharField(100)` | New split field |
| `customers` | *(none)* | — | `last_name` | `CharField(100)` | New split field |
| `customers` | *(none)* | — | `total_spent` | `DecimalField(12,2)` | New in Django |
| `customers` | *(none)* | — | `is_active` | `BooleanField` | New in Django |
| `employees` | `name` | `TEXT` | `first_name` / `last_name` | `CharField(100)` | Split into two |
| `employees` | `employee_type_id` | `INTEGER FK` | `role` | `CharField(20)` | FK → choice string |
| `employees` | `salary` | `REAL` | `hourly_rate` | `DecimalField(8,2)` | Renamed + changed meaning |
| `employees` | `joined_at` | `TEXT (nullable)` | *(none)* | — | Dropped in Django |
| `employees` | `uploaded` | `BOOLEAN` | *(none)* | — | No sync flag |
| `employees` | *(none)* | — | `first_name` | `CharField(100)` | New split field |
| `employees` | *(none)* | — | `last_name` | `CharField(100)` | New split field |
| `employees` | *(none)* | — | `pin_code` | `CharField(6)` | New in Django |
| `inventory_transactions` | `ingredient_id` | `INTEGER FK` | `product` | `ForeignKey` | FK to Product, not Ingredient |
| `inventory_transactions` | `quantity_change` | `REAL` | `quantity` | `IntegerField` | Renamed + type change |
| `inventory_transactions` | `reference_id` | `INTEGER (nullable)` | `reference` | `CharField(100)` | Different type entirely |
| `inventory_transactions` | `note` | `TEXT (nullable)` | `notes` | `TextField` | Pluralized |
| `inventory_transactions` | *(none)* | — | `shipping_fee` | `DecimalField(10,2)` | New in Django |
| `inventory_transactions` | *(none)* | — | `created_by` | `CharField(100)` | New in Django |
| `inventory_transactions` | *(none)* | — | `inventory_id` | `CharField(50)` | New in Django |
| `recipes` | `product_id` | `INTEGER FK` | `product` | `ForeignKey` | Different FK field name |
| `recipes` | `recipe_type_id` | `INTEGER FK` | *(none)* | — | Dropped (no recipe_types) |
| `recipes` | `yield_quantity` | `REAL` | `yield_quantity` | `DecimalField(10,2)` | Same name, different type |
| `recipes` | `uploaded` | `BOOLEAN` | *(none)* | — | No sync flag |
| `recipes` | *(none)* | — | `name` | `CharField(200)` | New in Django |
| `recipes` | *(none)* | — | `instructions` | `TextField` | New in Django |
| `purchase_orders` | `supplier_id` | `INTEGER FK` | `supplier` | `ForeignKey` | Different FK field name |
| `purchase_orders` | `reference_number` | `TEXT (nullable)` | `reference_number` | `CharField(100)` | Same name |
| `purchase_orders` | `total_amount` | `REAL` | `total_amount` | `DecimalField(12,2)` | Same name, diff type |
| `purchase_orders` | `shipping_fee` | `REAL` | *(none)* | — | Dropped in Django |
| `purchase_orders` | `expected_date` | `TIMESTAMP (nullable)` | `expected_date` | `DateField (null)` | Same name, type change |
| `purchase_orders` | `notes` | `TEXT (nullable)` | `notes` | `TextField` | Same name |
| `receipt_templates` | `name` | `TEXT` | `name` | `CharField(200)` | Same name |
| `receipt_templates` | `template_body` | `TEXT` | `template_html` | `TextField` | Renamed |
| `receipt_templates` | `category` | `TEXT (nullable)` | *(none)* | — | Dropped in Django |
| `receipt_templates` | `is_default` | `BOOLEAN` | `is_default` | `BooleanField` | Same name |
| `receipt_templates` | *(none)* | — | `description` | `TextField` | New in Django |
| `receipt_templates` | *(none)* | — | `template_css` | `TextField` | New in Django |
| `payrolls` | `employee_id` | `INTEGER FK` | `employee` | `ForeignKey` | Different FK field name |
| `payrolls` | `period_start` | `TEXT` | `period_start` | `DateField` | Same name, diff type |
| `payrolls` | `period_end` | `TEXT` | `period_end` | `DateField` | Same name, diff type |
| `payrolls` | `regular_hours` | `REAL` | `regular_hours` | `DecimalField(8,2)` | Same name, diff type |
| `payrolls` | `overtime_hours` | `REAL` | `overtime_hours` | `DecimalField(8,2)` | Same name, diff type |
| `payrolls` | `total_pay` | `REAL` | `total_pay` | `DecimalField(12,2)` | Same name, diff type |
| `payrolls` | `status` | `TEXT` | `status` | `CharField(20)` | Same name |
| `payrolls` | *(none)* | — | `base_salary` | `DecimalField(10,2)` | New in Django |
| `payrolls` | *(none)* | — | `deductions` | `DecimalField(10,2)` | New in Django |
| `payrolls` | *(none)* | — | `bonuses` | `DecimalField(10,2)` | New in Django |
| `payrolls` | *(none)* | — | `net_pay` | `DecimalField(10,2)` | New in Django |
| `employee_schedules` | `employee_id` | `INTEGER FK` | `employee` | `ForeignKey` | Different FK field name |
| `employee_schedules` | `shift_start` | `TIMESTAMP` | `start_time` | `TimeField` | Renamed + type change |
| `employee_schedules` | `shift_end` | `TIMESTAMP` | `end_time` | `TimeField` | Renamed + type change |
| `employee_schedules` | `status` | `TEXT` | `status` | `CharField(20)` | Same name |
| `employee_schedules` | `notes` | `TEXT (nullable)` | `notes` | `TextField` | Same name |
| `employee_schedules` | *(none)* | — | `day_of_week` | `CharField(10)` | New in Django |
| `tax_reports` | `period_start` | `TEXT` | `period_start` | `DateField` | Same name, diff type |
| `tax_reports` | `period_end` | `TEXT` | `period_end` | `DateField` | Same name, diff type |
| `tax_reports` | `total_sales` | `REAL` | `total_sales` | `DecimalField(12,2)` | Same name, diff type |
| `tax_reports` | `total_tax` | `REAL` | `total_tax` | `DecimalField(12,2)` | Same name, diff type |
| `tax_reports` | `transaction_count` | `INTEGER` | `transaction_count` | `IntegerField` | Same name |
| `tax_reports` | `generated_at` | `TIMESTAMP` | `created_at` | `DateTimeField` | Renamed |

---

## 6. Sync-Tracking Fields (Django-Only)

Every Django model in Solo/Full has these extra fields that don't exist in the Diesel schema:

| Field | Type | Purpose |
|:------|:-----|:--------|
| `is_synced` | `BooleanField (db_index=True)` | Whether record has been synced to cloud |
| `synced_at` | `DateTimeField (null=True)` | When it was last synced |
| `sync_status` | `CharField(20)` | State machine: `pending` / `synced` / `failed` |

**Total additional fields per model:** 3 sync fields + model-specific new fields (varies per model).

---

## 7. Summary Statistics

| Metric | Count |
|:-------|:------|
| Minimal tables total | **29** |
| Solo/Full Django models total | **30** |
| Tables with identical names (modulo prefix) | **18** (of 18 comparable) |
| Tables with resolved name differences | **2** (`inventory_transactions` → `full_inventory`, `payrolls` → `full_payroll`) |
| Tables unique to Minimal (no Django equivalent) | **7** (`settings`, `delivery_types`, `employee_types`, `recipe_types`, `recipe_ingredients`, `inventory_alerts`, `report_metadata`) |
| Tables replaced (auth) | **2** (`users`, `user_roles`) |
| Tables merged | **1** (`loyalty_transactions` into `Customer`) |
| Tables unique to Solo/Full | **14** (menu, node, config, sync, notes, support, CRM, etc.) |
| Columns with identical names (same table, same purpose) | **~45** |
| Columns with different names (same purpose) | **~20** |
| Columns new in Django (no Diesel equivalent) | **~35** |
| Columns dropped in Django (Diesel only) | **~15** |

---

## 8. Key Takeaways for Migration Script

1. **The `full_` prefix is universal** — every Solo/Full Django table starts with `full_` (except CRM `pos_crm_` and system `pos_sync_`/`pos_signal_` tables). The migration must add `full_` to all table references.

2. **FK fields renamed** — Diesel uses `category_id`, `employee_id`, `supplier_id`, etc. as raw integer columns. Django uses `category`, `employee`, `supplier` as ForeignKey ORM fields. The migration must map `column_id → column` in both directions.

3. **Three tables renamed beyond prefixing:**
   - `inventory_transactions` → `full_inventory` (completely different name)
   - `payrolls` → `full_payroll` (plural → singular)
   - `sale_items.subtotal` → `sale_items.line_total`

4. **Name splitting** — `customers.name` and `employees.name` (single TEXT) → `first_name` / `last_name` (two CharFields). Migration must put the whole string into `first_name` and leave `last_name` empty.

5. **Type changes** — `REAL` → `Decimal` (all money fields), `INTEGER` → `BigAutoField` (PKs), `TEXT (timestamp)` → `DateTimeField` (dates).

6. **No sync fields in Diesel** — The `is_synced / synced_at / sync_status` triad is exclusive to Django. All migrated records must be marked as synced.

7. **Auth is completely replaced** — No migration of `users` or `user_roles` to Django ORM tables; use allauth's management commands instead.
