---
Object type: API
Tags: api, component, django-fusion, wagtail, htmx
Status: Active
Related Features: component-framework
Related Integrations: pos-revenue-ingestion
Related Products: django-fusion
---

# django-fusion API & Component Surface

> **Description:** The shared Django/Wagtail component framework's surface — `{% comp %}` components, fragments, routes, forms, tables, and HTMX flows in `libs/django-fusion/`.

## Surface

| Capability | Purpose |
|---|---|
| `django_fusion.comp` | Registered `{% comp "name" /%}` components |
| `django_fusion.routes` | Product route helpers |
| `django_fusion.fragments` | Fragment identifiers + context keys |
| `django_fusion.forms` / `tables` | Shared form/table building blocks |
| DataToken sync tagging | GenericForeignKey sync row tagging (case study) |

## Contract notes

- Canonical imports: `django_fusion.*` — no re-export shims or forwarding `__init__` re-exports
- `{% include %}` only for genuinely dynamic template names or local includes
- Validated via `cd libs/django-fusion && uv run pytest`

## Related

- → `../objects/api.md` — API object type
- → `../objects/component.md` — Component object type
- → `../modules/django-fusion-module.md` — Module object
- → `../../case-studies/django-bolt-fusion.md` — Fusion case study
- → `../../case-studies/data-token-sync-tagging.md` — DataToken case study