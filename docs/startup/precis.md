---
title: Precis — Business Strategy 🔒
description: Private business strategy for Precis (LMS + landing + CMS/builder) — executive summary, market opportunity, positioning, revenue model, target segments, and the research agenda.
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
  - cms
  - saas
links:
  - label: "Startup home 🔒"
    to: "/startup"
    icon: "i-lucide-rocket"
  - label: "Precis product docs"
    to: "/precis"
    icon: "i-lucide-graduation-cap"
  - label: "CMS / Builder profile"
    to: "/precis/cms-builder"
    icon: "i-lucide-blocks"
---

# 🎓 Precis — Business Strategy 🔒

> Private · Owner: `precis-main` · Confidence tags: 🟢 sourced · 🟡 estimate · 🔴 assumption

## 1. Executive Summary

**Precis is the complete learning and content platform for organizations that
want ownership, not lock-in.** It pairs an LMS (courses, enrollment, progress,
certificates) with a marketing/catalog site and an assets-based CMS/builder —
all from one Django + Wagtail codebase, deployed on the customer's own
infrastructure. Structa Cloud uses it as its flagship site; the same assets
power client engagements under the public Solo and Business editions.

- **The product.** One unified stack replaces the five-tool sprawl — LMS,
  payments, marketing pages, learner progress, and content management.
- **The wedge.** A white-labeled course catalog and enrollment flow for training
  organizations that currently sell through spreadsheets and video calls.
- **The defensibility.** Full data ownership for the customer, Wagtail content
  power, and a merged LMS + landing + CMS surface that competitors split across
  separate products.

## 2. Market Opportunity

| Market | Definition | Size | Confidence | Source / note |
|--------|-----------|------|------------|---------------|
| TAM | Global corporate LMS / online learning platforms | ~$20–25B (2025, global e-learning) | 🟡 | Public e-learning market reports |
| SAM | LMS for mid-size academies & training companies (EU + MENA + GCC, Arabic/English) | ~$600M–1B | 🔴 | Derived: segment share assumption |
| SOM | Year-3 obtainable: 100–300 paying training orgs | ~$1–3M ARR | 🔴 | Depends on GTM capacity; validate |

> **SOM logic:** a 0.2–0.5% capture of SAM, given a partner-led sales capacity
> of 10–20 deals per year. Validate with a pilot cohort before scaling GTM.

## 3. Positioning & Differentiation

- **For** mid-size academies, bootcamps, and training companies that want a
  branded learning platform without SaaS lock-in,
- **Precis** is the self-hostable LMS + marketing site + CMS that runs courses,
  enrollment, progress, and content from one codebase,
- **unlike** Moodle's PHP plugin ecosystem, SaaS-only platforms (Canvas,
  Docebo, Teachable), or WordPress LMS plugins,
- **because** it delivers complete control, bilingual (AR/EN) content, and a
  unified stack with a fraction of the operational surface.

### 6.2 Positioning vs. alternatives

| Dimension | Precis | Direct competitors | Indirect substitutes |
|-----------|--------|--------------------|---------------------|
| Deployment | Self-hosted Django/Wagtail, one Compose stack | Moodle (OSS), SaaS (Canvas, Docebo) | YouTube courses, PDF manuals, spreadsheets |
| Data ownership | Customer DB, no vendor lock | Vendor-hosted (SaaS) | None |
| Price posture | License + services | Per-seat SaaS | Free / status quo |
| Differentiator | LMS + landing + CMS on shared django-fusion | Single-purpose LMS vendors | In-person training / docs |

## 4. Revenue Model

| Service line | What it is | Pricing posture | Status |
|--------------|-----------|-----------------|--------|
| Self-hosted license | Per-site license + updates | One-time + annual support % | 🟢 (product) |
| Managed hosting | Deployed Precis (DB, media, proxy, tasks) | Monthly per site | 🔴 planned |
| Setup & migration | Import courses/learners from legacy tools | Project fee | 🟡 beta |
| White-label theming | Branded catalog shell via Wagtail | Setup fee + retainer | 🟡 beta |
| Client sites (Solo / Business) | Public editions at structa.cloud/pricing | Fixed project + managed retainer | 🟢 live |

## 5. Target Segments

| Persona | Description | Pain | Buying trigger | Willingness to pay |
|---------|-------------|------|----------------|--------------------|
| Training ops lead | 20–200 learner training company | Tool sprawl, per-seat SaaS costs, no branded catalog | Renewal pain / growth of course catalog | $100–500/mo managed |
| Agency founder | Builds client training sites | Repeatable platform to productize | New client project needing LMS | Project + revenue share |
| Ed institution IT lead | University/bootcamp extension school | Control, data ownership, localization (AR) | Compliance/data sovereignty push | License + hosting |
| Marketing team (client work) | Needs a content-driven site with a CMS | Static site + no editorial workflow | Rebrand / site relaunch | Solo/Business edition |

## 6. Competitive Landscape

> Names are public-market facts; size/positioning claims carry confidence tags.

### 6.1 Competitor map

| Competitor | Category | Target | Strengths | Our edge / gap |
|-----------|----------|--------|-----------|----------------|
| Moodle | OSS LMS | Universities & enterprises | Huge plugin ecosystem, LTI/SCORM, self-host | We are Django/Wagtail-native with the landing catalog shell; Moodle is PHP/plugin-heavy |
| Canvas / Instructure | SaaS LMS | Higher ed & K-12 | Polished UX, analytics, ecosystem | SaaS-only; we self-host with full data ownership |
| Docebo | Enterprise LMS | Mid-large corporates | AI features, integrations, compliance | Higher price; we are license + services |
| TalentLMS (Epignosis) | SMB LMS | Small teams | Cheap, fast adoption | No landing/catalog shell; we pair LMS + marketing site |
| Teachable / Thinkific | Creator platform | Independent creators | Payments + course sales built in | Creator-focused; we target institutions needing progress/compliance tracking |
| LearnDash / LifterLMS | WordPress LMS | WordPress sites | Installs on existing WP | WP-centric; we are Django/Wagtail-native with a unified stack |

> **Gaps to attack (🟡):** LTI/SCORM compliance for institutional buyers,
> AI-assisted course authoring, and Arabic/RTL learning UX — all named research
> items in the agenda below.

## 7. Research Agenda

- [ ] Validate SAM segmentation (EU vs GCC/MENA split) with 10 customer interviews.
- [ ] Price-test managed hosting vs self-hosted license willingness-to-pay (🔴 → 🟡).
- [ ] Do institutions require LTI/SCORM? If yes, scope the integration (priority from STRATEGY.md).
- [ ] Measure deployment-to-value time for the managed path (target < 30 min).
- [ ] Arabic RTL learning UX validation — Precis ships en/ar; confirm parity is a selling point.
- [ ] Validate the CMS/builder expansion: which buyers pay for a Precis-built site (Solo vs Business)?

> **Citation status:** competitor names are public-market facts. Market-size
> figures are directional (🟡/🔴) until verified against a named public report.

## Remarks & Notes

- The LMS + landing + CMS merge is the differentiator; do not split the product
  story back into separate products in external materials.
- Legacy aliases (`precis-lms`, `precis-landing`) are internal only — never use
  them in customer-facing copy.
- All market figures are directional; upgrade tags as research completes.
- The Solo/Business editions are live at structa.cloud/pricing — keep this
  document consistent with the public pricing page.
