---
title: Loop-CRM
description: Unified sales + marketing CRM (Twenty + Postiz lineage) on Django + django-fusion.
navigation:
  title: Loop-CRM
  icon: i-lucide-users
object:
  type: "product"
  id: "loop-crm.index"
attributes:
  source_path: "loop-crm/README.md"
  canonical_route: "/docs/en/loop-crm"
  source_of_truth: "repository-markdown"
  audience: "engineers, operators, and coding agents"
  status: "maintained"
  owner: "loop-crm"
tags:
  - structa-cloud
  - loop-crm
  - crm
  - sales
  - marketing
  - django-fusion
links:
  - label: "Documentation home"
    to: "/"
    icon: "i-lucide-house"
  - label: "Design System"
    to: "/loop-crm/design-system"
    icon: "i-lucide-palette"
  - label: "Setup & Build"
    to: "/loop-crm/setup-and-build"
    icon: "i-lucide-wrench"
---

# 🤝 Loop-CRM — Unified Sales & Marketing CRM

> Unified sales + marketing platform (Twenty DNA + Postiz DNA) on
> Django + django-fusion. Canonical product location:
> `projects/loop-crm/`.

<!-- AI-generated: review needed -->

## Product Docs (canonical, in-repo)

| Doc | Path | Covers |
|-----|------|--------|
| **Design System** | [`projects/loop-crm/docs/DESIGN_SYSTEM.md`](../../projects/loop-crm/docs/DESIGN_SYSTEM.md) | Industrial-brutalist / tactical telemetry design tokens, typography, layout, components. |
| **Setup & Build** | [`projects/loop-crm/docs/SETUP_AND_BUILD.md`](../../projects/loop-crm/docs/SETUP_AND_BUILD.md) | Step-by-step startup, backend + frontend setup, build and run commands. |
| **Database ERD** | [`projects/loop-crm/docs/erd/README.md`](../../projects/loop-crm/docs/erd/README.md) | `make erd`/`erd-all` model diagrams per team domain — sales (crm), marketing, attribution, finance, pos, billing, pages, core. |

## Env & Config

| Doc | Path | Covers |
|-----|------|--------|
| **Env contract** | [`projects/loop-crm/configs/`](../../projects/loop-crm/configs/) | The 56-variable environment catalog + validator (`make validate-env`). |
| **Env example** | [`projects/loop-crm/.env.example`](../../projects/loop-crm/.env.example) | Copy-paste environment template. |
| **Site identity** | [`projects/loop-crm/Env/_site.yml`](../../projects/loop-crm/Env/_site.yml) | Domain, allowed hosts, per-environment overrides. |

## Commands

```bash
# From projects/loop-crm
make dev               # Astro frontend dev server
make backend-dev       # Django dev server (backend Makefile)
make check             # frontend typecheck
make backend-check     # Django system checks
make backend-test      # Django tests
make backend-migrate   # makemigrations + migrate
make backend-seed      # seed demo workspace (demo@loop.dev / demo-pass-123)
make validate-env      # check env against the configs contract
make i18n              # makemessages + compilemessages (en, ar)
make backend-erd       # Django model ERD → docs/erd/ (needs graphviz dot)
make backend-erd-all   # one model ERD PNG per domain app (sales crm, marketing, …)

# Through Nx (requires root npm install)
make nx-check          # npx nx run loop-crm:check
npx nx run loop-crm:backend-test
```

## Architecture Notes

- **Render-first:** Django renders the data screens (fusion tables/forms);
  the Astro shell proxies `/fragments`, `/api`, `/bolt`, `/accounts`.
- **API roads:** `/bolt/tables/{resource}` (canonical, JWT, needs django_bolt)
  and `/api/v1/tables/{resource}/` (compat, session cookie).
- **Fusion table contract:** render-first resource pages and both API roads use
  `apps.core.resource_tables.resource_table`, backed by
  `django_fusion.fragments.tables.RowGenerator`. Column keys, labels, types,
  and formatted cells therefore stay aligned without changing Bolt handlers.
- **Route ownership:** `apps.core.fusion` owns browser routes and menu entries;
  `apps.core.navigation` owns the shared navigation JSON/HTMX tree; domain
  `apps.*.urls` owns versioned APIs. Do not add API behavior to Fusion menu
  routes or expose Bolt-only auth through the session compatibility road.
- **Redis-free dev:** a RESP PING probe decides; DEBUG falls back to LocMem
  cache + in-memory channel layer when Redis is missing or another app squats
  the port.
- **i18n:** `LocaleMiddleware` + `LANGUAGES` (en/ar) + `LOCALE_PATHS`; models
  use `gettext_lazy`. See `docs/ai/templates-and-request-flows.md` for the
  translation flow.

## Remarks & Notes

- On dev machines where the Kiro app holds ports 8000/6379, run the backend on
  `PORT=8001` and the Redis probe handles the rest.
- The session changelog for recent Loop-CRM work lives at
  [`docs/changelogs/session-2026-08-18.md`](../changelogs/session-2026-08-18.md).
