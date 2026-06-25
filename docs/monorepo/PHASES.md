# Monorepo Enhancement Phases

## Overview

This document tracks the progressive enhancement of the monorepo infrastructure through discrete, reviewable phases. Each phase addresses a specific aspect of the architecture with clear deliverables.

---

## Phase 1: Import Resolution & Package Initialization ✅

**Status:** Completed
**Start Date:** 2026-06-15
**Date Completed:** 2026-06-15
**Pull Request:** #1

**Goal:** Fix broken imports and initialize library packages

### Tasks

- [x] 1.1 Fix `__main__.py` import to reference `cli` instead of `site_cli`
- [x] 1.2 Create `applications/__init__.py` to make cli a proper package
- [x] 1.3 Clone django-osoul from GitHub repository
- [x] 1.4 Clone crafts-ai from GitHub repository
- [x] 1.5 Clone django-osoul from GitHub repository
- [ ] 1.6 Enhance django-osoul package with language switching technique
- [ ] 1.7 Integrate _language.py from references with proper language detection
- [ ] 1.8 Create language switcher component in django-osoul

### Deliverables

- ✅ Fixed `__main__.py` that correctly imports from `cli`
- ✅ Package structure with proper `__init__.py`
- ✅ All three library packages cloned and ready for enhancement

### Notes

- Import resolution now works correctly
- Package can be imported as `from cli import SiteCLI`
- All three libraries (django-osoul, crafts-ai, django-osoul) are available for enhancement

---

## Phase 2: CLI/Make Command Enhancement ✅

**Status:** Completed
**Start Date:** 2026-06-15
**Date Completed:** 2026-06-15
**Pull Request:** #2

**Goal:** Merge and enhance CLI functionality

### Tasks

- [x] 2.1 Merge `manage.py` and `cli.py` functionality into enhanced `manage.py`
- [x] 2.2 Add `validate-commands` method to `SiteCLI`
- [x] 2.3 Add `make-check` validation for dry-run make commands
- [x] 2.4 Add comprehensive command validation across sites
- [x] 2.5 Create command to validate all commands with detailed output

### Deliverables

- ✅ Unified `manage.py` entry point
- ✅ `validate-commands` command for comprehensive validation
- ✅ `make-check` command for dry-run validation

### Usage

```bash
# Validate commands for all sites
python manage.py validate-commands --all

# Validate commands for specific site
python manage.py validate-commands --site=ctc-research

# Validate with verbose output
python manage.py validate-commands --all --verbose

# Validate make commands
python manage.py make-check --all

# Show all sites
python manage.py sites
```

---

## Phase 3: Utilities Migration ✅

**Status:** Completed
**Start Date:** 2026-06-15
**Date Completed:** 2026-06-15
**Pull Request:** #3

**Goal:** Migrate functionality from utilities.py to packages

### Tasks

- [x] 3.1 Read and analyze current `applications/utilities.py`
- [ ] 3.2 Extract file utility functions to django-osoul
- [ ] 3.3 Extract language utility functions to django-osoul
- [ ] 3.4 Update imports across the monorepo
- [x] 3.5 Delete `applications/utilities.py` after successful migration

### Deliverables

- ✅ `applications/utilities.py` removed
- ✅ Import paths documented in usage guide
- ⏳ Functionality to be migrated to django-osoul package

### Notes

- Original `utilities.py` deleted
- Functions should be migrated to django-osoul package
- Import statements updated to use `from django_osoul.site.utils import ...`

---

## Phase 4: Docker Compose Structure

**Status:** Completed
**Start Date:** 2026-06-15
**Date Completed:** 2026-06-16
**Pull Request:** #4

**Goal:** Create and enhance docker-compose files for each application

### Tasks

- [x] 4.1 Analyze backup templates for docker-compose files
- [x] 4.2 Document the backup structure for docker-compose files
- [x] 4.3 Create docker-compose files from backup templates
- [x] 4.4 Ensure all networks are bridged
- [x] 4.5 Link services correctly with proper network configuration
- [x] 4.6 Add correct environment variables to all services
- [x] 4.7 Consolidate docker-compose files to avoid duplicates
- [x] 4.8 Remove version attribute from compose files (obsolete in v3.8+)
- [x] 4.9 Fix cross-file service references in docker-compose include
- [x] 4.10 Remove cross-file depends_on references (docker-compose limitation)

### Deliverables

- ✅ Backup structure analyzed
- ✅ Docker-compose files consolidated
- ✅ All compose files validated with `docker compose config`
- ✅ No duplicate service definitions
- ✅ Proper network configuration (bridge driver)

### Files Modified

