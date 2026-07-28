# Tinker Dynaconf Configuration System

## Overview

Tinker now uses **Dynaconf** for multi-environment configuration management. This replaces hardcoded settings with flexible, environment-aware YAML configuration files.

## Configuration Files

### Base Configuration
**File**: `configs/settings.yml`  
**Purpose**: Default settings for all environments  
**Contains**: Django core settings, database, static files, templates, AI models, logging, security, caching, email

**Example**:
```yaml
DJANGO:
  secret_key: "{{ env 'TINKER_SECRET_KEY' or 'django-insecure-tinker-dev' }}"
  debug: "{{ env 'TINKER_DEBUG' or true }}"
  allowed_hosts:
    - "{{ env 'TINKER_ALLOWED_HOSTS' or 'localhost,127.0.0.1,tinker.localhost' }}"
```

### Environment-Specific Overrides
**Files**:
- `configs/settings.development.yml` - Development environment overrides
- `configs/settings.production.yml` - Production environment overrides
- `configs/settings.staging.yml` - Staging environment overrides (optional)

**Example** (settings.development.yml):
```yaml
DJANGO:
  debug: true
  allowed_hosts:
    - "localhost"
    - "127.0.0.1"
    - "tinker.localhost"

DATABASE:
  engine: "django.db.backends.sqlite3"
  name: "db.sqlite3"
```

### Model Registry
**File**: `configs/models.yml`  
**Purpose**: AI model definitions with provider configuration  
**Format**: Dynaconf YAML with environment variable interpolation

**Example**:
```yaml
models:
  - id: gemma3-4b
    name: Gemma 3 4B
    provider: ollama
    model: gemma3:4b
    base_url: "{{ env 'OLLAMA_BASE_URL' or 'http://localhost:11434' }}"
    default: true
```

### Environment Variables
**File**: `.env` (gitignored)  
**Purpose**: Secret configuration and environment-specific values  
**Templates**: 
- `.env.example` - Generic template for all environments
- `.env.development` - Development defaults
- `.env.production.example` - Production template with placeholders

## Environment Detection

Dynaconf detects the environment in this order:
1. `TINKER_ENV` environment variable
2. `DJANGO_ENV` environment variable
3. `ENV` environment variable
4. `ENVIRONMENT` environment variable
5. Defaults to `development`

**Set environment**:
```bash
export TINKER_ENV=production
python manage.py check
```

## Configuration Precedence

Settings are loaded in this order (later overrides earlier):
1. Python defaults (settings.py)
2. Base YAML (`configs/settings.yml`)
3. Environment-specific YAML (`configs/settings.{ENV}.yml`)
4. Environment variables (`.env` file or system)

**Example - Setting DEBUG for production**:
```bash
# In .env.production:
TINKER_DEBUG=false

# In configs/settings.production.yml:
DJANGO:
  debug: false

# Both set DEBUG=false, with .env taking precedence
```

## Available Settings

### Django Settings
```python
DJANGO:
  secret_key          # Encryption key (MUST set in production)
  debug               # Debug mode (boolean)
  allowed_hosts       # List of allowed domain names
  time_zone           # Timezone (default: UTC)
  language_code       # Language code (default: en-us)
```

### Database Configuration
```python
DATABASE:
  engine              # "django.db.backends.sqlite3" or "postgresql"
  name                # Database name or SQLite path
  host                # Database host (PostgreSQL only)
  port                # Database port (PostgreSQL only)
  user                # Database user (PostgreSQL only)
  password            # Database password (PostgreSQL only)
```

### Static Files
```python
STATIC_FILES:
  url                 # URL path for static files
  root                # Directory to collect static files into
  dirs                # Directories to search for static files
```

### Media Files
```python
MEDIA:
  url                 # URL path for media uploads
  root                # Directory for uploaded media
```

### AI Models Registry
```python
MODELS:
  registry_file       # Path to models.yml
  default_provider    # Default provider ("ollama", "openai_compatible")
  timeout             # Request timeout in seconds
```

### Ollama Configuration
```python
OLLAMA:
  enabled             # Enable Ollama support
  base_url            # Ollama API URL
  model               # Default model identifier
  timeout             # Request timeout in seconds
```

### OpenAI-Compatible APIs
```python
CEPTOR_AI:
  enabled             # Enable Ceptor-AI agents
  agents_dir          # Path to agents directory
  models_file         # Path to models.yml
```

### Security Settings
```python
SECURITY:
  csrf_cookie_secure           # CSRF cookie over HTTPS only
  session_cookie_secure        # Session cookie over HTTPS only
  ssl_redirect                 # Redirect HTTP to HTTPS
  secure_browser_xss_filter    # Enable XSS protection
```

### Logging
```python
LOGGING:
  version              # Logging config version
  disable_existing_loggers
  formatters
  handlers
  loggers
```

### Caching
```python
CACHES:
  default:
    backend          # Cache backend class
    location         # Cache location (Redis, memcached, etc)
    timeout          # Cache timeout in seconds
```

