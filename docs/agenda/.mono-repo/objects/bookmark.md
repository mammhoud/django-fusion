---
# yaml-language-server: $schema=../schemas/bookmark.schema.json
Object type: Bookmark
Tags: bookmark, reference
Status: Published
---

# Bookmark — External Resources & References

> **Type:** Bookmark 🔖
> **Layout:** Bookmark
> **Description:** External links and curated resources — bookmarks pointing to tools, libraries, and references outside the knowledge graph.

---

## Properties

| Property | Type | Options | Description |
|----------|------|---------|-------------|
| `URL` | Text | — | External link URL |
| `Tags` | Multi-select | — | Cross-cutting labels |
| `Category` | Select | Development, Documentation, Publishing, Staging, Done | Content category |
| `Related Features` | Relation → Feature | — | Feature this relates to |

---

## Usage in Knowledge Graph

| Relation | Target |
|----------|--------|
| Related Features | Feature |

---

## Related

- → `_object-types.md` — All type definitions
- → `_relations.md` — Relations guide
- → `../plans/projects.md` — Project references
