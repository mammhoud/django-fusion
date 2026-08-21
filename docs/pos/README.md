# POS — Restaurant Point of Sale Desktop App

> **Related Names:** `pos`, `POS system`, `desktop app`, `Tauri`, `React`, `Rust`, `SQLite`, `point-of-sale`, `offline-first`, `i18n`
> **Tags:** #site #pos #desktop #tauri #rust #react #offline

**Canonical path:** `projects/formints/`  \
**Stack:** Tauri 2 + React 19 + Rust (Diesel ORM) + SQLite (+ Django for Pro/Cloud)  \
**Platforms:** Windows, macOS, Linux, Android, iOS

> **Current edition model (21 Aug 2026):** Community ✅ done · Standard ✅
> done · Pro ✅ done · Cloud 🟡 staging · pos-client 🔵 dev. The retired
> 3-edition model (Minimal/Solo/Full) with its Robyn sidecar was removed; the
> pages below that still describe it are kept for history only. Canonical
> sources:
> [editions pointer](editions.md) ·
> [`docs/plans/editions/`](../plans/editions/README.md) (plans + finish board) ·
> [`docs/plans/editions/comparison.md`](../plans/editions/comparison.md) ·
> [product docs](../../projects/formints/docs/README.md).

---

## Overview

POS (now **Formints**) is a modern, offline-first desktop point-of-sale
family for restaurants, cafes, and food-service businesses. The desktop
editions (Community, Standard) are fully offline — Tauri `invoke` → Rust/Diesel
→ local SQLite, no server. The Pro and Cloud editions add a Django backend
(django-fusion, Unfold admin, Channels sync) and a hosted multi-tenant master.

## Editions at a glance

| Edition | Directory | Backend | Status |
|---------|-----------|---------|--------|
| **Community** | `formint-community/` | Rust/Diesel + SQLite (no server) | ✅ done |
| **Standard** | `formint-standard/` | Rust/Diesel + SQLite (+ optional Django sidecar) | ✅ done |
| **Pro** | `formint-pro/` | Django + django-fusion + Unfold (required) | ✅ done |
| **Cloud** | `formint-cloud/` | Django (multi-tenant, Channels) — hosted master | 🟡 staging |
| **pos-client** | `formint-client/` | Vue 3 + Tauri + Django shop backend | 🔵 dev |
| **JS/TS SDK** | `packages/formints-client/` | TypeScript (`@formints/client`) | ✅ done |

## Quick Start (current)

```bash
# Community / Standard (offline-first desktop)
cd projects/formints/formint-community    # or formint-standard
pnpm install && cd src-tauri && cargo fetch && cd ..
pnpm dev            # Vite dev server at localhost:1420

# Pro (merged package — backend + web + desktop)
cd projects/formints/formint-pro
just install && make seed && make env    # backend :8767 + frontend :4321

# Cloud (hosted master)
cd projects/formints/formint-cloud
just install && make migrate
make dev-backend && make dev-api && make dev-frontend

# pos-client (Vue 3 desktop)
cd projects/formints/formint-client && make dev
```

Full per-edition setup: [`projects/formints/docs/GETTING_STARTED.md`](../../projects/formints/docs/GETTING_STARTED.md).

## Canonical sources

| Topic | Canonical doc |
|-------|---------------|
| Edition plans + finish board | [`docs/plans/editions/README.md`](../plans/editions/README.md) |
| Feature/capability matrix + buyer guide | [`docs/plans/editions/comparison.md`](../plans/editions/comparison.md) |
| Per-edition components & features | [`projects/formints/docs/architecture/editions.md`](../../projects/formints/docs/architecture/editions.md) |
| Setup & build per edition | [`projects/formints/docs/GETTING_STARTED.md`](../../projects/formints/docs/GETTING_STARTED.md) |
| CLI / Makefile commands | [`projects/formints/docs/COMMANDS.md`](../../projects/formints/docs/COMMANDS.md) |
| Changelog | [`changelog.md`](changelog.md) |
| Strategy (private) 🔒 | [`../startup/formints.md`](../startup/formints.md) |

## Remarks

| # | Note |
|---|------|
| ⚠️ | POS requires **Rust toolchain** + Tauri CLI (`cargo install tauri-cli`) |
| ⚠️ | Auth is optional — configure via `SUPERUSER_EMAIL` + `SUPERUSER_PASSWORD` env vars |
| 🌐 | Community i18n: English, French, Arabic · pos-client: English, Chinese |
| ⛔ | The Robyn/Sanic **sidecar was removed** — see [`sidecar/README.md`](sidecar/README.md) (archived) and [`infrastructure.md`](infrastructure.md) |
| 📁 | Retired edition pages (Minimal/Solo/Full, sidecar, Sanic) are archived in [`features.md`](features.md), [`infrastructure.md`](infrastructure.md), [`use-cases.md`](use-cases.md), and `sidecar/` |

## Related Documentation

| Area | Path |
|------|------|
| POS docs (in-project, canonical) | [`projects/formints/docs/`](../../projects/formints/docs/README.md) |
| Editions guide (pointer) | [`editions.md`](editions.md) |
| Rust backend | [`backend/rust-backend.md`](backend/rust-backend.md) |
| TypeScript frontend | [`frontend/typescript-frontend.md`](frontend/typescript-frontend.md) |
| POS changelog | [`changelog.md`](changelog.md) |
| Development guide | [`../../guides/03-dev.md`](../../guides/03-dev.md) |
| Formint strategy 🔒 | [`../startup/formints.md`](../startup/formints.md) |
| Full portfolio strategy 🔒 | [`../startup/STRATEGY.md`](../startup/STRATEGY.md) |
