# Changelog

All notable changes to django-osoul are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-04-15

### Added

This release establishes `django_osoul` as the canonical pure Django/Python foundation
library for the ecosystem. All additions are extractions from `ctc-research.com` and
`structa.cloud` — zero Wagtail, Celery, or project-specific dependencies.

#### Handlers (`django_osoul.handlers`)
- `handlers/base.py` — handler base classes (pure Django, no Wagtail)
- `handlers/core.py` — handler core classes
- `handlers/mixins/fragment.py` — non-Wagtail fragment handler mixins
- `handlers/mixins/page.py` — non-Wagtail page handler mixins
- `handlers/search.py` — Django ORM-based search handler/mixin

#### Managers (`django_osoul.managers`)
- `managers/role_hierarchy.py` — `RoleHierarchyManager`
- `managers/group_access.py` — `GroupAccessControl`
- `managers/user.py` — `UserManager`
- `managers/group.py` — `GroupManager`

#### Mixins (`django_osoul.mixins`)
- `mixins/user.py` — `UserMixin`
- `mixins/group.py` — `GroupMixin`
- `mixins/models.py` — all other pure Django model mixins
- `mixins/views.py` — pure Django view mixins

#### Backends (`django_osoul.backends`)
- `backends/auth.py` — custom authentication backends
- `backends/storage.py` — custom storage backends

#### Adapters (`django_osoul.adapters`)
- `adapters/allauth.py` — allauth adapter
- `adapters/social.py` — social auth adapter

#### Services (`django_osoul.services`)
- `services/user.py` — `UserService`
- `services/group.py` — `GroupService`

#### Middleware (`django_osoul.middlewares`)
- `middlewares/error_tracker.py` — `ErrorTrackerMiddleware`
- Additional pure Django middleware (no Wagtail/Celery dependencies)

#### Filters / Validators (`django_osoul.filters`)
- `filters/validators.py` — `UniqueFieldValidator`, `SlugFieldValidator`, and other pure Django validators

#### Forms (`django_osoul.forms`)
- `forms/base.py` — pure Django base form classes (no Wagtail form widgets)

#### Components (`django_osoul.comp`)
- `comp/widgets.py` — pure Django UI widgets
- `comp/payloads.py` — payload classes

#### Contrib (`django_osoul.contrib`)
- `contrib/enums.py` — enums and choices
- `contrib/context.py` — context utilities
- `contrib/schemas.py` — schema classes
- `contrib/responses.py` — response helpers

#### Models (`django_osoul.models`)
- Foundation models: `Person`, `Certificate`, `Message` (pure Django, no Wagtail inheritance)

### Changed

#### Deduplication (Phase 6.10)
- Audited and deduplicated all modules against `django_rseal` — removed any accidental overlap
- Enforced hard boundary: zero `wagtail`, `celery`, or `django_rseal` imports anywhere in this package

#### Naming Conventions (Phase 8)
- All module files use `snake_case`
- All classes use `PascalCase`
- All functions and variables use `snake_case`

### Boundary Guarantees
- `scripts/check_boundaries.py` reports zero violations for the `osoul-no-wagtail` rule
- Safe to use in any pure Django project without Wagtail installed

## [1.x.x] - Prior releases

See git history for changes prior to the 2.0.0 architectural refactoring.
