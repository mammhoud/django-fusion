---
title: Sales Playbook — Requirements to Sell — 🔒 Private
description: Readiness checklist, proposal/contract checklist, zero-utilities & zero-hardware client onboarding, and delivery handover for Structa Cloud.
navigation:
  title: Sales Playbook 🔒
  icon: i-lucide-handshake
object:
  type: "private-sales"
  id: "docs.startup.sales"
attributes:
  source_path: "startup/SALES.md"
  canonical_route: "/docs/en/startup/sales"
  source_of_truth: "repository-markdown"
  owner: "workspace"
  status: "maintained"
  access: "private"
tags:
  - structa-cloud
  - startup
  - sales
  - onboarding
  - proposals
  - private
links:
  - label: "Startup home 🔒"
    to: "/startup"
    icon: "i-lucide-rocket"
  - label: "Pricing & offers"
    to: "/startup/pricing"
    icon: "i-lucide-tags"
  - label: "Plan & launch"
    to: "/startup/plan"
    icon: "i-lucide-map"
---

# 🤝 Sales Playbook — Requirements to Sell — 🔒 Private

> Internal. The readiness checklist before taking money, the proposal/contract
> checklist, the **zero-utilities / zero-hardware** client onboarding path, and
> the delivery handover.

<!-- AI-generated: review needed -->

## 1. Requirements to sell (readiness checklist)

Before selling any package, all boxes must be true:

- [ ] Package + price defined (`PRICING.md`) and a quote template exists.
- [ ] A demo site is live on production infra (structa.cloud / ctc-research.com).
- [ ] `make redeploy` works end-to-end (the delivery loop is productized).
- [ ] Backups + restore verified for the managed stack.
- [ ] Support tier + response times defined (L1 chat/email, L2 upgrades).
- [ ] Client-facing docs exist (EN + AR quickstart, admin guide).
- [ ] Every marketing claim is evidence-backed (`marketing-claims.md`).
- [ ] `PLAN.md` goal metrics have a tracking sheet.

## 2. Proposal & contract checklist

| Item | Detail |
|------|--------|
| Scope | exact deliverables from `PRICING.md` package + line items |
| Price & billing | one-time + monthly, currency, annual vs monthly, late-fee policy |
| Duration | minimum term (recommended 12 mo managed), renewal |
| IP & data | client owns content/data; we license software + provide service |
| Hosting | where it runs (our managed infra vs client server), backups SLA |
| Support | channels, hours (EN/AR), response targets, exclusions |
| Migration | what we import, source formats, who validates |
| Customization | what theming/configs are included; extra dev = separate SOW |
| Termination | notice, data export (full dump), deletion timeline |

## 3. Zero-utilities / zero-hardware clients

Clients starting with **nothing** — no domain, no email, no server, no IT
staff. The whole journey is included in **Managed** (never license-only):

| Step | What we do | Client does |
|------|------------|-------------|
| 1. Discovery | questionnaire: business, courses/content, branding, languages (AR?) | answers form (30 min) |
| 2. Domain & email | we buy/transfer domain + set up mailbox (Gmail/Workspace or self-host) | approves costs |
| 3. Infrastructure | we provision the managed stack (DB, proxy, TLS, media) | nothing |
| 4. Build | deploy site, white-label theme, migrate content, seed pages | sends content/branding files |
| 5. Training | AR/EN admin walkthrough + 1-page cheat sheets | attends 1–2 sessions |
| 6. Handover | credentials, runbook, support channel, SLA start | receives docs |

**Deliverables at handover:** admin URL + credentials (password rotation),
site URLs, backup/restore runbook, support contact, invoice schedule.

> The zero-utilities path is the highest-margin package: no client-side
> dependencies to debug, one deploy loop, recurring MRR.

## 4. Delivery handover checklist

- [ ] Production site healthy: `/health/`, `/apis/pages/`, `/static/`, `/media/`.
- [ ] TLS cert issued (Let's Encrypt) + redirects (www, http→https).
- [ ] Backups verified (restore tested once in staging).
- [ ] Monitoring + error logging active (Sentry optional).
- [ ] Client credentials handed over; admin password rotated.
- [ ] Client docs delivered (EN/AR quickstart + admin guide).
- [ ] Support ticket opened for the client; SLA clock starts.

## Remarks & Notes

- Never promise features outside the sold package — scope creep kills margins.
- Keep the questionnaire + templates in sync with `PRICING.md`.
- Private — client names and figures must never appear in public docs.
