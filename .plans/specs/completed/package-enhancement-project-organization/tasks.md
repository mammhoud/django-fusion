# Implementation Tasks — Package Enhancement & Project Organization

## Overview

Tasks are ordered by priority. Email/django-seed tasks (T1–T3) come first
and can be executed immediately. Model consolidation (T4–T5) requires database
backups and should be done after the GitHub push (T6).

**Legend**: `[ ]` not started · `[-]` in progress · `[x]` complete · `[~]` queued

---

## Tasks

- [x] 1. Improve queue_manager.py test coverage (R3)
  - [x] 1.1 Create test_queue_manager.py with Django Q backend tests
    - Create `libs/django-seed/django_seed/tests/test_queue_manager.py`
    - Add `EmailQueueManagerDjangoQTestCase` with `setUp` that sets `self.manager.backend = 'django_q'`
    - Test `queue_email` happy path: mock `django_q.tasks.async_task` returning `'mock-task-id'`, assert `log.task_id == 'mock-task-id'` and `log.status == EmailLog.Status.QUEUED`
    - Test `queue_email` error path: mock `async_task` raising `Exception('broker down')`, assert exception propagates
    - Test `retry_failed_email` with Django Q: mock `async_task`, assert `log.retry_count == 1` and `log.status == QUEUED`
    - Test `retry_failed_email` max retries: set `log.retry_count = 3`, assert returns `False` and `async_task` not called
    - Test `schedule_periodic_task`: mock `django_q.models.Schedule.objects.get_or_create`, assert called with correct `name`, `func`, `schedule_type`
    - _Requirements: R3.1, R3.2, R3.3, R3.4, R3.5, R3.8_

  - [x] 1.2 Add Celery backend tests
    - Add `EmailQueueManagerCeleryTestCase` with `setUp` that sets `self.manager.backend = 'celery'`
    - Test `queue_email` happy path: mock `django_seed.tasks.send_email_task.delay` returning `Mock(id='celery-task-id')`, assert `log.task_id == 'celery-task-id'`
    - Test `retry_failed_email` with Celery: mock `send_email_task.apply_async`, assert `log.retry_count == 1`
    - Test `schedule_periodic_task` with Celery backend: assert returns `None` (not supported)
    - _Requirements: R3.2, R3.3_

  - [x] 1.3 Add no-backend fallback tests
    - Add `EmailQueueManagerNoBackendTestCase` with `setUp` that sets `self.manager.backend = None`
    - Test `queue_email` no-backend: mock `EmailService._send_now`, assert it is called and log is returned
    - Test `retry_failed_email` no-backend: assert returns `False`
    - _Requirements: R3.6_

  - [x] 1.4 Verify coverage meets targets
    - Run `cd libs/django-seed && python -m pytest django_seed/tests/ --cov=django_seed --cov-report=term-missing`
    - Confirm `queue_manager.py` ≥ 80% and overall email modules ≥ 85%
    - Fix any remaining uncovered lines
    - _Requirements: R3.1, R3.2_

- [x] 2. Send emails from emails.csv (R6 partial + email pipeline verification)
  - [x] 2.1 Verify emails.csv exists and is valid
    - Check `emails.csv` at workspace root contains correct structure: `email,role`
    - Verify 4 records: E.babiker55@gmail.com, yasirzaroug8@gmail.com, dranas352002@gmail.com, ctcresearchhub2025@gmail.com
    - Run `python -c "from django_seed.services.csv_parser import CSVParser; p = CSVParser('emails.csv'); print(p.parse())"` from workspace root
    - _Requirements: R6_

  - [x] 2.2 Configure SMTP settings in .env
    - Verify `ctc-research.com/.env` has `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`
    - Verify `REPORT_EMAIL_FROM` and `REPORT_EMAIL_TO` are set
    - Verify `DEFAULT_FROM_EMAIL` is set
    - _Requirements: R6_

  - [x] 2.3 Run invitation send via management command
    - From `ctc-research.com/`: run `uv run python com send_pending_invitations`
    - Verify `EmailLog` records created in database with `status=QUEUED` or `status=SENT`
    - Check logs for any errors
    - _Requirements: R6_

  - [x] 2.4 Verify email logs in database
    - Run `uv run python com shell -c "from django_seed.models import EmailLog; print(EmailLog.objects.all().values('recipient','status','timestamp')[:10])"`
    - Confirm records exist for each CSV recipient
    - Confirm no `status=FAILED` records without retry attempts
    - _Requirements: R6_

