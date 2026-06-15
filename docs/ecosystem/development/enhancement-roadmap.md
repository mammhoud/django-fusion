# Enhancement Roadmap

> Converted from `NOTES.md` — April 2026

## Consolidation Roadmap (Remaining Work)

| # | Item | From | To | Lines | Effort | Priority |
|---|------|------|----|-------|--------|----------|
| 1 | `mixins.py` | Both sites | `django_grep.pipelines.site.mixins` | 907 | Medium | **High** |
| 2 | `call.py` | Both sites | `django_grep.CI.models.interaction.call` | 87 | Low | **High** |
| 3 | `notification.py` | Both sites | `django_grep.CI.models.interaction.notification` | 124 | Low | **High** |
| 4 | `submission.py` | Both sites | `django_grep.handlers.models.forms.submission` | 121 | Low | Medium |
| 5 | `integrations.py` | Both sites | `django_grep.CI.models.integrations` | 178 | Low | Medium |
| 6 | Blog models | Both sites | `django_grep.handlers.models.blog` | ~200 | Medium | Medium |
| 7 | `cart.py` (abstract) | Both sites | `django_grep.CI.models.cart` | ~70 | Low | Low |

**Total remaining**: ~1,687 lines across 7 items.

## Performance Suggestions

| Suggestion | Effort | Priority |
|------------|--------|----------|
| Composite index on `EmailLog(recipient, status, timestamp)` | Low | High |
| `select_related` in InvitationService to avoid N+1 | Low | High |
| Redis caching for `UserRole.get_highest_role()` (5 min TTL) | Low | Medium |
| Batch CSV processing in chunks of 100 | Low | Medium |

## Security Suggestions

| Suggestion | Effort | Priority |
|------------|--------|----------|
| Rate limit invitation sends (max 100/hour) | Low | High |
| Email domain validation against allowlist | Low | High |
| Invitation token expiry (`expires_at` on EmailLog) | Low | High |
| `secrets.token_urlsafe(32)` for invitation links | Low | High |
| CSV input sanitization (prevent injection via role field) | Low | Medium |

## Maintainability Suggestions

| Suggestion | Effort | Priority |
|------------|--------|----------|
| Raise test coverage to 90%+ | Low | High |
| CI/CD GitHub Actions for django-grep and django-seed | Low | High |
| Full type annotations on all service classes | Low | Medium |
| `CHANGELOG.md` with semantic versioning in both libs | Low | Medium |
| Pre-commit hooks: ruff, mypy, pytest | Low | Medium |

## Feature Suggestions

| Suggestion | Effort | Priority |
|------------|--------|----------|
| Unsubscribe mechanism (token-based link in emails) | Medium | High |
| Bounce and complaint handling via SMTP webhook | Medium | Medium |
| Email analytics dashboard in Django admin | Medium | Medium |
| Scheduled email campaigns (future date/time) | Medium | Medium |
| Multi-language email templates (`invitation.ar.html`) | Medium | Low |
| A/B testing for email templates | High | Low |
| Email preference center | High | Low |

## Import Paths After Full Consolidation

```python
# Profile and site mixins (pending)
from django_grep.pipelines.site.mixins import (
    ProfileContextMixin, ProfileOperationsMixin, ProfileDashboardMixin,
    NoteMixin, CertificateMixin, CourseMixin, MessageMixin,
)

# CI models (pending)
from django_grep.CI.models.interaction.call import Call
from django_grep.CI.models.interaction.notification import Notification
from django_grep.CI.models.integrations import Integration
from django_grep.handlers.models.forms.submission import FormSubmission

# Utilities (available now)
from django_grep.utils.validators import validate_email_format
from django_grep.utils.text import slugify_unique, truncate_words
from django_grep.utils.datetime_utils import format_relative_time
from django_grep.utils.responses import success_response, error_response

# Email automation (available now)
from django_seed.models import EmailLog, UserRole, UserGroup
from django_seed.services.invitation_service import InvitationService
from django_seed.services.email_service import EmailService
from django_seed.services.report_generator import ReportGenerator
```
