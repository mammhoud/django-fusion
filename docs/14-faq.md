# Frequently Asked Questions — DF-014

> Source of truth: questions answered by tests in `tests/`. Each entry
> has a test reference if you want to verify the behaviour yourself.

## General

### Q: What's the minimum Python version?

A: Python 3.11 (`requires-python = ">=3.11"` in `pyproject.toml`).
Justified by the `from __future__ import annotations` imports in
`projects/services.py` and `projects/models.py`, plus PEP 695 generic syntax
in `projects/cache.py`.

### Q: What's the minimum Django version?

A: Django 4.2 LTS. Django 5.0+ is also supported. `pyproject.toml`
declares `django>=4.2`.

### Q: Does it work with Wagtail 6?

A: Yes. `django_fusion.wagtail` is tested against Wagtail 5.x and 6.x.
Older 4.x versions may break `BaseSnippetViewSet`.

## Components

### Q: Can I use `{% comp %}` without `{% load components %}`?

A: Yes, by adding `django_fusion.comp.templatetags.components` to
`TEMPLATES[0]["OPTIONS"]["builtins"]`. See DF-001.

### Q: Difference between `fragment_name` and `route_name`?

A: `route_name` is the URL name registered with `Site`; `fragment_name`
is the dotted identity used by `ComponentRegistry` and
`FragmentComponent`. They often overlap but are separate concerns:
a single component can have multiple `route_name`s but one
`fragment_name`.

### Q: Can I set both `model` and `fragment_name` on `PaginatedListView`?

A: Yes, but priority order wins: explicit `fragment_name` > model
derivation > `items_template` derivation > base class default.
See `tests/test_routable_components.py:TestResolveTemplateNameIntegration`.

### Q: Are `fragment`, `name`, `fragment_slug`, `fragment_key` valid aliases?

A: **No.** They're rejected with `TemplateSyntaxError` to enforce the
single reserved kwarg. See
`tests/test_routable_components.py:TestFragmentNameConvention`.

### Q: Do I have to use `{{ props.name }}`, or can I write `{{ name }}`?

A: Both work since 0.5.0. A declared `{% prop name %}` is exposed
**both** as `{{ props.name }}` (the documented mapping) and as a bare
context variable `{{ name }}` — see
[DF-018 §2](./18-render-contract.md). The one gotcha: a
**declared-but-unpassed** prop resolves to `None` and shadows any
outer-context variable of the same name, so pass values explicitly at
call sites: `{% comp "…" name=name / %}`.

## Models / Database

### Q: How do migrations work with `CachedManager`?

A: `CachedManager` doesn't add a column; it's a manager-level feature.
Migrations are unaffected. Use `python manage.py makemigrations` as
usual.

### Q: Do `TimeStampedModel` and `CachedManager` work together?

A: Yes, both come from `django_fusion.models` and
`django_fusion.management.managers` respectively. Stack freely.

## Settings

### Q: Should I use `DJANGO_SETTINGS_MODULE=tests.settings` in CI?

A: **No.** For `django-fusion`'s own tests, the conftest's
`settings.configure()` is the canonical path — pytest-django's lazy
init can fail to resolve. This is enforced by
`tests/test_django_settings_configure_contract.py`.

### Q: How does Dynaconf know which YAML to read?

A: From any of these locations (first match wins):

```text
config/settings.yml
config/settings.yaml
config/settings.toml
config/settings.json
config/settings.env
```

### Q: How do I switch between environments?

A: Set `DJANGO_ENV=production`, `DJANGO_ENV=development`, etc.
Dynaconf picks the matching YAML top-level key.

### Q: Should I export `DJANGO_DEBUG_CONFTEST=1` in production?

A: **No.** This is a conftest-only diagnostic flag; it prints the
active Django config to stderr. Keep it in dev / CI test runs.

## Health endpoint

### Q: What does `/health/db/` 503 mean?

A: Postgres is unreachable from inside the worker process. Common
causes: connection-pool exhaustion, mis-set `DATABASES["default"]["HOST"]`,
or wrong `ALLOWED_HOSTS` rejecting the probe header.

## Wagtail

### Q: Can I add a custom block without forking `blocks.py`?

A: Yes — define `CallToActionBlock` (or any `StructBlock`) in your
**site's** `wagtail_blocks.py`, then reference it in `StreamField`.
Editing `django_fusion/wagtail/blocks.py` directly is **anti-pattern**
because upgrades overwrite it.

### Q: How do I enable `export_to_csv` on a snippet?

A: Set `export_csv_fields = ["field1", "field2", ...]` on the
viewset. The button auto-appears in the listing toolbar.

## Tests

### Q: How do I run only the registry tests?

A: `pytest tests/test_comp_registry.py -v`. The fast loop is
typically <2 s.

### Q: How do I enable verbose conftest logging?

A: `DJANGO_DEBUG_CONFTEST=1 pytest -s tests/test_comp_registry.py`.
Exact-match `== "1"`; `=true` and `=yes` won't trigger.

## Where to go next

- [DF-013 Troubleshooting](./13-troubleshooting.md) — symptom → cause → fix
- [DF-011 Best practices](./11-best-practices.md) — patterns
- [DF-012 Integration examples](./12-integration-examples.md) — end-to-end
