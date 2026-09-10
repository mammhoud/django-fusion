---
Object type: Report
Tags: report, analysis, findings, recommendations, data-analysis
Status: Active
---

# Report — Data Analysis Findings

> **Description:** A structured data analysis with methodology, findings, and recommendations that provides actionable insight.

## Properties

| Property | Type | Description |
|---|---|---|
| `Status` | Select | Draft, Published, Archived |
| `Type` | Select | Sales, Marketing, Product, Financial, Operational, Technical, User Research, Market Analysis |
| `Methodology` | Relation → Methodology | Analysis approach used |
| `Data Sources` | Relation → Any | Evidence sources |
| `Findings` | Text | What the analysis found |
| `Recommendations` | Relation → Recommendation | Suggested next steps |
| `Related Goals` | Relation → Goal | Strategic alignment |
| `Related Plans` | Relation → Plan | Plans the report informs |
| `Related Projects` | Relation → Project | Projects affected |
| `Tags` | Multi-select | Cross-cutting labels |

## Use

Structure: Data Collection → Analysis → Findings → Recommendations. Link to data sources for evidence and goals for alignment. Reports are the evidence layer behind decisions — link the decision back to the report.

## Graph

Report → Methodology → Methodology · Report → Recommendations → Recommendation · Report → Related Goals → Goal.

## Related

- → `_object-types.md` — Type registry
- → `_relations.md` — Relation guide
- → `../reports/_index.md` — Reports directory
- → `methodology.md` — Methodology object type
- → `recommendation.md` — Recommendation object type