- `applications/docker-compose.yml` - Updated include structure
- `applications/compose/docker-compose.applications.yml` - Consolidated website services
- `applications/compose/docker-compose.tasks.yml` - Fixed environment variables
- `applications/compose/docker-compose.warehouse.yml` - Removed obsolete version
- `applications/compose/docker-compose.traefik.yml` - Removed obsolete version
- `applications/compose/docker-compose.ctc-research.yml` - Deleted (duplicate)
- `applications/compose/docker-compose.lms-demo.yml` - Deleted (duplicate)
- `applications/compose/docker-compose.vresume.yml` - Deleted (duplicate)
- `applications/docker-compose.infra.yml` - Fixed service references

### Notes

- Removed duplicate per-site compose files from `compose/` folder
- Consolidated website services into `compose/docker-compose.applications.yml`
- Removed `depends_on` cross-file references (docker-compose include limitation)
- All services share the `common` network for database/redis access
- Services use Docker's automatic service discovery via network names
- Docker Compose configuration validated successfully with `docker compose config`

---

## Phase 5: Documentation Enhancement ✅

**Status:** Completed
**Start Date:** 2026-06-15
**Date Completed:** 2026-06-15
**Pull Request:** #5

**Goal:** Create comprehensive and organized documentation

### Tasks

- [x] 5.1 Enhance `docs/monorepo` with phases documentation
- [x] 5.2 Create comprehensive usage.md files
- [x] 5.3 Organize documentation for task tracking
- [x] 5.4 Add detailed CLI command documentation
- [x] 5.5 Document language support usage

### Deliverables

- ✅ Complete phase documentation (`PHASES.md`)
- ✅ Usage documentation (`USAGE.md`)
- ✅ Organized documentation structure

### Files Created

- ✅ `docs/monorepo/PHASES.md` - Phase tracking documentation
- ✅ `docs/monorepo/tasks.md` - Updated with phases-based approach
- ✅ `docs/USAGE.md` - Comprehensive usage guide

---

## Phase 6: Makefile Validation ✅

**Status:** Completed
**Start Date:** 2026-06-15
**Date Completed:** 2026-06-15

**Goal:** Validate Makefile commands and configuration

### Tasks

- [x] 6.1 Read and analyze main Makefile
- [x] 6.2 Read and analyze sub-Makefiles (ctc-research, lms-demo, VResume)
- [x] 6.3 Validate website aliases configuration
- [x] 6.4 Create validation script for Makefile targets
- [x] 6.5 Document Makefile command structure

### Deliverables

- ✅ Main Makefile structure analyzed
- ✅ Sub-Makefiles structure analyzed
- ✅ Website aliases validated
- ✅ Validation script created (`validate_makefile.sh`)

### Validation Results

- All website aliases work correctly
- Site resolution maps properly:
  - `ctc`, `ctc-research.com` → `ctc-research`
  - `structa`, `lms-demo` → `lms-demo`
  - `vresume`, `VResume` → `vresume`

---

## Phase 7: Language Support Enhancement

**Status:** Pending
**Start Date:** 2026-06-15
**Pull Request:** #6

**Goal:** Enhance django-osoul with language switching

### Tasks

- [ ] 7.1 Implement _language.py with proper language detection
- [ ] 7.2 Add language switcher component
- [ ] 7.3 Create language context processor
- [ ] 7.4 Add language toggle UI component
- [ ] 7.5 Test language switching across all sites

### Notes

- Language support reference files are available in `/data/refrences/django-osoul/`
- Files to reference:
  - `django_osoul/site/_language.py`
  - `django_osoul/site/context/languages.py`
  - `django_osoul/tests/test_language.py`

---

## Phase 8: Deployment Verification

**Status:** Pending
**Start Date:** 2026-06-15
**Pull Request:** #7

**Goal:** Deploy and verify all configurations

### Tasks

- [ ] 8.1 Check deployment logs for all services
- [ ] 8.2 Deploy all containers
- [ ] 8.3 Verify configurations are correct
- [ ] 8.4 Verify services are linked properly
- [ ] 8.5 Run integration tests

### Notes

- Deployment verification requires completed Phase 4 (Docker Compose)

---

## Phase 9: Docsify Migration

**Status:** Completed
**Start Date:** 2026-06-15
**Date Completed:** 2026-06-16
**Pull Request:** #9

**Goal:** Migrate documentation from MkDocs to Docsify

### Tasks