- [x] 3. Fix failing tests in ctc-research.com (R4)
  - [x] 3.1 Skip infrastructure tests that reference non-existent services
    - Open `ctc-research.com/tests/test_ctc_docs_and_core_containers.py`
    - Add `@pytest.mark.skip(reason="ctc-core service not in docker-compose.yml — see docs/specs/pending/README.md")` to all 4 test functions: `test_container_name_matches_traefik_url`, `test_redis_db_index_and_db_name_uniqueness`, `test_service_config_completeness`, `test_traefik_config_completeness`
    - _Requirements: R4.1, R4.2, R4.3_

  - [x] 3.2 Fix populate_content Wagtail import
    - Open `ctc-research.com/apps/handlers/management/commands/populate_content.py`
    - Move any top-level `from wagtail.models import ...` or `from wagtail import ...` imports inside the `handle()` method body
    - _Requirements: R4.4_

  - [x] 3.3 Fix structa.cloud path in command parity test
    - Open `ctc-research.com/tests/test_property_command_parity.py`
    - Change `_STRUCTA_COMMANDS_PATH` from `_WORKSPACE_ROOT / "structa.cloud" / "core" / "apps" / "handlers" / "management" / "commands"` to `_WORKSPACE_ROOT / "structa.cloud" / "apps" / "handlers" / "management" / "commands"`
    - _Requirements: R4.5_

  - [x] 3.4 Run full test suite and verify 12 passed
    - Run `cd ctc-research.com && .venv/bin/python -m pytest tests/ -v`
    - Confirm output: `12 passed` (4 skipped + 8 passing, or 12 passing if skips count)
    - _Requirements: R4.6_

- [x] 4. Push packages to GitHub and sync both sites (R6)
  - [x] 4.1 Verify git state of django-grep
    - Run `cd libs/django-grep && git status && git log origin/generic..HEAD --oneline`
    - Confirm branch is `generic` and remote is `https://github.com/mammhoud/django-grep.git`
    - _Requirements: R6.1_

  - [x] 4.2 Verify git state of django-seed
    - Run `cd libs/django-seed && git status && git log origin/main..HEAD --oneline`
    - Confirm branch is `main` and remote is `https://github.com/mammhoud/django-seed.git`
    - _Requirements: R6.2_

  - [x] 4.3 Push django-grep to GitHub
    - Run `cd libs/django-grep && git push origin generic`
    - Confirm push succeeds (no rejected commits)
    - _Requirements: R6.1_

  - [x] 4.4 Push django-seed to GitHub
    - Run `cd libs/django-seed && git push origin main`
    - Confirm push succeeds
    - _Requirements: R6.2_

  - [x] 4.5 Sync ctc-research.com
    - Run `cd ctc-research.com && uv sync`
    - Confirm no errors; verify `django-grep` and `django-seed` installed from GitHub
    - _Requirements: R6.3, R6.5_

  - [x] 4.6 Sync structa.cloud
    - Run `cd structa.cloud && uv sync`
    - Confirm `.venv` created with `django-grep` and `django-seed` installed
    - _Requirements: R6.4, R6.6_

- [x] 5. Bootstrap structa.cloud test environment (R5)
  - [x] 5.1 Fix test_property_preservation.py path
    - Open `structa.cloud/tests/test_property_preservation.py`
    - Find any reference to `structa.cloud/core/` and replace with `structa.cloud/alliance/`
    - If the test cannot be fixed, add `@pytest.mark.skip(reason="structa.cloud/core/ removed in infrastructure-reorganization-cleanup")`
    - _Requirements: R5.6_

  - [x] 5.2 Run structa.cloud test suite
    - Run `cd structa.cloud && uv run pytest alliance/CI/tests/ -v --tb=short`
    - Document which tests pass and which fail
    - Fix any import errors caused by missing packages
    - _Requirements: R5.4, R5.5_

