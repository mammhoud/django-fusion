# Master Task List: Ecosystem-Wide Architectural Refactoring

Generated: 2026-04-14 21:34:45

## Summary

- **Total Specs**: 7
  - Completed: 3
  - In Progress: 4
- **Total Tasks**: 353
  - Completed: 207
  - Incomplete: 146
- **Overall Completion**: 58.6%

## Spec Status Overview

### 🔄 core-logic-consolidation-and-app-restructure
- **Status**: In Progress
- **Completion**: 36% (18/50)
- **Files**: requirements.md ✓, design.md ✓, tasks.md ✓

### ✅ ctc-research-deployment-verification
- **Status**: Complete
- **Completion**: 100% (105/105)
- **Files**: requirements.md ✓, design.md ✓, tasks.md ✓

### 🔄 django-refactoring
- **Status**: In Progress
- **Completion**: N/A (0/0)
- **Files**: requirements.md ✓, design.md ✓, tasks.md ✓

### 🔄 ecosystem-architectural-refactoring
- **Status**: In Progress
- **Completion**: 0% (0/114)
- **Files**: requirements.md ✓, design.md ✓, tasks.md ✓

### ✅ finalize-refactor
- **Status**: Complete
- **Completion**: 100% (69/69)
- **Files**: requirements.md ✓, design.md ✓, tasks.md ✓

### 🔄 phase-2-website-sync-completion
- **Status**: In Progress
- **Completion**: N/A (0/0)
- **Files**: requirements.md ✓, design.md ✓, tasks.md ✓

### ✅ phase-3-production-deployment
- **Status**: Complete
- **Completion**: 100% (15/15)
- **Files**: requirements.md ✓, design.md ✗, tasks.md ✓

## Incomplete Tasks by Spec

### core-logic-consolidation-and-app-restructure
**Incomplete: 32 main tasks**

#### 10.1 Apply standard sub-module layout to `accounts` in both websites

- [ ] No subtasks defined

#### 10.2 Apply standard sub-module layout to `lms` (ctc) and `alliance` (structa)

- [ ] No subtasks defined

#### 10.3 Apply standard sub-module layout to `content` in both websites

- [ ] No subtasks defined

#### 11.1 Update imports for django-osoul classes in both websites

- [ ] No subtasks defined

#### 11.2 Update imports for django-rseal classes in both websites

- [ ] No subtasks defined

#### 11.3 Update all `apps.<old_name>` import references after app renames

- [ ] No subtasks defined

#### 11.4 Delete original source files after import verification

- [ ] No subtasks defined

#### 13.1 Add missing test utilities to django-grep

- [ ] No subtasks defined

#### 13.2 Migrate test base classes in both websites

- [ ] No subtasks defined

#### 13.3 Migrate test factories in both websites

- [ ] No subtasks defined

#### 13.4 Migrate custom test assertions in both websites

- [ ] No subtasks defined

#### 13.5 Migrate test fixtures in both websites

- [ ] No subtasks defined

#### 13.6 Migrate test mixins in both websites

- [ ] No subtasks defined

#### 13.7 Move shared-package tests to package test suites

- [ ] No subtasks defined

#### 15.1 Write integration tests for `CertificateServiceBase`

- [ ] No subtasks defined

#### 16.1 Create `.importlinter` config at repo root

- [ ] No subtasks defined

#### 16.2 Add `lint-imports` step to CI pipeline

- [ ] No subtasks defined

#### 21.1 Write `MIGRATION_GUIDE.md`

- [ ] No subtasks defined

#### 21.2 Write `ARCHITECTURE.md`

- [ ] No subtasks defined

#### 21.3 Update `README.md` files for `django-osoul`, `django-rseal`, and `django-grep`

- [ ] No subtasks defined

#### 8.1 Rename `handlers` to `accounts` in ctc-research.com

- [ ] No subtasks defined

#### 8.2 Generate migration for `handlers` to `accounts` rename in ctc-research.com

- [ ] No subtasks defined

#### 8.3 Rename `LMS` to `lms` in ctc-research.com

- [ ] No subtasks defined

#### 8.4 Generate migration for `LMS` to `lms` rename in ctc-research.com

- [ ] No subtasks defined

#### 8.5 Rename `pages` to `content` in ctc-research.com

- [ ] No subtasks defined

#### 8.6 Generate migration for `pages` to `content` rename in ctc-research.com

- [ ] No subtasks defined

#### 9.1 Rename `handlers` to `accounts` in structa.cloud

- [ ] No subtasks defined

#### 9.2 Generate migration for `handlers` to `accounts` rename in structa.cloud

- [ ] No subtasks defined

#### 9.3 Rename `LMS` to `alliance` in structa.cloud

- [ ] No subtasks defined

#### 9.4 Generate migration for `LMS` to `alliance` rename in structa.cloud

- [ ] No subtasks defined

#### 9.5 Rename `pages` to `content` in structa.cloud

- [ ] No subtasks defined

#### 9.6 Generate migration for `pages` to `content` rename in structa.cloud

- [ ] No subtasks defined


### ecosystem-architectural-refactoring
**Incomplete: 114 main tasks**

#### 1.1 Scan all Python modules across ctc-research.com/apps/, structa.cloud/apps/, and venv/libs/ packages and produce DUPLICATION_REPORT.md listing every duplicated class, function, and module with source locations and similarity percentage (≥70% threshold)

**Subtasks:**
- [ ] 1.1.1 Write scripts/analyze_duplication.py implementing DuplicationAnalyzer with AST-based comparison
- [ ] 1.1.2 Run analyzer against all three directory trees and capture output
- [ ] 1.1.3 Categorize each duplicate as extract-to-osoul, extract-to-rseal, extract-to-grep, already-extracted, or project-specific
- [ ] 1.1.4 Write DUPLICATION_REPORT.md with full results including cross-references to existing specs

#### 1.2 Detect all boundary violations and misplaced responsibilities across the ecosystem

**Subtasks:**
- [ ] 1.2.1 Write scripts/check_boundaries.py implementing BoundaryChecker with the four rule sets (nawaai-no-django, osoul-no-wagtail, rseal-no-projects, grep-test-only)
- [ ] 1.2.2 Run boundary checker and write BOUNDARY_VIOLATIONS.md listing every violation with file, line, import statement, and fix suggestion
- [ ] 1.2.3 Write scripts/detect_cycles.py implementing CircularDependencyDetector using networkx
- [ ] 1.2.4 Run cycle detector and append cycle report to BOUNDARY_VIOLATIONS.md

#### 1.3 Scan all specs in .kiro/specs/ for incomplete tasks and generate master task list

**Subtasks:**
- [ ] 1.3.1 Write scripts/track_spec_status.py implementing SpecStatusTracker
- [ ] 1.3.2 Run tracker against all specs and write MASTER_TASK_LIST.md with prioritized incomplete tasks grouped by spec

#### 1.4 Build complete execution plan with dependency ordering and validation checkpoints

**Subtasks:**
- [ ] 1.4.1 Write scripts/plan_implementation.py implementing ImplementationPlanner
- [ ] 1.4.2 Produce IMPLEMENTATION_PLAN.md with all phases, task dependencies (topological order), effort estimates, and rollback points
- [ ] 1.4.3 Create git tags for rollback points: rollback-phase-1-start, rollback-phase-2-start, etc.
- [ ] 1.4.4 Write BACKUP_LOG.md template and create initial database and media backups

