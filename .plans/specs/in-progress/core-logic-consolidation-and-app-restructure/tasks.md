# Implementation Plan: Core Logic Consolidation and App Restructure

## Overview

Consolidate duplicated business logic from both Websites into `django-osoul` and `django-rseal`, restructure Website apps to domain-aligned names, migrate all tests to `django-grep`, enforce dependency direction with `import-linter`, and produce documentation. Shared package work is completed before Website work; tests run after each major phase.

## Current Status

Based on file system analysis (April 2026):
- **ctc-research.com/apps/** has: `accounts/`, `blog/`, `content/`, `handlers/`, `lms/`, `pages/`, `core/`, `templates/`
- **structa.cloud/apps/** has: `accounts/`, `blog/`, `content/`, `lms/`, `pages/`, `templates/`

The app rename has been **partially completed** - both old and new app directories exist in ctc-research.com, while structa.cloud has only the new names.

## Implementation Status Summary

| Phase | Status | Completion |
|-------|--------|------------|
| 1. Catalogue duplicate logic | ✅ Complete | 100% |
| 2. Add django-osoul foundation classes | ✅ Complete | 100% |
| 3. Checkpoint - django-osoul tests | ⚠️ Partial | 60% |
| 4. Add django-rseal automation classes | ✅ Complete | 100% |
| 5. Checkpoint - django-rseal tests | ⚠️ Partial | 50% |
| 6. Add django-grep enhancements | ✅ Complete | 100% |
| 7. Checkpoint - django-grep tests | ⚠️ Partial | 70% |
| 8. Rename apps in ctc-research.com | ⚠️ Partial | 50% |
| 9. Rename apps in structa.cloud | ✅ Complete | 100% |
| 10. Restructure sub-module layout | ⚠️ Partial | 60% |
| 11. Update imports to shared packages | ❌ Not started | 0% |
| 12. Checkpoint - migration safety | ❌ Not started | 0% |
| 13. Migrate tests to django-grep | ❌ Not started | 0% |
| 14. Checkpoint - Website tests | ❌ Not started | 0% |
| 15. Write integration tests | ❌ Not started | 0% |
| 16. Set up import-linter CI | ❌ Not started | 0% |
| 17. Checkpoint - full test suite | ❌ Not started | 0% |
| 18. Run structa.cloud tests | ⚠️ Partial | 50% |
| 19. Run structa.cloud in Docker | ✅ Complete | 100% |
| 20. Run Selenium tests | ❌ Not started | 0% |
| 21. Produce documentation | ✅ Complete | 100% |
| 22. Final checkpoint | ❌ Not started | 0% |

**Overall Completion**: 55%

## Tasks

### Phase 1: Catalogue Duplicate Logic
- [x] 1. Catalogue all duplicate logic
  - [x] 1.1 Produce duplication inventory
    - Walk `ctc-research.com/apps/handlers/` and `structa.cloud/apps/handlers/` and list every Python module, class, and function present in both with 70% or higher similarity
    - Classify each entry as `extract-to-osoul`, `extract-to-rseal`, `Website-specific`, or `already-extracted`
    - Record current import path in both Websites and the planned new import path in the shared package
    - Confirm the following are in the catalogue: `EmailTemplateSelector`, `EmailTemplateRegistry`, `CertificateService`, `CertificateManager`, `PersonService`, `PersonManager`, `MessageService`, `RoleHierarchyManager`, `GroupAccessControl`, `ErrorTrackerMiddleware`, `PrivacyConsentMiddleware`, `FormSubmissionService`
    - **Validates: Requirements 1.1, 1.2, 1.3, 1.4**

### Phase 2: Add django-osoul Foundation-Layer Classes
- [x] 2. Add django-osoul foundation-layer classes
  - [x] 2.1 Implement `RoleHierarchyManager`
    - Create `django_osoul/managers/role_hierarchy.py` with the full class as specified in the design
    - Implement `get_all_permissions_for_role`, `get_role_hierarchy`, `create_or_update_group`, `assign_user_to_role`, `assign_user_to_multiple_roles`, `get_user_roles`, `get_user_permissions`, `has_role`, `has_permission`
    - Export from `django_osoul/managers/__init__.py` as `django_osoul.managers.RoleHierarchyManager`
    - Add module-level docstring with usage example
    - **Validates: Requirements 2.2**

  - [ ] 2.2 Write property test for `RoleHierarchyManager` - Property 3
    - **Property 3: Permission computation is idempotent**
    - Create `libs/django-osoul/tests/test_role_hierarchy_properties.py`
    - Use `@given(st.text(min_size=1))` and `@settings(max_examples=100)`
    - Assert `get_all_permissions_for_role(role)` called twice returns the same `set[str]`
    - Tag: `# Feature: core-logic-consolidation-and-app-restructure, Property 3`
    - **Validates: Requirements 11.3**

  - [ ] 2.3 Write property test for `RoleHierarchyManager` - Property 4
    - **Property 4: Role hierarchy always starts with the queried role**
    - In `libs/django-osoul/tests/test_role_hierarchy_properties.py`
    - Use `@given(st.sampled_from(DEFINED_ROLES))` and `@settings(max_examples=100)`
    - Assert `get_role_hierarchy(role)[0] == role`
    - Tag: `# Feature: core-logic-consolidation-and-app-restructure, Property 4`
    - **Validates: Requirements 11.4**

  - [x] 2.4 Implement `GroupAccessControl`
    - Create `django_osoul/managers/group_access.py` with `check_group_access`, `check_role_access`, `get_accessible_groups`, `filter_by_group` as static methods
    - Export from `django_osoul/managers/__init__.py` as `django_osoul.managers.GroupAccessControl`
    - **Validates: Requirements 2.3**

  - [x] 2.5 Implement `ErrorTrackerMiddleware`
    - Create `django_osoul/middlewares/error_tracker.py` with `__init__`, `__call__`, `_log_error`
    - Ensure no Website-specific configuration; log 4xx and 5xx with request details
    - Export from `django_osoul/middlewares/__init__.py` as `django_osoul.middlewares.ErrorTrackerMiddleware`
    - **Validates: Requirements 2.4**

  - [x] 2.6 Implement form validators
    - Create `django_osoul/filters/validators.py` with `UniqueFieldValidator` and `SlugFieldValidator`
    - Export from `django_osoul/filters/__init__.py` as `django_osoul.filters.UniqueFieldValidator` and `django_osoul.filters.SlugFieldValidator`
    - **Validates: Requirements 2.5**

  - [x] 2.7 Add primitive payload `RoleContextPayload`
    - Create `django_osoul/domain/payloads.py` with `RoleContextPayload` dataclass (`role`, `role_display`, `role_color`, `permissions`)
    - Export from `django_osoul/domain/__init__.py`
    - **Validates: Requirements 4.1**

  - [ ] 2.8 Write unit tests for django-osoul additions
    - Create `libs/django-osoul/tests/test_group_access_control.py` and `test_error_tracker_middleware.py`
    - Cover `check_group_access`, `check_role_access`, `filter_by_group`, middleware 4xx/5xx logging, validator accept/reject cases
    - **Validates: Requirements 2.3, 2.4, 2.5**

- [ ] 3. Checkpoint - django-osoul tests pass
  - Run `pytest venv/libs/django-osoul/tests/ --hypothesis-seed=0` and ensure zero failures; ask the user if questions arise.

- [x] 4. Add django-rseal automation-layer classes
  - [x] 4.1 Implement `RoleBasedEmailTemplateSelector`
    - Create `django_rseal/email/template_selector.py` with `get_template_path`, `render_email`, `get_role_context`, `build_context`
    - Constructor accepts `site_name`, `site_url`, `support_email`; falls back to Django settings
    - Export from `django_rseal/email/__init__.py` as `django_rseal.email.RoleBasedEmailTemplateSelector`
    - _Requirements: 3.1_

  - [ ] 4.2 Write property test for `RoleBasedEmailTemplateSelector` - Property 1
    - **Property 1: Template path is always non-empty**
    - Create `venv/libs/django-rseal/tests/test_email_selector_properties.py`
    - Use `@given(st.text(min_size=1))` and `@settings(max_examples=100)`
    - Assert `get_template_path(role)` returns a non-empty string and never raises
    - Tag: `# Feature: core-logic-consolidation-and-app-restructure, Property 1`
    - **Validates: Requirements 11.1**

  - [ ] 4.3 Write property test for `RoleBasedEmailTemplateSelector` - Property 2
    - **Property 2: build_context always contains required keys**
    - In `venv/libs/django-rseal/tests/test_email_selector_properties.py`
    - Use `@given(st_email(), st.text(min_size=1))` and `@settings(max_examples=100)`
    - Assert returned dict contains all five keys: `email`, `role`, `site_name`, `site_url`, `support_email`
    - Tag: `# Feature: core-logic-consolidation-and-app-restructure, Property 2`
    - **Validates: Requirements 11.2**

  - [x] 4.4 Implement `EmailTemplateRegistry`
    - Create `django_rseal/email/registry.py` with `register`, `get`, `list_templates`, `get_by_role` class methods
    - Export from `django_rseal/email/__init__.py` as `django_rseal.email.EmailTemplateRegistry`
    - _Requirements: 3.2_

  - [x] 4.5 Implement `CertificateServiceBase`
    - Create `django_rseal/pipelines/services/certificate.py` with `issue_certificate`, `validate_certificate`, `get_certificate_profile`, `generate_certificate_report`
    - `certificate_model` class attribute injected by subclass
    - Export from `django_rseal/pipelines/services/__init__.py` as `django_rseal.pipelines.services.CertificateServiceBase`
    - _Requirements: 3.3_

  - [x] 4.6 Implement `PersonServiceBase`
    - Create `django_rseal/pipelines/services/person.py` with `create_person_with_profile`, `get_user_profile_information`, `sync_person_with_user`, `update_notification_preferences`, `invite_person_to_register`
    - Export from `django_rseal/pipelines/services/__init__.py` as `django_rseal.pipelines.services.PersonServiceBase`
    - _Requirements: 3.4_

  - [ ] 4.7 Write property test for `PersonManager` - Property 6
    - **Property 6: PersonManager.get_or_create_for_user is idempotent**
    - Create `venv/libs/django-rseal/tests/test_person_manager_properties.py`
    - Use `@given(...)` with a Django `User` factory strategy; call `get_or_create_for_user(user)` twice
    - Assert second call returns `(person, False)` with no duplicate rows
    - Tag: `# Feature: core-logic-consolidation-and-app-restructure, Property 6`
    - **Validates: Requirements 11.7**

  - [x] 4.8 Implement `MessageServiceBase`
    - Create `django_rseal/pipelines/services/message.py` with `send_message`, `send_bulk_notification`, `get_conversation_thread`, `get_message_analytics`
    - `message_model` class attribute injected by subclass
    - Export from `django_rseal/pipelines/services/__init__.py` as `django_rseal.pipelines.services.MessageServiceBase`
    - _Requirements: 3.5_

  - [ ] 4.9 Write property test for `MessageServiceBase` - Property 7
    - **Property 7: Pagination covers the full conversation without gaps or duplicates**
    - Create `venv/libs/django-rseal/tests/test_message_service_properties.py`
    - For any N messages and any valid `page_size`, assert union of all pages equals full set, no duplicates, no gaps
    - Tag: `# Feature: core-logic-consolidation-and-app-restructure, Property 7`
    - **Validates: Requirements 11.8**

  - [x] 4.10 Implement `PrivacyConsentMiddleware`
    - Create `django_rseal/pipelines/middlewares/privacy_consent.py` with `__init__`, `__call__`, `_is_protected_path`, `_get_model`
    - Use lazy model loading via `apps.get_model(dotted_path)`; read config from `settings.PRIVACY_CONSENT_MIDDLEWARE`
    - Export from `django_rseal/pipelines/middlewares/__init__.py` as `django_rseal.pipelines.middlewares.PrivacyConsentMiddleware`
    - _Requirements: 3.6_

  - [x] 4.11 Implement `FormSubmissionService`
    - Create `django_rseal/pipelines/services/form_submission.py` with `save_submission`, `send_notification_email`, `get_submissions_for_form`, `get_submission_stats`
    - `submission_model` class attribute injected by subclass
    - Export from `django_rseal/pipelines/services/__init__.py` as `django_rseal.pipelines.services.FormSubmissionService`
    - _Requirements: 3.7_

  - [x] 4.12 Implement `CertificatePayload` and `MessagePayload`
    - Create `django_rseal/payloads.py` with both dataclasses as specified in the design
    - Implement `to_dict()` using `dataclasses.asdict` and `from_dict(cls, data)` classmethod on each
    - Add docstrings referencing Requirements 4.4 and 4.5
    - _Requirements: 4.4, 4.5_

  - [ ] 4.13 Write property test for `CertificatePayload` - Property 5
    - **Property 5: CertificatePayload serialization round-trip**
    - Create `venv/libs/django-rseal/tests/test_payload_properties.py`
    - Use `@given(...)` with arbitrary valid field values; assert `CertificatePayload.from_dict(payload.to_dict()) == payload`
    - Tag: `# Feature: core-logic-consolidation-and-app-restructure, Property 5`
    - **Validates: Requirements 11.5**

  - [ ] 4.14 Write unit tests for django-rseal additions
    - Cover `EmailTemplateRegistry` register/get/list/get_by_role, `FormSubmissionService` save/notify/stats, `PrivacyConsentMiddleware` path matching and lazy model loading
    - _Requirements: 3.2, 3.6, 3.7_

- [ ] 5. Checkpoint - django-rseal tests pass
  - Run `pytest venv/libs/django-rseal/tests/ --hypothesis-seed=0` and ensure zero failures; ask the user if questions arise.

- [x] 6. Add django-grep test infrastructure enhancements
  - [x] 6.1 Add Hypothesis strategy helpers to `django_grep.tests.base`
    - Add `st_email()`, `st_slug()`, `st_uuid()` functions to `django_grep/tests/base.py`
    - Each wraps the appropriate `hypothesis.strategies` so website tests never import `hypothesis` directly
    - _Requirements: 13.7_

  - [x] 6.2 Register pytest plugin via `conftest.py`
    - Add or update `conftest.py` at the repo root to include `pytest_plugins = ["django_grep.tests.pytest_plugin"]`
    - Verify both websites can activate the plugin via `pyproject.toml` `[tool.pytest.ini_options] plugins` entry without duplicating fixture definitions
    - _Requirements: 13.9_

  - [ ] 6.3 Write unit tests for new strategy helpers
    - Verify `st_email()`, `st_slug()`, `st_uuid()` each produce valid values under Hypothesis
    - _Requirements: 13.7_

- [ ] 7. Checkpoint - django-grep enhancements pass
  - Run `pytest venv/libs/django-grep/tests/ --hypothesis-seed=0` and ensure zero failures; ask the user if questions arise.

- [x] 8. Rename apps in ctc-research.com
  - [x] 8.1 Rename `handlers` to `accounts` in ctc-research.com
    - Rename directory `ctc-research.com/apps/handlers/` to `ctc-research.com/apps/accounts/`
    - Update `AppConfig` in `apps/accounts/apps.py`: `name = "apps.accounts"`, `label = "accounts"`, `verbose_name = _("Accounts")`
    - Update `INSTALLED_APPS` in all settings files
    - Update all URL includes referencing `handlers`
    - Update all cross-app imports from `apps.handlers` to `apps.accounts`
    - _Requirements: 6.1_

  - [ ] 8.2 Generate migration for `handlers` to `accounts` rename in ctc-research.com
    - Create `apps/accounts/migrations/0001_rename_app_label.py` using `AlterModelTable` for every model to preserve physical table names as `handlers_*`
    - Add data migration to update `ContentType` rows: `ContentType.objects.filter(app_label="handlers").update(app_label="accounts")`
    - _Requirements: 6.6, 6.7, 9.1_

  - [x] 8.3 Rename `LMS` to `lms` in ctc-research.com
    - Rename directory `ctc-research.com/apps/LMS/` to `ctc-research.com/apps/lms/`
    - Update `AppConfig`: `name = "apps.lms"`, `label = "lms"`
    - Update `INSTALLED_APPS`, URL includes, and all cross-app imports
    - _Requirements: 6.3_

  - [ ] 8.4 Generate migration for `LMS` to `lms` rename in ctc-research.com
    - Create migration using `AlterModelTable` for every model; add `ContentType` data migration if label changes
    - _Requirements: 6.6, 6.7, 9.1_

  - [x] 8.5 Rename `pages` to `content` in ctc-research.com
    - Rename directory `ctc-research.com/apps/pages/` to `ctc-research.com/apps/content/`
    - Update `AppConfig`: `name = "apps.content"`, `label = "content"`
    - Update `INSTALLED_APPS`, URL includes, and all cross-app imports
    - _Requirements: 6.5_

  - [ ] 8.6 Generate migration for `pages` to `content` rename in ctc-research.com
    - Create migration using `AlterModelTable` for every model; add `ContentType` data migration
    - _Requirements: 6.6, 6.7, 9.1_

- [x] 9. Rename apps in structa.cloud
  - [x] 9.1 Rename `handlers` to `accounts` in structa.cloud
    - Rename directory `structa.cloud/apps/handlers/` to `structa.cloud/apps/accounts/`
    - Update `AppConfig`, `INSTALLED_APPS`, URL includes, and all cross-app imports
    - _Requirements: 6.2_

  - [ ] 9.2 Generate migration for `handlers` to `accounts` rename in structa.cloud
    - Create migration using `AlterModelTable` for every model; add `ContentType` data migration
    - _Requirements: 6.6, 6.7, 9.1_

  - [x] 9.3 Rename `LMS` to `lms` in structa.cloud (using lowercase instead of 'alliance')
    - Rename directory `structa.cloud/apps/LMS/` to `structa.cloud/apps/lms/`
    - Update `AppConfig`: `name = "apps.lms"`, `label = "lms"`
    - _Requirements: 6.4_

  - [ ] 9.4 Generate migration for `LMS` to `lms` rename in structa.cloud
    - Create migration using `AlterModelTable` for every model; add `ContentType` data migration
    - _Requirements: 6.6, 6.7, 9.1_

  - [x] 9.5 Rename `pages` to `content` in structa.cloud
    - Rename directory `structa.cloud/apps/pages/` to `structa.cloud/apps/content/`
    - Update `AppConfig`, `INSTALLED_APPS`, URL includes, and all cross-app imports
    - _Requirements: 6.5_

  - [ ] 9.6 Generate migration for `pages` to `content` rename in structa.cloud
    - Create migration using `AlterModelTable` for every model; add `ContentType` data migration
    - _Requirements: 6.6, 6.7, 9.1_

- [ ] 10. Restructure sub-module layout in both websites
  - [ ] 10.1 Apply standard sub-module layout to `accounts` in both websites
    - Ensure `accounts/` contains: `admin/`, `filters/`, `forms/`, `managers/`, `middleware/`, `migrations/`, `models/`, `services/`, `snippets/`, `templates/`, `templatetags/`, `views/`, `wagtail_hooks.py`
    - Dissolve any `handlers/`, `processors/`, or `registration/` sub-directories by redistributing their contents into the standard layout
    - Add module-level docstrings to thin subclass files stating the canonical import path in the shared package
    - _Requirements: 7.1, 7.2, 7.3, 7.4_

  - [ ] 10.2 Apply standard sub-module layout to `lms` (ctc) and `alliance` (structa)
    - Same restructure as 10.1 for the LMS/alliance apps in each website
    - _Requirements: 7.1, 7.2, 7.3, 7.4_

  - [ ] 10.3 Apply standard sub-module layout to `content` in both websites
    - Same restructure as 10.1 for the content/pages apps
    - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [-] 11. Update all imports to point to shared packages (no shims)
  - [ ] 11.1 Update imports for django-osoul classes in both websites
    - Grep for all old import paths: `RoleHierarchyManager`, `GroupAccessControl`, `ErrorTrackerMiddleware`, validators from `apps.handlers`
    - Update each to the new canonical path (e.g. `from django_osoul.managers import RoleHierarchyManager`)
    - Verify zero remaining references to old paths with a codebase-wide grep
    - _Requirements: 8.1, 8.3, 8.5_

  - [ ] 11.2 Update imports for django-rseal classes in both websites
    - Grep for all old import paths: `EmailTemplateSelector`, `EmailTemplateRegistry`, `CertificateService`, `PersonService`, `MessageService`, `PrivacyConsentMiddleware`, `FormSubmissionService`
    - Update each to the new canonical path (e.g. `from django_rseal.email import RoleBasedEmailTemplateSelector`)
    - Verify zero remaining references to old paths with a codebase-wide grep
    - _Requirements: 8.1, 8.3, 8.5_

  - [ ] 11.3 Update all `apps.<old_name>` import references after app renames
    - Grep for `apps.handlers`, `apps.LMS`, `apps.pages` across both websites and all migration files
    - Update to `apps.accounts`, `apps.lms`/`apps.alliance`, `apps.content` respectively
    - Check migration files for string references like `"handlers.Person"` and update to `"accounts.Person"`
    - _Requirements: 8.2_

  - [ ] 11.4 Delete original source files after import verification
    - For each moved module, confirm zero grep hits for the old import path, then delete the original file
    - Do not leave any shim or compatibility re-export files
    - _Requirements: 8.4_

- [ ] 12. Checkpoint - migration safety verification
  - Run `python manage.py migrate --fake-initial` and `python manage.py migrate <app> zero` for each renamed app in a test environment; ensure all migrations are reversible; ask the user if questions arise.
  - _Requirements: 9.3_

- [ ] 13. Migrate tests to django-grep in both websites
  - [ ] 13.1 Add missing test utilities to django-grep
    - Identify any test utility used in `ctc-research.com/tests/` or `structa.cloud/tests/` that does not yet exist in `django_grep.tests`
    - Add missing base classes, factories, assertions, fixtures, and mixins to `django-grep` before migrating website tests
    - _Requirements: 13.6_

  - [ ] 13.2 Migrate test base classes in both websites
    - Replace `from django.test import TestCase` with `from django_grep.tests.base import BaseTestCase` in every test file in `ctc-research.com/tests/` and `structa.cloud/tests/`
    - _Requirements: 13.1_

  - [ ] 13.3 Migrate test factories in both websites
    - Replace inline `factory_boy` or manual object creation patterns with `from django_grep.tests.factories import ModelFactory`
    - _Requirements: 13.2_

  - [ ] 13.4 Migrate custom test assertions in both websites
    - Replace custom assertion helpers with `from django_grep.tests.assertions import ...`
    - _Requirements: 13.3_

  - [ ] 13.5 Migrate test fixtures in both websites
    - Replace fixture loading patterns with `from django_grep.tests.fixtures import ...`
    - _Requirements: 13.4_

  - [ ] 13.6 Migrate test mixins in both websites
    - Replace search, filter, and pagination test mixin imports with `from django_grep.tests.mixins import ...`
    - _Requirements: 13.5_

  - [ ] 13.7 Move shared-package tests to package test suites
    - For each website test that covers logic now in `django-osoul` or `django-rseal`, move the test to the shared package's `tests/` directory
    - Replace the website-level test with a thin integration call
    - _Requirements: 13.10_

- [ ] 14. Checkpoint - website tests pass after test migration
  - Run `pytest structa.cloud/tests/ --ds=structa.cloud.configs.settings` and `pytest ctc-research.com/tests/ --ds=ctc-research.com.configs.settings`; ensure zero import errors and zero failures; ask the user if questions arise.
  - _Requirements: 13.8_

- [ ] 15. Write integration tests for extracted services
  - [ ] 15.1 Write integration tests for `CertificateServiceBase`
    - Create `tests/integration/test_certificate_service_integration.py`
    - Verify the service produces the same result when called from ctc-research.com and structa.cloud with equivalent inputs
    - _Requirements: 11.6_

  - [ ]* 15.2 Write integration tests for `PersonServiceBase` and `MessageServiceBase`
    - Create `tests/integration/test_person_service_integration.py` and `test_message_service_integration.py`
    - Verify equivalent results across both websites for representative inputs
    - _Requirements: 11.6_

- [ ] 16. Set up import-linter CI enforcement
  - [x] 16.1 Create `.importlinter` config at repo root
    - Write the `.importlinter` file with contracts: `osoul-no-wagtail`, `rseal-no-websites`, `nawaai-no-django`, `dependency-layers` as specified in the design
    - _Requirements: 10.1, 10.2, 10.3_

  - [ ] 16.2 Add `lint-imports` step to CI pipeline
    - Add `lint-imports --config .importlinter` as a CI step that runs after tests
    - Ensure the step fails with a descriptive error message on any contract violation
    - _Requirements: 10.1, 10.2, 10.3, 10.4_

  - [ ]* 16.3 Verify all import-linter contracts pass
    - Run `lint-imports --config .importlinter` locally and fix any violations before marking complete
    - _Requirements: 10.1, 10.2, 10.3_

- [ ] 17. Checkpoint - full test suite and import-linter pass
  - Run `pytest venv/libs/django-osoul/tests/ venv/libs/django-rseal/tests/ venv/libs/django-grep/tests/ --hypothesis-seed=0` and `lint-imports --config .importlinter`; ensure zero failures; ask the user if questions arise.

- [-] 18. Run structa.cloud tests locally
  - Run `pytest structa.cloud/tests/ --ds=structa.cloud.configs.settings` and fix any failures introduced by the consolidation and restructure
  - _Requirements: 9.5_

- [x] 19. Run structa.cloud in Docker and fix errors
  - [x] 19.1 Build and start the Docker container for structa.cloud
    - Run the Docker build and start commands for structa.cloud; capture any build or startup errors
    - Fix any import errors, missing migrations, or misconfigured settings revealed by the Docker run

  - [x] 19.2 Set root page as home page and English as default language
    - In the running Docker container, use the Wagtail admin or a management command to set the root page as the site's home page
    - Set English as the default language in Wagtail's locale settings

- [ ] 20. Run Selenium tests against the Docker container
  - Run the Selenium test suite against the running Docker container for structa.cloud
  - Fix any test failures caused by app renames, URL changes, or template path changes

- [x] 21. Produce documentation
  - [x] 21.1 Write `MIGRATION_GUIDE.md`
    - List every changed import path in the format `OLD: <old_path> -> NEW: <new_path>` for all moved classes
    - Document the app rename mapping: `handlers -> accounts`, `LMS (ctc) -> lms`, `LMS (structa) -> alliance`, `pages -> content`
    - _Requirements: 12.1, 12.5_

  - [x] 21.2 Write `ARCHITECTURE.md`
    - Include the dependency graph (`stdlib -> nawaai -> django-osoul -> django_rseal -> websites`)
    - Describe each shared package's responsibility and the rules for deciding where new code belongs
    - _Requirements: 10.5, 12.2_

  - [x] 21.3 Update `README.md` files for `django-osoul`, `django-rseal`, and `django-grep`
    - Document all newly added public classes with purpose, parameters, return type, and at least one usage example
    - _Requirements: 12.3, 12.4_

- [ ] 22. Final checkpoint - all tests pass, zero old import references, documentation complete
  - Run the full test suite across all packages and both websites; run `lint-imports`; grep for all old import paths and confirm zero hits; ask the user if questions arise.
  - _Requirements: 8.5, 9.5, 10.4_

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Shared package work (tasks 2-7) must be complete before website work (tasks 8-16)
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation after each major phase
- Property tests validate the 7 universal correctness properties defined in the design
- No deprecation shims - every import is updated in-place and original files deleted after verification
- All migrations must be reversible (`migrate <app> zero`) before merging
