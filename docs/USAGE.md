# Monorepo Usage Guide

## Overview

This document describes how to use the enhanced monorepo structure, including the new CLI commands, language support, and deployment options.

---

## CLI Commands

### Utility Commands

All utility commands are accessed via `manage.py`:

```bash
cd /data/coolify/applications
python3 manage.py <command> [options]
```

#### `--list-sites`

List all configured sites:

```bash
python3 manage.py --list-sites
```

#### `sites`

Display site information:

```bash
python3 manage.py sites
```

Output:
```
ctc-research   path=ctc-research    service=ctc-research-website    port=5070    aliases=ctc, ctc-research.com, ctc-website
lms-demo       path=lms-demo        service=lms-demo-website        port=5071    aliases=structa, structa.cloud, core, lms
vresume        path=VResume         service=vresume-website         port=5072    aliases=resume, vresume.structa.cloud, VResume
```

#### `make`

Run make targets for a specific site:

```bash
# Default site (ctc-research)
python3 manage.py make help

# Specific site
python3 manage.py --site=lms-demo make build
```

#### `make-check`

Validate make commands without executing:

```bash
# Validate safe targets for current site
python3 manage.py make-check

# Validate all targets including destructive ones
python3 manage.py make-check --all

# Validate for specific site
python3 manage.py --site=vresume make-check
```

#### `validate-commands`

Validate all make commands across sites with detailed output:

```bash
# Validate all sites
python3 manage.py validate-commands --all

# Validate specific site
python3 manage.py validate-commands --site=ctc-research

# Validate with verbose output
python3 manage.py validate-commands --all --verbose
```

#### `local-check`

Run Django system check locally:

```bash
python3 manage.py local-check
```

#### `container-check`

Run Django system check inside the container:

```bash
python3 manage.py container-check
```

#### `check-sites`

Run Django system check on one or more sites:

```bash
# Check all sites
python3 manage.py check-sites

# Check specific sites
python3 manage.py check-sites ctc-research lms-demo
```

#### `deploy`

Build and deploy a site:

```bash
# Deploy current site
python3 manage.py deploy

# Deploy with specific options
python3 manage.py --site=ctc-research deploy --no-cache --skip-container-check

# Options:
# --no-cache            Skip build cache
# --skip-local-check    Skip local check before build
# --skip-container-check Skip container check before deploy
```

#### `logs`

Show container logs:

```bash
# Show last 100 lines for current site
python3 manage.py logs

# Show more lines
python3 manage.py logs --tail=500

# Show logs for specific service
python3 manage.py logs --service=ctc-research-website
```

#### `down`

Stop and remove containers:

```bash
# Stop current site
python3 manage.py down

# Stop all sites
python3 manage.py down --all
```

#### `ps`

Show status of website containers:

```bash
python3 manage.py ps
```

#### `build-assets`

Build static assets:

```bash
# Production build (default)
python3 manage.py build-assets

# Development build
python3 manage.py build-assets --development

# Clean build
python3 manage.py build-assets --clean
```

#### `test`

Run tests against running containers:

```bash
# Standard tests
python3 manage.py test

# Tests with live domains
python3 manage.py test --live
```

#### `push`

Commit and push library changes:

```bash
# Push all libraries
python3 manage.py push

# Push specific library
python3 manage.py push --lib=django-osoul

# With custom commit message
python3 manage.py push --message="Fix issue #123"

# Push to specific branch
python3 manage.py push --branch=main
```

---

## Django Management Commands

Django management commands are accessed directly:

```bash
# Standard Django commands
python3 manage.py migrate
python3 manage.py createsuperuser
python3 manage.py shell
python3 manage.py test

# With site selection
python3 manage.py --site=lms-demo migrate
```

---

## Language Support

The monorepo now includes enhanced language switching via django-osoul.

### Enabling Language Support

In your site's `settings.py`:

```python
from configs.settings import *

# Add language support
INSTALLED_APPS += [
    'django_osoul',
]

# Configure languages
WAGTAIL_CONTENT_LANGUAGES = (
    ('en', 'English'),
    ('ar', 'Arabic'),
    ('fr', 'French'),
    ('de', 'German'),
)

# Language code
LANGUAGE_CODE = 'en-us'

# Enable language switcher in templates
{% load language_tags %}
```

### Using the Language Switcher

In templates:

