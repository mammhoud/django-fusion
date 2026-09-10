---
Object type: Project
Tags: project, initiative, bounded, outcome-driven
Status: Active
---

# Project — Bounded Initiative

> **Description:** A bounded initiative with an outcome, scope, milestones, delivery plans, and accountable owners. Projects have clear start and end dates.

## Properties

| Property | Type | Description |
|---|---|---|
| `Status` | Select | Planning, Active, Monitoring, Complete, Cancelled |
| `Start Date` | Date | When work begins |
| `End Date` | Date | When the project closes |
| `Owner` | Relation → Person | Accountable individual |
| `Related Workspace` | Relation → Workspace | Parent portfolio hub |
| `Related Products` | Relation → Product | Products affected |
| `Related Teams` | Relation → Team | Delivery teams |
| `Related Plans` | Relation → Plan | Delivery plans |
| `Related Goals` | Relation → Goal | Strategic outcomes |
| `Related Milestones` | Relation → Milestone | Progress checkpoints |
| `Related Features` | Relation → Feature | Capabilities delivered |
| `Related Releases` | Relation → Release | Released versions |
| `Tags` | Multi-select | Cross-cutting labels |

## Use

State the bounded outcome, in/out of scope, completion evidence, and accountable owner. Link to the workspace for portfolio view and milestones for progress. Projects that close follow the plans → milestones contract: finished work is recorded as ✅ Shipped milestones.

## Graph

Workspace → Project → Product/Team → Plan → Goal → Milestone → Task.

## Related

- → `_object-types.md` — Type registry
- → `_relations.md` — Relation guide
- → `../projects/_index.md` — Projects directory
- → `workspace.md` — Workspace object type
- → `../../CONTENT_MODEL.md` — Plans → milestones reference contract