# Makefile Reference

**Last Updated:** June 7, 2026  
**Version:** Phase 12  
**Status:** Complete ✅  

---

## Overview

The root `Makefile` provides unified command interface for all development, build, and deployment tasks. It supports multiple websites (ctc-research, lms-demo, vresume) and delegates to sub-Makefiles for specialized tasks.

---

## Quick Start

### Basic Commands

```bash
# Show help and available targets
make help

# Check Django configuration
make check

# Run development server
make run-dev

# Run tests
make test

# Build frontend assets
make build-assets-all

# Docker: build and start services
make docker-up

# Docker: stop all services
make docker-down
```

### Website Selection

```bash
# Use WEBSITE variable to select site
make run-dev WEBSITE=ctc              # CTC Research
make run-dev WEBSITE=structa           # LMS Demo
make run-dev WEBSITE=vresume           # VResume

# Aliases supported
make run-dev WEBSITE=ctc-research      # Same as WEBSITE=ctc
make run-dev WEBSITE=lms-demo          # Same as WEBSITE=structa
make run-dev WEBSITE=VResume           # Same as WEBSITE=vresume
```

---

## Variable Reference

### Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `WEBSITE` | ctc | Selected website (ctc, structa, vresume) |
| `PYTHON` | .venv/bin/python | Python interpreter path |
| `LOG_DIR` | logs | Directory for log files |
| `SERVER_TYPE` | gunicorn | Server type (gunicorn, uvicorn) |
| `COMPOSE_FILE` | docker-compose.yml | Docker Compose file |

### Derived Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `SITE` | Internal site directory name | ctc-research, lms-demo, vresume |
| `TEST_WEBSITE` | Pytest website target | ctc, structa, vresume, all |
| `DOCKER_SERVICE` | Docker service name | ctc-research-website, etc. |
| `DOCKER_PROJECT_PATH` | Project directory path | ctc-research, lms-demo, VResume |
| `MANAGE` | Django manage.py command | uv run ctc-research |

---

## Category 1: Help & Information

### `make help`
Display all available targets and usage information.

```bash
make help
```

**Output:**
- Top-level targets list
- Website selection info
- Description of each target

---

## Category 2: Django Management

### `make check`
Run Django system checks for the selected website.

```bash
make check                    # Check current site (ctc)
make check WEBSITE=structa    # Check LMS Demo
```

**Purpose:** Verify Django configuration, model definitions, and setup.

### `make validate-config`
Validate Django configuration (if available).

```bash
make validate-config
```

**Purpose:** Additional configuration validation beyond standard checks.

### `make migrations`
Create Django migrations for model changes.

```bash
make migrations WEBSITE=ctc
```

**Output:** Creates new migration files in `*/migrations/`

### `make migrate`
Apply pending Django migrations.

```bash
make migrate WEBSITE=ctc
```

**Purpose:** Update database schema.

---

## Category 3: Development Server

### `make run-dev`
Start Django development server with auto-reload.

```bash
make run-dev                  # Run ctc-research dev server
make run-dev WEBSITE=structa  # Run lms-demo dev server
```

**Features:**
- Auto-reload on code changes
- Debug toolbar active
- Full traceback on errors

### `make server`
Start production ASGI server (default: gunicorn).

```bash
make server                        # Start with gunicorn
make server SERVER_TYPE=uvicorn    # Start with uvicorn
```

### `make server-gunicorn`
Start gunicorn ASGI server explicitly.

```bash
make server-gunicorn
```

### `make server-uvicorn`
Start uvicorn ASGI server.

```bash
make server-uvicorn
```

### `make rqworker`
Start RQ background job worker.

```bash
make rqworker
```

**Purpose:** Process background jobs (email, async tasks, etc.)

---

## Category 4: Asset Management

### `make build-assets`
Build frontend assets for selected website.

```bash
make build-assets              # Build ctc assets
make build-assets WEBSITE=vresume  # Build vresume assets
```

**Features:**
- Minification
- Source maps
- Tree-shaking
- Asset hashing

### `make build-assets-all`
Build frontend assets for all websites.

```bash
make build-assets-all
```

