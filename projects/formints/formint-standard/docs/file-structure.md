# File Structure — Formint

## Project Root

```
formintA/  (site slug formint-pos)
├── package.json              # Frontend dependencies & scripts
├── Makefile                  # Build, dev, test, seed commands
├── vite.config.ts            # Vite bundler configuration
├── tsconfig.json             # TypeScript configuration
├── tsconfig.node.json        # TypeScript config for Node.js files
├── tailwind.config.js        # Tailwind CSS v3 config (legacy, v4 uses @import)
├── postcss.config.js         # PostCSS with Tailwind v4 plugin
├── vitest.config.ts          # Vitest test runner configuration
├── pnpm-lock.yaml            # Lockfile for pnpm
├── pnpm-workspace.yaml       # pnpm workspace definition
├── index.html                # HTML entry point for Vite
├── restaurant.db             # SQLite database (created at runtime)
├── .env                      # Environment variables (optional)
├── .gitignore                # Git ignore rules
├── LICENSE                   # AGPL-3.0 license
├── README.md                 # Project overview
├── AGENTS.md                 # AI agent instructions
├── PROMPTS.md                # Prompt reference
└── CHANGELOG.md              # Version history
```

---

## Frontend (`src/`)

```
src/
├── main.tsx                  # React entry point, context providers, FlyonUI JS import
├── App.tsx                   # Router setup, animated routes, global keyboard shortcuts
├── index.css                 # Tailwind v4 + FlyonUI + theme imports
├── types.ts                  # All TypeScript interfaces (Product, Sale, Settings, etc.)
├── vite-env.d.ts             # Vite type declarations
│
├── components/               # 16 reusable UI components
│   ├── BackButton.tsx        # Navigate-back button with optional confirm
│   ├── ChatSupport.tsx       # Floating chat widget (structa.cloud integration)
│   ├── ConfirmDialog.tsx     # Reusable delete/deactivate confirmation modal
│   ├── DataTable.tsx         # Sortable, paginated data table
│   ├── DatePicker.tsx        # Date range picker with searchable months
│   ├── Invoice.tsx           # Invoice PDF preview component (3 designs)
│   ├── KeyboardShortcutsModal.tsx  # Help overlay for keyboard shortcuts
│   ├── LanguageToggle.tsx    # Language switcher (5 languages)
│   ├── Modal.tsx             # Generic modal dialog
│   ├── PageLayout.tsx        # Page shell with SideNav + content area
│   ├── ProductCard.tsx       # Product card with colors, image, animations
│   ├── Receipt.tsx           # Printable receipt component
│   ├── SideNav.tsx           # Navigation sidebar with collapsible categories
│   ├── Skeleton.tsx          # Loading skeleton placeholder
│   ├── StatusToast.tsx       # Toast notification component
│   └── ThemeToggle.tsx       # Theme variant + light/dark toggle
│
├── pages/                    # 22 route-level page components
│   ├── Home.tsx              # Dashboard with navigation categories
│   ├── Auth.tsx              # Login/register with illustration panel
│   ├── Sale.tsx              # Point of sale (product grid, cart, checkout)
│   ├── ProductManager.tsx    # CRUD for products
│   ├── Customers.tsx         # Customer management
│   ├── Suppliers.tsx         # Supplier management
│   ├── Employees.tsx         # Employee + employee types management
│   ├── Inventory.tsx         # Ingredient stock management + transactions
│   ├── Recipes.tsx           # Recipe creation with ingredient linking
│   ├── Transactions.tsx      # Transaction history with filtering
│   ├── Analytics.tsx         # Charts: revenue, orders, product distribution
│   ├── Reports.tsx           # Multi-tab reports (overview, sales, inventory, etc.)
│   ├── Settings.tsx          # App settings (general, business, dining, appearance)
│   ├── About.tsx             # App info, support form, version
│   ├── KitchenDisplay.tsx    # Kitchen ticket board
│   ├── EmployeeSchedule.tsx  # Shift scheduling
│   ├── Payroll.tsx           # Payroll management
│   ├── ReceiptTemplates.tsx  # Receipt template editor
│   ├── TaxReports.tsx        # Tax reporting
│   ├── Roles.tsx             # Role-based permissions
│   ├── SupportChat.tsx       # Customer support chat
│   └── InvoicePage.tsx       # Invoice generator
│
├── contexts/                 # React context providers
│   ├── AuthContext.tsx       # Authentication state, login/logout
│   ├── ThemeContext.tsx      # Theme variant + light/dark mode
│   └── LanguageContext.tsx   # i18n language selection
│
├── hooks/                    # Custom React hooks
│   ├── useDebouncedSearch.ts # Debounced search with AJAX spinner
│   └── useStatusToast.ts    # Toast notification state management
│
├── api/                      # Tauri invoke wrappers
│   ├── index.ts             # Unified API exports
│   ├── data.ts              # Data operations
│   ├── chat.ts              # Chat/support operations
│   ├── sidecar.ts           # Sidecar communication
│   └── tickets.ts           # Kitchen ticket operations
│
├── utils/                    # Utility modules
│   ├── export.ts            # CSV/Excel export
│   └── invoicePdf.ts        # Invoice PDF generation (jspdf)
│
├── i18n/                     # Internationalization
│   ├── index.ts             # i18next configuration
│   ├── en.json              # English (reference — 926 keys)
│   ├── ar.json              # Arabic (RTL)
│   ├── fr.json              # French
│   ├── de.json              # German
│   ├── es.json              # Spanish
│   └── README.md            # i18n documentation
│
├── styles/                   # CSS files
│   ├── themes.css           # Theme variant CSS custom properties
│   ├── theme-overrides.css  # Tailwind color token overrides per theme
│   ├── base/
│   │   ├── _variables.css   # CSS custom properties
│   │   └── _reset.css       # Base reset + RTL font stack
│   ├── components/
│   │   ├── _card.css        # Card hover/glass effects
│   │   └── _receipt.css     # Receipt print styles
│   └── utilities/
│       ├── _rtl.css         # RTL layout utilities
│       ├── _animations.css  # Animation delay utilities
│       └── _scrollbar.css   # Thin scrollbar styling
│
├── assets/                   # Static assets
│   ├── pos-crest.svg        # POS logo (used in PageLayout)
│   ├── CompanyLogo.png      # Company logo
│   └── logo-img.png         # Logo image
│
└── test/                     # Tests
    ├── setup.ts             # Vitest setup + Tauri mock
    ├── test-utils.tsx       # Custom render utilities
    ├── invoke.test.ts       # Tauri invoke integration tests
    ├── mocks/
    │   └── tauri.ts         # Tauri API mock (mockInvokeSuccess, etc.)
    ├── hooks/
    │   ├── useStatusToast.test.tsx
    │   └── useDebouncedSearch.test.ts
    ├── components/
    │   └── ProductCard.test.tsx
    ├── pages/
    │   ├── Auth.test.tsx
    │   ├── Sale.test.tsx
    │   ├── Inventory.test.tsx
    │   ├── ProductManager.test.tsx
    │   ├── Customers.test.tsx
    │   ├── Suppliers.test.tsx
    │   ├── Employees.test.tsx
    │   ├── Recipes.test.tsx
    │   ├── Reports.test.tsx
    │   ├── Settings.test.tsx
    │   ├── Transactions.test.tsx
    │   ├── TaxReports.test.tsx
    │   ├── Roles.test.tsx
    │   ├── ReceiptTemplates.test.tsx
    │   ├── KitchenDisplay.test.tsx
    │   ├── EmployeeSchedule.test.tsx
    │   ├── Payroll.test.tsx
    │   ├── SupportChat.test.tsx
    │   ├── About.test.tsx
    │   └── Home.test.tsx
    └── scripts/
        └── kill-port.test.ts
```