#### 10.1 Scan all pyproject.toml files and identify version conflicts

**Subtasks:**
- [ ] 10.1.1 Write scripts/analyze_dependencies.py implementing DependencyAnalyzer
- [ ] 10.1.2 Run analyzer against all pyproject.toml files in projects and packages
- [ ] 10.1.3 Write DEPENDENCY_CONFLICTS.md listing all version conflicts with recommended unified versions

#### 10.2 Unify dependency versions across all pyproject.toml files

**Subtasks:**
- [ ] 10.2.1 Update ctc-research.com/pyproject.toml with unified versions
- [ ] 10.2.2 Update structa.cloud/pyproject.toml with unified versions
- [ ] 10.2.3 Update venv/libs/django-osoul/pyproject.toml with unified versions
- [ ] 10.2.4 Update venv/libs/django-rseal/pyproject.toml with unified versions
- [ ] 10.2.5 Update venv/libs/django-grep/pyproject.toml with unified versions
- [ ] 10.2.6 Update venv/libs/nawaai/pyproject.toml with unified versions

#### 10.3 Remove unused dependencies from all pyproject.toml files

**Subtasks:**
- [ ] 10.3.1 Run scripts/analyze_dependencies.py find_unused_dependencies
- [ ] 10.3.2 Remove each unused dependency from the appropriate pyproject.toml
- [ ] 10.3.3 Run tests after each removal to verify nothing breaks

#### 10.4 Ensure all packages declare their dependencies explicitly

**Subtasks:**
- [ ] 10.4.1 Verify django_osoul/pyproject.toml lists all its direct dependencies
- [ ] 10.4.2 Verify django_rseal/pyproject.toml lists all its direct dependencies including django_osoul
- [ ] 10.4.3 Verify django_grep/pyproject.toml lists all its direct dependencies
- [ ] 10.4.4 Verify nawaai/pyproject.toml lists only pure Python dependencies

#### 10.5 Update uv.lock files after all dependency changes

**Subtasks:**
- [ ] 10.5.1 Run uv lock in ctc-research.com
- [ ] 10.5.2 Run uv lock in structa.cloud
- [ ] 10.5.3 Run full test suite in both projects to verify compatibility

#### 11.1 Scan git history for deleted files in the last 6 months

**Subtasks:**
- [ ] 11.1.1 Write scripts/recover_code.py implementing CodeRecoverySystem
- [ ] 11.1.2 Run scan_git_history() and identify all deleted Python files
- [ ] 11.1.3 Run find_references() for each deleted file to check if still referenced in current codebase
- [ ] 11.1.4 Write RECOVERY_CANDIDATES.md listing all deleted files still referenced, with recovery priority

#### 11.2 Recover and reintegrate deleted code

**Subtasks:**
- [ ] 11.2.1 For each high-priority recovery candidate, run recover_file() to extract from git history
- [ ] 11.2.2 Place recovered code in the correct package location per the new architecture
- [ ] 11.2.3 Update all imports to reference the new location
- [ ] 11.2.4 Add or verify test coverage for recovered code
- [ ] 11.2.5 Write RECOVERY_REPORT.md documenting all recovered files

#### 11.3 For code that cannot be recovered, document and create reimplementation tasks

**Subtasks:**
- [ ] 11.3.1 For each unrecoverable file, document the missing functionality in RECOVERY_REPORT.md
- [ ] 11.3.2 Create specific reimplementation tasks in this file under a "Reimplementation" section

#### 11.4 Compare recent feature branches with main and identify improvements to merge

**Subtasks:**
- [ ] 11.4.1 Write scripts/analyze_branches.py implementing BranchAnalyzer
- [ ] 11.4.2 Run list_recent_branches() to find all branches from last 3 months
- [ ] 11.4.3 Run compare_with_main() for each branch and identify improvements
- [ ] 11.4.4 Write MERGE_CANDIDATES.md listing improvements with merge priority

#### 11.5 Merge improvements from feature branches using quality-preserving strategy

**Subtasks:**
- [ ] 11.5.1 Write scripts/intelligent_merge.py implementing IntelligentMerger
- [ ] 11.5.2 For each high-priority improvement, run merge_with_validation()
- [ ] 11.5.3 Verify no duplication introduced, no boundary violations, no test regressions
- [ ] 11.5.4 Write MERGE_REPORT.md documenting all merged improvements

#### 12.1 Identify all parsers and serializers in the ecosystem

**Subtasks:**
- [ ] 12.1.1 Write scripts/detect_parsers.py implementing ParserDetector
- [ ] 12.1.2 Run find_all_parsers() and find_all_serializers() across entire codebase
- [ ] 12.1.3 Write PARSER_INVENTORY.md listing all parsers and serializers with their input/output types

#### 12.2 Verify each parser has a corresponding pretty printer

**Subtasks:**
- [ ] 12.2.1 For each parser without a pretty printer, create one in the same module
- [ ] 12.2.2 Pretty printer must accept the parser's output type and return valid input format
- [ ] 12.2.3 Document the grammar being parsed in module-level docstring

#### 12.3 Implement round-trip property tests for all parsers

**Subtasks:**
- [ ] 12.3.1 For each parser, create a property-based test: given valid_input, parse(pretty_print(parse(valid_input))) == parse(valid_input)
- [ ] 12.3.2 Use Hypothesis with appropriate strategies (st_email, st_slug, st_uuid, or custom strategies)
- [ ] 12.3.3 Verify parsers return descriptive errors for invalid inputs
- [ ] 12.3.4 Run all round-trip tests and verify they pass

#### 13.1 Create .importlinter configuration file

**Subtasks:**
- [ ] 13.1.1 Create .importlinter at workspace root with all four contracts: nawaai-no-django, osoul-no-wagtail, rseal-no-projects, grep-test-only
- [ ] 13.1.2 Add dependency-direction layers contract
- [ ] 13.1.3 Run import-linter --config .importlinter and verify zero violations
- [ ] 13.1.4 Fix any remaining violations

#### 13.2 Create GitHub Actions workflow for architecture validation

**Subtasks:**
- [ ] 13.2.1 Create .github/workflows/architecture-validation.yml with jobs: boundary-check, duplication-check, test-all-packages, test-projects, import-check
- [ ] 13.2.2 Configure boundary-check job to run import-linter and fail on any violation
- [ ] 13.2.3 Configure duplication-check job to run scripts/analyze_duplication.py --threshold 0.70 --fail-on-violation
- [ ] 13.2.4 Configure test-all-packages job with matrix strategy for all four packages
- [ ] 13.2.5 Configure test-projects job with matrix strategy for both projects
- [ ] 13.2.6 Configure import-check job to run scripts/check_imports.py --fail-on-error
- [ ] 13.2.7 Verify workflow runs in under 10 minutes

#### 13.3 Verify CI passes on current codebase

**Subtasks:**
- [ ] 13.3.1 Push to a test branch and verify all CI jobs pass
- [ ] 13.3.2 Fix any CI failures
- [ ] 13.3.3 Merge to main only after all CI jobs pass

#### 14.1 Create ARCHITECTURE.md at workspace root

