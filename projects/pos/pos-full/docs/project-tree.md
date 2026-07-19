# POS — Project Tree

> **Full edition:** `projects/pos/pos-full/`  
> **Stack:** Tauri 2 + React 19 + Rust (Diesel ORM) + SQLite + Python/Sanic + Django

---

```
pos-full/
├── .env.example                 # Environment variable template
├── .gitignore                   # Git ignore rules
├── LICENSE                      # AGPL-3.0 license
├── Makefile                     # Build, dev, test, seed commands
├── README.md                    # Edition README
├── index.html                   # Vite HTML entry
├── package.json                 # Frontend dependencies & scripts
├── pnpm-lock.yaml               # Locked dependency tree
├── pnpm-workspace.yaml          # pnpm workspace config
├── postcss.config.js            # PostCSS config (Tailwind)
├── tailwind.config.js           # Tailwind CSS v4 config
├── tsconfig.json                # TypeScript config
├── tsconfig.node.json           # TypeScript config for Node scripts
├── vite.config.ts               # Vite build config
├── vitest.config.ts             # Vitest test runner config
│
├── src/                         # ── React 19 + TypeScript Frontend ──
│   ├── main.tsx                 # App entry point — providers (Theme, Language, Auth)
│   ├── App.tsx                  # Router + route definitions + page transitions
│   ├── index.css                # Base CSS + Tailwind imports
│   ├── types.ts                 # Shared TypeScript types
│   │
│   ├── api/                     # Sidecar API client layer
│   │   ├── index.ts             # Barrel exports
│   │   ├── sidecar.ts           # Base HTTP client (get/post/patch + health check)
│   │   ├── chat.ts              # Chat REST + persistent WebSocket
│   │   ├── tickets.ts           # Support ticket CRUD
│   │   └── data.ts              # Sales, products, settings, invoice URL
│   │
│   ├── components/              # 16 reusable UI components
│   │   ├── PageLayout.tsx       # App shell — sidebar, topbar, content area
│   │   ├── SideNav.tsx          # Sidebar navigation with collapse
│   │   ├── DataTable.tsx        # Generic sortable/filterable table
│   │   ├── ProductCard.tsx      # Product display card
│   │   ├── Modal.tsx            # Reusable modal dialog
│   │   ├── ConfirmDialog.tsx    # Confirmation dialog
│   │   ├── ChatSupport.tsx      # Floating chat widget
│   │   ├── DatePicker.tsx       # Date picker component
│   │   ├── StatusToast.tsx      # Toast notification with severity
│   │   ├── Skeleton.tsx         # Loading skeleton placeholders
│   │   ├── BackButton.tsx       # Navigation back button
│   │   ├── Invoice.tsx          # Invoice viewer component
│   │   ├── Receipt.tsx          # Receipt renderer
│   │   ├── ThemeToggle.tsx      # Dark/light mode toggle
│   │   ├── LanguageToggle.tsx   # Language switcher (en/fr/ar)
│   │   └── KeyboardShortcutsModal.tsx  # Keyboard shortcuts reference
│   │
│   ├── contexts/                # React context providers
│   │   ├── AuthContext.tsx       # Authentication state & methods
│   │   ├── ThemeContext.tsx      # Dark/light theme state
│   │   └── LanguageContext.tsx   # i18n language state
│   │
│   ├── hooks/                   # Custom React hooks
│   │   ├── useDebouncedSearch.ts # Debounced text search
│   │   └── useStatusToast.ts    # Toast notification hook
│   │
│   ├── pages/                   # 22 route-level page components
│   │   ├── Home.tsx             # Dashboard — KPIs, charts, quick actions
│   │   ├── Sale.tsx             # Point of Sale — cart, checkout, payments
│   │   ├── ProductManager.tsx   # Product & category CRUD
│   │   ├── Inventory.tsx        # Stock tracking, low-stock alerts
│   │   ├── Analytics.tsx        # Revenue charts, trends, forecasts
│   │   ├── Transactions.tsx     # Sale history, refunds, void
│   │   ├── Employees.tsx        # Staff list, roles, status
│   │   ├── Recipes.tsx          # Recipes with ingredients & yield
│   │   ├── Reports.tsx          # PDF/Excel exportable reports
│   │   ├── Settings.tsx         # Restaurant, tax, display settings
│   │   ├── About.tsx            # App info, version, credits
│   │   ├── Auth.tsx             # Login / superuser setup / 2FA
│   │   ├── Customers.tsx        # Customer DB & loyalty points
│   │   ├── Suppliers.tsx        # Supplier management
│   │   ├── KitchenDisplay.tsx   # Kitchen ticket board
│   │   ├── EmployeeSchedule.tsx # Shift scheduling
│   │   ├── Payroll.tsx          # Payroll processing
│   │   ├── ReceiptTemplates.tsx # Custom receipt template editor
│   │   ├── TaxReports.tsx       # Tax period reporting
│   │   ├── Roles.tsx            # User roles & permissions
│   │   ├── SupportChat.tsx      # Full support chat page
│   │   └── InvoicePage.tsx      # Invoice viewer & print
│   │
│   ├── styles/                  # SCSS stylesheets
│   │   ├── base/
│   │   │   ├── _variables.css   # CSS custom properties
│   │   │   └── _reset.css       # CSS reset / normalize
│   │   ├── utilities/
│   │   │   ├── _animations.css  # Framer Motion / CSS animations
│   │   │   ├── _rtl.css         # Right-to-left (Arabic) overrides
│   │   │   └── _scrollbar.css   # Custom scrollbar styles
│   │   └── components/
│   │       ├── _card.css        # Card component styles
│   │       └── _receipt.css     # Receipt print styles
│   │
│   ├── i18n/                    # Internationalization (i18next)
│   │   ├── index.ts             # i18next init — en, fr, ar
│   │   ├── en.json              # English translations
│   │   ├── fr.json              # French translations
│   │   └── ar.json              # Arabic translations (RTL)
│   │
│   ├── utils/                   # Client-side utilities
│   │   ├── invoicePdf.ts        # Invoice PDF generation
│   │   └── export.ts            # Excel/CSV data export
│   │
│   └── test/                    # Vitest tests (frontend)
│       ├── setup.ts             # Test setup & mocks
│       ├── test-utils.tsx        # Test rendering helpers
│       ├── mocks/tauri.ts       # Tauri invoke mock
│       ├── invoke.test.ts       # Tauri bridge tests
│       ├── components/
│       │   └── ProductCard.test.tsx
│       ├── hooks/
│       │   ├── useStatusToast.test.tsx
│       │   └── useDebouncedSearch.test.ts
│       └── pages/               # Page-level tests (14 files)
│           ├── Auth.test.tsx
│           ├── Customers.test.tsx
│           ├── Employees.test.tsx
│           ├── Inventory.test.tsx
│           ├── KitchenDisplay.test.tsx
│           ├── ProductManager.test.tsx
│           ├── ReceiptTemplates.test.tsx
│           ├── Recipes.test.tsx
│           ├── Reports.test.tsx
│           ├── Roles.test.tsx
│           ├── Sale.test.tsx
│           ├── Suppliers.test.tsx
│           ├── TaxReports.test.tsx
│           └── Transactions.test.tsx
│
├── src-tauri/                   # ── Tauri 2 + Rust Backend ──
│   ├── tauri.conf.json          # Tauri app config (ID, name, window, plugins)
│   ├── Cargo.toml               # Rust dependencies (Diesel, Tauri, chrono, etc.)
│   ├── Cargo.lock               # Locked dependency tree
│   ├── build.rs                 # Tauri build script
│   │
│   ├── icons/                   # App icons (all platforms)
│   │   └── icon.icns            # macOS icon
│   │
│   ├── capabilities/
│   │   └── default.json         # Tauri capability permissions
│   │
│   ├── templates/               # Rust-side HTML templates
│   │   ├── invoice.html         # Invoice HTML template
│   │   └── support_email.html   # Support email template
│   │
│   ├── migrations/              # Diesel SQLite migrations
│   │   ├── 2026-01-01-000000_create_initial/
│   │   │   ├── up.sql           # Initial schema (29+ tables)
│   │   │   ├── down.sql         # Reverse migration
│   │   │   └── seed.sql         # Seed data
│   │   ├── 2026-01-02-000000_create_users/
│   │   │   ├── up.sql           # Users & roles tables
│   │   │   └── down.sql
│   │   ├── 2026-07-15-000000_add_product_image/
│   │   │   ├── up.sql           # Product image column
│   │   │   └── down.sql
│   │   ├── 2026-07-16-000000_add_enterprise_features/
│   │   │   ├── up.sql           # CRM, sync, payroll, schedules, tax
│   │   │   └── down.sql
│   │   └── 2026-07-17-000000_gaming_center_seed/
│   │       ├── up.sql           # POS-KO Gaming Center seed data
│   │       └── down.sql
│   │
│   └── src/
│       ├── main.rs              # Tauri app entry point — builder, plugins, invoke handler
│       ├── lib.rs               # All 80+ Tauri command registrations
│       ├── email.rs             # SMTP email sender
│       │
│       ├── db/                  # Database layer (Diesel ORM)
│       │   ├── mod.rs           # Connection pool, migrations runner
│       │   ├── schema.rs        # Table definitions (29 tables + 8 CRM tables)
│       │   └── models.rs        # Rust structs — models, inserts, updates
│       │
│       ├── operations/          # 27 CRUD operation modules
│       │   ├── mod.rs           # Module declarations
│       │   ├── auth.rs          # Superuser auth, login, 2FA, password change
│       │   ├── products.rs      # Product CRUD + uploaded tracking
│       │   ├── categories.rs    # Category CRUD
│       │   ├── sales.rs         # Sale + sale_items CRUD
│       │   ├── transactions.rs  # Transaction history
│       │   ├── analytics.rs     # Dashboard analytics & KPIs
│       │   ├── settings.rs      # Restaurant settings CRUD
│       │   ├── ingredients.rs   # Ingredient CRUD + soft delete
│       │   ├── recipes.rs       # Recipe + recipe_ingredients CRUD
│       │   ├── inventory_transactions.rs  # Stock adjustments & alerts
│       │   ├── dump.rs          # Database dump to JSON
│       │   ├── delivery_types.rs  # Delivery type CRUD
│       │   ├── employee_types.rs  # Employee type CRUD
│       │   ├── employees.rs     # Employee CRUD
│       │   ├── roles.rs         # Role + user_role assignment
│       │   ├── suppliers.rs     # Supplier CRUD
│       │   ├── purchase_orders.rs  # Purchase order + items CRUD
│       │   ├── kitchen_tickets.rs  # Kitchen ticket flow
│       │   ├── customers.rs     # Customer + loyalty transactions
│       │   ├── receipt_templates.rs  # Receipt template CRUD
│       │   ├── tax_reports.rs   # Tax report CRUD
│       │   ├── employee_schedules.rs  # Schedule CRUD
│       │   ├── payrolls.rs      # Payroll CRUD
│       │   ├── reports.rs       # Report metadata CRUD
│       │   ├── sidecar.rs       # Sidecar lifecycle (start/stop/status)
│       │   ├── signals.rs       # Change event broadcast (tokio)
│       │   └── crm.rs           # CRM entity CRUD (companies, contacts, deals, etc.)
│       │
│       └── bin/
│           └── seed.rs          # Seed binary — reset DB + apply presets
│
├── sidecar/                     # ── Python/Sanic Sidecar + Django Portal ──
│   ├── server.py                # Sanic REST API entry (chat, sales, products, invoices, tickets)
│   ├── sync_client.py           # Cloud CRM sync client (Solo → Cloud)
│   ├── sync_routes.py           # Sync API Blueprint (status, config, trigger)
│   ├── build.py                 # PyInstaller build script
│   ├── build.sh                 # Shell build wrapper
│   ├── requirements.txt         # Python dependencies (sanic, httpx, django)
│   ├── ARCHITECTURE.md          # Sidecar architecture overview
│   │
│   ├── settings.py              # Django settings (portal + node API)
│   ├── manage.py                # Django management entry
│   ├── urls.py                  # Django URL configuration
│   │
│   ├── shared/                  # Django app: shared models & viewsets
│   │   ├── models.py            # MenuItem, Category models
│   │   ├── admin.py             # Django admin registration
│   │   ├── portal_urls.py       # Portal URL patterns
│   │   ├── portal_viewsets.py   # django-fusion viewsets
│   │   ├── node_base.py         # Base node utilities
│   │   ├── management/commands/
│   │   │   └── seed_menu.py     # Menu seeding command
│   │   ├── static/
│   │   │   ├── css/portal.css   # Portal styles
│   │   │   └── js/portal.js     # Portal scripts
│   │   └── templates/portal/    # Portal templates
│   │       ├── base.html        # Portal base template
│   │       ├── dashboard.html   # Portal dashboard
│   │       ├── 404.html         # Portal 404 page
│   │       ├── menu_list.html   # Menu list view
│   │       ├── menu_item_detail.html  # Menu item detail
│   │       └── components/
│   │           └── sidebar.html # Portal sidebar component
│   │
│   ├── portal/                  # Django app: portal views
│   │   ├── __init__.py
│   │   └── admin.py
│   │
│   ├── posapp/                  # Django app: POS mirror models (Full only)
│   │   ├── __init__.py
│   │   ├── apps.py              # Django AppConfig
│   │   ├── models.py            # Django ORM models (mirror Rust schema)
│   │   └── fixtures/
│   │       └── seed_data.json   # Django-side seed data
│   │
│   └── cloud/                   # Cloud CRM server (Full only)
│       ├── server.py            # Sanic cloud CRM server (port 8766)
│       ├── api.py               # Cloud CRM REST API
│       ├── api_urls.py          # API URL routes
│       ├── models.py            # CRM models
│       ├── sync_proxy.py        # Sync proxy — accepts entity pushes from Solo
│       ├── sync_urls.py         # Sync URL routes
│       ├── webhook_receiver.py  # Webhook endpoint
│       ├── webhook_urls.py      # Webhook URL routes
│       └── migrations/
│
├── cloud/                       # ── Cloud CRM (standalone) ──
│   ├── server.py                # Cloud CRM server entry
│   ├── crm_models.py            # CRM data models
│   ├── crm_api.py               # CRM REST endpoints
│   ├── sync_proxy.py            # Sync proxy for Solo → Cloud
│   ├── sync_client.py           # Python sync client
│   ├── sync_models.py           # Sync data models
│   ├── webhook_receiver.py      # Webhook handler
│   └── requirements.txt         # Python dependencies
│
├── scripts/                     # ── Build & Automation Scripts ──
│   ├── dev/                     # Development scripts (12 files)
│   │   ├── check-i18n.cjs       # i18n translation audit
│   │   ├── i18n-merge-ar.cjs    # Merge Arabic translations
│   │   ├── fill-fr-translations.cjs  # Auto-fill French translations
│   │   ├── generate-checksums.cjs    # Generate file checksums
│   │   ├── verify-checksum.cjs       # Verify checksums
│   │   ├── kill-port.cjs         # Kill process on port 1420
│   │   ├── update-year.cjs       # Update copyright year
│   │   ├── ensure-db.cjs         # Ensure database exists
│   │   ├── build-sidecar.cjs     # Build sidecar binary
│   │   ├── build-all.cjs         # Build all platforms
│   │   ├── capture-screenshots.sh    # Screenshot capture
│   │   └── generate-android-keystore.sh  # Android keystore gen
│   │
│   └── github/                  # CI/CD scripts (2 files)
│       ├── diff-i18n.cjs        # i18n diff for PR checks
│       └── encode-keystore-for-github.sh  # Encode keystore for CI
│
├── .github/workflows/           # ── CI/CD Pipelines ──
│   ├── i18n.yml                 # i18n audit on PR
│   ├── release.yml              # Release pipeline
│   └── visual-regression.yml    # Visual regression tests
│
└── docs/                        # ── Documentation (this directory) ──
    ├── START_HERE.md            # Getting started guide
    ├── commands.md              # CLI commands reference
    ├── project-tree.md          # This file — full project tree
    ├── rust-code.md             # Rust backend architecture
    ├── customization-react.md   # React frontend customization
    ├── customization-tauri.md   # Tauri/Rust customization
    ├── i18n-conventions.md      # Translation conventions
    ├── i18n-gaps.md             # Translation gap report (auto-generated)
    ├── server/                  # Sidecar documentation
    │   └── README.md            # Sidecar API reference
    └── back-env/                # Backend environment docs
        └── README.md            # Django backend env setup
```
