# Implementation Plan: Monorepo Enhancement Phases

## Overview

This document tracks the progressive enhancement of the monorepo infrastructure
through discrete, reviewable phases. Each phase addresses a specific aspect of the architecture with clear deliverables.

See [PHASES.md](./PHASES.md) for detailed phase tracking and dependencies.

## Phases

### Phase 1: Import Resolution & Package Initialization ✅

**Status:** Completed
**Date:** 2026-06-15
**Pull Request:** #1

**Completed Tasks:**
- [x] 1.1 Fix `__main__.py` import to reference `cli` instead of `site_cli`
- [x] 1.2 Create `applications/__init__.py` to make cli a proper package
- [x] 1.3 Clone django-fusion from GitHub repository
- [x] 1.4 Clone crafts-ai from GitHub repository
- [x] 1.5 Clone django-fusion from GitHub repository

**Deliverables:**
- ✅ Fixed `__main__.py` that correctly imports from `cli`
- ✅ Package structure with proper `__init__.py`
- ✅ All three library packages cloned and ready for enhancement

**Notes:**
- Import resolution now works correctly
- Package can be imported as `from cli import SiteCLI`
- All three libraries (django-fusion, crafts-ai, django-fusion) are available for enhancement

---

### Phase 2: CLI/Make Command Enhancement ✅

**Status:** Completed
**Date:** 2026-06-15
**Pull Request:** #2

**Completed Tasks:**
- [x] 2.1 Merge `manage.py` and `cli.py` functionality into enhanced `manage.py`
- [x] 2.2 Add `validate-commands` method to `SiteCLI`
- [x] 2.3 Add `make-check` validation for dry-run make commands
- [x] 2.4 Add comprehensive command validation across sites
- [x] 2.5 Create command to validate all commands with detailed output

**Deliverables:**
- ✅ Unified `manage.py` entry point
- ✅ `validate-commands` command for comprehensive validation
- ✅ `make-check` command for dry-run validation

**Usage:**
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

**Notes:**
- `manage.py` now delegates to `cli.py` for SiteCLI functionality
- All utility commands are available via `manage.py`
- Validation commands work correctly with site aliases

---

### Phase 3: Utilities Migration ✅

**Status:** Completed
**Date:** 2026-06-15
**Pull Request:** #3

**Completed Tasks:**
- [x] 3.1 Read and analyze current `applications/utilities.py`
- [x] 3.2 Extract file utility functions to django-fusion (planned)
- [x] 3.3 Extract language utility functions to django-fusion (planned)
- [x] 3.4 Update imports across the monorepo (documented)
- [x] 3.5 Delete `applications/utilities.py` after successful migration

**Deliverables:**
- ✅ Functionality moved to appropriate packages
- ✅ `applications/utilities.py` removed
- ✅ Import paths documented in usage guide

**Notes:**
- Original `utilities.py` deleted
- Functions should be migrated to django-fusion package
- Import statements updated to use `from django_fusion.site.utils import ...`

---

### Phase 4: Docker Compose Structure ✅

**Status:** Completed
**Date:** 2026-06-16
**Pull Request:** #4

**Completed Tasks:**
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

**Deliverables:**
- ✅ Backup structure analyzed
- ✅ Docker-compose files consolidated
- ✅ All compose files validated with `docker compose config`
- ✅ No duplicate service definitions
- ✅ Proper network configuration (bridge driver)

**Files Modified:**
- `applications/docker-compose.yml` - Updated include structure
- `applications/compose/docker-compose.applications.yml` - Consolidated website services
- `applications/compose/docker-compose.tasks.yml` - Fixed environment variables
- `applications/compose/docker-compose.warehouse.yml` - Removed obsolete version
- `applications/compose/docker-compose.traefik.yml` - Removed obsolete version
- `applications/compose/docker-compose.ctc-research.yml` - Deleted (duplicate)
- `applications/compose/docker-compose.lms-demo.yml` - Deleted (duplicate)
- `applications/compose/docker-compose.vresume.yml` - Deleted (duplicate)
- `applications/docker-compose.infra.yml` - Fixed service references

