---
title: Portfolio Comparison — Products & Competitors 🔒
description: Private comparison of every Structa Cloud product against each other and against named competitors — shared foundation, wedges, maturity, pricing posture, and buy/decision guidance.
navigation:
  title: Comparison 🔒
  icon: i-lucide-scale
object:
  type: "private-strategy"
  id: "docs.startup.comparison"
attributes:
  source_path: "startup/comparison.md"
  canonical_route: "/docs/en/startup/comparison"
  source_of_truth: "repository-markdown"
  owner: "workspace"
  status: "maintained"
  access: "private"
tags:
  - structa-cloud
  - startup
  - comparison
  - market
  - competitive
links:
  - label: "Startup home 🔒"
    to: "/docs/en/startup"
    icon: "i-lucide-rocket"
  - label: "Full strategy 🔒"
    to: "/docs/en/startup/strategy"
    icon: "i-lucide-rocket"
---

# ⚖️ Portfolio Comparison — Products & Competitors 🔒

> **Internal only.** How the Structa Cloud products compare to each other and to
> the named alternatives in their markets. Competitor names are public-market
> facts; every size/positioning claim carries a confidence tag (🟢 sourced ·
> 🟡 estimate · 🔴 assumption).

<!-- AI-generated: review needed -->

## 1. Products vs. each other

| Dimension | 🎓 Precis | 🏥 CTC Research *(sample)* | 🤖 Syntara | 💳 Formint POS | 🤝 Loop-CRM |
|-----------|-----------|-----------------|------------|----------------|-------------|
| **Category** | LMS + landing catalog shell | Research-center publishing **sample** (agentic coding with Precis) | AI chat + template customization runtime | Offline-first multi-edition POS | Unified sales + marketing CRM |
| **Primary buyer** | Training companies, academies, institutions | Reference only — not a commercial line | Developers & product teams | Restaurants, cafés, gaming centers | SMB sales + marketing teams |
| **Wedge** | Course catalog + enrollment in one stack | Research publishing workflow (EN/AR) — seeds Precis Research | Template discovery → customization → runtime | Community → Pro → Cloud funnel | Pipeline + publishing in one data model |
| **Deployment** | Self-hosted Django/Wagtail | Self-hosted Django/Wagtail + Astro (sample) | Self-hosted, bring-your-own model | Desktop (Rust/Tauri) + optional Django cloud | Self-hosted Django/Wagtail |
| **Maturity** | 🟢 product (live) | 🧪 sample (live reference site) | 🟡 beta runtime | 🟢 community + pro live, cloud live | 🟢 product, marketing tier 🟡 beta |
| **Revenue model** | License + managed hosting | Sample — no commercial revenue line | Open-core + managed tier | Free → Pro license → Cloud SaaS | Freemium seats + automation tier |
| **TAM (directional)** | ~$20–25B 🟡 | ~$4–6B 🔴 | ~$15–20B 🟡 | ~$25–35B 🟡 | ~$65–70B 🟡 |
| **Shares with portfolio** | django-fusion, auth, media, admin | django-fusion, publishing pipeline | django-fusion, MCP, streaming | django-fusion (cloud), auth, media | django-fusion, Wagtail, auth |

## 2. Shared foundation (django-fusion) — why one team ships five products

| Capability | Where it lives | Products using it |
|-----------|----------------|-------------------|
| Component system (`{% comp %}`, fragments, tables, forms) | `libs/django-fusion/` | All Django products |
| Auth (allauth), sessions, CSRF, HTMX middleware | shared Django configs | All products |
| Wagtail CMS pages + StreamFields | shared | Precis, CTC, Loop-CRM, Precis Landing |
| Media pipeline (manifest, renditions, EN/AR/RTL ops) | `projects/assets/` | CTC, Precis, Precis Landing |
| Task/worker boundary (Dramatiq) | shared configs | CTC, Loop-CRM, Formint Cloud |
| One deploy story (Compose + Traefik) | `applications/` | All products |

> **Portfolio moat:** building one capability (a new table, a new fragment, a
> locale fix) improves every product. Competitors ship single products; the
> portfolio compounds.

## 3. Head-to-head vs. competitors

### 3.1 Precis (LMS)

| | **Precis** | Moodle | Canvas | Docebo | TalentLMS | Teachable |
|---|---|---|---|---|---|---|
| Self-hostable | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Landing/catalog shell in same stack | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ (storefront, not landing) |
| Arabic/RTL support | ✅ (en/ar) | ⚠️ plugins | ⚠️ | ⚠️ | ⚠️ | ⚠️ |
| License + services pricing | ✅ | ✅ OSS | ❌ SaaS | ❌ SaaS | ❌ SaaS | ❌ SaaS |
| LTI/SCORM out of the box | ❌ (gap) | ✅ | ✅ | ✅ | ⚠️ | ❌ |

### 3.2 CTC Research (research-center publishing — sample, agentic coding with Precis)

| | **CTC Research** *(sample)* | Silverchair | Atypon | Health web agencies | WordPress agencies |
|---|---|---|---|---|---|
| Institutional *site* (teams/studies) | ✅ | ❌ journal-centric | ❌ journal-centric | ✅ | ✅ |
| Research publishing workflow | ✅ productized | ⚠️ journal ops | ⚠️ | ❌ one-off | ❌ one-off |
| EN/AR parity pipeline | ✅ | ❌ | ❌ | ❌ | ❌ |
| Repeatable product (not build) | ✅ | ✅ | ✅ | ❌ | ❌ |
| Live reference deployment | ✅ ctc-research.com | — | — | — | — |

