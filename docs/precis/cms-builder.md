---
title: Precis — CMS / Builder Profile
description: Precis as an assets-based CMS/builder (under development) — reusable django-fusion assets, Wagtail-managed content, multi-site capability, and client work under the Solo/Business editions at structa.cloud/pricing.
navigation:
  title: CMS / Builder
  icon: i-lucide-blocks
object:
  type: "product"
  id: "docs.precis.cms-builder"
attributes:
  source_path: "precis/cms-builder.md"
  canonical_route: "/docs/en/precis/cms-builder"
  source_of_truth: "repository-markdown"
  owner: "precis-main"
  status: "maintained"
tags:
  - structa-cloud
  - precis
  - precis-main
  - cms
  - builder
  - wagtail
  - django-fusion
  - assets
  - editions
  - client-work
links:
  - label: "Precis home"
    to: "/docs/en/precis"
    icon: "i-lucide-graduation-cap"
  - label: "Architecture"
    to: "/docs/en/precis/architecture"
    icon: "i-lucide-landmark"
  - label: "Product profiles 🔒"
    to: "/docs/en/startup/product-profiles"
    icon: "i-lucide-boxes"
---

# 🧩 Precis — CMS / Builder Profile

> **Status:** Under development 🟡 · **Canonical path:** `projects/precis/precis-main/`
> **Public editions:** Solo · Business (see [`structa.cloud/pricing`](https://structa.cloud/pricing/))

<!-- AI-generated: review needed -->

Precis is built as an **assets-based project**: the product is a catalog of
reusable django-fusion assets (components, fragments, blocks, templates) on top
of a Wagtail content model. That asset base is what makes Precis a CMS/builder —
editors compose Wagtail pages from the same blocks the marketing site uses, and
new sites are assembled from the same assets instead of being written from
scratch.

## 🎯 What this means

| Layer | Asset | Reused by |
|-------|-------|-----------|
| Components | `{% comp %}` blocks (hero, CTA, FAQ, features, pricing) | Landing, product, and client pages |
| Routing | django-fusion `Viewset` / `PageHandler` | Every page road (HTML, HTMX fragment, JSON) |
| Content | Wagtail StreamField blocks + `PageTranslation` overlays | Multi-language editorial sites |
| Frontend | Astro pages + `SkeletonBridge` / `LiveFragment` | SSG marketing + SSR learning surfaces |
| Data API | Render-first contract (HTML / fragment / JSON) | Any client, including future CMS tenants |

## 🏗️ CMS / Builder under development

> **Update (Aug 2026):** the **thin Landing Builder MVP now exists** as
> `django_fusion.builder` — an abstract `BuilderPage` (theme/brand/dark +
> `template_context` + section StreamField), a `BuilderRenderer`, the
> `/apis/builder/` JSON road, and fu-* section templates — mounted in
> Loop-CRM (`apps.pages.BuilderPage`, `seed_builder`). It is the first real
> consumer of the theme engine. What remains before the Solo/Business
> builder surface is sellable: visual canvas, site scaffolding, and tenant
> isolation.

The builder capability is not shipped as a separate product yet; it is the
**underlying asset model** of Precis today:

- **Wagtail as the CMS core** — pages, snippets, StreamField blocks, locale-aware
  translations, and admin workflows are the content backbone.
- **django-fusion as the asset library** — every reusable UI/route/fragment
  lives in `libs/django-fusion/` and is shared across Precis, CTC, and (where
  licensed) client sites.
- **Multi-site path** — because content and assets are decoupled from any single
  site shell, the same stack can serve additional sites under the Solo/Business
  editions once the builder surface (site scaffolding, theme switching, tenant
  isolation) is productized.

## 💼 Client work under the editions

The public [`pricing`](https://structa.cloud/pricing/) page already sells Precis
in editions — **Solo** (single site, core LMS + landing) and **Business**
(cohorts, staff, connected systems, custom branding, API access). Client work is
delivered on those editions:

| Edition | What a client gets | Delivery model |
|---------|--------------------|----------------|
| **Solo** | One branded site, LMS + landing, Wagtail-editable | Fixed project + hosting |
| **Business** | Cohorts, staff, API access, custom branding, dedicated support | Project + managed retainer |

The reference deployments for this model are **structa.cloud itself** (the
flagship Precis site) and **ctc-research.com** (the [CTC client site](../precis-ctc/client-production.md))
— an institutional site built from the same assets with a managed publishing
workflow.

## 🔗 Related

- [Architecture](ARCHITECTURE.md) — ADRs and the full stack
- [Configuration](configuration.md) — settings and env vars
- [Courses](courses.md) — LMS course model and learning data
- [Deployment](deployment.md) — Docker Compose deployment
- [CTC client production case study](../precis-ctc/client-production.md) — anchor client deployment
- [Product profiles 🔒](../startup/product-profiles.md) — portfolio positioning (CMS/Builder/LMS/Research)
- [Precis strategy 🔒](../startup/precis.md) — market strategy, MVP, TAM/SAM/SOM

## Remarks & Notes

- The CMS/builder is a **direction, not a shipped product** — status is 🟡 under
  development. Do not present the builder surface as live until site scaffolding
  and tenant isolation ship.
- The Solo/Business edition names match `structa.cloud/pricing`; keep this page
  in sync if the public pricing changes.
- Assets stay in `libs/django-fusion/`; never copy product-specific templates
  into the shared library (ownership rule in the root `AGENTS.md`).
