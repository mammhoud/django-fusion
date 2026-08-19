# Environment Configuration Documentation

## Overview

This document provides comprehensive documentation of all environment variables required for deploying the multi-domain infrastructure. Environment variables control application behavior across different environments (development, staging, production) and are essential for proper service configuration.

**Key Principles:**
- All sensitive configuration is managed via environment variables
- Separate `.env` files for different environments
- No hardcoded secrets in configuration files
- Clear distinction between required and optional variables
- Security considerations documented for sensitive variables

---

## Table of Contents

1. [Django Frontend Service](#django-frontend-service)
2. [Django API Backend Service](#django-api-backend-service)
3. [PostgreSQL Database Service](#postgresql-database-service)
4. [Nginx Reverse Proxy Service](#nginx-reverse-proxy-service)
5. [Docsify Documentation Service](#docsify-documentation-service)
6. [LMS Service](#lms-service)
7. [Environment-Specific Configurations](#environment-specific-configurations)
8. [Security Considerations](#security-considerations)

---

## Django Frontend Service

The Frontend Service is the user-facing Django application serving the web interface.

### Required Variables

#### `DEBUG`
- **Type:** Boolean
- **Required:** Yes
- **Valid Values:** `True`, `False`
- **Default:** `False`
- **Purpose:** Controls Django debug mode and error reporting
- **Impact:**
  - `True`: Detailed error pages, static file serving, template error details
  - `False`: Generic error pages, no sensitive information exposed
- **Example Values:**
  - Development: `DEBUG=True`
  - Staging: `DEBUG=False`
  - Production: `DEBUG=False`
- **Security Note:** MUST be `False` in production. Exposing debug information is a security risk.

#### `SECRET_KEY`
- **Type:** String
- **Required:** Yes
- **Valid Values:** Long random string (50+ characters)
- **Default:** None (must be provided)
- **Purpose:** Django's secret key for cryptographic signing
- **Impact:** Used for session encryption, CSRF tokens, password reset tokens
- **Example Values:**
  ```
  SECRET_KEY=django-insecure-abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
  ```
- **Security Note:**
  - MUST be unique per environment
  - MUST be kept secret and never committed to version control
  - Generate using: `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`
  - Rotate periodically in production

#### `ALLOWED_HOSTS`
- **Type:** Comma-separated string
- **Required:** Yes
- **Valid Values:** Domain names and IP addresses
- **Default:** None (must be provided)
- **Purpose:** Specifies which hosts can serve the application
- **Impact:** Prevents Host header attacks
- **Example Values:**
  - Development: `ALLOWED_HOSTS=localhost,127.0.0.1,site.structa.cloud`
  - Staging: `ALLOWED_HOSTS=staging.structa.cloud`
  - Production: `ALLOWED_HOSTS=site.structa.cloud,www.site.structa.cloud`
- **Security Note:** Must match the Host header sent by reverse proxy

#### `DATABASE_URL`
- **Type:** String (connection string)
- **Required:** Yes
- **Valid Values:** PostgreSQL connection string
- **Default:** None (must be provided)
- **Purpose:** Database connection configuration
- **Impact:** Determines where application data is stored
- **Example Values:**
  ```
  DATABASE_URL=postgresql://user:password@postgres:5432/frontend_db
  ```
- **Format:** `postgresql://[user]:[password]@[host]:[port]/[database]`
- **Security Note:**
  - Password should be strong and unique
  - Use environment-specific credentials
  - Never use default credentials in production

#### `RUNNING_ENV`
- **Type:** String
- **Required:** Yes
- **Valid Values:** `docker`, `local`, `production`
- **Default:** `local`
- **Purpose:** Indicates the runtime environment
- **Impact:** Affects logging, error handling, and service discovery
- **Example Values:**
  - Development: `RUNNING_ENV=local`
  - Docker: `RUNNING_ENV=docker`
  - Production: `RUNNING_ENV=production`

#### `SERVER_ENV`
- **Type:** String
- **Required:** Yes
- **Valid Values:** `development`, `staging`, `production`
- **Default:** `development`
- **Purpose:** Specifies the deployment environment
- **Impact:** Controls feature flags, logging levels, and security settings
- **Example Values:**
  - Development: `SERVER_ENV=development`
  - Staging: `SERVER_ENV=staging`
  - Production: `SERVER_ENV=production`

### Optional Variables

#### `STATIC_URL`
- **Type:** String
- **Required:** No
- **Valid Values:** URL path
- **Default:** `/static/`
- **Purpose:** URL prefix for static files
- **Example:** `STATIC_URL=/static/`

#### `MEDIA_URL`
- **Type:** String
- **Required:** No
- **Valid Values:** URL path
- **Default:** `/media/`
- **Purpose:** URL prefix for user-uploaded media files
- **Example:** `MEDIA_URL=/media/`

#### `SECURE_SSL_REDIRECT`
- **Type:** Boolean
- **Required:** No
- **Valid Values:** `True`, `False`
- **Default:** `False`
- **Purpose:** Redirect HTTP requests to HTTPS
- **Impact:** Enforces secure connections
- **Example Values:**
  - Development: `SECURE_SSL_REDIRECT=False`
  - Production: `SECURE_SSL_REDIRECT=True`
- **Security Note:** Should be `True` in production

#### `SESSION_COOKIE_SECURE`
- **Type:** Boolean
- **Required:** No
- **Valid Values:** `True`, `False`
- **Default:** `False`
- **Purpose:** Only send session cookies over HTTPS
- **Impact:** Prevents session hijacking over unencrypted connections
- **Example Values:**
  - Development: `SESSION_COOKIE_SECURE=False`
  - Production: `SESSION_COOKIE_SECURE=True`
- **Security Note:** Should be `True` in production

#### `CSRF_COOKIE_SECURE`
- **Type:** Boolean
- **Required:** No
- **Valid Values:** `True`, `False`
- **Default:** `False`
- **Purpose:** Only send CSRF cookies over HTTPS
- **Impact:** Prevents CSRF token interception
- **Example Values:**
  - Development: `CSRF_COOKIE_SECURE=False`
  - Production: `CSRF_COOKIE_SECURE=True`
- **Security Note:** Should be `True` in production

#### `CSRF_TRUSTED_ORIGINS`
- **Type:** Comma-separated string
- **Required:** No
- **Valid Values:** Domain names
- **Default:** Empty
- **Purpose:** Specifies trusted origins for CSRF validation
- **Example:** `CSRF_TRUSTED_ORIGINS=https://site.structa.cloud,https://www.site.structa.cloud`
- **Security Note:** Only include trusted domains

#### `LOG_LEVEL`
- **Type:** String
- **Required:** No
- **Valid Values:** `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- **Default:** `INFO`
- **Purpose:** Controls logging verbosity
- **Example Values:**
  - Development: `LOG_LEVEL=DEBUG`
  - Staging: `LOG_LEVEL=INFO`
  - Production: `LOG_LEVEL=WARNING`

---

## Django API Backend Service

The API Backend Service provides REST API endpoints for core business logic.

### Required Variables

#### `DEBUG`
- **Type:** Boolean
- **Required:** Yes
- **Valid Values:** `True`, `False`
- **Default:** `False`
- **Purpose:** Controls Django debug mode
- **Impact:** Same as Frontend Service
- **Example Values:**
  - Development: `DEBUG=True`
  - Production: `DEBUG=False`
- **Security Note:** MUST be `False` in production

#### `SECRET_KEY`
- **Type:** String
- **Required:** Yes
- **Valid Values:** Long random string (50+ characters)
- **Default:** None (must be provided)
- **Purpose:** Django's secret key for cryptographic signing
- **Impact:** Used for token generation and validation
- **Example:** `SECRET_KEY=django-insecure-xyz789abc123def456ghi789jkl012mno345pqr678stu901vwx`
- **Security Note:**
  - MUST be different from Frontend Service key
  - Keep secret and never commit to version control
  - Rotate periodically

#### `ALLOWED_HOSTS`
- **Type:** Comma-separated string
- **Required:** Yes
- **Valid Values:** Domain names and IP addresses
- **Default:** None (must be provided)
- **Purpose:** Specifies which hosts can serve the API
- **Impact:** Prevents Host header attacks
- **Example Values:**
  - Development: `ALLOWED_HOSTS=localhost,127.0.0.1,core.structa.cloud`
  - Production: `ALLOWED_HOSTS=core.structa.cloud`
- **Security Note:** Must match the Host header sent by reverse proxy

#### `DATABASE_URL`
- **Type:** String (connection string)
- **Required:** Yes
- **Valid Values:** PostgreSQL connection string
- **Default:** None (must be provided)
- **Purpose:** Database connection configuration
- **Impact:** Determines where API data is stored
- **Example:** `DATABASE_URL=postgresql://user:password@postgres:5432/api_db`
- **Security Note:** Use strong, unique credentials

#### `RUNNING_ENV`
- **Type:** String
- **Required:** Yes
- **Valid Values:** `docker`, `local`, `production`
- **Default:** `local`
- **Purpose:** Indicates the runtime environment
- **Example:** `RUNNING_ENV=docker`

#### `SERVER_ENV`
- **Type:** String
- **Required:** Yes
- **Valid Values:** `development`, `staging`, `production`
- **Default:** `development`
- **Purpose:** Specifies the deployment environment
- **Example:** `SERVER_ENV=production`

### Optional Variables

#### `API_RATE_LIMIT`
- **Type:** Integer
- **Required:** No
- **Valid Values:** Requests per minute (e.g., 60, 100, 1000)
- **Default:** `100`
- **Purpose:** Rate limiting for API endpoints
- **Example Values:**
  - Development: `API_RATE_LIMIT=1000`
  - Production: `API_RATE_LIMIT=100`

#### `API_TIMEOUT`
- **Type:** Integer
- **Required:** No
- **Valid Values:** Seconds (e.g., 30, 60, 300)
- **Default:** `30`
- **Purpose:** Request timeout for API operations
- **Example:** `API_TIMEOUT=60`

#### `CORS_ALLOWED_ORIGINS`
- **Type:** Comma-separated string
- **Required:** No
- **Valid Values:** URLs
- **Default:** Empty
- **Purpose:** Allowed origins for CORS requests
- **Example:** `CORS_ALLOWED_ORIGINS=https://site.structa.cloud,https://www.site.structa.cloud`
- **Security Note:** Only include trusted origins

---

## PostgreSQL Database Service

The PostgreSQL service provides persistent data storage for both Frontend and API Backend services.

### Required Variables

#### `POSTGRES_USER`
- **Type:** String
- **Required:** Yes
- **Valid Values:** Valid PostgreSQL username
- **Default:** None (must be provided)
- **Purpose:** PostgreSQL superuser username
- **Example:** `POSTGRES_USER=postgres`
- **Security Note:** Use a strong, unique username

#### `POSTGRES_PASSWORD`
- **Type:** String
- **Required:** Yes
- **Valid Values:** Strong password (12+ characters, mixed case, numbers, symbols)
- **Default:** None (must be provided)
- **Purpose:** PostgreSQL superuser password
- **Example:** `POSTGRES_PASSWORD=SecureP@ssw0rd123`
- **Security Note:**
  - MUST be strong and unique
  - Never use default or simple passwords
  - Rotate periodically in production
  - Store securely in secrets management system

#### `INITDB_MULTIPLE_DATABASES`
- **Type:** Comma-separated string
- **Required:** Yes
- **Valid Values:** Database names
- **Default:** None (must be provided)
- **Purpose:** Creates multiple databases on initialization
- **Example:** `INITDB_MULTIPLE_DATABASES=frontend_db,api_db`
- **Impact:** Allows separate databases for Frontend and API services

### Optional Variables

#### `POSTGRES_PORT`
- **Type:** Integer
- **Required:** No
- **Valid Values:** Port number (1024-65535)
- **Default:** `5432`
- **Purpose:** PostgreSQL listening port
- **Example:** `POSTGRES_PORT=5432`
- **Note:** Internal port only, not exposed externally

#### `POSTGRES_INITDB_ARGS`
- **Type:** String
- **Required:** No
- **Valid Values:** PostgreSQL initdb arguments
- **Default:** Empty
- **Purpose:** Additional initialization arguments
- **Example:** `POSTGRES_INITDB_ARGS=--encoding=UTF8 --locale=en_US.UTF-8`

#### `POSTGRES_HOST_AUTH_METHOD`
- **Type:** String
- **Required:** No
- **Valid Values:** `trust`, `md5`, `scram-sha-256`
- **Default:** `scram-sha-256`
- **Purpose:** Authentication method for local connections
- **Security Note:** Use `scram-sha-256` for production

---

## Nginx Reverse Proxy Service

The Nginx Reverse Proxy routes requests to appropriate backend services based on Host headers.

### Required Variables

#### `NGINX_HOST`
- **Type:** String
- **Required:** Yes
- **Valid Values:** Domain name
- **Default:** None (must be provided)
- **Purpose:** Primary domain for the reverse proxy
- **Example:** `NGINX_HOST=structa.cloud`

#### `NGINX_PORT`
- **Type:** Integer
- **Required:** Yes
- **Valid Values:** Port number (80, 443)
- **Default:** `80`
- **Purpose:** Port for HTTP traffic
- **Example:** `NGINX_PORT=80`

### Optional Variables

#### `NGINX_WORKER_PROCESSES`
- **Type:** Integer or `auto`
- **Required:** No
- **Valid Values:** Number of worker processes or `auto`
- **Default:** `auto`
- **Purpose:** Number of Nginx worker processes
- **Example:** `NGINX_WORKER_PROCESSES=auto`

#### `NGINX_WORKER_CONNECTIONS`
- **Type:** Integer
- **Required:** No
- **Valid Values:** Number of connections (1024-65536)
- **Default:** `1024`
- **Purpose:** Maximum concurrent connections per worker
- **Example:** `NGINX_WORKER_CONNECTIONS=2048`

#### `NGINX_GZIP_ENABLED`
- **Type:** Boolean
- **Required:** No
- **Valid Values:** `on`, `off`
- **Default:** `on`
- **Purpose:** Enable gzip compression
- **Example:** `NGINX_GZIP_ENABLED=on`

#### `NGINX_GZIP_LEVEL`
- **Type:** Integer
- **Required:** No
- **Valid Values:** 1-9
- **Default:** `6`
- **Purpose:** Gzip compression level
- **Example:** `NGINX_GZIP_LEVEL=6`

#### `NGINX_CACHE_ENABLED`
- **Type:** Boolean
- **Required:** No
- **Valid Values:** `on`, `off`
- **Default:** `off`
- **Purpose:** Enable response caching
- **Example:** `NGINX_CACHE_ENABLED=off`

---

## Docsify Documentation Service

The Docsify Service serves technical documentation via Nginx.

### Required Variables

#### `NGINX_HOST`
- **Type:** String
- **Required:** Yes
- **Valid Values:** Domain name
- **Default:** None (must be provided)
- **Purpose:** Domain for documentation service
- **Example:** `NGINX_HOST=site-docs.structa.cloud`

### Optional Variables

#### `DOCS_CACHE_ENABLED`
- **Type:** Boolean
- **Required:** No
- **Valid Values:** `True`, `False`
- **Default:** `True`
- **Purpose:** Enable caching for documentation files
- **Example:** `DOCS_CACHE_ENABLED=True`

#### `DOCS_CACHE_DURATION`
- **Type:** Integer
- **Required:** No
- **Valid Values:** Seconds (e.g., 3600, 86400)
- **Default:** `3600`
- **Purpose:** Cache duration for documentation files
- **Example:** `DOCS_CACHE_DURATION=86400`

#### `DOCS_GZIP_ENABLED`
- **Type:** Boolean
- **Required:** No
- **Valid Values:** `True`, `False`
- **Default:** `True`
- **Purpose:** Enable gzip compression for documentation
- **Example:** `DOCS_GZIP_ENABLED=True`

---

## LMS Service

The LMS Service currently runs in maintenance mode.

### Required Variables

#### `NGINX_HOST`
- **Type:** String
- **Required:** Yes
- **Valid Values:** Domain name
- **Default:** None (must be provided)
- **Purpose:** Domain for LMS service
- **Example:** `NGINX_HOST=lms.structa.cloud`

### Optional Variables

#### `LMS_MAINTENANCE_MESSAGE`
- **Type:** String
- **Required:** No
- **Valid Values:** HTML content
- **Default:** "Coming Soon"
- **Purpose:** Custom maintenance message
- **Example:** `LMS_MAINTENANCE_MESSAGE=Learning Management System coming soon`

---

## Environment-Specific Configurations

### Development Environment

**Purpose:** Local development with relaxed security constraints

```env
# Django Frontend
DEBUG=True
SECRET_KEY=django-insecure-dev-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1,site.structa.cloud
DATABASE_URL=postgresql://user:password@localhost:5432/frontend_db
RUNNING_ENV=local
SERVER_ENV=development
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
LOG_LEVEL=DEBUG

# Django API Backend
API_RATE_LIMIT=1000
API_TIMEOUT=60
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=dev_password
INITDB_MULTIPLE_DATABASES=frontend_db,api_db

# Nginx Reverse Proxy
NGINX_HOST=structa.cloud
NGINX_PORT=80
NGINX_WORKER_PROCESSES=auto
NGINX_WORKER_CONNECTIONS=1024

# Docsify
DOCS_CACHE_ENABLED=False
DOCS_GZIP_ENABLED=True

# LMS
LMS_MAINTENANCE_MESSAGE=Learning Management System - Coming Soon
```

**Characteristics:**
- Debug mode enabled for detailed error reporting
- Relaxed security settings for easier development
- Higher logging verbosity for troubleshooting
- No SSL/TLS enforcement
- Higher rate limits for testing

### Staging Environment

**Purpose:** Pre-production testing with production-like configuration

```env
# Django Frontend
DEBUG=False
SECRET_KEY=django-insecure-staging-key-change-in-production
ALLOWED_HOSTS=staging.structa.cloud
DATABASE_URL=postgresql://user:password@staging-db:5432/frontend_db
RUNNING_ENV=docker
SERVER_ENV=staging
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
LOG_LEVEL=INFO

# Django API Backend
API_RATE_LIMIT=500
API_TIMEOUT=30
CORS_ALLOWED_ORIGINS=https://staging.structa.cloud

# PostgreSQL
POSTGRES_USER=staging_user
POSTGRES_PASSWORD=staging_secure_password
INITDB_MULTIPLE_DATABASES=frontend_db,api_db

# Nginx Reverse Proxy
NGINX_HOST=staging.structa.cloud
NGINX_PORT=80
NGINX_WORKER_PROCESSES=auto
NGINX_WORKER_CONNECTIONS=2048

# Docsify
DOCS_CACHE_ENABLED=True
DOCS_CACHE_DURATION=3600
DOCS_GZIP_ENABLED=True

# LMS
LMS_MAINTENANCE_MESSAGE=Learning Management System - Coming Soon
```

**Characteristics:**
- Debug mode disabled
- SSL/TLS enforcement enabled
- Moderate logging for monitoring
- Production-like security settings
- Moderate rate limits for realistic testing

### Production Environment

**Purpose:** Live deployment with maximum security and performance

```env
# Django Frontend
DEBUG=False
SECRET_KEY=<generate-secure-random-key>
ALLOWED_HOSTS=site.structa.cloud,www.site.structa.cloud
DATABASE_URL=postgresql://user:secure_password@prod-db:5432/frontend_db
RUNNING_ENV=production
SERVER_ENV=production
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
CSRF_TRUSTED_ORIGINS=https://site.structa.cloud,https://www.site.structa.cloud
LOG_LEVEL=WARNING

# Django API Backend
API_RATE_LIMIT=100
API_TIMEOUT=30
CORS_ALLOWED_ORIGINS=https://site.structa.cloud,https://www.site.structa.cloud

# PostgreSQL
POSTGRES_USER=prod_user
POSTGRES_PASSWORD=<generate-secure-random-password>
INITDB_MULTIPLE_DATABASES=frontend_db,api_db

# Nginx Reverse Proxy
NGINX_HOST=structa.cloud
NGINX_PORT=80
NGINX_WORKER_PROCESSES=auto
NGINX_WORKER_CONNECTIONS=4096

# Docsify
DOCS_CACHE_ENABLED=True
DOCS_CACHE_DURATION=86400
DOCS_GZIP_ENABLED=True

# LMS
LMS_MAINTENANCE_MESSAGE=Learning Management System - Coming Soon
```

**Characteristics:**
- Debug mode disabled
- SSL/TLS enforcement enabled
- Minimal logging for performance
- Maximum security settings
- Strict rate limiting
- Long cache durations for performance
- Secure, randomly generated secrets

---

## Security Considerations

### Sensitive Variables

The following variables contain sensitive information and require special handling:

#### `SECRET_KEY`
- **Risk:** If exposed, attackers can forge session tokens and CSRF tokens
- **Mitigation:**
  - Generate using cryptographically secure random generator
  - Store in secure secrets management system (AWS Secrets Manager, HashiCorp Vault)
  - Never commit to version control
  - Rotate periodically (at least annually)
  - Use different keys for each environment

#### `POSTGRES_PASSWORD`
- **Risk:** If exposed, attackers can access the database
- **Mitigation:**
  - Use strong passwords (12+ characters, mixed case, numbers, symbols)
  - Store in secure secrets management system
  - Never commit to version control
  - Rotate periodically (at least quarterly)
  - Use different passwords for each environment
  - Implement database access controls

#### `DATABASE_URL`
- **Risk:** Contains credentials for database access
- **Mitigation:**
  - Store in secure secrets management system
  - Never commit to version control
  - Use environment-specific credentials
  - Implement database access controls
  - Monitor database access logs

### Best Practices

1. **Use Secrets Management System**
   - AWS Secrets Manager
   - HashiCorp Vault
   - Azure Key Vault
   - Never store secrets in version control

2. **Environment Isolation**
   - Use separate credentials for each environment
   - Implement role-based access control
   - Restrict who can view environment variables

3. **Secret Rotation**
   - Rotate secrets periodically
   - Implement automated rotation where possible
   - Document rotation procedures

4. **Audit and Monitoring**
   - Log all access to environment variables
   - Monitor for unauthorized access attempts
   - Alert on suspicious activity

5. **Secure Communication**
   - Use HTTPS for all communications
   - Enforce SSL/TLS in production
   - Use secure headers (HSTS, CSP, etc.)

6. **Access Control**
   - Implement principle of least privilege
   - Restrict environment variable access
   - Use role-based access control

### Production Security Checklist

- [ ] All `SECRET_KEY` values are unique and randomly generated
- [ ] All passwords are strong (12+ characters, mixed case, numbers, symbols)
- [ ] `DEBUG=False` in production
- [ ] `SECURE_SSL_REDIRECT=True` in production
- [ ] `SESSION_COOKIE_SECURE=True` in production
- [ ] `CSRF_COOKIE_SECURE=True` in production
- [ ] All sensitive variables stored in secrets management system
- [ ] No secrets committed to version control
- [ ] Database credentials are environment-specific
- [ ] Access to environment variables is restricted
- [ ] Audit logging is enabled
- [ ] Monitoring and alerting are configured

---

## Loading Environment Variables

### Using .env Files

Create a `.env` file in the project root:

```bash
cp .env.example .env
# Edit .env with environment-specific values
```

### Docker Compose

Environment variables are loaded from `.env` file:

```bash
docker-compose up
```

### Manual Loading

```python
import os
from dotenv import load_dotenv

load_dotenv()

DEBUG = os.getenv('DEBUG', 'False') == 'True'
SECRET_KEY = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
```

### Django Settings

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
        'NAME': os.getenv('DB_NAME', 'frontend_db'),
        'USER': os.getenv('DB_USER', 'user'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}
```

---

## Troubleshooting

### Common Issues

**Issue:** "SECRET_KEY not set"
- **Solution:** Ensure `SECRET_KEY` is defined in `.env` file or environment

**Issue:** "Database connection refused"
- **Solution:** Verify `DATABASE_URL` is correct and PostgreSQL service is running

**Issue:** "Host header mismatch"
- **Solution:** Ensure `ALLOWED_HOSTS` matches the domain in the request

**Issue:** "CSRF token validation failed"
- **Solution:** Verify `CSRF_TRUSTED_ORIGINS` includes the request origin

**Issue:** "SSL certificate error"
- **Solution:** Verify SSL certificates are properly configured in reverse proxy

---

## Related Documentation

- [Docker Compose Setup](01-docker-compose-setup.md)
- [Nginx Reverse Proxy Setup](03-nginx-reverse-proxy-setup.md)
- [Production Deployment Checklist](04-production-deployment-checklist.md)
- [Troubleshooting Guide](06-troubleshooting.md)
- [Architecture Documentation](architecture.md)