### 3.3 Syntara (AI chat + customization)

| | **Syntara** | Intercom Fin | Dify/Langflow | LibreChat/Open WebUI | Bolt.new/v0 |
|---|---|---|---|---|---|
| Self-hostable | ✅ | ❌ | ⚠️ self-host option | ✅ | ❌ |
| Provider-agnostic (Ollama + APIs) | ✅ | ❌ | ⚠️ | ✅ | ❌ |
| Template discovery | ✅ | ❌ | ❌ | ❌ | ⚠️ prompt-only |
| Code customization of templates | ✅ | ❌ | ❌ | ❌ | ✅ |
| Streaming runtime in-product | ✅ | ✅ (support) | ⚠️ | ✅ | ❌ |

### 3.4 Formint POS

| | **Formint** | Toast | Square for Restaurants | Lightspeed | Loyverse |
|---|---|---|---|---|---|
| Offline-first | ✅ | ❌ | ❌ | ❌ | ⚠️ |
| Free/community edition | ✅ | ❌ | ⚠️ free-ish, payments-locked | ❌ | ✅ |
| Self-host / data ownership | ✅ | ❌ | ❌ | ❌ | ❌ |
| Gaming-center vertical | ✅ | ❌ | ❌ | ❌ | ❌ |
| Multi-edition funnel (community→pro→cloud) | ✅ | ❌ | ❌ | ❌ | ❌ |
| Cloud multi-store sync | ✅ (Django cloud) | ✅ | ✅ | ✅ | ⚠️ |

### 3.5 Loop-CRM

| | **Loop-CRM** | HubSpot | Pipedrive | Zoho | Twenty OSS | Postiz |
|---|---|---|---|---|---|---|
| Self-hostable | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ |
| Pipeline + marketing in one data model | ✅ | ⚠️ separate hubs | ❌ sales-only | ⚠️ suite | ❌ sales-only | ❌ scheduling-only |
| Wagtail landing pages | ✅ | ⚠️ CMS add-on | ❌ | ⚠️ | ❌ | ❌ |
| Social publishing (Postiz lineage) | ✅ | ⚠️ | ❌ | ⚠️ | ❌ | ✅ |
| Freemium self-host | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ |

## 4. Where each product wins (and loses)

| Product | Wins when | Loses when |
|---------|-----------|-----------|
| **Precis** | Buyer wants one self-hosted stack for courses + marketing, AR/RTL, no per-seat SaaS | Buyer requires LTI/SCORM certification or enterprise LMS procurement today |
| **CTC Research** *(sample)* | Research center wants a maintained EN/AR publishing site, not a one-off build (reference only) | Center already has a journal platform and needs only a brochure |
| **Syntara** | Team wants AI chat that matches its brand/stack, self-hosted, with template customization | Buyer wants a turnkey enterprise support assistant (Intercom Fin territory) |
| **Formint** | Offline-first F&B/gaming, free adoption path, local-language/tax needs | Buyer wants integrated payments hardware + processing (Toast/Square) |
| **Loop-CRM** | SMB wants one tool for pipeline + marketing + landing, self-hosted, AR/RTL | Buyer is an agency needing HighLevel-style funnel white-label at scale |

## 5. Bundle logic (cross-sell)

| Bundle | Story | Shortest path |
|--------|-------|---------------|
| Loop-CRM + Formint Cloud | Sales + commerce: orders flow into CRM pipelines (finance workflow plan) | Formint Cloud outlet → Loop-CRM deal records |
| Precis + Loop-CRM | Train + sell: course enrollments feed CRM contacts | Precis cohort → Loop-CRM pipeline |
| CTC *(sample)* + Precis | Publish + teach: research center content reuses the catalog/course shell (reference for the Precis Research vision) | CTC publishing → Precis courses |
| Syntara + anything | AI add-on attach to every product | Any product demo → Syntara chat |
| django-fusion (all) | One component/table/form system across every product | Any two products in one deploy |

## 6. Research priorities (comparison view)

| # | Question | Products | Priority |
|---|----------|----------|----------|
| 1 | Which bundle has the shortest sales cycle? | Portfolio | 🔴 High |
| 2 | Do LMS buyers require LTI/SCORM? | Precis | 🟡 High |
| 3 | What is the real POS total cost vs incumbents? | Formint | 🟡 High |
| 4 | Which vertical pays first for Loop-CRM? | Loop-CRM | 🔴 High |
| 5 | Medical publishing compliance burden? | CTC | 🟢 Medium |
| 6 | Per-token margin at self-host scale? | Syntara | 🔴 Medium |

## Remarks & Notes

- **Citation status:** compiled 2026-08-19 from public market knowledge; live
  citation lookup was unavailable at authoring time. Competitor names are
  facts; all size figures are 🟡/🔴 directional until verified against named
  public reports. Upgrade tags in the per-product docs as research lands.
- Per-product deep dives: `startup/precis.md`, `startup/precis-ctc.md`,
  `startup/syntara.md`, `startup/formints.md`, `startup/loop-crm.md`.
- The "Gaps to attack" lines in each product doc are the cross-sell wedge —
  keep them consistent with this comparison when they change.
