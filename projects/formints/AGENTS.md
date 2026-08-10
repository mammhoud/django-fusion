# Formints / POS — AI Agent Instructions

**Path:** `projects/formints/`  
**Product:** Formint(s) restaurant point-of-sale platform

Read the repository root and `projects/AGENTS.md` first. This directory contains
several related products; choose the edition deliberately before editing.

## Edition map

| Path | Identity | Architecture | Use for |
|---|---|---|---|
| `formintA/` | Community/Mini (`formint-pos`) | Tauri 2 + React 19 + Rust + Diesel/SQLite; no Python sidecar | Offline-first desktop POS |
| `formint/` | Professional/Formint POS | Astro + HTMX/Alpine frontend, Django boundary, typed APIs, Fusion fragments, Unfold, Tauri shell | Merged professional product |
| `formint-cloud/` | Cloud master (`formint-cloud`) | Django full setup, frontend, django-fusion, Unfold, Channels/WebSocket sync; no Robyn sidecar | Hosted multi-terminal SaaS |
| `formintC/` | POS Client template | Tauri 2 + Vue 3 + TypeScript + Pinia | Separate desktop client |
| `tests/` | Shared POS validation | pytest, Vitest, API tests, Selenium, Playwright | Cross-edition contracts and flows |
| `scripts/` | Build/release/dev tooling | Node/Python/shell | Packaging, screenshots, i18n, checks |

The old `pos-mini`, `pos-solo`, `pos-full`, `forge-pos`, and `pos-cloud` names
may appear in migration docs or compatibility manifests. Do not use them for
new source paths unless the compatibility contract specifically requires it.

## Professional package layout

```text
formint/
├── sidecar/                 # Django/Robyn boundary, models, APIs, fragments
│   ├── formint/             # domain models, schemas, controllers, views
│   ├── models/              # POS/CRM/HR/inventory/sync model modules
│   ├── routes/              # API and fragment routes
│   ├── fragments/           # server-rendered data fragments
│   ├── services/            # sync and scheduler services
│   └── tests/               # sidecar/backend integration tests
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
Robyn sidecar merely because a variable is still named `SIDECAR_BASE`; that
name is retained for frontend compatibility. Verify the current `README.md`,
`Makefile`, `backend/configs/`, and `frontend/astro.config.mjs` before changing
ports or server topology.

## Community edition rules

`formintA` has no Python runtime, Django ORM, or Fusion fragment server. Data
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
cd projects/formints/formint
make install
make migrate
make check
make test
make env                 # effectful: starts backend/frontend sessions

# Cloud master
cd projects/formints/formint-cloud
make install
make migrate
make check
make test
make dev-backend
make dev-api
make dev-frontend

# Community desktop
cd projects/formints/formintA
pnpm install
pnpm dev
pnpm tauri dev
pnpm test
npx tsc --noEmit
cargo check --manifest-path src-tauri/Cargo.toml

# Vue client
cd projects/formints/formintC
pnpm install
pnpm dev
pnpm lint
vue-tsc --noEmit
```

Read each edition Makefile before running targets that seed, reset, publish,
or start services.

## Testing matrix

- `formint/sidecar/tests/`: backend models, APIs, fragments, sync, WebSockets.
- `formint/frontend/src/**/test*`: frontend contract/unit tests.
- `formint-cloud/backend/apps/test_*.py`: cloud surface and WebSocket parity tests.
- `tests/pos-e2e/`: shared Playwright flows and API tests.
- `tests/js/`, `tests/api/`, and `tests/selenium/`: broader POS validation.

Run the smallest affected suite first, then the edition-level `make check` and
`make test` when practical.
