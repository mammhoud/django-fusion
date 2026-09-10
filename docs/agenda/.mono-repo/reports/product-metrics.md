---
Object type: Report
Tags: report, metrics, product, analytics
Status: Active
Type: Product
Methodology: evidence-led-lifecycle
Related Goals: product-goals
Related Plans: product-development
---

# Product Metrics — Evidence & KPIs

> **Description:** The metrics framework for Structa Cloud products — what to measure per product, data sources, and cadence (mirrors `../../data-analyst-plans.md`).

## Findings

| Product | Metrics | Data source |
|---|---|---|
| Loop-CRM | Workspace count, contacts, campaigns, social posts | Django + Channels + social APIs |
| Precis LMS | Enrollments, progress, completion | Wagtail + LMS models |
| Formint POS | Sales, branches, sync health | Rust/Diesel + Cloud master |
| CTC Research | Content publishes, newsletter subscribers | Wagtail |

## Recommendations

- Weekly product metrics; quarterly evidence review per `../../data-analyst-plans.md`
- Link every shipped feature to its metric

## Related

- → `../methodologies/evidence-led-lifecycle.md` — Method
- → `../dashboards/_index.md` — Dashboards
- → `../objects/report.md` — Report object type