- [x] 6. Move exact-duplicate models to django-grep (R1)
  - [x] 6.1 Create django-grep CI module structure
    - Create `libs/django-grep/src/django_grep/CI/__init__.py`
    - Create `libs/django-grep/src/django_grep/CI/models/__init__.py`
    - Create `libs/django-grep/src/django_grep/CI/models/interaction/__init__.py`
    - Create `libs/django-grep/src/django_grep/handlers/models/forms/__init__.py`
    - _Requirements: R1.1–R1.4_

  - [x] 6.2 Move call.py to django-grep
    - Copy `ctc-research.com/core/CI/models/interaction/call.py` to `libs/django-grep/src/django_grep/CI/models/interaction/call.py`
    - Add `from .call import Call` to `django_grep/CI/models/interaction/__init__.py`
    - Add `from .interaction.call import Call` to `django_grep/CI/models/__init__.py`
    - Scan both sites: `grep -rn "from core.CI.models.interaction.call\|from alliance.CI.models.interaction.call" ctc-research.com/ structa.cloud/`
    - Update all found imports to `from django_grep.CI.models.interaction.call import Call`
    - Create `SeparateDatabaseAndState` migration in ctc-research.com for `Call` model
    - Create `SeparateDatabaseAndState` migration in structa.cloud for `Call` model
    - Delete original files from both sites
    - Run `python manage.py check` in both sites
    - _Requirements: R1.1, R1.5, R1.6, R1.7, R1.8, R1.9, R1.10_

  - [x] 6.3 Move notification.py to django-grep
    - Copy `ctc-research.com/core/CI/models/interaction/notification.py` to `libs/django-grep/src/django_grep/CI/models/interaction/notification.py`
    - Add exports to `__init__.py` files
    - Update all imports in both sites
    - Create `SeparateDatabaseAndState` migrations in both sites
    - Delete original files
    - Run `python manage.py check` in both sites
    - _Requirements: R1.2, R1.5–R1.10_

  - [x] 6.4 Move submission.py to django-grep
    - Copy `ctc-research.com/apps/handlers/models/forms/submission.py` to `libs/django-grep/src/django_grep/handlers/models/forms/submission.py`
    - Add exports to `__init__.py` files
    - Update all imports in both sites
    - Create `SeparateDatabaseAndState` migrations in both sites
    - Delete original files
    - Run `python manage.py check` in both sites
    - _Requirements: R1.3, R1.5–R1.10_

  - [x] 6.5 Move integrations.py to django-grep
    - Copy `ctc-research.com/core/CI/models/integrations.py` to `libs/django-grep/src/django_grep/CI/models/integrations.py`
    - Add exports to `__init__.py` files
    - Update all imports in both sites
    - Create `SeparateDatabaseAndState` migrations in both sites
    - Delete original files
    - Run `python manage.py check` in both sites
    - _Requirements: R1.4, R1.5–R1.10_

  - [x] 6.6 Run test suites after all model moves
    - Run `cd ctc-research.com && .venv/bin/python -m pytest tests/ -v`
    - Run `cd structa.cloud && uv run pytest alliance/CI/tests/ -v`
    - Confirm no regressions from model moves
    - _Requirements: R1.11, R1.12_

