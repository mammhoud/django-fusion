# Redis Cache Documentation

> Caching, session storage, and message brokering

## Overview

Redis provides high-performance caching, session management, and message queuing for the ecosystem.

## Configuration

```yaml
# docker-compose.yml
services:
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
```

## Usage

### Django Cache Configuration

```python
# settings.py
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://redis:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}
```

### Session Storage

```python
# settings.py
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
```

### Celery Configuration

```python
# settings.py
CELERY_BROKER_URL = "redis://redis:6379/1"
CELERY_RESULT_BACKEND = "redis://redis:6379/2"
CELERY_CACHE_BACKEND = "redis://redis:6379/3"
```

## Commands

```bash
# Connect to Redis
docker exec -it redis redis-cli

# Monitor Redis
docker exec -it redis redis-cli monitor

# Check memory usage
docker exec -it redis redis-cli info memory

# Clear cache
docker exec -it redis redis-cli flushall
```

## Related Documentation

- [Traefik Documentation](../traefik/)
- [PostgreSQL Documentation](../postgres/)
- [Docker Documentation](../docker/)
- [Main Infrastructure](../README.md)
