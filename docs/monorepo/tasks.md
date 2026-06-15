# Implementation Plan: Monorepo Enhancement Phases

## Overview

This document tracks the progressive enhancement of the monorepo infrastructure through discrete, reviewable phases. Each phase addresses a specific aspect of the architecture with clear deliverables.

See [PHASES.md](./PHASES.md) for detailed phase tracking and dependencies.

## Phases

### Phase 1: Import Resolution & Package Initialization ✅

**Status:** Completed
**Date:** 2026-06-15

**Tasks:**
- [x] 1.1 Fix `__main__.py` import to reference `cli` instead of `site_cli`
- [x] 1.2 Create `applications/__init__.py` to make cli a proper package
- [x] 1.3 Clone django-grep from GitHub repository
- [x] 1.4 Clone django-rseal from GitHub repository
- [x] 1.5 Clone django-osoul from GitHub repository

**Deliverables:**
- Fixed `__main__.py` that correctly imports from `cli`
- Package structure with proper `__init__.py`
- All three library packages cloned and ready for enhancement

**Pull Request:** #1 - Phase 1: Import Resolution & Package Initialization

---

### Phase 2: CLI/Make Command Enhancement ✅

**Status:** Completed
**Date:** 2026-06-15

**Tasks:**
- [x] 2.1 Merge `manage.py` and `cli.py` functionality into enhanced `manage.py`
- [x] 2.2 Add `validate-commands` method to `SiteCLI`
- [x] 2.3 Add `make-check` validation for dry-run make commands
- [ ] 2.4 Add make command error checking
- [ ] 2.5 Create command to validate all commands across sites
md` volume mounts, change docs bind mount to `/data/docs:/usr/share/nginx/html:ro`, update healthcheck to use `wget`

**Deliverables:**
- Unified `manage.py` entry point
- `validate-commands` command for comprehensive validation
- `make-check` command for dry-run validation

**Usage:**
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

**Pull Request:** #2 - Phase 2: CLI/Make Command Enhancement

---

### Phase 3: Utilities Migration

**Status:** Pending
**Date:** 2026-06-15

**Tasks:**
- [ ] 3.1 Read and analyze current `applications/utilities.py`
- [ ] 3.2 Extract file utility functions to django-osoul
- [ ] 3.3 Extract language utility functions to django-osoul
- [ ] 3.4 Update imports across the monorepo
- [ ] 3.5 Delete `applications/utilities.py` after successful migration

**Deliverables:**
- Functionality moved to appropriate packages
- `applications/utilities.py` removed
- All imports updated to use package equivalents

**Pull Request:** #3 - Phase 3: Utilities Migration

---

### Phase 4: Docker Compose Structure

**Status:** Pending
**Date:** 2026-06-15

**Tasks:**
- [ ] 4.1 Create docker-compose files from backup templates
- [ ] 4.2 Ensure all networks are bridged
- [ ] 4.3 Link services correctly with proper network configuration
- [ ] 4.4 Add correct environment variables to all services
- [ ] 4.5 Add configurations from backups to main repo
- [ ] 4.6 Delete `backups/deploy` after verification

**Deliverables:**
- Complete docker-compose configuration for each application
- All services properly networked
- Environment configurations synced

**Pull Request:** #4 - Phase 4: Docker Compose Structure

---

### Phase 5: Documentation Enhancement

**Status:** Pending
**Date:** 2026-06-15

**Tasks:**
- [ ] 5.1 Create `docs/index.html` with the Docsify CDN bootstrap page (content specified in design.md)
- [ ] 5.2 Create `docs/architecture-notes.md` with the architectural hint notes from design.md §Architecture
- [ ] 5.3 Create `docs/error-resolution-log.md` with the error resolution table (single entry: `mnagement` typo in lessons.py line 12)
- [ ] 5.4 Create `docs/migration-record.md` with the ctc-research → lms-demo structural diff and theme migration facts from design.md §Migration Log
- [ ] 5.5 Update `docs/_sidebar.md` to add the Monorepo section (Architecture Notes, Error Resolution Log, Migration Record) at the top, retaining all existing sections
- [ ] 5.6 Replace `/data/docs/Dockerfile` with the Docsify `nginx:1.27-alpine` Dockerfile from design.md §Docsify Dockerfile
- [ ] 5.7 Replace `/data/deploy/compose/docs/Dockerfile` with the same Docsify Dockerfile
- [ ] 5.8 Update `/data/deploy/applications/docker-compose.docs.yml`: use the new image, remove `mkdocs.yml` and `README.- [ ] 5.9 Create usage.md files for each component
- [ ] 5.10 Organize documentation for task tracking and remove duplecated files and enhance the content structures and files lowwer case snake case
- [ ] 5.11 Add detailed deployment guides
- [ ] 5.12 Create migration guides for each phase
- [ ] 5.13 enhance and improve with project contents guides coolify/docs/ai with the script to give a context with the configs structures and website build and notes with each component args and usage and what data could be added as section and how to replace component with another at some tasks with hints and note as prompts on tasks


