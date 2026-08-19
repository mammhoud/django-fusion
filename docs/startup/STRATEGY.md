---
title: Full Startup Strategy — Portfolio Master 🔒
description: The complete consolidated startup strategy for the Structa Cloud portfolio — market strategy, MVP canvases, TAM/SAM/SOM sizing, SaaS service lines, ideal client personas, and the research backlog for every product in one document.
navigation:
  title: Full strategy 🔒
  icon: i-lucide-rocket
object:
  type: "private-strategy"
  id: "docs.startup.strategy"
attributes:
  source_path: "startup/STRATEGY.md"
  canonical_route: "/docs/en/startup/strategy"
  source_of_truth: "repository-markdown"
  owner: "workspace"
  status: "maintained"
  access: "private"
tags:
  - structa-cloud
  - startup
  - strategy
  - market
  - mvp
  - tam-sam-som
  - saas
  - private
links:
  - label: "Startup home 🔒"
    to: "/docs/en/startup"
    icon: "i-lucide-rocket"
  - label: "Precis strategy 🔒"
    to: "/docs/en/startup/precis"
    icon: "i-lucide-graduation-cap"
  - label: "CTC strategy 🔒"
    to: "/docs/en/startup/precis-ctc"
    icon: "i-lucide-hospital"
  - label: "Syntara strategy 🔒"
    to: "/docs/en/startup/syntara"
    icon: "i-lucide-bot"
  - label: "Formint strategy 🔒"
    to: "/docs/en/startup/formints"
    icon: "i-lucide-credit-card"
  - label: "Loop-CRM strategy 🔒"
    to: "/docs/en/startup/loop-crm"
    icon: "i-lucide-handshake"
---

# 🚀 Full Startup Strategy — Portfolio Master 🔒

> **Internal only.** This is the single consolidated startup strategy document
> for the whole Structa Cloud portfolio. Per-product deep dives live in
> `startup/<product>.md`; this master consolidates the portfolio view, the
> combined MVP canvas, the TAM/SAM/SOM table, SaaS service lines, ideal client
> personas, and the cross-product research backlog so decisions can be made
> against one picture.

<!-- AI-generated: review needed -->

## 1. Portfolio Market Strategy

### 1.1 Positioning statement

> For **operators of learning, medical, sales, and commerce businesses** who
> need **one self-hosted platform instead of five disconnected SaaS tools**,
> **Structa Cloud** is a **monorepo of products on a shared Django/Wagtail +
> django-fusion foundation** that **reuses one component system, one auth
> stack, and one deployment story across every product**.

### 1.2 The wedge

| # | Wedge | Why it comes first |
|---|-------|--------------------|
| 1 | **Loop-CRM** — sales + marketing workspace | Smallest wedge: one team, one pain (contacts + campaigns split across tools). Fastest to demo and sell. |
| 2 | **Formint POS** — offline-first restaurant POS | Clear buyer (restaurant owner), clear ROI (orders + payments offline), desktop distribution. |
| 3 | **Precis** — LMS + catalog | Education buyers need trust and content; longer cycle but highest contract size. |
| 4 | **CTC Research** — medical research center site | Anchor customer with real publishing requirements; validates content pipeline. |
| 5 | **Syntara** — AI chat/customizer | Horizontal AI layer that makes every other product more valuable; sells as an add-on. |

### 1.3 Portfolio moat

- **Shared django-fusion framework** — one component/table/form system reused by
  every product (CTC 194 files, Precis 41, Pro 25, Cloud 19, Loop-CRM). Building
  one capability improves five products.
- **Self-hosting story** — one Compose/Traefik stack deploys the whole portfolio;
  customers who self-host are harder to churn.
- **Data gravity** — Loop-CRM (sales data), Precis (learning data), Formint
  (transactions) accumulate switching-cost data.
- **Cross-product bundles** — POS + CRM + LMS share auth, media, and admin.

### 1.4 Go-to-market

| Motion | Channel | Used by |
|--------|---------|---------|
| Product-led | Docs site, self-serve trial, `make run-dev` | All products |
| Sales-led | CTC anchor, Loop-CRM pilot teams | CTC, Loop-CRM |
| Partner | POS resellers, restaurant software integrators | Formint |
| Marketplace | Astro/React component themes, template gallery | Precis, Syntara |

## 2. Combined MVP Canvas

| Canvas cell | Portfolio answer |
|-------------|------------------|
| **Problem** | Fragmented tools: CRM, POS, LMS, CMS, AI chat are separate products with separate logins, data, and deployment. |
| **Solution** | One self-hosted platform: Loop-CRM (sales), Formint (commerce), Precis (learning), CTC (publishing), Syntara (AI) on one Django + django-fusion core. |
| **Key metrics** | MRR per product · self-host installs · active workspaces · content pages published · orders processed · AI conversations |
| **Unfair advantage** | The shared django-fusion framework + monorepo velocity: every product ships the same components, tables, forms, and auth. |
| **Channels** | Docs site (Docus), GitHub monorepo, product landing pages, CTC anchor case study, POS reseller partners. |
| **Cost structure** | One infra stack (Postgres/Redis/Traefik) for all products; shared worker/scheduler; per-product frontends. |
| **Revenue streams** | SaaS subscriptions per product, self-host licenses, support/implementation services, AI usage add-on. |

