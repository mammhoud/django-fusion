---
# yaml-language-server: $schema=../schemas/note.schema.json
Object type: Note
Tags: note
Status: Published
---

# Note — Quick Thoughts & Meeting Minutes

> **Type:** Note 📝
> **Layout:** Note
> **Description:** Quick thoughts, ideas, meeting minutes, and informal documentation — lightweight captures that don't need formal structure.

---

## Properties

| Property | Type | Options | Description |
|----------|------|---------|-------------|
| `Tags` | Multi-select | — | Cross-cutting labels |
| `Related Architecture` | Relation → Architecture | — | Architectural context |
| `Related Features` | Relation → Feature | — | Related feature |
| `Related Guides` | Relation → Guide | — | Related guide |

---

## Usage in Knowledge Graph

| Relation | Target |
|----------|--------|
| Related Architecture | Architecture |
| Related Features | Feature |
| Related Guides | Guide |

---

## Related

- → `_object-types.md` — All type definitions
- → `_relations.md` — Relations guide
- → `page.md` — Page type (for formal content)