**Subtasks:**
- [ ] 14.1.1 Document the package dependency graph as a Mermaid diagram: stdlib → nawaai → django_osoul → django_rseal → projects
- [ ] 14.1.2 Document each package's responsibilities and what it contains
- [ ] 14.1.3 Document all boundary rules with examples of allowed and forbidden imports
- [ ] 14.1.4 Document domain organization (accounts, content, lms/alliance, messaging, cart, forms)
- [ ] 14.1.5 Document the thin layer pattern with a CartService example

#### 14.10 Organize .kiro/specs/ with clear status markers

**Subtasks:**
- [ ] 14.10.1 Verify all completed specs have all tasks marked [x]
- [ ] 14.10.2 Update .kiro/specs-organized/README.md with current status of all specs
- [ ] 14.10.3 Ensure every spec has requirements.md, design.md, and tasks.md

#### 14.2 Create MIGRATION_GUIDE.md at workspace root

**Subtasks:**
- [ ] 14.2.1 List every changed import path in the format: Before: from apps.handlers.managers... → After: from django_osoul.managers...
- [ ] 14.2.2 Document all app renames (handlers→accounts, LMS→lms/alliance, pages→content)
- [ ] 14.2.3 Document all deprecated APIs and their replacements
- [ ] 14.2.4 Include troubleshooting section for common migration errors

#### 14.3 Write comprehensive README.md for django_osoul

**Subtasks:**
- [ ] 14.3.1 Document package purpose: "Pure Django foundation layer — models, managers, mixins, utils, comp, contrib"
- [ ] 14.3.2 Document installation, quick start, and all public APIs with usage examples
- [ ] 14.3.3 Document boundary rules: must not import wagtail, celery, or django_rseal
- [ ] 14.3.4 Document all sub-modules: handlers/, managers/, mixins/, utils/, comp/, contrib/, middlewares/, filters/, forms/, backends/, adapters/, services/

#### 14.4 Write comprehensive README.md for django_rseal

**Subtasks:**
- [ ] 14.4.1 Document package purpose: "Automation layer — pipelines, services, workflows, email, signals, admin, cache, commands"
- [ ] 14.4.2 Document installation, quick start, and all public APIs with usage examples
- [ ] 14.4.3 Document CartServiceBase thin subclass pattern with full code example
- [ ] 14.4.4 Document all Wagtail components: blocks, snippets, hooks, admin customizations

#### 14.5 Write comprehensive README.md for django_grep

**Subtasks:**
- [ ] 14.5.1 Document package purpose: "Unified testing framework — seeder, test base, fixtures, factories, assertions, pytest plugin, health checks"
- [ ] 14.5.2 Document BaseTestCase usage and all Hypothesis helpers (st_email, st_slug, st_uuid)
- [ ] 14.5.3 Document health check endpoints and project integration via include('django_grep.health.urls')
- [ ] 14.5.4 Document pytest plugin registration

#### 14.6 Write comprehensive README.md for nawaai

**Subtasks:**
- [ ] 14.6.1 Document package purpose: "Pure Python AI/MCP toolkit — ai, chat, mcp, orchestrator, seeder"
- [ ] 14.6.2 Document boundary rule: zero Django imports
- [ ] 14.6.3 Document all public APIs with usage examples

#### 14.7 Write comprehensive README.md for ctc-research.com

**Subtasks:**
- [ ] 14.7.1 Document project purpose, features, prerequisites, installation, configuration
- [ ] 14.7.2 Document how to run locally and in Docker
- [ ] 14.7.3 Document project structure showing thin layer pattern
- [ ] 14.7.4 Document testing and deployment

#### 14.8 Write comprehensive README.md for structa.cloud

**Subtasks:**
- [ ] 14.8.1 Same structure as ctc-research.com README
- [ ] 14.8.2 Document alliance/ app instead of lms/

#### 14.9 Update all module-level docstrings to reference canonical import paths

**Subtasks:**
- [ ] 14.9.1 For every class moved to a package, add docstring: "Canonical import: from django_osoul.managers import RoleHierarchyManager"
- [ ] 14.9.2 For every thin subclass in projects, add docstring: "Delegates to django_rseal.pipelines.services.CartServiceBase"
- [ ] 14.9.3 Run grep to verify all moved classes have canonical import docstrings

#### 15.1 Verify all migrations have reverse operations

**Subtasks:**
- [ ] 15.1.1 Write scripts/validate_migrations.py implementing MigrationValidator
- [ ] 15.1.2 Run check_all_migrations() across both projects
- [ ] 15.1.3 For each migration without a reverse operation, add the reverse operation
- [ ] 15.1.4 Write MIGRATION_SAFETY_REPORT.md listing all migrations and their reversal status

#### 15.2 Test migration reversal for all app rename migrations

**Subtasks:**
- [ ] 15.2.1 Run python manage.py migrate accounts zero in ctc-research.com — verify success
- [ ] 15.2.2 Re-apply: python manage.py migrate accounts — verify success
- [ ] 15.2.3 Repeat for lms, content apps in ctc-research.com
- [ ] 15.2.4 Repeat for accounts, alliance, content apps in structa.cloud
- [ ] 15.2.5 Verify data integrity after each reversal and re-application

#### 15.3 Verify migrations run successfully in Docker containers

**Subtasks:**
- [ ] 15.3.1 Build Docker image for ctc-research.com and run python manage.py migrate — verify no errors
- [ ] 15.3.2 Build Docker image for structa.cloud and run python manage.py migrate — verify no errors
- [ ] 15.3.3 Fix any Docker-specific migration issues

#### 16.1 Run full duplication analysis — verify zero duplication

**Subtasks:**
- [ ] 16.1.1 Run scripts/analyze_duplication.py --threshold 0.70 across entire ecosystem
- [ ] 16.1.2 Verify all code pairs have < 70% similarity
- [ ] 16.1.3 Fix any remaining duplication found

#### 16.10 Generate COMPLETION_REPORT.md

**Subtasks:**
- [ ] 16.10.1 Write scripts/validate_system.py implementing SystemValidator
- [ ] 16.10.2 Run validate_all() and generate COMPLETION_REPORT.md documenting:
- [ ] 16.10.3 Verify COMPLETION_REPORT.md documents all 17 final deliverables from Requirement 17

#### 16.11 Final commit and tag

**Subtasks:**
- [ ] 16.11.1 Commit all remaining changes with message: "feat: complete ecosystem-wide architectural refactoring"
- [ ] 16.11.2 Create git tag: ecosystem-refactor-complete
- [ ] 16.11.3 Push tag to remote

#### 16.2 Run full boundary check — verify zero violations

**Subtasks:**
- [ ] 16.2.1 Run import-linter --config .importlinter
- [ ] 16.2.2 Verify zero violations for all four contracts
- [ ] 16.2.3 Fix any remaining violations

#### 16.3 Run full test suite across all packages and projects

**Subtasks:**
- [ ] 16.3.1 Run uv run pytest tests/ -v in venv/libs/django-osoul/
- [ ] 16.3.2 Run uv run pytest tests/ -v in venv/libs/django-rseal/
- [ ] 16.3.3 Run uv run pytest tests/ -v in venv/libs/django-grep/
- [ ] 16.3.4 Run uv run pytest tests/ -v in venv/libs/nawaai/
- [ ] 16.3.5 Run uv run pytest tests/ -v in ctc-research.com/
- [ ] 16.3.6 Run uv run pytest tests/ -v in structa.cloud/
- [ ] 16.3.7 Fix any test failures

