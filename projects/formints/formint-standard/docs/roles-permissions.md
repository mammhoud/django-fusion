# Formint — Roles & Permissions

> **Related:** [Shared Role System](../../docs/ROLE_SYSTEM.md) — unified permission design across all editions

---

## Overview

forge-pos implements a role-based access control system through the `roles` table (Rust/Diesel) with JSON-based permission flags. The system defines 5 default roles with granular permissions.

---

## Database Model

### `roles` Table

| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer (PK) | Auto-increment ID |
| `name` | Text | Role name (unique) |
| `permissions` | Text (JSON) | JSON object of permission flags |
| `is_active` | Boolean | Soft delete flag |
| `created_at` | DateTime | Creation timestamp |
| `updated_at` | DateTime | Last update timestamp |

### `user_roles` Join Table

| Column | Type | Description |
|--------|------|-------------|
| `user_id` | Integer (FK → users) | User reference |
| `role_id` | Integer (FK → roles) | Role reference |
| `created_at` | DateTime | Assignment timestamp |

### Permission Flags (JSON Schema)

The `permissions` column stores a JSON object with boolean flags:

```json
{
  "can_view_products": true,
  "can_manage_products": false,
  "can_manage_categories": false,
  "can_process_sales": true,
  "can_process_returns": false,
  "can_void_sales": false,
  "can_apply_discounts": false,
  "can_view_inventory": true,
  "can_manage_inventory": false,
  "can_manage_suppliers": false,
  "can_manage_purchase_orders": false,
  "can_view_customers": true,
  "can_manage_customers": false,
  "can_view_employees": false,
  "can_manage_employees": false,
  "can_manage_schedules": false,
  "can_manage_payroll": false,
  "can_view_reports": false,
  "can_view_analytics": false,
  "can_export_data": false,
  "can_access_settings": false,
  "can_manage_roles": false,
  "can_view_kitchen": false,
  "can_manage_kitchen": false,
  "can_sync_data": false
}
```

---

## Default Roles

### 1. Super Admin (Level 100)

| Permission | Value |
|-----------|:-----:|
| All permissions | ✅ `true` |

**Description:** Full system access. Can manage roles, access settings, view/edit everything.

### 2. Manager (Level 80)

| Permission | Value |
|-----------|:-----:|
| Products | ✅ view + manage |
| Categories | ✅ manage |
| Sales | ✅ process + returns + void |
| Discounts | ✅ apply |
| Inventory | ✅ view + manage |
| Suppliers | ✅ manage |
| Purchase Orders | ✅ manage |
| Customers | ✅ view + manage |
| Employees | ✅ view + manage |
| Schedules | ✅ manage |
| Reports | ✅ view + export |
| Analytics | ✅ view |
| Settings | ✅ access |
| **Roles** | ❌ **cannot manage** |
| **Payroll** | ❌ **cannot manage** |

**Description:** Day-to-day operations management. Cannot modify roles or payroll.

### 3. Cashier (Level 60)

| Permission | Value |
|-----------|:-----:|
| View Products | ✅ |
| Process Sales | ✅ |
| Process Returns | ✅ |
| View Customers | ✅ |
| View Inventory | ✅ |
| **All others** | ❌ `false` |

**Description:** Front-of-house sales processing. Can sell, view products/inventory, and process returns.

### 4. Kitchen (Level 40)

| Permission | Value |
|-----------|:-----:|
| View Kitchen | ✅ |
| Manage Kitchen | ✅ |
| View Products | ✅ |
| **All others** | ❌ `false` |

**Description:** Back-of-house kitchen operations. Can view and manage kitchen tickets and see products.

### 5. Viewer (Level 20)

| Permission | Value |
|-----------|:-----:|
| View Products | ✅ |
| View Reports | ✅ |
| View Analytics | ✅ |
| **All others** | ❌ `false` |

