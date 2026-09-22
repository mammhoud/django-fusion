---
title: Master Presentation — 25-Slide Executive Deck 🔒
description: Outline of the 25-slide executive presentation for Structa Cloud — company, market, product ecosystem, business model, roadmap — with the source docs each slide quotes.
navigation:
  title: Master deck 🔒
  icon: i-lucide-presentation
object:
  type: "private-presentation"
  id: "docs.startup.presentation"
attributes:
  source_path: "startup/presentation.md"
  canonical_route: "/docs/en/startup/presentation"
  source_of_truth: "repository-markdown"
  owner: "workspace"
  status: "maintained"
  access: "private"
tags:
  - structa-cloud
  - startup
  - presentation
  - investor-deck
  - private
links:
  - label: "Startup home 🔒"
    to: "/startup"
    icon: "i-lucide-rocket"
  - label: "Company profile 🔒"
    to: "/startup/company-profile"
    icon: "i-lucide-building-2"
  - label: "Product profiles 🔒"
    to: "/startup/product-profiles"
    icon: "i-lucide-boxes"
  - label: "Revenue model 🔒"
    to: "/startup/revenue-model"
    icon: "i-lucide-chart-line"
---

# 🎤 Master Presentation — 25-Slide Executive Deck 🔒

> **Internal only.** The canonical slide outline for investor/partner decks.
> Each slide links to the source doc it quotes so the deck is regenerable from
> one place. Private by policy — strip 🔒 research backlogs before presenting.

<!-- AI-generated: review needed -->

## 25-Slide Outline

| # | Slide | Source doc |
|---|-------|------------|
| 1 | Cover | [`company-profile.md`](company-profile.md) |
| 2 | Company Introduction | [`company-profile.md`](company-profile.md) |
| 3 | Vision & Mission | [`company-profile.md`](company-profile.md) |
| 4 | Market Opportunity | [`STRATEGY.md`](STRATEGY.md) §3 + [`comparison.md`](comparison.md) §3 |
| 5 | Product Ecosystem | [`product-profiles.md`](product-profiles.md) |
| 6 | Loop CRM | [`product-profiles.md`](product-profiles.md) §1 + [`loop-crm.md`](loop-crm.md) |
| 7 | Precis Platform | [`product-profiles.md`](product-profiles.md) §2 + [`precis.md`](precis.md) |
| 8 | Precis CMS | [`product-profiles.md`](product-profiles.md) §3 (🔴 vision) |
| 9 | Precis Builder | [`product-profiles.md`](product-profiles.md) §4 (🔴 vision) |
| 10 | Precis LMS | [`product-profiles.md`](product-profiles.md) §5 + [`precis.md`](precis.md) |
| 11 | Precis Research (CTC sample seed) | [`product-profiles.md`](product-profiles.md) §6 + [`precis-ctc.md`](precis-ctc.md) — CTC Research is the agentic-coding sample seed, not a product |
| 12 | AI Layer | [`syntara.md`](syntara.md) + [`docs/ai/mcp-integration.md`](../ai/mcp-integration.md) |
| 13 | Analytics Layer | vision (see product-profiles platform architecture) |
| 14 | Automation Layer | vision + [`plans/repository/precis-ctc-workflows.md`](../plans/repository/precis-ctc-workflows.md) |
| 15 | Django Fusion | [`product-profiles.md`](product-profiles.md) §7 + [`../libs/django-fusion.md`](../libs/django-fusion.md) |
| 16 | Architecture | [`../ARCHITECTURE.md`](../ARCHITECTURE.md) + [`../project-structure.md`](../project-structure.md) |
| 17 | Competitive Analysis | [`comparison.md`](comparison.md) |
| 18 | Technology Stack | [`company-profile.md`](company-profile.md) |
| 19 | Business Model | [`revenue-model.md`](revenue-model.md) |
| 20 | Pricing Strategy | [`PRICING.md`](PRICING.md) |
| 21 | Roadmap | [`PLAN.md`](PLAN.md) §6 + per-product strategy docs |
| 22 | Partnership Opportunities | [`PLAN.md`](PLAN.md) §8 + [`SALES.md`](SALES.md) |
| 23 | Investment Opportunities | [`revenue-model.md`](revenue-model.md) + [`STRATEGY.md`](STRATEGY.md) |
| 24 | Team | — (not documented yet) |
| 25 | Contact | — |

## Suggested Additional Slides

- Market opportunity per segment (CMS, LMS, Research, Website Builder) — from `comparison.md` + per-product TAM/SAM/SOM
- Competitive comparison (WordPress, Webflow, Moodle, etc.) — `comparison.md` §3
- Deployment options (SaaS, on-premise, private cloud, government) — `PRICING.md` §6 white-label/OEM
- Roadmap 2026–2028 (Phases 1–6) — `PLAN.md` §6 + `STRATEGY.md` §8 sequencing

## Remarks & Notes

- Every figure in the deck must trace back to a confidence-tagged doc; claims
  must be evidence-backed per [`docs/plans/marketing-claims.md`](../plans/marketing-claims.md).
- Mark 🔴 vision slides (CMS/Builder/Research platform, Analytics/Automation
  layers) clearly as roadmap, not shipped.
- Private by policy — produce a public variant without the 🔒 research backlogs
  and pricing assumptions.
