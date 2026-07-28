# structa.cloud

**AllianceCore LMS Platform** — A professional Learning Management System built with Django 5.x and Wagtail CMS following the thin layer architectural pattern.

structa.cloud is a thin-layer Django project that delegates all business logic to shared packages (`django_fusion`, `crafts_ai`, `django_fusion`). It provides course management, user enrollments, progress tracking, certification, and a blog/newsletter system under the `alliance` app label.

---


## Workspace commands

This project is managed from the workspace root. The local `manage.py` delegates to `../manage.py`, and frontend assets are built by the single shared package at `../assets/package.json`. Do not add project-local `package.json` or webpack config files.

```bash
# Django CLI
../.venv/bin/python ../manage.py --site structa check
./manage.py check
./manage.py runserver 0.0.0.0:5071

# Assets
make build-assets
make main-assets
make assets build
cd .. && make build-assets WEBSITE=structa
cd .. && npm --prefix assets run build -- --site structa
cd .. && npm --prefix assets run build:collect -- --site structa

# Data and tests
cd .. && npm --prefix assets run populate -- --site structa --dry-run
cd .. && make tests-website WEBSITE=structa
```

Runtime port: `5071`. Generated media/staticfiles/bundles and database files are ignored; source fixtures and source static assets remain tracked.

## Features

- **Alliance LMS**: Courses, modules, lessons, quizzes, enrollments, progress tracking
- **Certification**: Automated PDF certificate generation on course completion
- **CMS**: Wagtail-powered content management with StreamField components
- **Blog**: Integrated blog with tagging and search
- **Newsletter**: Celery-powered email delivery with AI-enhanced content
- **Auth**: Role-based access control, social auth, allauth integration
- **API**: Django Ninja REST API
- **Health Checks**: Unified health endpoints via `django_fusion`
- **i18n**: Multi-language support (English, Arabic, French, German)
- **Thin Layer Architecture**: All business logic delegated to shared packages

---

## Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+
- uv (Python package manager)

---

## Installation

### Local Development

```bash
# 1. Clone and enter the project
cd structa.cloud/

# 2. Copy environment file
cp .env.example .env
# Edit .env with your local settings

# 3. Install Python dependencies
uv sync

# 4. Install Node dependencies
npm install

# 5. Run database migrations
uv run python manage.py migrate

# 6. Create superuser
uv run python manage.py createsuperuser

# 7. Collect static files
uv run python manage.py collectstatic --noinput

# 8. Build frontend assets
npm run build
```

### Docker

```bash
# Start all services
docker compose up -d

# Run migrations
docker compose exec website python manage.py migrate

# Create superuser
docker compose exec website python manage.py createsuperuser
```

---

## Configuration

Key environment variables in `.env`:

```bash
# Django
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=structa.cloud,www.structa.cloud

# Database
DATABASE_URL=postgres://user:pass@localhost:5432/structa_cloud

# Redis
REDIS_URL=redis://localhost:6379/0

# Email
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=noreply@example.com
EMAIL_HOST_PASSWORD=your-password

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1

# Storage (production)
AWS_STORAGE_BUCKET_NAME=structa-cloud-media
AWS_S3_REGION_NAME=us-east-1
```

---

## Running Locally

### Development Server

```bash
# Django development server
uv run python manage.py runserver

# Or use Makefile
make dev
```

### Background Services

```bash
# Celery worker
uv run celery -A configs worker -l info

# Celery beat (scheduled tasks)
uv run celery -A configs beat -l info

# Frontend watcher
npm run dev
```

### Makefile Commands

The project follows the same pattern as ctc-research.com and can use the workspace root Makefile for Docker management. For development tasks, use the commands directly:

```bash
# Full setup (first time)
uv sync && npm install && python manage.py migrate && python manage.py collectstatic

# Run tests
uv run pytest tests/

# Format code
ruff format .

# Clean cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
```

---

## Running in Docker

### Development Deployment

```bash
# Start all services (website, website-media, website-worker)
docker compose up -d

# View logs
docker compose logs -f website

# Run management commands
docker compose exec website python manage.py shell

# Stop services
docker compose down
```

### Production Deployment with Traefik

```bash
# Start with Traefik for SSL and reverse proxy
cd compose/
./run_containers.sh --prod

# Or manually with Traefik
docker compose -f docker-compose.yml -f docker-compose.override.yml up -d
```

### Docker Services

- **website**: Django application server (Gunicorn) - port 5070
- **website-media**: Nginx server for static/media files - port 8271
- **website-worker**: RQ worker for background tasks - port 5075
- **postgres**: PostgreSQL database (from workspace root compose)
- **redis**: Redis cache (from workspace root compose)
- **traefik**: Reverse proxy with SSL termination (when using production setup)

