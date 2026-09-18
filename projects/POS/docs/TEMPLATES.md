# Formints — Template Architecture

> **Last updated:** 2026-08-10
> **Template engine:** Django (DjangoTemplates) + django-unfold admin
> **Frontend:** Astro 5 + Tauri (see edition plans at `docs/plans/editions/`)

---

## 1. Overview

Formints uses a **dual-interface** architecture:

1. **Desktop app** — Rust/Tauri native window with an Astro frontend. Templates are
   Astro `.astro` components, served locally by the Tauri webview. No Django involved.
2. **Admin server** — Optional Django backend (`formint-pro/server/`) that provides
   a django-unfold admin interface for cloud sync, user management, and product inventory.

The admin is the **only** Django template surface in Formints. The desktop app's UI is
entirely Astro + React 19 + Alpine.js.

```
Desktop App                     Admin Server (optional)
┌──────────────────┐           ┌──────────────────────────┐
│ Tauri Webview    │           │ Django + django-unfold    │
│ ├── Astro pages  │   sync    │ ├── admin/base.html      │
│ ├── React 19     │ ←─────→  │ ├── admin/dashboard.html │
│ └── Alpine.js    │  DataToken│ ├── admin/products.html  │
└──────────────────┘           │ ├── admin/users.html     │
                               │ └── admin/settings.html  │
                               └──────────────────────────┘
```

---

## 2. Template Directory Map

```
projects/formints/
├── formint-pro/server/templates/admin/
│   ├── base.html                          ← Root admin layout (django-unfold)
│   ├── dashboard.html                     ← Admin dashboard with stats
│   ├── login.html                         ← Admin login (superuser or PIN)
│   ├── products.html                      ← Product inventory management
│   ├── users.html                         ← User accounts & roles
│   └── settings.html                      ← Cloud sync, server config
│
├── formint-community/src/                 ← Community edition (no Django)
│   ├── App.astro                          ← Root Astro app
│   └── pages/                             ← Astro pages (28 in Standard)
│
└── formint-pro/server/models/            ← Django models with DataToken sync
    ├── extra.py                           ← Cash register, drawer, receipt
    └── loyalty.py                         ← Loyalty program models
```

---

## 3. Admin Template Hierarchy

### 3.1 Flow

```
Browser → /admin/ → django-unfold AdminSite
    │
    ▼
admin/base.html                          ← Root admin layout
    │
    ├── Sidebar navigation                ← Products, Users, Settings, Sync
    ├── Header (brand + user menu)        ← django-unfold header
    │
    └── Content block
        ├── admin/dashboard.html          ← Stats cards, recent activity
        ├── admin/products.html           ← Product list, create, edit
        ├── admin/users.html              ← User management, role assignment
        ├── admin/settings.html           ← Cloud sync toggle, server info
        └── admin/login.html              ← Superuser login + PIN login
```

### 3.2 Base Layout (`admin/base.html`)

The base template uses django-unfold's admin skin which provides:
- Dark/light theme support
- Responsive sidebar
- Breadcrumb navigation
- Action bar for bulk operations

```django
{% extends 'unfold/layouts/skeleton.html' %}
{% load i18n unfold %}

{% block content %}
    {% include "unfold/helpers/app_list_default.html" %}
{% endblock %}
```

### 3.3 Dashboard (`admin/dashboard.html`)

Shows key metrics for the POS fleet:

```
┌─────────────────────────────────────────────────────────────┐
│  📊 Dashboard                                               │
├───────────┬───────────┬───────────┬─────────────────────────┤
│ Sales     │ Products  │ Users     │ Sync Status             │
│ Today     │ Active    │ Active    │ Last sync: 2 min ago    │
│ $12,450   │ 847       │ 12        │ Cloud: ✓ Connected      │
├───────────┴───────────┴───────────┴─────────────────────────┤
│  Recent Activity                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 10:32  Sale #4821 — $245.00 — John D.                │  │
│  │ 10:28  Product updated — "Espresso" — Sarah K.       │  │
│  │ 10:15  New user — "cashier-04" — Admin               │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Template Flow by Edition

### 4.1 Community Edition (No Django)

```
Tauri window → src/App.astro → React 19 components
    │
    ├── /pos            → Point of sale screen
    ├── /products       → Product catalog (local SQLite)
    ├── /reports        → Sales reports
    └── /settings       → App configuration

