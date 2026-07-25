---
# yaml-language-server: $schema=schemas/page.schema.json
Object type:
    - Page
Creation date: "2026-07-24T19:54:39Z"
Created by:
    - mammhoud
id: bafyreidw7uvlv4z5ir3ea63kjcwvz4vavvaohvprnbjkf4zp5rroe5ekie
---
# pos-mini — Edition Features   
**Type:** Feature ✨
**Tags:** `#pos-mini` `#frontend` `#backend` `#tauri` `#database`
**Status:** Complete
**Edition:** Mini   
 --- 
## Stack   
```
React 19 ←→ Tauri Rust ←→ SQLite
              │
         Tauri Commands

```
 --- 
## Key Features   
### Sales   
```
addToCart(product) → cart state
updateQuantity(id, qty, unit) → updated item
handleSell() → invoke('add_sale') → receipt

```
### Product Manager   
```
get_products() → Product[]
add_product(name, price, unit, category) → id
update_product(id, fields) → success
delete_product(id) → success

```
### Analytics   
```
get_analytics() → { revenue, orders, avg_order, top_products }
get_daily_revenue() → { date, amount, orders_count }

```
### Inventory   
```
get_ingredients() → Ingredient[]
record_transaction(ingredient_id, qty, type, note) → id
get_low_stock() → Ingredient[] (filtered: stock ≤ reorder_level)

```
 --- 
## Rust Backend (Tauri Commands)   
```
┌─────────────────────────────────────────┐
│            Tauri Commands               │
├─────────────────────────────────────────┤
│ get_products        add_sale            │
│ get_settings        save_settings       │
│ get_employees       get_analytics       │
│ get_categories      get_inventory       │
│ get_delivery_types  save_settings       │
│ export_database     import_database     │
└─────────────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  SQLite (rusqlite)│
└─────────────────┘

```
 --- 
## Data Models (Rust)   
```
struct Product { id, name, price, unit, category_id, is_active, created_at }
struct Sale { id, total_amount, currency, order_type, status, table_number, created_at }
struct CartItem { id, name, price, quantity, unit }
struct Employee { id, name, phone, email, employee_type_id, salary, is_active }
struct Ingredient { id, name, unit, stock, reorder_level, cost_per_unit, is_active }
struct Role { id, name, permissions: String (JSON), is_active }

```
 --- 
## Related Docs   
- → `architecture/editions-overview.md` — Compare with other editions   
- → `features/comparison-matrix.md` — Full feature grid   
- → `references/tauri-commands.md` — All Tauri commands   
- → `references/database-schema.md` — SQLite schema   
- → `guides/setup.md` — Setup guide for pos-mini   
[pos-mini — Edition Features](pos-mini-edition-features.md)    
