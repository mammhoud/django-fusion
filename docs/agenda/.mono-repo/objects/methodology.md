---
Object type: Methodology
Tags: methodology, framework, standard, best-practice, analysis
Status: Active
---

# Methodology — Analysis Framework & Standard

> **Description:** An analysis framework, approach, or standard used for data analysis that ensures consistency and reproducibility.

## Properties

| Property | Type | Description |
|---|---|---|
| `Status` | Select | Draft, Active, Deprecated |
| `Category` | Select | Statistical, Qualitative, Quantitative, Mixed Methods, Agile, Lean |
| `Steps` | Text | The method's procedure |
| `Tools` | Relation → Tool | Supporting tools |
| `Related Reports` | Relation → Report | Reports that used this method |
| `Related Training` | Relation → Guide | How-to training |
| `Tags` | Multi-select | Cross-cutting labels |

## Use

Document the procedure, the tools it needs, and the reports it produced. Methodologies make analysis reproducible — record the approach before the analysis. Real examples: the DIÁTAXIS documentation method, A/B experiment design, evidence-led product development lifecycle.

## Graph

Methodology → Related Reports → Report · Methodology → Tools → Tool.

## Related

- → `_object-types.md` — Type registry
- → `_relations.md` — Relation guide
- → `../methodologies/_index.md` — Methodologies directory
- → `report.md` — Report object type