### Health Checks

Docker containers include health checks:

```bash
# Test health endpoints
curl http://localhost:5070/health/
curl http://localhost:5070/health/database/
curl http://localhost:5070/health/assets/
curl http://localhost:5070/health/media/
```

---

## Project Structure

### Thin Layer Architecture

```
structa.cloud/
├── apps/                    # Thin layer apps (delegate to packages)
│   ├── accounts/            # User management (thin subclasses of django_fusion)
│   │   ├── models/          # Project-specific user/group models
│   │   ├── services/        # Thin subclasses: UserService, GroupService
│   │   └── views/           # Account views
│   ├── lms/                 # Alliance learning management (AppConfig label: alliance)
│   │   ├── models/          # Course, Lesson, Enrollment, Cart models
│   │   ├── services/        # Thin subclasses: CartService, PersonService
│   │   └── views/           # LMS views
│   ├── content/             # CMS content (Wagtail pages)
│   │   ├── models/          # HomePage, ContentPage, etc.
│   │   └── views/           # Content views
│   └── blog/                # Blog functionality
│       ├── models/          # BlogPost, Tag models
│       └── views/           # Blog views
├── alliance/                # ASGI/WSGI entry points (project root module)
├── configs/                 # Settings and URL configuration
│   └── settings/            # base.py, local.py, production.py
├── assets/                  # Static files, media, templates
├── components/              # Reusable HTML components (HTMX/Alpine)
├── email_templates/         # Email HTML templates
├── locale/                  # Translation files
└── tests/                   # Test suite
```

### Domain-Aligned Apps

The project follows domain-driven design with clear boundaries:

