# Requirements Document — Package Enhancement & Project Organization

## Introduction

This spec covers the next phase of the Django project consolidation effort.
The prior phase established GitHub-hosted `django-grep` (branch `generic`) and
`django-seed` (branch `main`) as canonical shared libraries, removed all local
lib copies from both sites, and verified all imports reference the package
namespace correctly.

**This phase addresses all remaining unhandled tasks** identified by gap analysis
across the codebase, test reports, and cleanup checklists.

### Scope Summary

| Area | Remaining Work |
|------|---------------|
| R1 — Model consolidation | 4 exact-duplicate model files to move into django-grep |
| R2 — Mixin consolidation | 907-line `mixins.py` identical in both sites |
| R3 — Test coverage | `queue_manager.py` at 54% (target 80%+) |
| R4 — Test fixes | 6 failing tests in ctc-research.com |
| R5 — structa.cloud env | No `.venv`, tests cannot run |
| R6 — GitHub push | Packages not yet pushed; `uv sync` not run |
| R7 — Template tag audit | Unused tags in django-grep |
| R8 — Abstract patterns | `BaseCartMixin`, `BaseDashboardMixin` undocumented |
| R9 — Documentation | Sidebar, README, library changelogs |

---

## Glossary

- **django-grep**: Shared Django utility library at `libs/django-grep/`, GitHub branch `generic`.
- **django-seed**: Shared seeding + email automation library at `libs/django-seed/`, GitHub branch `main`.
- **ctc-research.com**: LMS-focused Django/Wagtail site at `ctc-research.com/`.
- **structa.cloud**: Workspace/team management Django/Wagtail site at `structa.cloud/`.
- **Duplicate_Model**: A Python model file byte-for-byte identical in both sites with no site-specific logic.
- **SeparateDatabaseAndState**: Django migration operation that updates ORM state without touching the DB table.
- **queue_manager**: `libs/django-seed/django_seed/services/queue_manager.py` — 54% coverage, wraps Django Q.
- **uv**: Python package manager used by both sites (`uv sync` installs from `pyproject.toml`).
- **Template_Tag**: A Django template tag in `django-grep/templatetags/django_grep_tags.py`.
- **Abstract_Base_Pattern**: An abstract mixin in django-grep defining a contract for site-specific subclasses.

---

## Dependencies & Prerequisites

Before starting implementation:

1. **Python 3.11+** installed (`python --version`)
2. **uv** installed (`uv --version` or `pip install uv`)
3. **Git** with write access to both GitHub repos:
   - `https://github.com/mammhoud/django-grep` (branch `generic`)
   - `https://github.com/mammhoud/django-seed` (branch `main`)
4. **PostgreSQL** running (for migration tests)
5. **Redis** running (for Django Q tests)
6. **Database backups** taken before any migration work (R1, R2)

---

## Requirements

### R1 — Move Exact-Duplicate Models to django-grep

**User Story:** As a developer, I want the 4 exact-duplicate model files consolidated
into `django-grep` so both sites share a single source of truth.

**Files to move** (all byte-for-byte identical between sites):

| Source (both sites) | Target in django-grep | Lines |
|--------------------|-----------------------|-------|
| `core/CI/models/interaction/call.py` | `django_grep/CI/models/interaction/call.py` | 87 |
| `core/CI/models/interaction/notification.py` | `django_grep/CI/models/interaction/notification.py` | 124 |
| `apps/handlers/models/forms/submission.py` | `django_grep/handlers/models/forms/submission.py` | 121 |
| `core/CI/models/integrations.py` | `django_grep/CI/models/integrations.py` | 178 |

#### Acceptance Criteria

**R1.1** THE django-grep package SHALL contain `django_grep/CI/models/interaction/call.py`
with the `Call` model moved from both sites.

**R1.2** THE django-grep package SHALL contain `django_grep/CI/models/interaction/notification.py`
with the `Notification` model moved from both sites.

