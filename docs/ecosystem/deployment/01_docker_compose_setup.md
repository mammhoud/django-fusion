# Docker Compose Setup

## Overview

Docker Compose provides a simple way to run the entire application stack locally or in production.

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- 10GB disk space

## Configuration

### docker-compose.yml

The main configuration file defines all services:

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=True
      - DATABASE_URL=postgresql://user:password@db:5432/xellent
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=xellent_user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=xellent
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

## Starting Services

### Start All Services

```bash
docker-compose up -d
```

### Start Specific Service

```bash
docker-compose up -d web
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web

# Last 100 lines
docker-compose logs --tail=100
```

## Stopping Services

### Stop All Services

```bash
docker-compose down
```

### Stop Specific Service

```bash
docker-compose stop web
```

### Remove Volumes

```bash
docker-compose down -v
```

## Running Commands

### Django Management Commands

```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Collect static files
docker-compose exec web python manage.py collectstatic
```

### Database Commands

```bash
# Open database shell
docker-compose exec db psql -U postgres -d xellent

# Create backup
docker-compose exec db pg_dump -U postgres xellent > backup.sql

# Restore backup
docker-compose exec -T db psql -U postgres xellent < backup.sql
```

## Service Configuration

### Web Service

```yaml
web:
  build: .
  ports:
    - "8000:8000"
  environment:
    - DEBUG=True
    - SECRET_KEY=your-secret-key
    - DATABASE_URL=postgresql://user:password@db:5432/xellent
  volumes:
    - .:/app
  depends_on:
    - db
    - redis
```

### Database Service

```yaml
db:
  image: postgres:15
  environment:
    - POSTGRES_USER=xellent_user
    - POSTGRES_PASSWORD=password
    - POSTGRES_DB=xellent
  volumes:
    - postgres_data:/var/lib/postgresql/data
  ports:
    - "5432:5432"
```

### Redis Service

```yaml
redis:
  image: redis:7
  ports:
    - "6379:6379"
  volumes:
    - redis_data:/data
```

## Networking

Services communicate via service names:

```python
# In Django settings
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'xellent',
        'USER': 'xellent_user',
        'PASSWORD': 'password',
        'HOST': 'db',  # Service name
        'PORT': '5432',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis:6379/0',  # Service name
    }
}
```

## Volumes

### Named Volumes

```yaml
volumes:
  postgres_data:
  redis_data:
```

### Bind Mounts

```yaml
volumes:
  - .:/app  # Current directory to /app in container
  - ./data:/data
```

## Environment Variables

### .env File

```env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:password@db:5432/xellent
REDIS_URL=redis://redis:6379/0
```

### In docker-compose.yml

```yaml
environment:
  - DEBUG=${DEBUG}
  - SECRET_KEY=${SECRET_KEY}
  - DATABASE_URL=${DATABASE_URL}
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs web

# Rebuild image
docker-compose build --no-cache

# Remove and restart
docker-compose down -v
docker-compose up -d
```

### Port Already in Use

```bash
# Change port in docker-compose.yml
ports:
  - "8001:8000"  # Use different port

# Or kill process
lsof -i :8000
kill -9 <PID>
```

### Database Connection Error

```bash
# Check if database is running
docker-compose ps

# Check database logs
docker-compose logs db

# Restart database
docker-compose restart db
```

## Related Documentation

- [Environment Configuration](02-environment-configuration.md)
- [Production Deployment Checklist](04-production-deployment-checklist.md)
- [Installation Guide](../getting-started/01-installation-guide.md)