**Equivalent to:**
```bash
make build-assets WEBSITE=ctc
make build-assets WEBSITE=structa
make build-assets WEBSITE=vresume
```

### `make collectstatic-site`
Collect static files for selected website.

```bash
make collectstatic-site WEBSITE=ctc
```

**Purpose:** Gather all static files for production deployment.

**Output:** Files collected to `*/static/`

---

## Category 5: Database & Data

### `make migrate-site`
Run migrations for selected website.

```bash
make migrate-site WEBSITE=ctc
```

**Logs:**
- makemigrations output → `logs/makemigrations-ctc.log`
- migrate output → `logs/migrate-ctc.log`

### `make load-dumps-site`
Load fixture/dump data for selected website.

```bash
make load-dumps-site WEBSITE=structa
```

**Purpose:** Populate database with fixture data.

**Log:** `logs/load_dumped_data-structa.log`

### `make populate-data-site`
Populate site with test data.

```bash
make populate-data-site WEBSITE=vresume
```

**Log:** `logs/populate_site_data-vresume.log`

### `make populate-data-all`
Populate all websites with test data.

```bash
make populate-data-all
```

**Logs:**
- `logs/populate_site_data-ctc-research.log`
- `logs/populate_site_data-lms-demo.log`
- `logs/populate_site_data-vresume.log`

---

## Category 6: Testing

### `make test`
Run pytest for repo-level tests.

```bash
make test
```

**Default:** Runs tests in `tests/` directory

### `make tests-unit`
Run unit tests only.

```bash
make tests-unit
```

### `make tests-integration`
Run integration tests only.

```bash
make tests-integration
```

### `make tests-websites`
Run website-specific tests.

```bash
make tests-websites
```

### `make tests-website`
Run tests for specific website.

```bash
make tests-website WEBSITE=ctc      # Test ctc
make tests-website WEBSITE=structa  # Test structa
make tests-website WEBSITE=vresume  # Test vresume
make tests-website WEBSITE=all      # Test all
```

**Script:** `tests/scripts/run_website_tests.sh`

---

## Category 7: Docker Management

### Docker Build Commands

#### `make docker-build`
Build Docker image for selected website.

```bash
make docker-build              # Build ctc-research image
make docker-build WEBSITE=lms-demo  # Build lms-demo image
```

**Alias:** `make docker-build-server`

**Args:** Passes `PROJECT_PATH`, `WEBSITE`, `DJANGO_SITE`, `SERVER_TYPE`

#### `make docker-rebuild`
Rebuild Docker image without cache.

```bash
make docker-rebuild WEBSITE=ctc
```

**Purpose:** Fresh build, ignoring layer cache.

**Aliases:** `make rebuild`

#### `make docker-redeploy`
Build and restart selected service.

```bash
make docker-redeploy WEBSITE=structa
```

**Purpose:** Quick redeploy after code changes.

**Aliases:** `make docker-deploy`, `make deploy`, `make redeploy`

### Docker Runtime Commands

#### `make docker-up`
Build and start selected website containers.

```bash
make docker-up                      # Start ctc services
make docker-up WEBSITE=vresume      # Start vresume services
```

**Features:**
- Builds images if needed
- Starts service and dependencies
- Removes orphaned containers

#### `make docker-down`
Stop and remove selected website containers.

```bash
make docker-down WEBSITE=lms-demo
```

**Purpose:** Graceful shutdown.

#### `make docker-logs`
Follow logs for selected service.

```bash
make docker-logs              # Tail ctc logs
make docker-logs WEBSITE=structa  # Tail structa logs
```

**Default:** Last 200 lines, follows new output

### Docker Cleanup Commands

#### `make docker-prune-containers`
Remove stopped containers and orphans.

```bash
make docker-prune-containers
```

**Purpose:** Clean up disk space.

#### `make docker-prune-data`
Remove generated compose data.

```bash
make docker-prune-data
```

**Warning:** ⚠️ DANGEROUS - Removes database and volumes!

**Removes:**
- `applications/databases/postgres/backups/*`
- `applications/compose/data/*`

---

## Category 8: Docker Comprehensive Deployment

