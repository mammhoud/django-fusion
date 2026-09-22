---
title: Precis Main — Fusion render-flow delivery plan
description: Accepted delivery contract for Precis Main full HTML, HTMX, Astro data, local Compose, production Compose, and Nx workflows.
navigation:
  title: Fusion render-flow plan
  icon: i-lucide-route
object:
  type: "plan"
  id: "docs.plans.repository.precis-main-render-flow"
attributes:
  source_path: "plans/repository/precis-main-render-flow.md"
  canonical_route: "/docs/en/plans/repository/precis-main-render-flow"
  source_of_truth: "repository-markdown"
  owner: "precis-main"
  status: "accepted"
tags:
  - structa-cloud
  - precis
  - precis-main
  - fusion
  - deployment
  - nx
links:
  - label: "Precis product"
    to: "/precis"
    icon: "i-lucide-graduation-cap"
  - label: "Render-flow reference"
    to: "/precis/landing-fusion-render-flow.html"
    icon: "i-lucide-route"
  - label: "Delivery report"
    to: "/agenda/.mono-repo/reports/precis-main-delivery"
    icon: "i-lucide-file-chart-column"
---

# Precis Main — Fusion render-flow delivery plan

> **Status:** Accepted · **Canonical project:** `projects/structa.cloud/` · **Updated:** 2026-09-15

## Context

Precis Main is the unified product created by merging the marketing/catalog and
learning surfaces. Its content source is served through a deliberate dual-road
contract: Django/Wagtail and django-fusion provide full HTML, HTMX returns small
server-rendered fragments, and Astro consumes explicit JSON APIs for interactive
islands.

The command surface must make environment choice visible. A local deployment
must load the overlay and publish localhost ports; a production deployment must
use the base Compose file and the root deployment environment. Nx should expose
those operations without creating a second implementation.

## Decision

Keep the project Makefile as the command source of truth and expose it through
Nx project `precis-main-assets`:

| Concern | Canonical command |
|---|---|
| Local Compose validation | `make validate-local` |
| Local deployment | `make deploy-local` |
| Production Compose validation | `make validate-production` |
| Production deployment | `make deploy-production` |
| Project checks | `make check` |
| Project tests | `make backend-test` |
| Production build | `make build-prod` |
| Nx check/build/deploy | `npx nx run precis-main-assets:<target>` |

`deploy-local` explicitly combines `docker-compose.yml` with
`docker-compose.override.yml`. `deploy-production` explicitly uses only the
base `docker-compose.yml` and `../../../.env`; neither target removes volumes.

## Render-road acceptance criteria

- [x] Public catalog and SEO paths have a documented full HTML road.
- [x] HTMX paths are documented as fragment responses, not client-only mocks.
- [x] Astro JSON paths are documented as explicit data API contracts.
- [x] Local and production Compose targets are distinct and named.
- [x] Nx `check`, `test`, `build`, `deploy-local`, and `deploy-production` targets delegate to Make.
- [x] Project-local and canonical HTML references exist.
- [ ] Add a CI-only render-road probe that does not deploy containers.
- [ ] Add a dedicated browser smoke workflow for local overlay startup.

## Related implementation

- `projects/structa.cloud/Makefile`
- `projects/structa.cloud/project.json`
- `projects/structa.cloud/docker-compose.yml`
- `projects/structa.cloud/docker-compose.override.yml`
- `projects/Makefile` (`WEBSITE=structa.cloud` dispatcher)
- `docs/precis/landing-fusion-render-flow.html`
- `projects/structa.cloud/docs/landing-fusion-render-flow.html`

## Remarks & Notes

- `precis-lms`, `precis-landing`, `lms`, and `structa` are compatibility aliases where supported; new work belongs under `precis-main`.
- Production deployment requires a populated root environment and shared infrastructure; this plan does not authorize deployment by itself.
- Keep any future command rename synchronized across Make, Nx metadata, product docs, agenda objects, and the HTML reference.

<!-- AI-generated: review needed -->
