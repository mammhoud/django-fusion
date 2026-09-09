---
Object type: Component
Tags: component, ui-component, layout-component, data-component, fusion
Status: Active
Related Features: component-framework
Related APIs: django-fusion-api
Related Styles: design-tokens
---

# django-fusion Components — Registered Library

> **Description:** The reusable component registry in `libs/django-fusion/` — BEM-style blocks, registered via `{% comp "name" /%}`, used across Structa Cloud products.

## Component categories

| Category | Examples |
|---|---|
| Layout | Containers, grids, sidebars |
| Data | Tables, lists, fragments |
| Form | Inputs, selects, forms with django-fusion helpers |
| Widget | HTMX islands, fragments |

## Rules

- BEM-style classes; never use IDs for styling
- `{% comp "name" /%}` for registered components; `{% include %}` only for dynamic/local includes
- Fragment identifiers via `fragment_name` + context keys

## Related

- → `../apis/django-fusion-api.md` — Surface contract
- → `../styles/design-tokens.md` — Design tokens
- → `../objects/component.md` — Component object type