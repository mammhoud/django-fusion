# M3 — Workspace Admin (Unfold), CMS Admin (Wagtail) & Landing Subscriptions

> **Status:** Proposed — awaiting review
> **Milestone:** M3 of [Workspace CRM Program](README.md)
> **Tags:** `#unfold` `#admin` `#wagtail` `#cms` `#subscriptions` `#stripe` `#landing` `#pricing`
> **Owning products:** `projects/loop-crm/` · landing surfaces (`projects/precis/`, `structa.cloud`)

<!-- AI-generated: review needed -->

## 1. Goal

Two admin surfaces and one commercial path: a **superuser workspace admin** in
Unfold across all tenants, a **per-tenant Wagtail CMS admin** for the tenant's
own pages, and a **subscription** a visitor can start from a main landing page
that lands them in the right workspace with the right plan.

## 2. Verified starting point

| Piece | Where | Gap |
|---|---|---|
| Billing backend | `loop-crm/backend/apps/billing/` — `Plan` (`stripe_price_id`), `BillingAccount` (`stripe_customer_id`, `stripe_subscription_id`), `Seat`, `gates.py` (permissive without keys), `services.py`, `views.py`, `urls.py`, `admin.py` | No self-serve path from a landing page |
| Wagtail | `loop-crm/backend/configs/default/__init__.py` L73–83 (`wagtail.admin`, `snippets`, `pages`, `images`, `documents`, `search`); `apps/pages/{models,api,blocks}.py`, `seed_builder`/`seed_pages` commands | No per-tenant page tree — one flat admin today |
| Unfold precedent | `formints/formint-pro/server/{configs,dashboard.py,formint/admin.py}`, `formint-cloud/backend` | Not used in loop-crm |
| Landings | `projects/precis/precis-landing/`, `projects/precis/precis-ctc/`, `loop-crm/frontend/src/components/landing/` | Pricing CTAs are static; no checkout |
| Prices/claims | `docs/plans/marketing-claims.md`, `docs/agenda/pricing-plans.md` | Prices also hand-maintained in marketing copy → drift risk |

**Decision needed (flagged):** the root `structa.cloud/` directory exists but is
**empty**, and the platform marketing site today is `precis-landing`. M3.5 must
confirm which surface is "the main project landing page" before adding a
checkout there, or the plan will wire a page that is not deployed.

## 3. Milestones (tasks)

### M3.1 — Unfold wiring

- Add `django-unfold` to `loop-crm/backend/requirements.txt` (pin to the version already resolved for formint-pro; do not add a second major).
- Settings: `"unfold"` before `"django.contrib.admin"`, `UNFOLD = {...}` with `SITE_TITLE`/`SITE_HEADER`/colours; keep Django admin working for anything Unfold does not register.
- Port the dashboard-card pattern from `formints/formint-pro/server/configs/dashboard.py` (`dashboard_callback`) with workspace-scoped KPI cards:

| Card | Query |
|---|---|
| Active workspaces | `Workspace.objects.filter(status="active").count()` |
| MRR / ARR | `BillingAccount` by `Plan.amount` × active subscriptions |
| Trials expiring (14d) | `BillingAccount.trial_ends_at` window |
| Failed payments | last `stripe` event state per account |
| Seat utilisation | `Seat` count vs `Plan.max_seats` |
| Session health | M2 verify 200/401 counters, handoff failures |

- **Gate:** `python manage.py check` clean; Unfold renders with existing staticfiles config.

### M3.2 — Superuser workspace admin (cross-tenant)

- Register with Unfold: `Workspace`, `WorkspaceDomain`, `Plan`, `BillingAccount`, `Seat`, `Registration`, plus read-only `AuditLog` and (from M2) session/`jti` revocations.
- **Access rule:** these are **platform-superuser only** (`is_superuser`), never tenant staff. Tenant staff get the tenant-scoped views inside their own schema.
- Making `Workspace`/`WorkspaceDomain` writable in admin is a privileged operation — every create/edit writes an `AuditLog` entry (model exists at `apps/core/models.py` L81).
- Guard the destructive paths: schema creation/rename is **not** an admin form field; it stays in the M1.5 provisioning service with an explicit confirmation step and a reversible-state note.
- Plan changes must invalidate live sessions (M2 `revoke`) so `pln`/`prd` cannot go stale.

### M3.3 — Per-tenant Wagtail CMS admin

