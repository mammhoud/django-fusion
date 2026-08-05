# Migration, Cleanup, and django-fusion Integration — Master Plan
> **Tags:** #migration #cleanup #master

> **Last updated:** 2026-07-26 | **Branch:** `generic`  
> **Scope:** Complete migrations for all Django sites, optional cleanup of old/duplicate directories, and full integration with django-fusion.

## Current Snapshot

- ✅ `lms-fusion` core migration — complete
- ✅ `cms-fusion` core migration — complete
- ✅ `DJANGO_BOLT_FUSION_CASE_STUDY.md` — historical reference retained; Bolt integration is project-owned
- ⬜ [`legacy/legacy-cleanup.md`](legacy/legacy-cleanup.md) — not started

> **Case Study:** [`../DJANGO_BOLT_FUSION_CASE_STUDY.md`](../DJANGO_BOLT_FUSION_CASE_STUDY.md) — comprehensive analysis of django-bolt patterns across projects and integration recommendations.

---

## 1. Plan Inventory

| # | Plan | Scope | Status | Progress |
|---|------|-------|:------:|:--------:|
| 1 | [`lms-fusion/migration-plan.md`](lms-fusion/migration-plan.md) | LMS Fusion — django-fusion + project-owned API + Next.js frontend | ✅ Complete | 100% |
| 2 | [`cms-fusion/migration-plan.md`](cms-fusion/migration-plan.md) | CMS Fusion — django-fusion + project-owned API + Next.js frontend + fallbacks | ✅ Complete | 100% |
| 3 | [`../DJANGO_BOLT_FUSION_CASE_STUDY.md`](../DJANGO_BOLT_FUSION_CASE_STUDY.md) | django-bolt usage analysis + fusion integration recommendations | ✅ Complete | 100% |
| 4 | [`legacy/legacy-cleanup.md`](legacy/legacy-cleanup.md) | Audit, archive, and remove old/duplicate project directories | ⬜ Not Started | 0% |

---

## 2. Migration Order

Run migrations in this order to respect shared-library and site dependencies:

1. **Shared libraries**
   - `libs/django-fusion/`
   - `libs/ceptor-ai/`
2. **Existing reference sites**
   - `projects/cms/ctc-research/`
   - `projects/lms/cms/` (legacy)
   - `projects/cms/lms-full/` (legacy)
   - `projects/cms/portfolio/`
   - `projects/cypercloud/`
3. **New Fusion sites**
   - `projects/lms-fusion/backend/` — django-fusion + project-owned API (`bolt_apis.py`) ✅
   - `projects/cms-fusion/backend/` — django-fusion + project-owned API (`bolt_apis.py`) ✅
   - `projects/lms-fusion/frontend/` — Next.js 14 + fusion types/decoder/store/client ✅
   - `projects/cms-fusion/frontend/` — Next.js 14 + fusion types/decoder/store/client + fallbacks ✅

---

## 3. django-Fusion Integration Checkpoints

Every Django site that uses django-fusion must pass the following checks before being considered migrated:

| # | Checkpoint | Verification |
|---|------------|--------------|
| 1 | `django_fusion` is in `INSTALLED_APPS` | `grep django_fusion backend/settings.py` |
| 2 | Base template loads `fusion_tags` | `{% load fusion_tags %}` in `templates/base.html` |
| 3 | Base template emits `fusion_render_first` flag | `<html data-fusion-render-first="{% fusion_render_first_flag %}">` |
| 4 | Wagtail pages inherit from `RoutableComponent` where applicable | `class HomePage(RoutableComponent): ...` |
| 5 | HTMX/fragment partials use `FragmentComponent` | `class MyFragment(FragmentComponent): ...` |
| 6 | Component templates use `{% comp "name" /%}` consistently | Search for legacy `{% include %}` and migrate |
| 7 | Context processors include django-fusion helpers | `fusion_render_first`, `is_htmx_request`, etc. |

---

## 4. Common Migration Commands

```bash
# Create migrations for a specific app
cd projects/<site>/backend && make makemigrations APP=plugins.branding

# Apply migrations
cd projects/<site>/backend && make migrate

# Django system checks
cd projects/<site>/backend && make check

# Full setup chain (frontend + backend + data)
cd projects/<site> && make setup
```

---

## 5. Testing & Validation

- [ ] Run `make check` on every migrated site.
- [ ] Run `make test` (or `pytest`) on every migrated site.
- [ ] Verify `showmigrations` reports no unapplied migrations.
- [ ] Verify django-fusion fragment rendering works on a sample page.
- [ ] Verify `fusion_render_first` flag is present in page source.

---

## 6. Rollback Plan

If a migration fails in production:

1. Restore the database from the latest backup.
2. Revert the offending code/migration in git.
3. Re-deploy the previous release.
4. Run `manage.py migrate` to align migration state.

---

## 7. Legend

| Symbol | Meaning |
|:------:|---------|
| ✅ | Complete |
| 🟡 | In Progress |
| ⬜ | Not Started |
| ❌ | Blocked |
| 🔄 | Needs Review |
