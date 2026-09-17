# Structa Cloud — AI Agent Instructions

This is the repository-wide guide for the Structa Cloud monorepo. Read it first,
then read the nearest scoped `AGENTS.md` before changing code. The current
checkout contains `libs/django-fusion/`; references to other internal libraries
are optional/legacy unless their directories are present locally. This document
describes the current filesystem layout; older project names are listed only as
compatibility aliases.

## 1. Repository map

```text
structa.cloud/
├── projects/                 # Product code, shared Django config, and assets
│   ├── precis/               # Product grouping: unified Precis, landing, and research sites
│   │   ├── precis-landing/   # Legacy Precis Landing copy (kept; dispatcher routes to structa.cloud)
│   │   └── precis-ctc/       # Medical research center site
│   ├── syntara/              # Cypercloud AI chat/customizer runtime
│   ├── formints/             # POS editions, cloud backend, and shared tests
│   ├── configs/              # Shared Django settings and workers
│   ├── assets/               # Monorepo-level shared assets
│   ├── scripts/              # Project-local automation
│   ├── webpack/              # Shared/legacy asset configuration
│   ├── Makefile              # Canonical project dispatcher
│   └── pyproject.toml        # Python workspace dependencies and pytest config
├── libs/                     # Reusable libraries (currently django-fusion)
├── application/             # Databases, proxy, Compose, scripts
├── .agents/                 # Agent skills, Kilo/MCP server, runtime config
├── tests/                    # Workspace integration, HTTP, browser, fixtures
├── docs/                     # MkDocs/docs site, plans, and project references
├── .github/                  # CI workflows and composite actions
├── Makefile                 # Root deployment and delegation entry point
└── pyproject.toml            # Root Python/tooling configuration
```

### Current product boundaries

| Product | Canonical path | Main responsibility | Local guidance |
|---|---|---|---|
| Precis (unified) | `projects/structa.cloud/` | Merged product: LMS courses/enrollment/progress/profile + landing marketing/catalog shell | `projects/structa.cloud/AGENTS.md` |
| Precis Landing | `projects/precis/precis-landing/` | Public marketing/catalog site; Astro frontend and Django/Wagtail backend | `projects/precis/precis-landing/AGENTS.md` |
| Cypercloud / Syntara | `projects/syntara/` | AI chat, template discovery, code customization, streaming responses | `projects/syntara/AGENTS.md` |
| Formint POS | `projects/formints/` | Desktop POS, professional product, cloud master, and POS test suites | `projects/formints/AGENTS.md` |
| django-fusion | `libs/django-fusion/` | Shared Django/Wagtail components, routing, fragments, forms, tables, and assets | `libs/django-fusion/AGENTS.md` |
| Infrastructure | `application/` | PostgreSQL, Redis, Traefik/Nginx, Compose, deployment and MCP tooling | `application/AGENTS.md` |
| Workspace tests | `tests/` | Cross-project validation, fixtures, browser tests, and deployment checks | `tests/AGENTS.md` |

### Name and migration rules

- `projects/structa.cloud` is the current filesystem location for the unified Precis
  product (LMS courses/learning/profile merged with the landing marketing/catalog
  shell), renamed and moved from `projects/structa.cloud/`. The dispatcher
  accepts `WEBSITE=structa.cloud`; `WEBSITE=precis-main`, `WEBSITE=precis-lms`, and
  `WEBSITE=precis-landing` are legacy aliases that all map to
  `projects/structa.cloud/`. The runtime identity (container names `precis-main-*`,
  images, `DJANGO_SITE=precis-main`) is intentionally preserved to keep volumes and
  deployed environments valid.
- `precis/precis-landing` is a kept legacy copy of the Precis Landing marketing
  site; `precis-landing` remains its runtime/site identity.
- `precis/precis-ctc` is the standalone medical research center site, mapped
  from `WEBSITE=ctc` / `precis-ctc` to `projects/precis/precis-ctc/`.
- `precis-lms/` was merged into the unified Precis product (now
  `projects/structa.cloud`) and removed; git history is the archive. Do not add new
  product code under any `precis-lms` path.
- `syntara` is the current filesystem location for the product historically
  called Cypercloud. Use `projects/syntara/` in new paths. Preserve the
  `cypercloud` name only where a runtime alias or external contract requires it.
- `formints/formint-community`, `formint-pro`, `formint-cloud`,
  `formint-standard`, and `formint-client` are distinct POS packages
  (historically `formintA`, `formint`, `formintC`). Do not infer that
  `formint-community` and `formint-cloud` share the same backend.
