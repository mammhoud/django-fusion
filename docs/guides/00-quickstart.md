# First-Time Setup

This guide covers a fresh checkout of the Structa Cloud monorepo.

## Prerequisites

- Python 3.11+
- Docker + Docker Compose
- `uv` for Python dependency management
- `make`
- Git with submodule support

## 1. Clone and initialize submodules

```bash
git clone <repo-url> structa.cloud
cd structa.cloud
git submodule update --init --recursive
```

The local libraries in `libs/` are Git submodules and must be initialized before the sites can boot.

## 2. Install local packages

```bash
uv pip install -e libs/django-fusion/
uv pip install -e libs/ceptor-ai/
```

## 3. Environment files

Copy the example env files:

```bash
cp .env.example .env
cp .env.local.example .env.local
# Optional: cp applications/proxy/.env.example applications/proxy/.env
```

Edit `.env` and set at minimum:

```
POSTGRES_USER=admin
POSTGRES_PASSWORD=postgres
DB_NAME_CTC=db_ctc
DB_NAME_LMS=db_structa
DB_NAME_VRESUME=vresume
```

## 4. Start infrastructure

```bash
make deploy-databases
make deploy-proxy
```

## 5. Build and start a site

```bash
make ctc-research
# Inside the ctc-research Makefile context:
make docker-up
```

Or directly:

```bash
cd projects
make docker-up WEBSITE=ctc-research
```

## 6. Run checks

```bash
cd projects
make check WEBSITE=ctc-research
```

## Common issues

- **Missing submodules**: `django-fusion` or `ceptor-ai` import errors almost always mean submodules were not initialized.
- **DB_NAME not set**: shared-worker and shared-scheduler require `DB_NAME` to be explicit; see `applications/compose/docker-compose.tasks.yml`.
- **Site directory not found**: ensure `WEBSITE` matches a canonical site name in `projects/cli.py`.

## Troubleshooting

### Wrong Python version

```bash
python --version  # expect 3.11+
```

### Database connection fails

```bash
docker ps | grep postgres
docker logs postgres | tail -50
docker exec postgres psql -U structa_user -d ctc_research_db -c "SELECT 1"
```

### Static files not loading

```bash
docker ps | grep shared-media
docker logs shared-media
docker exec ctc-research-website python manage.py collectstatic --noinput
```

### Import errors

```bash
# Verify django-fusion is installed
docker exec ctc-research-website python -c "import django_fusion; print('OK')"

# Reinstall local packages
uv pip install -e libs/django-fusion/
uv pip install -e libs/ceptor-ai/
```
