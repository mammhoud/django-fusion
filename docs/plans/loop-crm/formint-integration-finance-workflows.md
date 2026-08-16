# Formint ↔ Loop-CRM — Finance, Workflows & Integrations Plan

> **Goal:** Wire the Formints POS financial ledger into the Loop-CRM finance
> module so RevOps sees POS revenue, deal revenue, and marketing attribution in
> one workspace, then broaden the CRM's workflow/automation and integration
> surface on top of that shared data.
>
> **Scope:** `projects/loop-crm/` (primary) + `projects/formints/formint-pro/`
> and `formint-cloud/` (push side). Shared substrate is
> `libs/django-fusion/` (DataToken sync tracking, Bolt API, Dramatiq tasks).
>
> **Last reviewed:** 2026-08-15

---

## 1. Integration audit — what exists today

There is **no direct Formint ↔ Loop-CRM integration yet**. The two products share
the django-fusion substrate but talk to different masters.

| Surface | Formint side | Loop-CRM side | Shared? |
|---|---|---|---|
| Sync transport | `SyncClient` → `POST {CLOUD_CRM_URL}/api/sync/push/:entity_type` with `X-API-Key` | (no ingest road today) | ❌ Formint pushes only to **formint-cloud**, not Loop-CRM |
| Sync bookkeeping | `DataToken` + `is_synced/synced_at/sync_status` on every `full_*` model | `AuditLog` (append-only) | ⚠️ both use django-fusion `DataToken` |
| Tenancy | `Organization` → `Branch` (row-level; schema-per-tenant planned in 08) | `Workspace` (row-level) | ❌ different roots |
| CRM entities | `Company`, `Pipeline`, `Stage`, `Contact`, `Deal`, `Activity`, `Note` (`pos_crm_*`) | `Company`, `Contact`, `Deal`, `Pipeline`, `PipelineStage`, `Activity` | ⚠️ same concepts, separate tables |
| Finance | `Sale` (subtotal/tax/discount/cashback/total/payment_method/status), `SaleItem`, `Customer`, `InventoryTransaction` | `Invoice`, `Payment`, `RevenueEvent` (deal/campaign-linked) | ❌ no mapping |
| Auth | session + `X-API-Key` | session + Bolt JWT (no machine API-key road) | ❌ |
| Workflows | none (POS signals/webhooks only) | `WorkflowDefinition`/`Run` + 12-action catalog + 4 templates | ❌ |

**Implication:** integrating financial data is a *new* push+ingest contract, not
a rewire of an existing pipe. Formint already has the client, the idempotency
fields, and the API-key convention; Loop-CRM needs the ingest road, the
source-reference mapping, and the finance schema extension.

---

## 2. Financial data integration — Formint POS → Loop-CRM finance

### 2.1 Data mapping

| Formint source | Loop-CRM target | Notes |
|---|---|---|
| `Organization` + `Branch` | `Workspace` | add `Workspace.source` (e.g. `{"pos_org": id}`) + unique `external_ref` |
| `Customer` | `Contact` (+ optional auto `Company`) | upsert by `external_id`; POS customer has no company concept, so auto-create a contact-level "Walk-in" company or a null-company contact |
| `Sale` (completed) | new `PosSale` + `RevenueEvent(kind="pos_sale")` | the sale's `total` becomes recognized revenue so it lands in the trend + RevOps |
| `Sale.status == refunded` | `RevenueEvent(kind="refund")` + mark `PosSale.refunded` | negative or zeroed amount, idempotent |
| `Sale.payment_method` + `total` | `Payment` (optional, method-mapped) | `cash/card/mobile/mixed` → `cash/card/other/other` |
| `SaleItem` | new `PosSaleItem` | line-item detail, `product_name`, `quantity`, `unit_price`, `line_total` |
| `Sale.tax_amount` / `discount_amount` / `cashback_amount` | `PosSale` JSON metadata | preserved verbatim for reporting; no schema loss |

