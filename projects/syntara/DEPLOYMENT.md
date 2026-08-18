# Tinker Deployment Guide

Complete deployment instructions for Tinker across different environments.

## Table of Contents

1. [Local Development](#local-development)
2. [Docker Compose](#docker-compose)
3. [Production Deployment](#production-deployment)
4. [Traefik Integration](#traefik-integration)
5. [Database Management](#database-management)
6. [Troubleshooting](#troubleshooting)

---

## Local Development

### Prerequisites

- Python 3.11+
- Node.js 18+
- pip / venv
- Optional: Ollama (for local AI models)

### Setup

```bash
# Navigate to cypercloud directory
cd projects/cypercloud

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate on Windows

# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
npm --prefix assets ci --legacy-peer-deps

# Create environment file (optional)
cp .env.example .env.dev
# Edit .env.dev if needed

# Apply migrations
python manage.py migrate

# Build frontend assets
make build

# Collect static files
make collectstatic

# Create superuser (optional, for /admin/)
python manage.py createsuperuser

# Run development server
make runserver
```

**Access:**
- Chat: http://localhost:5073
- Admin: http://localhost:5073/admin/ (if superuser created)

### Environment Variables

Create `.env.dev` (git-ignored):

```bash
# Django
TINKER_SECRET_KEY=your-random-secret-key-here
TINKER_DEBUG=1
TINKER_ALLOWED_HOSTS=localhost,127.0.0.1,.localhost

# Database (local SQLite)
# DATABASE_URL is not set; uses db.sqlite3

# Ollama (for local AI)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma3:4b

# Optional: Ceptor AI backends
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
```

### Verify Setup

```bash
# Check Django
python manage.py check

# Check migrations
python manage.py showmigrations

# Access shell
python manage.py shell

# Verify Ollama
curl http://localhost:11434/api/tags
```

---

## Docker Compose

### Build Image

```bash
# From projects/ directory
docker build -f cypercloud/Dockerfile -t cypercloud:latest .

# Or use docker-compose
docker-compose -f projects/cypercloud/docker-compose.yml build
```

### Run Service

```bash
# Start cypercloud service
docker-compose -f projects/cypercloud/docker-compose.yml up -d

# View logs
docker-compose -f projects/cypercloud/docker-compose.yml logs -f cypercloud

# Stop service
docker-compose -f projects/cypercloud/docker-compose.yml down

# Remove volumes (careful!)
docker-compose -f projects/cypercloud/docker-compose.yml down -v
```

### Environment Configuration

The docker-compose.yml sets environment variables:

```yaml
environment:
  TINKER_SECRET_KEY: ${TINKER_SECRET_KEY:-django-insecure-cypercloud-dev}
  TINKER_DEBUG: ${TINKER_DEBUG:-0}
  TINKER_ALLOWED_HOSTS: ${TINKER_ALLOWED_HOSTS:-localhost,127.0.0.1,cypercloud.localhost}
  TINKER_PORT: "5073"
  OLLAMA_BASE_URL: ${OLLAMA_BASE_URL:-http://host.docker.internal:11434}
  OLLAMA_MODEL: ${OLLAMA_MODEL:-gemma3:4b}
```

Override in your `.env` file at workspace root:

```bash
# .env
TINKER_SECRET_KEY=your-random-key-here
TINKER_DEBUG=0
TINKER_ALLOWED_HOSTS=cypercloud.localhost,cypercloud.example.com
OLLAMA_BASE_URL=http://ollama-service:11434
```

### Container Volumes

Persistent volumes (survive container restarts):

```yaml
volumes:
  cypercloud-data:           # SQLite database + uploads
  cypercloud-static:         # Collected static files
  cypercloud-media:          # User uploads
```

Access data:

```bash
# View database
docker exec cypercloud sqlite3 /app/cypercloud/db.sqlite3 ".tables"

# Backup database
docker exec cypercloud cp /app/cypercloud/data/db.sqlite3 /tmp/backup.db
docker cp cypercloud:/tmp/backup.db ./db.sqlite3.backup
```

---

## Production Deployment

### Pre-Deployment Checklist

- [ ] Generate strong `TINKER_SECRET_KEY`
- [ ] Set `TINKER_DEBUG=0`
- [ ] Configure allowed hosts: `TINKER_ALLOWED_HOSTS=cypercloud.example.com`
- [ ] Set up PostgreSQL (if scaling beyond SQLite)
- [ ] Configure SSL/TLS certificates via Traefik
- [ ] Set up logging and monitoring
- [ ] Configure backup strategy for database
- [ ] Test with staging environment

### Secret Management

**Generate Secret Key:**

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Store in secrets manager:
```bash
# Example using environment file
TINKER_SECRET_KEY=django-insecure-abc123...xyz
```

### Database Configuration

**Option 1: SQLite (for small deployments)**

```python
# settings.py (already configured)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": _SITE_DIR / "data" / "db.sqlite3",
    }
}
```

**Option 2: PostgreSQL (for large deployments)**

```bash
# Install psycopg2
pip install psycopg2-binary

# Set environment variable
DATABASE_URL=postgresql://user:password@postgres:5432/tinker_db

# Or edit settings.py:
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "tinker_db",
        "USER": "tinker_user",
        "PASSWORD": "secure_password",
        "HOST": "postgres-host",
        "PORT": "5432",
    }
}
```

### Security Settings

**settings.py:**

```python
# Production security
DEBUG = False
ALLOWED_HOSTS = os.getenv("TINKER_ALLOWED_HOSTS", "localhost").split(",")

# HTTPS/SSL
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {...}

# CORS (if needed)
CORS_ALLOWED_ORIGINS = [
    "https://cypercloud.example.com",
]
```

### Gunicorn Configuration

Production server configuration:

```bash
# In docker-compose.yml or entrypoint script
gunicorn \
  --bind 0.0.0.0:5073 \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --max-requests 1000 \
  --max-requests-jitter 100 \
  --access-logfile - \
  --error-logfile - \
  server:asgi_application
```

**Tuning:**
- `--workers`: 2-4 × CPU cores
- `--max-requests`: Auto-recycle workers (prevents memory leaks)
- `--timeout`: 60-120 seconds for long-running requests

---

## Traefik Integration

### Enable Traefik Routing

Create `applications/proxy/configs/traefik/dynamic/cypercloud.yml`:

```yaml
# Tinker router configuration
http:
  routers:
    cypercloud:
      rule: Host(`cypercloud.structa.cloud`)
      entrypoints:
        - websecure
      service: cypercloud
      tls:
        certResolver: letsencrypt
      middlewares:
        - security-headers

  services:
    cypercloud:
      loadBalancer:
        servers:
          - url: http://cypercloud:5073
        healthCheck:
          path: /
          interval: 30s
          timeout: 5s
```

### Enable HTTPS (Let's Encrypt)

Traefik configuration already includes HTTP-01 and DNS-01 challenges. Tinker will automatically get a certificate for `cypercloud.structa.cloud`.

**Verify:**

```bash
# Check certificate status
curl -I https://cypercloud.structa.cloud

# Should return 200 with valid certificate
```

### Networking

Tinker connects to two Docker networks:

```yaml
networks:
  common:        # Connects to other services (postgres, redis, etc.)
  traefik-net:   # Connects to Traefik proxy
```

Ensure networks exist:

```bash
docker network create common
docker network create traefik-net
```

---

## Database Management

### Initial Setup

```bash
# Apply migrations
docker-compose -f cypercloud/docker-compose.yml exec cypercloud python manage.py migrate

# Or locally
python manage.py migrate
```

### Backup Database

```bash
# Backup SQLite
docker exec cypercloud cp /app/cypercloud/data/db.sqlite3 /tmp/db.backup
docker cp cypercloud:/tmp/db.backup ./db.sqlite3.backup

# Backup PostgreSQL (if used)
docker exec postgres pg_dump -U tinker_user tinker_db > backup.sql
```

### Restore Database

```bash
# Restore SQLite
docker cp ./db.sqlite3.backup cypercloud:/tmp/db.backup
docker exec cypercloud cp /tmp/db.backup /app/cypercloud/data/db.sqlite3

# Restore PostgreSQL
docker exec -i postgres psql -U tinker_user tinker_db < backup.sql
```

### Create/Modify Schema

```bash
# Create new migration
python manage.py makemigrations

# Apply migration
python manage.py migrate

# Squash migrations (if needed)
python manage.py squashmigrations chat 0005
```

---

## Monitoring & Logs

### Application Logs

```bash
# Docker container logs
docker-compose -f cypercloud/docker-compose.yml logs cypercloud

# Follow logs in real-time
docker-compose -f cypercloud/docker-compose.yml logs -f cypercloud

# Last 100 lines
docker logs --tail 100 cypercloud
```

### Log Files (inside container)

```
/app/cypercloud/logs/
  ├── django.log         # Django application logs
  ├── build.log          # Asset build logs
  ├── deploy.log         # Deployment logs
  └── collectstatic.log  # Static file collection logs
```

### Health Check

```bash
# Application health
curl http://cypercloud:5073/

# Ceptor AI health
curl http://cypercloud:5073/api/ceptor/health/

# Django checks
python manage.py check
```

### Metrics

Consider adding monitoring tools:

```bash
# Prometheus (metrics)
docker pull prom/prometheus

# Grafana (visualization)
docker pull grafana/grafana

# ELK Stack (logging)
docker pull docker.elastic.co/elasticsearch/elasticsearch:latest
```

---

## Performance Tuning

### Database

**SQLite:**
- Fine for < 10,000 conversations
- Single file backup is simple
- No separate database server needed

**PostgreSQL:**
- Better for scaling
- Connection pooling support
- Advanced monitoring

### Caching

```python
# Add Redis caching (optional)
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# Cache templates (in templates view)
@cache_page(60 * 5)  # 5 minutes
def get_pages(...):
    ...
```

### Static File Delivery

**Development:** Django serves static files directly

**Production:** Use Nginx or CDN

```nginx
# Nginx configuration
location /static/ {
    alias /app/cypercloud/staticfiles/;
    expires 30d;
    add_header Cache-Control "public, immutable";
}

location /media/ {
    alias /app/cypercloud/assets/media/;
    expires 7d;
}
```

### Worker Configuration

Optimize Gunicorn workers based on CPU count:

```bash
# Get CPU count
nproc

# Gunicorn workers = (2 × CPU_count) + 1
# Example: 4 CPUs → 9 workers
```

---

## Disaster Recovery

### Backup Strategy

**Daily backups:**

```bash
#!/bin/bash
# backup-cypercloud.sh

BACKUP_DIR="/backups/cypercloud"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Backup database
docker exec cypercloud cp /app/cypercloud/data/db.sqlite3 /tmp/db.backup
docker cp cypercloud:/tmp/db.backup "$BACKUP_DIR/db_$TIMESTAMP.sqlite3"

# Backup media
docker cp cypercloud:/app/cypercloud/assets/media "$BACKUP_DIR/media_$TIMESTAMP"

# Keep last 30 days
find "$BACKUP_DIR" -mtime +30 -delete

echo "✅ Backup complete: $BACKUP_DIR"
```

**Schedule with cron:**

```bash
# crontab -e
0 2 * * * /scripts/backup-cypercloud.sh  # Daily at 2 AM
```

### Recovery Plan

**RTO (Recovery Time Objective):** < 1 hour
**RPO (Recovery Point Objective):** < 24 hours (daily backups)

**Steps:**

1. Stop cypercloud service: `docker-compose down`
2. Restore database from backup
3. Verify data integrity
4. Restart service: `docker-compose up -d`
5. Test critical functionality

---

## Troubleshooting

### "Module not found: configs"

**Issue:** Django can't find shared `configs` module during build

**Solution:** This is expected during Docker build (non-fatal). It will work at runtime because the Docker entrypoint sets correct paths.

```bash
# If issues persist at runtime:
export PYTHONPATH="/app/core:$PYTHONPATH"
python manage.py runserver
```

### "Connection refused" (Ollama)

**Issue:** Ollama service not accessible

**Check:**

```bash
# From container
docker exec cypercloud curl http://host.docker.internal:11434/api/tags

# From host
curl http://localhost:11434/api/tags
```

**Fix:** Update `OLLAMA_BASE_URL`:

```bash
# In docker-compose.yml or .env
OLLAMA_BASE_URL=http://host.docker.internal:11434  # For Docker Desktop
OLLAMA_BASE_URL=http://172.17.0.1:11434            # For Linux Docker
OLLAMA_BASE_URL=http://ollama-service:11434        # If Ollama in same network
```

### "Database is locked" (SQLite)

**Issue:** Multiple processes accessing db.sqlite3

**Fix:**

```bash
# Restart container
docker-compose restart cypercloud

# Or migrate to PostgreSQL for concurrent access
```

### "Static files not found" (404)

**Issue:** CSS/JS files return 404

**Solution:**

```bash
# Rebuild frontend
make build

# Collect static files
make collectstatic

# Verify files exist
ls -la staticfiles/
```

### "Ceptor AI not installed" (503)

**Issue:** ceptor-ai package not available

**Solution:** 

```bash
# Install in container
docker-compose exec cypercloud pip install ceptor-ai

# Or add to requirements.txt and rebuild
docker-compose build cypercloud
```

### "Template not loading"

**Issue:** Templates from configured sites not appearing

**Solution:**

```bash
# Verify site configuration
python manage.py shell
>>> from django.conf import settings
>>> settings.CUSTOMIZER_APPS

# Verify paths exist
ls -la projects/precis-ctc/templates/
ls -la projects/lms/templates/
ls -la projects/portfolio/www/pages/templates/

# Restart service
docker-compose restart cypercloud
```

---

## Maintenance

### Regular Tasks

- **Daily:** Check logs, monitor disk space
- **Weekly:** Review error logs, test backups
- **Monthly:** Update dependencies, review analytics
- **Quarterly:** Performance tuning, security audit

### Dependency Updates

```bash
# Check for outdated packages
pip list --outdated

# Update specific package
pip install --upgrade Django

# Update all requirements
pip install --upgrade -r requirements.txt

# Rebuild and test
make build
make check
```

### Zero-Downtime Deployment

```bash
# 1. Build new image
docker-compose -f cypercloud/docker-compose.yml build

# 2. Bring up new container (Traefik handles switching)
docker-compose -f cypercloud/docker-compose.yml up -d

# 3. Old container automatically stopped
```

---

## Support & Help

- **Logs:** `docker-compose logs cypercloud`
- **Health:** `curl http://cypercloud:5073/api/ceptor/health/`
- **Shell:** `docker-compose exec cypercloud python manage.py shell`
- **Documentation:** See `README.md` and `API.md`
