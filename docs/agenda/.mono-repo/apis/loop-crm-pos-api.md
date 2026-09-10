---
Object type: API
Tags: api, rest-api, pos, ingestion, webhook
Status: Active
Related Features: pos-integration, finance-ingestion
Related Integrations: pos-revenue-ingestion
Related Products: loop-crm
---

# Loop-CRM POS Ingestion API — `/apis/pos/`

> **Description:** Idempotent POS revenue ingestion from Formints — sales, items, and payments land in the finance ledger.

## Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `ingest/sales/` | POST | Idempotent sale + items + payments ingestion (`X-API-Key` + HMAC) |

## Contract notes

- Idempotency key dedupes retries (duplicate → `200 {"status": "duplicate"}`)
- HMAC signature verified before processing; invalid → `401`
- Refunds net correctly into the revenue trend
- Workspace derived from the API key; tenant isolation preserved on every write

## Related

- → `loop-crm-core-api.md` — Core road
- → `../../diagrams/api-request-flows.md` § 4 — POS ingestion sequence
- → `../objects/api.md` — API object type