# Monorepo Enhancement Phases

## Overview

This document tracks the progressive enhancement of the monorepo infrastructure through discrete, reviewable phases. Each phase addresses a specific aspect of the architecture with clear deliverables.

---

## Phase 1: Import Resolution & Package Initialization

**Status:** In Progress
**Start Date:** 2026-06-15
**Goal:** Fix broken imports and initialize library packages

### Tasks

- [x] 1.1 Fix `__main__.py` import to reference `cli` instead of `site_cli`
- [x] 1.2 Create `applications/__init__.py` to make cli a proper package
- [x] 1.3 Clone django-grep from GitHub repository
- [x] 1.4 Clone django-rseal from GitHub repository
- [x] 1.5 Clone django-osoul from GitHub repository
- [ ] 1.6 Enhance django-osoul package with language switching technique
- [ ] 1.7 Integrate _language.py from references with proper language detection
- [ ] 1.8 Create language switcher component in django-osoul

### Deliverables

- Fixed `__main__.py` that correctly imports from `cli`
- Package structure with proper `__init__.py`
- All three library packages cloned and ready for enhancement

---

## Phase 2: CLI/Make Command Enhancement

**Status:** In Progress
**Start Date:** 2026-06-15
**Goal:** Merge and enhance CLI functionality

### Tasks

- [x] 2.1 Merge `manage.py` and `cli.py` functionality into enhanced `manage.py`
- [x] 2.2 Add `validate-commands` method to `SiteCLI`
- [x] 2.3 Add `make-check` validation for dry-run make commands
- [ ] 2.4 Add make command error checking
- [ ] 2.5 Create command to validate all commands across sites

### Deliverables

- Unified `manage.py` entry point
- `validate-commands` command for comprehensive validation
- `make-check` command for dry-run validation

### Usage

```bash
# Validate commands for all sites
python manage.py validate-commands --all

# Validate commands for specific site
python manage.py validate-commands --site=ctc-research

# Validate make commands
python manage.py make-check --all

# Show all sites
python manage.py sites
```

---

## Phase 3: Utilities Migration

**Status:** Pending
**Start Date:** 2026-06-15
**Goal:** Migrate functionality from utilities.py to packages

### Tasks

- [ ] 3.1 Read and analyze current `applications/utilities.py`
- [ ] 3.2 Extract file utility functions to django-osoul
- [ ] 3.3 Extract language utility functions to django-osoul
- [ ] 3.4 Update imports across the monorepo
- [ ] 3.5 Delete `applications/utilities.py` after successful migration

### Deliverables

- Functionality moved to appropriate packages
- `applications/utilities.py` removed
- All imports updated to use package equivalents

---

## Phase 4: Docker Compose Structure

**Status:** Pending
**Start Date:** 2026-06-15
**Goal:** Create and enhance docker-compose files for each application

### Tasks

- [ ] 4.1 Create docker-compose files from backup templates
- [ ] 4.2 Ensure all networks are bridged
- [ ] 4.3 Link services correctly with proper network configuration
- [ ] 4.4 Add correct environment variables to all services
- [ ] 4.5 Add configurations from backups to main repo
- [ ] 4.6 Delete `backups/deploy` after verification

### Deliverables

- Complete docker-compose configuration for each application
- All services properly networked
- Environment configurations synced

---

## Phase 5: Documentation Enhancement

**Status:** Pending
**Start Date:** 2026-06-15
**Goal:** Create comprehensive and organized documentation

### Tasks

- [ ] 5.1 Enhance `docs/monorepo` with phases documentation
- [ ] 5.2 Create usage.md files for each component
- [ ] 5.3 Organize documentation for task tracking
- [ ] 5.4 Add detailed deployment guides
- [ ] 5.5 Create migration guides for each phase

### Deliverables

- Complete phase documentation
- Usage guides for all components
- Organized documentation structure

---

## Phase 6: Language Support Enhancement

**Status:** Pending
**Start Date:** 2026-06-15
**Goal:** Enhance django-osoul with language switching

### Tasks

- [ ] 6.1 Implement _language.py with proper language detection
- [ ] 6.2 Add language switcher component
- [ ] 6.3 Create language context processor
- [ ] 6.4 Add language toggle UI component
- [ ] 6.5 Test language switching across all sites

### Deliverables

- Working language switching in django-osoul
- Language toggle UI
- Context processor for templates

---

## Phase 7: Deployment Verification

**Status:** Pending
**Start Date:** 2026-06-15
**Goal:** Deploy and verify all configurations

### Tasks

- [ ] 7.1 Check deployment logs for all services
- [ ] 7.2 Deploy all containers
- [ ] 7.3 Verify configurations are correct
- [ ] 7.4 Verify services are linked properly
- [ ] 7.5 Run integration tests

### Deliverables

- All containers running successfully
- Correct configurations verified
- Integration tests passing

---

## Task Progress Summary

| Phase | Tasks | Completed | Pending |
|-------|-------|-----------|---------|
| 1 | 8 | 5 | 3 |
| 2 | 5 | 3 | 2 |
| 3 | 5 | 0 | 5 |
| 4 | 6 | 0 | 6 |
| 5 | 5 | 0 | 5 |
| 6 | 5 | 0 | 5 |
| 7 | 5 | 0 | 5 |
| **Total** | **39** | **8** | **31** |

---

## Phase Dependencies

```
Phase 1 → Phase 2, Phase 3
Phase 2 → Phase 4, Phase 7
Phase 3 → Phase 4, Phase 7
Phase 4 → Phase 7
Phase 5 → Phase 7
Phase 6 → Phase 7
```

---

## Notes

- Each phase should be completed before moving to the next
- Phases can be worked on in parallel if they don't share dependencies
- Documentation updates should happen throughout the process
- Testing should occur after each phase
