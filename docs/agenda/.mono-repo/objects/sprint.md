---
# yaml-language-server: $schema=../schemas/page.schema.json
Object type: Sprint
Tags: sprint
Status: Published
---

# Sprint — Cycle Planning & Retrospective

> **Type:** Sprint 🏃
> **Layout:** Page
> **Description:** Sprint cycles — planning, execution, review, and retrospective tracking across team workflows.

---

## Properties

| Property | Type | Options | Description |
|----------|------|---------|-------------|
| `Status` | Select | Planning, Active, Completed, Cancelled | Sprint phase |
| `Sprint Number` | Number | — | Sprint identifier |
| `Start Date` | Date | — | Sprint start |
| `End Date` | Date | — | Sprint end |
| `Goals` | Text (multi-line) | — | Sprint objectives |
| `Retrospective` | Text (multi-line) | — | Lessons learned |
| `Owner` | Relation → Person | — | Scrum master/owner |
| `Related Tasks` | Relation → Task | — | Tasks in this sprint |
| `Related Goals` | Relation → Goal | — | Sprint goals |
| `Related Milestones` | Relation → Milestone | — | Related milestones |
| `Tags` | Multi-select | — | Cross-cutting labels |

---

## Usage

Sprint contains Tasks, which achieve Goals and target Milestones.

| Relation | Target |
|----------|--------|
| contains | Task |
| achieves | Goal |
| targets | Milestone |

---

## Related

- → `_object-types.md` — All type definitions
- → `task.md` — Task entity
- → `goal.md` — Goal entity
- → `milestone.md` — Milestone entity
- → `people.md` — Person/Owner entity
