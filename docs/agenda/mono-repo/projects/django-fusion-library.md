---
Object type: Project
Tags: project, django-fusion, library, wagtail, components
Status: Active
Related Workspace: workspace
Related Products: django-fusion
Related Teams: engineering
---

# django-fusion — Shared Django/Wagtail Component Framework

> **Description:** The shared library (`libs/django-fusion/`) powering Django/Wagtail routing, `{% comp %}` components, fragments, forms, tables, and HTMX flows across Structa Cloud products.

## Outcome

One canonical component framework: canonical `django_fusion.*` imports (no re-export shims), registered components, fragment identifiers, and validated `make check`/`pytest` green.

## Scope and gates

- In scope: `src/django_fusion/comp`, routes, fragments, core; DataToken sync tagging; Django-Bolt fusion case study.
- Out of scope: product-specific code — the library stays product-agnostic.
- Completion evidence: `cd libs/django-fusion && uv run pytest` green; `manage.py check` clean in consuming products.

## Related

- → `../modules/_index.md` — Module objects
- → `../objects/component.md` — Component object type
- → `../../../plans/django-fusion/README.md` — Library plans
- → `../objects/project.md` — Project object type