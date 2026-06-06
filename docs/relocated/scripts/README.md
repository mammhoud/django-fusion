# 🚀 Unified Deployment & Test Scripts

Comprehensive scripts for managing, testing, and deploying multi-website applications with Traefik reverse proxy.

---

## Overview

This directory contains two main unified scripts:

1. **`deploy.sh`** - Interactive deployment and service management
2. **`run-tests.sh`** - Comprehensive test suite with proxy verification

---

## Prerequisites

- Docker & Docker Compose
- Make
- Bash 4+
- Git (for some operations)

---

## Scripts

### 1. Deploy Script (`deploy.sh`)

**Interactive deployment and service management with multiple configuration options.**

#### Features

- ✅ Multiple environment selection (Development, Staging, Production)
- ✅ Website selection (Individual or All)
- ✅ Server type selection (Docker Compose, Local Development, Kubernetes)
- ✅ Debug mode control (Off, On, Verbose)
- ✅ Service start/stop/restart
- ✅ Log viewing
- ✅ Test execution
- ✅ Build management
- ✅ Configuration verification

#### Usage

```bash
# Start interactive deployment menu
./scripts/deploy.sh

# Non-interactive with environment variables
ENV=production SERVER_TYPE=docker ./scripts/deploy.sh
```

#### Workflow

1. **Select Environment** - Choose deployment environment
2. **Select Website(s)** - Choose which website(s) to manage
3. **Select Server Type** - Choose Docker or local development
4. **Select Debug Mode** - Set logging verbosity
5. **Select Action** - Choose operation (start, stop, test, etc.)

#### Traefik Service Names

Services are automatically configured with Traefik-compatible names:

```
traefik-proxy          → Traefik reverse proxy
db-postgres            → PostgreSQL database
cache-redis            → Redis cache
web-ctc-research       → CTC Research website
web-lms-demo           → LMS Demo website
web-vresume            → VResume website
shared-media           → Shared media server
tasks-worker-shared    → Shared task worker
tasks-beat-shared      → Shared task scheduler
```

#### Makefile Integration

The script uses Makefile commands:

```bash
make docker-deploy-full         # Full deployment
make docker-health-check        # Service health
make docker-status              # View status
make docker-logs                # View logs
make test                        # Run tests
```

---

### 2. Test Runner Script (`run-tests.sh`)

**Comprehensive test suite with 10 validation categories.**

#### Features

- ✅ SSL configuration verification
- ✅ Docker Compose syntax validation
- ✅ Makefile targets availability
- ✅ SSL certificate file checking
- ✅ Documentation completeness
- ✅ Repository structure validation
- ✅ Docker services configuration
- ✅ Environment variables verification
- ✅ Network connectivity checks
- ✅ Traefik proxy configuration

#### Usage

```bash
# Run complete test suite
./scripts/run-tests.sh

# Run and save report
./scripts/run-tests.sh > test-results.txt 2>&1
```

#### Test Categories

1. **SSL Configuration Verification**
   - Runs `/tests/scripts/verify-ssl-config.sh`
   - Validates certificates for all 3 domains
   - Checks certificate file permissions

2. **Docker Compose Syntax**
   - Validates docker-compose.yml syntax
   - Checks for configuration errors
   - Verifies service definitions

3. **Makefile Targets**
   - Verifies essential targets exist
   - Tests: help, check, build-assets-all, docker-status, test
   - Checks docker-health-check availability

4. **SSL Certificates**
   - Verifies ctc-research.crt present
   - Verifies structa-cloud.crt present
   - Verifies vresume.crt present

5. **Documentation**
   - Checks README files present
   - Verifies deployment guides
   - Checks error analysis documentation

6. **Repository Structure**
   - Verifies base directory is clean
   - Checks required directories exist
   - Validates organization

7. **Docker Services**
   - Verifies traefik service
   - Verifies database service
   - Verifies cache service
   - Verifies all website services

8. **Environment Variables**
   - Checks .env file exists
   - Verifies required variables set
   - Validates database configuration

9. **Network Connectivity**
   - Checks Docker networks
   - Verifies traefik-net exists
   - Validates network configuration

10. **Traefik Proxy Configuration**
    - Verifies TLS configuration
    - Checks entry points
    - Validates providers

#### Test Report

Test results are saved to:
```
logs/tests/test-report-YYYYMMDD_HHMMSS.txt
```

Output includes:
- Individual test results (✅/❌)
- Total tests run
- Pass/fail count
- Success percentage

---

## Makefile Commands

Key commands used by scripts:

```bash
# Deployment
make docker-deploy-full              # Full deployment
make docker-deploy-warehouse         # Start DB/Redis/Adminer
make docker-deploy-traefik           # Start reverse proxy
make docker-deploy-websites          # Build and start websites

# Service Management
make docker-start-all                # Start all services
make docker-stop-all                 # Stop all services
make docker-restart-all              # Restart all services
make docker-down                     # Stop and remove

# Monitoring
make docker-status                   # Show service status
make docker-logs-all                 # View all logs
make docker-health-check             # Check service health

# Maintenance
make docker-clean                    # Clean containers/images
make docker-prune-containers         # Remove stopped containers
make docker-prune-data               # Remove all volumes (dangerous!)

# Building
make docker-build WEBSITE=ctc         # Build specific website
make docker-rebuild WEBSITE=ctc       # Rebuild without cache
make docker-redeploy WEBSITE=ctc      # Build and deploy

# Testing
make test                            # Run test suite
make test-verbose                    # Run with verbose output
```

---

## Docker Service Names

