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
│   ├── precis/               # Current LMS / learning platform
│   ├── landing-fusion/       # Astro marketing site + Django/Wagtail CMS
│   ├── syntara/              # Cypercloud AI chat/customizer runtime
│   ├── formints/             # POS editions, cloud backend, and shared tests
│   ├── configs/              # Shared Django settings and workers
│   ├── assets/               # Monorepo-level shared assets
│   ├── lms-fusion/           # Retired compatibility project; merged elsewhere
│   ├── scripts/              # Project-local automation
│   ├── webpack/              # Shared/legacy asset configuration
│   ├── Makefile              # Canonical project dispatcher
│   └── pyproject.toml        # Python workspace dependencies and pytest config
├── libs/                     # Reusable libraries (currently django-fusion)
├── applications/             # Databases, proxy, Compose, scripts, Kilo/MCP
├── tests/                    # Workspace integration, HTTP, browser, fixtures
├── docs/                     # MkDocs/docs site, plans, and project references
├── .github/                  # CI workflows and composite actions
├── Makefile                 # Root deployment and delegation entry point
└── pyproject.toml            # Root Python/tooling configuration
```

### Current product boundaries

| Product | Canonical path | Main responsibility | Local guidance |
|---|---|---|---|
| Precis LMS | `projects/precis/` | Django/Wagtail learning platform: courses, enrollment, progress, profiles, content | `projects/precis/backend/AGENTS.md` |
| Landing-Fusion | `projects/landing-fusion/` | Public marketing/catalog site; Astro frontend and Django/Wagtail backend | `projects/landing-fusion/AGENTS.md` |
| Cypercloud / Syntara | `projects/syntara/` | AI chat, template discovery, code customization, streaming responses | `projects/syntara/AGENTS.md` |
| Formint POS | `projects/formints/` | Desktop POS, professional product, cloud master, and POS test suites | `projects/formints/AGENTS.md` |
| django-fusion | `libs/django-fusion/` | Shared Django/Wagtail components, routing, fragments, forms, tables, and assets | `libs/django-fusion/AGENTS.md` |
| Infrastructure | `applications/` | PostgreSQL, Redis, Traefik/Nginx, Compose, deployment and MCP tooling | `applications/AGENTS.md` |
| Workspace tests | `tests/` | Cross-project validation, fixtures, browser tests, and deployment checks | `tests/AGENTS.md` |

### Name and migration rules

- `precis` is the current filesystem location for the LMS product. The
  dispatcher still accepts `WEBSITE=lms-fusion`; that alias maps to
  `projects/precis/`.
- `lms-fusion/` is a retired compatibility/documentation boundary. Do not add
  new product code there; update Precis or Landing-Fusion instead.
- `syntara` is the current filesystem location for the product historically
  called Cypercloud. Use `projects/syntara/` in new paths. Preserve the
  `cypercloud` name only where a runtime alias or external contract requires it.
- `formints/formintA`, `formint-cloud`, `formintC`, and `formint` are distinct POS
  packages. Do not infer that `formintA` and `formint-cloud` share the same backend.
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
│   ├── projects/precis/backend/AGENTS.md
│   ├── projects/landing-fusion/AGENTS.md
│   ├── projects/syntara/AGENTS.md
│   └── projects/formints/AGENTS.md
├── libs/django-fusion/AGENTS.md
├── applications/AGENTS.md
│   └── applications/kilo/AGENTS.md
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

Landing-Fusion and Formint use a render-first/data-API contract. A request may
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
- Shared Django settings belong in `projects/configs/` only when multiple
  products genuinely consume the same behavior.
- Shared framework behavior belongs in `libs/django-fusion/`.
- Prefer existing app boundaries (`models`, `services`, `handlers`, `api`,
  `components`, `management`) over new catch-all modules.
- Use canonical `django_fusion.*` imports. Do not add re-export shims or alias
  modules.

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
  `projects/formints/formint/`.
- Cloud-master behavior belongs in `projects/formints/formint-cloud/`.
- Shared POS E2E tests belong in `projects/formints/tests/pos-e2e/`.
- Do not introduce a Python sidecar into `formintA`; it is the direct Rust/
  SQLite edition. Do not assume the cloud master still has a Robyn sidecar;
  current formint-cloud serves its API from Django.

## 5. Commands and validation

The root Makefile handles infrastructure/deployment. `projects/Makefile` is
the canonical dispatcher for project checks and site commands.

```bash
# Environment and dependencies
uv sync
uv run pytest

# Project dispatcher examples
cd projects
make check WEBSITE=lms-fusion       # maps to Precis
make test WEBSITE=lms-fusion
make run-dev WEBSITE=landing-fusion
make check WEBSITE=landing-fusion
make test WEBSITE=landing-fusion   # workspace pytest target; use the project backend test below for focused coverage
make run-dev WEBSITE=ctc-research   # legacy site alias if present in checkout

# Landing-Fusion direct workflows
cd projects/landing-fusion
make install
make check
make build
make backend-migrate
make backend-check
make backend-test

# Precis backend
cd projects/precis/backend
make check
make test
make migrate

# Formint professional product
cd projects/formints/formint
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