1. **accounts/**: User authentication, registration, profiles, permissions
2. **lms/**: Alliance learning management system (courses, lessons, enrollments) - uses `alliance` app label
3. **content/**: CMS content management (Wagtail pages, articles)
4. **blog/**: Blog posts, tags, categories, comments

### Package Dependencies

This project follows strict package boundaries:

| Package | Purpose | Import Rules |
|---------|---------|--------------|
| `django_fusion` | Pure Django foundation (models, mixins, utils, contrib) | No Wagtail/Celery imports |
| `crafts_ai` | Wagtail + automation (services, workflows, email, signals) | No project-specific imports |
| `django_fusion` | Testing infrastructure and health checks | Test-only, never in production |
| `nawaai` | AI/MCP toolkit | Pure Python, zero Django imports |

**Dependency Direction**: `stdlib` → `nawaai` → `django_fusion` → `crafts_ai` → `projects`

### Alliance App vs LMS App

structa.cloud uses `apps/lms/` as the directory but with `AppConfig(name='alliance')` as the app label. This distinguishes it from ctc-research.com's `lms` app label while sharing the same directory structure.

```python
# structa.cloud/apps/lms/apps.py
from django.apps import AppConfig

class AllianceConfig(AppConfig):
    name = "apps.lms"
    label = "alliance"  # Different from ctc-research.com's "lms" label
    verbose_name = "Alliance"
```

### Thin Layer Pattern Example

All business logic lives in shared packages. Project apps contain only:

```python
# apps/lms/services/cart.py — thin subclass
from crafts_ai.pipelines.services.cart import CartServiceBase
from apps.lms.models import Cart

class CartService(CartServiceBase):
    """
    Structa Alliance cart service.
    Delegates to crafts_ai.pipelines.services.CartServiceBase.

    Canonical import: from crafts_ai.pipelines.services import CartServiceBase
    """
    cart_model = Cart  # project-specific model injection

    # Only project-specific overrides here
    @classmethod
    def add_to_cart(cls, user, item, quantity: int, **kwargs):
        if not cls._validate_alliance_requirements(user, item):
            return (False, "Alliance requirements not met", None)
        return super().add_to_cart(user, item, quantity, **kwargs)
```

### What Stays in Projects

1. **Settings and configuration** (`configs/`)
2. **URL routing** (`urls.py` files)
3. **Project-specific models** (extend package models)
4. **Templates and static files** (`assets/`, `templates/`)
5. **Thin service subclasses** (override package defaults)
6. **Project-specific views** (use package services)

### What Goes to Packages

1. **Business logic** (all services, managers, utilities)
2. **Reusable models** (foundation models in `django_fusion`)
3. **Wagtail components** (blocks, snippets, hooks in `crafts_ai`)
4. **Testing infrastructure** (all in `django_fusion`)
5. **Health check system** (unified in `django_fusion`)

---

## Testing

### Test Infrastructure

Tests use `django_fusion` for unified infrastructure:

```python
from django_fusion.tests.base import BaseTestCase
from hypothesis import given

class CartServiceTest(BaseTestCase):
    @given(quantity=BaseTestCase.st_uuid())
    def test_cart_add(self, quantity):
        # Test logic here
        ...
```

### Running Tests

```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=apps --cov-report=html

# Run property-based tests only
uv run pytest tests/ -k "property" -v

# Run Selenium tests (requires running server)
uv run pytest tests/selenium/ -v

# Or use Makefile
make test
make test-coverage
```

### Test Organization

- **Package Tests**: In `venv/libs/<package>/tests/` (test package functionality)
- **Project Tests**: In `structa.cloud/tests/` (test thin layer integration)
- **Integration Tests**: In `tests/integration/` (test cross-package integration)
- **Selenium Tests**: In `tests/selenium/` (browser interactions)

### Property-Based Testing

The project uses Hypothesis for property-based testing:

```python
from hypothesis import given, strategies as st
from django_fusion.tests.base import BaseTestCase

class TestParsers(BaseTestCase):
    @given(st.text(min_size=1, max_size=100))
    def test_parser_roundtrip(self, text):
        # Parse → print → parse should be equivalent
        parsed = parse_text(text)
        printed = print_text(parsed)
        reparsed = parse_text(printed)
        self.assertEqual(parsed, reparsed)
```

---

## Health Checks

### Endpoints

```bash
# Basic health
curl http://localhost:8000/health/

# Database health
curl http://localhost:8000/health/database/

# Static files health
curl http://localhost:8000/health/assets/

# Media files health
curl http://localhost:8000/health/media/
```

### Docker Health Checks

Containers include built-in health checks that monitor:
- Application responsiveness
- Database connectivity
- Static/media file accessibility
- Background worker status

---

## Deployment

### Production Checklist

1. Set `DEBUG=False` in `.env`
2. Set `ALLOWED_HOSTS` to your domain
3. Configure PostgreSQL and Redis
4. Configure S3 for media storage
5. Run `python manage.py collectstatic`
6. Run `python manage.py migrate`
7. Configure Nginx as reverse proxy
8. Set up SSL certificate (Let's Encrypt)
9. Configure Celery worker and beat services

### Docker Production

```bash
# Build production image
docker compose -f docker-compose.yml -f docker-compose.override.yml up -d

# Run migrations
docker compose exec website python manage.py migrate --noinput

# Collect static files
docker compose exec website python manage.py collectstatic --noinput
```

### Environment Configuration

The project supports multiple environments:

```bash
# Local development
DJANGO_SETTINGS_MODULE=configs.settings.local

# Docker development
DJANGO_SETTINGS_MODULE=configs.settings.docker

# Production
DJANGO_SETTINGS_MODULE=configs.settings.production
```

### Monitoring

- **Health checks**: Built-in endpoints for monitoring
- **Sentry**: Error tracking and performance monitoring
- **Prometheus**: Metrics collection
- **Django Silk**: Profiling and performance analysis

---

## Development Workflow

### Code Organization

1. **New feature in package?** → Add to `django_fusion` (pure Django) or `crafts_ai` (Wagtail/automation)
2. **New feature in project?** → Create thin subclass in appropriate app
3. **New test?** → Use `django_fusion` infrastructure
4. **New template?** → Add to project's `templates/` directory

### Import Rules

```python
# ✅ Allowed
from django_fusion.managers import RoleHierarchyManager
from crafts_ai.pipelines.services import CartServiceBase
from django_fusion.tests.base import BaseTestCase

# ❌ Forbidden
# django_fusion importing wagtail
# crafts_ai importing project-specific code
# nawaai importing Django modules
# Production code importing django_fusion
```

### Boundary Enforcement

Boundary rules are enforced by import-linter in CI:

```bash
# Check boundary violations
import-linter --config .importlinter

# Run in CI to fail on violations
```

---

## Frontend Build System

### Technology Stack

- **Webpack**: Module bundling
- **Tailwind CSS 4**: Utility-first CSS framework
- **Alpine.js**: Minimal JavaScript framework
- **HTMX**: HTML extensions for AJAX
- **Vue.js**: Component framework (optional)

### Build Commands

```bash
# Development build with watcher
npm run dev

# Production build with PurgeCSS
npm run build

# Analyze bundle size
npm run analyze

# Clean build artifacts
npm run clean
```

### CSS Strategy

- **Tailwind CSS**: Utility classes for rapid development
- **PurgeCSS**: Removes unused CSS in production
- **RTL support**: Automatic RTL CSS generation
- **Theme switching**: Dark/light mode support

---

## Database Management

### Migrations

```bash
# Create migrations
uv run python manage.py makemigrations

# Apply migrations
uv run python manage.py migrate

# Check migration status
uv run python manage.py showmigrations

# Rollback migrations
uv run python manage.py migrate app_name zero
```

### Data Management

```bash
# Create superuser
uv run python manage.py createsuperuser

# Load fixtures
uv run python manage.py loaddata fixture_name

# Dump data
uv run python manage.py dumpdata --indent 2 > data.json

# Reset database (DANGER)
make reset-db
```

### Backup and Recovery

```bash
# Database backup
uv run python manage.py backup_db

# Media backup
uv run python manage.py backup_media

# Restore from backup
uv run python manage.py load_fixtures backup_file.json
```

---

## Package Management

### Python Dependencies

Managed with `uv` for fast, reliable dependency resolution:

```bash
# Install dependencies
uv sync

# Add new dependency
uv add package_name

# Update dependencies
uv sync --upgrade

# Check for updates
uv outdated
```

### Frontend Dependencies

Managed with `npm`:

```bash
# Install dependencies
npm install

# Add new dependency
npm install package_name --save

# Update dependencies
npm update

# Check for updates
npm outdated
```

---

## CI/CD Pipeline

### GitHub Actions

The project includes CI/CD workflows for:

1. **Boundary validation**: Enforces import rules
2. **Test execution**: Runs all tests across packages and projects
3. **Code quality**: Linting and formatting checks
4. **Security scanning**: Dependency vulnerability checks
5. **Docker builds**: Container image creation

### Deployment Pipeline

```bash
# Development workflow
make test → make format → make lint → git push

# Production deployment
make deploy  # Runs full sync and verification
```

### Rollback Strategy

```bash
# Rollback last deployment
make rollback

# Create recovery point
git tag recovery-$(date +%Y%m%d-%H%M%S)

# Restore from backup
make restore-backup
```

---

## Troubleshooting

### Common Issues

1. **Import errors**: Check boundary rules and package dependencies
2. **Database connection**: Verify `.env` settings and PostgreSQL service
3. **Static files**: Run `make static` to collect static files
4. **Frontend build**: Check Node.js version and run `npm install`
5. **Docker issues**: Use `docker compose logs` to view container logs

### Debug Tools

```bash
# Django debug toolbar
# Available at /__debug__/ when DEBUG=True

# Django Silk profiler
# Available at /silk/ when installed

# Sentry error tracking
# Automatic error reporting in production

# Health check endpoints
# Monitor system status at /health/
```

### Performance Optimization

1. **Caching**: Redis cache for frequent queries
2. **Database indexing**: Ensure proper indexes on frequently queried fields
3. **Static files**: CDN delivery for production
4. **Query optimization**: Use Django's `select_related` and `prefetch_related`
5. **Background processing**: Use RQ workers for long-running tasks

---

## Contributing

### Development Setup

1. Fork the repository
2. Set up development environment: `make setup`
3. Create feature branch: `git checkout -b feature/description`
4. Make changes following thin layer pattern
5. Run tests: `make test`
6. Submit pull request

### Code Standards

- **Python**: Follow PEP 8, use ruff for formatting
- **JavaScript**: Follow Airbnb style guide
- **Templates**: Use Django template language best practices
- **Documentation**: Update README and docstrings
- **Tests**: Write tests for new functionality

### Pull Request Checklist

- [ ] Tests pass
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] No boundary violations
- [ ] No duplication with existing code
- [ ] Migration files included if needed

---

## Changelog

See [CHANGELOG.md](./CHANGELOG.md) for version history.

---

## License

MIT License - see [LICENSE](./LICENSE) file for details.

---

## Support

- **Documentation**: [docs.structa.cloud](https://docs.structa.cloud)
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions

---

## Architecture References

- **Thin Layer Pattern**: [ARCHITECTURE.md](../ARCHITECTURE.md)
- **Migration Guide**: [MIGRATION_GUIDE.md](../MIGRATION_GUIDE.md)
- **Package Documentation**: See individual package README files
- **Specifications**: [.kiro/specs/](../.kiro/specs/)

---

## Differences from ctc-research.com

| Feature | ctc-research.com | structa.cloud |
|---------|-----------------|---------------|
| LMS app label | `lms` | `alliance` |
| Project module | `projects/` | `alliance/` |
| Docker setup | Standard compose | Traefik + SSL |
| Domain | ctc-research.com | structa.cloud |

Both projects share identical app structure (`accounts/`, `content/`, `blog/`, `lms/`) and use the same thin layer pattern delegating to `django_fusion` and `crafts_ai`.

