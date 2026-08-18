# Formint POS — Setup & Build Guide

> **Quick start + detailed setup/build steps for every POS edition**
> **Last updated:** August 2026

Formint POS is a modern, offline-first point-of-sale family for restaurants,
cafes, and food-service businesses — cross-platform desktop (Windows, macOS,
Linux, Android, iOS) plus a cloud SaaS master.

---

## Which edition do I need?

| If you want... | Use... | Stack | Database |
|----------------|--------|-------|----------|
| A free, offline-only desktop POS | **Community** (`formint-community/`) | Tauri 2 + React + Rust | SQLite |
| A standalone Tauri + React desktop edition | **Standard** (`formint-standard/`) | Astro 5 + React 19 + Tauri 2 | SQLite |
| The merged enterprise package (backend + web + desktop) | **Pro** (`formint-pro/`) | Django Ninja + Robyn + Astro + Tauri | SQLite / Postgres |
| A hosted SaaS dashboard for all branches | **Cloud** (`formint-cloud/`) | Django ASGI + Unfold + Bolt | Postgres |
| A thin Vue desktop client | **pos-client** (`formint-client/`) | Vue 3 + Tauri | SQLite |
| A typed TS SDK for editions | **SDK** (`packages/formints-client/`) | TypeScript | — |

The root `projects/formints/Makefile` exposes uniform verbs per edition:

```text
make <edition>-<verb>     # e.g. community-test · pro-env · cloud-check · sdk-test
verbs: install | check | test | run/dev | stop | clean
```

Aggregates: `make install-all` · `make check-all` · `make test-all` ·
`make stop-all` · `make clean-all`.

---

## 1. Community edition (`formint-community/`)

Free, offline-first desktop POS — Tauri 2 + React 19 + Rust + SQLite.

### Prerequisites

```bash
node --version && pnpm --version && rustc --version && cargo --version
```

### Install

```bash
cd projects/formints/formint-community
make install            # pnpm install + cargo fetch
```

### Run

```bash
make dev                # Vite dev server, browser only — http://localhost:1420
make dev-desktop        # full Tauri desktop app (hot-reload, includes Rust backend)
```

### Database & seed

```bash
make seed               # reset + seed restaurant.db (PRESET=all|base|gaming|coffee)
make seed PRESET=coffee # pick a preset
make clean-db           # delete the database only
```

### Check / test

```bash
make check              # TypeScript + Rust compilation check
make typecheck          # tsc --noEmit
make cargo-check        # cargo check
make cargo-test         # cargo test (Rust)
make test               # Vitest unit tests
make test-all           # Vitest + Playwright e2e
make cargo-clippy       # clippy (warnings as errors)
```

### Build

```bash
make build              # production desktop app (.dmg/.msi/.AppImage)
make build-frontend     # frontend only → dist/
make build-android      # Android APK (SDK required)
make build-ios          # iOS app (macOS + Xcode required)
```

### i18n

```bash
make i18n-audit         # regenerate docs/i18n-gaps.md
make i18n-check         # CI-friendly audit (exits non-zero on gaps)
make i18n-fix           # merge AR + regenerate
make i18n-fix-check     # full pipeline
```

---

## 2. Standard edition (`formint-standard/`)

Standalone Tauri + React desktop POS.

```bash
cd projects/formints/formint-standard
make install            # pnpm + cargo
make dev                # Vite dev server (browser only)
make check              # TS + Rust checks
make test               # Vitest unit tests
make clean              # clean artifacts
```

---

## 3. Pro edition (`formint-pro/`) — merged enterprise package

Django Ninja + ninja-extra + django-fusion + Unfold admin (backend),
Astro + Alpine + HTMX (frontend), Tauri 2 (desktop). **45 API resources.**

### Prerequisites

```bash
python3 --version && node --version && pnpm --version && tmux --version
```

### Install + seed

```bash
cd projects/formints/formint-pro
make install            # backend .venv + deps + migrate + frontend npm install
make seed               # migrate + superuser + demo data (admin@formint.local / admin123)
make seed-force         # wipe + re-seed all demo data
```

Demo data seeded: 9 products · 5 customers · 3 loyalty tiers · 12 sales ·
4 suppliers · 3 branches (nodes) · sync logs + menu/employees/CRM.

### Run (tmux env)

```bash
make env                # backend :8767 + frontend :4321 (health-checked)
#   API      → http://127.0.0.1:8767/api/v1/docs
#   Admin    → http://127.0.0.1:8767/admin/
#   Shell    → http://127.0.0.1:4321/
make status             # tmux sessions + endpoint health
make stop               # kill tmux sessions (formint-be / formint-fe)
```

Foreground variants:

```bash
make dev-backend        # runserver :8767
make dev-frontend       # astro dev :4321
```

### Check / test

```bash
make check              # django check + astro check
make test               # backend suite + frontend contract tests
make backend-test       # server tests only
make frontend-test      # frontend contract tests only
```

