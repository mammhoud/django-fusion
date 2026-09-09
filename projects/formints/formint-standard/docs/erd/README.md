# Formint POS — Database ERD & Operations Logic

> **Interactive viewer:** open [`index.html`](index.html) in a browser — searchable
> entity list, domain filters, SVG relationship diagram, and per-entity business
> logic derived from the Rust operations modules.
> **Print / PDF export:** click **Print / PDF** in the viewer toolbar — the print
> document contains the cover + stats, the full relationship diagram, the
> foreign-key relation table, and the complete per-entity reference (schema,
> FKs, operations logic). Choose "Save as PDF" in the print dialog.
> **Generated from:** `src-tauri/src/db/schema.rs` by [`scripts/generate-erd.mjs`](../../scripts/generate-erd.mjs).

**Stack:** SQLite via Diesel (Tauri 2 + Rust). Data flow is
`React → Tauri invoke → Rust operation → SQLite`.

## Quick stats

| Metric | Count |
|--------|------:|
| Tables | 40 |
| Relationships (FKs) | 29 |
| Operations modules (`src-tauri/src/operations/`) | 42 |

## Mermaid ER diagram

```mermaid
erDiagram
    currencies {
        INTEGER id PK
        TEXT code
        TEXT name
        TEXT symbol
        REAL exchange_rate
        BOOLEAN is_default
        BOOLEAN is_active
        DATETIME created_at
        DATETIME updated_at
    }
    settings {
        INTEGER id PK
        TEXT (nullable) restaurant_name
        TEXT (nullable) address
        TEXT (nullable) phone
        TEXT (nullable) email
        TEXT (nullable) tax_rate
        TEXT (nullable) tax_id
        TEXT currency
        TEXT (nullable) opening_time
        TEXT (nullable) closing_time
        TEXT (nullable) receipt_footer
        TEXT (nullable) logo
        TEXT (nullable) invoice_logo
        INTEGER dine_in_tables
        REAL delivery_fee
        REAL delivery_fee_per_km
        TEXT (nullable) smtp_server
        INTEGER (nullable) smtp_port
        TEXT (nullable) smtp_username
        TEXT (nullable) smtp_password
        TEXT (nullable) smtp_recipient
        TEXT (nullable) smtp_from_name
        TEXT (nullable) smtp_from_email
        TEXT (nullable) printer_port
        BOOLEAN printer_enabled
    }
    categories {
        INTEGER id PK
        TEXT name
        TEXT (nullable) color
        DATETIME created_at
        DATETIME updated_at
    }
    products {
        INTEGER id PK
        TEXT name
        REAL price
        TEXT unit
        INTEGER (nullable) category_id
        TEXT (nullable) image
        TEXT product_type
        INTEGER prepare_time_minutes
        TEXT (nullable) barcode
        TEXT (nullable) description
        TEXT available_order_types
        DATETIME created_at
        DATETIME updated_at
        BOOLEAN uploaded
        INTEGER (nullable) tax_profile_id
    }
    delivery_types {
        INTEGER id PK
        TEXT name
        TEXT (nullable) description
        REAL fee_multiplier
        BOOLEAN is_active
        DATETIME created_at
        DATETIME updated_at
    }
    employee_types {
        INTEGER id PK
        TEXT name
        TEXT (nullable) description
        BOOLEAN is_active
        DATETIME created_at
        DATETIME updated_at
    }
    employees {
        INTEGER id PK
        TEXT name
        TEXT (nullable) phone
        TEXT (nullable) email
        INTEGER employee_type_id
        REAL salary
        BOOLEAN is_active
        TEXT (nullable) joined_at
        DATETIME created_at
        DATETIME updated_at
        BOOLEAN uploaded
        TEXT (nullable) address
        TEXT (nullable) date_of_birth
        TEXT (nullable) national_id
        TEXT (nullable) emergency_contact
        TEXT pay_frequency
        REAL hourly_rate
        TEXT (nullable) bank_name
        TEXT (nullable) bank_account
        TEXT (nullable) tax_number
        TEXT (nullable) notes
    }
    sales {
        INTEGER id PK
        REAL total_amount
        TEXT currency
        TEXT date
        TEXT time
        TEXT order_type
        TEXT status
        INTEGER (nullable) table_number
        INTEGER (nullable) delivery_type_id
        INTEGER (nullable) delivery_zone_id
        TEXT (nullable) delivery_address
        INTEGER (nullable) employee_id
        INTEGER (nullable) customer_id
        TEXT (nullable) discount_code
        REAL discount_amount
        TEXT payment_method
        DATETIME created_at
        DATETIME updated_at
        BOOLEAN uploaded
        INTEGER (nullable) tax_profile_id
    }
    coupons {
        INTEGER id PK
        TEXT code
        TEXT kind
        REAL value
        REAL (nullable) min_subtotal
        BOOLEAN is_active
        DATETIME created_at
        DATETIME updated_at
    }
    user_actions {
        INTEGER id PK
        TEXT action
        TEXT (nullable) entity_type
        INTEGER (nullable) entity_id
        TEXT (nullable) details
        INTEGER (nullable) user_id
        DATETIME created_at
    }
    sale_items {
        INTEGER id PK
        INTEGER sale_id
        TEXT product_name
        REAL price
        REAL quantity
        TEXT unit
        REAL subtotal
        DATETIME created_at
    }
    ingredients {
        INTEGER id PK
        TEXT name
        TEXT unit
        REAL current_quantity
        REAL reorder_level
        REAL reorder_quantity
        REAL cost_per_unit
        BOOLEAN is_active
        DATETIME created_at
        DATETIME updated_at
        BOOLEAN uploaded
    }
    recipe_types {
        INTEGER id PK
        TEXT name
        TEXT (nullable) description
        BOOLEAN is_active
        DATETIME created_at
        DATETIME updated_at
    }
    recipes {
        INTEGER id PK
        INTEGER product_id
        INTEGER recipe_type_id
        REAL yield_quantity
        BOOLEAN is_active
        DATETIME created_at
        DATETIME updated_at
        BOOLEAN uploaded
    }
    recipe_ingredients {
        INTEGER id PK
        INTEGER recipe_id
        INTEGER ingredient_id
        REAL quantity
        TEXT (nullable) unit
        TEXT (nullable) preparation_note
        DATETIME created_at
        DATETIME updated_at
    }
    inventory_transactions {
        INTEGER id PK
        INTEGER ingredient_id
        TEXT transaction_type
        REAL quantity_change
        INTEGER (nullable) reference_id
        TEXT (nullable) note
        DATETIME created_at
        BOOLEAN uploaded
    }
    inventory_adjustments {
        INTEGER id PK
        INTEGER ingredient_id
        REAL previous_quantity
        REAL new_quantity
        TEXT reason
        TEXT (nullable) created_by
        DATETIME created_at
        BOOLEAN uploaded
    }
    users {
        INTEGER id PK
        TEXT email
        TEXT password_hash
        TEXT name
        DATETIME created_at
        DATETIME updated_at
    }
    roles {
        INTEGER id PK
        TEXT name
        TEXT permissions
        BOOLEAN is_active
        DATETIME created_at
        DATETIME updated_at
    }
    user_roles {
        INTEGER user_id PK
        INTEGER role_id PK
        DATETIME created_at
    }
    report_metadata {
        INTEGER id PK
        TEXT report_type
        TEXT format
        TEXT file_path
        TEXT (nullable) parameters
        INTEGER (nullable) generated_by
        DATETIME created_at
    }
    inventory_alerts {
        INTEGER id PK
        INTEGER ingredient_id
        TEXT alert_type
        TEXT alert_message
        BOOLEAN is_resolved
        DATETIME created_at
        DATETIME (nullable) resolved_at
    }
    suppliers {
        INTEGER id PK
        TEXT name
        TEXT (nullable) contact_name
        TEXT (nullable) email
        TEXT (nullable) phone
        TEXT (nullable) address
        TEXT (nullable) tax_id
        TEXT (nullable) payment_terms
        BOOLEAN is_active
        DATETIME created_at
        DATETIME updated_at
    }
    purchase_orders {
        INTEGER id PK
        INTEGER supplier_id
        TEXT (nullable) reference_number
        TEXT status
        REAL total_amount
        REAL shipping_fee
        DATETIME (nullable) expected_date
        TEXT (nullable) notes
        DATETIME created_at
        DATETIME updated_at
    }
    purchase_order_items {
        INTEGER id PK
        INTEGER purchase_order_id
        INTEGER ingredient_id
        REAL quantity
        REAL cost_per_unit
        REAL received_quantity
    }
    kitchen_tickets {
        INTEGER id PK
        INTEGER sale_id
        TEXT status
        INTEGER priority
        INTEGER prepare_time_minutes
        TEXT (nullable) notes
        DATETIME created_at
        DATETIME (nullable) completed_at
    }
    customers {
        INTEGER id PK
        TEXT name
        TEXT (nullable) phone
        TEXT (nullable) email
        REAL loyalty_points
        TEXT (nullable) notes
        DATETIME created_at
        DATETIME updated_at
    }
    loyalty_transactions {
        INTEGER id PK
        INTEGER customer_id
        INTEGER (nullable) sale_id
        REAL points_change
        TEXT reason
        DATETIME created_at
    }
    receipt_templates {
        INTEGER id PK
        TEXT name
        TEXT template_body
        TEXT (nullable) category
        INTEGER (nullable) recipe_id
        BOOLEAN is_default
        BOOLEAN use_as_template
        BOOLEAN selectable
        TEXT (nullable) steps
        DATETIME created_at
        DATETIME updated_at
    }
    support_messages {
        INTEGER id PK
        TEXT name
        TEXT email
        TEXT (nullable) phone
        TEXT (nullable) subject
        TEXT (nullable) category
        TEXT priority
        TEXT message
        TEXT status
        DATETIME created_at
        DATETIME updated_at
    }
    tax_reports {
        INTEGER id PK
        TEXT period_start
        TEXT period_end
        REAL total_sales
        REAL total_tax
        INTEGER transaction_count
        DATETIME generated_at
    }
    employee_schedules {
        INTEGER id PK
        INTEGER employee_id
        DATETIME shift_start
        DATETIME shift_end
        TEXT status
        TEXT (nullable) notes
        DATETIME created_at
        DATETIME updated_at
    }
    shifts {
        INTEGER id PK
        DATETIME opened_at
        DATETIME (nullable) closed_at
        REAL opening_cash
        REAL (nullable) closing_cash
        REAL (nullable) expected_cash
        REAL (nullable) cash_difference
        TEXT shift_status
        TEXT (nullable) shift_notes
    }
    payrolls {
        INTEGER id PK
        INTEGER employee_id
        TEXT period_start
        TEXT period_end
        REAL regular_hours
        REAL overtime_hours
        REAL total_pay
        TEXT status
        DATETIME created_at
        DATETIME updated_at
    }
    delivery_zones {
        INTEGER id PK
        TEXT name
        REAL base_fee
        REAL fee_per_km
        REAL max_distance
        BOOLEAN is_active
        DATETIME created_at
        DATETIME updated_at
    }
    finance_transactions {
        INTEGER id PK
        TEXT date
        TEXT category_id
        TEXT direction
        REAL amount
        TEXT (nullable) description
        TEXT (nullable) reference
        TEXT created_at
        TEXT updated_at
    }
    budgets {
        INTEGER id PK
        TEXT (nullable) category_id
        TEXT period_start
        TEXT period_end
        REAL amount
        TEXT created_at
        TEXT updated_at
    }
    badges {
        INTEGER id PK
        TEXT name
        TEXT description
        TEXT icon
        TEXT tone
        REAL threshold
        BOOLEAN is_active
        DATETIME created_at
        DATETIME updated_at
    }
    tax_profiles {
        INTEGER id PK
        TEXT name
        REAL rate
        BOOLEAN is_default
        BOOLEAN is_active
        DATETIME created_at
        DATETIME updated_at
    }
    sync_queue {
        INTEGER id PK
        TEXT entity_type
        TEXT entity_id
        TEXT change_type
        INTEGER sync_order
        TEXT status
        INTEGER retry_count
        TEXT error_message
        TEXT payload_json
        TEXT created_at
        TEXT (nullable) flushed_at
    }
    employee_types ||--o{ employees : "employee_type_id"
    categories ||--o{ products : "category_id"
    delivery_types ||--o{ sales : "delivery_type_id"
    employees ||--o{ sales : "employee_id"
    products ||--o{ recipes : "product_id"
    recipe_types ||--o{ recipes : "recipe_type_id"
    recipes ||--o{ recipe_ingredients : "recipe_id"
    ingredients ||--o{ recipe_ingredients : "ingredient_id"
    ingredients ||--o{ inventory_transactions : "ingredient_id"
    ingredients ||--o{ inventory_adjustments : "ingredient_id"
    users ||--o{ user_roles : "user_id"
    roles ||--o{ user_roles : "role_id"
    users ||--o{ report_metadata : "generated_by"
    ingredients ||--o{ inventory_alerts : "ingredient_id"
    suppliers ||--o{ purchase_orders : "supplier_id"
    purchase_orders ||--o{ purchase_order_items : "purchase_order_id"
    ingredients ||--o{ purchase_order_items : "ingredient_id"
    sales ||--o{ kitchen_tickets : "sale_id"
    customers ||--o{ loyalty_transactions : "customer_id"
    sales ||--o{ loyalty_transactions : "sale_id"
    employees ||--o{ employee_schedules : "employee_id"
    employees ||--o{ payrolls : "employee_id"
    sales ||--o{ sale_items : "sale_id"
    delivery_zones ||--o{ sales : "delivery_zone_id"
    customers ||--o{ sales : "customer_id"
    tax_profiles ||--o{ sales : "tax_profile_id"
    tax_profiles ||--o{ products : "tax_profile_id"
    recipes ||--o{ receipt_templates : "recipe_id"
    users ||--o{ user_actions : "user_id"
```

