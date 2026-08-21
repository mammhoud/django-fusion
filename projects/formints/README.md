# Formints POS — Restaurant Point of Sale

> **Multi-edition restaurant point-of-sale family** — Tauri 2 + React/Rust +
> SQLite (desktop) with optional Django backends (Pro/Cloud) and a Vue 3
> client. Offline-first at the core, cloud-connected at the top.

<p align="center">
  <a href="CHANGELOG.md"><img src="https://img.shields.io/badge/version-1.3.0-blue" alt="Version"/></a>
  <a href="docs/README.md"><img src="https://img.shields.io/badge/docs-repo-green" alt="Documentation"/></a>
  <a href="PUBLISH.md"><img src="https://img.shields.io/badge/publish-marketplace-orange" alt="Publish"/></a>
  <a href="https://github.com/mammhoud/POS"><img src="https://img.shields.io/badge/support-github-lightgrey" alt="Support"/></a>
</p>

Formints is a modern, offline-first point-of-sale family for restaurants,
cafes, and food-service businesses. Every edition runs natively on Windows,
macOS, Linux, Android, and iOS via Tauri; higher tiers add a Django backend,
multi-terminal sync, and a hosted cloud master.

---

## 📦 Editions

| Edition | Directory | Backend | Status |
|---------|-----------|---------|--------|
| **Community** | `formint-community/` | Rust/Diesel + SQLite (no server) | ✅ done |
| **Standard** | `formint-standard/` | Rust/Diesel + SQLite (+ optional Django sidecar) | ✅ done |
| **Pro** | `formint-pro/` | Django + django-fusion + Unfold (required) | ✅ done |
| **Cloud** | `formint-cloud/` | Django (multi-tenant, Channels) — hosted master | 🟡 staging |
| **pos-client** | `formint-client/` | Vue 3 + Tauri + Django shop backend | 🔵 dev |
| **JS/TS SDK** | `packages/formints-client/` | TypeScript (`@formints/client`) | ✅ done |

> Canonical edition plans + capability matrix:
> [`docs/plans/editions/`](../../docs/plans/editions/README.md) (Community `01` ·
> Standard `02` · Pro `03` · Cloud `04` · pos-client `05` · SDK `06` ·
> Community version `07` · tenant schemas `08`) and
> [`comparison.md`](../../docs/plans/editions/comparison.md).

---

## 🚀 Quick Start

> Full step-by-step setup for every edition:
> [`docs/GETTING_STARTED.md`](docs/GETTING_STARTED.md)

### Community / Standard (desktop, no server)

```bash
cd formint-community        # or formint-standard
pnpm install
cd src-tauri && cargo fetch && cd ..
pnpm dev          # Vite dev server at localhost:1420
pnpm dev:desktop  # Full Tauri desktop app
```

### Pro (merged package — backend + web + desktop)

```bash
cd formint-pro
just install      # backend .venv + deps + migrate + frontend npm install
make seed         # migrate + superuser + demo data
make env          # backend :8767 + frontend :4321 (tmux)
make test         # backend + frontend contract tests
make check        # django check + astro check
```

### Cloud (hosted SaaS master)

```bash
cd formint-cloud
just install && make migrate
make dev-backend   # Django :8082 (Unfold admin + bolt analytics)
make dev-api       # Django :8767 (daphne — API + WebSocket sync)
make dev-frontend  # Astro :4323
```

### pos-client (Vue 3 desktop)

```bash
cd formint-client
just install
make dev           # Vite dev server
```

### SDK

```bash
cd packages/formints-client
pnpm install && pnpm build && pnpm test
```

### Using the root Makefile

```bash
make community-test · standard-test · pro-env · cloud-check · client-test · sdk-test
make install-all · check-all · test-all · stop-all · clean-all
```

---

## 🏗️ Architecture

```
formint-community/          # Free, offline-first desktop POS (Rust/Diesel, no server)
formint-standard/           # + currencies, tax profiles, roles, export, offline sync queue
formint-pro/                # Django-first: 45-resource Ninja API, fusion render-mode,
│                           #   Unfold admin, KDS, gaming, gift cards, tables, delivery,
│                           #   kiosk, forecasting, scheduling, customer display, sync
formint-cloud/              # Hosted master: Organization → Branch, async sync,
│                           #   backups + monitoring, schema-per-tenant (flip-on)
formint-client/             # Vue 3 + Tauri desktop client + Django shop backend
packages/formints-client/   # @formints/client — modular TS fetch SDK
tests/                      # Shared POS validation (pytest, Vitest, Playwright e2e)
docs/                       # This documentation tree
```