```django
{% load language_tags %}

<!DOCTYPE html>
<html lang="{% get_current_language as lang %}{{ lang }}{% endget_current_language %}">
<head>
    <meta charset="UTF-8">
    <title>{% block title %}{{ site_name }}{% endblock %}</title>
</head>
<body>
    <header>
        <nav>
            {% get_language_options as language_options %}
            {% for option in language_options %}
                <a href="{{ option.url }}"
                   lang="{{ option.code }}"
                   {% if option.is_current %}class="active"{% endif %}>
                    {{ option.name }}
                </a>
            {% endfor %}
        </nav>
    </header>

    <main>
        {% block content %}{% endblock %}
    </main>
</body>
</html>
```

### Available Template Tags

- `{% get_current_language %}` - Get the current language code
- `{% get_language_options %}` - Get all language options with URLs
- `{% get_language_info %}` - Get language info (name, flag, etc.)

---

## Docker Compose

### Starting Services

```bash
# Start all services
cd /data/coolify/applications
docker compose up -d

# Start specific service
docker compose up -d ctc-research-website

# Start with rebuild
docker compose up -d --build
```

### Stopping Services

```bash
# Stop all services
docker compose down

# Stop specific service
docker compose down ctc-research-website

# Stop and remove volumes
docker compose down -v
```

### Viewing Logs

```bash
# View all logs
docker compose logs -f

# View specific service logs
docker compose logs -f ctc-research-website

# View with timestamps
docker compose logs -f --timestamps
```

### Running Migrations

```bash
# Run migrations for all services
docker compose exec ctc-research-website python manage.py migrate
docker compose exec lms-demo-website python manage.py migrate
docker compose exec vresume-website python manage.py migrate
```

---

## Library Management

### Adding New Libraries

1. Clone the library from GitHub:

```bash
cd /data/coolify/applications/libs
git clone https://github.com/owner/library.git
```

2. Add to `pyproject.toml`:

```toml
[tool.uv.sources]
library = { git = "https://github.com/owner/library.git", branch = "main" }
```

3. Install dependencies:

```bash
cd /data/coolify/applications
uv sync
```

### Pushing Library Changes

```bash
# Push local changes to GitHub
python3 manage.py push --lib=library-name --message="Update to version 1.2.3"
```

---

## Validation Commands

### Validating Make Commands

```bash
# Check if all make commands are valid
python3 manage.py make-check --all

# Validate for specific site
python3 manage.py --site=ctc-research make-check
```

### Validating Commands Across Sites

```bash
# Comprehensive validation
python3 manage.py validate-commands --all --verbose

# Validate specific sites
python3 manage.py validate-commands --site=ctc-research,lms-demo
```

---

## Configuration

### Environment Variables

```bash
# Site selection
DJANGO_SITE=ctc-research
WEBSITE=ctc-research
SITE=ctc-research

# Database
DB_NAME=db_ctc
DB_HOST=postgres

# Redis
REDIS_URL=redis://redis:6379/0

# Language
LANGUAGE_CODE=en-us

# Path to site directory
DJANGO_WEBSITE_DIR=/data/coolify/applications/ctc-research
```

### Site Aliases

| Alias | Resolves To |
|-------|-------------|
| ctc | ctc-research |
| ctc-research.com | ctc-research |
| structa | lms-demo |
| structa.cloud | lms-demo |
| core | lms-demo |
| lms | lms-demo |
| lms-demo.com | lms-demo |
| resume | vresume |
| vresume.structa.cloud | vresume |

---

## Troubleshooting

### Import Errors

If you see `ModuleNotFoundError: No module named 'site_cli'`:

```bash
# Ensure __init__.py exists
ls -la /data/coolify/applications/__init__.py

# Verify import works
python3 -c "from cli import SiteCLI; print('OK')"
```

### Django Not Found

```bash
# Ensure you're using the correct Python environment
which python3

# Or use virtual environment
cd /data/coolify/applications
source .venv/bin/activate
python manage.py ...
```

### Site Resolution Failed

```bash
# List available sites
python3 manage.py sites

# Check alias
python3 -c "
from cli import SiteCLI
print(SiteCLI.resolve_site('ctc'))
"
```

---

## Pull Requests

Each phase is implemented as a separate pull request:

| Phase | PR Number | Description |
|-------|-----------|-------------|
| 1 | #1 | Import Resolution & Package Initialization |
| 2 | #2 | CLI/Make Command Enhancement |
| 3 | #3 | Utilities Migration |
| 4 | #4 | Docker Compose Structure |
| 5 | #5 | Documentation Enhancement |
| 6 | #6 | Language Support Enhancement |
| 7 | #7 | Deployment Verification |

---

## Next Steps

1. Review the [PHASES.md](./PHASES.md) for detailed phase tracking
2. Check the [tasks.md](./tasks.md) for implementation progress
3. Read the [design.md](./design.md) for architectural details
4. Refer to the [requirements.md](./requirements.md) for functional requirements
