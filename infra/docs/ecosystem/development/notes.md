# Enhancement Opportunities & Library Notes

**Project:** Django Project Reorganization & Email Automation
**Spec:** `.kiro/specs/libs-consolidation`
**Date:** 2026-04-08

---

## Workspace Setup

All four libraries live in `/root/site/libs` as a unified uv workspace.

```bash
# Install all four libraries as editable installs
uv sync --directory /root/site/libs

# Or install individually as editable
uv pip install -e /root/site/libs/django-grep
uv pip install -e /root/site/libs/django-osoul
uv pip install -e /root/site/libs/django-rseal
uv pip install -e /root/site/libs/django-seed
```

Workspace layout:

```
/root/site/libs/
├── pyproject.toml      # uv workspace root
├── django-grep/        # canonical base utilities
├── django-osoul/       # abstract models, managers, validators (depends on django-grep)
├── django-rseal/       # AI integrations, Celery tasks, email models (depends on django-seed)
└── django-seed/        # email automation, orchestration, seeding
```

---

## 1. How to Use These Libraries for a New Site

### 1.1 What to Install

```bash
# From the consolidated workspace
uv sync --directory /root/site/libs

# Or add to a site's pyproject.toml as workspace dependencies
uv add django-grep django-seed django-osoul django-rseal
```

### 1.2 Required Settings

Add to `INSTALLED_APPS` in your site's `settings/base.py`:

```
# See settings/base.py — add these app labels:
# django_grep
# django_grep.pipelines
# django_grep.comp
# django_seed
```

### 1.3 Required Environment Variables

```bash
# .env
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=noreply@example.com
EMAIL_HOST_PASSWORD=secret
REPORT_EMAIL_FROM=noreply@example.com
REPORT_EMAIL_TO=vresume@structa.cloud

# Django Q workers
Q_CLUSTER_NAME=mysite
Q_CLUSTER_WORKERS=4
Q_CLUSTER_TIMEOUT=60
Q_CLUSTER_RETRY=120
Q_CLUSTER_ORM=default

# Logging
LOG_FILE=logs/email.log
LOG_MAX_BYTES=104857600
LOG_BACKUP_COUNT=5

# AI integrations (optional)
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
```

### 1.4 Available Management Commands

| Command | Description |
|---------|-------------|
| `python manage.py invite_user --email user@example.com --role instructor` | Queue an invitation email |
| `python manage.py send_pending_invitations` | Process all pending invitations |
| `python manage.py send_emails` | Send all queued emails (django-rseal) |
| `python manage.py seed` | Seed the database with test data |

### 1.5 Setting Up Email Automation

1. Create `emails.csv` at the project root:

```csv
email,role
user1@example.com,instructor/manager
user2@example.com,content manager
vresume@structa.cloud,supervisor
```

2. Run the periodic task worker:

```bash
python manage.py qcluster
```

3. The system will automatically check `emails.csv` every 2 days, send invitations, prevent duplicates within 7 days, and send weekly summary reports.

---

## 2. Library Overview

### 2.1 django-grep (Tier 1 — Canonical Base Utilities)

**GitHub:** https://github.com/mammhoud/django-grep

Provides:
- `django_grep.utils.text` — `slugify_unique`, `truncate_words`, `strip_html_tags`
- `django_grep.utils.responses` — `success_response`, `error_response`, `created_response`, `forbidden_response`
- `django_grep.utils.datetime_utils` — `format_relative_time`, `format_duration`
- `django_grep.utils.validators` — `validate_email_format`, `validate_email_domain`
- `django_grep.models.mixins` — `TimestampedModel`, `SoftDeleteModel`, `UUIDPrimaryKeyModel`
- `django_grep.views.mixins` — `AjaxResponseMixin`, `MessageMixin`
- `django_grep.management.base` — `BaseCommand` with logging
- `django_grep.templatetags.django_grep_tags` — `format_duration`, `render_widget`

### 2.2 django-osoul (Tier 2 — Abstract Models & Validators)

**GitHub:** https://github.com/mammhoud/django-osoul
**Depends on:** django-grep

Unique modules (not in django-grep):
- `django_osoul.models.base` — `BaseModel`, `TimeStampedModel`, `UUIDModel`
- `django_osoul.models.managers` — `SoftDeleteQuerySet`, `SoftDeleteManager`
- `django_osoul.services.validators` — `validate_phone_number`, `validate_url`, `validate_username`
- `django_osoul.utils.decorators` — `cache_result`, `retry_on_exception`, `log_execution`
- `django_osoul.constants` — timeout, pagination, cache, status, role constants
- `django_osoul.enums` — `StatusEnum`, `RoleEnum`, `PermissionEnum`, `VisibilityEnum`, `PriorityEnum`
- `django_osoul.exceptions` — `ForgeException`, `ValidationError`, `NotFoundError`, `PermissionDeniedError`

