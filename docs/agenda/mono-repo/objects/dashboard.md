---
Object type: Dashboard
Tags: dashboard, visualization, real-time, metrics, kpis
Status: Active
---

# Dashboard — Metrics Visualization

> **Description:** A real-time or scheduled data visualization showing key metrics and performance indicators for quick decision-making.

## Properties

| Property | Type | Description |
|---|---|---|
| `Status` | Select | Draft, Active, Archived |
| `Type` | Select | Executive, Operational, Analytical, Strategic |
| `Data Sources` | Relation → Any | Where the metrics come from |
| `Refresh Rate` | Text | Update cadence |
| `Related Reports` | Relation → Report | Reports behind the dashboard |
| `Related Goals` | Relation → Goal | KPIs served |
| `Tags` | Multi-select | Cross-cutting labels |

## Use

Describe the audience, the KPIs shown, the data sources, and the refresh cadence. Link to reports for analysis depth and goals for KPI alignment. Real Loop-CRM example: the RevOps dashboard (`GET /apis/core/dashboard/`) — revenue trend, deal totals, POS vs deal split.

## Graph

Dashboard → Related Reports → Report → Methodology · Dashboard → Related Goals → Goal.

## Related

- → `_object-types.md` — Type registry
- → `_relations.md` — Relation guide
- → `../dashboards/_index.md` — Dashboards directory
- → `report.md` — Report object type