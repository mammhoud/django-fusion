# Design: django-grep Selenium Testing + Docker Build + Workspace Unification

## Architecture Overview

```
workspace/
├── .venv/                          ← unified venv (uv workspace root)
├── pyproject.toml                  ← workspace root, updated members + venv path
├── libs/
│   └── django-grep/
│       ├── src/django_grep/
│       │   └── tests/
│       │       ├── selenium_base.py   ← enhanced SeleniumTestCase
│       │       └── pytest_plugin.py   ← selenium fixtures added
│       ├── tests/
│       │   └── selenium/              ← NEW: site-agnostic selenium tests
│       │       ├── conftest.py
│       │       └── test_site_health.py
│       ├── .env.example               ← NEW
│       └── src/django_grep/
│           └── management/commands/
│               ├── backup_db.py       ← NEW
│               └── backup_media.py    ← NEW
├── ctc-research.com/
│   ├── tests/
│   │   └── selenium/                  ← NEW: ctc-research selenium tests
│   │       ├── conftest.py
│   │       ├── test_homepage.py
│   │       ├── test_auth.py
│   │       └── test_admin.py
│   ├── docker-compose.yml             ← updated: depends_on postgres/redis
│   └── docker-compose.override.yml   ← unchanged
└── structa.cloud/
    └── apps/                          ← merged: apps/apps/ content moved here
        ├── blog/
        ├── handlers/
        ├── LMS/
        ├── pages/
        └── templates/
```

## Component Design

### 1. Unified venv

Root `pyproject.toml` gains `[tool.uv]` with `venv = ".venv"`. All `uv sync` calls at root install into `.venv/`. Sub-packages reference workspace deps via `{ workspace = true }`.

The `start` script in ctc-research uses `/app/.venv/bin/python` — this is correct for the container where uv installs into `/app/.venv`. No change needed there; the Dockerfile already runs `uv sync --frozen` at `/` which creates the venv.

### 2. structa.cloud apps Deduplication

`structa.cloud/apps/apps/` is a ghost duplicate. The real content lives there; `structa.cloud/apps/` has only `__init__.py`, `urls.py`, `readme.md`. Strategy:
- Move all subdirs from `apps/apps/` up to `apps/`
- Update `apps/urls.py` (already correct — references `apps.handlers.*`)
- Remove `apps/apps/` directory
- Update `INSTALLED_APPS` in structa.cloud settings if it references `apps.apps.*`

### 3. django-grep Selenium Infrastructure

`SeleniumTestCase` in `selenium_base.py` is already implemented. Enhancements:
- Add `pytest` fixtures for selenium driver in `pytest_plugin.py`
- Add `conftest.py` in `tests/selenium/` with `base_url` fixture from env
- Add `test_site_health.py` with generic page-load and asset-check tests

### 4. ctc-research Selenium Tests

Three test files under `ctc-research.com/tests/selenium/`:
- `conftest.py` — driver setup, `base_url = os.getenv("SELENIUM_BASE_URL", "http://localhost:8270")`
- `test_homepage.py` — GET `/`, assert 200, title present
- `test_auth.py` — GET `/accounts/login/`, form present
- `test_admin.py` — GET `/admin/`, redirect or login form

Tests use `requests` for HTTP-level checks (no browser needed for basic smoke) and `SeleniumTestCase` for browser tests, marked `@pytest.mark.selenium`.

### 5. Import Fixes

Key issues to check and fix:
- `django_grep.pipelines.urls` — must exist (shim if not)
- `django_grep.scripts.superuser` — must exist
- `start` script python path consistency

### 6. Docker Compose Updates

`ctc-research.com/docker-compose.yml` needs:
```yaml
website:
  depends_on:
    postgres:
      condition: service_healthy
    redis:
      condition: service_started
```

But postgres and redis are defined in the root `docker-compose.yml`. The ctc-research compose must reference them as external or the root compose must be used together.

Current setup: root `docker-compose.yml` has postgres/redis. ctc-research compose uses `traefik-net` (external). For local dev with override, postgres/redis come from root compose.

Solution: Add `postgres` and `redis` as external service references in ctc-research compose with `depends_on` using service names, and document that root compose must be up first.

### 7. Data Loading

Entrypoint already runs `migrate`. Add a `loaddata` step gated by `LOAD_FIXTURES=true` env var:
```bash
if [ "${LOAD_FIXTURES:-false}" = "true" ]; then
    uv run python com loaddata wagtail_pages_dump.json ctc-research-data.json
fi
```

### 8. Backup Commands

`backup_db` management command:
```python
# Uses pg_dump or Django dumpdata depending on DB engine
# Output: BACKUP_DIR/db_YYYYMMDD_HHMMSS.json (or .sql.gz)
```

`backup_media` management command:
```python
# tar.gz of MEDIA_ROOT to BACKUP_DIR/media_YYYYMMDD_HHMMSS.tar.gz
```

## Correctness Properties

**P1**: After `uv sync --frozen` at workspace root, `python -c "import django_grep"` succeeds.

**P2**: After structa.cloud deduplication, `python -c "from apps.handlers import urls"` succeeds and `apps/apps/` does not exist.

**P3**: `pytest ctc-research.com/tests/selenium/ --collect-only` exits 0 (no import errors).

**P4**: `docker compose up website` starts and `/health/` returns HTTP 200.

**P5**: `backup_db` command creates a file in `BACKUP_DIR` with a timestamp in the filename.
