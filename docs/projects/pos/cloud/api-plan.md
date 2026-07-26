# 📡 Cloud Sync API Plan

> Detailed endpoint reference for the django-bolt REST API used by the Cloud Sync system.

See the high-level sync plan at [`sync-plan.md`](sync-plan.md).

---

## Auth Endpoints

```
POST   /bolt/auth/login          # JWT login
POST   /bolt/auth/refresh        # Refresh token
POST   /bolt/auth/logout         # Invalidate token
```

## Product Endpoints

```
GET    /bolt/products             # List (with filtering, pagination)
POST   /bolt/products             # Create
GET    /bolt/products/{id}       # Detail
PUT    /bolt/products/{id}        # Update
DELETE /bolt/products/{id}       # Soft delete
```

## Order Endpoints

```
GET    /bolt/orders              # List (filter by date, status)
POST   /bolt/orders              # Create (with items)
GET    /bolt/orders/{id}         # Detail with items
PUT    /bolt/orders/{id}/status  # Update status
GET    /bolt/orders/{id}/invoice # Generate PDF invoice
```

## Sync Endpoints

```
GET    /bolt/sync/status         # Sync health
POST   /bolt/sync/trigger        # Force full sync
POST   /bolt/sync/push           # Push entities (Solo → Cloud)
GET    /bolt/sync/log            # Sync history
```

## CRM Endpoints (Cloud Only)

```
GET    /bolt/crm/contacts        # List contacts
POST   /bolt/crm/contacts        # Create contact
GET    /bolt/crm/companies       # List companies
GET    /bolt/crm/deals           # List deals
POST   /bolt/crm/deals           # Create deal
GET    /bolt/crm/dashboard       # CRM statistics
```

## Report Endpoints

```
GET    /bolt/reports/sales       # Sales report (by date range)
GET    /bolt/reports/inventory   # Inventory report
GET    /bolt/reports/employees   # Employee performance
GET    /bolt/reports/taxes       # Tax summary
```
