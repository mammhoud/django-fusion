# POS — Desktop Point-of-Sale Application

> **Edition System:** Minimal | Extended | Full  
> **Stack:** Tauri 2 + React 19 + Rust + SQLite (+ optional Python/Django sidecar)  
> **Shared Assets:** `projects/pos/assets/css/pos-theme.css`

---

## Edition Overview

| Edition | Sidecar | Django Models | WebSocket Chat | CRM | Use Case |
|---------|---------|---------------|----------------|-----|----------|
| **Minimal** | ❌ | ❌ | ❌ | ❌ | Core POS — fast, lightweight, offline-first |
| **Extended** | ✅ Sanic | ❌ | ❌ | ❌ | POS + REST API for external integrations |
| **Full** | ✅ Sanic | ✅ Django | ✅ | ✅ Cloud CRM | Enterprise POS with CRM, analytics, sync |

---

## Edition Plans

### Minimal — Core POS App

**Directory:** `projects/pos/pos-minimal/`

The minimal edition is the foundational point-of-sale desktop application built with **Tauri 2 + React 19 + Rust + SQLite**. It runs fully offline with no external dependencies.

**Architecture:**
```
pos-minimal/
├── src/                # React/TypeScript frontend
│   ├── api/            # Tauri invoke API layer
│   ├── components/     # 15 reusable UI components
│   ├── contexts/       # Auth, Theme, Language providers
│   ├── hooks/          # Custom React hooks
│   ├── i18n/           # en/fr/ar translations
│   ├── pages/          # 22 route-level page components
│   ├── styles/         # SCSS (utilities, base, components)
│   └── utils/          # PDF export, data utilities
├── src-tauri/          # Rust/Tauri backend
│   ├── src/
│   │   ├── db/         # Database (schema, models, migrations)
│   │   ├── operations/ # CRUD operations (25+ modules)
│   │   └── email.rs    # SMTP email sender
│   ├── migrations/     # Diesel SQLite migrations
│   └── icons/          # App icons
├── assets/             # Shared design system (symlinked from ../assets/)
└── Makefile            # Build & dev commands
```

**Commands:**
```bash
cd projects/pos/pos-minimal
pnpm install
pnpm tauri dev    # Development
pnpm build        # Production build
```

**Use Cases:**
- Restaurant POS: tables, orders, payments, tips
- Retail POS: products, inventory, sales, customers
- Kitchen Display: tickets, recipes, ingredients
- Employee Management: schedules, payroll, roles

---

### Extended — POS + Sidecar API

**Directory:** `projects/pos/pos-extended/`

The extended edition adds a **Python/Sanic sidecar server** that provides a REST + WebSocket API layer on top of the core POS SQLite database.

**Additional Architecture:**
```
pos-extended/
├── ...core POS files (same as minimal)...
├── sidecar/
│   ├── server.py       # Sanic REST + WebSocket API (35+ endpoints)
│   └── requirements.txt
└── assets/             # Shared design system (symlinked from ../assets/)
```

**API Endpoints:**
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/api/sales` | GET/POST | Sales CRUD |
| `/api/products` | GET/POST | Product CRUD |
| `/api/inventory` | GET | Inventory queries |
| `/api/customers` | GET/POST | Customer management |
| `/api/analytics` | GET | Dashboard analytics |

**Commands:**
```bash
cd projects/pos/pos-extended
pnpm install
python3 sidecar/server.py &   # Start sidecar
pnpm tauri dev                # Start Tauri app
```

**Use Cases:**
- External API integration (POS data accessible via HTTP)
- Real-time dashboard with WebSocket updates
- Third-party service connections (accounting, ERP)

---

### Full — POS + Sidecar + Django + CRM

**Directory:** `projects/pos/pos-full/`

The full edition adds **Django models** (independent of the Rust schema), a **WebSocket chat** support system, and integrates with the **Cloud CRM** at `projects/crm/`.

**Additional Architecture:**
```
pos-full/
├── ...core POS files (same as extended)...
├── sidecar/
│   ├── server.py        # Sanic REST API
│   ├── posapp/          # Django application (independent models)
│   │   ├── models.py    # POS Django models (mirrors Rust concepts)
│   │   ├── views.py     # Django REST views
│   │   ├── serializers.py
│   │   ├── admin.py
│   │   └── apps.py      # Django AppConfig
│   └── requirements.txt # + Django, djangorestframework
├── crm/                  # Cloud CRM (symlinked or imported)
└── assets/               # Shared design system
```

**Django Models (posapp.models):**
| Model | Fields | Purpose |
|-------|--------|---------|
| `Product` | name, sku, price, category, tax_rate | POS products |
| `Category` | name, icon, color | Product categories |
| `Customer` | name, email, phone, loyalty_points | Customer records |
| `Sale` | date, total, tax, payment_method, items | POS transactions |
| `SaleItem` | product, quantity, unit_price, line_total | Line items |
| `Inventory` | product, quantity, low_stock_threshold | Stock tracking |
| `Employee` | name, role, pin, schedule | Staff management |

**Integration with `projects/crm/`:**
- Shared color palette and CSS via `projects/pos/assets/css/pos-theme.css`
- CRM clients synced with POS customers
- Cross-sell analytics and reporting

**Commands:**
```bash
cd projects/pos/pos-full
pnpm install
pip install -r sidecar/requirements.txt
python3 sidecar/server.py &   # Start sidecar + Django
pnpm tauri dev                # Start Tauri app
```

**Use Cases:**
- Complete enterprise POS with CRM
- Customer relationship management
- WebSocket support chat
- Django admin dashboard for data management
- Sales analytics and reporting

---

## Shared Design System

**Location:** `projects/pos/assets/css/pos-theme.css`

All editions share a common design system through CSS custom properties:

```css
:root {
  --pos-primary: #2563eb;
  --pos-secondary: #059669;
  --pos-accent: #f59e0b;
  --pos-danger: #dc2626;
  --pos-bg: #f8fafc;
  --pos-surface: #ffffff;
  --pos-border: #e2e8f0;
  --pos-text: #1e293b;
  --pos-radius: 8px;
  --pos-font: 'Inter', sans-serif;
}
```

**Components provided:** buttons (`.pos-btn`), cards (`.pos-card`), tables (`.pos-table`), forms (`.pos-input`), badges (`.pos-badge`), layout (`.pos-layout`, `.pos-sidebar`, `.pos-main`), navigation (`.pos-nav-item`).

**Usage in any edition:**
```html
<link rel="stylesheet" href="../assets/css/pos-theme.css">
```

---

## CRM (`projects/crm/`)

The Cloud CRM project at `projects/crm/` uses the same POS design system for visual consistency:

- **Styles:** Imports `pos-theme.css` from `projects/pos/assets/css/`
- **Color Palette:** Same `--pos-*` CSS custom properties
- **Layout:** Same sidebar + main layout pattern (`.pos-layout`, `.pos-sidebar`, `.pos-main`)
- **Components:** Reuses `.pos-btn`, `.pos-card`, `.pos-table`, `.pos-input`

---

## Shared Assets Structure

```
projects/pos/assets/
├── css/
│   └── pos-theme.css        # Shared design system (all editions + CRM)
└── README.md                # This reference
```

## Related Documentation

- [Backend Environment](../../docs/back-env/)
- [Deployment Guide](../../docs/guides/04-deploy.md)
- [Customization Guide](../../docs/guides/05-customize.md)
- [Rust Backend Docs](../../docs/rust/)
- [TypeScript Frontend Docs](../../docs/typescript/)
