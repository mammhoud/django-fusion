# Structa Cloud – Deployment Guide

## Quick Start

```bash
# Deploy all services in correct dependency order
make deploy

# Or specific components
make deploy-app          # Applications only
make deploy-proxy        # Reverse proxy only
make deploy-databases    # PostgreSQL + Redis
```

## Deployment Commands Tree

### 🚀 Main Deployment Commands

```
make deploy              # Full deployment (default postgres-first order)
├── make deploy-databases   # PostgreSQL, Redis
├── make deploy-coder       # Coder IDE platform
├── make deploy-media       # Nginx media server
├── make deploy-app         # Django applications
├── make deploy-tasks       # Celery workers
├── make deploy-docs        # Documentation site
└── make deploy-proxy       # Traefik reverse proxy
```

### 📋 Preflight & Validation

```
make deploy-ci           # CI gate (no deploy, validation only)
make deploy-preflight    # Smoke-test compose files
make preflight-network   # Validate network names
make create-networks     # Create Docker networks (idempotent)
```

### 🔧 Component-Specific Deployment

```
make deploy-app          # Build and start all Django applications
make deploy-proxy        # Deploy Traefik reverse proxy
make deploy-media        # Deploy Nginx media server
make deploy-tasks        # Start Celery background workers
make deploy-docs         # Deploy documentation (Docsify)
make deploy-databases    # Deploy PostgreSQL and Redis
make deploy-coder        # Deploy Coder IDE platform
make deploy-customizer   # Deploy template customizer
```

### 🐳 Coolify Management (Separate Stack)

```
make deploy-coolify           # Full Coolify deployment
make restart-coolify          # Restart Coolify service
make build-coolify            # Rebuild Coolify images
make list-coolify             # List Coolify containers
make upgrade-coolify          # Upgrade to latest Coolify
make upgrade-postgres-coolify # Upgrade Coolify's internal Postgres
make start-coolify / stop-coolify # Service control
```

### 📊 Management & Monitoring

```
make status              # Show deployment status
make logs                # Show logs from all services
make logs-common         # Stream Coolify logs (follow mode)
make stop                # Stop all services
make restart             # Restart all services
```

### 🧹 Maintenance & Cleanup

```
make prune               # Remove stopped containers + volumes + images
make prune-containers    # Remove only stopped containers
make prune-volumes       # Remove only unused volumes
make prune-images        # Remove only unused images
make clean               # Aggressive teardown (containers, volumes, images)
```

### 🔐 Certificate Management

```
make cert-generate       # Generate self-signed certificates
make cert-backup         # Backup current certificates
make cert-restore        # Restore from backup
make cert-validate       # Validate certificate/key pairs
make cert-check          # Check certificate expiry status
```

### 🔨 Build Commands

```
make build               # Build all components
make build-app           # Build application images
make build-media         # Build media server image
make build-docs          # Build documentation image
make build-customizer    # Build customizer webpack bundles
```

### 🌐 Per-Site Shortcuts

```
make ctc-research        # CTC Research site commands (delegates to applications/Makefile)
make structa             # Structa main site commands
make vresume             # VResume site commands
```

### 📦 Component Makefiles

```
make proxy               # Run proxy/Makefile targets
make databases           # Run databases/Makefile targets
make services            # Run services/Makefile targets
make customizer          # Run applications/customizer/Makefile targets
```

### 🔄 Git Operations

```
make push                # Push full repo + all lib submodules
make push-libs           # Push all local library submodules
make push-lib LIB=django-fusion  # Push single library
make pull                # Fetch + smart-merge from origin
make sync                # Pull then push in one command
```

### 📈 Versioning

```
make bump-action-patch   # Bump deploy-preflight action (patch version)
make bump-action-minor   # Bump deploy-preflight action (minor version)
make bump-action-major   # Bump deploy-preflight action (major version)
make bump-app-patch      # Bump applications version (patch)
make bump-app-minor      # Bump applications version (minor)
make bump-app-major      # Bump applications version (major)
```

### ℹ️ Help Commands

```
make help                # Show main command reference
make help-all            # Show all commands + component-specific help
```

## Deployment Order & Strategy

### Default: `postgres-first` (Recommended)

```
1. PostgreSQL + Redis     # All apps depend on DB
2. Coder IDE              # Depends on: postgres (healthy)
3. Nginx media server     # Required for Django apps
4. Django applications    # Need DB + media storage
5. Celery task workers    # Depend on: Django + Redis
6. Documentation site     # Independent
7. Traefik reverse proxy  # Last so apps register labels
```

**Why this order?**
- Database-first ensures all dependent services don't crash on startup
- Media server ready before apps try to mount upload volumes
- Proxy last so apps + media publish their labels correctly

### Legacy: `legacy` (Not Recommended)

```
1. Proxy
2. Applications
3. Media
4. Tasks
5. Documentation
6. Databases
```

**Warning:** Django apps will likely crash on first boot waiting for DB.

### Override Deployment Order

```bash
# Use postgres-first (default, recommended)
make deploy DEPLOY_ORDER=postgres-first

# Use legacy order (not recommended, but supported)
make deploy DEPLOY_ORDER=legacy
```

## Common Workflows

### Fresh Deployment

```bash
# 1. Validate configuration (CI gate)
make deploy-ci

# 2. Create networks + preflight checks
make preflight-network
make deploy-preflight

# 3. Deploy everything
make deploy
```

### Redeploy a Single Site

```bash
# Redeploy CTC Research only
make ctc-research docker-up

# Redeploy LMS Demo only
make lms-demo docker-up

# Redeploy VResume only
make vresume docker-up
```

