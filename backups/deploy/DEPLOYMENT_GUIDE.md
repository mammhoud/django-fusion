# Structa Cloud Deployment Guide

## Directory Structure

```
/data/deploy/
├── Makefile                    # Central deployment Makefile
├── applications/               # Django application services
│   ├── Makefile               # Application-specific commands
│   ├── docker-compose.yml     # Main website services
│   ├── docker-compose.tasks.yml # Celery workers & schedulers
│   ├── docker-compose.docs.yml # Documentation service
│   └── django/
│       ├── Dockerfile         # Shared Django/Uvicorn container
│       ├── entrypoint         # Container entrypoint script
│       ├── start              # Server startup script
│       ├── flower             # Celery Flower monitoring
│       └── rqworker-start     # RQ worker startup
├── proxy/                      # Reverse proxy configuration
│   ├── Makefile               # Proxy management commands
│   ├── traefik.yml            # Traefik static configuration
│   ├── docker-compose.traefik.yml
│   ├── docker-compose.nginx.yml
│   ├── docker-compose.caddy.yml
│   ├── dynamic/               # Traefik dynamic configurations
│   │   ├── ctc-research.yml
│   │   ├── structa-cloud.yml
│   │   ├── vresume.yml
│   │   ├── media-servers.yml
│   │   ├── middlewares.yml
│   │   └── dashboard.yml
│   ├── certs/                 # SSL certificates
│   └── scripts/               # Certificate management scripts
├── services/                   # Additional services
│   ├── Makefile               # Service management commands
│   ├── docker-compose.media.yml
│   ├── media/
│   │   ├── Dockerfile
│   │   ├── nginx.conf
│   │   └── entrypoint.sh
│   └── ollama/
│       ├── docker-compose.yml
│       └── docker-compose.full.yml
├── source/                     # Coolify source deployment
│   ├── Makefile               # Source deployment commands
│   ├── docker-compose.yml
│   └── docker-compose.prod.yml
└── compose/                    # Shared compose files
    ├── django/                # Django Dockerfile (copy)
    ├── media/                 # Media Dockerfile (copy)
    └── docs/                  # Docs Dockerfile
```

## Quick Start

```bash
# Deploy everything
make deploy:all

# Deploy specific components
make deploy:app      # Application services
make deploy:proxy    # Reverse proxy
make deploy:media    # Media server
make deploy:tasks    # Background workers

# Check status
make status

# View logs
make logs

# Stop all services
make stop
```

## Path Reference

### Dockerfile Paths
All Dockerfiles now use consistent paths from the workspace root:

| Service | Dockerfile Path | Build Context |
|---------|----------------|---------------|
| Django Apps | `applications/django/Dockerfile` | `..` (workspace root) |
| Media Server | `services/media/Dockerfile` | `../..` (workspace root) |
| Docs | `compose/docs/Dockerfile` | `..` (deploy root) |

### Volume Mount Paths
All volume mounts in compose files use relative paths from their location:

```yaml
# From applications/docker-compose.yml
volumes:
  - ../configs:/app/configs:z
  - ../assets:/app/assets:z
  - ../ctc-research:/app/ctc-research:z

# From services/docker-compose.media.yml
volumes:
  - ../../assets/staticfiles:/var/www/static:ro
  - ../../assets/media:/var/www/media:ro
```

### Configuration Paths
- **Traefik Config**: `/data/coolify/proxy/` (live), `deploy/proxy/` (source)
- **Dynamic Routes**: `deploy/proxy/dynamic/*.yml`
- **Certificates**: `deploy/proxy/certs/`
- **ACME Storage**: `/traefik/acme/acme.json`

## Website Services

### ctc-research-website
- **Container**: `ctc-research-website`
- **Port**: 5070
- **Domains**: `ctc-research.com`, `www.ctc-research.com`, `arch.ctc-research.com`
- **Database**: `db_ctc`

### lms-demo-website
- **Container**: `lms-demo-website`
- **Port**: 5071
- **Domains**: `structa.cloud`, `www.structa.cloud`, `core.structa.cloud`
- **Database**: `db_structa`
- **Profile**: `lms`

