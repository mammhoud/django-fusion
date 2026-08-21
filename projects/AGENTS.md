# `projects/` — Product Workspace Guidance

This directory contains the active product applications, shared Django
configuration, project assets, and the canonical project Makefile. Read the
repository root `AGENTS.md` first.

## Current tree

```text
projects/
├── precis/             # Product grouping: unified Precis, landing, and research sites
│   ├── precis-main/    # Unified Precis product (merged precis-landing + precis-lms)
│   ├── precis-ctc/     # Medical research center site
│   └── precis-landing/ # Legacy Precis Landing copy (kept; dispatcher routes to precis-main)
├── syntara/            # Cypercloud AI chat/customizer runtime
├── formints/           # POS editions and their shared test suites
├── loop-crm/           # Unified CRM + social scheduling (Twenty + Postiz merge)
├── configs/            # Shared settings, middleware, workers, env config
├── assets/             # Monorepo-level shared assets
├── scripts/            # Project automation
├── webpack/            # Shared/legacy asset configuration
├── Makefile            # Website dispatcher and delegated workflows
└── pyproject.toml      # Workspace dependencies and pytest configuration
```

Generated or local directories such as `logs/`, `.pytest_cache/`, and
`.ruff_cache/` are not product boundaries.

## Dispatcher and aliases

`projects/Makefile` is authoritative for `WEBSITE` routing. It maps legacy
identifiers to current directories, so always inspect its `SITE`, `PROJECT_DIR`,
`COMPOSE_FILE`, `MANAGE`, and `DOCKER_SERVICE` values before running a command.
Important mappings include:

| `WEBSITE` value | Current code | Meaning |
|---|---|---|
| `precis-lms` | `projects/precis/precis-main/` | Legacy alias — merged into precis-main |
| `precis-landing` | `projects/precis/precis-main/` | Legacy alias — merged into precis-main (dir kept) |
| `loop-crm` | `projects/loop-crm/` | Unified CRM + social scheduling (Twenty + Postiz merge) |
| `cypercloud` (where supported) | `projects/syntara/` | Historical product name |
| `ctc`, `precis-ctc` | `projects/precis/precis-ctc/` | Standalone medical research center site |
| `structa`, `lms` | checkout-dependent LMS alias | Historical public-site aliases |
| `vresume`, `portfolio` | checkout-dependent portfolio alias | Historical portfolio aliases |

Do not add a new alias just to hide a path mismatch. Update the dispatcher and
its documentation together when a product boundary actually changes.

## Product selection workflow

```bash
cd projects
make show-config WEBSITE=precis-main
make check WEBSITE=precis-main
make test WEBSITE=precis-main
make run-dev WEBSITE=precis-landing
make check WEBSITE=precis-landing
```

For Docker, use the dispatcher rather than inventing a project name:

```bash
make validate-config WEBSITE=precis-landing
make docker-build WEBSITE=precis-main
make docker-up WEBSITE=precis-main
```

These commands may touch databases, containers, logs, or static output. Read
the target recipe before running deployment-oriented targets.

## Shared configuration

- `configs/base/` contains reusable Django settings modules.
- `configs/settings/` and `configs/Env/` contain environment/site settings.
- `configs/management/` contains workers, management helpers, and CI helpers.
- `assets/` contains only assets intentionally shared across active products.

A setting belongs in shared configuration only when multiple products consume
it with the same semantics. Otherwise keep it in the product's `settings.py`.
Avoid importing one product's settings into another product.

## Product guidance

- Precis: `precis/precis-main/backend/AGENTS.md`; backend app code is under
  `precis/precis-main/backend/apps/`, with product assets beside `backend/` and the Astro
  frontend under `precis/precis-main/frontend/`.
- Precis Landing: `precis/precis-landing/AGENTS.md`; keep the Astro frontend and
  Django/Wagtail backend contracts synchronized.
- CTC Research: `precis/precis-ctc/AGENTS.md`; standalone medical research
  center site, separated from the Precis LMS runtime.
- Syntara: `syntara/AGENTS.md`; keep AI providers, template discovery, and SSE
  behavior behind the `chat/` application boundaries.
- Formints: `formints/AGENTS.md`; each edition has its own backend/frontend/
  native boundary and the professional/cloud products are not interchangeable.
- Loop-CRM: `loop-crm/README.md`; keep the CRM/marketing/attribution app
  boundaries separate, use `django_fusion.*` components (no django-cotton), and
  treat `apps/tasks/` (Dramatiq) as the sole background-worker runtime.
- `precis-lms/` was merged into `precis/precis-main` and removed; git history is
  the archive. New learning features belong in `precis-main`.

## Project-level conventions

- Keep app-specific templates, static assets, migrations, and tests in the
  owning product.
- Use `django_fusion.*` canonical imports; do not re-export framework symbols.
- Use `{% comp %}` for registered components and `fragment_name` for HTMX
  fragments.
- Prefer services/managers/domain modules over business logic in URL views.
- Preserve existing product APIs and compatibility aliases unless the user
  explicitly requests a migration.
- Run targeted checks from the nearest product README/Makefile before the
  workspace suite.
