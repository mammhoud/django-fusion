# 📋 docs/agenda/ — Project Agenda System

> Team tracking, case studies, task management, meeting agendas, and project completion checklists for Structa Cloud products.

## What's in this directory

| File | Purpose |
|------|---------|
| **`MAIN.md`** | Hub and index — how everything connects |
| **`feature-tracking.md`** | Feature lifecycle: Proposed → Prioritized → In Progress → Review → Shipped |
| **`case-studies.md`** | Real implementation case studies with mermaid architecture diagrams |
| **`task-tracking.md`** | Sprint task board — assignees, status, due dates |
| **`team-notes.md`** | Meeting notes, decisions, blockers — the team's written memory |
| **`meeting-agenda.md`** | Templates for sprint planning, standup, review, retro, feature review, closeout |
| **`completion-checklist.md`** | Project closeout checklist — definition of done + sign-off |
| **`INDEX.md`** | Blinko-style index (legacy pointer) |

## Quick start

```
New feature? → feature-tracking.md
New task? → task-tracking.md
Meeting? → meeting-agenda.md (copy template) + team-notes.md (record notes)
Feature shipped? → case-studies.md (write case study with diagram) + feature-tracking.md (update status)
Project done? → completion-checklist.md (run through it) + team-notes.md (record decision)
```

## How it connects to the rest of docs/

```
docs/agenda/MAIN.md
├── docs/agenda/feature-tracking.md ──→ docs/features/feature-roadmap.md
├── docs/agenda/case-studies.md ──────→ docs/plans/README.md
├── docs/agenda/task-tracking.md ─────→ docs/features/feature-roadmap.md
├── docs/agenda/team-notes.md ───────→ docs/plans/README.md (major decisions)
├── docs/agenda/meeting-agenda.md ───→ docs/agenda/task-tracking.md
└── docs/agenda/completion-checklist.md ──→ docs/agenda/feature-tracking.md
                                                           → docs/agenda/case-studies.md
                                                           → docs/plans/README.md
```

## Anytype inspiration

This agenda system was designed with Anytype's object-based knowledge model in mind:

| Anytype concept | Agenda equivalent |
|----------------|-------------------|
| **Object** | A task, a feature, a case study, a meeting note |
| **Type** | Feature, Task, Case Study, Meeting Note — the category |
| **Properties** | Status, Assignee, Priority, Due Date, Sprint — the metadata |
| **Links** | Feature → Case Study, Task → Feature, Meeting → Decision |

Just like Anytype says: "Everything is an Object. Objects ask 'what does this relate to?'" — our agenda entries are objects that link to each other, not files stuffed into folders.

See: [Anytype Objects](https://doc.anytype.io/anytype/create/objects), [Anytype Types](https://doc.anytype.io/anytype/organize/types), [Anytype Properties](https://doc.anytype.io/anytype/organize/properties)

## Diagrams

All architecture and flow diagrams use mermaid. Patterns:

- `graph LR/TB` — architecture and data flow
- `sequenceDiagram` — request/response sequences
- `stateDiagram-v2` — status lifecycles
- `erDiagram` — data models

Test diagrams with `npm run validate-content` in `docs/docus/`.

## Maintenance

- **Owner:** Workspace / Product leads
- **Review cadence:** Per sprint + major release gates
- **Add entries when:** Features ship, tasks complete, meetings happen, decisions are made
- **Archive when:** Projects close (follow `docs/plans/document-lifecycle.md`)

---

## Remarks & Notes

- This is a working system, not a bureaucratic overhead — if a template isn't serving the team, adapt it
- The most valuable output is the case studies with mermaid diagrams — they're the team's institutional memory
- Link everything that relates to everything else — isolated entries lose their value
- Keep entries current — stale tracking is worse than no tracking

<!-- AI-generated: review needed -->
