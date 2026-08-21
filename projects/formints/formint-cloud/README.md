# Formint Cloud — Hosted SaaS Master

Hosted multi-terminal SaaS cloud master for Formints. This edition merges the
**Community UI** with the **Formint Cloud Django SaaS** backend as a
**full Django setup** — django-fusion viewsets + render-mode contract,
django-bolt analytics, Unfold admin, and channels WebSocket sync — with the
API surface the frontend consumes served directly by Django on `:8767`
(the port the Community UI already targets, so no frontend rewrites were
needed). The Robyn server has been removed.

## Layout (formintC-style project structure, precis-style apps)

```
formint-cloud/
├── backend/                 # Django full setup (Formint Cloud)
│   ├── configs/             # settings, urls, asgi, wsgi, Unfold dashboard
│   └── apps/                # precis-style apps package
│       ├── core/            # models (Org, Branch, CRM, reports, sync data) + viewsets + admin
│       ├── domain/          # sync domain services (broker, queue, conflict resolver)
│       └── handlers/        # consumers, sync dashboard, fragments, sync API receivers,
│                            #   fusion contract (fusion.py) + server surface (surface.py)
├── frontend/                # formintA Community UI (Astro + React 19)
│   ├── astro.config.mjs     # dev proxies → API :8767 + admin :8082
│   └── src/                 # pages, components, api client (SERVER_BASE → :8767)
└── Makefile                 # one-command orchestration
```

## Architecture

```
Astro frontend (:4323) ──┬── /organizations /branches /leads /deals … → Django API (:8767)
                         │                                              └── Django ORM (formint_cloud.db)
                         ├── /fusion/* (render-mode, nav, session)    → Django API (:8767)
                         ├── /api/sales /api/products /api/settings   → Django API (:8767, bridges)
                         └── /admin /apis/*                           → Django backend (:8082)
```

- **Django API server (:8767)** — one Django process serving the full
  server-compatible surface: django-fusion viewsets for every core model
  (`/organizations`, `/branches`, `/leads`, `/contacts`, `/deals`,
  `/inventory-reports`, `/branch-reports`, `/sync/*`, `/device-tokens`,
  `/conflicts`, `/queue`), the `/fusion/*` render-mode contract, the
  Community-UI bridges (`/api/sales`, `/api/products`, `/api/settings`),
  `/stats`, and `/health`. Anonymous bridges/fusion/stats for the frontend;
  CRUD viewsets are auth-gated via django-fusion permissions.
- **Django admin server (:8082)** — Unfold admin, django-fusion viewsets,
  channels WebSocket sync events, and the BoltAPI analytics dashboard
  (`/apis/data/*`).
- **Shared DB** — both dev servers read/write `backend/formint_cloud.db`
  (the same Django project started on two ports).

## Quick start

```bash
just install        # backend venv + frontend deps
make migrate        # apply Django migrations
make dev-backend    # Django :8082 (Unfold admin + bolt analytics)
make dev-api        # Django :8767 (server-compatible API surface)
make dev-frontend   # Astro :4323 (Community UI)
make check          # django check + astro check
make test           # backend Django test suite
```

> **Run `make migrate` before first boot.** A fresh clone ships with an
> un-migrated (or stale) `backend/formint_cloud.db`, so the first server start
> prints "unapplied migrations" warnings (e.g. the dependency migrations
> django-fusion pulls in via wagtailcore) and clutters the boot log.
> `make migrate` applies everything up front and keeps `make dev-backend` /
> `make dev-api` boots clean. The seeded dev DB is gitignored, so this is
> required on every fresh checkout.
>
> `make dev-server` is kept as an alias for `make dev-api` for
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
removed Robyn server's `/ws/sync` provided, but served directly by Django
(no separate server process). Use **daphne** to serve it:

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

**This protocol is contract-tested.**
[`apps/test_ws_parity_contract.py`](backend/apps/test_ws_parity_contract.py)
pins the exact frame shapes to the README — `identify_ack` by exact value
(fully deterministic), `sync_event` as the raw payload with *no*
`{type, …}` envelope, `broker_message` as the outer `{type, message}`
envelope wrapping the full `BrokerMessage.to_dict()` shape, and the
`error` frame. `make verify-stack` additionally runs a live end-to-end
parity check (real WebSocket connect → identify → sync push → frame
shape assertions) via `scripts/dev/verify-stack.mjs`.

