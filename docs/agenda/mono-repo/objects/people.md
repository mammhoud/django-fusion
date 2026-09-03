---
Object type: Person
Tags: person, people, team, ownership, contributor
Status: Active
---

# Person — Team Member & Contributor

> **Description:** An individual contributor, owner, stakeholder, advisor, author, or partner connected to work and decisions.

## Properties

| Property | Type | Description |
|---|---|---|
| `Status` | Select | Active, Inactive, Archived |
| `Role` | Select | Developer, Designer, Product, Marketing, Sales, Support, Manager, Contributor, Stakeholder |
| `Email` | Email | Work contact where appropriate |
| `Member Of` | Relation → Team | Teams and workstreams |
| `Assigned Tasks` | Relation → Task | Assigned delivery work |
| `Owned Plans` | Relation → Plan | Accountable plans |
| `Owned Products` | Relation → Product | Product responsibility |
| `Authored Posts` | Relation → Blog/Post | Published content |
| `Made Decisions` | Relation → Decision | Architecture or product decisions |
| `Tags` | Multi-select | Role and organization labels |

## Use

Use one Person object per individual. Keep private personal information outside the knowledge graph; store only work context needed for ownership, collaboration, and attribution. Use Team for groups, not duplicate person records.

## Related

- → `_object-types.md` — Type definitions
- → `_relations.md` — Relation guide
- → `team.md` — Team object type
- → `../plans/team.md` — Team operating plan
- → `../plans/project-workspace.md` — Workspace hub
