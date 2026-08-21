---
title: Product Plan & Launch — 🔒 Private
description: Product plan, goals, target, scope, stakeholders, roadmap, launch plan and PR calendar for the Structa Cloud portfolio.
navigation:
  title: Plan & Launch 🔒
  icon: i-lucide-map
object:
  type: "private-plan"
  id: "docs.startup.plan"
attributes:
  source_path: "startup/PLAN.md"
  canonical_route: "/docs/en/startup/plan"
  source_of_truth: "repository-markdown"
  owner: "workspace"
  status: "maintained"
  access: "private"
tags:
  - structa-cloud
  - startup
  - plan
  - launch
  - roadmap
  - pr
  - private
links:
  - label: "Startup home 🔒"
    to: "/docs/en/startup"
    icon: "i-lucide-rocket"
  - label: "Pricing & offers"
    to: "/docs/en/startup/pricing"
    icon: "i-lucide-tags"
  - label: "Sales playbook"
    to: "/docs/en/startup/sales"
    icon: "i-lucide-handshake"
---

# 🗺️ Product Plan & Launch — 🔒 Private

> Internal only. One product plan for the whole portfolio: vision, goals,
> target, scope, stakeholders, roadmap, launch sequence, and the PR calendar.

<!-- AI-generated: review needed -->

## 1. Vision & mission

**Vision:** One self-hosted, open, Django + Wagtail + Astro stack that replaces
five SaaS subscriptions for training companies, medical centers, agencies, and
restaurants — with full data ownership.

**Mission (90 days):** convert the shipped platforms (Precis LMS+landing,
Loop-CRM, Syntara, Formint POS) into **sellable packages** — managed
hosting + setup + white-label customization — starting with the Precis family.

## 2. Goals (targets)

| # | Goal | Metric | Target | Horizon |
|---|------|--------|--------|---------|
| 1 | First paid clients | signed deals | 3–5 | Q4 |
| 2 | Managed-hosting revenue | MRR | $2–5k | Q4–Q1 |
| 3 | Productized delivery | deployment time | < 30 min/site | Q4 |
| 4 | Arabic/MENA market | Arabic-first sites sold | 2–3 | Q1 |
| 5 | Agency channel | active reseller partners | 2 | Q1 |

## 3. Target (who we sell to)

| Segment | Pain | Product wedge | ICP |
|---------|------|---------------|-----|
| Training academies & bootcamps | tool sprawl, per-seat SaaS costs | Precis (LMS + landing catalog) | 20–500 learners, MENA/EU |
| Medical & research centers | institutional web presence + publishing | CTC Research *(sample)* | small hospitals, research institutes (sample reference) |
| Agencies | no repeatable platform to productize | white-label Precis (CTC sample as reference) | web agencies with 5+ clients |
| Restaurants & cafes | POS cost + lock-in | Formint POS (self-hosted) | single-to-multi outlet |
| Small businesses (zero IT) | no utilities/hardware, no staff IT | full turnkey managed package | 1–20 employee businesses |

## 4. Scope

**In scope (MVP packages):**

- Managed hosting (deploy, DB, media, proxy, tasks, backups, monitoring).
- Setup & migration (content import, DNS, SSL, email config).
- White-label theming (branded catalog/landing via Wagtail + design system).
- Training & documentation (Arabic + English).
- Support tiers (L1 chat/email, L2 upgrades).

**Out of scope (phase 2+):**

- Custom software development beyond the configs/theming layer (quote separately).
- On-premise hardware procurement (we deploy to the client's server or ours).
- LTI/SCORM compliance until validated (see `precis.md` research backlog).

## 5. Stakeholders (RACI)

| Role | Who | R | A | C | I |
|------|-----|---|---|---|---|
| Founder / product owner | workspace owner | A | A | I | I |
| Engineering | monorepo maintainers | R | I | A | I |
| Sales / delivery lead | founder + agency partners | R | A | I | I |
| Client | customer | I | C | R | A |
| Reseller agency | partner | R | I | I | I |

## 6. Roadmap

| Phase | Window | Deliverables |
|-------|--------|--------------|
| P0 — Packaging (now) | Wk 1–2 | Pricing tiers, sales playbook, proposal templates, zero-utilities onboarding guide |
| P1 — Productized delivery | Wk 3–6 | Deployment scripts, `make redeploy` per site, monitoring, backup/restore runbooks |
| P2 — Managed hosting | Wk 7–10 | Billing (Stripe), per-site dashboards, SLA + status page, support desk |
| P3 — Arabic/MENA push | Wk 11–14 | Arabic site templates, RTL parity pass, Arabic sales collateral, pricing in EGP/SAR/AED |
| P4 — Agency channel | Q1 | Reseller kit, white-label partner portal, revenue-share terms |

## 7. Launch plan

### Pre-launch (now → launch)
- [ ] Finalize packages + prices (`PRICING.md`).
- [ ] Ship the zero-utilities onboarding guide (`SALES.md`).
- [ ] Record a 10-min demo video per product (Precis, Formint, Loop-CRM; CTC sample included as a reference demo).
- [ ] Stand up demo sites (structa.cloud, ctc-research.com sample) on production infra.

### Launch week
- [ ] Announce on X/LinkedIn + Arabic channels (product hunt later).
- [ ] Offer 3 launch slots at founder pricing (one per product family).
- [ ] Publish case-study posts from the demo sites.

### Post-launch (30 days)
- [ ] Collect testimonials + screenshots; publish `marketing-claims.md` updates.
- [ ] Convert demo leads; measure `PLAN.md` goal 1.

## 8. PR / public relations calendar

| When | Channel | Message |
|------|---------|---------|
| Launch | X + LinkedIn (EN/AR) | "Self-hosted LMS + site for training companies — no SaaS lock-in" |
| +1 wk | Dev communities (GitHub, HN) | open-source django-fusion + self-hosting story |
| +2 wk | Arabic tech media (EN/AR blogs) | Arabic-first learning platform for MENA training companies |
| +4 wk | Agency outreach | white-label platform for agencies (revenue share) |

> PR copy must stay evidence-backed — every claim in `marketing-claims.md`.

## Remarks & Notes

- Keep this plan's metric table in sync with `STRATEGY.md` and the per-product
  docs (`precis.md`, `precis-ctc.md`, ...) — one source per fact.
- Pricing numbers live in `PRICING.md`; sales process in `SALES.md`.
- This section is private; strip the 🔒 research backlogs before publishing.