The frontend wraps this in `src/api/sync-events.ts` (`createSyncEventsWs`)
with auto-reconnect and typed frames; connect with `branchCode` to join the
per-branch group. Sync receivers (`POST /api/sync/push/*`) broadcast entity
events as they ingest branch data, and the broker pushes targeted messages
back to a branch's connected terminals.

The sync monitor (`/apis/data/sync-monitor`) consumes this stream directly:
it renders a live feed from `sync_event` frames, refreshes its branch-health
and queue tiles on each push (no interval polling while connected), and shows
a red `LINK LOST` banner with auto-retry + manual retry when the socket
drops. Terminal connect/disconnect frames (`terminal_connected` /
`terminal_disconnected`) let the monitor update health in real time. The
monitor connects to the daphne API port (`:8767`) — the `WS_PORT` constant at
the top of its embedded script.

## Admin design system — Tactical Telemetry

The whole Unfold admin surface (login, KPI dashboard, CRUD changelists)
runs the `industrial-brutalist-ui` Tactical Telemetry design language from
the sync monitor: CRT substrate `#0A0A0A`, phosphor `#EAEAEA`, hazard red
`#E61919` as the only accent, exactly one terminal-green `#4AF626` element
per surface (the live WebSocket fleet-link dot), zero border-radius,
monospace telemetry, scanline + grain texture.

**Shared SCSS token layer** — single source of truth:

```
backend/apps/core/static/tactical/scss/
├── _tokens.scss      # design tokens: colors, fonts, spacing, texture, button mixins
├── _base.scss        # admin skeleton re-skin (header, sidebar, focus, scrollbars)
├── _login.scss       # operator gate (login)
├── _dashboard.scss   # KPI dashboard components + floating sync-log panel re-skin
├── _changelist.scss  # CRUD list overrides (tables, filters, pagination)
├── _changeform.scss  # change-form detail pages (fieldsets, tabs, inlines,
│                     #   save bar, history sidebar)
└── tactical.scss     # entry point
```

Compiled to `apps/core/static/tactical/css/tactical.css` and wired into
`UNFOLD["STYLES"]` in `backend/configs/__init__.py`. Rebuild after editing:

```bash
make styles    # npx sass … --style=compressed
```

The compiled CSS is committed, so the app works without a Sass toolchain.
`tokens` are also bridged to CSS custom properties (`--tactical-*`) for
inline styles, templates, and JS.

## Design references

Static concept boards — open directly in a browser, no build step. Both
follow the same Tactical Telemetry design bible. Full index with open
instructions: [`docs/README.md`](docs/README.md).

| Board | Path | Contents |
|-------|------|----------|
| Mobile ops companion | [`docs/mobile_ops_preview.html`](docs/mobile_ops_preview.html) | 6-screen iPhone concept set: unit registration, branch overview roster, sync queue, conflict resolution, plus WS link-lost and first-run empty-queue states |
| Desktop sync monitor | [`docs/desktop_monitor_preview.html`](docs/desktop_monitor_preview.html) | 1440px editorial board: the brutalist telemetry dashboard in a desktop browser frame, spec sheet + design-bible annotation cards |

### Screenshots

| Mobile ops companion | Desktop sync monitor |
|---|---|
| ![Mobile ops concept board](docs/images/mobile-ops-preview.png) | ![Desktop sync monitor concept board](docs/images/desktop-monitor-preview.png) |

Regenerate the PNGs with `node scripts/dev/screenshot-boards.mjs` (headless
Chromium via the frontend's Playwright) whenever the boards change. The script
captures at 2× DPR, then downscales to 1280px wide and palette-quantizes to
256 colors (via Pillow in `backend/.venv`) so the committed PNGs stay lean.

## Notes

- The frontend is the formintA Community UI; `SERVER_BASE` points at the
  API server (`VITE_SERVER_URL` overrides it) — the variable name is kept
  for compatibility even though Django now answers on that port.
- This edition has no Tauri shell — the Cloud master is hosted (SaaS), so the
  desktop app (`formint-community/src-tauri`, `formint/src-tauri`) does not apply.
