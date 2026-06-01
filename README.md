# structa.cloud

**structa.cloud** is a multi-site Django/Wagtail workspace for Structa web platforms. It uses a thin-layer architecture: each deployable site keeps only site-specific glue while shared behavior lives in reusable packages, plugins, root configs, shared tasks, and a common asset pipeline.

## Deployable sites

| Directory | Purpose | Useful aliases |
|---|---|---|
| `ctc-research/` | CTC Research LMS and blog platform. | `ctc`, `ctc-website`, `ctc-research`, `ctc-research.com` |
| `lms-demo/` | Structa/LMS demo platform. | `structa`, `structa.cloud`, `core`, `lms`, `lms-demo` |
| `VResume/` | Personal portfolio/CMS. | `vresume`, `resume`, `VResume`, `vresume.structa.cloud` |

## What makes this architecture unique

- **Multi-site selector**: the root `manage.py` selects a site with `--site`, `DJANGO_SITE`, or `SITE`.
- **Thin application layer**: project code delegates reusable behavior to `django-osoul`, `django-rseal`, and `django-grep`.
- **Shared operational surface**: root `Makefile`, `configs/`, `tasks/`, `scripts/`, `assets/`, and `webpack/` serve all three sites.
- **Modular Docker flow**: warehouse, application, tasks, proxies, docs, and static/media services can be started independently.
- **Verification-first deployments**: compose validation, Django checks, migrations, static collection, and runtime verification are documented as deployment gates.


## Unified workspace command guide

The workspace now has one operational surface for all three websites. Use the root `manage.py`, root `Makefile`, and the single Node package in `assets/package.json`; project-local `manage.py` files are compatibility wrappers around the root command.

| Website | Aliases | Dev port | Docker service |
|---|---|---:|---|
| `ctc-research` / `ctc-website` | `ctc`, `ctc-website`, `ctc-research.com` | `5070` | `ctc-research-website` |
| `lms-demo` | `structa`, `structa.cloud`, `lms` | `5071` | `lms-demo-website` |
| `vresume` | `resume`, `VResume`, `vresume.structa.cloud` | `5072` | `vresume-website` |

Core commands:

```bash
python manage.py --list-sites
python manage.py --site ctc check
python manage.py --site structa check
python manage.py --site vresume check

make build-assets WEBSITE=ctc
make build-assets WEBSITE=structa
make build-assets WEBSITE=vresume
make build-assets-all

npm --prefix assets run build -- --site ctc
npm --prefix assets run build -- --site structa
npm --prefix assets run build -- --site vresume
npm --prefix assets run build:assets
npm --prefix assets run build:all
npm --prefix assets run collectstatic:all
npm --prefix assets run populate:all -- --dry-run

make -C tests scripts list
make -C tests vresume
make tests-website WEBSITE=ctc
make tests-website WEBSITE=structa
make tests-website WEBSITE=vresume
pytest tests/test_yaml_site_scenarios.py
```

Docker/deployment commands create/use the shared routing networks, one root compose file, and unique per-site ports. Install/build frontend dependencies on the host or in CI before deployment; the Django image no longer runs `npm ci` during `docker build`, which avoids webpack-cli install prompts and long repeated Node dependency installs for each website image.

```bash
docker network create traefik-net || true
docker network create site_network || true
npm --prefix assets ci --include=dev --legacy-peer-deps --no-audit --no-fund
npm --prefix assets run build:all
docker compose -f docker-compose.yml config
docker compose -f docker-compose.yml up -d --build postgres redis shared-media ctc-research-website lms-demo-website vresume-website
```

Makefile deployment shortcuts wrap the same root compose file:

```bash
make docker-build WEBSITE=ctc
make docker-rebuild WEBSITE=ctc
make docker-redeploy WEBSITE=ctc
make docker-redeploy WEBSITE=structa
make docker-redeploy WEBSITE=vresume
make docker-prune-containers
make docker-prune-data
```

Shared JS/SCSS lives under `assets/static/js/base/` and `assets/static/scss/`, site entry points live under each site `assets/static/js/*-app.js`, webpack mirrors bundles into `dist/shared`, `dist/lms-demo`, `dist/ctc-research`, and `dist/vresume`, and generated media, Wagtail originals, PostgreSQL volumes/backups, staticfiles, and webpack bundles are ignored by git. Commit only source fixtures, source static assets, and code.

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
npm --prefix assets run build:assets
npm --prefix assets run build:all
```

Run a selected site locally:

```bash
python manage.py --site ctc runserver 0.0.0.0:5070
python manage.py --site structa runserver 0.0.0.0:5071
python manage.py --site vresume runserver 0.0.0.0:5072
```

## Docker quick start

Use the root `docker-compose.yml`; it includes warehouse, Traefik, websites, and the shared nginx media server from `compose/`. For a production-like rebuild/redeploy of one site:

```bash
docker network create traefik-net || true
docker network create site_network || true
npm --prefix assets ci --include=dev --legacy-peer-deps --no-audit --no-fund
npm --prefix assets run build:all
make docker-rebuild WEBSITE=ctc
make docker-redeploy WEBSITE=ctc
```

Start all websites and shared media together:

```bash
docker compose -f docker-compose.yml up -d --build postgres redis shared-media ctc-research-website lms-demo-website vresume-website
```

Or use the runner script with the canonical compose file:

```bash
SITE=ctc-research INSTALL_ASSETS=true BUILD_ASSETS=true ./run_containers.sh
SITE=all ./run_containers.sh
```

Set `PROJECT_PATH` and `DJANGO_SITE` in `.env` to `ctc-research`, `lms-demo`, or `vresume` only when running a single-site custom command; the root compose file supplies those values for the managed website services.

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
python -m py_compile tests/scripts/verify_runtime.py tests/scripts/load_dumped_data.py
docker compose -f docker-compose.yml config
```

Before routing traffic, also run site-specific Django checks, migrations, static collection, and `tests/scripts/verify_runtime.py` as described in the deployment docs.
