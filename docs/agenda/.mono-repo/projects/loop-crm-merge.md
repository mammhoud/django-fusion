---
Object type: Project
Tags: project, loop-crm, crm, social, merge
Status: In Development
Related Workspace: workspace
Related Products: loop-crm
Related Teams: product, engineering
Related Plans: merge-plan
Related Milestones: formint-finance-integration, demo-state-gap-fixing, twenty-postiz-dna
---

# Loop-CRM Merge — Unified CRM + Social Scheduling

> **Description:** Merge CRM, marketing/social scheduling, POS finance, and billing into one workspace product (`projects/loop-crm/`) with a Django backend and Astro frontend.

## Outcome

One workspace where RevOps sees POS revenue, deals, attributed revenue, social publishing, and billing in a single tenant-scoped product.

## Scope and gates

- In scope: CRM (companies, contacts, pipelines, deals), marketing (channels, campaigns, posts, analytics), POS ledger ingestion, finance (invoices, payments, revenue events), attribution, billing, AI operations, webhooks.
- Out of scope: multi-product unrelated to Loop-CRM; legacy `precis-lms` paths.
- Completion evidence: backend 255+ tests green, frontend pages served, deployed `crm.structa.cloud` preview, API surface on `/apis/*` roads.

## Milestones (✅ Shipped)

- Formint finance integration — POS revenue ingestion + workflow actions
- Demo state & auth gap fixing — demo-ready preview
- Twenty/Postiz DNA research — visual language + merged-product validation

## Related

- → `../plans/_index.md` — Delivery plans
- → `../../feature-tracking.md` § Loop-CRM — Milestone records
- → `../../../plans/loop-crm/merge-plan.md` — Merge plan (active)
- → `../../../plans/loop-crm/wagtail-landing-plan.md` — Landing plan (active)
- → `../objects/project.md` — Project object type