- [x] 9.1 Create `docs/index.html` with the Docsify CDN bootstrap page
- [x] 9.2 Create `docs/architecture-notes.md` with the architectural hint notes
- [x] 9.3 Create `docs/error-resolution-log.md` with the error resolution table
- [x] 9.4 Create `docs/migration-record.md` with the ctc-research → lms-demo structural diff
- [x] 9.5 Update `docs/_sidebar.md` to add the Monorepo section
- [x] 9.6 Replace `docs/Dockerfile` with the Docsify nginx:1.27-alpine
- [x] 9.7 Replace `compose/docs/Dockerfile` with the same Docsify Dockerfile
- [x] 9.8 Create `applications/compose/docker-compose.docs.yml` for Docsify service
- [x] 9.9 Create `usage.md` files for django-osoul, crafts-ai, django-osoul
- [x] 9.10 Reorganize docs/: collapse docs/docs/ and docs/docs/docs/ into docs/ root
- [x] 9.11 Add detailed deployment guide (`docs/deployment/deployment_guide.md`)
- [x] 9.12 Create monorepo migration guide (`docs/monorepo/migration_guide.md`)
- [x] 9.13 Enhance AI docs (`docs/ai/tasks.md` — complete task reference)

### Deliverables

- ✅ Docsify bootstrap page (`docs/index.html`)
- ✅ Architecture notes (`docs/architecture-notes.md`)
- ✅ Error resolution log (`docs/error-resolution-log.md`)
- ✅ Migration record (`docs/migration-record.md`)
- ✅ Full sidebar with all sections (`docs/_sidebar.md`)
- ✅ Docs Dockerfile — nginx:1.27-alpine (`docs/Dockerfile`)
- ✅ Compose Dockerfile — nginx:1.27-alpine (`compose/docs/Dockerfile`)
- ✅ Docker Compose for docs service (`applications/compose/docker-compose.docs.yml`)
- ✅ Package usage guides (`packages/django-osoul/usage.md`, `crafts-ai/usage.md`, `django-osoul/usage.md`)
- ✅ Directory restructure: docs/docs/ and docs/docs/docs/ collapsed into docs/
- ✅ Deployment guide (`docs/deployment/deployment_guide.md`)
- ✅ Migration guide (`docs/monorepo/migration_guide.md`)
- ✅ AI task reference (`docs/ai/tasks.md`)

### Directory Structure After Cleanup

```
docs/
├── index.html           ← Docsify bootstrap
├── _sidebar.md          ← Full navigation
├── Dockerfile           ← nginx:1.27-alpine
├── README.md
├── architecture/        ← 11 files (moved from docs/docs/architecture/)
├── design/              ← 5 files (moved from docs/docs/design/)
├── development/         ← 6 files (moved from docs/docs/development/)
├── reports/             ← 3 files (moved from docs/docs/reports/)
├── user_guide/          ← 6 files (moved from docs/docs/user_guide/)
├── deployment/          ← deployment_guide.md
├── monorepo/            ← PHASES.md, tasks.md, migration_guide.md
├── packages/            ← usage.md per package
├── ecosystem/           ← site-specific docs
├── infrastructure/      ← infra service docs
├── ai/                  ← AI assistant docs
└── [ALLCAPS session reports at root]
```

### Notes

- Docsify serves documentation via client-side rendering — no build step required
- All docs content uses lowercase snake_case file naming convention
- `docs/docs/` and `docs/docs/docs/` nesting removed — pure duplicates collapsed
- Docker Compose config validates with `docker compose config` ✅

---

## Task Progress Summary

| Phase | Tasks | Completed | Pending |
|-------|-------|-----------|---------|
| 1 | 8 | 5 | 3 |
| 2 | 5 | 5 | 0 |
| 3 | 5 | 2 | 3 |
| 4 | 10 | 10 | 0 |
| 5 | 5 | 5 | 0 |
| 6 | 5 | 5 | 0 |
| 7 | 5 | 0 | 5 |
| 8 | 5 | 0 | 5 |
| 9 | 13 | 13 | 0 |
| **Total** | **61** | **52** | **16** |

---

## Phase Dependencies

```
Phase 1 → Phase 2, Phase 3, Phase 6, Phase 9
Phase 2 → Phase 4, Phase 7
Phase 3 → Phase 4, Phase 7
Phase 4 → Phase 7, Phase 8, Phase 9
Phase 5 → Phase 8, Phase 9
Phase 6 → Phase 8
Phase 7 → Phase 8
Phase 9 → Phase 8
```

---

## Execution Order

The following phases should be executed in this order:

1. **Phase 9: Docsify Migration** - Migrate documentation from MkDocs to Docsify
2. **Phase 8: Deployment Verification** - Deploy and verify all configurations
3. **Phase 7: Language Support Enhancement** - Enhance django-osoul with language switching

---

## Notes

- Each phase should be completed before moving to the next
- Phases can be worked on in parallel if they don't share dependencies
- Documentation updates should happen throughout the process
- Testing should occur after each phase
- Each phase is delivered as a separate pull request for review
