---
# yaml-language-server: $schema=../schemas/milestone.schema.json
Object type: Milestone
Tags: milestone, release
Status: Published
---

# Milestone — Key Checkpoints & Release Markers

> **Type:** Milestone 🏁
> **Layout:** Milestone
> **Description:** Delivery checkpoints and release markers — tracking progress from planned to reached with clear criteria.

---

## Properties

| Property | Type | Options | Description |
|----------|------|---------|-------------|
| `Status` | Select | Planned, In Progress, Reached, Delayed, Cancelled | Current state |
| `Due Date` | Date | — | Target completion date |
| `Completed Date` | Date | — | Actual completion date |
| `Related Plan` | Relation → Plan | — | Parent plan |
| `Related Release` | Relation → Release | — | Release tied to this milestone |
| `Related Goals` | Relation → Goal | — | Strategic goals this serves |
| `Related Tasks` | Relation → Task | — | Tasks to complete this milestone |
| `Related Features` | Relation → Feature | — | Features delivered at this milestone |
| `Tags` | Multi-select | — | Cross-cutting labels |

---

## Usage in Knowledge Graph

```
Milestone 🏁
    ├── Related Plan ──────→ Plan 📋
    ├── Related Release ───→ Release 🚀
    ├── Related Goals ─────→ Goal 🎯
    ├── Related Tasks ─────→ Task ✅
    └── Related Features ──→ Feature ✨
```

---

## Related

- → `_object-types.md` — All type definitions
- → `_relations.md` — Relations guide
- → `../milestones/_index.md` — Milestones directory
