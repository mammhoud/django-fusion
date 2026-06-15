# Local Development Setup

## Overview

This guide covers setting up your local development environment for the Xellent Website platform.

## Prerequisites

- Completed [Installation Guide](01-installation-guide.md)
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (optional but recommended)

## Development Environment Setup

### Option 1: Docker-Based Development (Recommended)

#### Step 1: Start Services

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

#### Step 2: Access Services

- **Frontend**: http://site.structa.cloud:8000
- **API**: http://core.structa.cloud:8000/api
- **Admin**: http://site.structa.cloud:8000/admin
- **Documentation**: http://site-docs.structa.cloud:3000

#### Step 3: Run Commands in Container

```bash
# Run Django management commands
docker-compose exec web python manage.py shell

# Run tests
docker-compose exec web pytest

# Run migrations
docker-compose exec web python manage.py migrate
```

### Option 2: Local Development Environment

#### Step 1: Activate Virtual Environment

```bash
# macOS/Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

#### Step 2: Start Development Server

```bash
# Using make command
make dev

# Or directly with Django
python manage.py runserver 0.0.0.0:8000
```

#### Step 3: Start Frontend Build Watcher

In a separate terminal:

```bash
# Using make command
make frontend-watch

# Or directly with npm
npm run watch
```

#### Step 4: Access Application

- **Frontend**: http://localhost:8000
- **Admin**: http://localhost:8000/admin

## Development Tools

### Django Management Commands

```bash
# Create superuser
python manage.py createsuperuser

# Run migrations
python manage.py migrate

# Create migrations
python manage.py makemigrations

# Open Django shell
python manage.py shell

# Run tests
python manage.py test

# Collect static files
python manage.py collectstatic
```

### Make Commands

```bash
# View all available commands
make help

# Start development server
make dev

# Run tests
make test

# Format code
make format

# Run linting
make lint

# Build frontend
make frontend-build

# Watch frontend changes
make frontend-watch
```

### Database Management

```bash
# Create database backup
docker-compose exec db pg_dump -U postgres xellent > backup.sql

# Restore from backup
docker-compose exec -T db psql -U postgres xellent < backup.sql

# Open database shell
docker-compose exec db psql -U postgres -d xellent

# Reset database
make reset-db
```

## Code Quality Tools

### Formatting

```bash
# Format code with Black
make format

# Or directly
black .
```

### Linting

```bash
# Run linting
make lint

# Or directly
flake8 .
```

### Type Checking

```bash
# Run mypy
mypy .
```

### Import Sorting

```bash
# Sort imports
isort .
```

## Testing

### Run All Tests

```bash
# Using make
make test

# Using pytest directly
pytest

# With coverage
pytest --cov
```

### Run Specific Tests

```bash
# Run tests in a specific file
pytest tests/test_models.py

# Run tests matching a pattern
pytest -k "test_user"

# Run with verbose output
pytest -v
```

### Test Coverage

```bash
# Generate coverage report
pytest --cov --cov-report=html

# View coverage report
open htmlcov/index.html
```

## Debugging

### Django Shell

```bash
# Open Django shell
python manage.py shell

# Or with IPython
python manage.py shell_plus
```

### Debug Toolbar

The Django Debug Toolbar is enabled in development. Access it at the bottom right of any page.

### Logging

```python
# In your code
import logging
logger = logging.getLogger(__name__)
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

### Breakpoints

```python
# Using pdb
import pdb; pdb.set_trace()

# Using ipdb (better)
import ipdb; ipdb.set_trace()
```

## Environment Variables

### Development Environment

Create a `.env` file in the project root:

```env
# Django
DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1,site.structa.cloud

# Database
DATABASE_URL=postgresql://xellent_user:password@localhost:5432/xellent

# Redis
REDIS_URL=redis://localhost:6379/0

# Email (Console backend for development)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Logging
LOG_LEVEL=DEBUG
```

## Hot Reload

### Frontend Hot Reload

```bash
# Watch for CSS/JS changes
make frontend-watch

# Or directly
npm run watch
```

### Django Auto-Reload

Django development server automatically reloads when Python files change.

## Performance Monitoring

### Django Debug Toolbar

The Debug Toolbar shows:
- SQL queries and execution time
- Template rendering time
- Cache hits/misses
- HTTP headers
- Settings

### Profiling

```bash
# Profile a management command
python -m cProfile -s cumulative manage.py migrate

# Profile with line_profiler
kernprof -l -v manage.py migrate
```

## Common Development Tasks

### Create a New App

```bash
python manage.py startapp myapp
```

### Create a New Model

```bash
# Create model in models.py
# Then create migration
python manage.py makemigrations

# Apply migration
python manage.py migrate
```

### Create a New View

```bash
# Add view to views.py
# Add URL pattern to urls.py
# Create template in templates/
```

### Create a New API Endpoint

```bash
# Create serializer in serializers.py
# Create viewset in views.py
# Register in urls.py
```

## Troubleshooting

### Port Already in Use

```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Database Connection Issues

```bash
# Check if database is running
docker-compose ps

# Restart database
docker-compose restart db

# Check logs
docker-compose logs db
```

### Module Import Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Clear Python cache
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name "*.pyc" -delete
```

## Next Steps

- [Project Structure Overview](03-project-structure-overview.md)
- [Development Workflow](../development/01-development-workflow.md)
- [Testing Strategy](../development/02-testing-strategy.md)

## Related Documentation

- [Installation Guide](01-installation-guide.md)
- [Environment Configuration](../deployment/02-environment-configuration.md)
- [Debugging Guide](../troubleshooting/02-debugging-guide.md)
