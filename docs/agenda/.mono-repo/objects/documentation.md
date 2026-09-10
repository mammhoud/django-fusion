---
Object type: Documentation
Tags: documentation, guides, reference, onboarding, knowledge
Status: Active
---

# Documentation — Project Documentation

> **Description:** Project documentation, guides, and reference materials that enable onboarding and knowledge sharing.

## Properties

| Property | Type | Description |
|---|---|---|
| `Status` | Select | Draft, Published, Deprecated |
| `Type` | Select | README, Guide, API Reference, Tutorial, Architecture, Changelog |
| `Audience` | Select | Developers, Operators, End Users, Team |
| `Related Repositories` | Relation → Repository | Where the docs live |
| `Related Projects` | Relation → Project | Projects documented |
| `Related Guides` | Relation → Guide | How-to methods |
| `Tags` | Multi-select | Cross-cutting labels |

## Use

Document the docs set's structure, audience, and maintenance method. The `docs/` tree is the canonical home (Docus pipeline, EN/AR parity via `docs/ar-content/`, agenda system in `docs/agenda/`); this object type links repo docs into the knowledge graph.

## Graph

Documentation → Related Guides → Guide · Documentation → Related Repositories → Repository.

## Related

- → `_object-types.md` — Type registry
- → `_relations.md` — Relation guide
- → `../documentation/_index.md` — Documentation directory
- → `guide.md` — Guide object type
- → `../../../guides/09-docus.md` — Docus docs pipeline guide