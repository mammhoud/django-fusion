---
Object type: Module
Tags: module, library, django-fusion, wagtail, components
Status: Active
Type: Library
Version: tracked in libs/django-fusion
Related Repositories: structa-cloud-monorepo
Related Projects: django-fusion-library
Related Documentation: _index
---

# django-fusion — Shared Django/Wagtail Framework

> **Description:** The reusable Django/Wagtail component framework at `libs/django-fusion/` — `{% comp %}` components, fragments, routes, forms, tables, and HTMX support.

## Responsibility

- Registered components (`django_fusion.comp`), fragment identifiers, route helpers
- Canonical `django_fusion.*` imports only — no re-export shims
- DataToken sync tagging (GenericForeignKey), Django-Bolt fusion patterns

## Consumers

- Precis (precis-main, precis-ctc), Formint Pro/Cloud, Loop-CRM, Syntara

## Evidence

- `cd libs/django-fusion && uv run pytest` green
- Case studies: django-bolt-fusion, data-token-sync-tagging

## Related

- → `../repositories/structa-cloud-monorepo.md` — Repo
- → `../apis/django-fusion-api.md` — Surface
- → `../components/django-fusion-components.md` — Components
- → `../objects/module.md` — Module object type