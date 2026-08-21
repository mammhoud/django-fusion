# 🔧 POS — Infrastructure

> **Archived (21 Aug 2026).** This page previously described the retired
> `Minimal` / `Solo` / `Full` editions and their **Robyn + Django-ORM sidecar**
> infrastructure (`pos-solo/sidecar`, `pos-full/sidecar`, ports 8765/8766,
> `projects/formints/shared/`). The sidecar was removed — Robyn no longer
> exists in any current edition.

## Current infrastructure (canonical)

| Edition | Runtime | Ports | Database |
|---------|---------|-------|----------|
| **Community** (`formint-community/`) | Tauri 2 + Rust/Diesel, offline-first, no server | 1420 (Vite) | SQLite (`restaurant.db`) |
| **Standard** (`formint-standard/`) | Tauri 2 + Rust/Diesel, offline-first | 1430 (Vite) | SQLite |
| **Pro** (`formint-pro/`) | Django (daphne ASGI) + django-fusion + Unfold | 8767 (API) / 4321 (frontend) | SQLite / Postgres |
| **Cloud** (`formint-cloud/`) | Django (daphne + Channels), hosted master | 8767 (API) / 8082 (admin) / 4323 (frontend) | `formint_cloud.db` / Postgres |
| **pos-client** (`formint-client/`) | Vue 3 + Tauri + Django shop backend | 1433 (Vite) | SQLite |

## Canonical sources

| Topic | Canonical doc |
|-------|---------------|
| Edition chain + data model + E2E matrix | [`docs/plans/editions/README.md`](../plans/editions/README.md) |
| Feature/capability comparison + buyer guide | [`docs/plans/editions/comparison.md`](../plans/editions/comparison.md) |
| Cloud edition (hosted master, sync, backups) | [`docs/plans/editions/04-cloud.md`](../plans/editions/04-cloud.md) |
| Pro ↔ Cloud sync contract | [`projects/formints/docs/architecture/pro-cloud-sync-contract.md`](../../projects/formints/docs/architecture/pro-cloud-sync-contract.md) |
| Setup & build per edition | [`projects/formints/docs/GETTING_STARTED.md`](../../projects/formints/docs/GETTING_STARTED.md) |

## Port reference (current)

| Service | Port | Protocol |
|---------|------|----------|
| Community Vite dev | `1420` | HTTP (Vite) |
| Standard Vite dev | `1430` | HTTP (Vite) |
| Pro Django API | `8767` | HTTP + WebSocket (daphne) |
| Pro Astro frontend | `4321` | HTTP |
| Cloud Django admin | `8082` | HTTP |
| Cloud Django API | `8767` | HTTP + WebSocket (Channels) |
| Cloud Astro frontend | `4323` | HTTP |
| pos-client Vite dev | `1433` | HTTP |
