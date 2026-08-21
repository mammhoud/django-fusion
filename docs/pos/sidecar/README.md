# 🖥️ Sidecar — Server Architecture (archived)

> **⛔ ARCHIVED (21 Aug 2026).** This folder documents the **retired POS
> sidecar** — the embedded Python **Robyn/Sanic** server (with Django-ORM
> mirror models) that extended the old `pos-solo` / `pos-full` editions.
> The sidecar was **removed** from every current edition:
>
> - **Community / Standard** are offline-first (Tauri `invoke` → Rust/Diesel,
>   no server at all).
> - **Pro** serves its API from Django (daphne ASGI + django-fusion).
> - **Cloud** serves its API from Django (daphne + Channels WebSocket).
>
> Do **not** follow the paths, ports (`8765`/`8766`), commands, or model maps
> below — they describe code that no longer exists.

## Canonical sources

| Topic | Canonical doc |
|-------|---------------|
| Edition chain + data model + E2E matrix | [`docs/plans/editions/README.md`](../../plans/editions/README.md) |
| Feature/capability comparison + buyer guide | [`docs/plans/editions/comparison.md`](../../plans/editions/comparison.md) |
| Pro edition (Django API + fusion) | [`docs/plans/editions/03-pro.md`](../../plans/editions/03-pro.md) |
| Cloud edition (Django master, sync) | [`docs/plans/editions/04-cloud.md`](../../plans/editions/04-cloud.md) |
| Pro ↔ Cloud sync contract | [`projects/formints/docs/architecture/pro-cloud-sync-contract.md`](../../../projects/formints/docs/architecture/pro-cloud-sync-contract.md) |
| Setup & build per edition | [`projects/formints/docs/GETTING_STARTED.md`](../../../projects/formints/docs/GETTING_STARTED.md) |

## Archived files in this folder

| File | Was |
|------|-----|
| `sidecar-api.md` | Full API reference for the Sanic/Robyn sidecar |
| `sidecar-readme.md` | Sanic server overview (chat, tickets, data APIs) |
| `sidecar-websocket.md` | Chat WebSocket protocol (`/ws/chat/<room>`) |
| `django-orm.md` | Django-ORM mirror models in the sidecar |
| `django-bolt-integration.md` | django-bolt API integration plan |
| `network-architecture.md` | Three-tier pos-mini/pos-solo/pos-full network model |
| `robyn-migration.md` | Sanic → Robyn migration record (historical) |

> The in-repo legacy copies live in
> [`projects/formints/docs/legacy/`](../../../projects/formints/docs/legacy/README.md).