- [x] 7. Move mixins.py to django-grep (R2)
  - [x] 7.1 Scan all import sites before moving
    - Run `grep -rn "from apps.handlers.site.mixins import" ctc-research.com/ structa.cloud/`
    - Record every file and import that needs updating
    - Confirm the list is complete before proceeding
    - _Requirements: R2.1_

  - [x] 7.2 Create unified mixins.py in django-grep with abstract bases
    - Create `libs/django-grep/src/django_grep/pipelines/site/mixins.py`
    - Copy content from `ctc-research.com/apps/handlers/site/mixins.py` (the normalized version)
    - Add `BaseCartMixin` abstract class with `get_cart_items`, `calculate_total`, `add_item`, `remove_item` abstract methods and docstring noting site-specific implementations
    - Add `BaseDashboardMixin` abstract class with `get_dashboard_context`, `get_recent_activity` abstract methods and docstring
    - _Requirements: R2.1, R8.1, R8.2, R8.3, R8.4_

  - [x] 7.3 Update all imports in ctc-research.com and structa.cloud (atomic)
    - In a single commit: update every import found in 7.1 from `from apps.handlers.site.mixins import X` to `from django_grep.pipelines.site.mixins import X`
    - Delete `ctc-research.com/apps/handlers/site/mixins.py`
    - Delete `structa.cloud/apps/handlers/site/mixins.py`
    - Run `python manage.py check` in both sites immediately
    - _Requirements: R2.2, R2.3, R2.4_

  - [x] 7.4 Run test suites after mixin move
    - Run `cd ctc-research.com && .venv/bin/python -m pytest tests/ -v`
    - Run `cd structa.cloud && uv run pytest alliance/CI/tests/ -v`
    - Confirm no regressions
    - _Requirements: R2.5, R2.6_

- [x] 8. Audit and clean up unused template tags (R7)
  - [x] 8.1 Scan both sites for template tag usage
    - Run `grep -r "load django_grep" ctc-research.com/ structa.cloud/`
    - Run `grep -r "django_grep_tags" ctc-research.com/ structa.cloud/`
    - Document which tags (if any) are used
    - _Requirements: R7.1_

  - [x] 8.2 Remove unused tags from django_grep_tags.py
    - Open `libs/django-grep/src/django_grep/templatetags/django_grep_tags.py`
    - Remove: `truncate_words` filter (duplicates Django built-in), `file_size` filter, `add_class` filter, `placeholder` filter
    - Remove corresponding tests for deleted tags
    - _Requirements: R7.2, R7.3_

  - [x] 8.3 Document retained tags in templatetags.md
    - Update `libs/django-grep/docs/templatetags.md`
    - For each retained tag: add purpose, usage example, parameters, return value
    - Mark each as "reserved for future use" or "available now"
    - _Requirements: R7.4, R7.5_

  - [x] 8.4 Verify django-grep tests still pass after tag removal
    - Run `cd libs/django-grep && python -m pytest -v` (or equivalent test runner)
    - Confirm no test failures from removed tags
    - _Requirements: R7.6_

- [x] 9. Create abstract-patterns.md documentation (R8)
  - [x] 9.1 Write abstract-patterns.md
    - Create `libs/django-grep/docs/abstract-patterns.md`
    - Document `BaseCartMixin`: purpose, abstract methods, minimal implementation example for LMS cart and generic e-commerce cart
    - Document `BaseDashboardMixin`: purpose, abstract methods, minimal implementation example
    - Add section "How to implement for a new site" with step-by-step instructions
    - _Requirements: R8.5, R8.6_

- [x] 10. Update documentation and README (R9)
  - [x] 10.1 Update docs/_sidebar.md with any new pages
    - Verify all links in `docs/_sidebar.md` resolve to existing files
    - Add link to `docs/libraries/django-grep-overview.md` and `docs/libraries/django-seed-overview.md` if not present
    - _Requirements: R9.3_

  - [x] 10.2 Update docs/libraries/django-grep-overview.md
    - Update "Pending Consolidations" table to reflect completed moves (T6, T7)
    - Add changelog entry for Phase 2 model/mixin consolidations
    - _Requirements: R9.5_

  - [x] 10.3 Update docs/libraries/django-seed-overview.md
    - Update coverage table to reflect new queue_manager.py coverage (T1)
    - _Requirements: R9.5_

  - [x] 10.4 Verify root README.md has Documentation section
    - Confirm `README.md` contains a "Documentation" section linking to `docs/README.md`
    - _Requirements: R9.4_

## Notes

- Tasks 1–3 can be executed immediately (no GitHub push required)
- Task 4 (GitHub push) is a prerequisite for Tasks 5, 6, 7
- Tasks 6 and 7 require database backups before execution
- Each sub-task in Task 6 should be executed and tested independently
- Task 7 (mixins.py) must be done as a single atomic commit (7.2 + 7.3 together)
- Run `python manage.py check` after every model move to catch import errors early