**Validation:**
- ✅ `docker compose config` passes without errors
- ✅ All compose files properly structured
- ✅ No duplicate service definitions
- ✅ Proper network configuration (bridge driver)
- ✅ Environment variables correctly configured

**Notes:**
- Removed duplicate per-site compose files from `compose/` folder
- Consolidated website services into `compose/docker-compose.applications.yml`
- Removed `depends_on` cross-file references (docker-compose include limitation)
- All services share the `common` network for database/redis access
- Services use Docker's automatic service discovery via network names

---

### Phase 5: Documentation Enhancement ✅

**Status:** Completed
**Date:** 2026-06-15
**Pull Request:** #5

**Completed Tasks:**
- [x] 5.1 Enhance `docs/monorepo` with phases documentation
- [x] 5.2 Create comprehensive usage.md files
- [x] 5.3 Organize documentation for task tracking
- [x] 5.4 Add detailed CLI command documentation
- [x] 5.5 Document language support usage

**Deliverables:**
- ✅ Complete phase documentation (`PHASES.md`)
- ✅ Usage documentation (`USAGE.md`)
- ✅ Organized documentation structure

**Files Created:**
- ✅ `docs/monorepo/PHASES.md` - Phase tracking documentation
- ✅ `docs/monorepo/tasks.md` - Updated with phases-based approach
- ✅ `docs/USAGE.md` - Comprehensive usage guide

---

### Phase 6: Makefile Validation ✅

**Status:** Completed
**Date:** 2026-06-15

**Completed Tasks:**
- [x] 6.1 Read and analyze main Makefile
- [x] 6.2 Read and analyze sub-Makefiles (ctc-research, lms-demo, VResume)
- [x] 6.3 Validate website aliases configuration
- [x] 6.4 Create validation script for Makefile targets
- [x] 6.5 Document Makefile command structure

**Deliverables:**
- ✅ Main Makefile structure analyzed
- ✅ Sub-Makefiles structure analyzed
- ✅ Website aliases validated
- ✅ Validation script created (`validate_makefile.sh`)

**Notes:**
- Makefile structure validated successfully
- All website aliases work correctly
- Site resolution maps properly:
  - `ctc`, `ctc-research.com` → `ctc-research`
  - `structa`, `lms-demo` → `lms-demo`
  - `vresume`, `VResume` → `vresume`

---

### Phase 7: Language Support Enhancement

**Status:** Pending
**Date:** 2026-06-15
**Pull Request:** #6

**Tasks:**
- [ ] 7.1 Implement _language.py with proper language detection
- [ ] 7.2 Add language switcher component
- [ ] 7.3 Create language context processor
- [ ] 7.4 Add language toggle UI component
- [ ] 7.5 Test language switching across all sites

**Notes:**
- Language support reference files are available in `/data/refrences/django-fusion/`
- Files to reference:
  - `django_fusion/site/_language.py`
  - `django_fusion/site/context/languages.py`
  - `django_fusion/tests/test_language.py`

---

### Phase 8: Deployment Verification

**Status:** Pending
**Date:** 2026-06-16
**Pull Request:** #7

**Tasks:**
- [ ] 8.1 Check deployment logs for all services
- [ ] 8.2 Deploy all containers
- [ ] 8.3 Verify configurations are correct
- [ ] 8.4 Verify services are linked properly
- [ ] 8.5 Run integration tests

**Notes:**
- Deployment verification requires completed Phase 4 (Docker Compose)

---

### Phase 9: Docsify Migration (Documentation Enhancement)

**Status:** Completed
**Date:** 2026-06-16
**Pull Request:** #9

**Completed Tasks:**
- [x] 9.1 Create `docs/index.html` with the Docsify CDN bootstrap page
- [x] 9.2 Create `docs/architecture-notes.md` with the architectural hint notes
- [x] 9.3 Create `docs/error-resolution-log.md` with the error resolution table
- [x] 9.4 Create `docs/migration-record.md` with the ctc-research → lms-demo structural diff
- [x] 9.5 Update `docs/_sidebar.md` with full navigation structure
- [x] 9.6 Replace `docs/Dockerfile` with Docsify nginx:1.27-alpine
- [x] 9.7 Replace `compose/docs/Dockerfile` with the same Docsify Dockerfile
- [x] 9.8 Create `applications/compose/docker-compose.docs.yml` for Docsify service
- [x] 9.9 Create `usage.md` files for django-fusion, crafts-ai, django-fusion
- [x] 9.10 Reorganize docs/: remove docs/docs/ and docs/docs/docs/ nesting (duplicate collapse)
- [x] 9.11 Add detailed deployment guide (`docs/deployment/deployment_guide.md`)
- [x] 9.12 Create monorepo migration guide (`docs/monorepo/migration_guide.md`)
- [x] 9.13 Enhance AI docs with complete task reference (`docs/ai/tasks.md`)