All services use Traefik-compatible naming:

### Core Infrastructure
- `traefik-proxy` - Traefik reverse proxy on port 8080
- `db-postgres` - PostgreSQL database
- `cache-redis` - Redis cache

### Websites
- `web-ctc-research` - CTC Research website (port 5070)
- `web-lms-demo` - LMS Demo website (port 5071)
- `web-vresume` - VResume website (port 5072)

### Supporting Services
- `shared-media` - Nginx media server
- `tasks-worker-shared` - Celery worker
- `tasks-beat-shared` - Celery scheduler

---

## Traefik Configuration

### Entry Points
```
web              → Port 80 (HTTP → HTTPS redirect)
web-secure       → Port 443 (HTTPS with SSL)
```

### Domains & Certificates
```
ctc-research.com    ↔ ctc-research.crt/key
structa.cloud       ↔ structa-cloud.crt/key
vresume.structa.cloud ↔ vresume.crt/key
```

### Access Points
```
Traefik Dashboard: http://localhost:8080
CTC Research:      https://ctc-research.com
LMS Demo:          https://structa.cloud
VResume:           https://vresume.structa.cloud
```

---

## Debug Modes

Controlled via `deploy.sh` menu or environment variables:

### Off (Default)
- Standard logging
- Production-ready
- Minimal debug output

### On
- Debug logging enabled
- Enhanced error messages
- Development mode

### Verbose
- Maximum logging
- Trace execution
- All operations logged

### Set via Environment
```bash
DEBUG_MODE=verbose ./scripts/deploy.sh
```

---

## Environment Variables

### Deployment Configuration
```bash
ENVIRONMENT=production          # development|staging|production
DEBUG=true                       # true|false
DEBUG_MODE=off                   # off|on|verbose
SERVER_TYPE=docker               # docker|local|k8s
WEBSITE=all                      # ctc-research|lms-demo|vresume|all|none
```

### Traefik Configuration
```bash
TRAEFIK_ENTRYPOINT=websecure
TRAEFIK_LOG_LEVEL=INFO
```

### Django Configuration
```bash
DJANGO_DEBUG=false
DJANGO_LOG_LEVEL=INFO
```

---

## Quick Start

### 1. First Run

```bash
# Run tests first
./scripts/run-tests.sh

# Fix any issues from test output
# Then proceed to deployment
```

### 2. Development Setup

```bash
ENV=development SERVER_TYPE=docker ./scripts/deploy.sh
# Select "All" websites
# Select "Start Services"
```

### 3. Production Deployment

```bash
ENV=production SERVER_TYPE=docker ./scripts/deploy.sh
# Select specific website or "All"
# Select "Setup & Deploy"
```

### 4. View Logs

```bash
./scripts/deploy.sh
# Select "Select Action"
# Select "View Logs"
```

---

## Troubleshooting

### SSL Certificate Issues
```bash
./scripts/run-tests.sh
# Check "Test 4: SSL Certificate Files" output
# Review docs/DEPLOYMENT_GUIDE_SSL.md
```

### Docker Compose Errors
```bash
./scripts/run-tests.sh
# Check "Test 2: Docker Compose Syntax Validation"
# Run: docker compose config
```

### Service Startup Failures
```bash
./scripts/run-tests.sh
# Check "Test 10: Traefik Proxy Configuration"
# View logs: docker compose logs
```

### Makefile Issues
```bash
./scripts/run-tests.sh
# Check "Test 3: Makefile Targets Availability"
# Verify Makefile exists: ls -la Makefile
```

---

## File Locations

```
/root/site/websites/
├── scripts/
│   ├── deploy.sh           ← Interactive deployment script
│   ├── run-tests.sh        ← Comprehensive test suite
│   └── README.md           ← This file
│
├── tests/
│   ├── scripts/
│   │   ├── verify-ssl-config.sh
│   │   ├── deploy-production.sh
│   │   └── [other test scripts]
│   └── [test code]
│
├── docs/
│   ├── SAFE_DEPLOYMENT_PROCEDURE.md
│   ├── DEPLOYMENT_GUIDE_SSL.md
│   ├── FIXTURE_LOADING_ERROR_ANALYSIS.md
│   └── [more documentation]
│
├── compose/
│   ├── traefik/
│   │   ├── traefik.yml
│   │   ├── certs/
│   │   └── dynamic/
│   └── [other compose files]
│
├── logs/
│   ├── tests/
│   │   └── test-report-*.txt
│   └── [application logs]
│
├── docker-compose.yml
└── Makefile
```

---

## Exit Codes

### deploy.sh
- `0` - Successful execution
- `1` - Script error or user quit
- `2` - Configuration error

### run-tests.sh
- `0` - All tests passed
- `1` - One or more tests failed
- `2` - Skipped (e.g., Docker not installed)

---

## Support & Documentation

- **Deployment Guide**: `/docs/SAFE_DEPLOYMENT_PROCEDURE.md`
- **SSL Configuration**: `/docs/DEPLOYMENT_GUIDE_SSL.md`
- **Error Analysis**: `/docs/FIXTURE_LOADING_ERROR_ANALYSIS.md`
- **Master Index**: `/docs/00_MASTER_INDEX.md`

---

## Version History

- **v1.0.0** - Initial release with 10 test categories and interactive deployment
  - Unified deployment control
  - Comprehensive test suite
  - Traefik integration
  - Multi-website support
  - Multiple debug modes

---

## License

Part of the Structa Cloud infrastructure.

---

**Last Updated:** June 2, 2026  
**Status:** ✅ Production Ready
