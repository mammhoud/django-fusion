---
# yaml-language-server: $schema=../schemas/page.schema.json
Object type: Workspace
Tags: workspace
Status: Published
---

# Workspace — Hub Pages & Knowledge Centers

> **Type:** Workspace 🏢
> **Layout:** Page
> **Description:** High-level hub pages grouping related plans, projects, and knowledge — serving as navigation centers for the documentation system.

---

## Properties

| Property | Type | Description |
|----------|------|-------------|
| `Backlinks` | Text | Documents that link back to this workspace |
| `Links` | Text | Key links to related objects |
| `Emoji` | Emoji | Visual identifier |
| `Related Plans` | Relation → Plan | Plans associated with this workspace |
| `Related Projects` | Relation → Project | Projects associated with this workspace |
| `Tags` | Multi-select | Cross-cutting labels |

---

## Usage in Knowledge Graph

```
Workspace 🏢
    ├── Related Plans ────→ Plan 📋
    └── Related Projects ──→ Project 📁
```

---

## Related

- → `_object-types.md` — All type definitions
- → `_relations.md` — Relations guide
- → `page.md` — Page type (for regular content)
- → `../plans/product-development.md` — Product development workspace
- → `../plans/project-guide.md` — Project guide workspace
