# Development and Testing Guide

---

## Prerequisites

- Python 3.11+
- Node.js 18+
- Docker and Docker Compose
- `uv` (Python package manager)

---

## Local Development Setup

### 1. Clone and configure

```bash
git clone <repo-url>
cd <workspace>

# Set up ctc-research.com
cd ctc-research.com
cp .env.example .env
# Edit .env with your local values

# Set up structa.cloud
cd ../structa.cloud
cp .env.example .env
# Edit .env with your local values
```

### 2. Install Python dependencies

```bash
# Using uv (recommended)
uv sync

# Or per-project
cd ctc-research.com && uv sync
cd structa.cloud && uv sync
```

### 3. Install frontend dependencies

```bash
cd ctc-research.com
npm install

cd structa.cloud
npm install
```

### 4. Run migrations

```bash
cd ctc-research.com
python manage.py migrate

cd structa.cloud
python manage.py migrate
```

### 5. Create superuser

```bash
python manage.py createsuperuser
# Or use env vars: SUPERUSER_USERNAME, SUPERUSER_EMAIL, SUPERUSER_PASSWORD
```

### 6. Start development server

```bash
python manage.py runserver
```

---

## Docker Development

### Start all services

```bash
# From workspace root
docker compose up -d

# Or per-project
cd ctc-research.com && docker compose up -d
cd structa.cloud && docker compose up -d
```

### Makefile commands (workspace root)

```bash
make rebuild              # rebuild and restart all containers
make rebuild svc=website  # rebuild only ctc website
make rebuild svc=core     # rebuild only alliance core
make remove svc=website   # remove container/image then rebuild
make logs svc=core        # tail logs for a service
make validate             # validate all compose files
make test-compose         # test compose file parsing
make cleanup              # prune unused Docker resources
make prune                # deep clean (includes volumes)
make build-with-logs      # build with logs saved to docker-build-logs/
```

### Services

| Service | Project | Description |
|---------|---------|-------------|
| `website` | ctc-research.com | Main Django app |
| `website-media` | ctc-research.com | Media file server |
| `website-worker` | ctc-research.com | Celery worker |
| `core` | structa.cloud | Main Django app |
| `alliance-media` | structa.cloud | Media file server |
| `lms` | structa.cloud | LMS service |
| `traefik` | infra | Reverse proxy + SSL |
| `redis` | infra | Cache + queue broker |
| `adminer` | infra | Database admin UI |
| `docs` | infra | Documentation server |

---

## Frontend Development

```bash
# Watch mode (development)
npm run dev

# Production build
npm run build

# Webpack config location
webpack/webpack.config.js
```

---

## Testing

### Run tests

```bash
# All tests
pytest tests/

# With coverage
pytest tests/ --cov=apps --cov-report=html

# Specific app
pytest tests/ -k "test_lms"
pytest tests/ -k "test_handlers"

# Single test file
pytest tests/test_enrollment.py -v

# Stop on first failure
pytest tests/ -x
```

### Property-Based Tests (Hypothesis)

Both projects use **Hypothesis** for property-based testing.

```bash
# Run PBT tests
pytest tests/test_properties.py -v

# With more examples
pytest tests/test_properties.py --hypothesis-seed=0
```

Hypothesis stores examples in `.hypothesis/` — commit this directory to reproduce failures.

### django-seed tests

```bash
cd libs/django-seed
pytest tests/ -v

# Key test files:
# tests/test_properties.py   — PBT for orchestrator
# tests/test_integration.py  — full orchestrator workflow
# tests/test_parser.py       — spec file parsing
# tests/test_executor.py     — task execution
# tests/test_progress.py     — progress tracking
# tests/test_filter.py       — task filtering
# tests/test_compatibility.py — spec format versions
# tests/test_config.py       — configuration loading
```

### Test fixtures

`libs/django-seed/tests/conftest.py` provides:
- `temp_spec_dir` — temporary `.kiro/specs` directory
- `orchestrator` — configured `SpecTaskOrchestrator` instance
- `sample_spec` — pre-populated spec for testing

---

## Code Quality

### Linting

```bash
# Ruff (fast Python linter)
ruff check .
ruff check . --fix   # auto-fix

# Config: .ruff.toml
```

### Type checking

```bash
# Pylint
pylint apps/

# Config: .pylintrc
```

### Pre-commit (if configured)

```bash
pre-commit run --all-files
```

---

## Seeding Test Data

```bash
# Seed a model with fake data
python manage.py seed LMS --number=20
python manage.py seed handlers --number=10

# Uses django-seed's Faker-based guessers
```

---

## Debugging

### Django shell

```bash
python manage.py shell_plus   # with django-extensions
python manage.py shell
```

### Database inspection

```bash
# Adminer UI (Docker)
http://localhost:8080

# Django admin
http://localhost:8000/admin/

# Wagtail admin
http://localhost:8000/cms/
```

### Validate deployment config

```bash
# structa.cloud only
python manage.py validate_config
python manage.py verify_deployment
```

---

## CI/CD

Build logs are saved to `docker-build-logs/` when using `make build-with-logs`.

```bash
make build-with-logs           # all services
make build-with-logs svc=core  # single service
```

Log files: `docker-build-logs/<project>_<service>_<timestamp>.log`
