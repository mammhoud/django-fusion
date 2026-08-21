---
title: Precis — Unified LMS + Landing product
description: Canonical documentation index for the Precis product (precis-main), including the merged landing/marketing shell and its legacy Precis Landing references.
navigation:
  title: Precis
  icon: i-lucide-graduation-cap
object:
  type: "product"
  id: "docs.precis"
attributes:
  source_path: "precis/README.md"
  canonical_route: "/docs/en/precis"
  source_of_truth: "repository-markdown"
  owner: "precis-main"
  status: "maintained"
tags:
  - structa-cloud
  - precis
  - precis-main
  - lms
  - landing
  - wagtail
  - django
links:
  - label: "Project awareness"
    to: "/docs/en/guides/00-project-awareness"
    icon: "i-lucide-compass"
  - label: "Architecture"
    to: "/docs/en/architecture"
    icon: "i-lucide-landmark"
  - label: "Startup strategy 🔒"
    to: "/docs/en/startup/precis"
    icon: "i-lucide-rocket"
---

# 🎓 Precis — Unified LMS + Landing Product

> **Canonical path:** `projects/precis/precis-main/` · **Dispatcher alias:** `WEBSITE=precis-main` (legacy aliases `precis-lms`, `precis-landing` route here too)

Precis is the unified learning platform: an **LMS** (courses, enrollment, progress, profile) merged with the **landing marketing/catalog shell** (Wagtail pages, pricing, blog). The two codebases were merged into a single runtime so one Django + Astro stack serves both audiences.

## 📚 Documentation Index

| Area | Document | Notes |
|------|----------|-------|
| Architecture | [`ARCHITECTURE.md`](ARCHITECTURE.md) | Monorepo-merged LMS + landing design |
| CMS / Builder | [`cms-builder.md`](cms-builder.md) | Assets-based CMS builder (under development) + client work under the Solo/Business editions |
| Configuration | [`configuration.md`](configuration.md) | Settings, env vars, Dynaconf wiring |
| Courses | [`courses.md`](courses.md) | LMS course model, enrollment, progress |
| Deployment | [`deployment.md`](deployment.md) | Unified Compose stack, health checks, and admin routes |
| Landing frontend | [`precis-landing/frontend.md`](precis-landing/frontend.md) | Astro shell, skeleton bridge, HTMX |
| Landing backend API | [`precis-landing/backend-api.md`](precis-landing/backend-api.md) | Render-first + data API contract |
| Proxy/admin runbook | [`../dev/infrastructure/precis-main-proxy-admin.md`](../dev/infrastructure/precis-main-proxy-admin.md) | Current Traefik targets for structa.cloud and lms.structa.cloud |
| Landing compatibility | [`precis-landing/deployment.md`](precis-landing/deployment.md) | Legacy Precis Landing pointer to the unified runtime |
| CTC research site | [`../precis-ctc/README.md`](../precis-ctc/README.md) | Standalone research center site in the Precis group |

## 🧭 Naming & Aliases

| Name | Status | Maps to |
|------|--------|---------|
| `precis-main` | ✅ canonical | `projects/precis/precis-main/` |
| `precis-lms` | ⚠️ legacy alias | `precis-main` (merged) |
| `precis-landing` / Precis Landing | ⚠️ legacy alias | `precis-main` (merged) |

> Legacy docs under the old `docs/precis-landing/` tree were moved here —
> `docs/precis/precis-landing/*` is the canonical home for the landing slice.

## 🏗️ Where django-fusion is used

Precis is the reference consumer of the shared framework: `{% comp %}` components,
`Viewset`/`ModelViewset` routing, Wagtail StreamField blocks, fragments, and HTMX
scoping all come from `libs/django-fusion/`. See [the package guide](../libs/django-fusion.md).

## 🚀 Business & strategy

Market strategy, MVP canvas, TAM/SAM/SOM, ideal clients, and research backlog for
Precis live in the private [startup section](../startup/precis.md) 🔒.

## Remarks & Notes

- The legacy `precis-landing/` directory in the repo is a **kept copy**; the dispatcher routes its identity to `precis-main`. Prefer `precis-main` paths in new work.
- `precis-lms/` was merged and removed from the tree; git history is the archive.
- The landing docs describe the render-first/data-API contract — preserve both roads (server HTML + HTMX + JSON for Astro) when changing either.