**R1.3** THE django-grep package SHALL contain `django_grep/handlers/models/forms/submission.py`
with the `FormSubmission` model moved from both sites.

**R1.4** THE django-grep package SHALL contain `django_grep/CI/models/integrations.py`
with the `Integrations` model moved from both sites.

**R1.5** WHEN a Duplicate_Model is moved, THE django-grep package SHALL export it from
an `__init__.py` so downstream imports resolve without path changes beyond the package prefix.

**R1.6** WHEN a Duplicate_Model is moved, THE ctc-research.com site SHALL update all
import statements to reference `django_grep.*`.

**R1.7** WHEN a Duplicate_Model is moved, THE structa.cloud site SHALL update all
import statements to reference `django_grep.*`.

**R1.8** WHEN a Duplicate_Model defines a DB table, THE ctc-research.com site SHALL
include a migration using `SeparateDatabaseAndState` generated as follows:
```bash
python manage.py makemigrations core --empty --name="move_<model>_to_django_grep"
# Then edit to use migrations.SeparateDatabaseAndState(
#     database_operations=[],
#     state_operations=[migrations.DeleteModel(name='<Model>')]
# )
```

**R1.9** WHEN a Duplicate_Model defines a DB table, THE structa.cloud site SHALL
include the same `SeparateDatabaseAndState` migration pattern.

**R1.10** AFTER moving all 4 models, THE original files SHALL be deleted from both sites.

**R1.11** WHEN consolidation is complete, THE ctc-research.com test suite SHALL pass
all tests that were passing before (currently 6/12).

**R1.12** WHEN consolidation is complete, THE structa.cloud test suite SHALL pass
all tests that were passing before.

#### Success Metric
`grep -r "from core.CI.models" ctc-research.com/` returns 0 matches.
`grep -r "from alliance.CI.models" structa.cloud/` returns 0 matches.

---

### R2 — Move mixins.py to django-grep

**User Story:** As a developer, I want the 907-line `apps/handlers/site/mixins.py`
(functionally identical in both sites) moved into django-grep.

> **Critical**: This must be done as a **single atomic commit** — move the file
> AND update all imports in the same PR to avoid a broken intermediate state.
> 20+ views in each site inherit from these mixins.

#### Acceptance Criteria

**R2.1** THE django-grep package SHALL contain `django_grep/pipelines/site/mixins.py`
with the unified mixin code.

**R2.2** WHEN mixins.py is moved, THE ctc-research.com site SHALL update all
`from apps.handlers.site.mixins import X` to `from django_grep.pipelines.site.mixins import X`
in the same commit.

**R2.3** WHEN mixins.py is moved, THE structa.cloud site SHALL update all
`from apps.handlers.site.mixins import X` to `from django_grep.pipelines.site.mixins import X`
in the same commit.

**R2.4** AFTER the move, THE original `apps/handlers/site/mixins.py` SHALL be deleted
from both sites.

**R2.5** WHEN consolidation is complete, THE ctc-research.com test suite SHALL pass
all previously passing tests.

**R2.6** WHEN consolidation is complete, THE structa.cloud test suite SHALL pass
all previously passing tests.

**R2.7** IF any mixin class requires a site-specific override, THEN THE site SHALL
define a subclass extending the django-grep base class rather than modifying the shared file.

#### Success Metric
`grep -r "from apps.handlers.site.mixins" ctc-research.com/ structa.cloud/` returns 0 matches.

---

### R3 — Improve django-seed queue_manager Test Coverage

**User Story:** As a developer, I want `queue_manager.py` coverage raised to 80%+
so the overall django-seed email automation module meets the 85% target.

**Current state**: `services/queue_manager.py` is at 54% coverage.
The uncovered paths are the Django Q and Celery backend branches
(`_queue_with_django_q`, `_queue_with_celery`, `_retry_with_django_q`,
`_retry_with_celery`, `schedule_periodic_task`).

