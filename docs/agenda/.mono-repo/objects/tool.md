---
Object type: Tool
Tags: tool, method, use-case, product, desktop
Status: Published
---

# Tool — Responsibility & Use Case

> **Description:** A named product or platform capability described by its responsibility, method, boundary, and user outcome. It is not a code listing or dependency inventory.

## Properties

| Property | Type | Description |
|---|---|---|
| `Status` | Select | Planned, Active, Stable, Deprecated |
| `Category` | Select | Desktop, Data, Integration, Operations, Design |
| `Edition` | Relation → Edition | Edition where the tool is available |
| `Related Features` | Relation → Feature | Product capability supported |
| `Method` | Text | What the tool does and how it is used |
| `Use Case` | Text | User or operator outcome |
| `Dependencies` | Relation → Tool | Required supporting tools |
| `Tags` | Multi-select | Shared classification |

## Use

Write the tool's responsibility and a concrete user scenario. Keep implementation details in repository plans or references. Use this object for a capability such as desktop notifications, a KDS window, or a sync broker—not for every function or source file.

## Related

- → `_object-types.md` — Type registry
- → `_relations.md` — Relation guide
- → `../plans/tauri-desktop.md` — Formint desktop tools
- → `edition.md` — Edition object type
