---
Object type: Dashboard
Tags: dashboard, loop-crm, revops, kpis
Status: Active
Type: Operational
Data Sources: apps/finance, apps/crm, apps/pos
Related Reports: product-metrics
Related Goals: product-goals
---

# Loop-CRM RevOps Dashboard

> **Description:** The dashboard KPIs served by `GET /apis/core/dashboard/` — revenue trend, deal pipeline totals, and the POS vs deal revenue split.

## KPIs

| KPI | Source |
|---|---|
| Revenue trend (POS + deal split) | `RevenueEvent` + `PosSale` |
| Deal pipeline totals by stage | `crm.Deal` + `PipelineStage` |
| Attributed revenue | `attribution.AttributionTouchpoint` |

## Refresh

- On-request (dashboard API); data recomputed server-side per tenant

## Related

- → `../apis/loop-crm-core-api.md` — Dashboard endpoint
- → `../../diagrams/api-request-flows.md` § 2 — Request sequence
- → `../objects/dashboard.md` — Dashboard object type