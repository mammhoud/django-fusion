# Project Structure

The repository is organized as a shared Django/Wagtail workspace with two deployable site directories and root-level orchestration.

## Root directories

| Path | Description |
|---|---|
| `manage.py` | Root site selector. Accepts `--site`, `DJANGO_SITE`, or `SITE` and maps legacy aliases to real site directories. |
| `pyproject.toml` | Workspace dependency definition for the real members `precis-ctc` and `lms-demo`. |
| `Makefile` | Root command interface for checks, tests, assets, Docker, and per-site runtime operations. |
| `configs/` | Shared settings fragments, YAML environment files, base Django settings modules, and config tests. |
| `tasks/` | Shared Celery/runtime task entrypoints that can serve more than one website. |
| `assets/` | Shared frontend assets, templates, static files, and package scripts. |
| `webpack/` | Shared webpack configuration used by the asset pipeline. |
| `compose/` | Dockerfiles and modular Compose stacks for app, warehouse, proxies, docs, tasks, PostgreSQL, and media. |
| `scripts/` | Runtime utilities such as dumped-data loading and deployment verification. |
| `tests/` | Unit, integration, website, Docker, HTTP, Selenium, and fixture tests. |
| `docs/` | Documentation source, architecture notes, deployment flow, and reports. |
| `precis-ctc/` | CTC Research site package. |
| `lms-demo/` | Structa/LMS demo site package. |

## Site directory pattern

Both site directories follow the same high-level pattern:

```text
site-name/
├── manage.py              # Site-local Django command wrapper
├── pyproject.toml         # Site package metadata and standalone dependency hints
├── settings.py            # Site-local Django settings entrypoint
├── configs/               # Site-specific settings package
├── www/                   # ASGI/WSGI/URLs, apps, core routes, handlers
├── plugins/               # Site feature plugins and reusable app surfaces
├── templates/             # Root templates for public, auth, profile, modal, email pages
├── assets/                # Site-specific static overrides
└── docker-compose.yml     # Site-focused compose entry where present
```

## Site aliases

The root `manage.py` supports aliases for compatibility, but the real directories are `precis-ctc` and `lms-demo`.

| Alias | Real directory |
|---|---|
| `ctc`, `precis-ctc`, `ctc-research.com` | `precis-ctc` |
| `structa`, `structa.cloud`, `core`, `lms`, `lms-demo` | `lms-demo` |

## Docker structure

```text
compose/
├── docker-compose.yml             # Django application service
├── docker-compose.warehouse.yml   # PostgreSQL, Redis, Celery definitions
├── docker-compose.tasks.yml       # Shared task workers
├── docker-compose.traefik.yml     # Traefik edge proxy
├── docker-compose.nginx.yml       # Optional Nginx static/media proxy (also hosts the docs service)
├── django/                        # Application image, entrypoint, start scripts
├── postgres/                      # PostgreSQL image and maintenance scripts
├── traefik/                       # Static and dynamic Traefik config
├── nginx/                         # Nginx image/config
└── media/                         # Media proxy config and local SSL placeholders
```

## Why this structure is stable

- Site packages remain small and independently selectable.
- Root tooling performs shared orchestration without duplicating commands in every site.
- Docker builds copy actual workspace members, so dependency installation fails early if a site directory is missing.
- Deployment docs and enhancement backlog are tracked under `docs/`, allowing `.plans/` to be removed safely.
