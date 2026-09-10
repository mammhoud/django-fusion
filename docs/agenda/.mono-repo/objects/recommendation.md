---
Object type: Recommendation
Tags: recommendation, action-item, improvement, priority, next-steps
Status: Active
---

# Recommendation — Suggested Action

> **Description:** A suggested action or improvement based on data analysis that provides clear next steps.

## Properties

| Property | Type | Description |
|---|---|---|
| `Status` | Select | Proposed, Prioritized, Accepted, Implemented, Declined |
| `Priority` | Select | Low, Medium, High, Critical |
| `Impact` | Select | Low, Medium, High |
| `Effort` | Select | Low, Medium, High |
| `Related Insights` | Relation → Insight | Evidence behind the recommendation |
| `Related Goals` | Relation → Goal | Strategic alignment |
| `Related Actions` | Relation → Task | Implementation tasks |
| `Tags` | Multi-select | Cross-cutting labels |

## Use

State the recommended action, its rationale (linked insights), priority, impact/effort, and the tasks that implement it. The `../../../recommendations.md` registry is the repo-level home for prioritized recommendations.

## Graph

Recommendation → Related Insights → Insight · Recommendation → Related Actions → Task.

## Related

- → `_object-types.md` — Type registry
- → `_relations.md` — Relation guide
- → `../recommendations/_index.md` — Recommendations directory
- → `insight.md` — Insight object type