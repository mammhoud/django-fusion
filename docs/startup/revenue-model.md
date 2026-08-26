---
title: Revenue Model — Streams & Projections 🔒
description: Revenue streams, pricing strategy, ARR projections, and unit economics (CAC/LTV/churn/gross margin) for the Structa Cloud portfolio. All figures are directional planning inputs.
navigation:
  title: Revenue model 🔒
  icon: i-lucide-chart-line
object:
  type: "private-revenue"
  id: "docs.startup.revenue-model"
attributes:
  source_path: "startup/revenue-model.md"
  canonical_route: "/docs/en/startup/revenue-model"
  source_of_truth: "repository-markdown"
  owner: "workspace"
  status: "maintained"
  access: "private"
tags:
  - structa-cloud
  - startup
  - revenue
  - pricing
  - arr
  - unit-economics
  - private
links:
  - label: "Startup home 🔒"
    to: "/startup"
    icon: "i-lucide-rocket"
  - label: "Pricing & offers 🔒"
    to: "/startup/pricing"
    icon: "i-lucide-tags"
  - label: "Plan & launch 🔒"
    to: "/startup/plan"
    icon: "i-lucide-map"
---

# 💹 Revenue Model — Streams & Projections 🔒

> **Internal only.** How Structa Cloud makes money. All figures are 🔴/🟡
> directional planning inputs, not commitments — validate before investor or
> board use. The price book itself lives in [`PRICING.md`](PRICING.md); this
> document holds the commercial structure and projections.

<!-- AI-generated: review needed -->

## 1. Revenue streams

| # | Stream | What it is | Where it maps |
|---|--------|------------|---------------|
| 1 | SaaS subscriptions | Monthly/annual fees for Loop-CRM and Precis modules | [`PRICING.md`](PRICING.md) §2 + §6 |
| 2 | Enterprise licensing | Custom contracts for large organizations, universities, government | `PLAN.md` target segments |
| 3 | White-label / OEM | Reseller and embedding fees | `PRICING.md` §6 (white-label/OEM) |
| 4 | AI usage fees | Additional AI tokens/agents (Syntara + MCP tools) | `syntara.md` strategy |
| 5 | Marketplace | Commission on third-party integrations and templates | vision |
| 6 | Professional services | Implementation, training, custom development | `PRICING.md` §4 + `SALES.md` |

## 2. Pricing strategy

- **Freemium** — Lite plans to attract users (Loop-CRM Lite, Precis CMS Lite).
- **Per-user / per-learner** pricing aligned with value (LMS per active learner).
- **Module-based add-ons** to grow with customer needs.
- **Annual discounts** (~20% off) and **volume discounts** (LMS 500+ learners).
- **Custom quotes** for enterprise (annual contract, dedicated support).

> Discount policy details (launch offers, floor pricing) live in `PRICING.md` §3.

## 3. Financial projections (example, 🔴)

| Year | ARR (USD) | Customers | Notes |
|------|-----------|-----------|-------|
| 1 | $500k | 200 SMB + 5 enterprise | Focus on regional sales |
| 2 | $2M | 800 SMB + 20 enterprise + 10 universities | Expand LMS/research |
| 3 | $6M | 2,500 SMB + 100 enterprise | International expansion |
| 4 | $15M | 6,000 SMB + 300 enterprise | Scale marketplace |

> These are model inputs, not targets agreed in `PLAN.md` — keep in sync with
> `PLAN.md` goal metrics (3–5 deals Q4, $2–5k MRR) when reconciling.

## 4. Unit economics (🔴)

| Metric | SMB | Enterprise |
|--------|-----|-----------|
| CAC | ~$500–1,000 | $5k+ |
| LTV | ~$3,000 | $100k+ |
| Churn | <5% annually (professional plans) | contract-based |
| Gross margin | >80% for SaaS | >80% for SaaS |

> **Research needed:** validate CAC/LTV against real pipeline once `PLAN.md`
> goal 1 lands; add to the startup research backlog per product.

## Remarks & Notes

- Keep the ARR table in sync with `PLAN.md` goals and `STRATEGY.md` SaaS service
  lines — one source per fact.
- Prices and projections are directional (🔴) until validated with customers.
- Private by policy — strip assumptions before external publication.