#### Acceptance Criteria

**R3.1** THE django-seed test suite SHALL achieve ≥85% coverage across all email
automation modules (`management/commands/`, `models.py`, `services/`, `tasks.py`).

**R3.2** THE django-seed test suite SHALL achieve ≥80% coverage for `services/queue_manager.py`.

**R3.3** WHEN testing Django Q code paths, THE test suite SHALL mock `django_q.tasks.async_task`
so tests run without a live Redis or Django Q worker:
```python
@patch("django_seed.services.queue_manager.async_task", return_value="mock-task-id")
def test_queue_with_django_q(self, mock_async):
    ...
```

**R3.4** THE queue_manager tests SHALL cover the happy path: `backend='django_q'`,
`async_task` called with correct args, `EmailLog.task_id` set to returned task ID.

**R3.5** THE queue_manager tests SHALL cover the error path: `async_task` raises
`Exception`, `EmailLog` status remains `QUEUED`, exception propagates.

**R3.6** THE queue_manager tests SHALL cover the no-backend fallback path:
`backend=None`, email sent synchronously via `EmailService._send_now()`.

**R3.7** THE queue_manager tests SHALL cover `retry_failed_email` with Django Q backend:
`_retry_with_django_q` called, `log.retry_count` incremented, `log.status` set to `QUEUED`.

**R3.8** THE queue_manager tests SHALL cover `schedule_periodic_task`:
`Schedule.objects.get_or_create` called with correct `name`, `func`, `schedule_type`.

**R3.9** WHEN new tests are added, THE existing 59 passing tests SHALL continue to pass.

#### Success Metric
```bash
cd libs/django-seed
python -m pytest django_seed/tests/ --cov=django_seed/services/queue_manager --cov-report=term
# Coverage: queue_manager.py ≥80%
```

---

### R4 — Fix Failing Tests in ctc-research.com

**User Story:** As a developer, I want all 12 tests in ctc-research.com to pass.

**Current state**: 6 pass, 6 fail. Failures are path mismatches and import errors,
not logic bugs.

#### Acceptance Criteria

**R4.1** THE `test_ctc_docs_and_core_containers.py` file SHALL fix the path:
```python
# Before (wrong):
COMPOSE_FILE = WORKSPACE_ROOT / "ctc-research" / "docker-compose.yml"
# After (correct):
COMPOSE_FILE = WORKSPACE_ROOT / "ctc-research.com" / "docker-compose.yml"
```
**Expected error resolved**: `FileNotFoundError: /root/site/ctc-research/docker-compose.yml`

**R4.2** THE `test_ctc_docs_and_core_containers.py` file SHALL reference an existing
Traefik config file. The file `ctc-core.yml` does not exist. Available files in
`compose/traefik/dynamic/` are: `adminer.yml`, `blinko.yml`, `catchall.yml`,
`docs.yml`, `lms.yml`, `middlewares.yml`, `services.yml`, `traefik-dashboard.yml`.
The test SHALL be updated to reference `lms.yml` (which routes the ctc-research.com
Django service) or the test SHALL be marked `pytest.mark.skip` with a documented reason.

**R4.3** THE `test_ctc_docs_and_core_containers.py` file SHALL use the correct
Docker service names from `ctc-research.com/docker-compose.yml`:
- Correct service names: `website`, `website-media`, `website-worker`
- Wrong names used in test: `ctc-core`, `ctc-nginx`, `ctc-django-main`

**R4.4** WHEN `test_property_command_exit_codes.py` patches `populate_content`,
THE `populate_content` command SHALL defer Wagtail imports to inside `handle()`:
```python
# Before (causes ImportError at patch time):
from wagtail.models import Page  # top-level import

# After (deferred):
def handle(self, *args, **options):
    from wagtail.models import Page  # deferred import
```
**Expected error resolved**: `AttributeError: module 'apps.handlers.management.commands' has no attribute 'populate_content'`

