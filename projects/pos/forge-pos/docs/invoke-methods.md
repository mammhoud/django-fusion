# Invoke Methods — Forge POS

## Overview

All data operations in Forge POS use **Tauri `invoke()`** from `@tauri-apps/api/core`. The frontend calls Rust command handlers directly via the Tauri IPC bridge. Each command is registered in `src-tauri/src/lib.rs` with `#[tauri::command]`.

## How It Works

```
// Frontend (TypeScript)
import { invoke } from '@tauri-apps/api/core';
const products = await invoke<Product[]>('get_products');

// Rust Backend
#[tauri::command]
fn get_products(db: tauri::State<DbPool>) -> Result<Vec<Product>, String> {
    products::get_all(&db)
}
```

---

## Products

### `get_products`
**Returns:** `Product[]` — all active products

**Frontend:**
```typescript
const products = await invoke<Product[]>('get_products');
```

**Rust Handler:** Returns all products ordered by name.

### `add_product`
**Parameters:** `{ product: NewProduct }`

**Frontend:**
```typescript
await invoke('add_product', { 
  product: { name: 'Zinger Burger', price: 450, unit: 'item', category_id: 1 }
});
```

**Rust Handler:** Inserts new product, returns product ID.

### `update_product`
**Parameters:** `{ id: number, update: Partial<Product> }`

**Frontend:**
```typescript
await invoke('update_product', { 
  id: 1, 
  update: { price: 500, border_color: '#ff0000' }
});
```

**Rust Handler:** Updates product fields by ID.

### `delete_product`
**Parameters:** `{ id: number }`

**Frontend:**
```typescript
await invoke('delete_product', { id: 1 });
```

**Rust Handler:** Deletes product by ID.

---

## Categories

### `get_categories`
**Returns:** `{ id: number, name: string }[]`

**Frontend:**
```typescript
const categories = await invoke<Category[]>('get_categories');
```

---

## Sales

### `add_sale`
**Parameters:** `{ sale: NewSaleData, items: NewSaleItemData[] }`

**Frontend:**
```typescript
await invoke('add_sale', {
  sale: {
    total_amount: 1360,
    currency: 'PKR',
    date: '2026-01-10',
    time: '13:15:00',
    order_type: 'dine_in',
    status: 'completed',
    table_number: 3,
    employee_id: 4
  },
  items: [
    { product_name: 'Chicken Burger', price: 350, quantity: 2, unit: 'item' },
    { product_name: 'French Fries', price: 200, quantity: 1, unit: 'plate' }
  ]
});
```

**Rust Handler:** Wraps in SQL transaction — inserts sale header + sale items.

### `get_sales`
**Returns:** `Sale[]`

**Frontend:**
```typescript
const sales = await invoke<Sale[]>('get_sales');
```

### `delete_transaction`
**Parameters:** `{ id: number }`

**Frontend:**
```typescript
await invoke('delete_transaction', { id: 5 });
```

---

## Settings

### `get_settings`
**Returns:** `Settings`

**Frontend:**
```typescript
const settings = await invoke<Settings>('get_settings');
```

**Rust Handler:** Returns the singleton settings row (id=1).

### `save_settings`
**Parameters:** `{ settings: Settings }`

**Frontend:**
```typescript
await invoke('save_settings', {
  settings: {
    restaurant_name: 'POS KO',
    address: '123 Main Street',
    phone: '+92-300-1234567',
    currency: 'USD',
    tax_rate: '13',
    dine_in_tables: 15,
    delivery_fee: 50
  }
});
```

**Rust Handler:** Updates the singleton settings row.

### `import_database_cmd`
**Parameters:** `{ data: string }` (base64-encoded SQLite file)

**Frontend:**
```typescript
await invoke('import_database_cmd', { data: base64String });
```

### `change_password_cmd`
**Parameters:** `{ current_password: string, new_password: string }`

**Frontend:**
```typescript
await invoke('change_password_cmd', {
  current_password: 'oldpass',
  new_password: 'newpass123'
});
```

---

## Customers

### `get_customers`
**Returns:** `Customer[]`

**Frontend:**
```typescript
const customers = await invoke<Customer[]>('get_customers');
```

### `add_customer`
**Parameters:** `{ customer: NewCustomer }`

**Frontend:**
```typescript
await invoke('add_customer', {
  customer: { name: 'John Doe', phone: '+92-300-7654321' }
});
```

### `update_customer`
**Parameters:** `{ id: number, update: Partial<Customer> }`

