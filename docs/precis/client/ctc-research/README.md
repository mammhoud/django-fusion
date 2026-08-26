---
title: CTC Research — Documentation
description: Canonical documentation index for the CTC Research site (precis-ctc) — guides, content & publishing, startup strategy, architecture, and commands.
navigation:
  title: CTC Research
  icon: i-lucide-heart-pulse
object:
  type: "product"
  id: "docs.precis-ctc"
attributes:
  source_path: "precis-ctc/README.md"
  canonical_route: "/docs/en/precis-ctc"
  source_of_truth: "repository-markdown"
  owner: "precis-ctc"
  status: "maintained"
tags:
  - structa-cloud
  - precis
  - precis-ctc
  - ctc-research
  - research
  - publishing
links:
  - label: "Precis group home"
    to: "/precis"
    icon: "i-lucide-graduation-cap"
  - label: "Content strategy"
    to: "/precis-ctc/content-strategy"
    icon: "i-lucide-pen-tool"
  - label: "Publishing & production"
    to: "/precis-ctc/publishing-and-production"
    icon: "i-lucide-send"
  - label: "Client production 🔒"
    to: "/precis-ctc/client-production"
    icon: "i-lucide-globe"
---

# 🏥 CTC Research Documentation

> **Canonical product path:** `projects/precis/precis-ctc/`
> **Runtime identity:** `precis-ctc`
> **Public identity:** `ctc-research.com`
> **Dispatcher aliases:** `WEBSITE=ctc`, `WEBSITE=precis-ctc`, `WEBSITE=ctc-website`, `WEBSITE=ctc-research.com`

<!-- AI-generated: review needed -->

CTC Research is the standalone medical research center and learning site in
the Precis product group. It has its own Django/Wagtail backend, Astro
frontend, Compose services, CTC database, shared media mapping, and proxy
routes. It is not the same runtime as the unified `precis-main` product.

## Guides

- [Project docs index](../../projects/precis/docs/precis-ctc/README.md)
- [Content map](../../projects/precis/docs/precis-ctc/CONTENTS.md)
- [Component registry and frontend components](../../projects/precis/docs/precis-ctc/COMPONENTS.md)
- [Template architecture](../../projects/precis/docs/precis-ctc/TEMPLATES.md)
- [Setup and build](../../projects/precis/docs/precis-ctc/SETUP_AND_BUILD.md)
- [Environment and redeploy](../../projects/precis/docs/precis-ctc/ENVIRONMENT.md)
- [Enhancement register](../../projects/precis/docs/precis-ctc/ENHANCEMENTS.md)
- [Learning cases & techniques](../../projects/precis/docs/precis-ctc/LEARNING_CASES.md) — incl. localized-slug translation resolution (Case 8) and SEO metadata on both roads (Case 9)
- [Changelog](../../projects/precis/precis-ctc/CHANGELOG.md) — session history, incl. SEO metadata, Wagtail-driven content and admin routing
- [Publish plan](../plans/repository/ctc-research-publish-2026-08-18.md)
- [Cross-module workflows](../plans/repository/precis-ctc-workflows.md)

## Content & publishing

- [Content strategy, ICP & market research](content-strategy.md)
- [Publishing workflow & production notes](publishing-and-production.md)
- [Client production website — case study](client-production.md) — ctc-research.com as the anchor reference deployment for the publishing service line

## Startup strategy 🔒

- [CTC Research market strategy](../startup/precis-ctc.md) — commercial positioning, buyer ICP, TAM/SAM/SOM, offers, and research backlog
- [Full portfolio strategy](../startup/STRATEGY.md) — consolidated master

The startup strategy owns commercial assumptions. The
[content strategy](content-strategy.md) owns editorial audiences and topic
clusters, while [publishing & production](publishing-and-production.md) owns
review, localization, release, and rollback. Keep these as linked sources, not
parallel copies.

## Architecture at a glance

```text
ctc-research.com
  ├─ Traefik: HTTPS/domain/path routing
  ├─ Astro frontend: public pages and learning shell
  ├─ Django/Wagtail backend: pages, APIs, fragments, auth, learning
  ├─ Dramatiq worker + scheduler: asynchronous execution boundary
  ├─ PostgreSQL: db_precis_ctc
  ├─ Redis: cache and task broker
  └─ shared-proxy/Nginx:
       /media/ctc-research/
       /static/bundles/ctc-research/
       /sites/ctc-research/static/
```

## Common commands

```bash
cd projects/precis/precis-ctc
make check
make frontend-check
make redeploy

cd projects
make check WEBSITE=precis-ctc
make redeploy-with-stack WEBSITE=precis-ctc
```

The full environment variable reference, safety notes, and asset release order
are in [Environment and redeploy](../../projects/precis/docs/precis-ctc/ENVIRONMENT.md).

## Remarks & Notes

- The filesystem path `projects/precis/precis-ctc/` is canonical. Do not create new code under historical paths such as `projects/precis-ctc/` or `projects/precis/lms-ctc/`.
- Public medical, legal, image-rights, and translation content requires CTC owner review before production publication.
- Generated bundles, collected static files, and runtime media are different asset classes; follow the environment guide rather than copying one into another.
