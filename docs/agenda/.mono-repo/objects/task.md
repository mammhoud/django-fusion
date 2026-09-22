---
# yaml-language-server: $schema=../schemas/task.schema.json
Object type: Task
Tags: task
Status: Published
---

# Task — Implementation Backlog & Sprint Work

> **Type:** Task ✅
> **Layout:** Task
> **Description:** Implementation work items — bugs, features, chores, and spikes tracked across sprints and milestones.

---

## Properties

| Property | Type | Options | Description |
|----------|------|---------|-------------|
| `Status` | Select | Backlog, In Progress, Done, Blocked, Cancelled | Current state |
| `Priority` | Select | Low, Medium, High, Critical | Importance level |
| `Edition` | Relation → Edition | — | Which edition(s) this affects |
| `Assignee` | Relation → Person | — | Who is working on this |
| `Depends On` | Relation → Task | — | Prerequisite tasks |
| `Related Goals` | Relation → Goal | — | Strategic goal this serves |
| `Related Milestones` | Relation → Milestone | — | Milestone this is part of |
| `Related Features` | Relation → Feature | — | Feature this implements |
| `Related Sprints` | Relation → Sprint | — | Sprint this is assigned to |
| `Tags` | Multi-select | — | Cross-cutting labels |
| `Estimated Hours` | Number | — | Estimated effort |
| `Actual Hours` | Number | — | Actual effort spent |

---

## Usage in Knowledge Graph

| Relation | Target |
|----------|--------|
| Edition | Edition |
| Assignee | Person |
| Depends On | Task |
| Related Goals | Goal |
| Related Milestones | Milestone |
| Related Features | Feature |
| Related Sprints | Sprint |

---

## Related

- → `_object-types.md` — All type definitions
- → `_relations.md` — Relations guide
- → `../tasks/_index.md` — Tasks directory
