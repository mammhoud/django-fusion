# Ecosystem Documentation

> Shared documentation for the entire Django multi-project ecosystem

## Overview

This section contains documentation shared across all projects in the ecosystem.

## Sections

### [Getting Started](getting-started/)
Quick start guides and installation instructions
- [01-quick-start.md](getting-started/01-quick-start.md) - Get running in minutes
- [01-installation-guide.md](getting-started/01-installation-guide.md) - Complete installation
- [02-environment-setup.md](getting-started/02-environment-setup.md) - Environment configuration
- [02-local-development-setup.md](getting-started/02-local-development-setup.md) - Local setup
- [03-project-structure-overview.md](getting-started/03-project-structure-overview.md) - Project layout
- [03-project-structure.md](getting-started/03-project-structure.md) - Detailed structure
- [04-common-tasks.md](getting-started/04-common-tasks.md) - Everyday operations

### [Architecture](architecture/)
System architecture, design decisions, and technical specifications
- [01-system-overview.md](architecture/01-system-overview.md) - System overview
- [02-project-relationships.md](architecture/02-project-relationships.md) - Project relationships
- [03-service-layer.md](architecture/03-service-layer.md) - Service layer design
- [ARCHITECTURE.md](architecture/ARCHITECTURE.md) - Main architecture document
- [technology-stack.md](architecture/technology-stack.md) - Technology stack

### [Deployment](deployment/)
Deployment procedures and production configuration
- [01-deployment-overview.md](deployment/01-deployment-overview.md) - Deployment strategies
- [01-docker-compose-setup.md](deployment/01-docker-compose-setup.md) - Docker Compose
- [02-build-for-production.md](deployment/02-build-for-production.md) - Production builds
- [02-environment-configuration.md](deployment/02-environment-configuration.md) - Environment config
- [03-deployment-procedures.md](deployment/03-deployment-procedures.md) - Deployment steps
- [03-nginx-reverse-proxy-setup.md](deployment/03-nginx-reverse-proxy-setup.md) - Nginx setup
- [04-production-deployment-checklist.md](deployment/04-production-deployment-checklist.md) - Checklist
- [05-rollback-procedures.md](deployment/05-rollback-procedures.md) - Rollback strategies
- [production-deployment.md](deployment/production-deployment.md) - Production guide

### [Development](development/)
Development workflow and coding standards
- [01-development-workflow.md](development/01-development-workflow.md) - Development process
- [04-commands-reference.md](development/04-commands-reference.md) - Command reference
- [05-repository-management.md](development/05-repository-management.md) - Repo management
- [06-branch-strategy.md](development/06-branch-strategy.md) - Branch strategy
- [coding_standards_and_conventions.md](development/coding_standards_and_conventions.md) - Code standards
- [testing_strategy.md](development/testing_strategy.md) - Testing approach
- [enhancement-roadmap.md](development/enhancement-roadmap.md) - Roadmap

---

## Projects

| Project | Description | Documentation |
|---------|-------------|---------------|
| ctc-research.com | Xellent LMS | [ctc-research/](../ctc-research/) |
| structa.cloud | Alliance Platform | [structa-cloud/](../structa-cloud/) |

## Packages

| Package | Purpose | Documentation |
|---------|---------|---------------|
| django-osoul | Django foundation | [packages/django-osoul/](../packages/django-osoul/) |
| crafts-ai | Wagtail automation | [packages/crafts-ai/](../packages/crafts-ai/) |
| django-osoul | Testing | [packages/django-osoul/](../packages/django-osoul/) |
| nawaai | AI toolkit | [packages/nawaai/](../packages/nawaai/) |

---

## Quick Commands

```bash
# Run all tests
python3 shared/scripts/run_all_tests.py

# Validate system
python3 shared/scripts/validate_system.py

# Start Docker services
docker compose up -d

# Check health
curl http://localhost:8080/health/
```

---

## Related

- [Main Documentation](../README.md)
- [Shared Resources](../shared/)
- [Infrastructure](../infrastructure/)
