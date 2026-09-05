# 🦀 Rust SQLite ERD — Formint Community (Diesel)

> **Purpose:** Document the Formint Community SQLite database (`restaurant.db`)
> — every Diesel table with its relations, plus the Rust module map that owns
> each concern.
> **Status:** Active · **Owner:** Formints (Community edition)

---

## 1. Rendered ERD

```mermaid
erDiagram
    CATEGORIES ||--o{ PRODUCTS : contains
    PRODUCTS ||--o{ SALE_ITEMS : sold_as
    PRODUCTS ||--o{ RECIPES : assembled_by
    RECIPES ||--o{ RECIPE_INGREDIENTS : uses
    INGREDIENTS ||--o{ RECIPE_INGREDIENTS : in
    INGREDIENTS ||--o{ INVENTORY_TRANSACTIONS : tracked_by
    INGREDIENTS ||--o{ INVENTORY_ADJUSTMENTS : adjusted_by
    INGREDIENTS ||--o{ INVENTORY_ALERTS : triggers
    INGREDIENTS ||--o{ PURCHASE_ORDER_ITEMS : ordered_as
    PURCHASE_ORDERS ||--o{ PURCHASE_ORDER_ITEMS : contains
    SUPPLIERS ||--o{ PURCHASE_ORDERS : supplies
    SALES ||--o{ SALE_ITEMS : contains
    SALES ||--o{ KITCHEN_TICKETS : opens
    SALES ||--o{ LOYALTY_TRANSACTIONS : earns
    SALES }o--|| DELIVERY_TYPES : uses
    SALES }o--|| EMPLOYEES : handled_by
    EMPLOYEES ||--o{ EMPLOYEE_SCHEDULES : scheduled
    EMPLOYEES ||--o{ PAYROLLS : paid
    EMPLOYEES }o--|| EMPLOYEE_TYPES : typed_by
    USERS ||--o{ USER_ROLES : granted
    ROLES ||--o{ USER_ROLES : assigned
    USERS ||--o{ REPORT_METADATA : generates
    CUSTOMERS ||--o{ LOYALTY_TRANSACTIONS : earns
```
![Rendered diagram](/agenda/diagrams/diagrams-rust-sqlite-er-1.svg)

## 2. Tables & relations

| Table | PK | Relations (FK → table) |
|-------|----|------------------------|
| `settings` | `id` | single row (app config) |
| `categories` | `id` | 1—N `products.category_id` |
| `products` | `id` | `category_id → categories` · 1—N `sale_items` · 1—N `recipes` |
| `delivery_types` | `id` | N—1 `sales.delivery_type_id` |
| `employee_types` | `id` | N—1 `employees.employee_type_id` |
| `employees` | `id` | `employee_type_id → employee_types` · 1—N `sales` · 1—N `employee_schedules` · 1—N `payrolls` |
| `sales` | `id` | `employee_id → employees` · `delivery_type_id → delivery_types` · 1—N `sale_items` · 1—N `kitchen_tickets` · 1—N `loyalty_transactions` |
| `sale_items` | `id` | `product_id → products` (via sale FK) |
| `ingredients` | `id` | 1—N `recipe_ingredients` · 1—N `inventory_transactions` · 1—N `inventory_adjustments` · 1—N `inventory_alerts` · 1—N `purchase_order_items` |
| `recipe_types` | `id` | N—1 `recipes.recipe_type_id` |
| `recipes` | `id` | `product_id → products` · `recipe_type_id → recipe_types` · 1—N `recipe_ingredients` |
| `recipe_ingredients` | `id` | `recipe_id → recipes` · `ingredient_id → ingredients` |
| `inventory_transactions` | `id` | `ingredient_id → ingredients` |
| `inventory_adjustments` | `id` | `ingredient_id → ingredients` |
| `inventory_alerts` | `id` | `ingredient_id → ingredients` |
| `users` | `id` | 1—N `user_roles` · 1—N `report_metadata.generated_by` |
| `roles` | `id` | 1—N `user_roles.role_id` |
| `user_roles` | `id` | `user_id → users` · `role_id → roles` |
| `report_metadata` | `id` | `generated_by → users` |
| `suppliers` | `id` | 1—N `purchase_orders.supplier_id` |
| `purchase_orders` | `id` | `supplier_id → suppliers` · 1—N `purchase_order_items` |
| `purchase_order_items` | `id` | `purchase_order_id → purchase_orders` · `ingredient_id → ingredients` |
| `kitchen_tickets` | `id` | `sale_id → sales` |
| `customers` | `id` | 1—N `loyalty_transactions.customer_id` |
| `loyalty_transactions` | `id` | `customer_id → customers` · `sale_id → sales` |
| `employee_schedules` | `id` | `employee_id → employees` |
| `payrolls` | `id` | `employee_id → employees` |

Additional tables without relations: `coupons`, `user_actions`,
`receipt_templates`, `support_messages`, `tax_reports`, `delivery_zones`,
`finance_transactions`, `budgets`, `badges`.

## 3. Module map (`src-tauri/src/`)

| Module | Owns | Key symbols |
|--------|------|-------------|
| `main.rs` / `lib.rs` | Tauri bootstrap, command registration | `invoke_handler` |
| `db/mod.rs` | Connection open, migrations | `open_conn`, `run_migrations` |
| `db/schema.rs` | Diesel table declarations (generated + hand-edited) | all `table!` blocks |
| `db/models.rs` | Structs + `New*`/`Update*` insert/update models | `User`, `Product`, `Sale`, `SaleItem`, `Recipe`, `Ingredient`, `Employee`, … |
| `operations/` | Domain operations per entity | `sales.rs` (`add_sale`, `refund_sale`), inventory, recipes, employees, payroll |
| `email.rs` | SMTP receipt/notification dispatch | `send_*` |
| `macros.rs` | Shared macros | — |

> Standard edition shares this Diesel core (Community capabilities + multi-currency,
> tax profiles, custom roles, export, offline sync queue); the ERD above is the
> canonical base schema for both.

<!-- AI-generated: review needed -->