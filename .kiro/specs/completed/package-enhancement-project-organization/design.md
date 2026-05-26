# Design Document — Package Enhancement & Project Organization

## Overview

This document describes the technical design for all 9 requirements in the
package enhancement spec. The work is split into two tracks that can proceed
in parallel after the GitHub push (R6):

- **Track A — django-seed** (R3, R6 partial): Improve test coverage for
  `queue_manager.py` by adding isolated unit tests with mocked Django Q/Celery.
- **Track B — django-grep** (R1, R2, R7, R8): Move duplicate models and mixins
  into django-grep using `SeparateDatabaseAndState` migrations.

R4 (test fixes), R5 (structa.cloud env), and R9 (docs) are independent and
can be done at any time.

---

## Architecture

### Current State

```
libs/
├── django-grep/          branch: generic   (362 Python files)
│   └── src/django_grep/
│       ├── pipelines/    ← core models, views, managers
│       ├── comp/         ← Wagtail blocks, site components
│       ├── utils/        ← text, validators, datetime, responses ✅
│       ├── views/        ← AjaxResponseMixin, MessageMixin ✅
│       ├── models/       ← TimestampedModel, SoftDeleteModel ✅
│       └── templatetags/ ← django_grep_tags.py (unused by sites)
│
└── django-seed/          branch: main      (30 Python files)
    └── django_seed/
        ├── models.py           ← EmailLog, UserRole, UserGroup ✅
        ├── tasks.py            ← send_email_task, check_registrations ✅
        ├── services/
        │   ├── csv_parser.py       ✅
        │   ├── email_service.py    ✅
        │   ├── invitation_service.py ✅
        │   ├── queue_manager.py    ← 54% coverage ⚠️
        │   └── report_generator.py ✅
        ├── management/commands/
        │   ├── invite_user.py      ✅
        │   └── send_pending_invitations.py ✅
        └── tests/
            ├── test_models.py      ✅ 25 tests
            ├── test_services.py    ✅ 27 tests
            ├── test_tasks.py       ✅ 16 tests
            └── test_management_commands.py ✅ 16 tests
```

### Target State (after this spec)

```
libs/django-grep/src/django_grep/
├── CI/
│   └── models/
│       ├── interaction/
│       │   ├── call.py          ← moved from both sites (R1)
│       │   └── notification.py  ← moved from both sites (R1)
│       └── integrations.py      ← moved from both sites (R1)
├── handlers/
│   └── models/
│       └── forms/
│           └── submission.py    ← moved from both sites (R1)
└── pipelines/
    └── site/
        └── mixins.py            ← moved from both sites (R2)
            ├── ProfileContextMixin
            ├── ProfileOperationsMixin
            ├── ProfileDashboardMixin
            ├── NoteMixin
            ├── CertificateMixin
            ├── CourseMixin
            ├── MessageMixin
            ├── BaseCartMixin (abstract)    ← new (R8)
            └── BaseDashboardMixin (abstract) ← new (R8)

libs/django-seed/django_seed/tests/
└── test_queue_manager.py        ← new (R3), covers Django Q + Celery paths
```

---

## Component Designs

### Design 1 — queue_manager.py Test Coverage (R3)

**Problem**: `queue_manager.py` has 54% coverage because the Django Q and Celery
backend branches (`_queue_with_django_q`, `_queue_with_celery`, `_retry_with_django_q`,
`_retry_with_celery`, `schedule_periodic_task`) are never exercised in tests.
The test environment has no live Redis or Django Q worker.

**Solution**: Add `test_queue_manager.py` with `unittest.mock.patch` to isolate
all external dependencies. Three test classes cover the three backend states:

```
EmailQueueManagerDjangoQTestCase   — backend='django_q', mocks async_task
EmailQueueManagerCeleryTestCase    — backend='celery', mocks send_email_task.delay
EmailQueueManagerNoBackendTestCase — backend=None, falls back to _send_now
```

**Mock strategy**:

