---
Object type: Architecture
Tags: architecture, technical, system-design, adr
Status: Active
---

# Architecture — System Design & Durable Decisions

> **Description:** System architecture, data flow, and durable design decisions. Captures the technical foundation that guides all product development.

## Properties

| Property | Type | Description |
|---|---|---|
| `Status` | Select | Draft, Active, Reviewed, Deprecated |
| `Related Editions` | Relation → Edition | Editions affected by the architecture |
| `Version` | Text | Architecture version |
| `Related Features` | Relation → Feature | Features this architecture supports |
| `Related Guides` | Relation → Guide | How-to methods for this architecture |
| `Related Goals` | Relation → Goal | Strategic outcomes served |
| `Related Decisions` | Relation → Decision | ADRs that shaped this design |
| `Tags` | Multi-select | Cross-cutting labels |

## Use

Describe the system context, boundaries, and data flow before product details. Link to features for scope and decisions for rationale. Use for durable technical foundations and ADRs — not for one-off implementation notes.

## Graph

Architecture → Related Features → Edition · Architecture → Related Decisions → ADR · Architecture → Related Guides → Guide.

## Related

- → `_object-types.md` — Type registry
- → `_relations.md` — Relation guide
- → `../architecture/_index.md` — Architecture directory
- → `decision.md` — Decision (ADR) object type