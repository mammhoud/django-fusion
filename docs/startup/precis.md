---
title: Precis — Market Strategy 🔒
description: Private strategy for Precis (LMS + landing) — MVP canvas, TAM/SAM/SOM, SaaS services, ideal clients, research backlog.
navigation:
  title: Precis strategy 🔒
  icon: i-lucide-graduation-cap
object:
  type: "private-strategy"
  id: "docs.startup.precis"
attributes:
  source_path: "startup/precis.md"
  canonical_route: "/docs/en/startup/precis"
  source_of_truth: "repository-markdown"
  owner: "precis-main"
  status: "maintained"
  access: "private"
tags:
  - structa-cloud
  - startup
  - precis
  - lms
  - edtech
  - saas
links:
  - label: "Startup home 🔒"
    to: "/docs/en/startup"
    icon: "i-lucide-rocket"
  - label: "Precis product docs"
    to: "/docs/en/precis"
    icon: "i-lucide-graduation-cap"
---

# 🎓 Precis — Market Strategy 🔒

> Private · Owner: `precis-main` · Confidence tags: 🟢 sourced · 🟡 estimate · 🔴 assumption

## 1. Market Strategy

- **Positioning:** For mid-size academies, bootcamps, and training companies that want a branded learning platform without SaaS lock-in, **Precis** is the open, self-hostable LMS + marketing site that runs courses, enrollment, progress, and a landing/catalog shell from one Django + Wagtail codebase.
- **Wedge:** White-labeled **course catalog + enrollment** for training companies currently selling via spreadsheets and Zoom — one platform replaces five tools.
- **Go-to-market:** Partner-led (agencies that build training sites) + direct sales to training ops leads; open-source visibility to drive inbound.
- **Moat:** Complete control (self-host), Wagtail content power, and a single unified stack (LMS + landing merged) that competitors split across products.

## 2. MVP Canvas

| Block | Answer |
|-------|--------|
| **Problem** | Training businesses juggle separate tools for courses, payments, marketing pages, and learner progress; SaaS LMS fees + per-seat pricing hurt small operators |
| **Solution** | Unified LMS + landing: Wagtail-managed catalog, course/enrollment/progress models, profile, HTMX-first UX |
| **Key metrics** | Activated learners per cohort, enrollment conversion, course completion, deployment time |
| **Unfair advantage** | Full ownership of the codebase + shared django-fusion framework; merges marketing + learning into one deployable |
| **Channels** | GitHub visibility, agency partnerships, developer communities, productized deployment service |
| **Revenue model** | Self-hosted license + support tiers; managed hosting subscription |
| **Cost structure** | Low (one Django stack, one infra footprint); docs and support are the main costs |
| **Timeline** | MVP (courses+enrollment+landing) ✅ shipped → paid first client → managed hosting tier |

## 3. TAM / SAM / SOM

| Market | Definition | Size | Confidence | Source / note |
|--------|-----------|------|------------|---------------|
| TAM | Global corporate LMS / online learning platforms | ~$20–25B (2025, global e-learning) | 🟡 | Public e-learning market reports |
| SAM | LMS for mid-size academies & training companies (EU + MENA + GCC, Arabic/English) | ~$600M–1B | 🔴 | Derived: segment share assumption |
| SOM | Year-3 obtainable: 100–300 paying training orgs | ~$1–3M ARR | 🔴 | Depends on GTM capacity; validate |

> **SOM logic:** assume 0.2–0.5% capture of SAM given partner-led sales capacity of 10–20 deals/yr. Validate with pilot cohort.

## 4. SaaS Services

| Service line | What it is | Pricing posture | Status |
|--------------|-----------|-----------------|--------|
| Self-hosted license | Per-site license + updates | One-time + annual support % | 🟢 (product) |
| Managed hosting | Deployed Precis (DB, media, proxy, tasks) | Monthly per site | 🔴 planned |
| Setup & migration | Import courses/learners from legacy tools | Project fee | 🟡 beta |
| White-label theming | Branded catalog shell via Wagtail | Setup fee + retainer | 🟡 beta |

## 5. Ideal Clients

| Persona | Description | Pain | Buying trigger | Willingness to pay |
|---------|-------------|------|----------------|--------------------|
| Training ops lead | 20–200 learner training company | Tool sprawl, per-seat SaaS costs, no branded catalog | Renewal pain / growth of course catalog | $100–500/mo managed |
| Agency founder | Builds client training sites | Repeatable platform to productize | New client project needing LMS | Project + revenue share |
| Ed institution IT lead | University/bootcamp extension school | Control, data ownership, localization (AR) | Compliance/data sovereignty push | License + hosting |

## 6. Research Needed

- [ ] Validate SAM segmentation (EU vs GCC/MENA split) with 10 customer interviews.
- [ ] Price-test managed hosting vs self-hosted license willingness-to-pay (🔴 → 🟡).
- [ ] Competitive matrix: Moodle, Teachable, Thinkific, LearnDash — feature gaps to attack.
- [ ] Measure deployment-to-value time for the managed path (target < 30 min).
- [ ] Arabic RTL learning UX validation — Precis ships en/ar; confirm parity is a selling point.

## Remarks & Notes

- The LMS + landing merge is the differentiator; do not split the product story back into "LMS" and "landing" in external materials.
- Legacy aliases (`precis-lms`, `precis-landing`) are internal only — never use them in customer-facing copy.
- All market figures are directional; upgrade tags as research completes.