```python
# Patch at the point of import inside the method (deferred import pattern)
@patch('django_q.tasks.async_task', return_value='mock-task-id-123')
def test_queue_with_django_q_happy_path(self, mock_async):
    # Force backend to django_q regardless of environment
    self.manager.backend = 'django_q'
    log = self.manager.queue_email(...)
    mock_async.assert_called_once()
    self.assertEqual(log.task_id, 'mock-task-id-123')
    self.assertEqual(log.status, EmailLog.Status.QUEUED)
```

**Coverage target**: 80%+ for `queue_manager.py`, 85%+ overall for email modules.

**New test file**: `libs/django-seed/django_seed/tests/test_queue_manager.py`

---

### Design 2 — Model Consolidation into django-grep (R1)

**Problem**: 4 model files are byte-for-byte identical in both sites.
Maintaining them in two places means any bug fix or enhancement must be
applied twice.

**Migration strategy**: `SeparateDatabaseAndState`

This Django migration operation tells the ORM "this model has moved to a
different app" without touching the actual database table. The table stays
where it is; only Django's internal model registry is updated.

```python
# ctc-research.com/core/CI/migrations/XXXX_move_call_to_django_grep.py
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [("core_CI", "XXXX_previous")]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],   # no DB changes
            state_operations=[
                migrations.DeleteModel(name="Call"),
            ],
        )
    ]
```

After this migration, Django knows `Call` is no longer owned by `core.CI`
and will look for it in `django_grep.CI.models.interaction.call`.

**Module structure in django-grep**:

```python
# libs/django-grep/src/django_grep/CI/__init__.py  (new)
# libs/django-grep/src/django_grep/CI/models/__init__.py  (new)
# libs/django-grep/src/django_grep/CI/models/interaction/__init__.py  (new)
# libs/django-grep/src/django_grep/CI/models/interaction/call.py  (moved)
# libs/django-grep/src/django_grep/CI/models/interaction/notification.py  (moved)
# libs/django-grep/src/django_grep/CI/models/integrations.py  (moved)
# libs/django-grep/src/django_grep/handlers/models/forms/submission.py  (moved)
```

**Export from `__init__.py`**:

```python
# django_grep/CI/models/__init__.py
from .interaction.call import Call
from .interaction.notification import Notification
from .integrations import Integration

__all__ = ["Call", "Notification", "Integration"]
```

**Import update in both sites**:

```python
# Before
from core.CI.models.interaction.call import Call
# After
from django_grep.CI.models.interaction.call import Call
```

**Execution order** (one model at a time to isolate risk):
1. `call.py` (87 lines, lowest risk)
2. `notification.py` (124 lines)
3. `submission.py` (121 lines)
4. `integrations.py` (178 lines)

---

### Design 3 — mixins.py Consolidation (R2)

**Problem**: `apps/handlers/site/mixins.py` is 907 lines and identical in both
sites. It contains 7 mixin classes used by 20+ views.

**Atomic commit strategy**: The move and all import updates MUST be in a single
commit to avoid a broken intermediate state where the file is deleted but imports
still reference the old path.

**Target location**: `django_grep/pipelines/site/mixins.py`

This location is consistent with the existing `django_grep.pipelines` namespace
where `PageHandler`, `NotificationMixin`, and other site components live.

**Classes being moved**:

| Class | Type | Used by |
|-------|------|---------|
| `ProfileContextMixin` | View mixin | All profile views |
| `ProfileOperationsMixin` | View mixin | ProfileView, ProfileEditView |
| `ProfileDashboardMixin` | View mixin | DashboardView |
| `NoteMixin` | Model mixin | Note-related models |
| `CertificateMixin` | Model mixin | Certificate models |
| `CourseMixin` | Model mixin | Course enrollment models |
| `MessageMixin` | Model mixin | Message counter models |

**Import scan before move**:
```bash
grep -rn "from apps.handlers.site.mixins import" ctc-research.com/ structa.cloud/
# Must update every match in the same commit
```

**New abstract base classes** (R8, added to same file):

