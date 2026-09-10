---
Object type: Data Pipeline
Tags: data-pipeline, pos, revenue, ingestion
Status: Active
Type: Event-driven
Source: Formint POS
Destination: Loop-CRM finance ledger
Schedule: On push (POS events)
Related Reports: product-metrics
Related Dashboards: loop-crm-revops
---

# POS → Loop-CRM Revenue Ingestion

> **Description:** POS sales, items, and payments flow from Formints into the Loop-CRM ledger idempotently and tenant-isolated.

## Flow

1. POS pushes to `POST /apis/pos/ingest/sales/` (X-API-Key + HMAC)
2. Idempotency key dedupes retries
3. `PosSale`/`PosSaleItem`/`PosPayment` written in one transaction
4. Refunds net into the revenue trend
5. RevOps dashboard reads the split

## Failure handling

- HMAC/API-key failures → 401, nothing written
- Duplicate keys → 200 `{"status": "duplicate"}`
- Retries idempotent by design

## Related

- → `webhook-delivery.md` — Retry pattern
- → `../apis/loop-crm-pos-api.md` — API contract
- → `../integrations/pos-revenue-ingestion.md` — Integration object
- → `../objects/data-pipeline.md` — Data Pipeline object type