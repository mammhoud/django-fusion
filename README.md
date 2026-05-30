# structa.cloud

**structa.cloud** is a multi-site Django/Wagtail workspace for Structa web platforms. It uses a thin-layer architecture: each deployable site keeps only site-specific glue while shared behavior lives in reusable packages, plugins, root configs, shared tasks, and a common asset pipeline.

## Deployable sites

| Directory | Purpose | Useful aliases |
|---|---|---|
| `ctc-research/` | CTC Research LMS and blog platform. | `ctc`, `ctc-research`, `ctc-research.com` |
| `lms-demo/` | Structa/LMS demo platform. | `structa`, `structa.cloud`, `core`, `lms`, `lms-demo` |

## What makes this architecture unique

- **Multi-site selector**: the root `manage.py` selects a site with `--site`, `DJANGO_SITE`, or `SITE`.
- **Thin application layer**: project code delegates reusable behavior to `django-osoul`, `django-rseal`, and `django-grep`.
- **Shared operational surface**: root `Makefile`, `configs/`, `tasks/`, `scripts/`, `assets/`, and `webpack/` serve both sites.
- **Modular Docker flow**: warehouse, application, tasks, proxies, docs, and static/media services can be started independently.
- **Verification-first deployments**: compose validation, Django checks, migrations, static collection, and runtime verification are documented as deployment gates.

## Prerequisites

- Python 3.11+
- Node.js and npm for frontend assets
- Docker and Docker Compose for container deployments
- PostgreSQL and Redis for production-like runtime
- `uv` for Python dependency management

## Local setup

```bash
uv sync
npm --prefix assets install
python manage.py --site ctc-research check
python manage.py --site lms-demo check
npm --prefix assets run build
```

Run a selected site locally:

```bash
python manage.py --site lms-demo runserver 0.0.0.0:8000
```

## Docker quick start

```bash
docker network create traefik-net || true
docker compose -f compose/docker-compose.warehouse.yml up -d vresume-postgres vresume-redis
docker compose -f compose/docker-compose.warehouse.yml -f compose/docker-compose.yml up -d --build vresume-website
```

Set `PROJECT_PATH` and `DJANGO_SITE` in `.env` to either `lms-demo` or `ctc-research` before production deployment.

## Important docs

- [Documentation index](docs/index.md)
- [Unique architecture](docs/architecture/unique_architecture.md)
- [Project structure](docs/architecture/project_structure.md)
- [Docker deployment flow](docs/deployment_flow.md)
- [Deployment guide](docs/deployment.md)
- [Enhancement backlog](docs/reports/enhancement_backlog.md)

## Stability checks

```bash
python -m py_compile manage.py
python -m py_compile scripts/verify_runtime.py scripts/load_dumped_data.py
docker compose -f compose/docker-compose.warehouse.yml -f compose/docker-compose.yml config
```

Before routing traffic, also run site-specific Django checks, migrations, static collection, and `scripts/verify_runtime.py` as described in the deployment docs.