**R4.5** THE `test_property_command_parity.py` file SHALL fix the structa.cloud path:
```python
# Before (wrong):
_STRUCTA_COMMANDS_PATH = _WORKSPACE_ROOT / "structa.cloud" / "core" / "apps" / "handlers" / "management" / "commands"
# After (correct):
_STRUCTA_COMMANDS_PATH = _WORKSPACE_ROOT / "structa.cloud" / "apps" / "handlers" / "management" / "commands"
```
**Expected error resolved**: `FileNotFoundError: .../structa.cloud/core/apps/handlers/management/commands/validate_config.py`

**R4.6** AFTER all fixes, THE ctc-research.com test suite SHALL report 12 passed, 0 failed:
```bash
cd ctc-research.com
.venv/bin/python -m pytest tests/ -v
# Expected: 12 passed
```

#### Success Metric
`pytest tests/ -v` in `ctc-research.com/` exits with code 0, 12 passed.

---

### R5 — Bootstrap structa.cloud Test Environment

**User Story:** As a developer, I want structa.cloud to have a working venv
so its test suite can be executed.

**Current state**: No `.venv` directory. `django_grep` not installed.
All 9 tests in `structa.cloud/tests/` and `alliance/CI/tests/` fail with
`ModuleNotFoundError: No module named 'django_grep'`.

#### Acceptance Criteria

**R5.1** THE structa.cloud project SHALL have a `.venv` created by:
```bash
cd structa.cloud
uv sync
```

**R5.2** WHEN `uv sync` completes, THE `.venv` SHALL contain `django-grep`
from `https://github.com/mammhoud/django-grep.git` at branch `generic`.

**R5.3** WHEN `uv sync` completes, THE `.venv` SHALL contain `django-seed`
from `https://github.com/mammhoud/django-seed.git` at branch `main`.

**R5.4** AFTER `uv sync`, THE test suite SHALL be executable:
```bash
cd structa.cloud
uv run pytest alliance/CI/tests/ -v
```

**R5.5** WHEN the test suite runs, THE tests that do not depend on missing
infrastructure SHALL pass (at minimum: `test_property_security_headers.py`,
`test_property_health_check.py`).

**R5.6** IF `test_property_preservation.py` references `structa.cloud/core/`
(which no longer exists after the infrastructure reorganization), THEN THE test
SHALL be updated to reference the correct path or marked `pytest.mark.skip`
with reason: `"structa.cloud/core/ removed in infrastructure-reorganization-cleanup"`.

#### Success Metric
```bash
cd structa.cloud && uv run pytest alliance/CI/tests/ -v --tb=short
# At least test_property_security_headers.py and test_property_health_check.py pass
```

---

### R6 — GitHub Push and Package Sync

**User Story:** As a developer, I want both packages pushed to GitHub and both
sites synced so the latest consolidated code is the installed version.

**Current state**: Both packages have local commits not yet pushed.
Neither site has run `uv sync` since the GitHub URL was set.

#### Acceptance Criteria

**R6.1** THE `libs/django-grep` repository SHALL be pushed to
`https://github.com/mammhoud/django-grep.git` on branch `generic`:
```bash
cd libs/django-grep && git push origin generic
```

**R6.2** THE `libs/django-seed` repository SHALL be pushed to
`https://github.com/mammhoud/django-seed.git` on branch `main`:
```bash
cd libs/django-seed && git push origin main
```

**R6.3** AFTER the push, THE ctc-research.com site SHALL sync:
```bash
cd ctc-research.com && uv sync
```

**R6.4** AFTER the push, THE structa.cloud site SHALL sync:
```bash
cd structa.cloud && uv sync
```

**R6.5** WHEN `uv sync` completes in ctc-research.com, THE installed `django-grep`
version SHALL match the latest commit on the `generic` branch.

**R6.6** WHEN `uv sync` completes in structa.cloud, THE installed `django-grep`
version SHALL match the latest commit on the `generic` branch.

