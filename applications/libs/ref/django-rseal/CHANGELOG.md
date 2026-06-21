# Changelog

All notable changes to django-rseal are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-04-15

### Added

This release establishes `django_rseal` as the canonical Wagtail + automation layer
for the ecosystem. All additions are extractions from `ctc-research.com` and
`structa.cloud`. Projects consume this package via thin subclasses.

#### Handlers (`django_rseal.handlers`)
- `handlers/mixins/wagtail_page.py` — Wagtail page handler mixins
- `handlers/mixins/wagtail_fragment.py` — Wagtail-specific fragment handlers
- `handlers/search.py` — Wagtail search integration

#### Pipeline Services (`django_rseal.pipelines.services`)
- `pipelines/services/cart.py` — `CartServiceBase` with `add_to_cart`, `remove_from_cart`, `get_cart`, `clear_cart` using cart model injection pattern
- `pipelines/services/person.py` — `PersonServiceBase`
- `pipelines/services/message.py` — `MessageServiceBase`
- `pipelines/services/form_submission.py` — `FormSubmissionServiceBase`

#### Email (`django_rseal.email`)
- `email/selectors.py` — `RoleBasedEmailTemplateSelector`
- `email/registry.py` — `EmailTemplateRegistry`

#### Components (`django_rseal.comp`)
- `comp/blocks.py` — reusable Wagtail `StructBlock`, `StreamBlock`, and other block classes
- `comp/stream_blocks.py` — StreamField block definitions

#### Contrib (`django_rseal.contrib`)
- `contrib/snippets/` — reusable Wagtail snippet classes
- `contrib/wagtail_hooks.py` — reusable Wagtail hook registrations
- `contrib/admin_site/unfold.py` — Unfold admin customizations
- `contrib/admin_site/wagtail.py` — Wagtail admin customizations
- `contrib/privacy/middleware.py` — `PrivacyConsentMiddleware`
- `contrib/cache/utils.py` — cache utility classes and decorators
- `contrib/signals/` — reusable Django signal definitions
- `contrib/debug_tools/` — debug utility classes
- `contrib/email_config/` — email configuration helpers

#### Workflows (`django_rseal.workflows`)
- `workflows/orchestrator.py` — Orchestrator CLI

### Changed

#### Deduplication (Phase 6.10)
- Audited and deduplicated all modules against `django_osoul` — removed any accidental overlap
- Enforced hard boundary: zero project-specific imports anywhere in this package

#### Naming Conventions (Phase 8)
- All module files use `snake_case`
- All classes use `PascalCase`
- All functions and variables use `snake_case`

### Boundary Guarantees
- `scripts/check_boundaries.py` reports zero violations for the `rseal-no-projects` rule
- Projects must only consume this package via thin subclasses, never by modifying it directly

## [1.x.x] - Prior releases

See git history for changes prior to the 2.0.0 architectural refactoring.