- Older documentation may mention `projects/lms`, `projects/portfolio`,
  `projects/cypercloud`, or `projects/pos`. Treat those as legacy references;
  verify the current path in `projects/Makefile` and the relevant README before
  editing.
- Do not create compatibility symlinks or duplicate source trees merely to
  satisfy stale documentation.

## 2. Scoped guidance hierarchy

Instruction files are cumulative: the nearest file wins for local details, but
root safety and repository rules remain in force.

```text
/AGENTS.md
├── projects/AGENTS.md
│   ├── projects/structa.cloud/AGENTS.md  (moved from projects/structa.cloud/)
│   │   └── projects/structa.cloud/backend/AGENTS.md
│   ├── projects/precis/precis-landing/AGENTS.md
│   ├── projects/syntara/AGENTS.md
│   └── projects/formints/AGENTS.md
│       ├── projects/formints/formint-pro/AGENTS.md
│       ├── projects/formints/formint-community/AGENTS.md
│       ├── projects/formints/formint-standard/AGENTS.md
│       ├── projects/formints/formint-cloud/frontend/AGENTS.md
│       ├── projects/formints/formint-client/AGENTS.md
│       └── projects/formints/tests/pos-e2e/AGENTS.md
├── libs/django-fusion/AGENTS.md
├── application/AGENTS.md
├── .agents/mcp/AGENTS.md
├── tests/AGENTS.md
├── .github/AGENTS.md
└── deeper template/frontend/test AGENTS.md files
```

Before editing:

1. Locate all `AGENTS.md` files from the repository root to the target file.
2. Read the nearest project/backend/frontend/template guidance.
3. Search for existing implementations and callers with `rg`.
4. Confirm the project dispatcher/README before choosing a command.
5. Keep changes inside the owning product boundary unless the change is truly
   shared framework or infrastructure behavior.

## 3. Shared architecture

### Django and Wagtail

Most web products use Django, Wagtail, django-allauth, HTMX, and the local
`django-fusion` package. A normal request is:

```text
Traefik/local server
  → project urls.py
  → middleware (sessions, auth, CSRF, locale, HTMX, site middleware)
  → PageHandler/Viewset/Wagtail page/API endpoint
  → model/service/query layer
  → template, fragment, JSON, or stream response
```

Use Wagtail page models and StreamFields for editor-managed content. Keep
business logic in services, managers, domain modules, or application classes;
do not grow large view functions or templates into service layers.

### Dual rendering

Precis Landing and Formint use a render-first/data-API contract. A request may
receive complete server-rendered HTML, an HTMX fragment, or JSON for an Astro
client. Preserve explicit endpoint contracts and headers when changing either
road. Do not replace a server-rendered fragment with a client-only mock.

### Background work

PostgreSQL is the primary shared relational database in deployed environments.
Redis backs queues/cache and is used by Celery/Dramatiq-related workers. Do not
run migrations, destructive fixture loads, volume pruning, or production
commands against a shared environment without explicit user direction.

## 4. Ownership and placement rules

### Python/Django

- Product code belongs in the product under `projects/<product>/`.
- Shared Django settings belong in `projects/precis/configs/` only when
  multiple products genuinely consume the same behavior.
- Shared framework behavior belongs in `libs/django-fusion/`.
- Prefer existing app boundaries (`models`, `services`, `handlers`, `api`,
  `components`, `management`) over new catch-all modules.
- Use canonical `django_fusion.*` imports. Do not add re-export shims, alias
  modules, or forwarding `__init__.py` re-exports — import the real symbol from
  its owning module. Delete empty/forwarding-only modules and empty directories
  rather than leaving placeholder `__init__.py` files behind.

### Templates and components

- Check the product's template `AGENTS.md` and Django `TEMPLATES['DIRS']`
  before adding a file.
- Use `{% comp "name" /%}` for registered django-fusion components.
- Use `{% include %}` only for genuinely dynamic template names or local
  includes that are not registered components.
- Use `fragment_name` for fragment identifiers and context keys.
- Preserve Wagtail context, translation tags, permissions, and HTMX attributes.
- Use BEM-style classes for reusable UI; do not use IDs for styling.

### Assets

Keep source assets, generated bundles, collected static files, and runtime
media separate. Product-specific SCSS, CSS, JavaScript, images, and locale
files belong under that product. Put assets in `projects/assets/` only when
multiple active products consume them and the owning project is not a better
home. Never edit generated output instead of its source.

### POS

- UI code belongs in the relevant `formints/*/frontend` or `src` tree.
- Native desktop behavior belongs in that edition's `src-tauri/`.
- Professional product APIs, models, fragments, and sync services belong in
  `projects/formints/formint-pro/`.
