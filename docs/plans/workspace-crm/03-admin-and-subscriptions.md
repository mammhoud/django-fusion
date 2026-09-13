# M3 — Admin surfaces (Unfold + Wagtail) & landing subscriptions

> **Status:** Proposed — awaiting review · **Owner:** Mahmoud · **Validator:** Moustafa
> **Owning products:** `projects/loop-crm/` · landing surfaces (`projects/precis/`)
> **Depends on:** [M1](01-multi-tenant-domain-schemas.md), [M2](02-workspace-session-and-proxy.md)
> **Tags:** `#unfold` `#admin` `#wagtail` `#cms` `#subscriptions` `#stripe` `#landing`

<!-- AI-generated: review needed -->

## Goal

Two admin surfaces and one commercial path: a **superuser workspace admin** in
Unfold across all tenants, a **per-tenant Wagtail CMS admin** for the tenant's own
pages, and a **subscription** a visitor can start from a main landing page that
lands them in the right workspace with the right plan.

## Decisions

- **Reuse what exists.** Loop-CRM already ships Wagtail
  (`configs/default/__init__.py`) and a Stripe-shaped `apps/billing/`. This plan
  extends them rather than adding a second CMS or a second billing model.
- **Unfold precedent is `formint-pro`.** Port its dashboard-card pattern; pin to
  the version already resolved there, do not add a second major.
- **Platform admin ≠ tenant admin.** Unfold lists are superuser-only. Tenant staff
  get tenant-scoped views inside their own schema.
- **One source of truth for prices.** `Plan` in the public schema is the only
  place a price or limit lives; landings read it, never hardcode it.
- **Open decision (must be answered first):** the root `structa.cloud/` directory
  is **empty**; the deployed platform marketing surface is `precis-landing`.
  Confirm which is "the main landing page" before wiring a checkout.

## Tasks

| # | Task | Done when | Effectful |
|---|---|---|---|
| M3.1 | Unfold wiring | `unfold` loads before `django.contrib.admin`; KPI cards render: active workspaces, MRR/ARR, trials expiring, failed payments, seat utilisation, session health | no |
| M3.2 | Superuser workspace admin | Workspace, domain, plan, account, seat, registration registered; every write audited; schema create/rename stays out of admin forms (lives in M1.5) | admin writes |
| M3.3 | Per-tenant Wagtail CMS | Each tenant has its own page tree, media, and editor group at `/{workspace}/cms/`; existing seed commands still work; publish workflow draft → live | no |
| M3.4 | Subscription from the landing | Plan-driven pricing → checkout → webhook → provisioning → session → redirect into the workspace; signature-verified, idempotent by event id | **money-affecting** |
| M3.5 | Prices from `Plan` | Landing price payload equals `Plan` rows; no number hand-typed into marketing copy | no |
| M3.6 | Tests | Non-superuser blocked from platform admin; tenant staff see only their own CMS; plan gates; checkout flow; webhook idempotency; plan change revokes the live session; no price drift | no |
| M3.7 | Operator runbook | Stripe keys, webhook endpoint, test-mode runbook, refund/cancel procedure, granting a superuser — documented with placeholder names only | no |

## Gates

- A superuser sees every workspace and its billing state; a tenant editor edits
  only their own pages.
- A test-mode checkout provisions a tenant and lands the buyer inside it, logged in.
- The landing build must not require Stripe keys; the CTA renders as "contact
  sales" when keys are absent.
- Cancellation and payment failure revoke the session and make the tenant
  read-only — never deleted.

## Effectful — confirm first

- No live-mode Stripe keys, no live webhook endpoints, and no plan edits against a
  shared environment without explicit operator approval.

## Links

- → [`README.md`](README.md) — Program index
- → [`../marketing-claims.md`](../marketing-claims.md) — A public price is a claim
- → [`../loop-crm/wagtail-landing-plan.md`](../loop-crm/wagtail-landing-plan.md) — Landing pages this extends
