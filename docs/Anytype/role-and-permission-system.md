---
# yaml-language-server: $schema=schemas/page.schema.json
Object type:
    - Page
Creation date: "2026-07-24T19:54:39Z"
Created by:
    - mammhoud
id: bafyreiaihnfyqohezzcdorslpnickx2zo4le5er4pxz2h2t423yx3xzili
---
# Role & Permission System   
**Type:** Architecture 🏗️
T**ags: **#`auth `#`pos-solo `#`pos-full `#`pos-cloud
`S**tatus: **Published
E**dition: **Mini, Solo, Full, Cloud (varying implementation)   
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
|            Role   <br> | Level   <br> |                                                                             Flags (true)   <br> |
|:-----------------------|:-------------|:------------------------------------------------------------------------------------------------|
| **Super Admin**   <br> |   100   <br> |                                                                                All flags   <br> |
|     **Manager**   <br> |    80   <br> | products, inventory, employees, reports, sales, returns, customers, suppliers, analytics   <br> |
|     **Cashier**   <br> |    50   <br> |                                              process\_sales, process\_returns, customers   <br> |
|     **Kitchen**   <br> |    30   <br> |                                                 manage\_kitchen, view\_reports (limited)   <br> |
|      **Viewer**   <br> |    10   <br> |                                                     view\_reports, customers (read-only)   <br> |

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
```
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
```
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
[Role &amp; Permission System](role-and-permission-system.md)    