**R6.7** AFTER syncing, THE ctc-research.com test suite SHALL pass all previously
passing tests (currently 6/12 — or 12/12 after R4 is applied).

**R6.8** AFTER syncing, THE structa.cloud test suite SHALL pass all previously
passing tests.

#### Success Metric
```bash
cd ctc-research.com
uv run python -c "import django_grep; print(django_grep.__version__)"
# Prints version matching latest generic branch commit
```

---

### R7 — Remove Unused Template Tags from django-grep

**User Story:** As a developer, I want unused template tags removed so
django-grep does not carry dead code.

**Current state**: `templatetags/django_grep_tags.py` was added in Phase 2
with `format_duration`, `render_widget`, and other tags. Neither site uses
any template tags from django-grep (confirmed by usage analysis).

#### Acceptance Criteria

**R7.1** THE django-grep package SHALL be audited: scan both sites for
`{% load django_grep_tags %}` or `{% load django_grep %}` usage.

**R7.2** WHEN a template tag is confirmed unused in both sites, THE tag SHALL
be removed from `django_grep_tags.py`.

**R7.3** WHEN a template tag is removed, THE corresponding test SHALL also be removed.

**R7.4** WHERE a template tag has documented future value, THE tag SHALL be retained
and documented in `docs/templatetags.md` with: purpose, usage example, parameters.

**R7.5** AFTER cleanup, `templatetags/django_grep_tags.py` SHALL contain only tags
that are either actively used or explicitly documented as reserved.

**R7.6** WHEN tags are removed, THE django-grep test suite SHALL continue to pass.

#### Success Metric
```bash
grep -r "load django_grep" ctc-research.com/ structa.cloud/
# Returns 0 matches (or only matches for tags explicitly kept)
```

---

### R8 — Document Abstract Base Patterns

**User Story:** As a developer, I want `BaseCartMixin` and `BaseDashboardMixin`
documented as abstract patterns so future sites have a clear contract to implement.

#### Acceptance Criteria

**R8.1** THE django-grep package SHALL define an abstract `BaseCartMixin` in
`django_grep/pipelines/site/mixins.py` with method signatures and docstrings
for cart operations, containing no site-specific logic.

**R8.2** THE django-grep package SHALL define an abstract `BaseDashboardMixin`
in `django_grep/pipelines/site/mixins.py` with method signatures and docstrings
for dashboard context, containing no site-specific logic.

**R8.3** THE `BaseCartMixin` docstring SHALL note that ctc-research.com implements
an LMS-specific subclass and structa.cloud implements a generic e-commerce subclass.

**R8.4** THE `BaseDashboardMixin` docstring SHALL note that ctc-research.com
implements an LMS analytics subclass and structa.cloud implements a generic dashboard.

**R8.5** THE django-grep documentation SHALL include `docs/abstract-patterns.md`
explaining the abstract base pattern with a minimal implementation example for each.

**R8.6** WHEN a new site uses django-grep, THE site SHALL be able to subclass
the abstract base classes without modifying the shared library.

#### Success Metric
`libs/django-grep/docs/abstract-patterns.md` exists and contains code examples
for both `BaseCartMixin` and `BaseDashboardMixin`.

---

### R9 — Documentation Organization

**User Story:** As a developer, I want all project documentation organized into
correct categorized folders with an updated README and sidebar.

**Current state**: Docs reorganization is partially done. The `docs/api/` folder
has been replaced with Wagtail-specific docs. The sidebar has been updated.
The root README still lacks a Documentation section.

#### Acceptance Criteria

**R9.1** THE `docs/` directory SHALL maintain the following categories:
`api/` (Wagtail/Django reference), `libraries/`, `project-status/`,
`development/`, `infrastructure/`, `specs/`.

**R9.2** WHEN a new document is created as part of this spec's work,
THE document SHALL be placed in the appropriate category folder.