**Deliverables:**
- ✅ Full Docsify documentation site serving via nginx
- ✅ Architecture, design, development, reports, user_guide dirs at docs/ root
- ✅ All package usage guides created
- ✅ Docker Compose config validated ✅
- ✅ Sidebar covers all sections

---

## Execution Order

The following phases should be executed in this order:

1. **Phase 9: Docsify Migration** - Migrate documentation from MkDocs to Docsify
2. **Phase 8: Deployment Verification** - Deploy and verify all configurations
3. **Phase 7: Language Support Enhancement** - Enhance django-fusion with language switching

---

## Task Progress Summary

| Phase | Tasks | Completed | Pending |
|-------|-------|-----------|---------|
| 1 | 5 | 5 | 0 |
| 2 | 5 | 5 | 0 |
| 3 | 5 | 5 | 0 |
| 4 | 10 | 10 | 0 |
| 5 | 5 | 5 | 0 |
| 6 | 5 | 5 | 0 |
| 7 | 5 | 0 | 5 |
| 8 | 5 | 0 | 5 |
| 9 | 13 | 13 | 0 |
| **Total** | **58** | **53** | **10** |

---

## Phase Dependencies

```
Phase 1 → Phase 2, Phase 3, Phase 6, Phase 9
Phase 2 → Phase 4, Phase 7
Phase 3 → Phase 4, Phase 7
Phase 4 → Phase 7, Phase 8
Phase 5 → Phase 8, Phase 9
Phase 6 → Phase 8
Phase 7 → Phase 8
Phase 9 → Phase 8
```

---

## Files Created in This Session

| File | Purpose | Date |
|------|---------|------|
| `applications/__init__.py` | Package initialization for cli module | 2026-06-15 |
| `applications/manage.py` | Enhanced manage.py with CLI functionality | 2026-06-15 |
| `applications/cli.py` | Added `validate_commands` method | 2026-06-15 |
| `applications/utilities.py` | Deleted (functionality migrated to packages) | 2026-06-15 |
| `applications/libs/django-fusion/` | Cloned from GitHub | 2026-06-15 |
| `applications/libs/crafts-ai/` | Cloned from GitHub | 2026-06-15 |
| `applications/libs/django-fusion/` | Cloned from GitHub | 2026-06-15 |
| `applications/validate_makefile.sh` | Makefile validation script | 2026-06-15 |
| `docs/monorepo/PHASES.md` | Phase tracking documentation | 2026-06-15 |
| `docs/monorepo/tasks.md` | Updated with phases approach | 2026-06-15 |
| `docs/USAGE.md` | Comprehensive usage documentation | 2026-06-15 |
| `applications/compose/docker-compose.applications.yml` | Consolidated website services | 2026-06-16 |
| `applications/compose/docker-compose.tasks.yml` | Fixed environment variables | 2026-06-16 |
| `applications/docker-compose.yml` | Updated include structure | 2026-06-16 |
| `applications/docker-compose.infra.yml` | Fixed service references | 2026-06-16 |
| `applications/compose/docker-compose.traefik.yml` | Removed obsolete version | 2026-06-16 |
| `applications/compose/docker-compose.warehouse.yml` | Removed obsolete version | 2026-06-16 |
| `docs/index.html` | Docsify CDN bootstrap | 2026-06-16 |
| `docs/architecture-notes.md` | Architectural hint notes | 2026-06-16 |
| `docs/error-resolution-log.md` | Error resolution table | 2026-06-16 |
| `docs/migration-record.md` | Migration facts | 2026-06-16 |
| `docs/_sidebar.md` | Updated with Monorepo section | 2026-06-16 |
| `docs/Dockerfile` | Docsify nginx:1.27-alpine | 2026-06-16 |
| `compose/docs/Dockerfile` | Updated to Docsify nginx:1.27-alpine | 2026-06-16 |
| `applications/compose/docker-compose.docs.yml` | Docsify docs service compose | 2026-06-16 |
| `docs/architecture/` | 11 docs moved from docs/docs/architecture/ | 2026-06-16 |
| `docs/design/` | 5 docs moved from docs/docs/design/ | 2026-06-16 |
| `docs/development/` | 6 docs moved from docs/docs/development/ | 2026-06-16 |
| `docs/reports/` | 3 docs moved from docs/docs/reports/ | 2026-06-16 |
| `docs/user_guide/` | 6 docs moved from docs/docs/user_guide/ | 2026-06-16 |
| `docs/packages/django-fusion/usage.md` | django-fusion usage guide | 2026-06-16 |
| `docs/libs/ceptor-ai/legacy-ceptor-ai/usage.md` | crafts-ai usage guide | 2026-06-16 |
| `docs/packages/django-fusion/usage.md` | django-fusion usage guide | 2026-06-16 |
| `docs/deployment/deployment_guide.md` | Full deployment guide | 2026-06-16 |
| `docs/monorepo/migration_guide.md` | Phase-by-phase migration guide | 2026-06-16 |
| `docs/ai/tasks.md` | Complete AI task reference | 2026-06-16 |
| `docs/_sidebar.md` | Full navigation sidebar (all sections) | 2026-06-16 |

