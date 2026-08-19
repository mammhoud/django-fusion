---
title: Precis — Unified LMS + Landing product
description: Canonical documentation index for the Precis product (precis-main), including the merged landing/marketing shell and its legacy Landing-Fusion references.
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
| Configuration | [`configuration.md`](configuration.md) | Settings, env vars, Dynaconf wiring |
| Courses | [`courses.md`](courses.md) | LMS course model, enrollment, progress |
| Deployment | [`deployment.md`](deployment.md) | Docker Compose deployment of the merged stack |
| Landing frontend | [`landing-fusion/frontend.md`](landing-fusion/frontend.md) | Astro shell, skeleton bridge, HTMX |
| Landing backend API | [`landing-fusion/backend-api.md`](landing-fusion/backend-api.md) | Render-first + data API contract |
| Landing deployment | [`landing-fusion/deployment.md`](landing-fusion/deployment.md) | Traefik routing for the landing slice |

## 🧭 Naming & Aliases

| Name | Status | Maps to |
|------|--------|---------|
| `precis-main` | ✅ canonical | `projects/precis/precis-main/` |
| `precis-lms` | ⚠️ legacy alias | `precis-main` (merged) |
| `precis-landing` / Landing-Fusion | ⚠️ legacy alias | `precis-main` (merged) |

> Legacy docs under the old `docs/landing-fusion/` tree were moved here —
> `docs/precis/landing-fusion/*` is the canonical home for the landing slice.

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
