# Role & Permission System

**Type:** Architecture 🏗️
**Tags:** `#auth` `#pos-solo` `#pos-full` `#pos-cloud`
**Status:** Published
**Edition:** Mini, Solo, Full, Cloud (varying implementation)

---

## Permission Model

```
User ──→ Role ──→ [Permission Flags]
                      │
                      ├─ can_manage_products
                      ├─ can_manage_inventory
                      ├─ can_manage_employees
                      ├─ can_view_reports
                      ├─ can_process_sales
                      ├─ can_process_returns
                      ├─ can_manage_customers
                      ├─ can_manage_suppliers
                      ├─ can_access_settings
                      ├─ can_manage_roles
                      ├─ can_sync_data
                      ├─ can_view_analytics
                      └─ can_manage_kitchen
```

---

## Default Roles

| Role | Level | Flags (true) |
|------|-------|-------------|
| **Super Admin** | 100 | All flags |
| **Manager** | 80 | products, inventory, employees, reports, sales, returns, customers, suppliers, analytics |
| **Cashier** | 50 | process_sales, process_returns, customers |
| **Kitchen** | 30 | manage_kitchen, view_reports (limited) |
| **Viewer** | 10 | view_reports, customers (read-only) |

---

## Edition Implementation

### pos-mini (Rust)
```
roles table:
  id, name, permissions (JSON text), is_active, created_at

user_roles join table:
  user_id, role_id
```

### pos-solo / pos-full (Django)
```python
# extra.py — Role model
class Role(models.Model):
    name = models.CharField(max_length=100)
    permissions = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)

# Employee model links to Role
class Employee(models.Model):
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
```

### Permission Check Flow (React)
```typescript
// hooks/usePermissions.ts
const { permissions } = usePermissions();
const canSell = permissions?.can_process_sales ?? false;

// UI hiding
{canSell && <button>Complete Sale</button>}
```

---

## Related Docs
- → `editions-overview.md` — Compare editions
- → `guides/development.md` — Adding new permissions
- → `references/database-schema.md` — Roles schema