```python
from abc import abstractmethod

class BaseCartMixin:
    """
    Abstract base for site-specific cart implementations.

    ctc-research.com: LMS course cart (CourseCartItem model)
    structa.cloud: Generic e-commerce cart (Product model)

    Subclass and implement all abstract methods for your site.
    """
    @abstractmethod
    def get_cart_items(self, request): ...

    @abstractmethod
    def calculate_total(self, items): ...

    @abstractmethod
    def add_item(self, request, item_id): ...

    @abstractmethod
    def remove_item(self, request, item_id): ...


class BaseDashboardMixin:
    """
    Abstract base for site-specific dashboard implementations.

    ctc-research.com: LMS analytics (enrollment stats, learning streaks)
    structa.cloud: Generic workspace dashboard

    Subclass and implement get_dashboard_context() for your site.
    """
    @abstractmethod
    def get_dashboard_context(self, request): ...

    @abstractmethod
    def get_recent_activity(self, user): ...
```

---

### Design 4 — Fix Failing Tests (R4)

**Three independent fixes**:

#### Fix A — `test_ctc_docs_and_core_containers.py`

The test was written for a planned `ctc-core` service that was never added to
`ctc-research.com/docker-compose.yml`. The actual services are `website`,
`website-media`, `website-worker`.

**Decision**: Skip the 4 failing tests with a documented reason rather than
rewriting them for a service that doesn't exist yet. This is the lowest-risk
approach.

```python
@pytest.mark.skip(reason=(
    "ctc-core service not yet in ctc-research.com/docker-compose.yml. "
    "Re-enable when ctc-core is added. See docs/specs/pending/README.md"
))
def test_container_name_matches_traefik_url(_): ...
```

#### Fix B — `test_property_command_exit_codes.py`

The `populate_content` command imports Wagtail models at module level, which
fails when the test patches the module before Django's app registry is ready.

**Fix**: Defer the Wagtail import inside `handle()`:

```python
# apps/handlers/management/commands/populate_content.py
class Command(BaseCommand):
    def handle(self, *args, **options):
        from wagtail.models import Page  # deferred — was at top of file
        ...
```

#### Fix C — `test_property_command_parity.py`

Wrong path: `structa.cloud/core/apps/...` → correct: `structa.cloud/apps/...`

```python
_STRUCTA_COMMANDS_PATH = (
    _WORKSPACE_ROOT / "structa.cloud" / "apps" / "handlers" / "management" / "commands"
)
```

---

### Design 5 — structa.cloud Bootstrap (R5)

**Steps**:
1. Ensure GitHub push (R6) is done first so packages are available
2. `cd structa.cloud && uv sync`
3. Fix `test_property_preservation.py` path reference
4. Run `uv run pytest alliance/CI/tests/ -v`

**`test_property_preservation.py` fix**:

The test references `structa.cloud/core/` which was removed in the
infrastructure reorganization. Update to reference `structa.cloud/alliance/`:

```python
# Before
CORE_DIR = WORKSPACE_ROOT / "structa.cloud" / "core"
# After
CORE_DIR = WORKSPACE_ROOT / "structa.cloud" / "alliance"
```

---

### Design 6 — Template Tag Audit (R7)

**Audit approach**: Scan both sites for `{% load django_grep_tags %}`.

```bash
grep -r "load django_grep" ctc-research.com/ structa.cloud/
```

Based on the usage analysis, neither site uses any template tags from django-grep.
All tags in `django_grep_tags.py` were added in Phase 2 but never integrated.

**Decision matrix**:

| Tag | Keep/Remove | Reason |
|-----|-------------|--------|
| `format_duration` | Keep + document | Useful for LMS lesson duration display |
| `render_widget` | Keep + document | Useful for component rendering |
| `relative_time` | Keep + document | Useful for activity feeds |
| `truncate_words` | Remove | Duplicates Django's built-in `truncatewords` |
| `percentage` | Keep + document | Useful for progress bars |
| `format_currency` | Keep + document | Useful for LMS pricing |
| `file_size` | Remove | Rarely needed, easy to inline |
| `query_string` | Keep + document | Useful for pagination |
| `render_pagination` | Keep + document | Useful for list views |
| `add_class` | Remove | Duplicates `django-widget-tweaks` |
| `placeholder` | Remove | Duplicates `django-widget-tweaks` |