No Django templates. All UI is Astro + React.
```

### 4.2 Standard Edition (Optional Django Server)

```
Tauri window → same Astro + React UI as Community
    │
    └── Optional: formint-pro/server/ Django admin
        │
        ├── /admin/            → django-unfold admin
        │   ├── Products CRUD
        │   ├── User management
        │   └── Settings
        │
        └── /api/v1/           → REST API (ninja-extra)
            └── Sync endpoints for DataToken sync_batch()
```

### 4.3 Pro Edition (Required Django Server)

```
Tauri window → Astro + Alpine + HTMX
    │
    └── formint-pro/server/ (always running)
        │
        ├── /admin/            → Full django-unfold admin
        ├── /api/v1/           → REST API
        ├── /fusion/           → Astro rendering proxy
        └── /mcp/tools/        → MCP task management tools
```

### 4.4 Cloud Edition

```
Browser → formint-cloud/backend/
    │
    ├── /admin/                → Multi-tenant django-unfold admin
    ├── /api/v1/               → REST API for all connected devices
    └── /fusion/               → Astro rendering for cloud dashboard
```

---

## 5. DataToken Sync & Template Integration

The admin settings page exposes sync configuration:

```django
{# admin/settings.html #}
<form method="post">
    {% csrf_token %}
    <fieldset>
        <legend>Cloud Sync</legend>
        <label>
            <input type="checkbox" name="sync_enabled"
                   {% if settings.sync_enabled %}checked{% endif %}>
            Enable cloud synchronization
        </label>
        <input type="url" name="cloud_endpoint"
               value="{{ settings.cloud_endpoint }}"
               placeholder="https://cloud.formints.com/api/v1/sync/">
    </fieldset>
    <button type="submit">Save</button>
</form>
```

Sync status is shown on the dashboard via `DataToken.objects.sync_batch()` query results.

---

## 6. Frontend/Backend Bridge

### 6.1 Tauri → Django Communication

The desktop app communicates with the optional server via HTTP:

```typescript
// src/api/server.ts — Tauri frontend
export async function pushToServer(endpoint: string, data: unknown) {
  const base = await getServerBaseUrl(); // e.g., http://localhost:5173
  const res = await fetch(`${base}/api/v1/${endpoint}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return res.json();
}
```

### 6.2 Rust → Django Sync (DataToken Shell)

The Rust backend can tag data for sync without Django:

```rust
// src-tauri/src/operations/dispatcher.rs
fn create_currency(name: &str, code: &str) -> Result<()> {
    // 1. Try server API
    if let Ok(_) = server::post("/api/v1/currencies", ...) {
        return Ok(()); // DataToken auto-tagged by Django
    }

    // 2. Write to local SQLite
    diesel::insert_into(currencies::table)
        .values((name, code))
        .execute(&mut conn)?;

    // 3. Tag for later sync (DataToken Shell)
    diesel::insert_into(sync_queue::table)
        .values((table: "currencies", status: "pending"))
        .execute(&mut conn)?;

    // 4. Emit signal for frontend
    app.emit("data-changed", payload)?;
    Ok(())
}
```

---

## 7. Related Files

| File | Role |
|---|---|
| `formint-pro/server/templates/admin/base.html` | django-unfold admin layout |
| `formint-pro/server/templates/admin/dashboard.html` | Admin dashboard |
| `formint-pro/server/templates/admin/products.html` | Product CRUD |
| `formint-pro/server/templates/admin/users.html` | User management |
| `formint-pro/server/templates/admin/settings.html` | Sync & server config |
| `formint-pro/server/models/` | Django models (extra.py, loyalty.py) |
| `formint-community/src/App.astro` | Community edition Astro root |
| `formint-community/src-tauri/src/operations/dispatcher.rs` | DataToken Shell (Rust) |
| `docs/plans/editions/` | Per-edition architecture plans |
| `docs/plans/django-fusion/django-fusion-tasks-mcp-plan.md` | Task & MCP infrastructure |
