# structa.cloud Workspace Documentation

Welcome to the documentation for the **structa.cloud multi-site Django/Wagtail workspace**. The repository currently contains two deployable site directories, shared runtime tooling, a shared frontend pipeline, reusable tasks, and Docker Compose stacks.

## Current deployable sites

| Site directory | Purpose | Common aliases |
|---|---|---|
| `ctc-research/` | CTC Research LMS and blog platform. | `ctc`, `ctc-research`, `ctc-research.com` |
| `lms-demo/` | Structa/LMS demo platform. | `structa`, `structa.cloud`, `core`, `lms`, `lms-demo` |

The root `manage.py` selects a site by using `--site`, `DJANGO_SITE`, or `SITE` and then places that site directory plus the repository root on `PYTHONPATH`.

## Quick links

| Topic | Link |
|---|---|
| Unique architecture | [Architecture: Unique Architecture](architecture/unique_architecture.md) |
| Project structure | [Architecture: Project Structure](architecture/project_structure.md) |
| Configuration | [Architecture: Configuration](architecture/configuration.md) |
| Request flow | [Architecture: Request Flow](architecture/request_flow.md) |
| Docker deployment flow | [Docker Deployment Flow](deployment_flow.md) |
| Deployment guide | [Deployment](deployment.md) |
| Development workflow | [Development](development.md) |
| Testing guide | [Development: Testing Guide](development/testing_guide.md) |
| Enhancement backlog | [Reports: Enhancement Backlog](reports/enhancement_backlog.md) |

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11+, Django, Wagtail, ASGI |
| Runtime | Gunicorn with Uvicorn workers, optional direct Uvicorn |
| Frontend | Shared webpack pipeline, site-specific assets, HTMX patterns |
| Database | PostgreSQL in Docker, SQLite/local options where configured |
| Cache and queues | Redis, Celery/RQ-compatible task entrypoints |
| Configuration | Environment variables, YAML settings, Dynaconf/Pydantic patterns |
| Infrastructure | Docker Compose, Traefik, optional Nginx/Caddy/docs services |
| Shared libraries | `django-osoul`, `django-rseal`, `django-grep` |

## Minimal local commands

```bash
uv sync
python manage.py --site ctc-research check
python manage.py --site lms-demo check
npm --prefix assets run build
```

## Minimal Docker commands

```bash
docker network create traefik-net || true
docker compose -f compose/docker-compose.warehouse.yml up -d vresume-postgres vresume-redis
docker compose -f compose/docker-compose.warehouse.yml -f compose/docker-compose.yml up -d --build vresume-website
```

See [Docker Deployment Flow](deployment_flow.md) for the complete stable deployment sequence.