Deliberately **not** forced into `Invoice`: POS sales are B2C transactions, not
deal-linked B2B invoices. A dedicated `pos` ledger keeps the invoice lifecycle
clean and lets `RevenueEvent` carry POS money into the existing trend/attribution
queries without corrupting the invoice state machine.

### 2.2 Ingestion architecture

```text
formint-pro / formint-cloud (existing SyncClient, X-API-Key)
   → POST /api/v1/ingest/pos/sales  (batch, idempotent by external_id)
   → Loop-CRM apps/pos ingest service
        ├── resolve Workspace by source reference (reject unknown)
        ├── upsert Contact / Company (by external_id)
        ├── create PosSale + PosSaleItem (get_or_create on external_id)
        ├── create RevenueEvent(kind=pos_sale|refund) + Payment (get_or_create)
        └── AuditLog write (create/ingest)
   → finance.revenue_trend picks up RevenueEvent automatically
   → RevOps dashboard shows POS + deal + attributed revenue
```

Loop-CRM keeps one contract: a workspace-scoped, idempotent `POST` that returns
per-row `{external_id, status: created|skipped|error}` so the POS can mark its
`sync_status` back to `synced`/`failed` exactly like its existing DataToken loop.

### 2.3 New models (apps/pos)

- `PosSale` — `workspace`, `contact`, `external_id` (unique per workspace),
  `sale_date`, `subtotal`, `tax_amount`, `discount_amount`, `cashback_amount`,
  `total`, `payment_method`, `status` (`completed`/`refunded`/`cancelled`),
  `source` (`formint-pro`/`formint-cloud`), `metadata` JSON, timestamps.
- `PosSaleItem` — FK `PosSale`, `product_name`, `quantity`, `unit_price`,
  `line_total`, `external_id`.
- `PosPayment` — FK `PosSale`, `amount`, `method`, `reference`, `paid_on`.
  (Or reuse `finance.Payment` via a nullable `pos_sale` FK — decided in Step 1.)
- `Workspace.source` / `Workspace.external_ref` — the POS→workspace correlation.

### 2.4 Tasks

> **Ledger decision (implemented 2026-08-14):** dedicated `apps/pos` ledger
> (`PosSale`/`PosSaleItem`/`PosPayment`) + a `RevenueEvent(kind="pos_sale")`
> bridge. `RevenueEvent.deal` is now nullable and gained `external_ref` for
> idempotency. A **refund removes** the `pos_sale` event and flips
> `PosSale.status="refunded"` (refund stays auditable in the POS ledger +
> `AuditLog`); creating a `pos_refund` revenue event + netting it in the trend
> is deferred to Step 6.

- [x] **Step 1 — Decide ledger shape.** Dedicated `pos` app + `RevenueEvent`
  bridge (decision above).
- [x] **Step 2 — Workspace correlation.** `Workspace.external_ref` (unique,
  nullable) + `source` JSON added.
- [x] **Step 3 — `apps/pos` models + migration.** `PosSale`, `PosSaleItem`,
  `PosPayment` with `external_id` unique-per-workspace constraints.
- [x] **Step 4 — Ingest service.** `apps/pos/services.py::ingest_sales(payload)`
  upsert + `RevenueEvent` bridge + `AuditLog`, idempotent.
- [x] **Step 5 — Ingest road + auth.** `POST /api/v1/ingest/pos/sales` with
  machine `X-API-Key` (`POS_INGEST_API_KEY` setting), tenant-scoped, batch
  response. (Bolt parity variant deferred.)
- [x] **Step 6 — Trend split.** `trend_aggregates()` now carries
  `pos_total`/`deal_total` per bucket (plus grand totals) on both the Django
  and Bolt roads; the RevOps card renders a stacked Deal/POS split. Refunds
  net by *removing* the `pos_sale` event (a refunded sale contributes zero),
  so no separate `pos_refund` revenue event is needed.
