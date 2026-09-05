---
Object type: Data Pipeline
Tags: data-pipeline, etl, automation, data-flow, integration
Status: Active
---

# Data Pipeline — Automated Data Movement

> **Description:** Automated data movement and transformation from source to destination that ensures data availability and quality.

## Properties

| Property | Type | Description |
|---|---|---|
| `Status` | Select | Draft, Active, Paused, Deprecated |
| `Type` | Select | Batch, Real-time, Streaming, Scheduled, Event-driven |
| `Source` | Relation → Any | Where data comes from |
| `Destination` | Relation → Any | Where data lands |
| `Transformations` | Text | Processing steps |
| `Schedule` | Text | Run cadence |
| `Related Reports` | Relation → Report | Reports that consume the output |
| `Related Dashboards` | Relation → Dashboard | Dashboards fed by the pipeline |
| `Tags` | Multi-select | Cross-cutting labels |

## Use

Document the source → transformation → destination chain, the schedule, failure handling, and downstream consumers. Real examples: POS → Loop-CRM revenue ingestion (idempotent, HMAC-signed), email OAuth sync, webhook delivery with retry + dead-letter.

## Graph

Data Pipeline → Related Reports → Report · Data Pipeline → Related Dashboards → Dashboard.

## Related

- → `_object-types.md` — Type registry
- → `_relations.md` — Relation guide
- → `../data-pipelines/_index.md` — Data pipelines directory
- → `report.md` — Report object type