### Build

```bash
make build              # frontend production build + backend collectstatic
make preview            # astro preview :4321
```

### Desktop (Tauri)

```bash
make desktop            # full desktop dev: backend tmux + Tauri window
make desktop-build      # production desktop bundle (frontend + collectstatic + Tauri)
make server-binary      # PyInstaller server binary → src-tauri/binaries/
make release            # check + test + build + desktop-build
```

### API surface

Base URL: `http://127.0.0.1:8767/api/v1/`

| Endpoint | Description |
|----------|-------------|
| `/api/v1/health` | Service health + product + model count (fusion envelope) |
| `/api/v1/stats` | System stats |
| `/api/v1/openapi.json` | OpenAPI schema |
| `/api/v1/docs` | Swagger UI |
| `/api/v1/{resource}` | Paginated CRUD (45 resources: products, sales, inventory, suppliers, purchase orders, loyalty, CRM, HR, …) |

HTMX fragments: `/htmx/tables/{resource}/` · `/htmx/forms/{resource}/` ·
`/htmx/branches/summary/`. All support the fusion **render-first** contract
via the `X-Fusion-Render-First` header.

---

## 4. Cloud edition (`formint-cloud/`)

Hosted SaaS master — Django ASGI + Unfold admin + django-bolt analytics,
with the Community UI frontend.

### Install

```bash
cd projects/formints/formint-cloud
make install            # backend uv sync + frontend pnpm install
make migrate            # apply Django migrations (shared formint_cloud.db)
```

### Run

```bash
make dev-backend        # Django :8082 (Unfold admin + bolt)
make dev-api            # Django :8767 (daphne — server-compatible API + WebSocket sync)
make dev-frontend       # Astro :4323 (Community UI, proxies API + admin)
make verify-stack       # boot both servers + sweep the full surface
make stop               # kill dev processes
```

### Check / test

```bash
make check              # django check + astro check
make test               # backend Django test suite
make styles             # compile tactical SCSS token layer → static CSS
```

---

## 5. pos-client (`formint-client/`)

Vue 3 + Tauri thin desktop client.

```bash
cd projects/formints/formint-client
make install
make dev                # Vite dev server
make build              # production build
make lint               # oxlint
make test               # lint + vue-tsc typecheck
```

---

## 6. SDK (`packages/formints-client/`)

Typed TypeScript SDK consumed by the editions.

```bash
cd projects/formints/packages/formints-client
pnpm install
pnpm build              # tsc
pnpm typecheck
pnpm test               # vitest
```

Via the root Makefile: `make sdk-install` · `make sdk-build` ·
`make sdk-typecheck` · `make sdk-test`.

---

## 7. Legacy Robyn server (merged, optional)

The merged `formint-pro/server/` retains a Robyn compatibility runner for
desktop packaging:

```bash
cd projects/formints/formint-pro/server
pip install -r requirements.txt
python3 server.py --port 8765              # server
python3 server.py --port 8765 --dev --verbose   # dev + hot reload
DJANGO_SETTINGS_MODULE='' python3 -m pytest tests/ -k 'not rust_db'   # test suite
```

Root aliases: `make server-run` · `make server-dev` · `make server-check` ·
`make server-test` · `make server-clean`.

---

## 8. Publishing & screenshots

```bash
cd projects/formints
make community-bundle   # refresh publish/community-bundle/ from formint-community
make screenshots        # capture marketplace screenshots (Community)
make publish            # prepare publish-bundle/ from the merged edition
```

---

## 9. Troubleshooting

### Port conflicts across editions

Editions share API ports (8767) between Pro and Cloud. Only run one at a
time, or override:

```bash
# Pro: BACKEND_PORT=8770 FRONTEND_PORT=4330 make env
# Cloud: BACKEND_PORT=8083 API_PORT=8771 FRONTEND_PORT=4324 make dev-backend
```

### tmux missing for `make env`

`make env` requires tmux. Run the foreground variants instead:

```bash
make dev-backend && make dev-frontend   # two terminals
```

### Desktop build fails on missing Rust target

Install the Rust target for your platform:

```bash
rustup target add x86_64-pc-windows-msvc   # example for Windows packaging on macOS
```

### Database in a weird state

```bash
make seed PRESET=all     # Community — reset + reseed
make seed-force          # Pro — wipe + reseed
make clean               # Cloud — remove db + bytecode cache
```

---

## See also

- [Root README](../README.md) — editions overview, architecture, features
- [docs/POS_ARCHITECTURE.md](POS_ARCHITECTURE.md) — full architecture
- [docs/SERVER_V2.md](SERVER_V2.md) — merged server v2 reference (70+ APIs)
- [docs/THEME_SYSTEM.md](THEME_SYSTEM.md) — theme variant system
- [docs/ROLE_SYSTEM.md](ROLE_SYSTEM.md) — roles & permissions
- [docs/COMMANDS.md](COMMANDS.md) — CLI command reference