## Domain map

| Domain | Tables |
|--------|--------|
| **Auth & Users** | `users`, `roles`, `user_roles`, `user_actions` |
| **Catalog** | `categories`, `products`, `delivery_types`, `delivery_zones`, `tax_profiles` |
| **Sales & Orders** | `sales`, `sale_items`, `coupons`, `kitchen_tickets` |
| **Inventory & Recipes** | `ingredients`, `recipe_types`, `recipes`, `recipe_ingredients`, `inventory_transactions`, `inventory_adjustments`, `inventory_alerts`, `suppliers`, `purchase_orders`, `purchase_order_items` |
| **HR & Payroll** | `employee_types`, `employees`, `employee_schedules`, `payrolls` |
| **Finance & Tax** | `currencies`, `tax_reports`, `report_metadata`, `finance_transactions`, `budgets`, `tax_profiles` |
| **CRM & Loyalty** | `customers`, `loyalty_transactions`, `receipt_templates`, `badges` |
| **Operations & Sync** | `settings`, `shifts`, `support_messages`, `sync_queue` |

## Entity reference & operations logic matrix

Each entity lists the operations module(s) that own its business logic
(`src-tauri/src/operations/*.rs`). "Logical FK" = foreign-key-style reference
that is not declared via `diesel::joinable!` but is enforced/assumed in code.

