# Changelog

All notable changes to django-grep are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-04-15

### Added

This release establishes `django_grep` as the unified testing infrastructure and
health check library for the ecosystem. All test helpers are extracted from
`ctc-research.com` and `structa.cloud`. This package must never be imported by
production code.

#### Test Infrastructure (`django_grep.tests`)
- `tests/base.py` — `BaseTestCase` extending `django.test.TestCase` with Hypothesis strategies:
  - `st_email()` — email address strategy
  - `st_slug()` — slug strategy
  - `st_uuid()` — UUID strategy
- `tests/factories/` — unified `factory_boy` factory classes
- `tests/fixtures/` — reusable test fixtures
- `tests/assertions/` — custom assertion helpers
- `tests/mixins/` — reusable test mixin classes
- `tests/pytest_plugin.py` — pytest plugin registered under `[tool.pytest11]`

#### Health Checks (`django_grep.health`)
- `health/views.py` — `HealthCheckView`, `DatabaseHealthView`, `AssetsHealthView`, `MediaHealthView`
- `health/urls.py` — URL patterns for all four endpoints:
  - `GET /health/` → 200
  - `GET /health/database/` → 200 (503 when database unreachable)
  - `GET /health/assets/` → 200
  - `GET /health/media/` → 200

#### Seeder (`django_grep.seeder`)
- `seeder/` — database seeder classes
- `management/commands/backup_db` — database backup management command
- `management/commands/backup_media` — media backup management command
- `management/commands/load_fixtures` — fixture loading management command

### Changed

#### Naming Conventions (Phase 8)
- All module files use `snake_case`
- All classes use `PascalCase`
- All functions and variables use `snake_case`

### Boundary Guarantees
- `scripts/check_boundaries.py` reports zero violations for the `grep-test-only` rule
- No production code in `ctc-research.com` or `structa.cloud` imports from `django_grep`
- This package is a `dev`/`test` dependency only

## [1.x.x] - Prior releases

See git history for changes prior to the 2.0.0 architectural refactoring.
