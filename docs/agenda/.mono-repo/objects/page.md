---
# yaml-language-server: $schema=../schemas/page.schema.json
Object type: Page
Tags: page, documentation
Status: Published
---

# Page — General Knowledge Content

> **Type:** Page 📄
> **Layout:** Page
> **Description:** General-purpose knowledge pages — structured documentation, reference content, and information that serves as foundation for all other types.

---

## Properties

| Property | Type | Options | Description |
|----------|------|---------|-------------|
| `Status` | Select | Draft, Review, Published | Review status |
| `Tags` | Multi-select | — | Cross-cutting labels |
| `Related Architecture` | Relation → Architecture | — | System architecture links |
| `Related Features` | Relation → Feature | — | Feature references |
| `Related Guides` | Relation → Guide | — | Guide references |

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
- → `_tags.md` — Tag definitions
- → `workspace.md` — Workspace type (for hub pages)
- → `note.md` — Note type (for informal content)
