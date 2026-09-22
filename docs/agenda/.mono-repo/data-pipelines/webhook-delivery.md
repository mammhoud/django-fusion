---
Object type: Data Pipeline
Tags: data-pipeline, webhook, retry, dead-letter
Status: Active
Type: Event-driven
Source: Workflow actions / event sources
Destination: External webhook endpoints
Schedule: On event, with backoff retries
Related Reports: product-metrics
---

# Webhook Delivery — Retry + Dead-Letter

> **Description:** Outbound webhooks signed with HMAC, retried with exponential backoff, and dead-lettered after max attempts.

## Flow

1. Event source fires webhook → `WebhookDelivery` row (pending)
2. Signed POST (`X-Webhook-Signature: HMAC`)
3. 2xx → mark delivered; failure → schedule backoff retry
4. Max attempts → move to dead-letter queue (manual replay possible)

## Failure handling

- HMAC signing prevents tampering
- DLQ entries recorded with full payload for replay

## Related

- → `pos-revenue-ingestion.md` — Ingestion pipeline
- → `../apis/loop-crm-core-api.md` — Webhook surface
- → `../../diagrams/api-request-flows.md` § 6 — Sequence
- → `../objects/data-pipeline.md` — Data Pipeline object type