# CHANGELOG

## 2026-06-30 — Template Reorganization, Settings Inlining & Documentation

### Template Cleanup (`projects/assets/templates/`)

- **Deduplicated 60+ template files** — consolidated `errors/`, `newsletter/`, `privacy/`, `mfa/` into their `plugins/` equivalents (kept `plugins/` as canonical source)
- **Merged `LMS/` → `lms/`** (Linux case-sensitivity — these were separate directories)
- **Removed 6 empty files** (0-byte placeholders) and 2 `" copy"`-suffixed files
- **Kept `emails/` and `components/pagination/`** as backwards-compatible mirrors of `plugins/` (117+ `render_to_string("emails/...")` references in Python code depend on those paths)
- **Fixed template reference paths** — updated 7 `{% extends "emails/..." %}`, 6 `{% include "components/pagination/..." %}`, and 1 `{% include "mfa/..." %}` to use correct resolved paths
- **Moved `email/` unique files** (`enrollment_confirmation.txt`, `enrollment_status_update.txt`) into `plugins/emails/`
- **Cleaned empty directories**: `projects/`, `appspecific/`, `ui/wagtailprojects/`, `events/sections/`
- Preserved `allauth.md` (comprehensive allauth template mapping reference)

### Settings Inlining — Per-Site Architecture

- **Inlined `LMS_LOCAL_APPS`** from `configs/base/lms.py` into `precis-ctc/settings.py` and `lms/settings.py`
  - Deleted `configs/base/lms.py`
  - Removed `from configs.base.lms import *` from `configs/base/__init__.py`
  - Cleaned up stale `# LMS_LOCAL_APPS has been moved to configs.base.lms` comment from `configs/base/apps.py`
- **Inlined UNFOLD admin sidebar** from `configs/base/admin_site.py`
  - Shared baseline now uses `show_all_applications: True` (auto-discovery for LMS sites) and generic branding
  - VResume overrides with curated navigation in its `settings.py`
  - Removed dead imports (`static`, `reverse_lazy`) from shared `admin_site.py`
- **Inlined `CELERY_BEAT_SCHEDULE`** from `configs/base/celery_beat.py`
  - Shared file now `CELERY_BEAT_SCHEDULE = {}`
  - VResume defines its 5 periodic tasks (`pages.connect.*`, `pages.blog.*`) in its `settings.py`
- **Deleted `configs/base/storages.py`** — deprecated, had broken `from core.config import BASE_DIR` import, superseded by `configs/base/assets.py`, zero references

### Documentation — 6 New Files

| File | Content |
|---|---|
| `assets/templates/README.md` | Template directory structure, resolution order, BEM conventions, rules |
| `docs/INDEX.md` | Master documentation index with quick-reference tables |
| `docs/websites.md` | Per-website config, LOCAL_APPS, UNFOLD sidebar architecture, CELERY_BEAT schedules |
| `docs/environments.md` | Dynaconf environments, feature toggles, settings API, env variables |
| `docs/packages.md` | Internal libs (django-fusion, ceptor-ai), external deps, best practices |
| `docs/templates.md` | Template inheritance, HTMX fragments, layouts, Wagtail blocks, email templates |

- **Updated** `assets/templates/AGENTS.md` → points to new docs
- **Copied** all docs to `libs/django-fusion/docs/` and `libs/ceptor-ai/docs/`

### Test Fixes — 30 failures → 0 failures

| File | Root Cause | Fix |
|---|---|---|
| `test_parser.py` (4 failures) | Fragment now uses `{% include %}` not `{% comp %}` | Updated expectations |
| `test_component_tag.py` (4 failures) | Relative template `DIRS` path | Changed to absolute path |
| `test_error_tracker_middleware.py` (8 failures) | Middleware didn't log on response status codes | Added 4xx/5xx logging in `__call__`, fixed test assertions |
| `test_deduplication_properties.py` (2 failures) | Hypothesis `function_scoped_fixture` health check | Suppressed with `HealthCheck` enum |
| `test_osoul_smoke.py` (2 failures) | Stale import paths (`BaseModel`, utils) | Updated to current module structure |
| `test_utils.py` (8 failures) | Validators/datetime moved to new module paths | Updated all import paths |
| `test_page_catalog.py` (2 failures) | Missing `@pytest.mark.django_db`, Wagtail pages in test DB | Added mark, used `template_pages()` |

**Final: 169 passed, 0 failed, 2 pre-existing errors, 1 skipped** (up from 139 passed, 30 failed).

### Validation

- All 3 sites pass `manage.py check` with zero issues
- Test suite: 169 passed, 0 failures