**Description:** Read-only access. Can view but cannot create, edit, or delete anything.

---

## Frontend Permission Checks

### Permission Hook

```typescript
// hooks/usePermissions.ts
export function usePermissions() {
  const { user } = useAuth();

  const can = (permission: string): boolean => {
    return user?.permissions?.[permission] ?? false;
  };

  return { can };
}
```

### Conditional Rendering

```typescript
function DeleteProductButton({ productId }: { productId: number }) {
  const { can } = usePermissions();

  if (!can('can_manage_products')) return null;

  return <button onClick={() => deleteProduct(productId)}>Delete</button>;
}
```

### UI Element Hiding Rules

| UI Element | Required Permission | Hidden For |
|-----------|-------------------|------------|
| Product Add/Edit buttons | `can_manage_products` | Cashier, Kitchen |
| Delete Customer | `can_manage_customers` | Cashier, Kitchen |
| Settings menu item | `can_access_settings` | All except Manager+ |
| Reports tab | `can_view_reports` | Cashier, Kitchen |
| Inventory Adjust | `can_manage_inventory` | Cashier, Kitchen |
| Employee Management | `can_manage_employees` | All except Manager+ |
| Role Manager | `can_manage_roles` | All except Super Admin |
| Payroll | `can_manage_payroll` | All except Super Admin |

---

## Backend Enforcement (Rust)

```rust
// Example: Permission check in operation module
pub fn delete_product(db_path: &PathBuf, product_id: i32, user_id: i32) -> Result<(), String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::{roles, user_roles};

    // Check user has manage_products permission
    let has_perm = user_roles::table
        .inner_join(roles::table)
        .filter(user_roles::user_id.eq(user_id))
        .filter(roles::permissions.like("%\"can_manage_products\": true%"))
        .count()
        .get_result::<i64>(&mut conn)
        .map_err(|e| e.to_string())? > 0;

    if !has_perm {
        return Err("Forbidden: requires can_manage_products permission".to_string());
    }

    // Proceed with delete...
    Ok(())
}
```

---

## Role Management

Roles are managed through the `/roles` route (Roles.tsx page):

| Feature | Description |
|---------|-------------|
| List roles | Table with active/inactive status |
| Create role | Name + permission toggle grid |
| Edit role | Update name + toggle permissions |
| Delete role | Soft delete (deactivate) |
| Clone role | Duplicate existing role |
| Assign to user | User form includes role selector |
| System protection | Default roles cannot be deleted |

---

## Seed Data

```sql
-- System roles created on first migration
INSERT INTO roles (name, permissions, is_active, priority)
VALUES
  ('Super Admin', '{"can_view_products":true,...ALL_PERMISSIONS...}', true, 100),
  ('Manager',     '{"can_view_products":true,...EXCEPT_ROLES_PAYROLL...}', true, 80),
  ('Cashier',     '{"can_process_sales":true,"can_view_products":true,...}', true, 60),
  ('Kitchen',     '{"can_view_kitchen":true,"can_manage_kitchen":true,...}', true, 40),
  ('Viewer',      '{"can_view_products":true,"can_view_reports":true,...}', true, 20);
```

---

## Migration Path from Other Editions

> The former pos-solo/pos-full editions were merged into `formint-pos` (archived
> React UIs under `formint-pos/legacy-react/`).

### Legacy React editions → forge-pos

| Difference | pos-full / pos-solo | forge-pos |
|-----------|----------|-----------|
| Role model | CharField (string) / `Role` model in `extra.py` | `roles` table (JSON permissions) |
| Permission check | None (string-based) | Granular permission flags |
| UI management | No role management UI | Full role list + editor |

---

## Related Documentation

- **[Shared Role System](../../docs/ROLE_SYSTEM.md)** — Unified permission design across all editions
- **[Customization Guide](customization.md)** — Adding new permissions
- **[Rust Code](rust-code.md)** — `roles.rs` operation module
