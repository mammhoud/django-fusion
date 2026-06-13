# Docker Compose Documentation

> Container orchestration for the Django multi-project ecosystem

## Overview

Docker Compose orchestrates all services including Traefik, Nginx, PostgreSQL, Redis, and both Django applications.

## Services

| Service | Image | Ports | Purpose |
|---------|-------|-------|---------|
| traefik | traefik:v3.0 | 80, 443 | Reverse proxy |
| nginx | nginx:alpine | 80 | Static files |
| postgres | postgres:15 | 5432 | Database |
| redis | redis:alpine | 6379 | Cache |
| ctc-research | ctc-research:latest | 8000 | CTC Research app |
| structa-cloud | structa-cloud:latest | 8001 | Structa Cloud app |

## Quick Start

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f

# Stop all services
docker compose down

# Stop and remove volumes
docker compose down -v
```

## Service Management

```bash
# Start specific service
docker compose up -d postgres

# Restart service
docker compose restart nginx

# View service logs
docker compose logs -f ctc-research

# Scale service
docker compose up -d --scale ctc-research=2
```

## Health Checks

All services expose health check endpoints:
- `GET /health/` - Overall health
- `GET /health/database/` - Database connectivity
- `GET /health/assets/` - Static assets
- `GET /health/media/` - Media files

## Environment Variables

```yaml
# docker-compose.yml environment
services:
  ctc-research:
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings.production
      - DATABASE_URL=postgres://user:pass@postgres:5432/ctc
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started

  structa-cloud:
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings.production
      - DATABASE_URL=postgres://user:pass@postgres:5432/structa
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started
```

## Volume Management

```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect site_postgres_data

# Remove unused volumes
docker volume prune
```

## Network Configuration

Services communicate over the `site_default` network:

```yaml
networks:
  default:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/24
```

## Related Documentation

- [Traefik Documentation](../traefik/)
- [Nginx Documentation](../nginx/)
- [PostgreSQL Documentation](../postgres/)
- [Main Infrastructure](../README.md)
