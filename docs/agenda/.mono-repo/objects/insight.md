---
Object type: Insight
Tags: insight, finding, pattern, observation, discovery
Status: Active
---

# Insight — Discovered Pattern

> **Description:** A discovered pattern, finding, or observation from data analysis that drives recommendations and actions.

## Properties

| Property | Type | Description |
|---|---|---|
| `Status` | Select | Draft, Validated, Superseded |
| `Confidence` | Select | Low, Medium, High |
| `Impact` | Select | Low, Medium, High |
| `Related Reports` | Relation → Report | Where the insight came from |
| `Related Goals` | Relation → Goal | Strategic impact |
| `Related Actions` | Relation → Recommendation | Actions the insight drives |
| `Tags` | Multi-select | Cross-cutting labels |

## Use

State the finding, its confidence, impact, and the report that produced it. Validate before sharing. Link to recommendations that act on it.

## Graph

Insight → Related Reports → Report · Insight → Related Actions → Recommendation.

## Related

- → `_object-types.md` — Type registry
- → `_relations.md` — Relation guide
- → `../insights/_index.md` — Insights directory
- → `report.md` — Report object type
- → `recommendation.md` — Recommendation object type