- Cloud-master behavior belongs in `projects/formints/formint-cloud/`.
- Shared POS E2E tests belong in `projects/formints/tests/pos-e2e/`.
- Do not introduce a Python sidecar into `formint-community`; it is the direct
  Rust/SQLite edition. Do not assume the cloud master still has a Robyn sidecar;
  current `formint-cloud` serves its API from Django.

## 5. Commands and validation

The root Makefile handles infrastructure/deployment. `projects/Makefile` is
the canonical dispatcher for project checks and site commands.

```bash
# Environment and dependencies
uv sync
uv run pytest

# Project dispatcher examples
cd projects
make check WEBSITE=structa.cloud     # unified Precis product (canonical)
make test WEBSITE=structa.cloud
make run-dev WEBSITE=precis-landing
make check WEBSITE=precis-landing
make test WEBSITE=precis-landing   # workspace pytest target; use the project backend test below for focused coverage
make run-dev WEBSITE=precis-ctc   # legacy site alias if present in checkout

# Workspace command layer (root Justfile — thin delegator; every recipe calls make)
just install                       # full workspace install (uv sync + JS + Formints + docs)
just check                         # nx run-many check --all
just test                          # nx run-many test --all
just deploy                        # full stack deploy (postgres-first)
just deploy-docs                   # deploy Docus (nx run docs:deploy)
just deploy-tools                  # deploy self-hosted tools (affine, adminer, …)
just nx run docs:build             # delegate any target to Nx

# Clean family (root Makefile) — safe by default, destructive variants are explicit.
# Every target below preserves volumes (database/media data); only clean-all drops them.
make clean             # generated files: caches, dist, old build artifacts + logs, and root compose teardown (volumes KEPT)
make clean-logs        # generated logs only (preserves .gitkeep)
make clean-docker      # stop known compose stacks + prune unused containers/images/build cache (volumes KEPT)
make clean-unused      # clean + clean-docker: everything unused, volumes preserved
make clean-all         # clean-unused + unused volumes (full teardown — DESTRUCTIVE)
# Never removed by the clean family: node_modules, .venv, and database/media volumes.

# Precis Landing direct workflows
cd projects/precis/precis-landing
just install                  # root Justfile: just install → just install
make check
make build
make backend-migrate
make backend-check
make backend-test

# Precis backend (unified product now at projects/structa.cloud)
cd projects/structa.cloud/backend
make check
make test
make migrate

# Formint professional product
cd projects/formints/formint-pro
make check
make test

# Library tests
cd libs/django-fusion
uv run pytest
```

Use the narrowest relevant check first, then expand only when practical:

- Python/Django: `ruff check`, `python manage.py check`, targeted pytest.
- Astro/TypeScript: the package's `check`, `test`, and `build` scripts.
- Rust/Tauri: `cargo check` and targeted `cargo test`.
- Playwright: the scoped project command, with browsers already installed.
- Compose/YAML: `docker compose -f <file> config -q` and YAML parsing where
  applicable. Do not bring up the stack merely to validate documentation.

## 6. Safety rules

- Do not commit, push, reset, restore, delete, prune, migrate production data,
  or install global packages unless explicitly requested.
- Treat `docker compose down --volumes`, `docker system prune`, fixture reloads,
  database restores, certificate operations, and deployment targets as
  effectful operations requiring confirmation.
- The root clean family is volume-safe by design: `make clean`, `clean-docker`,
  and `clean-unused` stop stacks and prune unused Docker resources but always
  preserve volumes. Only `make clean-all` removes unused volumes (`docker
  volume prune -f`) — treat it as destructive and confirm before running it
  against a shared environment.
- Never print secrets, tokens, passwords, private keys, or full environment
  files. Use `.env.example` names without values.
- Preserve pre-existing user changes. Inspect `git status` before editing and
  do not revert unrelated changes.
- If an exported symbol or route changes, search and update all references.
- Keep documentation paths synchronized with the actual tree and Makefile
  aliases. If a project is renamed or migrated, document both the canonical
  path and the compatibility alias.

## 7. Change checklist

Before finishing a change:

- [ ] Read the applicable scoped `AGENTS.md` files.
- [ ] Confirm the owning product and current path.
- [ ] Search for existing helpers, components, routes, and tests.
- [ ] Keep generated files and unrelated worktree changes untouched.
- [ ] Add or update focused tests when behavior changes.
- [ ] Run the narrowest check and report any unavailable broader checks.
- [ ] Review the diff for stale paths, accidental secrets, and scope leakage.