- Split as decided in precis-dev: `wagtail.admin` stays **shared**, page/content models are **tenant** (M1 § 4). Each tenant gets its own page tree, images, documents.
- Tenant admin entry: `/{workspace}/cms/` (behind the M2 session middleware) with the `editor` group from the tenant seed; platform superusers can enter any tenant's CMS explicitly.
- `apps/pages/` gains: HomePage → landing sections (StreamField blocks already in `blocks.py`), a theme/option field that selects the tenant's theme variation (M4), and a publish workflow (draft → live) so landing edits are safe.
- Keep the existing `seed_pages` / `seed_builder` commands working — they become the tenant seed actor payload (M1.5).
- Media: per-tenant image/document collections; no cross-tenant file references.

### M3.4 — Subscription from the landing pages

```text
Landing pricing section (Plan-driven)
  → "Start" → POST /apis/billing/checkout {plan_code, workspace_name, email}
  → BillingAccount(status=pending) + Registration
  → Stripe Checkout (test keys in dev; feature-flagged off without keys)
  → webhook: checkout.session.completed / customer.subscription.updated
  → BillingAccount active + stripe_subscription_id  (= M2 `sk`)
  → M1.5 provisioning actor → tenant schema + seed
  → session issued (M2.2) → redirect to the tenant workspace
```

- Reuse `apps/billing/services.py` (`_stripe_enabled` gate) — **never** hard-fail when keys are absent; the CTA renders as "contact sales" in that case.
- Webhook handling: signature verification, idempotency by event id, replay-safe, and a stored raw payload for support.
- Post-checkout redirect target is derived server-side (no user-supplied `next`) — same rule as M2.5.
- Cancellation/dunning: `subscription.deleted` / `invoice.payment_failed` → account state + session revoke + tenant read-only (not deleted).

### M3.5 — One source of truth for prices

- `Plan` (public schema) is the only place a price/limit lives. Landings fetch
  `GET /apis/billing/plans/` at build/ISR time or via the landing's data API —
  never hardcode a number in marketing copy.
- Cross-check against `docs/plans/marketing-claims.md`: a price or limit shown
  publicly is a claim and needs the same evidence discipline (`docs/agenda/pricing-plans.md` holds targets).

### M3.6 — Tests

| Test | Asserts |
|---|---|
| `test_admin_access.py` | non-superuser cannot reach the platform admin; tenant staff only see their own CMS |
| `test_plan_gates.py` | `gates.py` blocks over-limit actions when a plan is active; permissive when Stripe is off |
| `test_checkout_flow.py` | checkout → webhook → provisioning → session, with Stripe test fixtures |
| `test_webhook_idempotency.py` | the same event twice creates one account change |
| `test_plan_change_revokes_session.py` | plan change invalidates `pln`/`prd` in a live session |
| `test_landing_prices.py` | landing price payload equals `Plan` rows (no drift) |

### M3.7 — Operator surface

- Document in `projects/loop-crm/docs/SETUP_AND_BUILD.md`: Stripe keys, webhook
  endpoint, test-mode runbook, refund/cancel procedure, and how to grant a
  superuser. No keys in the repo — `.env.example` names only.

## 4. Verification

```bash
cd projects/loop-crm/backend
python manage.py check
python manage.py test apps.billing apps.pages apps.core.test_admin_access apps.core.test_plan_gates

# Admin smoke (dev): sign in as superuser, open each Unfold list, open a tenant CMS
make dev                       # or the project's documented dev target

# Landing build must not require Stripe keys
cd projects/precis/precis-landing && make check
```

Pass criteria: a superuser sees every workspace and its billing state; a tenant
editor edits only their own pages; a test-mode checkout provisions a tenant and
lands the buyer inside it logged in.

## 5. Risks

| Risk | Mitigation |
|---|---|
| Selling from a landing that is not the deployed platform surface | M3.5 confirms the target surface first; flag `structa.cloud/` (empty) explicitly |
| Price drift between `Plan` and marketing copy | `test_landing_prices.py` + claims register |
| Unfold + Wagtail admin coexisting | Both are admin-side only; keep separate URLs (`/admin/` vs `/cms/`) and verify static assets collect |
| Writable tenant fields in a cross-tenant admin | Superuser-only, AuditedModel writes, no schema fields in forms |
| Webhook replays double-provision | Idempotency by event id + provisioning actor keyed on workspace |
| Dev/staging without Stripe keys | Gates stay permissive; checkout UI hidden; provisioning still testable via a management command |

## 6. Remarks & Notes

- "CMS admin panel with Wagtail as added at old projects" is satisfied by
  reusing loop-crm's already-installed Wagtail (L73–83) and giving it a
  per-tenant tree, rather than introducing a second CMS.
- The subscription key minted here is the `sk` claim M2 carries; M3 must call
  M2's revoke/refresh on every billing state change.
- Billing changes are money-affecting: no live-mode keys, no live webhook
  endpoints, and no plan edits against a shared environment without explicit
  operator approval.