---

## Backend (`src-tauri/`)

```
src-tauri/
├── Cargo.toml               # Rust dependencies & metadata
├── Cargo.lock               # Rust dependency lockfile
├── build.rs                 # Tauri build script
├── tauri.conf.json          # Tauri app configuration (window, bundle, plugins)
├── .gitignore               # Rust-specific gitignore
│
├── migrations/              # Diesel SQLite migrations
│   └── 2026-01-01-000000_create_all/
│       ├── up.sql           # Full schema + comprehensive seed data
│       └── down.sql         # DROP TABLE statements
│
├── src/
│   ├── main.rs              # Tauri entry point (main function)
│   ├── lib.rs               # 72+ Tauri command registrations + app builder
│   ├── email.rs             # SMTP email sending
│   │
│   ├── db/                  # Database setup
│   │   ├── mod.rs           # Connection pool + initialization
│   │   ├── schema.rs        # Diesel auto-generated schema
│   │   └── models.rs        # Rust structs mapped to DB tables
│   │
│   ├── operations/          # 27 CRUD operation modules
│   │   ├── mod.rs           # Module re-exports
│   │   ├── auth.rs          # Authentication (register, login, verify)
│   │   ├── products.rs      # Product CRUD + categories
│   │   ├── categories.rs    # Category management
│   │   ├── sales.rs         # Sales + sale_items
│   │   ├── transactions.rs  # Transaction queries
│   │   ├── customers.rs     # Customer management
│   │   ├── employees.rs     # Employee CRUD
│   │   ├── employee_types.rs# Employee type CRUD
│   │   ├── employee_schedules.rs  # Shift scheduling
│   │   ├── payrolls.rs      # Payroll management
│   │   ├── ingredients.rs   # Ingredient CRUD
│   │   ├── inventory_transactions.rs # Stock movements
│   │   ├── recipes.rs       # Recipe CRUD + ingredients
│   │   ├── suppliers.rs     # Supplier management
│   │   ├── purchase_orders.rs # Purchase order management
│   │   ├── delivery_types.rs# Delivery type CRUD
│   │   ├── settings.rs      # Settings operations
│   │   ├── analytics.rs     # Aggregated analytics queries
│   │   ├── reports.rs       # Report generation
│   │   ├── tax_reports.rs   # Tax report CRUD
│   │   ├── receipt_templates.rs # Receipt template CRUD
│   │   ├── roles.rs         # Role-based permissions CRUD
│   │   ├── shifts.rs        # Shift management
│   │   ├── hardware.rs      # ESC/POS printer support
│   │   ├── kitchen_tickets.rs # Kitchen display tickets
│   │   ├── sidecar.rs       # Sidecar process management
│   │   └── dump.rs          # Database import/export
│   │
│   └── bin/
│       └── seed.rs          # Seed binary (4 presets: all, base, gaming, coffee)
│
├── capabilities/
│   └── default.json         # Tauri capability permissions
│
├── templates/               # HTML templates
│   ├── invoice.html         # Invoice email template
│   └── support_email.html   # Support email template
│
├── binaries/                # Sidecar binaries (platform-specific)
│   └── pos-sidecar-*        # Compiled sidecar for current platform
│
└── icons/                   # App icons
    ├── icon.icns            # macOS icon
    ├── icon.png             # Generic icon (512x512)
    ├── 32x32.png            # Small icon
    ├── 128x128.png          # Medium icon
    ├── 128x128@2x.png       # Retina icon
    ├── 256x256.png          # Large icon
    ├── 512x512.png          # Extra large icon
    └── icon.ico             # Windows icon
```

