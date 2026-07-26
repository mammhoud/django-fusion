# Forge POS — Project Tree

> **Edition:** Forge POS (formerly pos-mini)  
> **Stack:** Tauri 2 + React 19 + Rust (Diesel ORM) + SQLite  
> **No sidecar** — pure Rust/Diesel backend, no Python dependencies

---

```
forge-pos/
├── .env.example                 # Environment variable template
├── .gitignore                   # Git ignore rules
├── LICENSE                      # AGPL-3.0 license
├── Makefile                     # Build, dev, test, seed commands
├── README.md                    # Edition overview
├── AGENTS.md                    # AI agent instructions
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
│   ├── main.tsx                 # App entry point — providers
│   ├── App.tsx                  # Router + route definitions
│   ├── index.css                # Base CSS + Tailwind imports
│   ├── types.ts                 # Shared TypeScript type definitions
│   │
│   ├── api/                     # Sidecar / Tauri invoke wrappers
│   │   ├── index.ts             # Barrel exports
│   │   ├── sidecar.ts           # HTTP client (optional sidecar)
│   │   ├── chat.ts              # Chat WebSocket
│   │   ├── tickets.ts           # Support tickets
│   │   └── data.ts              # Sales, products, settings
│   │
│   ├── components/              # 16 reusable UI components
│   │   ├── PageLayout.tsx       # App shell — sidebar + topbar + content
│   │   ├── SideNav.tsx          # Sidebar navigation
│   │   ├── DataTable.tsx        # Sortable/filterable table
│   │   ├── ProductCard.tsx      # Product display with border_color
│   │   ├── Modal.tsx            # Modal dialog
│   │   ├── ConfirmDialog.tsx    # Confirmation dialog
│   │   ├── ChatSupport.tsx      # Floating chat widget
│   │   ├── DatePicker.tsx       # Date picker
│   │   ├── StatusToast.tsx      # Toast notifications
│   │   ├── Skeleton.tsx         # Loading skeletons
│   │   ├── BackButton.tsx       # Navigation back
│   │   ├── Invoice.tsx          # Invoice viewer
│   │   ├── Receipt.tsx          # Receipt renderer
│   │   ├── ThemeToggle.tsx      # Dark/light mode toggle
│   │   ├── LanguageToggle.tsx   # Language switcher
│   │   └── KeyboardShortcutsModal.tsx  # Shortcuts reference
│   │
│   ├── contexts/                # React context providers
│   │   ├── AuthContext.tsx       # Auth state
│   │   ├── ThemeContext.tsx      # Theme (dark/light)
│   │   └── LanguageContext.tsx   # i18n language
│   │
│   ├── hooks/                   # Custom React hooks
│   │   ├── useDebouncedSearch.ts
│   │   └── useStatusToast.ts
│   │
│   ├── pages/                   # 22 route-level page components
│   │   ├── Home.tsx             # Dashboard KPIs
│   │   ├── Sale.tsx             # POS terminal
│   │   ├── ProductManager.tsx   # Product CRUD
│   │   ├── Inventory.tsx        # Stock tracking
│   │   ├── Analytics.tsx        # Charts & revenue
│   │   ├── Transactions.tsx     # Sale history
│   │   ├── Employees.tsx        # Staff
│   │   ├── Recipes.tsx          # Recipe management
│   │   ├── Reports.tsx          # PDF/Excel reports
│   │   ├── Settings.tsx         # Restaurant settings
│   │   ├── About.tsx            # App info
│   │   ├── Auth.tsx             # Login
│   │   ├── Customers.tsx        # Customer DB
│   │   ├── Suppliers.tsx        # Supply chain
│   │   ├── KitchenDisplay.tsx   # Kitchen tickets
│   │   ├── EmployeeSchedule.tsx # Shift scheduling
│   │   ├── Payroll.tsx          # Payroll
│   │   ├── ReceiptTemplates.tsx # Receipt designs
│   │   ├── TaxReports.tsx       # Tax reporting
│   │   ├── Roles.tsx            # Role management
│   │   ├── SupportChat.tsx      # Support
│   │   └── InvoicePage.tsx      # Invoice print
│   │
│   ├── styles/                  # CSS (Tailwind + custom)
│   │   ├── themes.css           # Theme definitions
│   │   ├── theme-overrides.css  # Theme CSS variable overrides
│   │   ├── base/
│   │   │   ├── _variables.css   # CSS custom properties
│   │   │   └── _reset.css       # CSS reset
│   │   ├── utilities/
│   │   │   ├── _animations.css  # Animations
│   │   │   ├── _rtl.css         # RTL (Arabic)
│   │   │   └── _scrollbar.css   # Scrollbar styles
│   │   └── components/
│   │       ├── _card.css        # Card styles
│   │       └── _receipt.css     # Receipt print styles
│   │
│   ├── i18n/                    # Internationalization
│   │   ├── index.ts             # i18next init
│   │   ├── en.json              # English
│   │   ├── fr.json              # French
│   │   └── ar.json              # Arabic (RTL)
│   │
│   ├── utils/                   # Utilities
│   │   ├── invoicePdf.ts        # Invoice PDF (jsPDF)
│   │   └── export.ts            # Excel/CSV export
│   │
│   └── test/                    # Vitest tests
│       ├── setup.ts
│       ├── test-utils.tsx
│       ├── mocks/tauri.ts
│       └── pages/               # Page tests
│
├── src-tauri/                   # ── Tauri 2 + Rust Backend ──
│   ├── tauri.conf.json          # Tauri config
│   ├── Cargo.toml               # Rust dependencies
│   ├── build.rs                 # Build script
│   ├── icons/                   # App icons
│   ├── capabilities/
│   │   └── default.json         # Tauri permissions
│   ├── templates/
│   │   ├── invoice.html         # Invoice template
│   │   └── support_email.html   # Email template
│   ├── migrations/              # Diesel SQLite migrations
│   │   ├── 2026-01-01-000000_create_initial/
│   │   ├── 2026-01-02-000000_create_users/
│   │   ├── 2026-07-15-000000_add_product_image/
│   │   ├── 2026-07-16-000000_add_enterprise_features/
│   │   └── 2026-07-17-000000_gaming_center_seed/
│   └── src/
│       ├── main.rs              # App entry
│       ├── lib.rs               # 80+ Tauri command registrations
│       ├── email.rs             # SMTP email
│       ├── db/
│       │   ├── mod.rs           # Connection + migrations
│       │   ├── schema.rs        # 29+ table definitions
│       │   └── models.rs        # Rust structs
│       ├── operations/          # 27 CRUD modules
│       │   ├── products.rs, sales.rs, categories.rs
│       │   ├── customers.rs, employees.rs, auth.rs
│       │   ├── inventory_transactions.rs, ingredients.rs
│       │   ├── recipes.rs, analytics.rs, settings.rs
│       │   ├── suppliers.rs, purchase_orders.rs
│       │   ├── kitchen_tickets.rs, delivery_types.rs
│       │   ├── employee_types.rs, roles.rs
│       │   ├── receipt_templates.rs, tax_reports.rs
│       │   ├── employee_schedules.rs, payrolls.rs
│       │   ├── reports.rs, transactions.rs, dump.rs
│       │   ├── sidecar.rs       # Sidecar lifecycle
│       │   └── hardware.rs      # Printer & cash drawer
│       └── bin/
│           └── seed.rs          # Seed binary
│
├── scripts/                     # Build & dev scripts
│   └── dev/                     # 12 utility scripts
│
└── docs/                        # Documentation
    ├── commands.md              # This file
    ├── project-tree.md          # This file
    ├── rust-code.md             # Rust backend docs
    ├── customization.md         # Customization guide
    ├── calculations.md          # All formulas & calculations
    ├── roles-permissions.md     # Role permissions
    └── {rust,sql,typescript}/   # Language-specific index
```