**Frontend:**
```typescript
await invoke('update_customer', { id: 1, update: { email: 'john@example.com' } });
```

### `delete_customer`
**Parameters:** `{ id: number }`

**Frontend:**
```typescript
await invoke('delete_customer', { id: 1 });
```

---

## Employees

### `get_employees`
**Parameters:** `{ includeInactive?: boolean }`
**Returns:** `Employee[]`

**Frontend:**
```typescript
const employees = await invoke<Employee[]>('get_employees', { includeInactive: false });
```

### `add_employee`
**Parameters:** `{ employee: NewEmployee }`

**Frontend:**
```typescript
await invoke('add_employee', {
  employee: { name: 'Ali Ahmed', employee_type_id: 1, salary: 60000 }
});
```

### `update_employee`
**Parameters:** `{ id: number, update: Partial<Employee> }`

**Frontend:**
```typescript
await invoke('update_employee', { id: 1, update: { salary: 65000 } });
```

### `soft_delete_employee`
**Parameters:** `{ id: number }`

**Frontend:**
```typescript
await invoke('soft_delete_employee', { id: 1 });
```

### Employee Types

#### `get_employee_types`
**Returns:** `EmployeeType[]`

#### `add_employee_type`
**Parameters:** `{ employeeType: NewEmployeeType }`

#### `update_employee_type`
**Parameters:** `{ id: number, update: Partial<EmployeeType> }`

#### `soft_delete_employee_type`
**Parameters:** `{ id: number }`

---

## Inventory (Ingredients)

### `get_ingredients`
**Returns:** `Ingredient[]`

### `add_ingredient`
**Parameters:** `{ ingredient: NewIngredient }`

### `update_ingredient`
**Parameters:** `{ id: number, update: Partial<Ingredient> }`

### `soft_delete_ingredient`
**Parameters:** `{ id: number }`

### `add_inventory_transaction`
**Parameters:** `{ transaction: NewInventoryTransaction, adjustmentReason?: string, createdBy?: string }`

**Frontend:**
```typescript
await invoke('add_inventory_transaction', {
  transaction: { 
    ingredient_id: 1, 
    transaction_type: 'purchase', 
    quantity_change: 30 
  }
});
```

### `get_inventory_transactions`
**Returns:** `InventoryTransaction[]`

### `get_inventory_adjustments`
**Returns:** `InventoryAdjustment[]`

---

## Recipes

### `get_recipes`
**Returns:** `Recipe[]`

### `create_recipe`
**Parameters:** `{ recipe: NewRecipe, ingredients: NewRecipeIngredient[] }`

### `update_recipe`
**Parameters:** `{ id: number, recipe: Partial<Recipe> }`

### `soft_delete_recipe`
**Parameters:** `{ id: number }`

### `add_recipe_ingredient`
**Parameters:** `{ recipeId: number, ingredientId: number, quantity: number, unit?: string, preparationNote?: string }`

### `delete_recipe_ingredient`
**Parameters:** `{ id: number }`

### `get_recipe_ingredients`
**Parameters:** `{ recipeId: number }`
**Returns:** `RecipeIngredient[]`

---

## Analytics

### `get_analytics`
**Returns:** `AnalyticsData`

```typescript
const analytics = await invoke<AnalyticsData>('get_analytics');
```

**Response shape:**
```typescript
{
  summary: { total_orders: 12, total_revenue: 18360, average_order_value: 1530 },
  daily_revenue: [{ date: '2026-01-10', revenue: 4610, orders: 3 }],
  top_products: [{ name: 'Chicken Karahi', sales: 3, revenue: 3400 }],
  product_distribution: [{ name: 'Burgers', value: 8 }]
}
```

---

## Authentication

### `check_auth_required`
**Returns:** `boolean` — whether auth is configured for this instance

### `has_users`
**Returns:** `boolean` — whether any users exist

### `send_auth_confirmation_code`
**Parameters:** `{ email: string }`
**Returns:** `void`

### `setup_account`
**Parameters:** `{ name: string, email: string, password: string, code: string }`

### `verify_user`
**Parameters:** `{ email: string }`

### `login_user`
**Parameters:** `{ email: string, password: string }`

### `get_user_count`
**Returns:** `number` — total registered users

---

## Kitchen Display

### `get_kitchen_tickets`
**Returns:** `KitchenTicket[]`

### `update_kitchen_ticket`
**Parameters:** `{ id: number, update: { status: string } }`

