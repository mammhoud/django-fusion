# django-osoul — Library Overview

**GitHub**: https://github.com/mammhoud/django-osoul (branch: `generic`)
**Local path**: `libs/django-osoul/`
**Install**: `pip install git+https://github.com/mammhoud/django-osoul.git@generic`

## Purpose

`django-osoul` is the shared Django utility library for ctc-research.com and structa.cloud.
It provides reusable models, views, utilities, template tags, and management command base classes
following a "small code tips" philosophy — practical, composable Django patterns.

## Module Map

| Module | Import Path | Description |
|--------|-------------|-------------|
| Model mixins | `django_osoul.models.mixins` | `TimestampedModel`, `SoftDeleteModel`, `UUIDPrimaryKeyModel` |
| View mixins | `django_osoul.views.mixins` | `AjaxResponseMixin`, `MessageMixin` |
| Text utils | `django_osoul.utils.text` | `slugify_unique`, `truncate_words` |
| Validators | `django_osoul.utils.validators` | `validate_email_format`, `validate_email_domain` |
| Datetime utils | `django_osoul.utils.datetime_utils` | `format_relative_time`, `format_duration` |
| Response helpers | `django_osoul.utils.responses` | `success_response`, `error_response` |
| Template tags | `django_osoul.templatetags.django_osoul_tags` | `format_duration`, `render_widget` |
| Management base | `django_osoul.management.base` | `BaseCommand` with logging |
| Pipelines | `django_osoul.pipelines` | Core models, views, managers, services |
| Components | `django_osoul.comp` | Wagtail blocks, site components |
| Email tools | `django_osoul.email_tools` | Email extraction, CSV management |

## Pending Consolidations

The following files are still duplicated between ctc-research.com and structa.cloud
and should be moved into django-osoul (see `docs/development/final-cleanup-checklist.md`):

| File | Lines | Target in django-osoul | Priority |
|------|-------|-----------------------|----------|
| `apps/handlers/site/mixins.py` | 907 | `django_osoul/pipelines/site/mixins.py` | High |
| `CI/models/interaction/call.py` | 87 | `django_osoul/CI/models/interaction/call.py` | High |
| `CI/models/interaction/notification.py` | 124 | `django_osoul/CI/models/interaction/notification.py` | High |
| `apps/handlers/models/forms/submission.py` | 121 | `django_osoul/handlers/models/forms/submission.py` | Medium |
| `CI/models/integrations.py` | 178 | `django_osoul/CI/models/integrations.py` | Medium |

## Changelog

### Phase 2 (April 2026)
- Added `models/mixins.py` — TimestampedModel, SoftDeleteModel, UUIDPrimaryKeyModel
- Added `views/mixins.py` — AjaxResponseMixin, MessageMixin, ProfileContextMixin
- Added `utils/` — text, validators, datetime_utils, responses
- Added `templatetags/django_osoul_tags.py` — format_duration, render_widget, relative_time, percentage, format_currency, query_string, render_pagination (4 unused tags removed: truncate_words, file_size, add_class, placeholder)
- Added `management/base.py` — BaseCommand with structured logging
- Added `docs/abstract-patterns.md` — BaseCartMixin, BaseDashboardMixin abstract base patterns
- Added `docs/templatetags.md` — full template tag reference
- Added `docs/` — models.md, views.md, utils.md, templatetags.md, management.md, examples.md, abstract-patterns.md
- Pushed to GitHub: branch `generic` ✅

### Phase 1 (April 2026)
- Established as single source of truth at `libs/django-osoul/`
- Removed duplicate copies from ctc-research.com/libs and structa.cloud/libs
- Both sites now reference via `pyproject.toml` git+https URL
