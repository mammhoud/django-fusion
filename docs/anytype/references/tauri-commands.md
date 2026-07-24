# Reference — Tauri Commands

**Type:** Reference 📚
**Tags:** `#pos-mini` `#pos-solo` `#pos-full` `#tauri` `#backend`
**Status:** Published
**Category:** CLI

---

## Command Categories

```
┌──────────────────────────────────────────────────┐
│                 Tauri Commands                    │
├───────────┬──────────┬───────────┬───────────────┤
│ Products  │  Sales   │ Inventory │  System       │
├───────────┼──────────┼───────────┼───────────────┤
│ get       │ add_sale │ get       │ get_settings  │
│ add       │ invoice  │ record    │ save_settings │
│ update    │ PDF/Print│ adjust    │ export_db     │
│ delete    │          │           │ import_db     │
│ categories│          │           │ change_pwd    │
└───────────┴──────────┴───────────┴───────────────┘
```

---

## Products

| Command | Returns | Params |
|---------|---------|--------|
| `get_products` | `Product[]` | — |
| `add_product` | `id: number` | `{ name, price, unit, category_id? }` |
| `update_product` | `void` | `{ id, ...fields }` |
| `delete_product` | `void` | `{ id }` |
| `get_categories` | `Category[]` | — |

## Sales

| Command | Returns | Params |
|---------|---------|--------|
| `add_sale` | `Receipt` | `{ sale: NewSaleData, items: NewSaleItemData[] }` |
| `get_receipts` | `Receipt[]` | `{ limit?, offset? }` |
| `download_invoice_pdf` | `string` (path) | `{ invoice_type, items[], ... }` |

## Employees

| Command | Returns | Params |
|---------|---------|--------|
| `get_employees` | `Employee[]` | `{ include_inactive? }` |
| `add_employee` | `id` | `{ name, phone, email, type_id, salary }` |
| `update_employee` | `void` | `{ id, ...fields }` |
| `deactivate_employee` | `void` | `{ id }` |

## Inventory

| Command | Returns | Params |
|---------|---------|--------|
| `get_ingredients` | `Ingredient[]` | — |
| `add_ingredient` | `id` | `{ name, unit, stock, reorder_level, cost }` |
| `record_transaction` | `id` | `{ ingredient_id, quantity_change, note }` |

## System

| Command | Returns | Params |
|---------|---------|--------|
| `get_settings` | `Settings` | — |
| `save_settings` | `void` | `{ ...settings }` |
| `export_database_cmd` | `string` (base64) | — |
| `import_database_cmd` | `void` | `{ data: base64 }` |
| `change_password_cmd` | `void` | `{ email, old_password, new_password }` |

---

## Related Docs
- → `features/pos-mini.md` — pos-mini feature details
- → `guides/setup.md` — Running the app
- → `references/database-schema.md` — Underlying DB schema
