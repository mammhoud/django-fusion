# Formint Client — AI Agent Instructions

**Path:** `projects/formints/formint-client/`  
**Product:** Formint Client POS (historically `formintC`, `pos-client`)  
**Stack:** Tauri 2 + Vue 3 + TypeScript + Pinia; Django shop/employee backend; Astro frontend shell

Read `projects/formints/AGENTS.md` and the repository root first. This is the
desktop client edition — a Tauri shell with a Vue 3 POS UI, served by a
lightweight Django backend for shop and employee operations.

## Layout

```text
formint-client/
├── src/                      # Vue 3 POS application
│   ├── views/                # Dashboard, Settings, Menu, Orders views
│   ├── components/           # TitleBar and shared UI components
│   ├── layouts/              # MainLayout wrapper
│   ├── router/               # Vue Router configuration
│   ├── api/                  # Backend API client wrappers
│   ├── utils/                # Settings, i18n, theme utilities
│   ├── locales/              # en-US, zh-CN translations
│   ├── assets/               # CSS (variables, reset, cards, receipt, pos-theme)
│   └── App.vue / main.ts     # Vue entry point
├── frontend/                 # Astro shell
│   ├── src/pages/            # Astro routes
│   ├── src/layouts/          # Document shell
│   ├── src/components/       # Header, Footer, HtmxBootstrap, CartDrawer, modals
│   └── src/lib/              # HTMX bootstrap, site config, API helpers
├── src-tauri/                # Tauri 2 desktop shell
│   └── src/                  # lib.rs, main.rs
├── backend/                  # Django backend
│   ├── shop/                 # Products, cart, checkout, orders
│   ├── employee/             # Employee dashboard, order management
│   ├── settings.py           # Self-contained settings
│   ├── urls.py               # Shop + employee routing
│   └── manage.py             # Django CLI
├── README.md
├── Makefile
└── package.json
```

## Architecture

- **Vue 3 UI** (`src/`): Primary POS interface with Pinia state management,
  vue-router navigation, and i18n support.
- **Astro shell** (`frontend/`): Lightweight Astro wrapper providing
  HTMX/Alpine.js bootstrap and shared UI components (cart drawer, login modal,
  toasts).
- **Django backend** (`backend/`): Shop API (products, cart, checkout, orders)
  and employee dashboard. Uses django-fusion fragments for cart/order
  components.
- **Tauri shell** (`src-tauri/`): Desktop packaging; wraps the Vue 3 + Astro
  application.

## Conventions

- Vue 3 component state uses Pinia stores; keep store modules per domain
  (settings, cart, orders).
- Astro shell provides the document wrapper and HTMX bootstrap; Vue handles
  interactive POS UI.
- Django backend serves both REST endpoints and HTMX fragments (cart drawer,
  cart count, product grid, order rows).
- Keep frontend API types (`frontend/src/lib/api.ts`) synchronized with
  backend serializers and URL names.
- Translations live in `src/locales/` as TypeScript modules.
- CSS follows the POS theme variables in `src/assets/css/base/_variables.css`.

## Commands

```bash
cd projects/formints/formint-client
pnpm install
pnpm dev                # Vite dev server
pnpm build              # Production build
pnpm lint               # oxlint + vue-tsc
pnpm test               # Vitest (if configured)
vue-tsc --noEmit        # TypeScript typecheck

# Tauri desktop
pnpm tauri dev
pnpm tauri build

# Django backend
cd backend
python manage.py check
python manage.py migrate
python manage.py runserver
python manage.py test
python manage.py seed_shop
```

## Testing

- Vue components: Vitest (from `src/`).
- Django backend: `cd backend && python manage.py test`.
- Tauri/Rust: `cargo check --manifest-path src-tauri/Cargo.toml`.
- Run the narrowest suite first; ensure backend is running for integration tests.

## Do not

- Do not introduce a Python server or django-fusion render-mode server; this
  edition uses a simple Django backend.
- Do not copy `formint-pro` or `formint-cloud` sync/Channels/WebSocket code.
- Do not add Tauri plugins or permissions without updating `capabilities/`.
- Do not commit local databases, generated installers, or signing keys.

## Related

- [`../AGENTS.md`](../AGENTS.md) — Formint multi-edition overview
- [`README.md`](README.md) — Product README
- [`../../docs/pos/`](../../docs/pos/) — POS documentation
- [`../../docs/plans/editions/05-pos-client.md`](../../docs/plans/editions/05-pos-client.md)
