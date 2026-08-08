# POS Cloud (formintB) — Cloud Master Edition

Hosted multi-terminal SaaS cloud master for Formints. This edition merges the
**formintA Community UI** with the **pos-cloud Django SaaS** backend, served
through a **Robyn sidecar** for fast async REST APIs over the same Django ORM.

## Layout (formintC-style project structure, precis-style apps)

```
formintB/
├── backend/                 # Django SaaS (pos-cloud)
│   ├── configs/             # settings, urls, asgi, wsgi, Unfold dashboard
│   └── apps/                # precis-style apps package
│       ├── core/            # models (Org, Branch, CRM, reports, sync data) + viewsets + admin
│       ├── domain/          # sync domain services (broker, queue, conflict resolver)
│       └── handlers/        # consumers, sync dashboard, fragments, sync API receivers
├── sidecar/                 # Robyn + Django ORM sidecar (REST APIs on :8767)
│   ├── server.py            # bootstrap + CRUD registration
│   ├── handlers.py          # serialization + generic CRUD helpers
│   └── routes/              # feature routes (fusion render-mode contract)
├── frontend/                # formintA Community UI (Astro + React 19)
│   ├── astro.config.mjs     # dev proxies → sidecar :8767 + backend :8082
│   └── src/                 # pages, components, api client (SIDECAR_BASE → :8767)
└── Makefile                 # one-command orchestration
```

## Architecture

```
Astro frontend (:4323) ──┬── /organizations /branches /leads /deals … → Robyn sidecar (:8767)
                         │                                              └── Django ORM (pos_cloud.db)
                         ├── /fusion/* (render-mode, nav, session)    → Robyn sidecar
                         └── /admin /apis/*                           → Django backend (:8082)
```

- **Sidecar** — one Robyn async server, all pos-cloud models exposed as
  `GET/POST/PATCH/DELETE` REST endpoints plus `/health`, `/stats`, and the
  django-fusion render-mode contract (`/fusion/*`).
- **Django backend** — Unfold admin, django-fusion viewsets, channels
  WebSocket sync events, and the BoltAPI analytics dashboard.
- **Shared DB** — both layers read/write `backend/pos_cloud.db`.

## Quick start

```bash
make install        # backend venv + sidecar venv + frontend deps
make migrate        # apply Django migrations
make dev-backend    # Django :8082 (admin + fusion road)
make dev-sidecar    # Robyn :8767 (REST APIs)
make dev-frontend   # Astro :4323 (Community UI)
make check          # django check + astro check
make test           # backend + sidecar tests
```

## Sidecar REST surface

| Resource            | Path                       |
|---------------------|----------------------------|
| Organizations       | `/organizations`           |
| Branches            | `/branches`                |
| Leads / Contacts / Deals | `/leads` `/contacts` `/deals` |
| Reports             | `/inventory-reports` `/branch-reports` |
| Branch sync data    | `/sync/products` `/sync/sales` `/sync/inventory` `/sync/logs` |
| System              | `/device-tokens` `/conflicts` `/queue` |
| Fusion contract     | `/fusion/health` `/fusion/render-mode` `/fusion/nav` `/fusion/session-mode` |

## Notes

- The frontend is the formintA Community UI; `SIDECAR_BASE` points at the
  sidecar (`VITE_SIDECAR_URL` overrides it).
- This edition has no Tauri shell — the Cloud master is hosted (SaaS), so the
  desktop app (`formintA/src-tauri`, `formint/src-tauri`) does not apply.