- [x] **Step 7 — POS push side.** New `formint-pro/server/services/pos_ingest.py`
  (`serialize_sale` → Loop-CRM ingest shape, `PosIngestClient.collect_pending/push`,
  and `push_pending_sales`) POSTs completed/refunded sales to
  `/api/v1/ingest/pos/sales/` with `X-API-Key` and marks each row's
  `sync_status` from the per-row response (`synced`/`failed`; missing rows stay
  `pending` for retry). Reconciling uses queryset `.update()` so the
  `flag_for_sync` post-save signal can't immediately re-flag an acknowledged
  row. Wired into `BranchSyncScheduler._sync_cycle` via a best-effort
  `_push_loop_ingest()` (no-op when `LOOP_CRM_URL`/`LOOP_CRM_INGEST_API_KEY`/
  `LOOP_CRM_WORKSPACE_REF` are unset). Tests in `server/tests/test_pos_ingest.py`
  (10) cover shape, collection, push, per-row error, and offline/unconfigured.
  (Not `handlers.py` — that module is deprecated Robyn legacy.)
- [x] **Step 8 — Tests.** API-key auth, unknown-workspace 404, idempotent
  re-push, refund reconciliation, tenant-scoped trend rollup (`apps/pos/tests.py`).

---

## 3. More workflows — CRM automation expansion

### 3.1 New workflow actions (extend `WORKFLOW_ACTION_CATALOG` + `execute_action`)

| Action id | Module | Behavior |
|---|---|---|
| `mark_invoice_overdue` | finance | set `Invoice.status=overdue` when past due and unpaid |
| `record_payment` | finance | create `Payment` + advance invoice to paid/partially_paid |
| `reconcile_pos_sale` | pos | bridge an ingested `PosSale` → `RevenueEvent` + `Payment` |
| `send_email` | workspace | real SMTP/Dramatiq email (replaces deferred notify) |
| `send_slack` | workspace | webhook/API post to a configured Slack channel |
| `call_webhook` | workspace | outbound webhook with signed payload + retry |
| `create_follow_up_task` | crm | create a due-dated `Activity(type=task)` for the owner |
| `refresh_analytics` (real) | marketing | promote from deferred → concrete provider fetch |

### 3.2 New workflow templates (extend `WORKFLOW_CATALOG`)

- `invoice-dunning` — trigger `invoice.due_date_passed` → `mark_invoice_overdue`
  + `send_email` + `create_follow_up_task`.
- `payment-received` — trigger `payment.created` → `record_payment` +
  `update_campaign_roi` + `notify_revops`.
- `pos-revenue-reconciled` — trigger `pos_sale.ingested` → `reconcile_pos_sale`
  + `recalculate_attribution` + `update_campaign_roi`.
- `contact-nurture` — trigger `contact.created` → `assign_owner` +
  `create_activity` + `send_email` (welcome sequence).

### 3.3 Tasks

- [x] **Step 1 — Action catalog.** 8 new actions added (`mark_invoice_overdue`,
  `record_payment`, `reconcile_pos_sale`, `create_follow_up_task`, `send_email`,
  `send_slack`, `call_webhook`, and a real `refresh_analytics`).
- [x] **Step 2 — Action implementations.** Concrete, tenant-scoped branches in
  `workflow_actions.py::execute_action`; idempotent where possible; `deferred`
  only when a connector/webhook is genuinely unconfigured.
- [x] **Step 3 — Template catalog.** 4 templates added + seeded as global
  `WorkflowDefinition` rows (migration `core.0008`).
- [x] **Step 4 — Triggers.** `Invoice.post_save` (dunning, loop-guarded),
  `Payment.post_save`, `Contact.post_save` via `apps/core/signals.py`, and
  `PosSale` ingest in `apps/pos/services.py`.
- [x] **Step 5 — Tests.** `apps/core/test_workflow_actions.py` — 29 tests over
  each action's completed/skipped/deferred paths, cross-tenant isolation, and
  the post-save triggers.

> **Loop-safety note (implemented 2026-08-15):** the `payment-received` template
> runs `update_campaign_roi` + `notify_revops` rather than `record_payment`, and
> `contact-nurture` runs `assign_owner` + `send_email` rather than
> `create_activity` — otherwise a workflow action creating a `Payment` (or
> requiring a deal on a contact) would re-trigger its own signal. `invoice-
> dunning` only fires while the invoice is `issued`/`partially_paid` and past
> due, so the workflow marking it `overdue` cannot loop.

