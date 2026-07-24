# POS Role System

> **Version:** 1.0.0  
> **Last Updated:** 24 July 2026  
> **Applies to:** pos-mini (Rust), pos-solo (Django), pos-full (Django)  
> **Related:** [Sync Architecture](SYNC_ARCHITECTURE.md), [Architecture Overview](POS_ARCHITECTURE.md)

---

## 1. Current State

| Version | Role Model | Permissions | UI | Gaps |
|---------|-----------|-------------|----|------|
| **pos-mini** | `roles` table (Rust Diesel) | JSON text field `permissions` | Role CRUD via Tauri commands | No UI role assignment on user creation. Roles exist but are invisible to cashiers |
| **pos-solo** | Employee has `role` CharField (choices: admin/manager/cashier/kitchen) | None (string-based) | No role management UI | No granular permissions. Role is a string, not linked to permissions model |
| **pos-full** | Has both: Employee `role` field + `Role` model in `extra.py` | `Role` model has JSONField permissions | No role management UI | Two parallel role systems — `Role` model exists but is **not wired** to Employee |
| **pos-cloud** | Django admin auth (groups/permissions) | Django permission system | Admin panel | Separate auth system, no POS role mapping |

---

## 2. Proposed Unified Role Model

### Permission Flags

```python
PERMISSION_FLAGS = {
    # ── Products & Categories ──
    'can_view_products': True,        # Default: all roles
    'can_manage_products': False,     # Create/edit/delete products
    'can_manage_categories': False,
    
    # ── Sales & Transactions ──
    'can_process_sales': True,        # Default: all roles
    'can_process_returns': False,     # Process refunds/returns
    'can_void_sales': False,          # Void/cancel sales
    'can_apply_discounts': False,     # Apply manual discounts
    'can_set_cashback': False,        # Set cashback amounts
    
    # ── Inventory ──
    'can_view_inventory': True,
    'can_manage_inventory': False,    # Stock adjustments, transfers
    'can_manage_suppliers': False,
    'can_manage_purchase_orders': False,
    
    # ── Customers ──
    'can_view_customers': True,
    'can_manage_customers': False,
    
    # ── Employees ──
    'can_view_employees': False,
    'can_manage_employees': False,    # Hire/fire/update
    'can_manage_schedules': False,    # Employee scheduling
    'can_manage_payroll': False,
    
    # ── Reports & Analytics ──
    'can_view_reports': False,
    'can_view_analytics': False,
    'can_export_data': False,
    
    # ── Settings ──
    'can_access_settings': False,
    'can_manage_roles': False,        # Superadmin only
    
    # ── Kitchen ──
    'can_view_kitchen': False,
    'can_manage_kitchen': False,
    
    # ── Sync & Network ──
    'can_sync_data': False,
    'can_manage_nodes': False,
    'can_manage_cloud_link': False,
}
```

### Default Roles

| Role | Key Permissions | Description |
|------|----------------|-------------|
| **Super Admin** | All permissions | Full system access |
| **Manager** | Everything except `manage_roles`, `manage_payroll` (optional) | Day-to-day operations |
| **Cashier** | Sales, returns, customers, view products/inventory | Front-of-house |
| **Kitchen** | View kitchen, manage kitchen tickets | Back-of-house |
| **Viewer** | View products, view reports (read-only) | Read-only access |

### Database Model

```python
class Role(models.Model):
    """Access control role with granular JSONField permissions."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, default="")
    permissions = models.JSONField(default=dict)  # PERMISSION_FLAGS shape
    is_system_role = models.BooleanField(default=False)  # Cannot delete system roles
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0)  # Higher = more precedence
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "full_roles"  # pos-solo: "solo_roles"
        ordering = ["-priority", "name"]
```

### Employee Integration

```python
class Employee(models.Model):
    # ... existing fields ...
    # Replace CharField role with FK:
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    
    @property
    def permissions(self) -> dict:
        """Resolve effective permissions for this employee."""
        if self.role:
            return {**PERMISSION_FLAGS, **self.role.permissions}
        return dict(PERMISSION_FLAGS)
    
    def has_permission(self, flag: str) -> bool:
        return self.permissions.get(flag, False)
```

---

## 3. Permission Check Middleware

### Backend: Django/Robyn

> ⚠️ **Not yet implemented** — the following is the planned design.

