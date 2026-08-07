# POS Seed Data

Consolidated seed data for all POS versions. Each version has a single migration that creates all tables and seeds data on first install.

## Migration Structure

```
pos-mini/src-tauri/migrations/2026-01-01-000000_create_all/
├── up.sql    # ALL 29 tables + restaurant + gaming center seed
└── down.sql  # Clean rollback (drops all tables)

pos-solo/src-tauri/migrations/2026-01-01-000000_create_all/
├── up.sql    # ALL 29 tables (no product_type column)
└── down.sql

pos-full/src-tauri/migrations/2026-01-01-000000_create_all/
├── up.sql    # Same as solo
└── down.sql
```

## Version Differences

| Feature | Mini | Solo | Full |
|---------|------|------|------|
| Tables | 29 | 29 | 29 |
| `products.product_type` | ✅ | ❌ | ❌ |
| `products.image` | ✅ | ✅ | ✅ |
| `sales.customer_id` | ✅ | ✅ | ✅ |
| Restaurant seed (PKR) | ✅ | ✅ | ✅ |
| Gaming center seed (USD) | ✅ | ✅ | ✅ |
| Enterprise seed (suppliers, PO, etc.) | ✅ | ✅ | ✅ |

## Seed Data Contents

### Restaurant Example (POS KO - Lahore, Pakistan)
- **Currency**: PKR
- **Categories**: 10 food categories (Burgers, Pizza, BBQ, Biryani, etc.)
- **Products**: 47 menu items
- **Ingredients**: 55 ingredients with stock levels
- **Recipes**: 41 recipes with ingredient mappings
- **Employees**: 12 staff members
- **Sales**: 12 sample transactions
- **Inventory**: 31 transactions

### Gaming Center Example (Level Up - USD)
- **Currency**: USD
- **Categories**: 6 gaming categories (PS5, PS4, VR, etc.)
- **Products**: 26 gaming products (sessions, rentals, snacks)
- **Employees**: 7 gaming center staff
- **Sales**: 20 transactions across 6 days
- **Delivery Types**: Walk-in, Pre-booked

### Enterprise Features (shared across both)
- **Suppliers**: 6 vendors with contact info
- **Customers**: 10 loyalty customers
- **Purchase Orders**: 6 orders with line items
- **Tax Reports**: 3 bi-weekly tax summaries
- **Employee Schedules**: 12 shift assignments
- **Payroll**: 8 payroll records
- **Roles**: 4 default roles (Admin, Manager, Cashier, Kitchen)

## JSON Seed Files

- `mini.json` - Structured seed data overview for POS Mini
- `solo.json` - Structured seed data overview for POS Solo
- `full.json` - Structured seed data overview for POS Full

## Seed Strategy

All data uses `INSERT OR IGNORE` so restaurant and gaming center data coexist with different ID ranges:
- Restaurant: IDs 1-47 (products), 1-55 (ingredients), etc.
- Gaming Center: IDs 51-76 (products), 11-16 (categories), etc.