---

## 4. Integrations — connectors & external surfaces

### 4.1 Prioritized integration list

1. **Outbound webhooks** — signed (`HMAC`) events for `deal_won`,
   `post_published`, `payment_received`, `pos_sale_ingested`; retry + dead-letter.
2. **Email (SMTP/provider)** — transactional templates for dunning, welcome,
   and approval notifications via Dramatiq.
3. **Slack** — channel notifications for RevOps/approval events.
4. **Accounting export** — CSV/JSON export of invoices + payments + POS revenue
   (reuse the `exports` pattern already in Standard/Pro).
5. **Remaining social adapters** — Instagram/Facebook/TikTok/YouTube/Reddit/
   WhatsApp behind `SocialConnector` (6 remaining catalog entries; Discord and
   Slack are now real incoming-webhook publishers).
6. **Bidirectional POS sync** — optional push-back of Loop-CRM contacts/deals
   into formint-cloud (reverse of Section 2), behind a consent flag.

### 4.2 Tasks

- [x] **Step 1 — Webhook model + delivery.** `Webhook` (workspace, url, secret,
  events) + `WebhookDelivery` (queued/succeeded/failed/dead) + Dramatiq
  `deliver_webhook` with `X-Loop-Signature` HMAC + exponential backoff (3
  attempts → dead letter). `dispatch_webhooks` is wired into `deal_won`,
  `post_published`, `payment_received`, and `pos_sale_ingested`; the
  `webhooks` resource is CRUD-ed on both API roads (secret never projected).
- [x] **Step 2 — Email connector.** `apps/core/integrations.EmailConnector`
  (SMTP first) wired into the `send_email` action.
- [x] **Step 3 — Slack connector.** `apps/core/integrations.SlackConnector`
  wired into the `send_slack` action; the shared `post_json`/`sign_payload`
  helpers in `apps/core/webhooks.py` replace the inline copies.
- [x] **Step 4 — Accounting export.** `apps/finance/export.py` + `GET
  /api/v1/finance/export/?kind=invoices|payments|pos_revenue&format=csv|json`,
  workspace-scoped, attachment-served CSV.
- [x] **Step 5 — Social adapters.** The 8 catalog platforms each have a named
  adapter; Discord and Slack are promoted to real incoming-webhook publishers
  (no OAuth — the webhook URL is the credential), leaving 6 credential-gated
  `CatalogOnlyConnector`s (see `apps/marketing/connector_adapters.py`).
- [x] **Step 6 — Tests.** `apps/core/test_webhooks.py` (HMAC + retry +
  dead-letter + connectors + secret hiding) and `apps/finance/test_export.py`
  (CSV/JSON shape, tenant scoping).

---

## 5. Sequencing & verification

1. **Finance ingestion (Section 2)** — highest value; unlocks every downstream
   workflow and the RevOps view. Shippable independently.
2. **Finance workflows (Section 3)** — build on the ingested data (`dunning`,
   `payment_received`, `pos_revenue_reconciled`).
3. **Integrations (Section 4)** — webhooks/email/Slack make the workflows
   externally observable; social adapters are independent.

Verification:

```bash
cd projects/loop-crm/backend
make check && make test        # tenant isolation + ingest + workflow action tests

cd projects/formints/formint-pro/server
# pos_sales push test + existing data-sync/webhook suites
unset DJANGO_SETTINGS_MODULE; .venv/bin/python -m pytest tests/test_pos_ingest.py tests/test_scheduler_outbox.py -q
```

Every new read/write stays workspace-scoped through `apps/core/tenancy.py` and
the `apps/core/resources.py` registry; no unscoped FK is accepted. Machine
ingestion is API-key gated, never session-gated.

## Related

- [`merge-plan.md`](merge-plan.md) — Loop-CRM architecture + roadmap
- [`../../../projects/formints/formint-pro/server/README.md`](../../../projects/formints/formint-pro/server/README.md)
- [`../../../docs/plans/editions/README.md`](../../editions/README.md) — Formints editions index
