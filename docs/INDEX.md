# Documentation Index

Complete documentation organized by category.

## Quick Links

- **[Getting Started](#getting-started)** - Start here for new developers
- **[Guides](#guides)** - Feature and system guides
- **[API & Infrastructure](#api--infrastructure)** - API docs and infrastructure
- **[Components](#components)** - UI components library
- **[Setup & Installation](#setup--installation)** - Installation guides
- **[Troubleshooting](#troubleshooting)** - Common issues and solutions
- **[Archives](#archives)** - Historical documents

---

## Getting Started

### For New Developers
1. **[START_HERE.md](setup/00_START_HERE.md)** - Quick start guide
2. **[DEPLOYMENT_QUICK_START.md](setup/DEPLOYMENT_QUICK_START.md)** - Quick deployment

### First Steps
```bash
# Setup development environment
make check WEBSITE=ctc
make run-dev WEBSITE=ctc
make test
```

---

## Guides

Comprehensive guides for key features and systems.

### Libraries & Integration
- **[LIBS_INTEGRATION.md](guides/LIBS_INTEGRATION.md)** - django-osoul, django-rseal, django-grep integration guide

### Course System
- **[COURSE_SYSTEM_IMPLEMENTATION.md](guides/COURSE_SYSTEM_IMPLEMENTATION.md)** - Complete course system
- **[COURSE_SYSTEM_QUICK_REFERENCE.md](guides/COURSE_SYSTEM_QUICK_REFERENCE.md)** - Quick reference

### Payment System
- **[PAYMENT_PROVIDERS.md](guides/PAYMENT_PROVIDERS.md)** - Payment integration (3 providers)

### CMS Integration
- **[WAGTAIL_CMS_INTEGRATION.md](guides/WAGTAIL_CMS_INTEGRATION.md)** - Wagtail admin setup

### Development Tools
- **[MAKEFILE_REFERENCE.md](guides/MAKEFILE_REFERENCE.md)** - All make commands (49 targets)

---

## API & Infrastructure

### Infrastructure Setup
- **[INFRASTRUCTURE_GUIDE.md](infrastructure/INFRASTRUCTURE_GUIDE.md)** - Compose stack, networks, databases, ports
- **[DEPLOYMENT_CHECKLIST.md](infrastructure/DEPLOYMENT_CHECKLIST.md)** - Deployment checklist
- **[DEPLOYMENT_GUIDE_SSL.md](infrastructure/DEPLOYMENT_GUIDE_SSL.md)** - SSL configuration
- **[CERTIFICATE_BACKUP_GUIDE.md](infrastructure/CERTIFICATE_BACKUP_GUIDE.md)** - Certificate management

### Docker & Deployment
- **[DEPLOYMENT_COMPLETE.md](infrastructure/DEPLOYMENT_COMPLETE.md)** - Deployment status

### Services
- **PostgreSQL** - Primary database (structa-db)
- **Redis** - Caching layer (structa-cache)
- **Prometheus** - Monitoring (prometheus.localhost:9090)
- **Loki** - Logging (loki.localhost:3100)
- **Grafana** - Visualization (grafana.localhost:3000)

---

## Components

### UI Components Library
**Location:** `packages/ui/`

- **[packages/ui/README.md](../packages/ui/README.md)** - Component documentation

#### Component Categories
- **Forms** - HTMX form integration
- **HTMX** - Core HTMX utilities
- **Modals** - Modal dialogs
- **Notifications** - Toast notifications
- **Search** - Search components
- **Tables** - Data tables

---

## Frontend & Assets

### Build System & JS Libraries
- **[assets/ASSETS_GUIDE.md](../assets/ASSETS_GUIDE.md)** - Webpack build, JS libraries, per-site commands

#### Quick Build Reference
```bash
npm --prefix assets run build:ctc      # ctc-research
npm --prefix assets run build:structa  # lms-demo
npm --prefix assets run build:vresume  # VResume
npm --prefix assets run build:all      # all sites
```

### Test Fixtures
**Location:** `tests/fixtures/`

- **[tests/fixtures/INDEX.md](../tests/fixtures/INDEX.md)** - Complete fixture index (all sites)
- **[tests/fixtures/README.md](../tests/fixtures/README.md)** - Fixture documentation
- **[tests/fixtures/vresume/README.md](../tests/fixtures/vresume/README.md)** - VResume fixtures reference
- **[tests/fixtures/lms-demo/README.md](../tests/fixtures/lms-demo/README.md)** - lms-demo fixtures reference

#### Available Fixtures
- **LMS Data** - Courses, tags, specializations
- **Users** - User test data
- **Courses** - Course fixtures
- **System** - System test data

### Test Scripts
**Location:** `tests/scripts/`

- **[tests/scripts/README.md](../tests/scripts/README.md)** - Script documentation

#### Script Categories
- **Deployment** - Production deployment
- **Validation** - System validation
- **Utilities** - Helper utilities
- **Helpers** - Test runners

---

## Setup & Installation

### Initial Setup
1. **Clone repository**
   ```bash
   git clone <repo-url>
   cd websites
   ```

2. **Install dependencies**
   ```bash
   make check
   ```

3. **Start development**
   ```bash
   make run-dev WEBSITE=ctc
   ```

### Database Setup
```bash
# Apply migrations
make migrate

# Load fixtures
make load-dumps-site WEBSITE=ctc

# Populate test data
make populate-data-all
```

### Docker Setup
```bash
# Full deployment
make docker-deploy-full

# Start specific service
make docker-up WEBSITE=ctc

# Check status
make docker-status
```

---

## Troubleshooting

### Common Issues

**Asset loading problems**
- [ASSET_HEALTH_VERIFICATION.md](troubleshooting/ASSET_HEALTH_VERIFICATION.md)

**Container issues**
- [CONTAINER_LOGS_ANALYSIS.md](troubleshooting/CONTAINER_LOGS_ANALYSIS.md)

### Debug Commands

```bash
# Check system
make check WEBSITE=ctc

# View logs
make docker-logs-all

# Validate config
docker compose config --quiet

# Test endpoints
make verify-runtime-site WEBSITE=ctc
```

---

## Archives

Historical documentation and phase reports.

**Location:** `docs/archives/`

- Phase completion reports (Phases 4-14)
- Session summaries
- Implementation reports
- Planning documents

**See:** [docs/archives/README.md](archives/README.md)

---

## File Organization

```
docs/
├── INDEX.md                     (this file)
├── guides/                      (Feature guides)
│   ├── LIBS_INTEGRATION.md
│   ├── COURSE_SYSTEM_*.md
│   ├── PAYMENT_PROVIDERS.md
│   ├── WAGTAIL_CMS_INTEGRATION.md
│   └── MAKEFILE_REFERENCE.md
├── infrastructure/              (Infrastructure & deployment)
│   ├── INFRASTRUCTURE_GUIDE.md
│   ├── DEPLOYMENT_*.md
│   ├── CERTIFICATE_*.md
│   └── ...
├── setup/                       (Setup & installation)
│   ├── 00_START_HERE.md
│   └── DEPLOYMENT_QUICK_START.md
├── troubleshooting/             (Troubleshooting guides)
│   ├── ASSET_HEALTH_VERIFICATION.md
│   ├── CONTAINER_LOGS_ANALYSIS.md
│   └── ...
├── archives/                    (Historical documents)
│   ├── README.md
│   ├── PHASE*.md
│   └── ...
└── _INDEX.md                    (Master index)
```

### Related Docs (outside docs/)
- `assets/ASSETS_GUIDE.md` — Frontend build & JS library reference
- `packages/ui/README.md` — UI component library

---

## Quick Commands

### Development
```bash
make run-dev               # Start dev server
make test                  # Run tests
make lint-all             # Check code quality
```

### Build & Deploy
```bash
make docker-deploy-full   # Full deployment
make docker-rebuild       # Rebuild images
make docker-logs-all      # View all logs
```

### Testing
```bash
make test                 # Run all tests
make tests-unit          # Unit tests only
make tests-website       # Website tests
```

### Database
```bash
make migrate              # Apply migrations
make populate-data-all   # Load test data
make load-dumps-site    # Load dumps
```

---

## Need Help?

1. **Check [START_HERE.md](setup/00_START_HERE.md)** - Quick start guide
2. **Review [MAKEFILE_REFERENCE.md](guides/MAKEFILE_REFERENCE.md)** - Command reference
3. **See [troubleshooting/](troubleshooting/)** - Common issues
4. **Check [archives/](archives/)** - Historical context

---

**Last Updated:** June 9, 2026  
**Status:** ✅ COMPLETE & ORGANIZED

