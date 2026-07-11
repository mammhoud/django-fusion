# Environments — Configuration & Management

Structa Cloud uses [Dynaconf](https://www.dynaconf.com/) for environment-based configuration management across development, demo, and production environments.

## Environment Types

| Environment | Dynaconf Value | Description | Debug | Production |
|---|---|---|---|---|
| **Development** | `development` | Local development workstation | `True` | `False` |
| **Demo** | `demo` / `staging` | Staging/preview server | `True` | `False` |
| **Production** | `production` / `prod` | Live production server | `False` | `True` |

## Environment Detection

Environments are detected in `configs/settings/conf.py` via the `Environment` enum:

```python
class Environment(str, Enum):
    DEVELOPMENT = "development"
    DEMO = "demo"
    PRODUCTION = "production"
```

Detection priority:
1. `DJANGO_ENV` environment variable
2. `DYNACONF_ENV` environment variable  
3. Falls back to `development` for local runs

## Configuration Files

| File | Purpose |
|---|---|
| `configs/settings/conf.py` | Dynaconf initialization, environment enum, settings object |
| `configs/settings/setup.py` | Environment detection, feature flags (`is_production`, `is_demo`, `is_debug`) |
| `configs/settings/CD/core.py` | Core/CD-specific settings |
| `configs/settings/CD/production.py` | Production overrides |
| `configs/settings/CD/demo.py` | Demo/staging overrides |
| `configs/settings/CD/services.py` | Service-specific settings |

## Settings Object API

The `settings` object (from `configs.settings.conf`) provides a consistent API:

```python
from configs.settings.conf import settings

# Core attributes
settings.MODULE          # "LMS" or "CMS"
settings.SERVER_ENV      # Environment enum
settings.is_production   # bool
settings.is_demo         # bool
settings.is_debug        # bool

# Type-safe getters
settings.get("KEY", default, block="SECTION")
settings.get_bool("KEY", default, block="SECTION")
settings.get_int("KEY", default, block="SECTION")

# Section access
settings.section("SECTION_NAME")   # Returns section as dict
settings.setting_map(mapping, block="SECTION")  # Bulk mapping with defaults
```

## Feature Toggles by Environment

### Production (`is_production = True`)
- `DEBUG = False`
- Secure cookies enabled
- SSL redirect enabled
- HSTS enabled (31536000 seconds)
- Email queue enabled
- Email tracking enabled
- Rate limiting enabled
- Session engine: cache-based
- 2FA required for admin (by default)
- CORS: only allowed origins
- Webpack cache enabled

### Demo/Staging (`is_demo = True`)
- `DEBUG = True`
- Secure cookies disabled
- Email strategy: Mailtrap
- Local timezone: Africa/Cairo
- Cache timeout: 60 seconds (shorter for testing)

### Development (`is_development = True`)  
- `DEBUG = True`
- Secure cookies disabled
- Email strategy: Console backend
- `INTERNAL_IPS`: localhost, 127.0.0.1
- Debug toolbar available (if installed)
- Webpack: FakeWebpackLoader if bundles.json absent
- WAGTAIL_ENABLE_UPDATE_CHECK: False

## Environment Variables

Key environment variables used across environments:

| Variable | Purpose | Required |
|---|---|---|
| `DJANGO_ENV` | Environment name | No (auto-detected) |
| `DJANGO_SITE` | Active website name | Yes (set by site manage.py) |
| `DJANGO_WEBSITE` | Active website name (alias) | Yes |
| `WEBSITE` | Active website name (alias) | Yes |
| `ALLOWED_HOSTS` | Comma-separated hostnames | Production only |
| `DJANGO_SECRET_KEY` | Django secret key | Yes |
| `REDIS_URL` | Redis connection URL | Yes (for cache/queue) |
| `DATABASES.default` | Database configuration | Yes |

## Adding a New Environment Variable

1. Add the variable to your `.env` file or deployment config
2. Access it via `settings.get("KEY", default)` in config modules
3. Never hardcode secrets — use dynaconf or env vars
4. For optional features, use `settings.get_bool("FEATURE_FLAG", False)`

## Docker Environment

In Docker, environment variables are passed via `docker-compose.yml`:

```yaml
services:
  website:
    environment:
      - DJANGO_SITE=ctc-research
      - DJANGO_ENV=production
      - DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}
      - REDIS_URL=redis://redis:6379/0
```

## See Also
- [websites.md](websites.md) — Per-website configuration
- [packages.md](packages.md) — Package dependencies
- [Dynaconf docs](https://www.dynaconf.com/)