---

## Docs (`docs/`)

```
docs/
├── README.md                # Documentation landing page (NEW)
├── architecture.md          # System architecture & design (NEW)
├── database.md              # ERD, schema, migrations (NEW)
├── invoke-methods.md        # Tauri command catalog (NEW)
├── file-structure.md        # This file (NEW)
├── guides.md                # Setup & deployment guides (NEW)
├── commands.md              # Makefile & CLI reference (existing)
├── calculations.md          # All formulas (existing)
├── customization.md         # Theme, colors, i18n (existing)
├── roles-permissions.md     # RBAC documentation (existing)
├── rust-code.md             # Rust backend docs (existing)
├── project-tree.md          # Legacy tree (existing)
├── sql/
│   └── index.md             # SQL reference
├── typescript/
│   └── index.md             # TypeScript reference
└── rust/
    └── index.md             # Rust reference
```

---

## Scripts (`scripts/`)

```
scripts/
├── dev/
│   ├── check-i18n.cjs       # i18n key validation script
│   ├── i18n-merge-ar.cjs    # Arabic i18n merge
│   ├── kill-port.cjs        # Port killer for dev server
│   ├── update-year.cjs      # Copyright year updater
│   ├── ensure-db.cjs        # DB existence checker
│   └── capture-screenshots.sh # Screenshot capture pipeline
├── github/
│   └── diff-i18n.cjs        # i18n diff for CI
├── publish/
│   ├── build-all.cjs        # Multi-platform build orchestrator
│   ├── build-sidecar.cjs    # Sidecar builder
│   ├── generate-checksums.cjs # Checksum generation
│   └── verify-checksum.cjs  # Checksum verification
└── README.md                # Scripts documentation
```

---

## CI/CD (`.github/`)

```
.github/workflows/
├── release.yml              # Full release pipeline (build + sign + publish)
├── i18n.yml                 # PR i18n diff check
├── i18n-strict.yml          # Strict locale key validation
└── visual-regression.yml   # Screenshot diff testing
```