**Deliverables:**
- Complete phase documentation
- Usage guides for all components
- Organized documentation structure

**Pull Request:** #5 - Phase 5: Documentation Enhancement

---

### Phase 6: Language Support Enhancement

**Status:** Pending
**Date:** 2026-06-15

**Tasks:**
- [ ] 6.1 Implement _language.py with proper language detection
- [ ] 6.2 Add language switcher component
- [ ] 6.3 Create language context processor
- [ ] 6.4 Add language toggle UI component
- [ ] 6.5 Test language switching across all sites

**Deliverables:**
- Working language switching in django-osoul
- Language toggle UI
- Context processor for templates

**Pull Request:** #6 - Phase 6: Language Support Enhancement

---

### Phase 7: Deployment Verification

**Status:** Pending
**Date:** 2026-06-15

**Tasks:**
- [ ] 7.1 Check deployment logs for all services
- [ ] 7.2 Deploy all containers
- [ ] 7.3 Verify configurations are correct
- [ ] 7.4 Verify services are linked properly
- [ ] 7.5 Run integration tests

**Deliverables:**
- All containers running successfully
- Correct configurations verified
- Integration tests passing

**Pull Request:** #7 - Phase 7: Deployment Verification

---

## Task Progress Summary

| Phase | Tasks | Completed | Pending |
|-------|-------|-----------|---------|
| 1 | 5 | 5 | 0 |
| 2 | 3 | 3 | 0 |
| 3 | 5 | 0 | 5 |
| 4 | 6 | 0 | 6 |
| 5 | 5 | 1 | 4 |
| 6 | 5 | 0 | 5 |
| 7 | 5 | 0 | 5 |
| **Total** | **34** | **9** | **25** |

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
- Each phase is delivered as a separate pull request for review

---

## Previous Task History

The following tasks were from the original tasks.md and have been replaced by the phased approach:

### Group 1: Architectural Cleanup (REPLACED)
- Removed stale aliases
- Consolidated settings
- Build verification

### Group 2: Log Directory Isolation (REPLACED)
- Added WEBSITE_IDENTIFIER derivation
- Added mkdir guards
- Updated FileHandler paths

### Group 3: Docsify Migration (REPLACED)
- Created Docsify bootstrap
- Created architecture notes
- Created migration record

### Group 4: Docker-Compose Overlay (REPLACED)
- Created docker-compose.infra.yml
- Added named volumes
- Added log volume mounts

### Group 5: Governance Pipeline (REPLACED)
- Installed husky, lint-staged, etc.
- Created pre-commit hooks
- Created import check script

### Group 6: Verification (REPLACED)
- Verified file content
- Verified Docsify service
- Verified log isolation

All previous tasks have been incorporated into the phased approach above.
## Task Dependency Graph

```json
{
  "waves": [
    {
      "wave": 1,
      "tasks": ["1.1", "1.2", "2.1", "2.2", "2.3", "3.1", "3.2", "3.3", "3.4", "3.5", "3.6", "3.7", "5.1", "5.2"]
    },
    {
      "wave": 2,
      "tasks": ["1.3", "2.4", "2.5", "3.8", "5.3", "5.4", "5.5", "5.6", "5.7", "5.8"],
      "dependsOn": ["wave1"]
    },
    {
      "wave": 3,
      "tasks": ["4.1", "4.2", "4.3", "5.9", "5.10"],
      "dependsOn": ["wave2"]
    },
    {
      "wave": 4,
      "tasks": ["6.1", "6.2", "6.3", "6.4", "6.5"],
      "dependsOn": ["wave3"]
    }
  ]
}
```

Group 1 (cleanup) → Group 5, task 5.9 (import check validates the cleanup)
Group 2 (log isolation) → Group 4 (compose overlay needs volume paths confirmed)
Group 3 (Docsify content) → Group 4, task 4.1 (compose overlay references the docs image)
Groups 1, 2, 3 → Group 6 (verification)

## Notes

The bundle-size audit (task 5.7) will likely report that the `client` and `marketing` budgets are exceeded by the current large bundles. This is expected — the budgets set a target for a follow-on vendor-split task and serve as a baseline measurement rather than a hard gate in the initial rollout. The `admin` budget at 120 kB is more likely to pass given lms-demo's admin bundle is primarily Quill plus admin CSS.

The `@theme`, `@layouts`, `@usecases` aliases are confirmed stale based on live codebase inspection. Task 1.1 is the single highest-priority item — it eliminates a latent build failure risk that could surface if any developer adds a new file importing `@theme`.