```python
# (planned) middleware/permissions.py
from functools import wraps

def require_permission(permission_flag: str):
    """Decorator to check a specific permission on a Robyn route handler."""
    def decorator(handler):
        @wraps(handler)
        async def wrapper(request, *args, **kwargs):
            token_info = get_token_info()
            if not token_info:
                return jsonify({"error": "Unauthorized"}), 401
            
            role = token_info.get("role", "")
            permissions = get_role_permissions(role)
            
            if not permissions.get(permission_flag, False):
                return jsonify({
                    "error": "Forbidden",
                    "required": permission_flag,
                    "your_role": role,
                }), 403
            
            return await handler(request, *args, **kwargs)
        return wrapper
    return decorator
```

### Frontend: React Components

> ⚠️ **Not yet implemented** — the following is the planned design.

```typescript
// (planned) hooks/usePermissions.ts
export function usePermissions() {
  const { user } = useAuth();
  
  const can = useCallback((permission: string): boolean => {
    return user?.permissions?.[permission] ?? false;
  }, [user]);
  
  return { can };
}

// Usage in components:
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
| Sync Now button | `can_sync_data` | All except Manager+ |
| Role Manager | `can_manage_roles` | All except Super Admin |
| Payroll | `can_manage_payroll` | All except Super Admin |

---

## 4. Implementation Plan

### Phase 1: Backend Model Unification

1. **pos-solo**: Add `Role` model (matching pos-full's `extra.py`)
2. **pos-solo + pos-full**: Wire `Role` FK to `Employee` — replace CharField
3. **Both**: Seed default roles on first server start
4. **Both**: Add `has_permission()` helper to Employee model

### Phase 2: Permission Middleware

1. **Both**: Create `middleware/permissions.py` with `require_permission` decorator
2. **Both**: Add permission check to sensitive endpoints:
   - `POST/PATCH/DELETE /products/*` → requires `can_manage_products`
   - `POST/PATCH/DELETE /employees/*` → requires `can_manage_employees`
   - `POST /sales/:id/return` → requires `can_process_returns`
   - `GET/PATCH /settings/*` → requires `can_access_settings`
3. **Both**: Return 403 with permission info on denied access

### Phase 3: Frontend Role Manager UI

1. **All versions**: Add `/roles` route and RoleManager page
2. **Features**:
   - Role list with permission toggle grid
   - Inline creation/editing
   - Clone role from existing
   - Delete confirmation (system roles protected)
3. **Employee form**: Add role selector dropdown with permission summary tooltip

### Phase 4: UI Permission Hiding

1. **All versions**: Create `usePermissions()` hook
2. **All versions**: Add conditional rendering based on permissions
3. **All versions**: Add permission badge to user profile dropdown

### Phase 5: pos-mini Rust Integration

1. Add permissions JSON parsing in Rust `Role` model
2. Add frontend permission checking using same flag names
3. Add Role Manager page to pos-mini

---

## 5. Seed Data

```python
SYSTEM_ROLES = [
    {
        "name": "Super Admin",
        "description": "Full system access — all permissions enabled",
        "permissions": {k: True for k in PERMISSION_FLAGS},
        "is_system_role": True,
        "priority": 100,
    },
    {
        "name": "Manager",
        "description": "Day-to-day operations management",
        "permissions": {
            **{k: True for k in PERMISSION_FLAGS},
            "can_manage_roles": False,     # Only super admin
            "can_manage_payroll": False,   # Sensitive
        },
        "is_system_role": True,
        "priority": 80,
    },
    {
        "name": "Cashier",
        "description": "Front-of-house sales processing",
        "permissions": {
            "can_view_products": True,
            "can_process_sales": True,
            "can_process_returns": True,
            "can_view_customers": True,
            "can_view_inventory": True,
            # All others: False
        },
        "is_system_role": True,
        "priority": 60,
    },
    {
        "name": "Kitchen",
        "description": "Back-of-house kitchen operations",
        "permissions": {
            "can_view_kitchen": True,
            "can_manage_kitchen": True,
            "can_view_products": True,
            # All others: False
        },
        "is_system_role": True,
        "priority": 40,
    },
    {
        "name": "Viewer",
        "description": "Read-only access to reports and products",
        "permissions": {
            "can_view_products": True,
            "can_view_reports": True,
            "can_view_analytics": True,
            # All others: False
        },
        "is_system_role": True,
        "priority": 20,
    },
]
```
