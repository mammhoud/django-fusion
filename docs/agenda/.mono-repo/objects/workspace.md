---
Object type: Workspace
Tags: workspace, projects, planning, portfolio, knowledge-graph
Status: Active
---

# Workspace — Project Hub

> **Description:** A navigable hub that groups projects, products, plans, teams, campaigns, channels, research, and delivery evidence around a shared purpose.

## Properties

| Property | Type | Description |
|---|---|---|
| `Status` | Select | Active, Paused, Archived |
| `Purpose` | Text | Why this workspace exists |
| `Backlinks` | Text | Documents linking to this hub |
| `Related Projects` | Relation → Project | Initiatives and repository work |
| `Related Products` | Relation → Product | Customer-facing products |
| `Related Plans` | Relation → Plan | Roadmaps, campaigns, sales, and operating plans |
| `Related Teams` | Relation → Team | Owners and contributors |
| `Related Research` | Relation → Market Research | Evidence and discovery |
| `Related Channels` | Relation → Integration | Social, community, sales, or partner channels |
| `Tags` | Multi-select | Workspace and business labels |

## Use

Create one Workspace for a portfolio or major initiative. Use Project for a bounded initiative, Product for an offering, Plan for a time-bound or operational method, and Team for collective ownership.

## Graph

| Path | Flow |
|------|------|
| Products | Workspace → Project → Product → Edition → Feature; Product → Campaign → Channel, Sales → Commerce, Team → Person |
| Delivery | Workspace → Research → Goals → Milestones → Tasks |

## Related

- → `_object-types.md` — Type definitions
- → `_relations.md` — Relation guide
- → `../plans/project-workspace.md` — Portfolio workspace
- → `../objects/product.md` — Product object
- → `../objects/team.md` — Team object
- → `../plans/product-development.md` — Development lifecycle