### Redeploy Applications (All Sites)

```bash
# Rebuild and start all Django applications
make deploy-app
```

### Stop and Restart All Services

```bash
# Stop everything
make stop

# Restart from scratch
make deploy
```

### View Deployment Status

```bash
# Show which services are running
make status

# Stream logs from all services
make logs

# Follow Coolify logs (streaming)
make logs-common
```

### Clean Up Old Resources

```bash
# Remove stopped containers (safe)
make prune-containers

# Remove unused volumes (⚠️ data loss possible)
make prune-volumes

# Remove unused images (safe)
make prune-images

# Full aggressive cleanup (⚠️ resets everything)
make clean
```

## Environment Variables

### Deployment Configuration

```bash
# Override deployment order (default: postgres-first)
DEPLOY_ORDER=postgres-first
DEPLOY_ORDER=legacy

# Git operations (stored in .env or environment)
GITHUB_TOKEN=ghp_xxxxxxxxxxxxx
export GITHUB_TOKEN

# Pull mode for `make pull` (default: rebase)
PULL_MODE=rebase      # Rebase local onto remote
PULL_MODE=merge       # Create merge commit

# Sync configuration
SYNC_MODE=rebase      # Rebase during sync
SYNC_SKIP_PUSH=1      # Pull only, don't push
```

## Docker Compose File Tree

```
docker-compose.yml (root)
├── databases/docker-compose.yml
├── proxy/docker-compose.yml
└── compose/docker-compose.applications.yml
    ├── applications/ctc-research/docker-compose.yml
    ├── applications/lms-demo/docker-compose.yml
    ├── applications/VResume/docker-compose.yml
    ├── applications/crm/docker-compose.yml
    └── (applications/customizer/docker-compose.yml — commented out)

Additional compose files (optional):
├── compose/docker-compose.docs.yml
├── compose/docker-compose.tasks.yml
├── services/docker-compose.media.yml
└── source/docker-compose.yml (Coolify, if installed)
```

## Networks

All services use these Docker networks (created by `make create-networks`):

```
common              # Default network for most services
traefik-net         # Proxy-specific network
internal            # Internal services (no external access)
utilities-net       # Monitoring stack
warehouse-net       # Data warehouse services
ollama-net          # AI/ML services (Ollama)
```

## Volumes

Persistent data stored in:

```
postgres_data       # PostgreSQL database files
redis_data          # Redis cache
crm-static          # CRM static files
crm-media           # CRM user uploads
customizer-static   # Customizer static assets
customizer-media    # Customizer media
customizer-data     # Customizer database
```

## Services & Ports

```
ctc-research-website    localhost:5070      CTC Research Django app
lms-demo-website        localhost:5071      LMS Demo Django app
vresume-website         localhost:5072      VResume Django app
shared-media            localhost:8080      Nginx media server
default-proxy           localhost:443       Traefik reverse proxy (HTTPS)
postgres                5432                PostgreSQL database
redis                   6379                Redis cache
```

## Troubleshooting

### Preflight Failures

```bash
# Validate compose files without deploying
make deploy-ci

# Check network names
make preflight-network

# Check DEPLOY_ORDER
make deploy DEPLOY_ORDER=postgres-first   # Explicit order
```

### Service Won't Start

```bash
# Check service logs
make logs

# Check service status
make status

# Try explicit component deployment
make deploy-databases    # or deploy-app, deploy-proxy, etc.
```

### Out of Disk Space

```bash
# Remove stopped containers
make prune-containers

# Remove unused volumes (⚠️ data loss)
make prune-volumes

# Remove unused images
make prune-images
```

### Need to Rebuild Services

```bash
# Rebuild all components
make build

# Rebuild specific component
make build-app
make build-proxy
make build-media
```

## Git Workflow

### Push Changes

```bash
# Push all changes to origin
make push

# This will:
# 1. Push main repo to origin
# 2. Push each library submodule to its GitHub repo
```

### Pull Changes

```bash
# Pull from origin (auto-rebase if branches diverged)
make pull

# Pull with merge strategy instead of rebase
make pull PULL_MODE=merge

# Pull without auto-stash (if you want manual conflict resolution)
make pull PULL_MODE=merge
```

### Sync with Origin

```bash
# Pull then push in one command
make sync

# Pull with merge, then push
make sync SYNC_MODE=merge

# Pull only (don't push back)
make sync SYNC_SKIP_PUSH=1
```

## Versioning & Releases

### Bump Deployment Action Version

```bash
make bump-action-patch    # v1.0.0 → v1.0.1
make bump-action-minor    # v1.0.0 → v1.1.0
make bump-action-major    # v1.0.0 → v2.0.0
```

### Bump Applications Version

```bash
make bump-app-patch       # applications version
make bump-app-minor
make bump-app-major
```

### Verify Release

```bash
# Sanity-check published Composite Action
make verify-release       # Checks v1.0.0 (default)
make verify-release TAG=v1.1.0-rc1  # Check specific tag
```

## See Also

- **Root Makefile**: `/home/structa.cloud/Makefile`
- **Applications Makefile**: `/home/structa.cloud/applications/Makefile`
- **Proxy Makefile**: `/home/structa.cloud/proxy/Makefile`
- **Databases Makefile**: `/home/structa.cloud/databases/Makefile`
- **Infrastructure Guide**: `/home/structa.cloud/docs/infrastructure/INFRASTRUCTURE_GUIDE.md`
- **Project AGENTS.md**: `/home/structa.cloud/AGENTS.md`

