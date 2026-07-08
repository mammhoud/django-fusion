# Django-Fusion Configuration Guide

Complete guide to configuring django-fusion for different environments and use cases.

## Basic Setup

### 1. Installation

```bash
pip install django-fusion
```

### 2. Add to INSTALLED_APPS

```python
# settings.py
INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    # ...
    'django_fusion',
    'django_fusion.comp',
    # ...
]
```

### 3. Include URLs

```python
# urls.py
from pages.routable_components import site

urlpatterns = [
    # Routable components (before Wagtail/catch-all)
    path("", include((site.urls[0], site.urls[1]), namespace=site.urls[2])),
    
    # Other URLs
    path("admin/", admin.site.urls),
]
```

## Django Settings

### Core Settings

```python
# Enable/disable django-fusion
FUSION_ENABLED = True

# Auto-discover components
FUSION_AUTO_DISCOVER = True

# Components module name
FUSION_COMPONENTS_MODULE = 'routable_components'

# Component cache settings
FUSION_CACHE = {
    'TIMEOUT': 3600,
    'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    'KEY_PREFIX': 'fusion',
}

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django_fusion': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}
```

### Template Settings

```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
            BASE_DIR / 'applications/assets/templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django_fusion.context_processors.fusion',  # Add this
            ],
            'libraries': {
                'django_fusion': 'django_fusion.templatetags.fusion',
            },
        },
    },
]
```

### Database Settings

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'fusion_db'),
        'USER': os.environ.get('DB_USER', 'fusion_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'ATOMIC_REQUESTS': True,
    }
}
```

## Environment-Specific Configuration

### Development

```python
# settings_dev.py
from .settings import *

DEBUG = True
ALLOWED_HOSTS = ['*']

# Console email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Local cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Verbose logging
LOGGING['loggers']['django_fusion']['level'] = 'DEBUG'

FUSION_CACHE['TIMEOUT'] = 60  # Short cache for development
```

### Staging

```python
# settings_staging.py
from .settings import *

DEBUG = False
ALLOWED_HOSTS = ['staging.example.com']

# SMTP email backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# Redis cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# Standard logging
LOGGING['loggers']['django_fusion']['level'] = 'INFO'

FUSION_CACHE['TIMEOUT'] = 3600  # 1 hour
```

### Production

```python
# settings_prod.py
from .settings import *

DEBUG = False
ALLOWED_HOSTS = ['example.com', 'www.example.com']

# Secure settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {
    'default-src': ("'self'",),
    'script-src': ("'self'", "'unsafe-inline'"),
    'style-src': ("'self'", "'unsafe-inline'"),
}

# SMTP email backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# Redis cache with password
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': f"redis://:{os.environ.get('REDIS_PASSWORD')}@{os.environ.get('REDIS_HOST')}:6379/0",
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Quiet logging
LOGGING['loggers']['django_fusion']['level'] = 'WARNING'

# Long cache timeout
FUSION_CACHE['TIMEOUT'] = 7200  # 2 hours
```

## Component Registration

### Automatic Discovery

```python
# If FUSION_AUTO_DISCOVER = True, components are auto-discovered from:
# - <app>/routable_components.py
# - <app>/components.py
# - pages/routable_components.py
```

### Manual Registration

```python
# pages/routable_components.py
from django_fusion.comp.routes import Site, Application, RoutableComponent

class HomePage(RoutableComponent):
    route_path = ""
    template_name = "pages/home.html"

class AboutPage(RoutableComponent):
    route_path = "about/"
    template_name = "pages/about.html"

# Create application
pages_app = Application(
    name="pages",
    label="Pages",
    components=[HomePage, AboutPage],
)

# Create site
site = Site(
    name="mysite",
    label="My Site",
    applications=[pages_app],
)

# Export for URL registration
__all__ = ['site']
```

## Cache Configuration

### Local Memory Cache (Development)

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'fusion-cache',
    }
}
```

### Redis Cache (Recommended)

```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_CLASS_KWARGS': {
                'max_connections': 50,
            },
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
        }
    }
}

# Fusion-specific cache
FUSION_CACHE = {
    'TIMEOUT': 3600,
    'BACKEND': 'django_redis.cache.RedisCache',
    'KEY_PREFIX': 'fusion',
}
```

### Memcached Cache

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyMemcacheCache',
        'LOCATION': '127.0.0.1:11211',
    }
}
```

## Template Customization

### Custom Template Context Processor

```python
# myapp/context_processors.py
def fusion_context(request):
    """Add custom context to all templates."""
    return {
        'site_name': 'My Site',
        'site_description': 'My awesome site',
        'nav_items': get_navigation(),
    }

