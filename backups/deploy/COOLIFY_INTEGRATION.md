# Coolify Integration - Complete Configuration

## Overview

This document describes the complete Coolify integration with relative paths, custom compose overrides, and centralized configuration management.

## Directory Structure

```
/data/
├── coolify/                    # Coolify installation (primary deployment)
│   ├── source/                 # Coolify source deployment (primary)
│   │   ├── Makefile           # Coolify management commands
│   │   ├── .env               # Environment variables (enhanced)
│   │   ├── .env.production    # Production overrides
│   │   ├── docker-compose.yml     # Base Compose (relative paths)
│   │   ├── docker-compose.prod.yml # Production overrides
│   │   └── docker-compose.custom.yml # Custom overrides (persistent)
│   ├── applications/           # Deployed applications
│   ├── databases/              # Database backups
│   ├── services/               # Service configurations
│   ├── backups/                # Coolify backups
│   ├── ssh/                    # SSH keys
│   └── ssl/                    # SSL certificates
└── deploy/                     # Deployment configuration (source of truth)
    ├── source/                 # Source deployment (mirrors to coolify)
    │   ├── Makefile           # Management commands
    │   ├── .env               # Environment variables
    │   ├── .env.production    # Production overrides
    │   ├── docker-compose.yml     # Base Compose
    │   ├── docker-compose.prod.yml # Production overrides
    │   ├── docker-compose.custom.yml # Custom overrides
    │   ├── utilities/         # Monitoring & logging utilities
    │   └── warehouses/        # Warehouse databases
    ├── applications/           # Application compose files
    ├── proxy/                  # Reverse proxy configuration
    └── services/               # Service configurations
```

## Relative Path Configuration

### Environment Variables (`.env`)

All paths use relative naming and can be overridden by environment variables:

```bash
# Data Directory (defaults to /data/coolify)
DATA_DIR=/data/coolify

# Database paths (use relative names)
DB_HOST=coolify-db
DB_PORT=5432

# Redis paths
REDIS_PASSWORD=<password>

# Application settings
APP_PORT=8000
APP_URL=http://localhost:8000
```

### Docker Compose Paths

All volume mounts use relative paths:

```yaml
volumes:
  - type: bind
    source: .env
    target: /var/www/html/.env
    read_only: true
  - ${DATA_DIR:-/data/coolify}/ssh:/var/www/html/storage/app/ssh
  - ${DATA_DIR:-/data/coolify}/applications:/var/www/html/storage/app/applications
  - ${DATA_DIR:-/data/coolify}/databases:/var/www/html/storage/app/databases
  - ${DATA_DIR:-/data/coolify}/services:/var/www/html/storage/app/services
  - ${DATA_DIR:-/data/coolify}/backups:/var/www/html/storage/app/backups
```

### Networks

Two networks are created:
- `coolify` - External network for proxy connectivity
- `coolify-internal` - Internal network for database/redis communication

## Custom Compose Overrides (`docker-compose.custom.yml`)

### Purpose