---

## Delivery Types

### `get_delivery_types`
**Parameters:** `{ includeInactive?: boolean }`
**Returns:** `DeliveryType[]`

---

## Suppliers

### `get_suppliers`
**Returns:** `Supplier[]`

### `add_supplier`
**Parameters:** `{ supplier: NewSupplier }`

### `update_supplier`
**Parameters:** `{ id: number, update: Partial<Supplier> }`

### `soft_delete_supplier`
**Parameters:** `{ id: number }`

---

## Employee Schedule

### `get_employee_schedules`
**Returns:** `EmployeeSchedule[]`

### `add_employee_schedule`
**Parameters:** `{ schedule: { employee_id: number, shift_start: string, shift_end: string } }`

### `delete_employee_schedule`
**Parameters:** `{ id: number }`

---

## Payroll

### `get_payrolls`
**Returns:** `Payroll[]`

### `add_payroll`
**Parameters:** `{ payroll: NewPayroll }`

### `delete_payroll`
**Parameters:** `{ id: number }`

---

## Receipt Templates

### `get_receipt_templates`
**Returns:** `ReceiptTemplate[]`

### `add_receipt_template`
**Parameters:** `{ template: NewReceiptTemplate }`

### `update_receipt_template`
**Parameters:** `{ id: number, update: Partial<ReceiptTemplate> }`

### `delete_receipt_template`
**Parameters:** `{ id: number }`

---

## Tax Reports

### `get_tax_reports`
**Returns:** `TaxReport[]`

### `add_tax_report`
**Parameters:** `{ report: NewTaxReport }`

### `delete_tax_report`
**Parameters:** `{ id: number }`

---

## Roles

### `get_roles`
**Returns:** `Role[]`

### `add_role`
**Parameters:** `{ role: NewRole }`

### `update_role`
**Parameters:** `{ id: number, update: Partial<Role> }`

### `soft_delete_role`
**Parameters:** `{ id: number }`

---

## Support

### `send_support_email`
**Parameters:** `{ name: string, email: string, subject: string, message: string }`
**Returns:** `void`

---

## Summary Table

| Group | Commands | Count |
|-------|----------|-------|
| **Products** | `get_products`, `add_product`, `update_product`, `delete_product`, `get_categories` | 5 |
| **Sales** | `get_sales`, `add_sale`, `delete_transaction` | 3 |
| **Settings** | `get_settings`, `save_settings`, `import_database_cmd`, `change_password_cmd` | 4 |
| **Customers** | `get_customers`, `add_customer`, `update_customer`, `delete_customer` | 4 |
| **Employees** | `get_employees`, `add_employee`, `update_employee`, `soft_delete_employee`, `get_employee_types`, `add_employee_type`, `update_employee_type`, `soft_delete_employee_type` | 8 |
| **Inventory** | `get_ingredients`, `add_ingredient`, `update_ingredient`, `soft_delete_ingredient`, `add_inventory_transaction`, `get_inventory_transactions`, `get_inventory_adjustments` | 7 |
| **Recipes** | `get_recipes`, `create_recipe`, `update_recipe`, `soft_delete_recipe`, `add_recipe_ingredient`, `delete_recipe_ingredient`, `get_recipe_ingredients`, `get_recipe_types` | 8 |
| **Analytics** | `get_analytics` | 1 |
| **Auth** | `check_auth_required`, `has_users`, `send_auth_confirmation_code`, `setup_account`, `verify_user`, `login_user`, `get_user_count` | 7 |
| **Kitchen** | `get_kitchen_tickets`, `update_kitchen_ticket` | 2 |
| **Delivery** | `get_delivery_types` | 1 |
| **Suppliers** | `get_suppliers`, `add_supplier`, `update_supplier`, `soft_delete_supplier` | 4 |
| **Schedule** | `get_employee_schedules`, `add_employee_schedule`, `delete_employee_schedule` | 3 |
| **Payroll** | `get_payrolls`, `add_payroll`, `delete_payroll` | 3 |
| **Templates** | `get_receipt_templates`, `add_receipt_template`, `update_receipt_template`, `delete_receipt_template` | 4 |
| **Tax Reports** | `get_tax_reports`, `add_tax_report`, `delete_tax_report` | 3 |
| **Roles** | `get_roles`, `add_role`, `update_role`, `soft_delete_role` | 4 |
| **Support** | `send_support_email` | 1 |
| **Total** | | **72+** |