# settings.py
TEMPLATES = [
    {
        'OPTIONS': {
            'context_processors': [
                'myapp.context_processors.fusion_context',  # Add this
            ],
        },
    },
]
```

### Template Loaders

```python
TEMPLATES = [
    {
        'OPTIONS': {
            'loaders': [
                # Load from filesystem first
                'django.template.loaders.filesystem.Loader',
                # Then from app directories
                'django.template.loaders.app_directories.Loader',
                # Optional: cache loader for production
                ('django.template.loaders.cached.Loader', [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                ]),
            ],
        },
    },
]
```

## Static & Media Files

### Static Files

```python
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
    BASE_DIR / 'applications/assets/static',
]

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Whitenoise for production
MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # ... other middleware
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### Media Files

```python
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# In urls.py
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

## Security Configuration

### CORS Settings

```python
INSTALLED_APPS = [
    'corsheaders',
    # ...
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    # ...
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://example.com",
]

CORS_ALLOW_CREDENTIALS = True
```

### CSRF Settings

```python
CSRF_TRUSTED_ORIGINS = [
    'https://example.com',
    'https://*.example.com',
]

CSRF_COOKIE_HTTPONLY = False  # JavaScript needs to read CSRF token
CSRF_COOKIE_SECURE = True     # Only send over HTTPS
```

### Security Headers

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # ...
]

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {
    'default-src': ("'self'",),
    'script-src': ("'self'", "cdn.jsdelivr.net"),
    'style-src': ("'self'", "'unsafe-inline'"),
}
```

## Middleware Configuration

```python
MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_fusion.core.middlewares.fusion.FusionMiddleware',  # Add this
]
```

## Authentication Configuration

### Django-Allauth Integration

```python
INSTALLED_APPS = [
    # ...
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    # ...
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = 1

LOGIN_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
```

## Logging Configuration

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/fusion.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
        'django_fusion': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
        },
    },
}
```

## Environment Variables

### Required Variables

```bash
# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=fusion_db
DB_USER=fusion_user
DB_PASSWORD=secure_password
DB_HOST=localhost
DB_PORT=5432

# Django
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=example.com,www.example.com

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-password

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=redis-password

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### Optional Variables

```bash
# Fusion-specific
FUSION_CACHE_TIMEOUT=3600
FUSION_ENABLE_TRACKING=True
FUSION_AUTO_DISCOVER=True

# AWS/Cloud storage
AWS_STORAGE_BUCKET_NAME=my-bucket
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret

# Analytics
GOOGLE_ANALYTICS_ID=UA-XXXXXXXXX-X
SENTRY_DSN=https://...
```

## Health Checks

### Health Check Endpoint

```python
# urls.py
from django_fusion.health import HealthCheckView

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health'),
    path('health/db/', DatabaseHealthView.as_view(), name='health_db'),
    path('health/assets/', AssetsHealthView.as_view(), name='health_assets'),
]
```

### Docker Health Check

```dockerfile
FROM python:3.10

# ... build steps ...

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

## Troubleshooting Configuration

### Debug Mode Issues

```python
# If components not loading:
FUSION_AUTO_DISCOVER = True
FUSION_ENABLE_TRACKING = True

# Check logs
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Cache Issues

```python
# Clear cache if components not updating
from django.core.cache import cache
cache.clear()

# Or set shorter timeout during development
FUSION_CACHE['TIMEOUT'] = 60
```

### Template Not Found

```python
# Verify template directories are configured
print(settings.TEMPLATES[0]['DIRS'])
print(settings.TEMPLATES[0]['APP_DIRS'])

# Check template loader order
print(settings.TEMPLATES[0]['OPTIONS']['loaders'])
```

## Performance Tuning

### Database Connection Pooling

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'CONN_MAX_AGE': 600,  # Connection pooling
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}
```

### Gunicorn Configuration

```python
# gunicorn_config.py
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
```

### Caching Strategy

```python
# Cache API responses
from django.views.decorators.cache import cache_page

@cache_page(60 * 5)  # 5 minutes
def my_view(request):
    pass
```

## Related Documentation

- [GETTING_STARTED.md](./GETTING_STARTED.md) - Quick start
- [BEST_PRACTICES.md](./BEST_PRACTICES.md) - Best practices
- [DEPLOYMENT.md](./DEPLOYMENT.md) - Deployment guide (if available)

---

**Next**: Review [BEST_PRACTICES.md](./BEST_PRACTICES.md) for coding patterns.