### 2.3 django-seed (Tier 1 — Canonical Email Automation)

**GitHub:** https://github.com/mammhoud/django-seed

Provides:
- `django_seed.models` — `EmailLog`, `UserRole`, `UserGroup`
- `django_seed.services.email_service` — `EmailService`, `BulkEmailService`
- `django_seed.services.invitation_service` — `InvitationService` (7-day duplicate prevention)
- `django_seed.services.csv_parser` — `CSVParser`
- `django_seed.services.queue_manager` — `EmailQueueManager`
- `django_seed.services.report_generator` — `ReportGenerator`
- `django_seed.orchestrator` — full workflow orchestration
- `django_seed.tasks` — `send_email_task`, `check_registrations_task`, `generate_weekly_report_task`

### 2.4 django-rseal (Tier 2 — AI & Celery Automation)

**GitHub:** https://github.com/mammhoud/django-rseal
**Depends on:** django-seed

Unique modules (not in django-seed):
- `django_rseal.ai.integrations` — `OpenAIIntegration`, `ClaudeIntegration`, `AIIntegrationRegistry`
- `django_rseal.email.models` — `EmailLog` (rseal variant with token expiry), `EmailTemplate`
- `django_rseal.tasks.celery` — `send_email_task`, `process_queued_emails`, `retry_failed_emails`
- `django_rseal.management.commands.send_emails` — CLI to send queued emails
- `django_rseal.exceptions` — `RelayException`, `EmailSendError`, `WorkflowError`, `AIIntegrationError`

---

## 3. Deduplication Map

Modules removed from django-osoul (use django-grep instead):

| Removed from django-osoul | Use instead |
|---|---|
| `django_osoul.utils.text` | `django_grep.utils.text` |
| `django_osoul.utils.responses` | `django_grep.utils.responses` |
| `django_osoul.utils.datetime_utils` | `django_grep.utils.datetime_utils` |
| `django_osoul.models.mixins` | `django_grep.models.mixins` |

Modules removed from django-rseal (use django-seed instead):

| Removed from django-rseal | Use instead |
|---|---|
| `django_rseal.email.services` | `django_seed.services.email_service` |
| `django_rseal.management.commands.send_invitations_from_csv` | `django_seed.management.commands.send_invitations_from_csv` |
| `django_rseal.workflows.orchestrator` | `django_seed.orchestrator` |

---

## 4. Performance Suggestions

| Suggestion | Effort | Priority |
|------------|--------|----------|
| Database indexes on EmailLog `(recipient, status, timestamp)` | Low | High |
| `select_related` / `values_list` in InvitationService to avoid N+1 | Low | High |
| Redis caching for role lookups (5 min TTL) | Low | Medium |
| Scale `qcluster` to 4+ workers for high volume | Low | Medium |
| Process `emails.csv` in chunks of 100 rows | Low | Medium |

---

## 5. Security Suggestions

| Suggestion | Effort | Priority |
|------------|--------|----------|
| Rate limit invitation sends (max 100/hour) | Low | High |
| Email domain allowlist validation | Low | High |
| Invitation token expiry (`expires_at` field) | Low | High |
| Use `secrets.token_urlsafe(32)` for invitation links | Low | High |
| CSV input sanitization (prevent injection via role field) | Low | Medium |
| Audit log checksum field on `EmailLog` | Medium | Medium |

---

## 6. Maintainability Suggestions

| Suggestion | Effort | Priority |
|------------|--------|----------|
| Test coverage to 90%+ | Low | High |
| CI/CD GitHub Actions for libs | Low | High |
| Consolidate remaining site duplicates (mixins.py, call.py, notification.py) | Medium | High |
| Pre-commit hooks: `ruff`, `mypy`, `pytest` | Low | Medium |
| `CHANGELOG.md` with semantic versioning | Low | Medium |

---

## 7. Remaining Consolidation Roadmap

| # | Item | From | To | Lines | Priority |
|---|------|------|----|-------|----------|
| 1 | `mixins.py` | Both sites | `django_grep.pipelines.site.mixins` | 907 | High |
| 2 | `call.py` | Both sites | `django_grep.CI.models.interaction.call` | 87 | High |
| 3 | `notification.py` | Both sites | `django_grep.CI.models.interaction.notification` | 124 | High |
| 4 | `submission.py` | Both sites | `django_grep.handlers.models.forms.submission` | 121 | Medium |
| 5 | `integrations.py` | Both sites | `django_grep.CI.models.integrations` | 178 | Medium |

---

*See `docs/code-duplication-analysis.md` and `docs/final-cleanup-checklist.md` for detailed migration steps.*