## 3. TAM / SAM / SOM (Portfolio Table)

> Confidence tags: 🟢 sourced · 🟡 estimate · 🔴 assumption (research needed).
> Full sizing with sources in each product doc.

| Product | TAM | SAM | SOM (24 mo) | Confidence | Source anchor |
|---------|-----|-----|-------------|------------|---------------|
| 🎓 Precis | LMS + corporate training worldwide | Regional edtech + corporate LMS buyers | Early adopters in 1–2 segments | 🟡 | [`precis.md`](precis.md) |
| 🏥 CTC Research | Medical research center digital presence | Research centers with publishing needs | CTC + 1–2 similar centers | 🟡 | [`precis-ctc.md`](precis-ctc.md) |
| 🤖 Syntara | AI chat/customizer market | Teams already on the platform | Add-on attach to existing products | 🔴 | [`syntara.md`](syntara.md) |
| 💳 Formint POS | Restaurant/café POS market | Offline-first independent restaurants | Local restaurant cluster | 🟡 | [`formints.md`](formints.md) |
| 🤝 Loop-CRM | CRM + marketing automation market | Small sales teams replacing 2–3 tools | Pilot teams in one vertical | 🔴 | [`loop-crm.md`](loop-crm.md) |

## 4. SaaS Service Lines (Portfolio)

| Service line | Products | Pricing posture | Status |
|--------------|----------|-----------------|--------|
| **Workspace SaaS** | Loop-CRM, Precis | Per-seat monthly | 🔴 assumption |
| **Commerce SaaS** | Formint Cloud | Per-outlet monthly + hardware-free | 🟡 estimate |
| **Publishing SaaS** | CTC Research, Precis landing | Per-site retainer | 🟡 estimate |
| **AI add-on** | Syntara | Usage-based (tokens) on top of any product | 🔴 assumption |
| **Self-host license** | All | One-time + support | 🟡 estimate |
| **Implementation services** | CTC, Loop-CRM, Precis | Project-based | 🟢 sourced (CTC anchor) |

## 5. Ideal Clients (Portfolio Personas)

| Persona | Product | Pains | Buying trigger |
|---------|---------|-------|----------------|
| **Sales team lead** (10–50 people) | Loop-CRM | Contacts in sheets, campaigns in another tool | Quarterly pipeline review miss |
| **Restaurant owner** (1–5 outlets) | Formint | Offline orders fail, receipts slow, no analytics | New outlet opening / POS contract renewal |
| **Training manager** | Precis | Courses scattered, no progress tracking | Compliance deadline / onboarding wave |
| **Research center director** | CTC | Outdated site, no publishing workflow, translation burden | Grant cycle / conference season |
| **Product engineer** | Syntara | Wants AI in the product without vendor lock | Trial of a competing AI tool |

## 6. Cross-Product Research Backlog

> Each item is the open question that must be answered before doubling down.
> The owning product doc carries the full backlog; this is the consolidated priority.

| # | Question | Product | Priority |
|---|----------|---------|----------|
| 1 | Which vertical pays first for Loop-CRM? | Loop-CRM | 🔴 High |
| 2 | What is the real POS total cost vs. incumbents? | Formint | 🟡 High |
| 3 | Do LMS buyers require LTI/SCORM compliance? | Precis | 🟡 Medium |
| 4 | What is the medical publishing compliance burden? | CTC | 🟢 Medium |
| 5 | What is the per-token margin at self-host scale? | Syntara | 🔴 Medium |
| 6 | Which bundle (CRM+POS, LMS+CRM) has the shortest sales cycle? | Portfolio | 🔴 Low |

## 7. Sequencing (What We Build Next)

```mermaid
graph LR
    A[Loop-CRM pilot] --> B[Formint Cloud outlet]
    B --> C[Precis LMS wave]
    C --> D[CTC publishing anchor]
    D --> E[Syntara AI add-on]
    E --> F[Bundles & self-host]
```

1. **Loop-CRM pilot** — validate the wedge with one vertical.
2. **Formint Cloud** — turn the desktop POS into a SaaS outlet.
3. **Precis LMS** — land the education contract with the catalog shell.
4. **CTC publishing** — anchor case study + publishing pipeline validation.
5. **Syntara AI** — attach AI to every product.
6. **Bundles** — package the portfolio as one self-host platform.

## Remarks & Notes

- This document is the **portfolio master**; per-product detail lives in the
  five product strategy docs. Update those first, then reconcile this master.
- Every figure carries a confidence tag; 🟢/🟡/🔴 conventions are defined in
  [`README.md`](README.md).
- Private by policy — strip research backlogs and pricing assumptions before
  any external publication.
- The per-product docs follow [`_template.md`](_template.md); keep the section
  order in sync when adding sections here.