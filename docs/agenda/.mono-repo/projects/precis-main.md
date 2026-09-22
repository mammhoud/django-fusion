---
Object type: Project
Tags: project, precis, precis-main, landing, lms, django, astro, fusion
Status: Active
Owner: workspace
Related Workspace: workspace
Related Products: precis
Related Teams: product, engineering, documentation
Related Plans: precis-main-render-flow
---

# Precis Main — Unified Learning and Landing Project

> **Description:** The canonical Precis product at `projects/structa.cloud/`, combining the Wagtail/Django learning platform with the Astro marketing and catalog shell.

## Outcome

One product boundary serves public catalog and marketing pages, learner journeys, course APIs, and authenticated administration. Django/Wagtail and django-fusion remain the content and server-rendering source; Astro consumes the explicit data API where an interactive island is appropriate.

## Delivery contract

- Local Compose uses `docker-compose.override.yml`, publishes Django on `8074` and Astro on `3000`, and is invoked with `make validate-local` then `make deploy-local`.
- Production Compose uses `docker-compose.yml` without the local override and is invoked with `make validate-production` then `make deploy-production`.
- Nx project `precis-main-assets` delegates `check`, `test`, `build`, `deploy-local`, and `deploy-production` to the project Makefile.
- `precis-lms`, `precis-landing`, `lms`, and `structa` remain compatibility aliases where the dispatcher supports them; they are not separate current runtimes.

## Render use cases

| Use case | Road | Owner |
|---|---|---|
| Public catalog, blog, and SEO pages | Django/Wagtail full HTML through Fusion | Content + backend |
| Enroll, save, filter, and other small updates | HTMX fragment | Backend + frontend |
| Learner dashboard and course-player islands | Astro plus JSON data API | Frontend + learning |
| Local route and design work | Local Compose overlay | Engineering |
| Release candidate and host rollout | Base production Compose | Infrastructure |

## References

- [Precis product docs](../../../precis/README.md)
- [Fusion render-flow reference](../../../precis/landing-fusion-render-flow.html)
- [Precis Main project-local docs](../../../../projects/structa.cloud/docs/README.md)
- [Precis feature tracking](../../feature-tracking/precis-main.md)
- [Precis delivery report](../reports/precis-main-delivery.md)

## Remarks & Notes

- The project-local HTML reference intentionally mirrors the canonical product page so it remains available beside the source tree in an isolated checkout.
- Do not use the local overlay for a production rollout, and do not use production deployment targets as a substitute for a local preview.
- Keep the Makefile, Nx metadata, Compose files, proxy configuration, and this object in sync when a command or service changes.

<!-- AI-generated: review needed -->
