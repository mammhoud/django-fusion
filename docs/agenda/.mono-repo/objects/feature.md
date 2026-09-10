---
Object type: Feature
Tags: feature, product, capability
Status: Active
---

# Feature — Product Capability

> **Description:** A customer-facing capability with a defined outcome, edition scope, priority, dependencies, and delivery evidence.

## Properties

| Property | Type | Description |
|---|---|---|
| `Status` | Select | Planned, In Development, Complete, Deprecated |
| `Related Editions` | Relation → Edition | Editions that include this capability |
| `Priority` | Select | Low, Medium, High, Critical |
| `Tags` | Multi-select | Cross-cutting labels |
| `Depends On` | Relation → Feature | Prerequisite capabilities |
| `Implementation` | Relation → Guide | Operating or implementation guide |
| `Related Goals` | Relation → Goal | Strategic outcomes served |
| `Related Milestones` | Relation → Milestone | Delivery checkpoint |
| `Related APIs` | Relation → API | API contracts exposed or consumed |
| `Related Products` | Relation → Product | Products containing the capability |

## Use

Describe the customer or operator outcome first. Link implementation, APIs, product editions, plans, and evidence instead of copying source code into the object.

## Graph

Product → Feature → Related Editions → Edition, expanded to Guide, API, Plan, Goal, Milestone, and Release.

## Related

- → `_object-types.md` — Type definitions
- → `_relations.md` — Relations guide
- → `../features/_index.md` — Features directory
- → `../products/formint-pos.md` — Current product example