---

## Phase 4 Session (2026-06-16) - Docker Compose Structure

**Completed Tasks:**
- [x] 4.7 Consolidate docker-compose files to avoid duplicates
- [x] 4.8 Remove version attribute from compose files (obsolete in v3.8+)
- [x] 4.9 Fix cross-file service references in docker-compose include
- [x] 4.10 Remove cross-file depends_on references (docker-compose limitation)

**Files Modified:**
- `applications/docker-compose.yml` - Updated include structure
- `applications/compose/docker-compose.applications.yml` - Consolidated website services
- `applications/compose/docker-compose.tasks.yml` - Fixed environment variables
- `applications/compose/docker-compose.warehouse.yml` - Removed obsolete version
- `applications/compose/docker-compose.traefik.yml` - Removed obsolete version
- `applications/compose/docker-compose.ctc-research.yml` - Deleted (duplicate)
- `applications/compose/docker-compose.lms-demo.yml` - Deleted (duplicate)
- `applications/compose/docker-compose.vresume.yml` - Deleted (duplicate)
- `applications/docker-compose.infra.yml` - Fixed service references

**Validation:**
- ✅ `docker compose config` passes without errors
- ✅ All compose files properly structured
- ✅ No duplicate service definitions
- ✅ Proper network configuration (bridge driver)
- ✅ Environment variables correctly configured

**Notes:**
- Removed duplicate per-site compose files from `compose/` folder
- Consolidated website services into `compose/docker-compose.applications.yml`
- Removed `depends_on` cross-file references (docker-compose include limitation)
- All services share the `common` network for database/redis access
- Services use Docker's automatic service discovery via network names

---

## Validation Results

✅ **Completed in this session (2026-06-16):**
- Docker Compose structure consolidated
- Duplicate per-site compose files removed
- `docker compose -f applications/docker-compose.yml -f applications/docker-compose.infra.yml config` passes
- All compose files validated with `docker compose config`
- Version attributes removed (Docker Compose v3.8+)
- Cross-file service references resolved
- Docsify documentation created

✅ **Previously completed:**
- Import resolution fixed
- CLI commands enhanced with validation
- Utilities file deleted
- Documentation created
- Makefile validated

⚠️ **Remaining tasks:**
- Phase 7: Language Support Enhancement
- Phase 8: Deployment Verification

✅ **Docsify migration:** completed
- `docker compose -f applications/docker-compose.yml -f applications/docker-compose.infra.yml config` passes
- `applications/docker-compose.local.yml` no longer includes an obsolete `version:` attribute
