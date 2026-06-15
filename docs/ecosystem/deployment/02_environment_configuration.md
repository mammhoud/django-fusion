# Environment Configuration

## Overview

Environment variables control application behavior across different environments.

## Configuration File

### .env File

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

## Django Settings

### Debug Mode

```env
# Development
DEBUG=True

# Production
DEBUG=False
```

### Secret Key

```env
# Generate a secure key
SECRET_KEY=your-very-secure-secret-key-here
```

### Allowed Hosts

```env
# Development
ALLOWED_HOSTS=localhost,127.0.0.1,site.structa.cloud

# Production
ALLOWED_HOSTS=site.structa.cloud,www.site.structa.cloud
```

## Database Configuration

### PostgreSQL

```env
DATABASE_URL=postgresql://user:password@localhost:5432/xellent

# Or individual settings
DB_ENGINE=django.db.backends.postgresql
DB_NAME=xellent
DB_USER=xellent_user
DB_PASSWORD=secure_password
DB_HOST=localhost
DB_PORT=5432
```

## Cache Configuration

### Redis

```env
REDIS_URL=redis://localhost:6379/0

# Or with password
REDIS_URL=redis://:password@localhost:6379/0
```

## Email Configuration

### Console Backend (Development)

```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### SMTP Backend (Production)

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@example.com
```

## API Keys

### OpenAI

```env
OPENAI_API_KEY=sk-...
```

### Anthropic

```env
ANTHROPIC_API_KEY=sk-ant-...
```

### Sentry

```env
SENTRY_DSN=https://...@sentry.io/...
```

## Security Settings

### CORS

```env
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

### CSRF

```env
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://site.structa.cloud
```

### SSL/TLS

```env
# Production
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
```

## Logging

### Log Level

```env
LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### Log File

```env
LOG_FILE=/var/log/django/app.log
```

## Environment-Specific Configurations

### Development

```env
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgresql://user:password@localhost:5432/xellent
REDIS_URL=redis://localhost:6379/0
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
LOG_LEVEL=DEBUG
```

### Staging

```env
DEBUG=False
ALLOWED_HOSTS=staging.structa.cloud
DATABASE_URL=postgresql://user:password@staging-db:5432/xellent
REDIS_URL=redis://staging-redis:6379/0
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
LOG_LEVEL=INFO
SENTRY_DSN=https://...@sentry.io/...
```

### Production

```env
DEBUG=False
ALLOWED_HOSTS=site.structa.cloud,www.site.structa.cloud
DATABASE_URL=postgresql://user:password@prod-db:5432/xellent
REDIS_URL=redis://:password@prod-redis:6379/0
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
LOG_LEVEL=WARNING
SENTRY_DSN=https://...@sentry.io/...
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

## Loading Environment Variables

### Python

```python
import os
from dotenv import load_dotenv

load_dotenv()

DEBUG = os.getenv('DEBUG', 'False') == 'True'
SECRET_KEY = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
```

### Django

```python
# settings.py
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = os.getenv('DEBUG', 'False') == 'True'
SECRET_KEY = os.getenv('SECRET_KEY')
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'xellent'),
        'USER': os.getenv('DB_USER', 'xellent_user'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}
```

## Security Best Practices

1. **Never commit .env file**: Add to .gitignore
2. **Use strong passwords**: Generate secure passwords
3. **Rotate secrets**: Regularly update API keys
4. **Use environment-specific values**: Different values per environment
5. **Limit access**: Restrict who can view environment variables
6. **Use secrets management**: Consider using AWS Secrets Manager or similar

## Related Documentation

- [Docker Compose Setup](01-docker-compose-setup.md)
- [Production Deployment Checklist](04-production-deployment-checklist.md)
- [Installation Guide](../getting-started/01-installation-guide.md)