| # | Entity | Domain | Key logic | Operations module(s) |
|---|--------|--------|-----------|----------------------|
| 1 | `currencies` | Finance & Tax | Multi-currency support: full CRUD, one row flagged `is_default`; exchange rates convert sale totals | `currency` |
| 2 | `settings` | Operations & Sync | Single-row restaurant config (branding, tax %, delivery fees, SMTP, thermal printer); `save_settings` upserts | `settings` |
| 3 | `categories` | Catalog | Product categories: plain CRUD with optional color for UI pills | `categories` |
| 4 | `products` | Catalog | Product CRUD; `uploaded` flag drives offline→cloud sync via dump; optional `tax_profile_id` selects sale tax rate | `products` |
| 5 | `delivery_types` | Catalog | Delivery channel presets (fee multiplier); soft delete via `is_active` | `delivery_types` |
| 6 | `employee_types` | HR & Payroll | Job-type presets (waiter, chef, …); soft delete via `is_active` | `employee_types` |
| 7 | `employees` | HR & Payroll | Records incl. payroll settings (salary vs hourly, bank details); soft delete; `uploaded` sync flag | `employees` |
| 8 | `sales` | Sales & Orders | Atomic insert: sale + `sale_items` in one transaction, then auto-creates a kitchen ticket with prep time by order type (dine-in 15, takeaway 20, delivery 25 min); `refund_sale` marks `status=refunded` (once only) | `sales`, `transactions`, `analytics` |
| 9 | `coupons` | Sales & Orders | Discount codes: kind (percent/flat), `min_subtotal` gate; `get_active_coupons` feeds checkout; sales record applied code | `coupons` |
| 10 | `user_actions` | Auth & Users | Audit log: every sale/coupon/offer action appends a row via `add_user_action`; queried by entity or globally | `user_actions` |
| 11 | `sale_items` | Sales & Orders | Line items written atomically with the parent sale; `get_sale_with_items` loads sale + lines for receipts/KDS | `sales` |
| 12 | `ingredients` | Inventory & Recipes | Stock item CRUD with reorder levels; soft delete via `is_active`; `uploaded` sync flag. Stock mutated by `inventory_transactions`, never directly | `ingredients` |
| 13 | `recipe_types` | Inventory & Recipes | Recipe classification (e.g. standard, bulk); referenced by `recipes`, no standalone CRUD module — seeded via migrations | `recipes` |
| 14 | `recipes` | Inventory & Recipes | Recipe = product × recipe_type with yield; `create_recipe` inserts recipe + ingredients; soft delete; `uploaded` sync flag | `recipes` |
| 15 | `recipe_ingredients` | Inventory & Recipes | Bill-of-materials lines: ingredient quantity per recipe, with preparation note and optional unit override | `recipes` |
| 16 | `inventory_transactions` | Inventory & Recipes | Stock movements ledger (sale deduction, purchase receipt, adjustment); rejects negative stock with `InsufficientStockError` + rollback | `inventory_transactions` |
| 17 | `inventory_adjustments` | Inventory & Recipes | Manual count corrections storing previous→new quantity and reason; deleting an adjustment reverses its stock delta | `inventory_transactions` |
| 18 | `users` | Auth & Users | Auth lifecycle: account setup, login/verify, password change & reset, superuser bootstrap; roles join via `user_roles` for RBAC | `auth`, `roles` |
| 19 | `roles` | Auth & Users | RBAC: permission catalog (comma-separated flags in `permissions`), role CRUD with soft delete, assignment via `user_roles` | `roles`, `permissions` |
| 20 | `user_roles` | Auth & Users | Join table between users and roles; `assign_role` / `remove_role` manage membership; `get_user_roles` lists a user's roles | `roles` |
| 21 | `report_metadata` | Finance & Tax | Generated report registry: type, format, file path, params, generating user | `reports` |
| 22 | `inventory_alerts` | Inventory & Recipes | Low-stock alert records; no standalone operations module — rows consumed by exports/dump for cloud sync | — |
| 23 | `suppliers` | Inventory & Recipes | Vendor CRUD with tax/payment terms; soft delete via `is_active` | `suppliers` |
| 24 | `purchase_orders` | Inventory & Recipes | Procurement workflow: PO header (status, totals, expected date) plus items; receiving updates item quantities | `purchase_orders` |
| 25 | `purchase_order_items` | Inventory & Recipes | PO lines: ingredient, ordered quantity, cost per unit, received quantity for partial receiving | `purchase_orders` |
| 26 | `kitchen_tickets` | Sales & Orders | KDS workflow: status transitions, priority, `count_pending_tickets`, category resolution for filter pills; auto-created by `add_sale` | `kitchen_tickets`, `sales` |
| 27 | `customers` | CRM & Loyalty | Customer CRUD + loyalty balance; `add_loyalty_transaction` updates `loyalty_points` atomically with the transaction | `customers` |
| 28 | `loyalty_transactions` | CRM & Loyalty | Points ledger: signed `points_change` per sale; joined with customer name for the loyalty report | `customers` |
| 29 | `receipt_templates` | CRM & Loyalty | Recipe/kitchen "notes": templates with steps, per-recipe notes, default + selectable flags | `notes` |
| 30 | `support_messages` | Operations & Sync | Support inbox: message CRUD with priority/status workflow | `support_messages` |
| 31 | `tax_reports` | Finance & Tax | Periodic tax summaries (total sales, total tax, transaction count) | `tax_reports` |
| 32 | `employee_schedules` | HR & Payroll | Shift scheduling: employee × shift window with status and notes | `employee_schedules` |
| 33 | `shifts` | Operations & Sync | Cash drawer lifecycle; `open_shift` refuses a second open shift; `close_shift` computes expected cash from cash sales in the shift window and the cash difference | `shifts` |
| 34 | `payrolls` | HR & Payroll | Payslips per period; `generate_payrolls` is idempotent: monthly → salary, hourly → rate × 160h, skips employees already covered | `payrolls` |
| 35 | `delivery_zones` | Catalog | Zones with base fee, per-km fee and max distance; soft delete via `is_active` | `delivery_zones` |
| 36 | `finance_transactions` | Finance & Tax | Income/expense ledger with direction + category; powers finance summary (totals per category, budget vs actual) | `finance` |
| 37 | `budgets` | Finance & Tax | Period budgets per category (or global); `get_finance_summary` computes spent/remaining/over | `finance` |
| 38 | `badges` | CRM & Loyalty | Customer reward badges with threshold, icon and tone | `badges` |
| 39 | `tax_profiles` | Finance & Tax | Named tax rates; products and sales reference one profile; `compute_tax` applies rate per sale totals | `tax_profile`, `tax` |
| 40 | `sync_queue` | Operations & Sync | Offline→cloud sync FIFO: `tag_for_sync` enqueues mutations, `dispatch_mutation` fans out, `mark_flushed`/`mark_failed` track retries, `flush_pending_sync` pushes on reconnect | `sync_queue`, `dispatcher`, `server_reconnect` |

