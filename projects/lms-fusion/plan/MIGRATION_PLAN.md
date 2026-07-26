# LMS Fusion — Migration & django-fusion Integration Plan

> **Site:** `lms-fusion`  
> **Path:** `projects/lms-fusion/`  
> **Last updated:** 2026-07-26

---

## 1. Pre-Migration Inventory

| App / Area | Status | Notes |
|------------|:------:|-------|
| `plugins.branding` | ⬜ | Needs migration `0001_initial.py` already scaffolded |
| `plugins.accounts` | ⬜ | Copied from ctc-research; verify compatibility |
| `plugins.lms` | ⬜ | Copied from ctc-research; verify models |
| `plugins.blog` |  | Copied from ctc-research |
| `plugins.profile` |  | Copied from ctc-research |
| `www.core` |  | Copied from ctc-research |
| `django_fusion` |  | Verify `INSTALLED_APPS` and context processors |

---

## 2. Migration Steps

| # | Task | Command / Action | Status |
|---|------|------------------|:------:|
| 1 | Create branding migration | `cd backend && python3 manage.py makemigrations plugins.branding` | ⬜ |
| 2 | Create remaining migrations | `cd backend && python3 manage.py makemigrations` | ⬜ |
| 3 | Apply migrations | `cd backend && make migrate` | ⬜ |
| 4 | Run Django checks | `cd backend && make check` | ⬜ |
| 5 | Create superuser | `cd backend && python3 manage.py createsuperuser` | ⬜ |
| 6 | Seed initial branding | `python3 manage.py shell < scripts/seed_branding.py` | ⬜ |

---

## 3. django-fusion Integration Checklist

- [ ] `django_fusion` is listed in `backend/settings.py` `INSTALLED_APPS`.
- [ ] Base template `templates/base.html` loads `{% load fusion_tags %}`.
- [ ] Base template emits `data-fusion-render-first="{% fusion_render_first_flag %}"`.
- [ ] `fusion_branding_context` is registered in `TEMPLATES[0]["OPTIONS"]["context_processors"]`.
- [ ] At least one Wagtail page inherits from `RoutableComponent`.
- [ ] Fragment partials inherit from `FragmentComponent`.
- [ ] Templates use `{% comp "name" /%}` instead of bare `{% include %}` where possible.

---

## 4. Verification Tests

```bash
cd projects/lms-fusion/backend
make check
make test
python3 manage.py showmigrations
```

Expected outcomes:

- `make check` passes with no `ImproperlyConfigured` errors.
- `make test` passes (or runs with only expected failures from unimplemented features).
- `showmigrations` shows all migrations applied.
- Page source of the homepage contains `data-fusion-render-first`.

---

## 5. Optional Cleanup

Once `lms-fusion` is fully operational, the following legacy directories may be removed or archived:

- `projects/lms/cms/`
- `projects/cms/lms-full/`
- `projects/lms/front-end/` (if replaced by `lms-fusion/frontend/`)

See [`projects/docs/LEGACY_CLEANUP_PLAN.md`](../docs/LEGACY_CLEANUP_PLAN.md) for the audit and removal procedure.