### Email Configuration
```python
EMAIL:
  backend              # Email backend class
  host                 # SMTP host
  port                 # SMTP port
  use_tls              # Use TLS encryption
  user                 # SMTP username
  password             # SMTP password
  from_address         # From address for emails
```

## Django Integration

### In settings.py
```python
from django_fusion.config.dynaconf_loader import (
    DynaconfSettings,
    ModelsRegistry,
    TemplateRegistry,
)

# Load Dynaconf
dynaconf_settings = DynaconfSettings(config_dir="configs/").load()

# Initialize registries
MODELS_REGISTRY = ModelsRegistry(dynaconf_settings)
TEMPLATES_REGISTRY = TemplateRegistry(dynaconf_settings)

# Access settings
SECRET_KEY = dynaconf_settings.get("DJANGO.secret_key")
DEBUG = dynaconf_settings.get("DJANGO.debug")
```

### In Django Code
```python
from django.conf import settings

# Access Dynaconf functions
from tinker.settings import get_models, get_default_model

# Get all models
all_models = get_models()

# Get specific model
model = get_default_model(provider="ollama")

# Get template apps
apps = settings.CUSTOMIZER_APPS
```

## Make Commands for Configuration

### Check Configuration
```bash
make config-check       # Verify Dynaconf loads
make config-validate    # Validate configuration structure
make config-show        # Display current configuration
make config-env         # Show environment variables
```

### Django Checks
```bash
make check              # Django system checks
make check-deploy       # Production readiness checks
```

## Usage Examples

### Development Setup
```bash
# Copy development env template
cp .env.example .env.development

# Set environment
export TINKER_ENV=development

# Check configuration
make config-check

# Run Django check
make check

# Start server
make run
```

### Production Deployment
```bash
# Create production env file (add real secrets!)
cp .env.production.example .env.production
# Edit .env.production with real values

# Set environment
export TINKER_ENV=production

# Validate configuration
make config-validate

# Deploy
make deploy
```

### Override Single Setting
```bash
# Via command line
export TINKER_SECRET_KEY=your-production-key
export TINKER_DEBUG=false

# Django check will use these values
make check
```

### Access Models from Django Shell
```bash
python manage.py shell

from tinker.settings import get_models, get_default_model
models = get_models()
for model in models:
    print(f"{model['name']} ({model['provider']})")

default_model = get_default_model(provider="ollama")
print(f"Default: {default_model['name']}")
```

## Troubleshooting

### Configuration Not Loading
```bash
# Check for errors
python manage.py check

# Verify files exist
ls -la configs/settings.yml
ls -la configs/settings.development.yml

# Check environment
make config-env
```

### Wrong Environment Detected
```bash
# Explicitly set environment
export TINKER_ENV=production
python manage.py check
```

### Secret Key Not Found
```bash
# Set in environment
export TINKER_SECRET_KEY=your-generated-key

# Or in .env file
echo "TINKER_SECRET_KEY=your-generated-key" >> .env

# Check what's loaded
make config-show
```

### Dynaconf Import Error
```bash
# Install Dynaconf
pip install dynaconf

# Verify installation
python -c "import dynaconf; print(dynaconf.__version__)"
```

## Best Practices

1. **Never commit secrets** - Use `.env.production.example` as template, keep `.env` gitignored
2. **Use environment variables** - Most secure for production secrets
3. **Document overrides** - Comment in YAML files when overriding defaults
4. **Validate on deploy** - Run `make config-validate` before production deployment
5. **Use specific types** - Dynaconf will parse YAML types (strings, booleans, numbers, lists, dicts)
6. **Test locally first** - Always test configuration locally before production

## Migration from Old Settings

Old hardcoded settings can be migrated to Dynaconf:

**Before** (settings.py):
```python
DEBUG = True
SECRET_KEY = "insecure-key"
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", ...}}
```

**After** (configs/settings.yml):
```yaml
DJANGO:
  debug: true
  secret_key: "{{ env 'TINKER_SECRET_KEY' or 'insecure-key' }}"

DATABASE:
  engine: "django.db.backends.sqlite3"
  name: "db.sqlite3"
```

**Then in settings.py**:
```python
dynaconf_settings = DynaconfSettings(config_dir="configs/").load()
DEBUG = dynaconf_settings.get("DJANGO.debug")
SECRET_KEY = dynaconf_settings.get("DJANGO.secret_key")
```

## Documentation References

- **Dynaconf Docs**: https://www.dynaconf.com/
- **Django Settings**: https://docs.djangoproject.com/en/5.2/topics/settings/
- **django-fusion**: See `django_fusion.config.dynaconf_loader` module

## Environment Files Reference

See also:
- `.env.example` - Template with all possible settings
- `.env.development` - Development defaults (checked into git for team reference)
- `.env.production.example` - Production template with placeholders (guide for deployment)
