---
Object type: Diagram
Tags: diagram, visualization, architecture, flow, documentation
Status: Active
---

# Diagram — Visualization Object

> **Description:** Flow, architecture, sequence, data model, or timeline visualization that makes complex systems understandable.

## Properties

| Property | Type | Description |
|---|---|---|
| `Status` | Select | Draft, Published, Deprecated |
| `Type` | Select | Flow, Architecture, Sequence, ERD, State, Gantt, Timeline |
| `Related Editions` | Relation → Edition | Editions the diagram applies to |
| `Related Docs` | Relation → Any | Docs the diagram illustrates |
| `Tags` | Multi-select | Cross-cutting labels |

## Use

Write the diagram's intent, the source of truth it visualizes, and its rendered asset path. The agenda keeps editable mermaid sources in `../diagrams/` and rendered SVGs in `docs/public/agenda/diagrams/`.

## Graph

Diagram → Related Docs → Feature/Architecture/Plan · Diagram → Related Editions → Edition.

## Related

- → `_object-types.md` — Type registry
- → `_relations.md` — Relation guide
- → `../diagrams/_index.md` — Diagrams directory
- → `../../diagrams/README.md` — Agenda diagram package (rendered assets + render script)