### `make docker-clean`
Clean all Docker containers and images.

```bash
make docker-clean
```

**Actions:**
- Stop all containers
- Remove orphaned containers
- Prune system (unused images, volumes, networks)

### `make docker-clean-all`
Aggressive clean - removes ALL Docker resources.

```bash
make docker-clean-all
```

**Actions:**
- Runs `docker-clean`
- Removes all images
- Removes all volumes

**Warning:** ⚠️ DESTRUCTIVE - Full reset required!

### `make docker-deploy-warehouse`
Deploy warehouse services (PostgreSQL, Redis, Adminer).

```bash
make docker-deploy-warehouse
```

**Services Started:**
- postgres
- redis
- adminer
- blinko

**Creates:** traefik-net network if needed

**Waits:** 10 seconds for services to become healthy

### `make docker-deploy-traefik`
Deploy Traefik reverse proxy.

```bash
make docker-deploy-traefik
```

**Features:**
- Creates traefik-net network
- Starts Traefik service
- Dashboard: http://localhost:8080

### `make docker-deploy-websites`
Build and deploy all three websites.

```bash
make docker-deploy-websites
```

**Sequence:**
1. Build ctc-research
2. Build lms-demo
3. Build vresume

**Purpose:** Deploy all applications in sequence.

### `make docker-deploy-full`
Full deployment: clean, build, deploy everything.

```bash
make docker-deploy-full
```

**Sequence:**
1. Clean all resources
2. Deploy warehouse
3. Deploy Traefik
4. Deploy websites

**Result:** Complete running system from scratch.

**Access Points:**
- Traefik Dashboard: http://localhost:8080
- CTC Research: http://ctc-research.local:5070
- LMS Demo: http://lms-demo.local:5071
- VResume: http://vresume.local:5072

### `make docker-status`
Show status of all Docker services.

```bash
make docker-status
```

**Output:**
- Running containers list
- Resource usage statistics

### `make docker-logs-all`
Show logs for all services.

```bash
make docker-logs-all
```

**Shows:** Last 50 lines from all containers

### `make docker-logs-service`
Show available services for logging.

```bash
make docker-logs-service
```

### `make docker-health-check`
Health check all services.

```bash
make docker-health-check
```

**Checks:** Each service's `/health/` endpoint

### `make docker-restart-all`
Restart all services.

```bash
make docker-restart-all
```

**Wait:** 5 seconds before showing status