#### 16.4 Verify Docker health for both projects

**Subtasks:**
- [ ] 16.4.1 Run docker compose up -d for ctc-research.com
- [ ] 16.4.2 Verify GET /health/ returns HTTP 200
- [ ] 16.4.3 Verify GET /health/database/ returns HTTP 200
- [ ] 16.4.4 Verify GET /health/assets/ returns HTTP 200
- [ ] 16.4.5 Verify GET /health/media/ returns HTTP 200
- [ ] 16.4.6 Repeat for structa.cloud
- [ ] 16.4.7 Fix any Docker health issues

#### 16.5 Verify zero import errors across entire ecosystem

**Subtasks:**
- [ ] 16.5.1 Run python -c "import django_osoul" — verify no ImportError
- [ ] 16.5.2 Run python -c "import django_rseal" — verify no ImportError
- [ ] 16.5.3 Run python -c "import django_grep" — verify no ImportError
- [ ] 16.5.4 Run python -c "import nawaai" — verify no ImportError
- [ ] 16.5.5 Run python manage.py check in ctc-research.com — verify zero errors
- [ ] 16.5.6 Run python manage.py check in structa.cloud — verify zero errors

#### 16.6 Verify all migrations applied successfully

**Subtasks:**
- [ ] 16.6.1 Run python manage.py showmigrations in ctc-research.com — verify all [X]
- [ ] 16.6.2 Run python manage.py showmigrations in structa.cloud — verify all [X]

#### 16.7 Verify naming conventions across entire ecosystem

**Subtasks:**
- [ ] 16.7.1 Run scripts/enforce_naming.py check_module_names — verify zero violations
- [ ] 16.7.2 Run scripts/enforce_naming.py check_class_names — verify zero violations
- [ ] 16.7.3 Run scripts/enforce_naming.py check_function_names — verify zero violations

#### 16.8 Verify template organization

**Subtasks:**
- [ ] 16.8.1 Run scripts/validate_templates.py check_no_package_templates — verify zero violations
- [ ] 16.8.2 Run scripts/validate_templates.py verify_template_resolution — verify zero broken references

#### 16.9 Verify all specs are complete

**Subtasks:**
- [ ] 16.9.1 Run scripts/track_spec_status.py — verify all specs have all tasks marked [x]
- [ ] 16.9.2 Fix any incomplete tasks found

#### 2.1 Extract handlers base, core, and non-Wagtail mixins from apps/handlers to django_osoul

**Subtasks:**
- [ ] 2.1.1 Identify all classes in apps/handlers/ (both projects) that have zero Wagtail imports — base handler classes, core handler classes, fragment handlers, page handlers that use only pure Django (not wagtail.core.models.Page), search handlers using Django ORM (not Wagtail search)
- [ ] 2.1.2 Copy django_osoul-bound handler base classes to venv/libs/django-osoul/src/django_osoul/handlers/base.py
- [ ] 2.1.3 Copy django_osoul-bound handler core classes to venv/libs/django-osoul/src/django_osoul/handlers/core.py
- [ ] 2.1.4 Copy non-Wagtail fragment handler mixins to venv/libs/django-osoul/src/django_osoul/handlers/mixins/fragment.py
- [ ] 2.1.5 Copy non-Wagtail page handler mixins to venv/libs/django-osoul/src/django_osoul/handlers/mixins/page.py
- [ ] 2.1.6 Copy non-Wagtail search handler/mixin to venv/libs/django-osoul/src/django_osoul/handlers/search.py
- [ ] 2.1.7 Update all imports across ctc-research.com and structa.cloud to use new django_osoul.handlers paths
- [ ] 2.1.8 Delete original handler files from both projects after verifying imports resolve
- [ ] 2.1.9 Run full test suite and verify zero failures

#### 2.10 Extract pure Django base form classes to django_osoul

**Subtasks:**
- [ ] 2.10.1 Copy base form classes (no Wagtail form widgets) to venv/libs/django-osoul/src/django_osoul/forms/base.py
- [ ] 2.10.2 Update all imports in both projects and delete originals
- [ ] 2.10.3 Run tests

#### 2.11 Extract non-Wagtail UI components (pure Django widgets, payloads) to django_osoul/comp/

**Subtasks:**
- [ ] 2.11.1 Audit all comp/ components in both projects — flag any that import wagtail
- [ ] 2.11.2 Copy pure Django widgets to venv/libs/django-osoul/src/django_osoul/comp/widgets.py
- [ ] 2.11.3 Copy payload classes to venv/libs/django-osoul/src/django_osoul/comp/payloads.py
- [ ] 2.11.4 Update all imports in both projects and delete originals
- [ ] 2.11.5 Run tests

#### 2.12 Extract contrib utilities (enums, choices, context, schemas, responses) to django_osoul

**Subtasks:**
- [ ] 2.12.1 Copy enums/choices to venv/libs/django-osoul/src/django_osoul/contrib/enums.py
- [ ] 2.12.2 Copy context utilities to venv/libs/django-osoul/src/django_osoul/contrib/context.py
- [ ] 2.12.3 Copy schema classes to venv/libs/django-osoul/src/django_osoul/contrib/schemas.py
- [ ] 2.12.4 Copy response helpers to venv/libs/django-osoul/src/django_osoul/contrib/responses.py
- [ ] 2.12.5 Update all imports in both projects and delete originals
- [ ] 2.12.6 Run tests

#### 2.13 Extract foundation models (Person, Certificate, Message — pure Django, no Wagtail) to django_osoul

**Subtasks:**
- [ ] 2.13.1 Copy foundation model classes to venv/libs/django-osoul/src/django_osoul/models/
- [ ] 2.13.2 Verify no Wagtail model inheritance (no Page, StreamField, etc.)
- [ ] 2.13.3 Update all imports in both projects and delete originals
- [ ] 2.13.4 Run migrations check and tests

#### 2.14 Run full boundary check on django_osoul after all extractions

**Subtasks:**
- [ ] 2.14.1 Run scripts/check_boundaries.py — verify zero wagtail, celery, django_rseal imports in django_osoul
- [ ] 2.14.2 Fix any violations found
- [ ] 2.14.3 Run full test suite for django_osoul package
- [ ] 2.14.4 Commit with message: "feat(osoul): extract all pure Django foundation logic"

#### 2.2 Extract RoleHierarchyManager and GroupAccessControl to django_osoul

**Subtasks:**
- [ ] 2.2.1 Copy ctc-research.com/apps/handlers/managers/role_hierarchy.py to venv/libs/django-osoul/src/django_osoul/managers/role_hierarchy.py
- [ ] 2.2.2 Copy GroupAccessControl to venv/libs/django-osoul/src/django_osoul/managers/group_access.py
- [ ] 2.2.3 Update all imports in both projects to from django_osoul.managers import RoleHierarchyManager, GroupAccessControl
- [ ] 2.2.4 Delete original files from both projects
- [ ] 2.2.5 Run boundary checker — verify osoul has no wagtail/celery/rseal imports
- [ ] 2.2.6 Run tests

