# Formint Professional — AI Agent Instructions

**Path:** `projects/formints/formint-pro/`  
**Product:** Formint Professional POS (historically `formint/`, `pos-full` + `pos-solo` merged)  
**Stack:** Django + django-ninja + django-fusion + Unfold admin + HTMX + Alpine.js; Astro 5 frontend; Tauri 2 desktop shell

Read `projects/formints/AGENTS.md` and the repository root first. This is the
merged professional product. The `formint-community/`, `formint-cloud/`, and
`formint-client/` editions are separate; do not copy their conventions here.

## Layout

```text
formint-pro/
├── server/                 # Django boundary — models, APIs, fragments, admin
│   ├── formint/             # Domain models, Ninja schemas, controllers, API,
│   │   ├── models/          #   views, fusion components, handlers, templates
│   │   ├── schemas.py       # Ninja writable/patch schema factory
│   │   ├── controllers.py   # 45+ ModelControllerBase CRUD endpoints
│   │   ├── api.py           # NinjaAPI with fusion encoder renderer
│   │   ├── components.py    # django-fusion table/form components
│   │   ├── fusion.py        # Render-mode/nav/assets (precis-landing parity)
│   │   ├── handlers.py      # Class-based HTMX fragment handlers
│   │   ├── admin.py         # Canonical Unfold admin
│   │   └── templates/       # Fusion table + form templates
│   ├── models/              # POS/CRM/HR/inventory/sync model layer
│   ├── routes/              # API and fragment route wiring
│   ├── fragments/           # Server-rendered data fragments
│   ├── services/            # Sync and scheduler services
│   ├── tests/               # Backend integration tests (~66)
│   ├── configs/             # Django settings (Unfold + fusion render-mode)
│   └── Makefile             # Backend targets
├── frontend/                # Astro shell
│   ├── src/pages/           # pos, admin, crm, hr, ops, kitchen, data routes
│   ├── src/components/      # Shared UI shell and components
│   ├── src/lib/             # Fusion decoder, session-sync, HTMX bootstrap
│   ├── src/styles/          # Tokens and global CSS
│   └── src/tests/           # Frontend contract tests
├── src-tauri/               # Tauri 2 desktop shell
├── assets/                  # Pro-only boundary; shared assets live at ../../assets/shared
├── migration/               # Compatibility manifest and migration notes
├── README.md
└── Makefile                 # Root orchestrator (frontend + server + desktop)
```

## Architecture

- **Backend:** Django + django-ninja (typed REST API) + django-fusion (tables,
  forms, fragments, render-mode) + Unfold (admin). The development server uses
  Django runserver on port 8767. A Robyn server (`server/server.py`) exists
  for Tauri desktop bundling as an external binary; do not introduce a second
  Robyn process for the main API surface.
- **Frontend:** Astro 5 + Alpine.js + HTMX shell proxying `/api`, `/htmx`, and
  `/fusion` to the backend.
- **Desktop:** Tauri 2 shell wrapping the Astro frontend with the server as an
  external binary.
- **Render-mode:** Supports fusion-render and data-api modes via
  `X-Fusion-Render-First` header — precis-landing parity contract.

## Conventions

- All API responses use the Fusion envelope (`{ status, message, data }`).
- HTMX fragment endpoints return server-rendered tables/forms with fusion
  component contracts; keep `X-Formint-*` response headers stable.
- Keep Ninja schemas, controllers, and frontend types synchronized.
- Use `{% comp %}` for registered django-fusion components in server templates.
- Preserve Unfold admin integrations and the fusion render-mode toggle.
- Model changes require migrations in `server/formint/models/migrations/`.
- The `SERVER_BASE` variable naming is retained for frontend compatibility;
  the API is served by Django, not a separate Robyn process.

## Commands

```bash
cd projects/formints/formint-pro
just install          # Backend .venv + deps + frontend npm install + migrate
make seed             # Migrate + superuser + demo data (admin@formint.local / admin123)
make env              # Tmux: backend :8767 + frontend :4321
make check            # Django check + astro check
make test             # Backend suite + frontend contract tests
make dev-backend      # Django runserver :8767 (foreground)
make dev-frontend     # Astro dev :4321 (foreground)
make build            # Frontend production build + collectstatic
make desktop          # Tauri desktop dev (backend tmux + Tauri window)
make desktop-build    # Full production desktop bundle
make stop             # Kill tmux sessions
make status           # Tmux sessions + endpoint health
```

## Testing

- `server/tests/`: Backend models, APIs, fragments, sync, WebSocket tests.
- `frontend/src/tests/`: Frontend contract/unit tests (Vitest).
- `src-tauri/`: Rust tests via `cargo test --manifest-path src-tauri/Cargo.toml`.
- Run `make check` before `make test`; use the narrowest suite first.

## Do not

- Do not copy `formint-community` Tauri/Rust patterns into this edition.
- Do not add a separate Robyn/server process; the API is Django-native.
- Do not import `formint-cloud` or `formint-community` internals.
- Do not hard-code ports outside the existing `BACKEND_PORT`/`FRONTEND_PORT` convention.
- Use `@formints-assets` for shared frontend assets and `FORMINT_SHARED_ASSETS`
  for Django static inputs; keep collected files in the Pro `STATIC_ROOT`.
- Do not commit `restaurant.db`, generated installers, secrets, or signing keys.

## Related

- [`../AGENTS.md`](../AGENTS.md) — Formint multi-edition overview
- [`README.md`](README.md) — Full product README with API reference
- [`../../docs/pos/`](../../docs/pos/) — POS documentation
- [`../../../docs/plans/editions/03-pro.md`](../../../docs/plans/editions/03-pro.md) — Professional plan
- [`server/ARCHITECTURE.md`](server/ARCHITECTURE.md) — Server architecture