### `make docker-stop-all`
Stop all services (don't remove).

```bash
make docker-stop-all
```

**Purpose:** Pause services while keeping data.

### `make docker-start-all`
Start all stopped services.

```bash
make docker-start-all
```

**Wait:** 5 seconds before showing status

---

## Category 9: Delegation Targets

### `make compose`
Delegate to applications/compose/Makefile.

```bash
make compose <target>
```

**Example:**
```bash
make compose help     # Show compose targets
make compose status   # Run compose status
```

### `make assets`
Delegate to assets/Makefile.

```bash
make assets <target>
```

**Example:**
```bash
make assets build   # Build assets
make assets watch   # Watch for changes
```

### `make scripts`
Delegate to tests/scripts/Makefile.

```bash
make scripts <target>
```

**Alias:** `make script`

### `make website-ctc`
Delegate to ctc-research/Makefile.

```bash
make website-ctc <target>
```

**Example:**
```bash
make website-ctc help   # Show ctc targets
make website-ctc lint   # Run ctc linting
```

### `make website-structa`
Delegate to lms-demo/Makefile.

```bash
make website-structa <target>
```

### `make website-vresume`
Delegate to VResume/Makefile.

```bash
make website-vresume <target>
```

### `make projects`
Run target in all project Makefiles.

```bash
make projects help   # Show help from all projects
make projects lint   # Lint all projects
make projects test   # Test all projects
```

---

## Category 10: Complex Workflows

### `make full-site-check`
Complete site verification workflow.

```bash
make full-site-check WEBSITE=ctc
```

**Sequence:**
1. Build assets
2. Collect static files
3. Run migrations
4. Load fixture data
5. Verify runtime

**Purpose:** Pre-deployment verification.

### `make verify-runtime-site`
Verify site runtime functionality.

```bash
make verify-runtime-site WEBSITE=structa
```

**Checks:**
- Asset loading
- Static file serving
- Page rendering

---

## Logging

All complex operations log to `logs/` directory:

```bash
# Log files created by operations:
logs/makemigrations-ctc.log         # Migration output
logs/migrate-ctc.log                # Migration application
logs/load_dumped_data-ctc.log       # Fixture loading
logs/populate_site_data-ctc.log     # Data population
logs/verify_runtime-ctc.log         # Runtime verification
logs/build_assets-ctc.log           # Asset building
logs/collectstatic-ctc.log          # Static collection
```

---

## Common Workflows

### Development Workflow

```bash
# 1. Start development server
make run-dev

# 2. After model changes
make migrations
make migrate

# 3. Run tests
make test

# 4. Rebuild assets if needed
make build-assets
```

### Docker Development

```bash
# 1. Build image
make docker-build WEBSITE=ctc

# 2. Start container
make docker-up WEBSITE=ctc

# 3. View logs
make docker-logs WEBSITE=ctc

# 4. After changes
make docker-redeploy WEBSITE=ctc

# 5. Stop when done
make docker-down WEBSITE=ctc
```

### Full Deployment

```bash
# 1. Clean old resources
make docker-clean

# 2. Deploy all services
make docker-deploy-full

# 3. Check status
make docker-status

# 4. View access points
make docker-logs-all
```

### Testing All Sites

```bash
# Run tests for specific site
make tests-website WEBSITE=ctc
make tests-website WEBSITE=structa
make tests-website WEBSITE=vresume

# Or test all at once
make tests-website WEBSITE=all
```

### Database Operations

```bash
# 1. Load fixtures
make load-dumps-site WEBSITE=ctc

# 2. Populate test data
make populate-data-all

# 3. Verify setup
make full-site-check WEBSITE=ctc
```

---

## Troubleshooting

### Issue: Unknown website WEBSITE=xyz

**Solution:** Use valid website names:
- `ctc` or `ctc-research`
- `structa` or `lms-demo`
- `vresume` or `VResume`

### Issue: Permission denied

**Solution:** Ensure Python virtual environment is activated:
```bash
source .venv/bin/activate
```

### Issue: Docker daemon not running

**Solution:** Start Docker:
```bash
# macOS
open -a Docker

# Linux
sudo systemctl start docker

# Windows
# Open Docker Desktop
```

### Issue: Port already in use

**Solution:** Stop existing containers:
```bash
make docker-stop-all
docker ps  # Verify all stopped
```

### Issue: Build fails with cache

**Solution:** Rebuild without cache:
```bash
make docker-rebuild WEBSITE=ctc
```

---

## Advanced Usage

### Custom Variables

```bash
# Use different Python executable
make check PYTHON=/usr/bin/python3

# Use different server type
make server SERVER_TYPE=uvicorn

# Use different compose file
make docker-build COMPOSE_FILE=docker-compose.prod.yml

# Combine multiple variables
make run-dev WEBSITE=structa PYTHON=.venv/bin/python
```

### Bash Completion

```bash
# Source make completion (bash)
eval "$(make -C scripts/completion bash-completion)"
```

---

## Performance Tips

- ✅ Use `make docker-rebuild` for clean builds
- ✅ Run `make test` with `pytest -x` to stop on first failure
- ✅ Use `make build-assets-all` at end of development day
- ✅ Run `make docker-clean` periodically to free disk space
- ✅ Cache Docker layers by ordering Dockerfile commands

---

## See Also

- `Makefile` - Root Makefile
- `applications/compose/Makefile` - Docker Compose targets
- `assets/Makefile` - Frontend build targets
- `tests/Makefile` - Testing targets
- `ctc-research/Makefile` - CTC targets
- `lms-demo/Makefile` - LMS Demo targets
- `VResume/Makefile` - VResume targets

---

**Status:** Phase 12 Complete ✅  
**Last Updated:** June 7, 2026  
**Maintained By:** Kiro Agent v1.0