#### 2.3 Extract UserManager and GroupManager to django_osoul

**Subtasks:**
- [ ] 2.3.1 Copy UserManager to venv/libs/django-osoul/src/django_osoul/managers/user.py
- [ ] 2.3.2 Copy GroupManager to venv/libs/django-osoul/src/django_osoul/managers/group.py
- [ ] 2.3.3 Update all imports in both projects
- [ ] 2.3.4 Delete originals and run tests

#### 2.4 Extract pure Django model mixins (UserMixin, GroupMixin, and non-Wagtail model mixins) to django_osoul

**Subtasks:**
- [ ] 2.4.1 Audit all mixins in both projects — flag any that import from wagtail (those go to django_rseal)
- [ ] 2.4.2 Copy UserMixin to venv/libs/django-osoul/src/django_osoul/mixins/user.py
- [ ] 2.4.3 Copy GroupMixin to venv/libs/django-osoul/src/django_osoul/mixins/group.py
- [ ] 2.4.4 Copy all other pure Django model mixins to venv/libs/django-osoul/src/django_osoul/mixins/models.py
- [ ] 2.4.5 Copy pure Django view mixins to venv/libs/django-osoul/src/django_osoul/mixins/views.py
- [ ] 2.4.6 Update all imports in both projects
- [ ] 2.4.7 Delete originals and run tests

#### 2.5 Extract custom authentication backends and storage backends to django_osoul

**Subtasks:**
- [ ] 2.5.1 Copy all custom auth backends to venv/libs/django-osoul/src/django_osoul/backends/auth.py
- [ ] 2.5.2 Copy all custom storage backends to venv/libs/django-osoul/src/django_osoul/backends/storage.py
- [ ] 2.5.3 Update AUTHENTICATION_BACKENDS and DEFAULT_FILE_STORAGE settings in both projects
- [ ] 2.5.4 Update all imports and delete originals
- [ ] 2.5.5 Run tests

#### 2.6 Extract allauth and social auth adapters to django_osoul

**Subtasks:**
- [ ] 2.6.1 Copy allauth adapter to venv/libs/django-osoul/src/django_osoul/adapters/allauth.py
- [ ] 2.6.2 Copy social auth adapter to venv/libs/django-osoul/src/django_osoul/adapters/social.py
- [ ] 2.6.3 Update ACCOUNT_ADAPTER and SOCIALACCOUNT_ADAPTER settings in both projects
- [ ] 2.6.4 Update all imports and delete originals
- [ ] 2.6.5 Run tests

#### 2.7 Extract User/Group services (no Wagtail dependencies) to django_osoul

**Subtasks:**
- [ ] 2.7.1 Copy UserService to venv/libs/django-osoul/src/django_osoul/services/user.py
- [ ] 2.7.2 Copy GroupService to venv/libs/django-osoul/src/django_osoul/services/group.py
- [ ] 2.7.3 Verify neither service imports wagtail, celery, or django_rseal
- [ ] 2.7.4 Update all imports in both projects and delete originals
- [ ] 2.7.5 Run tests

#### 2.8 Extract ErrorTrackerMiddleware and other pure Django middleware to django_osoul

**Subtasks:**
- [ ] 2.8.1 Copy ErrorTrackerMiddleware to venv/libs/django-osoul/src/django_osoul/middlewares/error_tracker.py
- [ ] 2.8.2 Copy any other pure Django middleware (no Wagtail/Celery) to django_osoul/middlewares/
- [ ] 2.8.3 Update MIDDLEWARE settings in both projects
- [ ] 2.8.4 Update all imports and delete originals
- [ ] 2.8.5 Run tests

#### 2.9 Extract UniqueFieldValidator, SlugFieldValidator, and other pure Django form validators to django_osoul

**Subtasks:**
- [ ] 2.9.1 Copy validators to venv/libs/django-osoul/src/django_osoul/filters/validators.py
- [ ] 2.9.2 Update all imports in both projects and delete originals
- [ ] 2.9.3 Run tests

#### 3.1 Extract all Wagtail-related handler mixins and page handlers to django_rseal

**Subtasks:**
- [ ] 3.1.1 Identify all handler classes in both projects that inherit from wagtail.core.models.Page or import from wagtail
- [ ] 3.1.2 Copy Wagtail page handler mixins to venv/libs/django-rseal/src/django_rseal/handlers/mixins/wagtail_page.py
- [ ] 3.1.3 Copy Wagtail-specific fragment handlers to venv/libs/django-rseal/src/django_rseal/handlers/mixins/wagtail_fragment.py
- [ ] 3.1.4 Copy Wagtail search integration to venv/libs/django-rseal/src/django_rseal/handlers/search.py
- [ ] 3.1.5 Update all imports in both projects and delete originals
- [ ] 3.1.6 Run tests

#### 3.10 Extract Unfold admin and Wagtail admin customizations to django_rseal/contrib/admin_site/

**Subtasks:**
- [ ] 3.10.1 Copy Unfold admin customizations to venv/libs/django-rseal/src/django_rseal/contrib/admin_site/unfold.py
- [ ] 3.10.2 Copy Wagtail admin customizations to venv/libs/django-rseal/src/django_rseal/contrib/admin_site/wagtail.py
- [ ] 3.10.3 Update all imports in both projects and delete originals
- [ ] 3.10.4 Run tests

#### 3.11 Extract PrivacyConsentMiddleware to django_rseal

**Subtasks:**
- [ ] 3.11.1 Copy PrivacyConsentMiddleware to venv/libs/django-rseal/src/django_rseal/contrib/privacy/middleware.py
- [ ] 3.11.2 Update MIDDLEWARE settings in both projects
- [ ] 3.11.3 Update all imports and delete originals
- [ ] 3.11.4 Run tests

#### 3.12 Extract cache utilities to django_rseal/contrib/cache/

**Subtasks:**
- [ ] 3.12.1 Copy cache utility classes and decorators to venv/libs/django-rseal/src/django_rseal/contrib/cache/utils.py
- [ ] 3.12.2 Update all imports in both projects and delete originals
- [ ] 3.12.3 Run tests

#### 3.13 Extract Django signals to django_rseal/contrib/signals/

**Subtasks:**
- [ ] 3.13.1 Copy reusable signal definitions to venv/libs/django-rseal/src/django_rseal/contrib/signals/
- [ ] 3.13.2 Update all imports in both projects and delete originals
- [ ] 3.13.3 Run tests

#### 3.14 Extract debug tools to django_rseal/contrib/debug_tools/

**Subtasks:**
- [ ] 3.14.1 Copy debug utility classes to venv/libs/django-rseal/src/django_rseal/contrib/debug_tools/
- [ ] 3.14.2 Update all imports in both projects and delete originals
- [ ] 3.14.3 Run tests

#### 3.15 Extract email configuration utilities to django_rseal/contrib/email_config/

**Subtasks:**
- [ ] 3.15.1 Copy email config helpers to venv/libs/django-rseal/src/django_rseal/contrib/email_config/
- [ ] 3.15.2 Update all imports in both projects and delete originals
- [ ] 3.15.3 Run tests

#### 3.16 Extract Orchestrator CLI to django_rseal/workflows/

