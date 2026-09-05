---
Object type: Workspace
Tags: diagrams, diagram, visualization, architecture
Status: Active
---

# Diagrams — Visualization Objects

> Flow, architecture, sequence, data model, and timeline visualizations. Editable mermaid sources live in the agenda diagram package; rendered SVGs are served from `docs/public/agenda/diagrams/`.

## Diagram objects

| Diagram | Mermaid source | Rendered SVG |
|---|---|---|
| Loop-CRM API request flows | [`../../diagrams/api-request-flows.md`](../../diagrams/api-request-flows.md) | `/agenda/diagrams/diagrams-api-request-flows-1.svg` |
| Django model ERD — Loop-CRM | [`../../diagrams/django-loop-crm-er.md`](../../diagrams/django-loop-crm-er.md) | `/agenda/diagrams/diagrams-django-loop-crm-er-1.svg` |
| Rust SQLite ERD — Formint Community | [`../../diagrams/rust-sqlite-er.md`](../../diagrams/rust-sqlite-er.md) | `/agenda/diagrams/diagrams-rust-sqlite-er-1.svg` |
| Blinko SurrealDB | [`../../diagrams/blinko-surrealdb.md`](../../diagrams/blinko-surrealdb.md) | `/agenda/diagrams/diagrams-blinko-surrealdb-1.svg` |
| Anytype channel model | [`../objects/_object-types.md`](../objects/_object-types.md) | `/agenda/diagrams/mono-repo-objects-_object-types-1.svg` |
| Object graph | [`../objects/_index.md`](../objects/_index.md) | `/agenda/diagrams/mono-repo-objects-_index-1.svg` |

## Re-render

```bash
node docs/scripts/render-agenda-diagrams.mjs
```

## Related

- → `../objects/diagram.md` — Diagram object type
- → `../../diagrams/README.md` — Diagram package index
- → `../../case-studies/INDEX.md` — Case-study diagrams