**R9.3** THE `docs/_sidebar.md` SHALL list all documents with accurate relative links.

**R9.4** THE root `README.md` SHALL include a "Documentation" section linking to
`docs/README.md` or `docs/_sidebar.md`.

**R9.5** THE `docs/libraries/` folder SHALL contain `django-grep-overview.md`
and `django-seed-overview.md` with module structure, usage examples, and changelogs.

**R9.6** WHEN a document becomes outdated due to completed work, THE document
SHALL be updated to reflect completed status rather than deleted.

#### Success Metric
`docs/_sidebar.md` has no broken links. `README.md` contains a "Documentation" section.

---

## Risk Assessment

### Risk 1 — Database Migration Failure (R1, R2)

**Probability**: Medium. **Impact**: High.

Moving models with `SeparateDatabaseAndState` is safe if done correctly,
but a mistake in the migration could corrupt the ORM state.

**Mitigation**:
- Take full database backups before any migration work
- Test migrations in a staging environment first
- Use `--fake` flag to verify migration state before applying
- Keep backups for 30 days minimum

---

### Risk 2 — Import Path Breakage (R1, R2)

**Probability**: Medium. **Impact**: High.

After moving models/mixins, any missed import statement causes a runtime error.

**Mitigation**:
- Run `grep -r "from apps.handlers.site.mixins" .` before and after to verify 0 remaining
- Run `python manage.py check` in both sites after each move
- Run the full test suite after each individual model move (not just at the end)
- For R2 (mixins.py), do the move + all import updates in a single atomic commit

---

### Risk 3 — GitHub Push Blocked (R6)

**Probability**: Low. **Impact**: Medium.

The GitHub push may fail if the remote has diverged or credentials are not configured.

**Mitigation**:
- Verify git remote: `cd libs/django-grep && git remote -v`
- Verify branch: `git branch` (should show `generic`)
- If push fails: `git pull --rebase origin generic` then retry
- For django-seed: branch is `main`, not `generic`

---

## Rollback Plan

### Rollback R1/R2 (Model/Mixin Moves)

If a model move causes issues:

```bash
# 1. Revert the migration in the affected site
python manage.py migrate <app> <previous_migration>

# 2. Restore the original model file from git
git checkout HEAD~1 -- apps/handlers/site/mixins.py

# 3. Revert import changes
git revert <commit-hash>

# 4. Restore from database backup if needed
pg_restore -d db_ctc backup_before_migration.dump
```

### Rollback R6 (Package Sync)

If `uv sync` breaks imports:

```bash
# Revert pyproject.toml to local path references
cd ctc-research.com
git checkout HEAD~1 -- pyproject.toml
uv sync  # reinstalls from local path
```

Backups of local libs are at:
- `.backup/ctc-research-libs-20260407-101909/`
- `.backup/structa-cloud-libs-20260407-101909/`

---

## Validation Matrix

| Requirement | Verification Command |
|-------------|---------------------|
| R1 — Models moved | `grep -r "from core.CI.models" ctc-research.com/` → 0 matches |
| R2 — Mixins moved | `grep -r "from apps.handlers.site.mixins" . ` → 0 matches |
| R3 — Coverage | `pytest --cov=django_seed/services/queue_manager --cov-report=term` → ≥80% |
| R4 — Tests fixed | `cd ctc-research.com && .venv/bin/pytest tests/ -v` → 12 passed |
| R5 — structa.cloud env | `cd structa.cloud && uv run pytest alliance/CI/tests/ -v` → passes |
| R6 — GitHub push | `cd libs/django-grep && git log origin/generic..HEAD` → 0 commits ahead |
| R7 — Template tags | `grep -r "load django_grep" ctc-research.com/ structa.cloud/` → 0 or documented |
| R8 — Abstract patterns | `ls libs/django-grep/docs/abstract-patterns.md` → file exists |
| R9 — Docs sidebar | `cat docs/_sidebar.md` → all links valid |