**Subtasks:**
- [ ] 3.16.1 Copy orchestrator CLI code to venv/libs/django-rseal/src/django_rseal/workflows/orchestrator.py
- [ ] 3.16.2 Update all imports in both projects and delete originals
- [ ] 3.16.3 Run tests

#### 3.17 Run full boundary check on django_rseal after all extractions

**Subtasks:**
- [ ] 3.17.1 Run scripts/check_boundaries.py — verify django_rseal has no project-specific imports
- [ ] 3.17.2 Fix any violations found
- [ ] 3.17.3 Run full test suite for django_rseal package
- [ ] 3.17.4 Commit with message: "feat(rseal): extract all Wagtail and automation logic"

#### 3.2 Extract CartServiceBase to django_rseal

**Subtasks:**
- [ ] 3.2.1 Create venv/libs/django-rseal/src/django_rseal/pipelines/services/cart.py with CartServiceBase class
- [ ] 3.2.2 Implement add_to_cart, remove_from_cart, get_cart, clear_cart base methods with cart_model injection pattern
- [ ] 3.2.3 Replace ctc-research.com CartService with thin subclass: class CartService(CartServiceBase): cart_model = Cart
- [ ] 3.2.4 Replace structa.cloud CartService with thin subclass: class CartService(CartServiceBase): cart_model = Cart
- [ ] 3.2.5 Update all imports in both projects and delete original service files
- [ ] 3.2.6 Run tests

#### 3.3 Extract PersonServiceBase to django_rseal

**Subtasks:**
- [ ] 3.3.1 Create venv/libs/django-rseal/src/django_rseal/pipelines/services/person.py with PersonServiceBase
- [ ] 3.3.2 Replace both project PersonService implementations with thin subclasses
- [ ] 3.3.3 Update all imports and delete originals
- [ ] 3.3.4 Run tests

#### 3.4 Extract MessageServiceBase to django_rseal

**Subtasks:**
- [ ] 3.4.1 Create venv/libs/django-rseal/src/django_rseal/pipelines/services/message.py with MessageServiceBase
- [ ] 3.4.2 Replace both project MessageService implementations with thin subclasses
- [ ] 3.4.3 Update all imports and delete originals
- [ ] 3.4.4 Run tests

#### 3.5 Extract FormSubmissionService to django_rseal

**Subtasks:**
- [ ] 3.5.1 Create venv/libs/django-rseal/src/django_rseal/pipelines/services/form_submission.py
- [ ] 3.5.2 Replace both project implementations with thin subclasses
- [ ] 3.5.3 Update all imports and delete originals
- [ ] 3.5.4 Run tests

#### 3.6 Extract RoleBasedEmailTemplateSelector and EmailTemplateRegistry to django_rseal

**Subtasks:**
- [ ] 3.6.1 Create venv/libs/django-rseal/src/django_rseal/email/selectors.py with RoleBasedEmailTemplateSelector
- [ ] 3.6.2 Create venv/libs/django-rseal/src/django_rseal/email/registry.py with EmailTemplateRegistry
- [ ] 3.6.3 Update all imports in both projects and delete originals
- [ ] 3.6.4 Run tests

#### 3.7 Extract Wagtail blocks (StructBlock, StreamBlock, etc.) to django_rseal/comp/

**Subtasks:**
- [ ] 3.7.1 Audit all comp/ directories in both projects for Wagtail block classes
- [ ] 3.7.2 Copy all Wagtail blocks to venv/libs/django-rseal/src/django_rseal/comp/blocks.py
- [ ] 3.7.3 Copy StreamField block definitions to venv/libs/django-rseal/src/django_rseal/comp/stream_blocks.py
- [ ] 3.7.4 Update all imports in both projects and delete originals
- [ ] 3.7.5 Run tests

#### 3.8 Extract Wagtail snippets to django_rseal

**Subtasks:**
- [ ] 3.8.1 Copy reusable Wagtail snippet classes to venv/libs/django-rseal/src/django_rseal/contrib/snippets/
- [ ] 3.8.2 Update all imports in both projects and delete originals
- [ ] 3.8.3 Run tests

#### 3.9 Extract Wagtail hooks to django_rseal

**Subtasks:**
- [ ] 3.9.1 Copy reusable wagtail_hooks.py logic to venv/libs/django-rseal/src/django_rseal/contrib/wagtail_hooks.py
- [ ] 3.9.2 Update both projects to import hooks from django_rseal
- [ ] 3.9.3 Run tests

#### 4.1 Create unified BaseTestCase in django_grep

**Subtasks:**
- [ ] 4.1.1 Create venv/libs/django-grep/src/django_grep/tests/base.py with BaseTestCase extending django.test.TestCase
- [ ] 4.1.2 Add st_email() Hypothesis strategy to base.py
- [ ] 4.1.3 Add st_slug() Hypothesis strategy to base.py
- [ ] 4.1.4 Add st_uuid() Hypothesis strategy to base.py
- [ ] 4.1.5 Run django_grep package tests to verify helpers work

#### 4.10 Run full boundary check — verify django_grep not imported by production code

**Subtasks:**
- [ ] 4.10.1 Run scripts/check_boundaries.py grep-test-only rule
- [ ] 4.10.2 Fix any production code that imports django_grep
- [ ] 4.10.3 Commit with message: "feat(grep): extract unified testing infrastructure and health checks"

#### 4.2 Create unified factories in django_grep

**Subtasks:**
- [ ] 4.2.1 Audit all factory_boy factory classes in both projects and packages
- [ ] 4.2.2 Copy reusable factories to venv/libs/django-grep/src/django_grep/tests/factories/
- [ ] 4.2.3 Update all test imports in both projects to use django_grep.tests.factories
- [ ] 4.2.4 Delete duplicate factory files from projects
- [ ] 4.2.5 Run tests

#### 4.3 Create unified fixtures in django_grep

**Subtasks:**
- [ ] 4.3.1 Copy reusable test fixtures to venv/libs/django-grep/src/django_grep/tests/fixtures/
- [ ] 4.3.2 Update all test imports in both projects to use django_grep.tests.fixtures
- [ ] 4.3.3 Delete duplicate fixture files from projects
- [ ] 4.3.4 Run tests

#### 4.4 Create unified assertions in django_grep

**Subtasks:**
- [ ] 4.4.1 Copy custom assertion helpers to venv/libs/django-grep/src/django_grep/tests/assertions/
- [ ] 4.4.2 Update all test imports in both projects to use django_grep.tests.assertions
- [ ] 4.4.3 Delete duplicate assertion files from projects
- [ ] 4.4.4 Run tests

#### 4.5 Create unified test mixins in django_grep

**Subtasks:**
- [ ] 4.5.1 Copy reusable test mixin classes to venv/libs/django-grep/src/django_grep/tests/mixins/
- [ ] 4.5.2 Update all test imports in both projects
- [ ] 4.5.3 Delete duplicate mixin files from projects
- [ ] 4.5.4 Run tests

#### 4.6 Register pytest plugin in django_grep

**Subtasks:**
- [ ] 4.6.1 Create venv/libs/django-grep/src/django_grep/tests/pytest_plugin.py with plugin registration
- [ ] 4.6.2 Register plugin in pyproject.toml under [tool.pytest11]
- [ ] 4.6.3 Verify plugin loads correctly in both projects

