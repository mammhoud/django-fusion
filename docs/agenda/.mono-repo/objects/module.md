---
Object type: Module
Tags: module, library, package, reusable, component
Status: Active
---

# Module — Reusable Library & Package

> **Description:** A reusable code package or library within the repository that enables code sharing and separation of concerns.

## Properties

| Property | Type | Description |
|---|---|---|
| `Status` | Select | Active, Archived, Deprecated |
| `Type` | Select | Library, Package, Plugin, Extension, Tool |
| `Version` | Text | Current version |
| `Dependencies` | Relation → Module | Required modules |
| `Related Repositories` | Relation → Repository | Where the module lives |
| `Related Projects` | Relation → Project | Projects using the module |
| `Related Documentation` | Relation → Documentation | Module docs |
| `Tags` | Multi-select | Cross-cutting labels |

## Use

Document the module's responsibility, consumers, and version. Real examples: `libs/django-fusion` (shared Django/Wagtail component framework), the Formints design-system package, and legacy `ceptor-ai` (removed 2026-08 — record as Archived with the replacement).

## Graph

Module → Related Repositories → Repository · Module → Related Projects → Project.

## Related

- → `_object-types.md` — Type registry
- → `_relations.md` — Relation guide
- → `../modules/_index.md` — Modules directory
- → `repository.md` — Repository object type