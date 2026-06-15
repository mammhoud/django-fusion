# Infrastructure Documentation

> Shared infrastructure components for the ecosystem

## Overview

This section contains documentation for the shared infrastructure used across all projects.

## Components

### Docker
Container configuration and management
- Docker Compose setup
- Container networking
- Volume management

**Key Files:**
- `docker-compose.yml` - Main compose file
- `compose/traefik/` - Traefik configuration
- `compose/nginx/` - Nginx configuration
- `compose/postgres/` - PostgreSQL configuration

### Nginx
Reverse proxy and static file serving
- [alliance-media.conf](nginx/alliance-media.conf) - Media serving
- [nginx.conf](nginx/nginx.conf) - Main config
- [docsify.conf](nginx/docsify.conf) - Docsify config

### Traefik
Modern reverse proxy and load balancer
- [traefik.yml](traefik/traefik.yml) - Main configuration
- [README.md](traefik/README.md) - Traefik documentation
- Dynamic configuration in `dynamic/` directory

### PostgreSQL
Database configuration and management
- [Dockerfile](postgres/Dockerfile) - Postgres image
- Init scripts in `init.d/` directory
- Maintenance scripts in `maintenance/` directory
- Backups in `backups/` directory

---

## Architecture

```
                    ┌─────────────┐
                    │   Traefik   │
                    │  (Port 80)  │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
        ┌─────┴─────┐ ┌────┴────┐ ┌─────┴─────┐
        │   Nginx   │ │  App 1  │ │   App 2   │
        │  (Static) │ │ (ctc)   │ │ (structa) │
        └───────────┘ └────┬────┘ └─────┬─────┘
                           │            │
                    ┌──────┴────────────┴──────┐
                    │       PostgreSQL         │
                    │      (Port 5432)         │
                    └──────────────────────────┘
```

## Docker Compose

The main `docker-compose.yml` orchestrates all services:

```yaml
services:
  traefik:
    # Reverse proxy (port 80, 443)
  nginx:
    # Static file serving
  postgres:
    # Database (port 5432)
  redis:
    # Cache (port 6379)
  ctc-research:
    # ctc-research.com application
  structa-cloud:
    # structa.cloud application
```

## Quick Commands

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f

# Stop all services
docker compose down

# Stop and remove volumes
docker compose down -v

# Rebuild images
docker compose build

# Rebuild specific service
docker compose build ctc-research
```

## Service-Specific Commands

```bash
# Start only PostgreSQL
docker compose up -d postgres

# View logs for specific service
docker compose logs -f postgres

# Restart specific service
docker compose restart nginx
```

## Health Checks

All services expose health check endpoints:
- `GET /health/` - Overall health
- `GET /health/database/` - Database connectivity
- `GET /health/assets/` - Static assets
- `GET /health/media/` - Media files

---

## Related Documentation

- [Deployment Guide](../ecosystem/deployment/)
- [Development Workflow](../ecosystem/development/)
- [Shared Scripts](../shared/scripts/)