#### 4.7 Create health check system in django_grep

**Subtasks:**
- [ ] 4.7.1 Create venv/libs/django-grep/src/django_grep/health/__init__.py
- [ ] 4.7.2 Create venv/libs/django-grep/src/django_grep/health/views.py with HealthCheckView, DatabaseHealthView, AssetsHealthView, MediaHealthView
- [ ] 4.7.3 Create venv/libs/django-grep/src/django_grep/health/urls.py with urlpatterns for all four endpoints
- [ ] 4.7.4 Add path('health/', include('django_grep.health.urls')) to ctc-research.com/configs/urls.py
- [ ] 4.7.5 Add path('health/', include('django_grep.health.urls')) to structa.cloud/configs/urls.py
- [ ] 4.7.6 Remove any existing health check views/urls from both projects
- [ ] 4.7.7 Test GET /health/ returns 200, GET /health/database/ returns 200, GET /health/assets/ returns 200, GET /health/media/ returns 200
- [ ] 4.7.8 Test GET /health/database/ returns 503 when database is unreachable

#### 4.8 Migrate all existing tests in both projects to use django_grep infrastructure

**Subtasks:**
- [ ] 4.8.1 Write scripts/migrate_tests.py implementing TestMigrator
- [ ] 4.8.2 Run migrator against ctc-research.com/tests/ — replace TestCase with BaseTestCase, update factory/assertion imports
- [ ] 4.8.3 Run migrator against structa.cloud/tests/ — same replacements
- [ ] 4.8.4 Run migrator against all package tests in venv/libs/
- [ ] 4.8.5 Delete duplicate test infrastructure files from projects
- [ ] 4.8.6 Run full test suite and verify all tests pass

#### 4.9 Move seeder infrastructure to django_grep

**Subtasks:**
- [ ] 4.9.1 Copy database seeder classes to venv/libs/django-grep/src/django_grep/seeder/
- [ ] 4.9.2 Copy management commands (backup_db, backup_media, load_fixtures) to venv/libs/django-grep/src/django_grep/management/commands/
- [ ] 4.9.3 Update all imports in both projects and delete originals
- [ ] 4.9.4 Run tests

#### 5.1 Audit nawaai for any Django imports and remove them

**Subtasks:**
- [ ] 5.1.1 Run scripts/check_boundaries.py nawaai-no-django rule
- [ ] 5.1.2 For each violation found, refactor the nawaai module to remove the Django import (use dependency injection or pure Python alternatives)
- [ ] 5.1.3 Re-run boundary checker and verify zero violations
- [ ] 5.1.4 Run nawaai package tests
- [ ] 5.1.5 Commit with message: "fix(nawaai): remove all Django imports — pure Python only"

#### 6.1 Rename apps/handlers to apps/accounts in ctc-research.com

**Subtasks:**
- [ ] 6.1.1 Create ctc-research.com/apps/accounts/ directory with __init__.py and apps.py (AppConfig name='accounts')
- [ ] 6.1.2 Create migration ctc-research.com/apps/accounts/migrations/0001_rename_app_label.py with AlterModelTable operations to preserve all existing table names (e.g., table="handlers_person")
- [ ] 6.1.3 Create data migration to update ContentType records: ContentType.objects.filter(app_label='handlers').update(app_label='accounts')
- [ ] 6.1.4 Update INSTALLED_APPS in ctc-research.com settings to replace 'apps.handlers' with 'apps.accounts'
- [ ] 6.1.5 Update all imports across ctc-research.com from apps.handlers to apps.accounts
- [ ] 6.1.6 Run python manage.py migrate and verify no errors
- [ ] 6.1.7 Test migration reversal: python manage.py migrate accounts zero
- [ ] 6.1.8 Re-apply migration and verify data integrity
- [ ] 6.1.9 Run tests

#### 6.2 Rename apps/handlers to apps/accounts in structa.cloud

**Subtasks:**
- [ ] 6.2.1 Repeat steps 6.1.1–6.1.9 for structa.cloud

#### 6.3 Rename apps/LMS to apps/lms in ctc-research.com

**Subtasks:**
- [ ] 6.3.1 Create ctc-research.com/apps/lms/ with AppConfig name='lms'
- [ ] 6.3.2 Create migration with AlterModelTable to preserve table names (e.g., table="lms_cart")
- [ ] 6.3.3 Create data migration to update ContentType records
- [ ] 6.3.4 Update INSTALLED_APPS and all imports
- [ ] 6.3.5 Run migrations, test reversal, verify data integrity, run tests

#### 6.4 Rename apps/LMS to apps/lms in structa.cloud

**Subtasks:**
- [ ] 6.4.1 Create structa.cloud/apps/lms/ with AppConfig name='alliance'
- [ ] 6.4.2 Create migration with AlterModelTable to preserve table names
- [ ] 6.4.3 Create data migration to update ContentType records
- [ ] 6.4.4 Update INSTALLED_APPS and all imports
- [ ] 6.4.5 Run migrations, test reversal, verify data integrity, run tests

#### 6.5 Rename apps/pages to apps/content in both projects

**Subtasks:**
- [ ] 6.5.1 Create apps/content/ in ctc-research.com with AppConfig name='content'
- [ ] 6.5.2 Create migration with AlterModelTable to preserve table names
- [ ] 6.5.3 Create data migration to update ContentType records
- [ ] 6.5.4 Update INSTALLED_APPS and all imports in ctc-research.com
- [ ] 6.5.5 Repeat for structa.cloud
- [ ] 6.5.6 Run migrations, test reversal, verify data integrity, run tests

#### 6.6 Enforce standard sub-module layout in all renamed apps

**Subtasks:**
- [ ] 6.6.1 For each renamed app in both projects, create missing subdirectories: admin/, filters/, forms/, managers/, middleware/, models/, services/, views/
- [ ] 6.6.2 Move existing files into correct subdirectories (e.g., move models.py content into models/__init__.py)
- [ ] 6.6.3 Update all internal imports within each app
- [ ] 6.6.4 Run tests after each app reorganization

#### 6.7 Detect and eliminate cross-domain leakage

**Subtasks:**
- [ ] 6.7.1 Run scripts/identify_domains.py to detect modules that mix multiple domains
- [ ] 6.7.2 For each CrossDomainLeak found, split the module into domain-specific files
- [ ] 6.7.3 Update all imports after splits
- [ ] 6.7.4 Run tests

#### 6.8 Detect and eliminate circular dependencies

**Subtasks:**
- [ ] 6.8.1 Run scripts/detect_cycles.py to find all circular dependency cycles
- [ ] 6.8.2 For each cycle, apply the suggested break strategy (extract-interface, dependency-injection, or event-based)
- [ ] 6.8.3 Re-run cycle detector and verify zero cycles
- [ ] 6.8.4 Run tests

#### 6.9 Commit domain restructuring

**Subtasks:**
- [ ] 6.9.1 Run python manage.py check in both projects — verify zero errors
- [ ] 6.9.2 Run python manage.py showmigrations — verify all migrations applied
- [ ] 6.9.3 Commit with message: "refactor: rename apps to domain-aligned names with reversible migrations"

#### 7.1 Audit both projects for remaining business logic that belongs in packages