Tags to remove: `truncate_words`, `file_size`, `add_class`, `placeholder`
Tags to keep and document: all others

---

### Design 7 — GitHub Push (R6)

**Pre-push checklist**:
```bash
# Verify branch names
cd libs/django-grep && git branch   # should show: generic
cd libs/django-seed && git branch   # should show: main

# Verify remotes
cd libs/django-grep && git remote -v
# origin  https://github.com/mammhoud/django-grep.git (fetch/push)

# Check what will be pushed
cd libs/django-grep && git log origin/generic..HEAD --oneline
cd libs/django-seed && git log origin/main..HEAD --oneline
```

**Push commands**:
```bash
cd libs/django-grep && git push origin generic
cd libs/django-seed && git push origin main
```

**Post-push sync**:
```bash
cd ctc-research.com && uv sync
cd structa.cloud && uv sync
```

---

## Data Flow — Email Automation (django-seed)

```
emails.csv
    │
    ▼
CSVParser.parse()
    │ List[EmailRecord]
    ▼
InvitationService.send_invitations_from_csv()
    │
    ├── _filter_unregistered()   ← DB query: User.objects.filter(email__in=...)
    ├── _filter_recently_invited() ← DB query: EmailLog.objects.filter(...)
    │
    ▼ for each unregistered, non-recently-invited record:
EmailService.send_invitation(queue=True)
    │
    ▼
EmailQueueManager.queue_email()
    │
    ├── EmailLog.objects.create(status=QUEUED)
    │
    ├── backend='django_q' → async_task('django_seed.tasks.send_email_task', ...)
    ├── backend='celery'   → send_email_task.delay(...)
    └── backend=None       → EmailService._send_now() (synchronous fallback)
    │
    ▼ (async, in worker process)
send_email_task(log_id, recipient, subject, template_name, context)
    │
    ├── EmailLog.status = SENDING
    ├── EmailService._send_now() → render template → send SMTP
    ├── Success: EmailLog.mark_sent()
    └── Failure: EmailQueueManager.retry_failed_email()
                    │
                    ├── retry_count < 3: re-queue with delay [60, 300, 900]s
                    └── retry_count >= 3: ReportGenerator.send_alert()
    │
    ▼ (periodic, every 2 days)
check_registrations_task()
    └── InvitationService.send_invitations_from_csv()
    └── ReportGenerator.send_batch_report()

    ▼ (periodic, weekly)
generate_weekly_report_task()
    └── ReportGenerator.send_weekly_report()
        └── EmailLog stats + CSV attachment → REPORT_EMAIL_TO
```

---

## Test Architecture — queue_manager.py (R3)

### New file: `libs/django-seed/django_seed/tests/test_queue_manager.py`

```
EmailQueueManagerDjangoQTestCase
├── test_queue_email_django_q_happy_path
│     mock: async_task → 'mock-task-id'
│     assert: log.task_id == 'mock-task-id', log.status == QUEUED
│
├── test_queue_email_django_q_async_task_raises
│     mock: async_task → raises Exception('broker down')
│     assert: exception propagates, log.status unchanged
│
├── test_retry_failed_email_django_q
│     mock: async_task → 'retry-task-id'
│     assert: log.retry_count == 1, log.status == QUEUED
│
├── test_retry_max_retries_django_q
│     setup: log.retry_count = 3
│     assert: returns False, async_task not called
│
└── test_schedule_periodic_task_django_q
      mock: Schedule.objects.get_or_create → (mock_schedule, True)
      assert: get_or_create called with correct name/func/schedule_type

EmailQueueManagerCeleryTestCase
├── test_queue_email_celery_happy_path
│     mock: send_email_task.delay → Mock(id='celery-task-id')
│     assert: log.task_id == 'celery-task-id'
│
├── test_retry_failed_email_celery
│     mock: send_email_task.apply_async → Mock(id='retry-id')
│     assert: log.retry_count == 1, log.status == QUEUED
│
└── test_schedule_periodic_task_celery_not_supported
      setup: backend='celery'
      assert: returns None (only Django Q supports scheduling)

EmailQueueManagerNoBackendTestCase
├── test_queue_email_no_backend_sends_immediately
│     mock: EmailService._send_now
│     assert: _send_now called, log returned
│
└── test_retry_no_backend_returns_false
      setup: backend=None
      assert: returns False
```