Data flows (per tier):

```text
Community/Standard:  React → Tauri invoke → Rust/Diesel → SQLite
Pro:                 Astro/HTMX → Django Ninja → Django ORM → SQLite (daphne :8767)
Cloud:               Branches → sync push → Django ASGI (Channels) → pos_cloud.db
pos-client:          Vue 3 → Tauri invoke → Rust → SQLite + Django shop backend
```

---

## 🔧 Tech Stack

| Layer | Technology |
|-------|-----------|
| Desktop | Tauri 2 + Rust (Diesel ORM, SQLite) |
| Frontend | React 19 (Community/Standard) · Astro 5 + Alpine + HTMX (Pro/Cloud) · Vue 3 (pos-client) |
| Backend (Pro/Cloud) | Django 5 + django-fusion + django-ninja + django-unfold |
| Sync | Channels WebSocket (Pro multi-terminal, Cloud master) |
| SDK | `@formints/client` — framework-agnostic TypeScript |
| Testing | pytest (backend) · Vitest (frontend) · Playwright (e2e, `tests/pos-e2e/`) · cargo test (Rust) |
| Build | make, pnpm, uv/.venv |

---

## ✨ Key Features

- **Offline-first desktop POS** — Community/Standard run with no server; data
  stays in local SQLite
- **Refunds & returns** — Rust `refund_sale` + confirm dialog (Community+)
- **Multi-currency, tax profiles, roles, CSV/JSON export** — Standard tier
- **45-resource Django Ninja REST API** — django-fusion encoder/decoder envelope
- **Unfold admin** — KPI dashboard, charts, loyalty & settings management
- **Fusion render-mode** — HTMX fragments / data API dual-mode contract
- **Kitchen Display System (KDS)** — ticket flow with station routing + timers
- **POS-KO Gaming Center** — token-based gaming sessions with time tracking
- **Gift cards, table management, delivery integration, kiosk, forecasting,
  scheduling, customer display, purchase-order workflow** — Pro tier modules
- **Multi-terminal sync + offline queue** — durable outbox with backoff
- **Cloud master** — Organization → Branch hierarchy, async sync pipeline,
  conflict resolution, automatic backups + monitoring
- **i18n** — en/fr/ar (Community) · en/zh-CN (pos-client)
- **Theme system** — 5 variants with Theme Studio (Community)

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [`docs/GETTING_STARTED.md`](docs/GETTING_STARTED.md) | Setup & build guide for every edition |
| [`docs/README.md`](docs/README.md) | In-repo docs index (architecture, reference, legacy) |
| [`docs/architecture/editions.md`](docs/architecture/editions.md) | Per-edition components & features |
| [`docs/architecture/pos-architecture.md`](docs/architecture/pos-architecture.md) | Cross-edition architecture |
| [`docs/COMMANDS.md`](docs/COMMANDS.md) | CLI / Makefile commands reference |
| [`CHANGELOG.md`](CHANGELOG.md) | Full version history |
| [`PUBLISH.md`](PUBLISH.md) | Marketplace publish kit (ThemeForest, CodeCanyon, Gumroad) |
| [`../../docs/plans/editions/README.md`](../../docs/plans/editions/README.md) | Canonical edition plans + finish board |
| [`../../docs/pos/README.md`](../../docs/pos/README.md) | Reader-facing docs site entry |

---

## 🏷️ Environment

Copy `.env.example` to `.env`:

```bash
SUPERUSER_EMAIL=admin@pos.local
SUPERUSER_PASSWORD=changeme
SUPERUSER_NAME=Admin
DATABASE_URL=restaurant.db
SERVER_HOST=127.0.0.1
SERVER_PORT=8765
```

---

## 📄 License

AGPL-3.0 — See [LICENSE](LICENSE)

---

## 🔗 Links

- **Website**: [structa.cloud](https://structa.cloud)
- **GitHub**: [github.com/mammhoud/POS](https://github.com/mammhoud/POS)
- **Marketplace**: See [`PUBLISH.md`](PUBLISH.md) for listing instructions
