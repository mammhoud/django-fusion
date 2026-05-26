# Tasks: Ecosystem-Wide Architectural Refactoring

## Status Summary

All 17 phases are complete. All tasks are marked `[x]`. This spec is fully implemented.

**Related Specs:**
- finalize-refactor (completed — foundation for package extraction)
- phase-3-production-deployment (completed — Docker infrastructure)
- ctc-research-deployment-verification (completed — deployment verification)
- django-refactoring (completed — initial refactoring patterns)
- core-logic-consolidation-and-app-restructure (in-progress — extends this spec's work)
- phase-2-website-sync-completion (not-started — website sync integrated into Phase 7–8)

---

## Phase 1: Analysis and Planning

- [x] 1.1 Scan all Python modules across ctc-research.com/apps/, structa.cloud/apps/, and venv/libs/ packages and produce DUPLICATION_REPORT.md listing every duplicated class, function, and module with source locations and similarity percentage (≥70% threshold)
  - [x] 1.1.1 Write scripts/analyze_duplication.py implementing DuplicationAnalyzer with AST-based comparison
  - [x] 1.1.2 Run analyzer against all three directory trees and capture output
  - [x] 1.1.3 Categorize each duplicate as extract-to-osoul, extract-to-rseal, extract-to-grep, already-extracted, or project-specific
  - [x] 1.1.4 Write DUPLICATION_REPORT.md with full results including cross-references to existing specs

- [x] 1.2 Detect all boundary violations and misplaced responsibilities across the ecosystem
  - [x] 1.2.1 Write scripts/check_boundaries.py implementing BoundaryChecker with the four rule sets (nawaai-no-django, osoul-no-wagtail, rseal-no-projects, grep-test-only)
  - [x] 1.2.2 Run boundary checker and write BOUNDARY_VIOLATIONS.md listing every violation with file, line, import statement, and fix suggestion
  - [x] 1.2.3 Write scripts/detect_cycles.py implementing CircularDependencyDetector using networkx
  - [x] 1.2.4 Run cycle detector and append cycle report to BOUNDARY_VIOLATIONS.md

- [x] 1.3 Scan all specs in .kiro/specs/ for incomplete tasks and generate master task list
  - [x] 1.3.1 Write scripts/track_spec_status.py implementing SpecStatusTracker
  - [x] 1.3.2 Run tracker against all specs and write MASTER_TASK_LIST.md with prioritized incomplete tasks grouped by spec

- [x] 1.4 Build complete execution plan with dependency ordering and validation checkpoints
  - [x] 1.4.1 Write scripts/plan_implementation.py implementing ImplementationPlanner
  - [x] 1.4.2 Produce IMPLEMENTATION_PLAN.md with all phases, task dependencies (topological order), effort estimates, and rollback points
  - [x] 1.4.3 Create git tags for rollback points: rollback-phase-1-start, rollback-phase-2-start, etc.
  - [x] 1.4.4 Write BACKUP_LOG.md template and create initial database and media backups


## Phase 2: django_osoul — Extract Pure Django/Python Foundation

- [x] 2.1 Extract handlers base, core, and non-Wagtail mixins from apps/handlers to django_osoul
  - [x] 2.1.1 Identify all classes in apps/handlers/ (both projects) that have zero Wagtail imports — base handler classes, core handler classes, fragment handlers, page handlers that use only pure Django (not wagtail.core.models.Page), search handlers using Django ORM (not Wagtail search)
  - [x] 2.1.2 Copy django_osoul-bound handler base classes to venv/libs/django-osoul/src/django_osoul/handlers/base.py
  - [x] 2.1.3 Copy django_osoul-bound handler core classes to venv/libs/django-osoul/src/django_osoul/handlers/core.py
  - [x] 2.1.4 Copy non-Wagtail fragment handler mixins to venv/libs/django-osoul/src/django_osoul/handlers/mixins/fragment.py
  - [x] 2.1.5 Copy non-Wagtail page handler mixins to venv/libs/django-osoul/src/django_osoul/handlers/mixins/page.py
  - [x] 2.1.6 Copy non-Wagtail search handler/mixin to venv/libs/django-osoul/src/django_osoul/handlers/search.py
  - [x] 2.1.7 Update all imports across ctc-research.com and structa.cloud to use new django_osoul.handlers paths
  - [x] 2.1.8 Delete original handler files from both projects after verifying imports resolve
  - [x] 2.1.9 Run full test suite and verify zero failures

- [x] 2.2 Extract RoleHierarchyManager and GroupAccessControl to django_osoul
  - [x] 2.2.1 Copy ctc-research.com/apps/handlers/managers/role_hierarchy.py to venv/libs/django-osoul/src/django_osoul/managers/role_hierarchy.py
  - [x] 2.2.2 Copy GroupAccessControl to venv/libs/django-osoul/src/django_osoul/managers/group_access.py
  - [x] 2.2.3 Update all imports in both projects to from django_osoul.managers import RoleHierarchyManager, GroupAccessControl
  - [x] 2.2.4 Delete original files from both projects
  - [x] 2.2.5 Run boundary checker — verify osoul has no wagtail/celery/rseal imports
  - [x] 2.2.6 Run tests

- [x] 2.3 Extract UserManager and GroupManager to django_osoul
  - [x] 2.3.1 Copy UserManager to venv/libs/django-osoul/src/django_osoul/managers/user.py
  - [x] 2.3.2 Copy GroupManager to venv/libs/django-osoul/src/django_osoul/managers/group.py
  - [x] 2.3.3 Update all imports in both projects
  - [x] 2.3.4 Delete originals and run tests

- [x] 2.4 Extract pure Django model mixins (UserMixin, GroupMixin, and non-Wagtail model mixins) to django_osoul
  - [x] 2.4.1 Audit all mixins in both projects — flag any that import from wagtail (those go to django_rseal)
  - [x] 2.4.2 Copy UserMixin to venv/libs/django-osoul/src/django_osoul/mixins/user.py
  - [x] 2.4.3 Copy GroupMixin to venv/libs/django-osoul/src/django_osoul/mixins/group.py
  - [x] 2.4.4 Copy all other pure Django model mixins to venv/libs/django-osoul/src/django_osoul/mixins/models.py
  - [x] 2.4.5 Copy pure Django view mixins to venv/libs/django-osoul/src/django_osoul/mixins/views.py
  - [x] 2.4.6 Update all imports in both projects
  - [x] 2.4.7 Delete originals and run tests

- [x] 2.5 Extract custom authentication backends and storage backends to django_osoul
  - [x] 2.5.1 Copy all custom auth backends to venv/libs/django-osoul/src/django_osoul/backends/auth.py
  - [x] 2.5.2 Copy all custom storage backends to venv/libs/django-osoul/src/django_osoul/backends/storage.py
  - [x] 2.5.3 Update AUTHENTICATION_BACKENDS and DEFAULT_FILE_STORAGE settings in both projects
  - [x] 2.5.4 Update all imports and delete originals
  - [x] 2.5.5 Run tests

- [x] 2.6 Extract allauth and social auth adapters to django_osoul
  - [x] 2.6.1 Copy allauth adapter to venv/libs/django-osoul/src/django_osoul/adapters/allauth.py
  - [x] 2.6.2 Copy social auth adapter to venv/libs/django-osoul/src/django_osoul/adapters/social.py
  - [x] 2.6.3 Update ACCOUNT_ADAPTER and SOCIALACCOUNT_ADAPTER settings in both projects
  - [x] 2.6.4 Update all imports and delete originals
  - [x] 2.6.5 Run tests

- [x] 2.7 Extract User/Group services (no Wagtail dependencies) to django_osoul
  - [x] 2.7.1 Copy UserService to venv/libs/django-osoul/src/django_osoul/services/user.py
  - [x] 2.7.2 Copy GroupService to venv/libs/django-osoul/src/django_osoul/services/group.py
  - [x] 2.7.3 Verify neither service imports wagtail, celery, or django_rseal
  - [x] 2.7.4 Update all imports in both projects and delete originals
  - [x] 2.7.5 Run tests

- [x] 2.8 Extract ErrorTrackerMiddleware and other pure Django middleware to django_osoul
  - [x] 2.8.1 Copy ErrorTrackerMiddleware to venv/libs/django-osoul/src/django_osoul/middlewares/error_tracker.py
  - [x] 2.8.2 Copy any other pure Django middleware (no Wagtail/Celery) to django_osoul/middlewares/
  - [x] 2.8.3 Update MIDDLEWARE settings in both projects
  - [x] 2.8.4 Update all imports and delete originals
  - [x] 2.8.5 Run tests

- [x] 2.9 Extract UniqueFieldValidator, SlugFieldValidator, and other pure Django form validators to django_osoul
  - [x] 2.9.1 Copy validators to venv/libs/django-osoul/src/django_osoul/filters/validators.py
  - [x] 2.9.2 Update all imports in both projects and delete originals
  - [x] 2.9.3 Run tests

- [x] 2.10 Extract pure Django base form classes to django_osoul
  - [x] 2.10.1 Copy base form classes (no Wagtail form widgets) to venv/libs/django-osoul/src/django_osoul/forms/base.py
  - [x] 2.10.2 Update all imports in both projects and delete originals
  - [x] 2.10.3 Run tests

- [x] 2.11 Extract non-Wagtail UI components (pure Django widgets, payloads) to django_osoul/comp/
  - [x] 2.11.1 Audit all comp/ components in both projects — flag any that import wagtail
  - [x] 2.11.2 Copy pure Django widgets to venv/libs/django-osoul/src/django_osoul/comp/widgets.py
  - [x] 2.11.3 Copy payload classes to venv/libs/django-osoul/src/django_osoul/comp/payloads.py
  - [x] 2.11.4 Update all imports in both projects and delete originals
  - [x] 2.11.5 Run tests

- [x] 2.12 Extract contrib utilities (enums, choices, context, schemas, responses) to django_osoul
  - [x] 2.12.1 Copy enums/choices to venv/libs/django-osoul/src/django_osoul/contrib/enums.py
  - [x] 2.12.2 Copy context utilities to venv/libs/django-osoul/src/django_osoul/contrib/context.py
  - [x] 2.12.3 Copy schema classes to venv/libs/django-osoul/src/django_osoul/contrib/schemas.py
  - [x] 2.12.4 Copy response helpers to venv/libs/django-osoul/src/django_osoul/contrib/responses.py
  - [x] 2.12.5 Update all imports in both projects and delete originals
  - [x] 2.12.6 Run tests

- [x] 2.13 Extract foundation models (Person, Certificate, Message — pure Django, no Wagtail) to django_osoul
  - [x] 2.13.1 Copy foundation model classes to venv/libs/django-osoul/src/django_osoul/models/
  - [x] 2.13.2 Verify no Wagtail model inheritance (no Page, StreamField, etc.)
  - [x] 2.13.3 Update all imports in both projects and delete originals
  - [x] 2.13.4 Run migrations check and tests

- [x] 2.14 Run full boundary check on django_osoul after all extractions
  - [x] 2.14.1 Run scripts/check_boundaries.py — verify zero wagtail, celery, django_rseal imports in django_osoul
  - [x] 2.14.2 Fix any violations found
  - [x] 2.14.3 Run full test suite for django_osoul package
  - [x] 2.14.4 Commit with message: "feat(osoul): extract all pure Django foundation logic"


## Phase 3: django_rseal — Extract Wagtail + Automation Logic

- [x] 3.1 Extract all Wagtail-related handler mixins and page handlers to django_rseal
  - [x] 3.1.1 Identify all handler classes in both projects that inherit from wagtail.core.models.Page or import from wagtail
  - [x] 3.1.2 Copy Wagtail page handler mixins to venv/libs/django-rseal/src/django_rseal/handlers/mixins/wagtail_page.py
  - [x] 3.1.3 Copy Wagtail-specific fragment handlers to venv/libs/django-rseal/src/django_rseal/handlers/mixins/wagtail_fragment.py
  - [x] 3.1.4 Copy Wagtail search integration to venv/libs/django-rseal/src/django_rseal/handlers/search.py
  - [x] 3.1.5 Update all imports in both projects and delete originals
  - [x] 3.1.6 Run tests

- [x] 3.2 Extract CartServiceBase to django_rseal
  - [x] 3.2.1 Create venv/libs/django-rseal/src/django_rseal/pipelines/services/cart.py with CartServiceBase class
  - [x] 3.2.2 Implement add_to_cart, remove_from_cart, get_cart, clear_cart base methods with cart_model injection pattern
  - [x] 3.2.3 Replace ctc-research.com CartService with thin subclass: class CartService(CartServiceBase): cart_model = Cart
  - [x] 3.2.4 Replace structa.cloud CartService with thin subclass: class CartService(CartServiceBase): cart_model = Cart
  - [x] 3.2.5 Update all imports in both projects and delete original service files
  - [x] 3.2.6 Run tests

- [x] 3.3 Extract PersonServiceBase to django_rseal
  - [x] 3.3.1 Create venv/libs/django-rseal/src/django_rseal/pipelines/services/person.py with PersonServiceBase
  - [x] 3.3.2 Replace both project PersonService implementations with thin subclasses
  - [x] 3.3.3 Update all imports and delete originals
  - [x] 3.3.4 Run tests

- [x] 3.4 Extract MessageServiceBase to django_rseal
  - [x] 3.4.1 Create venv/libs/django-rseal/src/django_rseal/pipelines/services/message.py with MessageServiceBase
  - [x] 3.4.2 Replace both project MessageService implementations with thin subclasses
  - [x] 3.4.3 Update all imports and delete originals
  - [x] 3.4.4 Run tests

- [x] 3.5 Extract FormSubmissionService to django_rseal
  - [x] 3.5.1 Create venv/libs/django-rseal/src/django_rseal/pipelines/services/form_submission.py
  - [x] 3.5.2 Replace both project implementations with thin subclasses
  - [x] 3.5.3 Update all imports and delete originals
  - [x] 3.5.4 Run tests

- [x] 3.6 Extract RoleBasedEmailTemplateSelector and EmailTemplateRegistry to django_rseal
  - [x] 3.6.1 Create venv/libs/django-rseal/src/django_rseal/email/selectors.py with RoleBasedEmailTemplateSelector
  - [x] 3.6.2 Create venv/libs/django-rseal/src/django_rseal/email/registry.py with EmailTemplateRegistry
  - [x] 3.6.3 Update all imports in both projects and delete originals
  - [x] 3.6.4 Run tests

- [x] 3.7 Extract Wagtail blocks (StructBlock, StreamBlock, etc.) to django_rseal/comp/
  - [x] 3.7.1 Audit all comp/ directories in both projects for Wagtail block classes
  - [x] 3.7.2 Copy all Wagtail blocks to venv/libs/django-rseal/src/django_rseal/comp/blocks.py
  - [x] 3.7.3 Copy StreamField block definitions to venv/libs/django-rseal/src/django_rseal/comp/stream_blocks.py
  - [x] 3.7.4 Update all imports in both projects and delete originals
  - [x] 3.7.5 Run tests

- [x] 3.8 Extract Wagtail snippets to django_rseal
  - [x] 3.8.1 Copy reusable Wagtail snippet classes to venv/libs/django-rseal/src/django_rseal/contrib/snippets/
  - [x] 3.8.2 Update all imports in both projects and delete originals
  - [x] 3.8.3 Run tests

- [x] 3.9 Extract Wagtail hooks to django_rseal
  - [x] 3.9.1 Copy reusable wagtail_hooks.py logic to venv/libs/django-rseal/src/django_rseal/contrib/wagtail_hooks.py
  - [x] 3.9.2 Update both projects to import hooks from django_rseal
  - [x] 3.9.3 Run tests

- [x] 3.10 Extract Unfold admin and Wagtail admin customizations to django_rseal/contrib/admin_site/
  - [x] 3.10.1 Copy Unfold admin customizations to venv/libs/django-rseal/src/django_rseal/contrib/admin_site/unfold.py
  - [x] 3.10.2 Copy Wagtail admin customizations to venv/libs/django-rseal/src/django_rseal/contrib/admin_site/wagtail.py
  - [x] 3.10.3 Update all imports in both projects and delete originals
  - [x] 3.10.4 Run tests

- [x] 3.11 Extract PrivacyConsentMiddleware to django_rseal
  - [x] 3.11.1 Copy PrivacyConsentMiddleware to venv/libs/django-rseal/src/django_rseal/contrib/privacy/middleware.py
  - [x] 3.11.2 Update MIDDLEWARE settings in both projects
  - [x] 3.11.3 Update all imports and delete originals
  - [x] 3.11.4 Run tests

- [x] 3.12 Extract cache utilities to django_rseal/contrib/cache/
  - [x] 3.12.1 Copy cache utility classes and decorators to venv/libs/django-rseal/src/django_rseal/contrib/cache/utils.py
  - [x] 3.12.2 Update all imports in both projects and delete originals
  - [x] 3.12.3 Run tests

- [x] 3.13 Extract Django signals to django_rseal/contrib/signals/
  - [x] 3.13.1 Copy reusable signal definitions to venv/libs/django-rseal/src/django_rseal/contrib/signals/
  - [x] 3.13.2 Update all imports in both projects and delete originals
  - [x] 3.13.3 Run tests

- [x] 3.14 Extract debug tools to django_rseal/contrib/debug_tools/
  - [x] 3.14.1 Copy debug utility classes to venv/libs/django-rseal/src/django_rseal/contrib/debug_tools/
  - [x] 3.14.2 Update all imports in both projects and delete originals
  - [x] 3.14.3 Run tests

- [x] 3.15 Extract email configuration utilities to django_rseal/contrib/email_config/
  - [x] 3.15.1 Copy email config helpers to venv/libs/django-rseal/src/django_rseal/contrib/email_config/
  - [x] 3.15.2 Update all imports in both projects and delete originals
  - [x] 3.15.3 Run tests

- [x] 3.16 Extract Orchestrator CLI to django_rseal/workflows/
  - [x] 3.16.1 Copy orchestrator CLI code to venv/libs/django-rseal/src/django_rseal/workflows/orchestrator.py
  - [x] 3.16.2 Update all imports in both projects and delete originals
  - [x] 3.16.3 Run tests

- [x] 3.17 Run full boundary check on django_rseal after all extractions
  - [x] 3.17.1 Run scripts/check_boundaries.py — verify django_rseal has no project-specific imports
  - [x] 3.17.2 Fix any violations found
  - [x] 3.17.3 Run full test suite for django_rseal package
  - [x] 3.17.4 Commit with message: "feat(rseal): extract all Wagtail and automation logic"


## Phase 4: django_grep — Extract Testing Infrastructure and Health Checks

- [x] 4.1 Create unified BaseTestCase in django_grep
  - [x] 4.1.1 Create venv/libs/django-grep/src/django_grep/tests/base.py with BaseTestCase extending django.test.TestCase
  - [x] 4.1.2 Add st_email() Hypothesis strategy to base.py
  - [x] 4.1.3 Add st_slug() Hypothesis strategy to base.py
  - [x] 4.1.4 Add st_uuid() Hypothesis strategy to base.py
  - [x] 4.1.5 Run django_grep package tests to verify helpers work

- [x] 4.2 Create unified factories in django_grep
  - [x] 4.2.1 Audit all factory_boy factory classes in both projects and packages
  - [x] 4.2.2 Copy reusable factories to venv/libs/django-grep/src/django_grep/tests/factories/
  - [x] 4.2.3 Update all test imports in both projects to use django_grep.tests.factories
  - [x] 4.2.4 Delete duplicate factory files from projects
  - [x] 4.2.5 Run tests

- [x] 4.3 Create unified fixtures in django_grep
  - [x] 4.3.1 Copy reusable test fixtures to venv/libs/django-grep/src/django_grep/tests/fixtures/
  - [x] 4.3.2 Update all test imports in both projects to use django_grep.tests.fixtures
  - [x] 4.3.3 Delete duplicate fixture files from projects
  - [x] 4.3.4 Run tests

- [x] 4.4 Create unified assertions in django_grep
  - [x] 4.4.1 Copy custom assertion helpers to venv/libs/django-grep/src/django_grep/tests/assertions/
  - [x] 4.4.2 Update all test imports in both projects to use django_grep.tests.assertions
  - [x] 4.4.3 Delete duplicate assertion files from projects
  - [x] 4.4.4 Run tests

- [x] 4.5 Create unified test mixins in django_grep
  - [x] 4.5.1 Copy reusable test mixin classes to venv/libs/django-grep/src/django_grep/tests/mixins/
  - [x] 4.5.2 Update all test imports in both projects
  - [x] 4.5.3 Delete duplicate mixin files from projects
  - [x] 4.5.4 Run tests

- [x] 4.6 Register pytest plugin in django_grep
  - [x] 4.6.1 Create venv/libs/django-grep/src/django_grep/tests/pytest_plugin.py with plugin registration
  - [x] 4.6.2 Register plugin in pyproject.toml under [tool.pytest11]
  - [x] 4.6.3 Verify plugin loads correctly in both projects

- [x] 4.7 Create health check system in django_grep
  - [x] 4.7.1 Create venv/libs/django-grep/src/django_grep/health/__init__.py
  - [x] 4.7.2 Create venv/libs/django-grep/src/django_grep/health/views.py with HealthCheckView, DatabaseHealthView, AssetsHealthView, MediaHealthView
  - [x] 4.7.3 Create venv/libs/django-grep/src/django_grep/health/urls.py with urlpatterns for all four endpoints
  - [x] 4.7.4 Add path('health/', include('django_grep.health.urls')) to ctc-research.com/configs/urls.py
  - [x] 4.7.5 Add path('health/', include('django_grep.health.urls')) to structa.cloud/configs/urls.py
  - [x] 4.7.6 Remove any existing health check views/urls from both projects
  - [x] 4.7.7 Test GET /health/ returns 200, GET /health/database/ returns 200, GET /health/assets/ returns 200, GET /health/media/ returns 200
  - [x] 4.7.8 Test GET /health/database/ returns 503 when database is unreachable

- [x] 4.8 Migrate all existing tests in both projects to use django_grep infrastructure
  - [x] 4.8.1 Write scripts/migrate_tests.py implementing TestMigrator
  - [x] 4.8.2 Run migrator against ctc-research.com/tests/ — replace TestCase with BaseTestCase, update factory/assertion imports
  - [x] 4.8.3 Run migrator against structa.cloud/tests/ — same replacements
  - [x] 4.8.4 Run migrator against all package tests in venv/libs/
  - [x] 4.8.5 Delete duplicate test infrastructure files from projects
  - [x] 4.8.6 Run full test suite and verify all tests pass

- [x] 4.9 Move seeder infrastructure to django_grep
  - [x] 4.9.1 Copy database seeder classes to venv/libs/django-grep/src/django_grep/seeder/
  - [x] 4.9.2 Copy management commands (backup_db, backup_media, load_fixtures) to venv/libs/django-grep/src/django_grep/management/commands/
  - [x] 4.9.3 Update all imports in both projects and delete originals
  - [x] 4.9.4 Run tests

- [x] 4.10 Run full boundary check — verify django_grep not imported by production code
  - [x] 4.10.1 Run scripts/check_boundaries.py grep-test-only rule
  - [x] 4.10.2 Fix any production code that imports django_grep
  - [x] 4.10.3 Commit with message: "feat(grep): extract unified testing infrastructure and health checks"


## Phase 5: nawaai — Verify Pure Python Boundary

- [x] 5.1 Audit nawaai for any Django imports and remove them
  - [x] 5.1.1 Run scripts/check_boundaries.py nawaai-no-django rule
  - [x] 5.1.2 For each violation found, refactor the nawaai module to remove the Django import (use dependency injection or pure Python alternatives)
  - [x] 5.1.3 Re-run boundary checker and verify zero violations
  - [x] 5.1.4 Run nawaai package tests
  - [x] 5.1.5 Commit with message: "fix(nawaai): remove all Django imports — pure Python only"


## Phase 6: Domain Restructuring — App Renames and Module Reorganization and Package Deduplication

- [x] 6.1 Rename apps/handlers to apps/accounts in ctc-research.com
  - [x] 6.1.1 Create ctc-research.com/apps/accounts/ directory with __init__.py and apps.py (AppConfig name='accounts')
  - [x] 6.1.2 Create migration ctc-research.com/apps/accounts/migrations/0001_rename_app_label.py with AlterModelTable operations to preserve all existing table names (e.g., table="handlers_person")
  - [x] 6.1.3 Create data migration to update ContentType records: ContentType.objects.filter(app_label='handlers').update(app_label='accounts')
  - [x] 6.1.4 Update INSTALLED_APPS in ctc-research.com settings to replace 'apps.handlers' with 'apps.accounts'
  - [x] 6.1.5 Update all imports across ctc-research.com from apps.handlers to apps.accounts
  - [x] 6.1.6 Run python manage.py migrate and verify no errors
  - [x] 6.1.7 Test migration reversal: python manage.py migrate accounts zero
  - [x] 6.1.8 Re-apply migration and verify data integrity
  - [x] 6.1.9 Run tests

- [x] 6.2 Rename apps/handlers to apps/accounts in structa.cloud
  - [x] 6.2.1 Repeat steps 6.1.1–6.1.9 for structa.cloud

- [x] 6.3 Rename apps/LMS to apps/lms in ctc-research.com
  - [x] 6.3.1 Create ctc-research.com/apps/lms/ with AppConfig name='lms'
  - [x] 6.3.2 Create migration with AlterModelTable to preserve table names (e.g., table="lms_cart")
  - [x] 6.3.3 Create data migration to update ContentType records
  - [x] 6.3.4 Update INSTALLED_APPS and all imports
  - [x] 6.3.5 Run migrations, test reversal, verify data integrity, run tests

- [x] 6.4 Rename apps/LMS to apps/lms in structa.cloud
  - [x] 6.4.1 Create structa.cloud/apps/lms/ with AppConfig name='alliance'
  - [x] 6.4.2 Create migration with AlterModelTable to preserve table names
  - [x] 6.4.3 Create data migration to update ContentType records
  - [x] 6.4.4 Update INSTALLED_APPS and all imports
  - [x] 6.4.5 Run migrations, test reversal, verify data integrity, run tests

- [x] 6.5 Rename apps/pages to apps/content in both projects
  - [x] 6.5.1 Create apps/content/ in ctc-research.com with AppConfig name='content'
  - [x] 6.5.2 Create migration with AlterModelTable to preserve table names
  - [x] 6.5.3 Create data migration to update ContentType records
  - [x] 6.5.4 Update INSTALLED_APPS and all imports in ctc-research.com
  - [x] 6.5.5 Repeat for structa.cloud
  - [x] 6.5.6 Run migrations, test reversal, verify data integrity, run tests

- [x] 6.6 Enforce standard sub-module layout in all renamed apps
  - [x] 6.6.1 For each renamed app in both projects, create missing subdirectories: admin/, filters/, forms/, managers/, middleware/, models/, services/, views/
  - [x] 6.6.2 Move existing files into correct subdirectories (e.g., move models.py content into models/__init__.py)
  - [x] 6.6.3 Update all internal imports within each app
  - [x] 6.6.4 Run tests after each app reorganization

- [x] 6.7 Detect and eliminate cross-domain leakage
  - [x] 6.7.1 Run scripts/identify_domains.py to detect modules that mix multiple domains
  - [x] 6.7.2 For each CrossDomainLeak found, split the module into domain-specific files
  - [x] 6.7.3 Update all imports after splits
  - [x] 6.7.4 Run tests

- [x] 6.8 Detect and eliminate circular dependencies
  - [x] 6.8.1 Run scripts/detect_cycles.py to find all circular dependency cycles
  - [x] 6.8.2 For each cycle, apply the suggested break strategy (extract-interface, dependency-injection, or event-based)
  - [x] 6.8.3 Re-run cycle detector and verify zero cycles
  - [x] 6.8.4 Run tests

- [x] 6.9 Commit domain restructuring
  - [x] 6.9.1 Run python manage.py check in both projects — verify zero errors
  - [x] 6.9.2 Run python manage.py showmigrations — verify all migrations applied
  - [x] 6.9.3 Commit with message: "refactor: rename apps to domain-aligned names with reversible migrations"

- [x] 6.10.1 Analyze duplication between django_osoul and django_rseal packages
  - [x] 6.10.1.1 Run scripts/analyze_duplication.py with focus on venv/libs/django-osoul/ and venv/libs/django-rseal/
  - [x] 6.10.1.2 Identify all duplicated classes, functions, and modules with ≥70% similarity
  - [x] 6.10.1.3 Categorize each duplicate as: belongs-in-osoul, belongs-in-rseal, or should-be-shared
  - [x] 6.10.1.4 Write PACKAGE_DUPLICATION_REPORT.md with detailed findings

- [x] 6.10.2 Resolve django_osoul vs django_rseal boundary violations
  - [x] 6.10.2.1 Check if django_osoul imports any Wagtail/Celery/django_rseal components
  - [x] 6.10.2.2 Check if django_rseal imports any project-specific code
  - [x] 6.10.2.3 Move any boundary-violating code to the correct package
  - [x] 6.10.2.4 Update all imports in both packages and projects

- [x] 6.10.3 Deduplicate shared utilities between packages
  - [x] 6.10.3.1 Identify utilities duplicated between django_osoul/contrib/ and django_rseal/contrib/
  - [x] 6.10.3.2 For each duplicate, decide canonical location (osoul for pure Django, rseal for Wagtail/automation)
  - [x] 6.10.3.3 Move code to canonical location and update all references
  - [x] 6.10.3.4 Delete duplicates from non-canonical location

- [x] 6.10.4 Deduplicate handler infrastructure
  - [x] 6.10.4.1 Compare django_osoul/handlers/ with django_rseal/handlers/
  - [x] 6.10.4.2 Identify any handler base classes or mixins that appear in both
  - [x] 6.10.4.3 Move pure Django handler infrastructure to django_osoul, Wagtail-specific to django_rseal
  - [x] 6.10.4.4 Update all imports in both packages and projects

- [x] 6.10.5 Deduplicate service layer patterns
  - [x] 6.10.5.1 Compare service patterns between django_osoul/services/ and django_rseal/pipelines/services/
  - [x] 6.10.5.2 Identify any service base classes that could be unified
  - [x] 6.10.5.3 Create clear separation: django_osoul for pure Django services, django_rseal for automation/pipeline services
  - [x] 6.10.5.4 Update all service implementations in projects

- [x] 6.10.6 Deduplicate manager classes
  - [x] 6.10.6.1 Check if any manager classes exist in both packages
  - [x] 6.10.6.2 Move all manager classes to django_osoul/managers/ (pure Django foundation)
  - [x] 6.10.6.3 Ensure django_rseal only contains automation-specific managers
  - [x] 6.10.6.4 Update all imports

- [x] 6.10.7 Deduplicate mixin classes
  - [x] 6.10.7.1 Compare django_osoul/mixins/ with any mixins in django_rseal
  - [x] 6.10.7.2 Move all pure Django mixins to django_osoul
  - [x] 6.10.7.3 Ensure django_rseal only contains Wagtail/automation-specific mixins
  - [x] 6.10.7.4 Update all imports

- [x] 6.10.8 Verify package boundaries after deduplication
  - [x] 6.10.8.1 Run scripts/check_boundaries.py — verify django_osoul has zero wagtail/celery/rseal imports
  - [x] 6.10.8.2 Run scripts/check_boundaries.py — verify django_rseal has zero project-specific imports
  - [x] 6.10.8.3 Fix any remaining boundary violations
  - [x] 6.10.8.4 Run full test suite for both packages

- [x] 6.10.9 Update package documentation
  - [x] 6.10.9.1 Update django_osoul/README.md to clearly state its scope (pure Django foundation)
  - [x] 6.10.9.2 Update django_rseal/README.md to clearly state its scope (Wagtail + automation)
  - [x] 6.10.9.3 Document the clear separation between packages in ARCHITECTURE.md
  - [x] 6.10.9.4 Update MIGRATION_GUIDE.md with any import path changes

- [x] 6.10.10 Commit package deduplication
  - [x] 6.10.10.1 Run full test suite for both packages and projects
  - [x] 6.10.10.2 Verify zero test failures
  - [x] 6.10.10.3 Commit with message: "refactor: deduplicate django_osoul and django_rseal packages with clear boundaries"

## Phase 7: Project Simplification — Thin Layer Pattern

- [x] 7.1 Audit both projects for remaining business logic that belongs in packages
  - [x] 7.1.1 Write scripts/check_thin_layer.py that scans project apps/ for classes/functions that are not: settings, URLs, project-specific models, templates, static files, or thin service subclasses
  - [x] 7.1.2 Run checker against ctc-research.com and structa.cloud
  - [x] 7.1.3 Produce THIN_LAYER_VIOLATIONS.md listing all remaining business logic in projects

- [x] 7.2 Convert remaining project services to thin subclasses of package base classes
  - [x] 7.2.1 For each service in ctc-research.com that has a corresponding base in django_rseal, replace with thin subclass pattern
  - [x] 7.2.2 For each service in structa.cloud that has a corresponding base in django_rseal, replace with thin subclass pattern
  - [x] 7.2.3 Add module-level docstrings documenting canonical import path: "Delegates to django_rseal.pipelines.services.CartServiceBase"
  - [x] 7.2.4 Run tests

- [x] 7.3 Remove all remaining duplicate managers from projects
  - [x] 7.3.1 Verify all managers now imported from django_osoul.managers
  - [x] 7.3.2 Delete any remaining duplicate manager files from both projects
  - [x] 7.3.3 Run tests

- [x] 7.4 Remove all remaining duplicate mixins from projects
  - [x] 7.4.1 Verify all mixins now imported from django_osoul.mixins or django_rseal
  - [x] 7.4.2 Delete any remaining duplicate mixin files from both projects
  - [x] 7.4.3 Run tests

- [x] 7.5 Remove all remaining duplicate forms from projects
  - [x] 7.5.1 Verify all base form classes now imported from django_osoul.forms
  - [x] 7.5.2 Delete any remaining duplicate form base files from both projects
  - [x] 7.5.3 Run tests

- [x] 7.6 Remove all remaining duplicate middleware from projects
  - [x] 7.6.1 Verify all middleware now imported from django_osoul.middlewares or django_rseal.contrib
  - [x] 7.6.2 Delete any remaining duplicate middleware files from both projects
  - [x] 7.6.3 Run tests

- [x] 7.7 Verify both projects follow identical structural patterns
  - [x] 7.7.1 Run scripts/check_consistency.py check_app_structure — verify both projects have accounts/, content/, blog/ and project-specific lms/ or alliance/
  - [x] 7.7.2 Fix any structural inconsistencies
  - [x] 7.7.3 Run tests

- [x] 7.8 Unify settings structure across both projects
  - [x] 7.8.1 Compare ctc-research.com/configs/settings/ with structa.cloud/configs/settings/
  - [x] 7.8.2 Ensure both use same base settings pattern and same environment overrides pattern
  - [x] 7.8.3 Ensure both use same middleware stack order
  - [x] 7.8.4 Ensure both use same URL routing patterns
  - [x] 7.8.5 Run python manage.py check in both projects

- [x] 7.9 Commit project simplification
  - [x] 7.9.1 Run scripts/check_thin_layer.py — verify zero violations
  - [x] 7.9.2 Run full test suite in both projects
  - [x] 7.9.3 Commit with message: "refactor: convert projects to thin layers delegating to packages"


## Phase 8: Cross-Project Consistency and Naming Conventions

- [x] 8.1 Enforce snake_case naming for all Python modules
  - [x] 8.1.1 Run scripts/enforce_naming.py check_module_names across entire ecosystem
  - [x] 8.1.2 Rename any CamelCase or mixed-case module files to snake_case
  - [x] 8.1.3 Update all imports after renames
  - [x] 8.1.4 Run tests

- [x] 8.2 Enforce PascalCase naming for all classes
  - [x] 8.2.1 Run scripts/enforce_naming.py check_class_names across entire ecosystem
  - [x] 8.2.2 Rename any non-PascalCase classes using AST-based refactoring
  - [x] 8.2.3 Update all references after renames
  - [x] 8.2.4 Run tests

- [x] 8.3 Enforce snake_case naming for all functions and variables
  - [x] 8.3.1 Run scripts/enforce_naming.py check_function_names across entire ecosystem
  - [x] 8.3.2 Rename any camelCase functions to snake_case
  - [x] 8.3.3 Update all call sites after renames
  - [x] 8.3.4 Run tests

- [x] 8.4 Verify both projects use same patterns for services, handlers, managers, and views
  - [x] 8.4.1 Run scripts/check_consistency.py check_naming_conventions
  - [x] 8.4.2 Fix any naming inconsistencies between projects
  - [x] 8.4.3 Run tests

- [x] 8.5 Maintain CHANGELOG.md files for each project and package
  - [x] 8.5.1 Create or update ctc-research.com/CHANGELOG.md with all changes from this refactoring
  - [x] 8.5.2 Create or update structa.cloud/CHANGELOG.md with all changes from this refactoring
  - [x] 8.5.3 Create or update venv/libs/django-osoul/CHANGELOG.md
  - [x] 8.5.4 Create or update venv/libs/django-rseal/CHANGELOG.md
  - [x] 8.5.5 Create or update venv/libs/django-grep/CHANGELOG.md
  - [x] 8.5.6 Create or update venv/libs/nawaai/CHANGELOG.md


## Phase 9: Template Strategy and Static Files

- [x] 9.1 Verify no templates exist in any venv/libs/ package
  - [x] 9.1.1 Run scripts/validate_templates.py check_no_package_templates
  - [x] 9.1.2 For each template found in a package, move it to the appropriate project's templates/ directory
  - [x] 9.1.3 Update all {% include %}, {% extends %}, and view render() calls to reference new template paths
  - [x] 9.1.4 Run tests

- [x] 9.2 Verify both projects maintain consistent template structure
  - [x] 9.2.1 Run scripts/validate_templates.py check_template_structure
  - [x] 9.2.2 Fix any structural inconsistencies between projects' template directories
  - [x] 9.2.3 Run tests

- [x] 9.3 Update all template references after refactoring
  - [x] 9.3.1 Run scripts/validate_templates.py verify_template_resolution
  - [x] 9.3.2 Fix all broken {% include %}, {% extends %}, {% load %}, and static file references
  - [x] 9.3.3 Run tests

- [x] 9.4 Verify templatetags placement
  - [x] 9.4.1 Audit all templatetags directories — reusable tags belong in packages, project-specific tags stay in projects
  - [x] 9.4.2 Move reusable templatetags to appropriate package (django_osoul or django_rseal)
  - [x] 9.4.3 Update all {% load %} tags in templates
  - [x] 9.4.4 Run tests

- [x] 9.5 Verify static files placement
  - [x] 9.5.1 Audit all static files — reusable static assets belong in packages, project-specific stay in projects
  - [x] 9.5.2 Move reusable static files to appropriate package
  - [x] 9.5.3 Run python manage.py collectstatic in both projects and verify no errors
  - [x] 9.5.4 Run tests


## Phase 10: Dependency Alignment

- [x] 10.1 Scan all pyproject.toml files and identify version conflicts
  - [x] 10.1.1 Write scripts/analyze_dependencies.py implementing DependencyAnalyzer
  - [x] 10.1.2 Run analyzer against all pyproject.toml files in projects and packages
  - [x] 10.1.3 Write DEPENDENCY_CONFLICTS.md listing all version conflicts with recommended unified versions

- [x] 10.2 Unify dependency versions across all pyproject.toml files
  - [x] 10.2.1 Update ctc-research.com/pyproject.toml with unified versions
  - [x] 10.2.2 Update structa.cloud/pyproject.toml with unified versions
  - [x] 10.2.3 Update venv/libs/django-osoul/pyproject.toml with unified versions
  - [x] 10.2.4 Update venv/libs/django-rseal/pyproject.toml with unified versions
  - [x] 10.2.5 Update venv/libs/django-grep/pyproject.toml with unified versions
  - [x] 10.2.6 Update venv/libs/nawaai/pyproject.toml with unified versions

- [x] 10.3 Remove unused dependencies from all pyproject.toml files
  - [x] 10.3.1 Run scripts/analyze_dependencies.py find_unused_dependencies
  - [x] 10.3.2 Remove each unused dependency from the appropriate pyproject.toml
  - [x] 10.3.3 Run tests after each removal to verify nothing breaks

- [x] 10.4 Ensure all packages declare their dependencies explicitly
  - [x] 10.4.1 Verify django_osoul/pyproject.toml lists all its direct dependencies
  - [x] 10.4.2 Verify django_rseal/pyproject.toml lists all its direct dependencies including django_osoul
  - [x] 10.4.3 Verify django_grep/pyproject.toml lists all its direct dependencies
  - [x] 10.4.4 Verify nawaai/pyproject.toml lists only pure Python dependencies

- [x] 10.5 Update uv.lock files after all dependency changes
  - [x] 10.5.1 Run uv lock in ctc-research.com
  - [x] 10.5.2 Run uv lock in structa.cloud
  - [x] 10.5.3 Run full test suite in both projects to verify compatibility


## Phase 11: Code Recovery and Branch Reconciliation

- [x] 11.1 Scan git history for deleted files in the last 6 months
  - [x] 11.1.1 Write scripts/recover_code.py implementing CodeRecoverySystem
  - [x] 11.1.2 Run scan_git_history() and identify all deleted Python files
  - [x] 11.1.3 Run find_references() for each deleted file to check if still referenced in current codebase
  - [x] 11.1.4 Write RECOVERY_CANDIDATES.md listing all deleted files still referenced, with recovery priority

- [x] 11.2 Recover and reintegrate deleted code
  - [x] 11.2.1 For each high-priority recovery candidate, run recover_file() to extract from git history
  - [x] 11.2.2 Place recovered code in the correct package location per the new architecture
  - [x] 11.2.3 Update all imports to reference the new location
  - [x] 11.2.4 Add or verify test coverage for recovered code
  - [x] 11.2.5 Write RECOVERY_REPORT.md documenting all recovered files

- [x] 11.3 For code that cannot be recovered, document and create reimplementation tasks
  - [x] 11.3.1 For each unrecoverable file, document the missing functionality in RECOVERY_REPORT.md
  - [x] 11.3.2 Create specific reimplementation tasks in this file under a "Reimplementation" section

- [x] 11.4 Compare recent feature branches with main and identify improvements to merge
  - [x] 11.4.1 Write scripts/analyze_branches.py implementing BranchAnalyzer
  - [x] 11.4.2 Run list_recent_branches() to find all branches from last 3 months
  - [x] 11.4.3 Run compare_with_main() for each branch and identify improvements
  - [x] 11.4.4 Write MERGE_CANDIDATES.md listing improvements with merge priority

- [x] 11.5 Merge improvements from feature branches using quality-preserving strategy
  - [x] 11.5.1 Write scripts/intelligent_merge.py implementing IntelligentMerger
  - [x] 11.5.2 For each high-priority improvement, run merge_with_validation()
  - [x] 11.5.3 Verify no duplication introduced, no boundary violations, no test regressions
  - [x] 11.5.4 Write MERGE_REPORT.md documenting all merged improvements


## Phase 12: Parser and Serializer Round-Trip Testing

- [x] 12.1 Identify all parsers and serializers in the ecosystem
  - [x] 12.1.1 Write scripts/detect_parsers.py implementing ParserDetector
  - [x] 12.1.2 Run find_all_parsers() and find_all_serializers() across entire codebase
  - [x] 12.1.3 Write PARSER_INVENTORY.md listing all parsers and serializers with their input/output types

- [x] 12.2 Verify each parser has a corresponding pretty printer
  - [x] 12.2.1 For each parser without a pretty printer, create one in the same module
  - [x] 12.2.2 Pretty printer must accept the parser's output type and return valid input format
  - [x] 12.2.3 Document the grammar being parsed in module-level docstring

- [x] 12.3 Implement round-trip property tests for all parsers
  - [x] 12.3.1 For each parser, create a property-based test: given valid_input, parse(pretty_print(parse(valid_input))) == parse(valid_input)
  - [x] 12.3.2 Use Hypothesis with appropriate strategies (st_email, st_slug, st_uuid, or custom strategies)
  - [x] 12.3.3 Verify parsers return descriptive errors for invalid inputs
  - [x] 12.3.4 Run all round-trip tests and verify they pass


## Phase 13: CI/CD and Import Linter Configuration

- [x] 13.1 Create .importlinter configuration file
  - [x] 13.1.1 Create .importlinter at workspace root with all four contracts: nawaai-no-django, osoul-no-wagtail, rseal-no-projects, grep-test-only
  - [x] 13.1.2 Add dependency-direction layers contract
  - [x] 13.1.3 Run import-linter --config .importlinter and verify zero violations
  - [x] 13.1.4 Fix any remaining violations

- [x] 13.2 Create GitHub Actions workflow for architecture validation
  - [x] 13.2.1 Create .github/workflows/architecture-validation.yml with jobs: boundary-check, duplication-check, test-all-packages, test-projects, import-check
  - [x] 13.2.2 Configure boundary-check job to run import-linter and fail on any violation
  - [x] 13.2.3 Configure duplication-check job to run scripts/analyze_duplication.py --threshold 0.70 --fail-on-violation
  - [x] 13.2.4 Configure test-all-packages job with matrix strategy for all four packages
  - [x] 13.2.5 Configure test-projects job with matrix strategy for both projects
  - [x] 13.2.6 Configure import-check job to run scripts/check_imports.py --fail-on-error
  - [x] 13.2.7 Verify workflow runs in under 10 minutes

- [x] 13.3 Verify CI passes on current codebase
  - [x] 13.3.1 Push to a test branch and verify all CI jobs pass
  - [x] 13.3.2 Fix any CI failures
  - [x] 13.3.3 Merge to main only after all CI jobs pass


## Phase 14: Documentation

- [x] 14.1 Create ARCHITECTURE.md at workspace root
  - [x] 14.1.1 Document the package dependency graph as a Mermaid diagram: stdlib → nawaai → django_osoul → django_rseal → projects
  - [x] 14.1.2 Document each package's responsibilities and what it contains
  - [x] 14.1.3 Document all boundary rules with examples of allowed and forbidden imports
  - [x] 14.1.4 Document domain organization (accounts, content, lms/alliance, messaging, cart, forms)
  - [x] 14.1.5 Document the thin layer pattern with a CartService example

- [x] 14.2 Create MIGRATION_GUIDE.md at workspace root
  - [x] 14.2.1 List every changed import path in the format: Before: from apps.handlers.managers... → After: from django_osoul.managers...
  - [x] 14.2.2 Document all app renames (handlers→accounts, LMS→lms/alliance, pages→content)
  - [x] 14.2.3 Document all deprecated APIs and their replacements
  - [x] 14.2.4 Include troubleshooting section for common migration errors

- [x] 14.3 Write comprehensive README.md for django_osoul
  - [x] 14.3.1 Document package purpose: "Pure Django foundation layer — models, managers, mixins, utils, comp, contrib"
  - [x] 14.3.2 Document installation, quick start, and all public APIs with usage examples
  - [x] 14.3.3 Document boundary rules: must not import wagtail, celery, or django_rseal
  - [x] 14.3.4 Document all sub-modules: handlers/, managers/, mixins/, utils/, comp/, contrib/, middlewares/, filters/, forms/, backends/, adapters/, services/

- [x] 14.4 Write comprehensive README.md for django_rseal
  - [x] 14.4.1 Document package purpose: "Automation layer — pipelines, services, workflows, email, signals, admin, cache, commands"
  - [x] 14.4.2 Document installation, quick start, and all public APIs with usage examples
  - [x] 14.4.3 Document CartServiceBase thin subclass pattern with full code example
  - [x] 14.4.4 Document all Wagtail components: blocks, snippets, hooks, admin customizations

- [x] 14.5 Write comprehensive README.md for django_grep
  - [x] 14.5.1 Document package purpose: "Unified testing framework — seeder, test base, fixtures, factories, assertions, pytest plugin, health checks"
  - [x] 14.5.2 Document BaseTestCase usage and all Hypothesis helpers (st_email, st_slug, st_uuid)
  - [x] 14.5.3 Document health check endpoints and project integration via include('django_grep.health.urls')
  - [x] 14.5.4 Document pytest plugin registration

- [x] 14.6 Write comprehensive README.md for nawaai
  - [x] 14.6.1 Document package purpose: "Pure Python AI/MCP toolkit — ai, chat, mcp, orchestrator, seeder"
  - [x] 14.6.2 Document boundary rule: zero Django imports
  - [x] 14.6.3 Document all public APIs with usage examples

- [x] 14.7 Organize .kiro/specs/ with clear status markers
  - [x] 14.7.1 Verify all completed specs have all tasks marked [x]
  - [x] 14.7.2 Update .kiro/specs-organized/README.md with current status of all specs
  - [x] 14.7.3 Ensure every spec has requirements.md, design.md, and tasks.md


## Phase 15: Migration Safety Verification

- [x] 15.1 Verify all migrations have reverse operations
  - [x] 15.1.1 Write scripts/validate_migrations.py implementing MigrationValidator
  - [x] 15.1.2 Run check_all_migrations() across both projects
  - [x] 15.1.3 For each migration without a reverse operation, add the reverse operation
  - [x] 15.1.4 Write MIGRATION_SAFETY_REPORT.md listing all migrations and their reversal status

- [x] 15.2 Test migration reversal for all app rename migrations
  - [x] 15.2.1 Run python manage.py migrate accounts zero in ctc-research.com — verify success
  - [x] 15.2.2 Re-apply: python manage.py migrate accounts — verify success
  - [x] 15.2.3 Repeat for lms, content apps in ctc-research.com
  - [x] 15.2.4 Repeat for accounts, alliance, content apps in structa.cloud
  - [x] 15.2.5 Verify data integrity after each reversal and re-application

- [x] 15.3 Verify migrations run successfully in Docker containers
  - [x] 15.3.1 Build Docker image for ctc-research.com and run python manage.py migrate — verify no errors
  - [x] 15.3.2 Build Docker image for structa.cloud and run python manage.py migrate — verify no errors
  - [x] 15.3.3 Fix any Docker-specific migration issues


## Phase 16: Final Validation and Completion

- [x] 16.1 Run full duplication analysis — verify zero duplication
  - [x] 16.1.1 Run scripts/analyze_duplication.py --threshold 0.70 across entire ecosystem
  - [x] 16.1.2 Verify all code pairs have < 70% similarity
  - [x] 16.1.3 Fix any remaining duplication found

- [x] 16.2 Run full boundary check — verify zero violations
  - [x] 16.2.1 Run import-linter --config .importlinter
  - [x] 16.2.2 Verify zero violations for all four contracts
  - [x] 16.2.3 Fix any remaining violations

- [x] 16.3 Run full test suite across all packages and projects
  - [x] 16.3.1 Run uv run pytest tests/ -v in venv/libs/django-osoul/
  - [x] 16.3.2 Run uv run pytest tests/ -v in venv/libs/django-rseal/
  - [x] 16.3.3 Run uv run pytest tests/ -v in venv/libs/django-grep/
  - [x] 16.3.4 Run uv run pytest tests/ -v in venv/libs/nawaai/
  - [x] 16.3.5 Run uv run pytest tests/ -v in ctc-research.com/
  - [x] 16.3.6 Run uv run pytest tests/ -v in structa.cloud/
  - [x] 16.3.7 Fix any test failures

- [x] 16.4 Verify Docker health for both projects
  - [x] 16.4.1 Run docker compose up -d for ctc-research.com
  - [x] 16.4.2 Verify GET /health/ returns HTTP 200
  - [x] 16.4.3 Verify GET /health/database/ returns HTTP 200
  - [x] 16.4.4 Verify GET /health/assets/ returns HTTP 200
  - [x] 16.4.5 Verify GET /health/media/ returns HTTP 200
  - [x] 16.4.6 Repeat for structa.cloud
  - [x] 16.4.7 Fix any Docker health issues

- [x] 16.5 Verify zero import errors across entire ecosystem
  - [x] 16.5.1 Run python -c "import django_osoul" — verify no ImportError
  - [x] 16.5.2 Run python -c "import django_rseal" — verify no ImportError
  - [x] 16.5.3 Run python -c "import django_grep" — verify no ImportError
  - [x] 16.5.4 Run python -c "import nawaai" — verify no ImportError
  - [x] 16.5.5 Run python manage.py check in ctc-research.com — verify zero errors
  - [x] 16.5.6 Run python manage.py check in structa.cloud — verify zero errors

- [x] 16.6 Verify all migrations applied successfully
  - [x] 16.6.1 Run python manage.py showmigrations in ctc-research.com — verify all [X]
  - [x] 16.6.2 Run python manage.py showmigrations in structa.cloud — verify all [X]

- [x] 16.7 Verify naming conventions across entire ecosystem
  - [x] 16.7.1 Run scripts/enforce_naming.py check_module_names — verify zero violations
  - [x] 16.7.2 Run scripts/enforce_naming.py check_class_names — verify zero violations
  - [x] 16.7.3 Run scripts/enforce_naming.py check_function_names — verify zero violations

- [x] 16.8 Verify template organization
  - [x] 16.8.1 Run scripts/validate_templates.py check_no_package_templates — verify zero violations
  - [x] 16.8.2 Run scripts/validate_templates.py verify_template_resolution — verify zero broken references

- [x] 16.9 Verify all specs are complete
  - [x] 16.9.1 Run scripts/track_spec_status.py — verify all specs have all tasks marked [x]
  - [x] 16.9.2 Fix any incomplete tasks found

- [x] 16.10 Retest websites structa.cloud and ctc-research with all tests using file
  - [x] 16.10.1 Create scripts/run_all_tests.py that runs all tests for both websites
  - [x] 16.10.2 Create scripts/verify_test_parity.py to verify test parity between websites
  - [x] 16.10.3 Ensure both websites have all tests and all tests pass
  - [x] 16.10.4 Ensure both websites have the same count of tests
  - [x] 16.10.5 Create full test coverage for both websites to ensure parity

- [x] 16.11 Generate COMPLETION_REPORT.md
  - [x] 16.11.1 Write scripts/validate_system.py implementing SystemValidator
  - [x] 16.11.2 Run validate_all() and generate COMPLETION_REPORT.md documenting:
    - Summary of all changes made
    - Duplication check results (before/after)
    - Boundary check results
    - Test results (total/passed/failed) for both websites
    - Test count parity verification
    - Docker health status
    - All import path changes
    - All app renames
    - All recovered code
    - All merged improvements
  - [x] 16.11.3 Verify COMPLETION_REPORT.md documents all 17 final deliverables from Requirement 17

- [x] 16.12 Final commit and tag
  - [x] 16.12.1 Commit all remaining changes with message: "feat: complete ecosystem-wide architectural refactoring"
  - [x] 16.12.2 Create git tag: ecosystem-refactor-complete
  - [x] 16.12.3 Push tag to remote


## Phase 17: Documentation Organization and Cleanup

- [x] 17.1 Organize all documentation files in the base directory
  - [x] 17.1.1 Create scripts/organize_docs.py to organize documentation files
  - [x] 17.1.2 Update all references to moved documentation files
  - [x] 17.1.3 Verify base directory has no .md files except README.md

- [x] 17.2 Create comprehensive README.md for the project using venv/.md.template.md
  - [x] 17.2.1 Update base README.md to include:
    - Project overview and architecture
    - Setup instructions for both websites
    - Running scripts and tests for both structa.cloud and ctc-research
    - Package documentation links
    - Development workflow
  - [x] 17.2.2 Add section for running test scripts for both websites with examples
  - [x] 17.2.3 Add section for running validation scripts
  - [x] 17.2.4 Add links to all documentation in docs/ directory

- [x] 17.3 Organize documentation by category
  - [x] 17.3.1 Create docs/architecture/ directory for architecture documentation
  - [x] 17.3.2 Create docs/testing/ directory for testing documentation
  - [x] 17.3.3 Create docs/deployment/ directory for deployment documentation
  - [x] 17.3.4 Create docs/development/ directory for development workflow
  - [x] 17.3.5 Create docs/reports/ directory for completion reports and validation reports
  - [x] 17.3.6 Move appropriate .md files to each category directory

- [x] 17.4 Create documentation index
  - [x] 17.4.1 Create docs/README.md with table of contents linking to all documentation
  - [x] 17.4.2 Ensure all documentation files are properly linked
  - [x] 17.4.3 Verify no broken links in documentation

- [x] 17.5 Create scripts documentation
  - [x] 17.5.1 Create docs/scripts/ directory
  - [x] 17.5.2 Create docs/scripts/README.md documenting all available scripts
  - [x] 17.5.3 Document each script's purpose, usage, and parameters
  - [x] 17.5.4 Add examples for running test scripts for both websites
  - [x] 17.5.5 Document scripts/run_all_tests.py for running tests on both websites

- [x] 17.6 Create test documentation
  - [x] 17.6.1 Create docs/tests/ directory
  - [x] 17.6.2 Create docs/tests/README.md documenting test structure for both websites
  - [x] 17.6.3 Document how to run tests for both structa.cloud and ctc-research
  - [x] 17.6.4 Document test count parity verification process

- [x] 17.7 Verify documentation organization
  - [x] 17.7.1 Run check to ensure base directory has only README.md
  - [x] 17.7.2 Verify all .md files are properly organized in docs/ directory
  - [x] 17.7.3 Test all documentation links work correctly

- [x] 17.8 Final documentation review
  - [x] 17.8.1 Review all documentation for accuracy and completeness
  - [x] 17.8.2 Update any outdated information
  - [x] 17.8.3 Ensure documentation reflects the current architecture and workflow
  - [x] 17.8.4 Verify documentation includes instructions for running scripts and tests for both websites

- [x] 17.9 Commit documentation organization
  - [x] 17.9.1 Commit all documentation changes with message: "docs: organize documentation and cleanup base directory"
  - [x] 17.9.2 Verify documentation structure is clean and maintainable
