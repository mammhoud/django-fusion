# django-fusion — Library Overview

**GitHub**: https://github.com/mammhoud/django-fusion (branch: `generic`)
**Local path**: `libs/django-fusion/`
**Install**: `pip install git+https://github.com/mammhoud/django-fusion.git@generic`

## Purpose

`django-fusion` is the shared Django utility library for ctc-research.com and structa.cloud.
It provides reusable models, views, utilities, template tags, and management command base classes
following a "small code tips" philosophy — practical, composable Django patterns.

## Module Map

| Module | Import Path | Description |
|--------|-------------|-------------|
| Model mixins | `django_fusion.models.mixins` | `TimestampedModel`, `SoftDeleteModel`, `UUIDPrimaryKeyModel` |
| View mixins | `django_fusion.views.mixins` | `AjaxResponseMixin`, `MessageMixin` |
| Text utils | `django_fusion.utils.text` | `slugify_unique`, `truncate_words` |
| Validators | `django_fusion.utils.validators` | `validate_email_format`, `validate_email_domain` |
| Datetime utils | `django_fusion.utils.datetime_utils` | `format_relative_time`, `format_duration` |
| Response helpers | `django_fusion.utils.responses` | `success_response`, `error_response` |
| Template tags | `django_fusion.templatetags.django_fusion_tags` | `format_duration`, `render_widget` |
| Management base | `django_fusion.management.base` | `BaseCommand` with logging |
| Pipelines | `django_fusion.pipelines` | Core models, views, managers, services |
| Components | `django_fusion.comp` | Wagtail blocks, site components |
| Email tools | `django_fusion.email_tools` | Email extraction, CSV management |

## Pending Consolidations

The following files are still duplicated between ctc-research.com and structa.cloud
and should be moved into django-fusion (see `docs/development/final-cleanup-checklist.md`):

| File | Lines | Target in django-fusion | Priority |
|------|-------|-------------------------|----------|
| `apps/handlers/site/mixins.py` | 907 | `django_fusion/pipelines/site/mixins.py` | High |
| `CI/models/interaction/call.py` | 87 | `django_fusion/CI/models/interaction/call.py` | High |
| `CI/models/interaction/notification.py` | 124 | `django_fusion/CI/models/interaction/notification.py` | High |
| `apps/handlers/models/forms/submission.py` | 121 | `django_fusion/handlers/models/forms/submission.py` | Medium |
| `CI/models/integrations.py` | 178 | `django_fusion/CI/models/integrations.py` | Medium |

## Changelog

### Phase 2 (April 2026)
- Added `models/mixins.py` — TimestampedModel, SoftDeleteModel, UUIDPrimaryKeyModel
- Added `views/mixins.py` — AjaxResponseMixin, MessageMixin, ProfileContextMixin
- Added `utils/` — text, validators, datetime_utils, responses
- Added `templatetags/django_fusion_tags.py` — format_duration, render_widget, relative_time, percentage, format_currency, query_string, render_pagination (4 unused tags removed: truncate_words, file_size, add_class, placeholder)
- Added `management/base.py` — BaseCommand with structured logging
- Added `docs/abstract-patterns.md` — BaseCartMixin, BaseDashboardMixin abstract base patterns
- Added `docs/templatetags.md` — full template tag reference
- Added `docs/` — models.md, views.md, utils.md, templatetags.md, management.md, examples.md, abstract-patterns.md
- Pushed to GitHub: branch `generic` ✅

### Phase 1 (April 2026)
- Established as single source of truth at `libs/django-fusion/`
- Removed duplicate copies from ctc-research.com/libs and structa.cloud/libs
- Both sites now reference via `pyproject.toml` git+https URL
