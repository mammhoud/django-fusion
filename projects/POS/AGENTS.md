# Formints / POS — AI Agent Instructions

**Path:** `projects/formints/`  
**Product:** Formint(s) restaurant point-of-sale platform

Read the repository root and `projects/AGENTS.md` first. This directory contains
several related products; choose the edition deliberately before editing.

## Edition map

| Path | Identity | Architecture | Use for |
|---|---|---|---|
| `formint-community/` | Community (`formint-pos`) | Tauri 2 + React 19 + Rust + Diesel/SQLite; no Python server | Offline-first desktop POS |
| `formint-pro/` | Professional | Astro + HTMX/Alpine frontend, Django boundary, typed APIs, Fusion fragments, Unfold, Tauri shell | Merged professional product |
| `formint-cloud/` | Cloud master (`formint-cloud`) | Django full setup, frontend, django-fusion, Unfold, Channels/WebSocket sync; no Robyn server | Hosted multi-terminal SaaS |
| `formint-standard/` | Standard edition | Astro 5 + React 19 + Tauri 2 + Rust/Diesel | Standard desktop POS |
| `formint-client/` | POS Client | Tauri 2 + Vue 3 + TypeScript + Pinia | Separate desktop client |
| `tests/` | Shared POS validation | pytest, Vitest, API tests, Selenium, Playwright | Cross-edition contracts and flows |
| `scripts/` | Build/release/dev tooling | Node/Python/shell | Packaging, screenshots, i18n, checks |
| `packages/design-system/` | Shared design system | React components, CSS tokens, Double-Bezel architecture | Unified UI language across editions |
| `assets/` | Shared asset registry | Canonical brand/fonts/icons + static delegation | Multi-edition asset ownership |
| `configs/` | Product config contracts | Asset and environment cascade definitions | Shared settings metadata |

The old `pos-mini`, `pos-solo`, `pos-full`, `forge-pos`, and `pos-cloud` names
may appear in migration docs or compatibility manifests. Do not use them for
new source paths unless the compatibility contract specifically requires it.

## Shared packages layout

```text
packages/
├── design-system/          # @formints/design-system
│   ├── src/tokens/         # Design tokens (spacing, colors, typography, motion)
│   ├── src/components/     # React components (BezelCard, CompactInput, CompactButton)
│   ├── src/css/            # CSS variables and animations
│   └── README.md           # Documentation and usage guide
└── formints-client/        # @formints/client (API client)
```

The design system provides a unified design language across all Formint editions.
Import `@formints/design-system` for tokens, components, and CSS utilities.

Shared binary and public assets are owned by `assets/shared/` rather than copied
into each edition. The ownership and wiring contract is recorded in
`configs/assets.yml`; edition configs expose it through `@formints-assets`,
`publicDir`, or Django `STATICFILES_DIRS` as appropriate.

## Professional package layout

```text
formint-pro/
├── server/                 # Django boundary, models, APIs, fragments
│   ├── formint/             # domain models, schemas, controllers, views
│   ├── models/              # POS/CRM/HR/inventory/sync model modules
│   ├── routes/              # API and fragment routes
│   ├── fragments/           # server-rendered data fragments
│   ├── services/            # sync and scheduler services
│   └── tests/               # server/backend integration tests
├── frontend/                # Astro shell and client API/fusion helpers
├── src-tauri/               # native desktop shell
├── assets/                  # source/static product assets
├── migration/               # compatibility manifest and migration notes
└── Makefile
```

The professional product's API, HTMX fragments, and render-mode contract are
shared between the browser shell and desktop shell. Keep model/schema/API
changes synchronized with frontend types and contract tests.

## Cloud master rules

`formint-cloud` now serves the API surface directly from Django on the configured
cloud/API port and uses Channels for WebSocket sync. Do not reintroduce a
Robyn server merely because a variable is still named `SERVER_BASE`; that
name is retained for frontend compatibility. Verify the current `README.md`,
`Makefile`, `backend/configs/`, and `frontend/astro.config.mjs` before changing
ports or server topology.

## Community edition rules

`formint-community` has no Python runtime, Django ORM, or Fusion fragment server. Data
flows through Tauri `invoke` commands to Rust/Diesel/SQLite. Keep native
commands, migrations, TypeScript wrappers, and UI types aligned. Do not copy
professional/cloud backend code into this edition.

## Cross-cutting conventions

- Model and API resources should remain explicit and typed.
- Preserve the Fusion response envelope and render-first/data-API headers where
  they are part of the product contract.
- Sync events and WebSocket frame shapes are contracts; update both producer,
  consumer, and parity tests when changing them.
- Keep secrets, signing keys, database files, and generated release artifacts
  out of commits unless explicitly required by the product.
- Use product-local assets and styles. Do not place POS-specific UI in the
  shared web-site asset tree.
- Prefer narrow vertical slices: model/schema → API/handler → frontend type →
  test.

## Commands

```bash
# Professional package
cd projects/formints/formint-pro
just install              # root Justfile: just install → just install
make migrate
make check
make test
make env                 # effectful: starts backend/frontend sessions

# Cloud master
cd projects/formints/formint-cloud
just install              # root Justfile: just install → just install
make migrate
make check
make test
make dev-backend
make dev-api
make dev-frontend

# Community desktop
cd projects/formints/formint-community
pnpm install
pnpm dev
pnpm tauri dev
pnpm test
npx tsc --noEmit
cargo check --manifest-path src-tauri/Cargo.toml

# Standard edition
cd projects/formints/formint-standard
pnpm install
pnpm dev
pnpm tauri dev
pnpm test

# Vue client
cd projects/formints/formint-client
pnpm install
pnpm dev
pnpm lint
vue-tsc --noEmit
```

Read each edition Makefile before running targets that seed, reset, publish,
or start services.

## Testing matrix

- `packages/design-system/tests/`: design tokens and component unit tests.
- `formint-pro/server/tests/`: backend models, APIs, fragments, sync, WebSockets.
- `formint-pro/frontend/src/**/test*`: frontend contract/unit tests.
- `formint-cloud/backend/apps/test_*.py`: cloud surface and WebSocket parity tests.
- `tests/pos-e2e/`: shared Playwright flows and API tests.
- `tests/js/`, `tests/api/`, and `tests/selenium/`: broader POS validation.

Run the smallest affected suite first, then the edition-level `make check` and
`make test` when practical.
