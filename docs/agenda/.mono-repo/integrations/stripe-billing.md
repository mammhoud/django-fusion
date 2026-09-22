---
Object type: Integration
Tags: integration, payment-gateway, stripe, billing
Status: In Progress
Category: Payment
Provider: Stripe
Related Products: loop-crm
Related Features: billing-features
Related Plans: pricing-plans
Related APIs: billing-apis
---

# Stripe Billing — Subscription & Usage Payments

> **Description:** Subscription plans (Free/Pro/Enterprise), usage-based billing, Stripe webhooks, and invoice generation for Loop-CRM (`apps/billing`).

## Method

- Plan + BillingAccount (1—1 workspace) + Seat models
- Stripe webhooks update plan/account state
- Invoice generation per billing cycle

## Use case

Workspace owner subscribes, seats grant users, webhooks keep the local billing state in sync.

## Auth type

- Stripe API keys + webhook signature verification

## Evidence

- Case study: `../../case-studies/stripe-billing.md` (3 diagrams)
- Status: In Progress

## Related

- → `social-publishing.md` — Related product surface
- → `../apis/_index.md` — Billing API road
- → `../objects/integration.md` — Integration object type