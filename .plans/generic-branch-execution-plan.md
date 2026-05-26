# Generic Branch Execution Plan (CTC Research + Structa Cloud)

Status: **IN PROGRESS**
Date: 2026-05-26

## Scope
Validate the two-website workspace (`ctc-research.com`, `structa.cloud`) for:
- project config loading and yml availability
- Django/Wagtail URL/bootstrap wiring
- assets/build command availability
- package import usage (`django-osoul`, `django-rseal`, `django-grep`)
- deprecated shim cleanup (`www/conf.py`)

## Phase Progress
1. **Phase 1 (Path + baseline checks)** — ✅ done
2. **Phase 2 (Site runtime checks)** — ✅ done
3. **Phase 3 (Alliance scope checks)** — ✅ done
4. **Phase 4 (URL wiring deep import checks)** — ⚠️ blocked (`django_grep` import missing in current env)
5. **Phase 5 (Finalize + close undone tasks)** — ⏳ pending

## Completed
- Removed deprecated `www/conf.py` in both sites.
- Added and executed root validation commands (`check-paths`, `check-sites`, `check-alliance`).
- Verified site-level `manage.py check` passes for both websites.
- Fixed undefined module risk in `www/__init__.py` files by replacing `structlog` hard import with stdlib logging.

## Current Errors
- `ModuleNotFoundError: No module named 'django_grep'` during direct URL module import checks for both websites.
- Alliance targeted pytest still blocked (`pytest` unavailable in current env; package install restricted by proxy).

## Finalization Criteria
- `django_grep` import availability confirmed in active env.
- URL module import checks pass in both sites.
- Alliance targeted pytest run completes.