### vresume-website
- **Container**: `vresume-website`
- **Port**: 5072
- **Domains**: `vresume.structa.cloud`, `resume.structa.cloud`
- **Database**: `vresume`
- **Profile**: `vresume`

## Certificate Management

```bash
# Generate self-signed certificates
make cert:generate

# Check certificate expiry
make cert:check

# Backup certificates
make cert:backup

# Restore from backup
make cert:restore

# Validate certificates
make cert:validate
```

## Traefik Routes

### Main Sites
- `ctc-research.com` → `ctc-research-website:5070`
- `structa.cloud` → `lms-demo-website:5071`
- `vresume.structa.cloud` → `vresume-website:5072`

### Media Servers
- `media.structa.cloud` → `shared-media:80`
- `media.ctc-research.com` → `shared-media:80`
- `media.vresume.structa.cloud` → `shared-media:80`

### Dashboard
- `traefik.structa.cloud` → Traefik dashboard (basic auth required)

## Environment Variables

Key environment variables are defined in:
- `deploy/source/.env` - Coolify configuration
- `deploy/source/.env.production` - Production overrides
- Workspace `.env` - Application settings

### Required Variables
```bash
DB_HOST=structa-db
DB_PORT=5432
DB_USER=structa
DB_PASSWORD=<password>
REDIS_URL=redis://:<password>@structa-cache:6379/0
CELERY_BROKER_URL=redis://:<password>@structa-cache:6379/1
```

## Makefile Commands Reference

### Root Makefile (`/data/deploy/Makefile`)

| Command | Description |
|---------|-------------|
| `make help` | Show all available commands |
| `make deploy:all` | Deploy all services |
| `make deploy:app` | Deploy application services |
| `make deploy:proxy` | Deploy reverse proxy |
| `make deploy:media` | Deploy media server |
| `make status` | Show deployment status |
| `make logs` | Show service logs |
| `make stop` | Stop all services |
| `make restart` | Restart all services |
| `make build` | Build all images |
| `make validate` | Validate configuration files |

### Application Makefile (`/data/deploy/applications/Makefile`)

| Command | Description |
|---------|-------------|
| `make up` | Start application services |
| `make down` | Stop application services |
| `make build` | Build application images |
| `make start:ctc` | Start ctc-research website |
| `make start:lms` | Start lms-demo website |
| `make start:vresume` | Start vresume website |
| `make tasks` | Start background workers |
| `make docs` | Start documentation service |

### Proxy Makefile (`/data/deploy/proxy/Makefile`)

| Command | Description |
|---------|-------------|
| `make deploy` | Deploy proxy configuration |
| `make validate` | Validate YAML configs |
| `make backup` | Backup configuration |
| `make restore` | Restore from backup |
| `make restart` | Restart proxy |
| `make status` | Show proxy status |
| `make cert:generate` | Generate certificates |
| `make cert:check` | Check certificate expiry |

### Services Makefile (`/data/deploy/services/Makefile`)

| Command | Description |
|---------|-------------|
| `make media` | Start media server |
| `make ollama` | Start Ollama (minimal) |
| `make ollama:full` | Start Ollama + WebUI |
| `make build:media` | Build media server |

### Source Makefile (`/data/deploy/source/Makefile`)

| Command | Description |
|---------|-------------|
| `make deploy` | Deploy Coolify |
| `make deploy:prod` | Deploy in production mode |
| `make upgrade` | Upgrade Coolify |
| `make backup` | Backup Coolify data |
| `make status` | Show Coolify status |

## Troubleshooting

### Check Service Health
```bash
make status
docker ps --filter name=structa-
docker ps --filter name=coolify-
```

### View Logs
```bash
make logs
docker logs ctc-research-website --tail 100 -f
docker logs coolify-proxy --tail 100 -f
```

### Restart Services
```bash
make restart
# Or individual services
docker restart ctc-research-website
docker restart coolify-proxy
```

### Rebuild Images
```bash
make build
# Or with no cache
docker compose build --no-cache
```

### Validate Configuration
```bash
make validate
docker compose config
```
