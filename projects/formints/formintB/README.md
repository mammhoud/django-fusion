# POS Cloud (formintB) — Cloud Master Edition

Hosted multi-terminal SaaS cloud master for Formints. This edition merges the
**formintA Community UI** with the **pos-cloud Django SaaS** backend as a
**full Django setup** — django-fusion viewsets + render-mode contract,
django-bolt analytics, Unfold admin, and channels WebSocket sync — with the
API surface the frontend consumes served directly by Django on `:8767`
(the port the Community UI already targets, so no frontend rewrites were
needed). The Robyn sidecar has been removed.

## Layout (formintC-style project structure, precis-style apps)

```
formintB/
├── backend/                 # Django full setup (pos-cloud)
│   ├── configs/             # settings, urls, asgi, wsgi, Unfold dashboard
│   └── apps/                # precis-style apps package
│       ├── core/            # models (Org, Branch, CRM, reports, sync data) + viewsets + admin
│       ├── domain/          # sync domain services (broker, queue, conflict resolver)
│       └── handlers/        # consumers, sync dashboard, fragments, sync API receivers,
│                            #   fusion contract (fusion.py) + sidecar surface (surface.py)
├── frontend/                # formintA Community UI (Astro + React 19)
│   ├── astro.config.mjs     # dev proxies → API :8767 + admin :8082
│   └── src/                 # pages, components, api client (SIDECAR_BASE → :8767)
└── Makefile                 # one-command orchestration
```

## Architecture

```
Astro frontend (:4323) ──┬── /organizations /branches /leads /deals … → Django API (:8767)
                         │                                              └── Django ORM (pos_cloud.db)
                         ├── /fusion/* (render-mode, nav, session)    → Django API (:8767)
                         ├── /api/sales /api/products /api/settings   → Django API (:8767, bridges)
                         └── /admin /apis/*                           → Django backend (:8082)
```

- **Django API server (:8767)** — one Django process serving the full
  sidecar-compatible surface: django-fusion viewsets for every core model
  (`/organizations`, `/branches`, `/leads`, `/contacts`, `/deals`,
  `/inventory-reports`, `/branch-reports`, `/sync/*`, `/device-tokens`,
  `/conflicts`, `/queue`), the `/fusion/*` render-mode contract, the
  Community-UI bridges (`/api/sales`, `/api/products`, `/api/settings`),
  `/stats`, and `/health`. Anonymous bridges/fusion/stats for the frontend;
  CRUD viewsets are auth-gated via django-fusion permissions.
- **Django admin server (:8082)** — Unfold admin, django-fusion viewsets,
  channels WebSocket sync events, and the BoltAPI analytics dashboard
  (`/apis/data/*`).
- **Shared DB** — both dev servers read/write `backend/pos_cloud.db`
  (the same Django project started on two ports).

## Quick start

```bash
make install        # backend venv + frontend deps
make migrate        # apply Django migrations
make dev-backend    # Django :8082 (Unfold admin + bolt analytics)
make dev-api        # Django :8767 (sidecar-compatible API surface)
make dev-frontend   # Astro :4323 (Community UI)
make check          # django check + astro check
make test           # backend Django test suite
```

> `make dev-sidecar` is kept as an alias for `make dev-api` for
> backwards compatibility with older muscle memory / scripts.

## API surface (served by Django on :8767)

| Resource            | Path                       |
|---------------------|----------------------------|
| Organizations       | `/organizations`           |
| Branches            | `/branches`                |
| Leads / Contacts / Deals | `/leads` `/contacts` `/deals` |
| Reports             | `/inventory-reports` `/branch-reports` |
| Branch sync data    | `/sync/products` `/sync/sales` `/sync/inventory` `/sync/logs` |
| System              | `/device-tokens` `/conflicts` `/queue` |
| Community-UI bridges | `/api/sales` `/api/products` `/api/settings` |
| Sync dashboard      | `/api/dashboard/branches/health` `/api/dashboard/branches/{code}/health` |
|                     | `/api/dashboard/queue/summary` `/api/dashboard/queue/by-branch` `/api/dashboard/queue/list/{status}` |
|                     | `/api/dashboard/queue/retry/{id}` `/api/dashboard/queue/cancel/{id}` |
|                     | `/api/dashboard/conflicts` `/api/dashboard/conflicts/stats` |
|                     | `/api/dashboard/conflicts/{id}/resolve` `/api/dashboard/conflicts/{id}/dismiss` `/api/dashboard/activity` |
| Fusion contract     | `/fusion/health` `/fusion/render-mode` `/fusion/nav` `/fusion/session-mode` `/fusion/assets` |
| System              | `/stats` `/health`         |
| Sync-events WebSocket | `ws://…/ws/sync-events/` |

## WebSocket sync-events stream

The Django Channels consumer (`apps/handlers/consumers.py`, routed in
`configs/asgi.py`) serves the real-time stream the Astro frontend consumes
at `/ws/sync-events/` — same per-branch group + entity-event protocol the
removed Robyn sidecar's `/ws/sync` provided, but served directly by Django
(no separate sidecar process). Use **daphne** to serve it:

```bash
cd backend && .venv/bin/daphne -b 127.0.0.1 -p 8767 configs.asgi:application
```

Client protocol (JSON frames):

```jsonc
→ {"type": "identify", "payload": {"branch_code": "BR001", "node_id": "n-1"}}
← {"type": "identify_ack", "branch_code": "BR001", "node_id": "n-1", "status": "registered"}
← {"entity_type": "products", "synced": 3, "branch": "…", "node_id": "…", "timestamp": "…"}   // sync_event (all clients)
← {"type": "broker_message", "message": {"subtype": "entity_event", "payload": {…}}}              // branch group only
```

The frontend wraps this in `src/api/sync-events.ts` (`createSyncEventsWs`)
with auto-reconnect and typed frames; connect with `branchCode` to join the
per-branch group. Sync receivers (`POST /api/sync/push/*`) broadcast entity
events as they ingest branch data, and the broker pushes targeted messages
back to a branch's connected terminals.

## Notes

- The frontend is the formintA Community UI; `SIDECAR_BASE` points at the
  API server (`VITE_SIDECAR_URL` overrides it) — the variable name is kept
  for compatibility even though Django now answers on that port.
- This edition has no Tauri shell — the Cloud master is hosted (SaaS), so the
  desktop app (`formintA/src-tauri`, `formint/src-tauri`) does not apply.
