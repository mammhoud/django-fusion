# Changelog

All notable changes to structa.cloud are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-04-15

### Changed

#### App Renames (Phase 6)
- Renamed `apps/handlers` → `apps/accounts` with reversible migrations preserving all table names
- Renamed `apps/LMS` → `apps/lms` (AppConfig name: `alliance`) with reversible migrations preserving all table names
- Renamed `apps/pages` → `apps/content` with reversible migrations preserving all table names
- Added data migrations to update `ContentType` records for all renamed apps
- Enforced standard sub-module layout (`admin/`, `filters/`, `forms/`, `managers/`, `middleware/`, `models/`, `services/`, `views/`) in all apps

#### Thin Layer Pattern (Phase 7)
- Converted all project services to thin subclasses of `django_rseal` base classes
- `CartService` now delegates to `django_rseal.pipelines.services.CartServiceBase`
- `PersonService` now delegates to `django_rseal.pipelines.services.PersonServiceBase`
- `MessageService` now delegates to `django_rseal.pipelines.services.MessageServiceBase`
- `FormSubmissionService` now delegates to `django_rseal.pipelines.services.FormSubmissionServiceBase`
- Removed all duplicate managers (now imported from `django_osoul.managers`)
- Removed all duplicate mixins (now imported from `django_osoul.mixins` or `django_rseal`)
- Removed all duplicate form base classes (now imported from `django_osoul.forms`)
- Removed all duplicate middleware (now imported from `django_osoul.middlewares` or `django_rseal.contrib`)
- Unified settings structure with consistent base/environment override pattern

#### Naming Conventions (Phase 8)
- Renamed all CamelCase module files to `snake_case`
- Renamed all non-PascalCase classes to PascalCase
- Renamed all camelCase functions to `snake_case`

### Removed

#### Extracted to django_osoul (Phase 2)
- Removed handler base/core classes (now in `django_osoul.handlers`)
- Removed `RoleHierarchyManager`, `GroupAccessControl` (now in `django_osoul.managers`)
- Removed `UserManager`, `GroupManager` (now in `django_osoul.managers`)
- Removed pure Django model and view mixins (now in `django_osoul.mixins`)
- Removed custom auth and storage backends (now in `django_osoul.backends`)
- Removed allauth and social auth adapters (now in `django_osoul.adapters`)
- Removed `UserService`, `GroupService` (now in `django_osoul.services`)
- Removed `ErrorTrackerMiddleware` and other pure Django middleware (now in `django_osoul.middlewares`)
- Removed pure Django validators (now in `django_osoul.filters.validators`)
- Removed pure Django base form classes (now in `django_osoul.forms`)
- Removed pure Django UI components and payloads (now in `django_osoul.comp`)
- Removed contrib utilities: enums, context, schemas, responses (now in `django_osoul.contrib`)
- Removed foundation models: Person, Certificate, Message (now in `django_osoul.models`)

#### Extracted to django_rseal (Phase 3)
- Removed Wagtail handler mixins and page handlers (now in `django_rseal.handlers`)
- Removed Wagtail blocks and StreamField definitions (now in `django_rseal.comp`)
- Removed Wagtail snippets (now in `django_rseal.contrib.snippets`)
- Removed Wagtail hooks (now in `django_rseal.contrib.wagtail_hooks`)
- Removed Unfold and Wagtail admin customizations (now in `django_rseal.contrib.admin_site`)
- Removed `PrivacyConsentMiddleware` (now in `django_rseal.contrib.privacy`)
- Removed cache utilities (now in `django_rseal.contrib.cache`)
- Removed signal definitions (now in `django_rseal.contrib.signals`)
- Removed debug tools (now in `django_rseal.contrib.debug_tools`)
- Removed email config utilities (now in `django_rseal.contrib.email_config`)
- Removed `RoleBasedEmailTemplateSelector`, `EmailTemplateRegistry` (now in `django_rseal.email`)
- Removed Orchestrator CLI (now in `django_rseal.workflows`)

#### Extracted to django_grep (Phase 4)
- Removed duplicate test infrastructure: `BaseTestCase`, factories, fixtures, assertions, mixins
- Removed health check views and URLs (now served from `django_grep.health`)
- Removed database seeder classes and management commands

### Fixed
- Eliminated all circular dependencies across app boundaries
- Eliminated all cross-domain leakage between `accounts`, `lms` (alliance), and `content` apps
- Updated `AUTHENTICATION_BACKENDS`, `DEFAULT_FILE_STORAGE`, `ACCOUNT_ADAPTER`, `SOCIALACCOUNT_ADAPTER` settings to reference `django_osoul`
- Added `path('health/', include('django_grep.health.urls'))` to URL configuration

## [1.x.x] - Prior releases

See git history for changes prior to the 2.0.0 architectural refactoring.