**Subtasks:**
- [ ] 7.1.1 Write scripts/check_thin_layer.py that scans project apps/ for classes/functions that are not: settings, URLs, project-specific models, templates, static files, or thin service subclasses
- [ ] 7.1.2 Run checker against ctc-research.com and structa.cloud
- [ ] 7.1.3 Produce THIN_LAYER_VIOLATIONS.md listing all remaining business logic in projects

#### 7.2 Convert remaining project services to thin subclasses of package base classes

**Subtasks:**
- [ ] 7.2.1 For each service in ctc-research.com that has a corresponding base in django_rseal, replace with thin subclass pattern
- [ ] 7.2.2 For each service in structa.cloud that has a corresponding base in django_rseal, replace with thin subclass pattern
- [ ] 7.2.3 Add module-level docstrings documenting canonical import path: "Delegates to django_rseal.pipelines.services.CartServiceBase"
- [ ] 7.2.4 Run tests

#### 7.3 Remove all remaining duplicate managers from projects

**Subtasks:**
- [ ] 7.3.1 Verify all managers now imported from django_osoul.managers
- [ ] 7.3.2 Delete any remaining duplicate manager files from both projects
- [ ] 7.3.3 Run tests

#### 7.4 Remove all remaining duplicate mixins from projects

**Subtasks:**
- [ ] 7.4.1 Verify all mixins now imported from django_osoul.mixins or django_rseal
- [ ] 7.4.2 Delete any remaining duplicate mixin files from both projects
- [ ] 7.4.3 Run tests

#### 7.5 Remove all remaining duplicate forms from projects

**Subtasks:**
- [ ] 7.5.1 Verify all base form classes now imported from django_osoul.forms
- [ ] 7.5.2 Delete any remaining duplicate form base files from both projects
- [ ] 7.5.3 Run tests

#### 7.6 Remove all remaining duplicate middleware from projects

**Subtasks:**
- [ ] 7.6.1 Verify all middleware now imported from django_osoul.middlewares or django_rseal.contrib
- [ ] 7.6.2 Delete any remaining duplicate middleware files from both projects
- [ ] 7.6.3 Run tests

#### 7.7 Verify both projects follow identical structural patterns

**Subtasks:**
- [ ] 7.7.1 Run scripts/check_consistency.py check_app_structure — verify both projects have accounts/, content/, blog/ and project-specific lms/ or alliance/
- [ ] 7.7.2 Fix any structural inconsistencies
- [ ] 7.7.3 Run tests

#### 7.8 Unify settings structure across both projects

**Subtasks:**
- [ ] 7.8.1 Compare ctc-research.com/configs/settings/ with structa.cloud/configs/settings/
- [ ] 7.8.2 Ensure both use same base settings pattern and same environment overrides pattern
- [ ] 7.8.3 Ensure both use same middleware stack order
- [ ] 7.8.4 Ensure both use same URL routing patterns
- [ ] 7.8.5 Run python manage.py check in both projects

#### 7.9 Commit project simplification

**Subtasks:**
- [ ] 7.9.1 Run scripts/check_thin_layer.py — verify zero violations
- [ ] 7.9.2 Run full test suite in both projects
- [ ] 7.9.3 Commit with message: "refactor: convert projects to thin layers delegating to packages"

#### 8.1 Enforce snake_case naming for all Python modules

**Subtasks:**
- [ ] 8.1.1 Run scripts/enforce_naming.py check_module_names across entire ecosystem
- [ ] 8.1.2 Rename any CamelCase or mixed-case module files to snake_case
- [ ] 8.1.3 Update all imports after renames
- [ ] 8.1.4 Run tests

#### 8.2 Enforce PascalCase naming for all classes

**Subtasks:**
- [ ] 8.2.1 Run scripts/enforce_naming.py check_class_names across entire ecosystem
- [ ] 8.2.2 Rename any non-PascalCase classes using AST-based refactoring
- [ ] 8.2.3 Update all references after renames
- [ ] 8.2.4 Run tests

#### 8.3 Enforce snake_case naming for all functions and variables

**Subtasks:**
- [ ] 8.3.1 Run scripts/enforce_naming.py check_function_names across entire ecosystem
- [ ] 8.3.2 Rename any camelCase functions to snake_case
- [ ] 8.3.3 Update all call sites after renames
- [ ] 8.3.4 Run tests

#### 8.4 Verify both projects use same patterns for services, handlers, managers, and views

**Subtasks:**
- [ ] 8.4.1 Run scripts/check_consistency.py check_naming_conventions
- [ ] 8.4.2 Fix any naming inconsistencies between projects
- [ ] 8.4.3 Run tests

#### 8.5 Maintain CHANGELOG.md files for each project and package

**Subtasks:**
- [ ] 8.5.1 Create or update ctc-research.com/CHANGELOG.md with all changes from this refactoring
- [ ] 8.5.2 Create or update structa.cloud/CHANGELOG.md with all changes from this refactoring
- [ ] 8.5.3 Create or update venv/libs/django-osoul/CHANGELOG.md
- [ ] 8.5.4 Create or update venv/libs/django-rseal/CHANGELOG.md
- [ ] 8.5.5 Create or update venv/libs/django-grep/CHANGELOG.md
- [ ] 8.5.6 Create or update venv/libs/nawaai/CHANGELOG.md

#### 9.1 Verify no templates exist in any venv/libs/ package

**Subtasks:**
- [ ] 9.1.1 Run scripts/validate_templates.py check_no_package_templates
- [ ] 9.1.2 For each template found in a package, move it to the appropriate project's templates/ directory
- [ ] 9.1.3 Update all {% include %}, {% extends %}, and view render() calls to reference new template paths
- [ ] 9.1.4 Run tests

#### 9.2 Verify both projects maintain consistent template structure

**Subtasks:**
- [ ] 9.2.1 Run scripts/validate_templates.py check_template_structure
- [ ] 9.2.2 Fix any structural inconsistencies between projects' template directories
- [ ] 9.2.3 Run tests

#### 9.3 Update all template references after refactoring

**Subtasks:**
- [ ] 9.3.1 Run scripts/validate_templates.py verify_template_resolution
- [ ] 9.3.2 Fix all broken {% include %}, {% extends %}, {% load %}, and static file references
- [ ] 9.3.3 Run tests

#### 9.4 Verify templatetags placement

**Subtasks:**
- [ ] 9.4.1 Audit all templatetags directories — reusable tags belong in packages, project-specific tags stay in projects
- [ ] 9.4.2 Move reusable templatetags to appropriate package (django_osoul or django_rseal)
- [ ] 9.4.3 Update all {% load %} tags in templates
- [ ] 9.4.4 Run tests

#### 9.5 Verify static files placement

**Subtasks:**
- [ ] 9.5.1 Audit all static files — reusable static assets belong in packages, project-specific stay in projects
- [ ] 9.5.2 Move reusable static files to appropriate package
- [ ] 9.5.3 Run python manage.py collectstatic in both projects and verify no errors
- [ ] 9.5.4 Run tests


### phase-2-website-sync-completion
**Incomplete: 0 main tasks**


## Prioritization Guide

Tasks are organized by spec and should be executed in the following order:

1. **ecosystem-architectural-refactoring** (114 incomplete tasks)
2. **core-logic-consolidation-and-app-restructure** (32 incomplete tasks)