## Regenerating & staleness check

The diagram, data file and this README are generated:

```bash
node scripts/generate-erd.mjs        # regenerate in place
node scripts/check-erd-stale.mjs     # CI-style: fail (exit 1) if docs/erd is stale
pnpm check:erd                       # same, via package.json
```

`check-erd-stale.mjs` regenerates `erd-data.js`/`erd.mmd` into a temp directory
and compares them with the committed files, so CI (or pre-push) can fail when
`src-tauri/src/db/schema.rs` or `src-tauri/src/operations/*.rs` changed but the
docs were not regenerated. It is covered by Vitest
(`src/test/scripts/check-erd-stale.test.ts`).

Edit the *source of truth* (`src-tauri/src/db/schema.rs` for tables/columns/FKs,
the operations modules for function lists) and re-run; do not hand-edit
`docs/erd/erd-data.js` or `docs/erd/erd.mmd`.

## Conventions

- **Physical FKs** (from `diesel::joinable!`) and **logical FKs** (foreign-key
  columns joined in code but not declared as joinables) are both listed per
  entity; the viewer marks logical relations with a dashed style.
- `uploaded` columns everywhere are offline→cloud sync markers; `is_active` is
  the soft-delete flag; `created_at`/`updated_at` are universal audit columns.
- Stock is only mutated through `inventory_transactions`/adjustments — sales
  deduct via recipe ingredients.