Per [Coolify documentation](https://coolify.io/docs/knowledge-base/custom-compose-overrides), this file:
- Is **NOT** overwritten during Coolify upgrades
- Allows persistent customizations
- Is automatically merged with base compose files

### Merge Order

Docker Compose merges files in order (later overrides earlier):
1. `docker-compose.yml` (base)
2. `docker-compose.override.yml` (development)
3. `docker-compose.prod.yml` (production)
4. `docker-compose.custom.yml` (your customizations)

### Customization Examples

The `docker-compose.custom.yml` includes:

#### 1. Enhanced Health Checks
```yaml
services:
  coolify:
    healthcheck:
      test: ["CMD-SHELL", "curl --fail http://127.0.0.1:8080/api/health || exit 1"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 60s
```

#### 2. Additional Networks
```yaml
services:
  coolify:
    networks:
      - coolify
      - internal
```

#### 3. Internal Network
```yaml
networks:
  internal:
    name: coolify-internal
    driver: bridge
    internal: true
    external: false
```

#### 4. Extra Volumes
```yaml
volumes:
  coolify-db-backups:
    name: coolify-db-backups
  coolify-redis-backups:
    name: coolify-redis-backups
```

#### 5. Additional Soketi Metrics
```yaml
services:
  soketi:
    environment:
      SOKETI_METRICS_ENABLED: "true"
      SOKETI_METRICS_HTTP_PORT: "9601"
    ports:
      - "9601:9601"  # Metrics
```

## Usage

### Deployment

```bash
# Deploy Coolify from source (primary)
cd /data/coolify/source
make deploy

# Deploy in production mode
make deploy:prod

# Validate compose files
make validate

# Or use deploy/source as source of truth
cd /data/deploy/source
make deploy
```

### Environment Variables

Key variables to configure:

| Variable | Default | Description |
|----------|---------|-------------|
| `DATA_DIR` | `/data/coolify` | Data directory for Coolify |
| `APP_PORT` | `8000` | Application port |
| `DB_USERNAME` | `coolify` | Database username |
| `DB_PASSWORD` | *required* | Database password |
| `REDIS_PASSWORD` | *required* | Redis password |
| `SOKETI_PORT` | `6001` | Soketi WebSocket port |
| `PHP_MEMORY_LIMIT` | `512M` | PHP memory limit |

### Backup & Restore

```bash
# Backup Coolify data
make backup

# Restore from backup
make backup:restore
# Enter backup timestamp (e.g., 20260613_225231)
```

### Upgrades

```bash
# Upgrade Coolify (includes backup)
make upgrade

# Upgrade PostgreSQL only
make upgrade:postgres
```

### Management Commands

| Command | Description |
|---------|-------------|
| `make deploy` | Deploy Coolify |
| `make deploy:prod` | Deploy in production mode |
| `make validate` | Validate compose files |
| `make upgrade` | Upgrade Coolify |
| `make restart` | Restart Coolify services |
| `make stop` | Stop Coolify services |
| `make start` | Start Coolify services |
| `make status` | Show Coolify status |
| `make logs` | Show logs |
| `make logs:all` | Show all logs |
| `make backup` | Backup data |
| `make backup:restore` | Restore from backup |

## File Locations

| File | Path | Purpose |
|------|------|---------|
| Base Compose | `coolify/source/docker-compose.yml` | Base configuration (primary) |
| Production Overrides | `coolify/source/docker-compose.prod.yml` | Production settings |
| Custom Overrides | `coolify/source/docker-compose.custom.yml` | Persistent customizations |
| Environment | `coolify/source/.env` | Development settings |
| Production Env | `coolify/source/.env.production` | Production settings |
| Makefile | `coolify/source/Makefile` | Management commands |

## Source of Truth

The deployment configuration in `/data/deploy/source/` is the **source of truth**:
- All configuration files are developed here first
- Changes are synchronized to `/data/coolify/source/`
- Use `rsync` or `cp` to sync: `cp -r /data/deploy/source/* /data/coolify/source/`

## Network Architecture

```
coolify (external)
├── coolify container (proxy access)
└── soketi container (real-time)

coolify-internal (internal)
├── postgres container (database)
├── redis container (cache)
└── All internal communication only
```

## Environment Variable Precedence

1. `.env.production` (highest priority)
2. `.env`
3. Default values in `docker-compose.yml`
4. Built-in defaults

## Best Practices

1. **Use `docker-compose.custom.yml`** for all persistent customizations
2. **Never edit** `docker-compose.yml` or `docker-compose.prod.yml` directly
3. **Store secrets** in `.env` (git-ignored)
4. **Use relative paths** for portability
5. **Test upgrades** in staging first
6. **Maintain sync** from deploy/source (source of truth) to coolify/source

## Synchronization

To sync from deploy to coolify:

```bash
# Sync all source files (from deploy to coolify)
cp -r /data/deploy/source/* /data/coolify/source/

# Or using rsync (for incremental sync)
rsync -av /data/deploy/source/ /data/coolify/source/
```

## Troubleshooting

### Validate Configuration
```bash
make validate
docker compose -f docker-compose.yml config
```

### View Logs
```bash
make logs
docker compose -f docker-compose.yml logs
```

### Restart Services
```bash
make restart
docker compose -f docker-compose.yml restart
```

### Rebuild Images
```bash
docker compose -f docker-compose.yml build --no-cache
```

### Check Status
```bash
make status
docker ps --filter name=coolify-
```

## References

- [Coolify Custom Compose Overrides](https://coolify.io/docs/knowledge-base/custom-compose-overrides)
- [Docker Compose Multi-File](https://docs.docker.com/compose/production/)
- [Coolify Documentation](https://coolify.io/docs)
