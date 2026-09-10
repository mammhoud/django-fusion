---
Object type: Integration
Tags: integration, pos, revenue, ingestion, webhook
Status: Completed
Category: Delivery
Provider: Formint POS → Loop-CRM
Related Products: formint-pos, loop-crm
Related Features: pos-integration, finance-ingestion
Related Plans: formint-pos-professional-plan
Related APIs: pos-apis
---

# POS Revenue Ingestion — Formint → Loop-CRM Ledger

> **Description:** POS revenue from Formints lands in the Loop-CRM finance ledger so RevOps sees POS, deal, and attributed revenue in one workspace.

## Method

- Idempotent `POST /apis/pos/ingest/sales/` with `X-API-Key` + HMAC-signed payloads
- `PosSale`/`PosSaleItem`/`PosPayment` ledger with idempotency keys
- Net refunds into the revenue trend; tenant isolation preserved

## Use case

POS terminal pushes sales; finance ledger updates without duplicates; RevOps reads the trend split (POS vs deal).

## Auth type

- API key + HMAC signature (server secret)

## Evidence

- ✅ Shipped — milestone in `../../feature-tracking.md` § Loop-CRM (Formint finance integration)
- 29 workflow-action tests + connector tests green

## Related

- → `../apis/loop-crm-pos-api.md` — POS API road
- → `../objects/integration.md` — Integration object type