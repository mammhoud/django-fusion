---
# yaml-language-server: $schema=../schemas/page.schema.json
Object type: Feature
Tags: feature, product
Status: Published
---

# Feature — Product Capabilities & Editions

> **Type:** Feature ✨
> **Layout:** Page
> **Description:** Product capabilities, edition-specific implementations, and feature comparisons across the Structa Cloud platform.

---

## Properties

| Property | Type | Options | Description |
|----------|------|---------|-------------|
| `Status` | Select | Planned, In Development, Complete, Deprecated | Feature lifecycle |
| `Edition` | Relation → Edition | — | Which edition(s) include this |
| `Priority` | Select | Low, Medium, High, Critical | Importance level |
| `Tags` | Multi-select | — | Cross-cutting labels |
| `Depends On` | Relation → Feature | — | Prerequisite features |
| `Implementation` | Relation → Guide | — | Guide that implements this feature |
| `Related Goals` | Relation → Goal | — | Strategic goals this serves |
| `Related Milestones` | Relation → Milestone | — | Milestone this is part of |
| `Related API` | Relation → API | — | API endpoints this exposes |

---

## Usage in Knowledge Graph

```
Feature ✨
    ├── Edition ──────────→ Edition 📦
    ├── Related Goals ────→ Goal 🎯
    ├── Related Milestones → Milestone 🏁
    ├── Related API ──────→ API 📡
    ├── Implementation ───→ Guide 📘
    └── Depends On ───────→ Feature ✨
```

---

## Related

- → `_object-types.md` — All type definitions
- → `_relations.md` — Relations guide
- → `../features/_index.md` — Features directory