---

## File Change Summary

### django-seed changes (R3)

| File | Change |
|------|--------|
| `django_seed/tests/test_queue_manager.py` | **New** — 15+ tests for queue_manager.py |

### django-grep changes (R1, R2, R7, R8)

| File | Change |
|------|--------|
| `src/django_grep/CI/__init__.py` | **New** |
| `src/django_grep/CI/models/__init__.py` | **New** |
| `src/django_grep/CI/models/interaction/__init__.py` | **New** |
| `src/django_grep/CI/models/interaction/call.py` | **New** (moved from sites) |
| `src/django_grep/CI/models/interaction/notification.py` | **New** (moved from sites) |
| `src/django_grep/CI/models/integrations.py` | **New** (moved from sites) |
| `src/django_grep/handlers/models/forms/__init__.py` | **New** |
| `src/django_grep/handlers/models/forms/submission.py` | **New** (moved from sites) |
| `src/django_grep/pipelines/site/mixins.py` | **New** (moved from sites + abstract bases) |
| `src/django_grep/templatetags/django_grep_tags.py` | **Modified** — remove 4 unused tags |
| `docs/abstract-patterns.md` | **New** |
| `docs/templatetags.md` | **Modified** — document kept tags |

### ctc-research.com changes (R1, R2, R4)

| File | Change |
|------|--------|
| `core/CI/models/interaction/call.py` | **Deleted** |
| `core/CI/models/interaction/notification.py` | **Deleted** |
| `core/CI/models/integrations.py` | **Deleted** |
| `apps/handlers/models/forms/submission.py` | **Deleted** |
| `apps/handlers/site/mixins.py` | **Deleted** |
| `core/CI/migrations/XXXX_move_call_to_django_grep.py` | **New** |
| `core/CI/migrations/XXXX_move_notification_to_django_grep.py` | **New** |
| `core/CI/migrations/XXXX_move_integrations_to_django_grep.py` | **New** |
| `apps/handlers/migrations/XXXX_move_submission_to_django_grep.py` | **New** |
| All files importing from deleted paths | **Modified** — update imports |
| `apps/handlers/management/commands/populate_content.py` | **Modified** — defer Wagtail import |
| `tests/test_ctc_docs_and_core_containers.py` | **Modified** — skip 4 tests |
| `tests/test_property_command_parity.py` | **Modified** — fix structa.cloud path |

### structa.cloud changes (R1, R2, R5)

| File | Change |
|------|--------|
| `alliance/CI/models/interaction/call.py` | **Deleted** |
| `alliance/CI/models/interaction/notification.py` | **Deleted** |
| `alliance/CI/models/integrations.py` | **Deleted** |
| `apps/handlers/models/forms/submission.py` | **Deleted** |
| `apps/handlers/site/mixins.py` | **Deleted** |
| `alliance/CI/migrations/XXXX_move_*.py` | **New** (4 migrations) |
| All files importing from deleted paths | **Modified** |
| `tests/test_property_preservation.py` | **Modified** — fix core/ path |

---

## Correctness Properties

### Property 1 — Email queue idempotence
For any `(recipient, subject, template)` tuple, calling `queue_email()` twice
creates two distinct `EmailLog` records (no deduplication at queue level).
Deduplication is handled by `InvitationService._filter_recently_invited()`.

### Property 2 — Retry backoff monotonicity
For retry counts 0, 1, 2: `RETRY_DELAYS[0] < RETRY_DELAYS[1] < RETRY_DELAYS[2]`
(60 < 300 < 900). This is a constant invariant, not a runtime property.

### Property 3 — Import path equivalence after model move
After moving `Call` to django-grep:
`from django_grep.CI.models.interaction.call import Call` and
`from django_grep.CI.models import Call` both resolve to the same class.

### Property 4 — Migration state consistency
After applying `SeparateDatabaseAndState` migrations, `python manage.py migrate --check`
exits 0 and `python manage.py check` exits 0 in both sites.
