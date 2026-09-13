---
Object type: Team
Tags: team, people, ownership, operations, collaboration
Status: Active
---

# Team — People & Responsibilities

> **Description:** A delivery, product, marketing, sales, support, or partner group with named members, ownership, and measurable responsibilities.

## Properties

| Property | Type | Description |
|---|---|---|
| `Status` | Select | Forming, Active, Paused, Archived |
| `Team Type` | Select | Product, Engineering, Marketing, Sales, Support, Leadership, Partner |
| `Mission` | Text | Outcome the team is responsible for |
| `Members` | Relation → Person | People in the team |
| `Lead` | Relation → Person | Accountable lead |
| `Related Projects` | Relation → Project | Projects served by the team |
| `Related Products` | Relation → Product | Products served by the team |
| `Related Plans` | Relation → Plan | Plans owned or delivered |
| `Related Campaigns` | Relation → Plan | Campaigns owned by the team |
| `Periodic Tasks` | Relation → Task | Recurring operating tasks the team runs |
| `Tags` | Multi-select | Team, function, market, and lifecycle labels |

## Use

Create one Team object for a durable group or a named workstream. Use Person objects for individuals and Team relations for collective ownership; do not duplicate a person as a separate team record.

Each Team object may link a set of `Periodic Tasks` (weekly, bi-weekly, monthly, quarterly) that define the recurring delivery, review, and operating rhythm for the team.

## Periodic task pattern

| Cadence | Typical Tasks |
|---|---|
| Daily | Deployments, uptime checks, support triage |
| Weekly | Sprint delivery, bug triage, pipeline review, evidence collection |
| Bi-weekly | Code review, architectural review, prioritization |
| Monthly | Metrics review, roadmap update, documentation freshness |
| Quarterly | Strategy review, claims audit, pilot decisions, dependency audit |

## Active teams

| Team | Members | Lead |
|---|---|---|
| Leadership | Mahmoud | Mahmoud |
| Product & PM | Moustafa | Moustafa |
| Front-end & UX | Yahia | Yahia |
| Data & Reporting | Asmaa | Asmaa |
| Marketing | Moustafa | Moustafa |
| Support | Dariia | Moustafa |

## Related

- → `_object-types.md` — Type definitions
- → `_relations.md` — Relation guide
- → `people.md` — Person object type
- → `people/mahmoud.md` — Mahmoud (General Manager)
- → `people/moustafa.md` — Moustafa (Product Manager)
- → `people/yahia.md` — Yahia (Front-end + UX)
- → `people/asmaa.md` — Asmaa (Data Development)
- → `people/dariia.md` — Dariia (Contributor)
- → `../plans/team.md` — Team operating plan
- → `../plans/project-workspace.md` — Workspace and project map
