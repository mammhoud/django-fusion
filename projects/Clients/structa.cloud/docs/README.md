# Precis Main project documentation

This directory contains documentation owned by the unified Precis Main project.
The repository-facing product docs live in [`../../../../docs/precis/`](../../../../docs/precis/);
project-local documents describe implementation details that belong beside the
source tree.

## Documents

| Document | Purpose |
|---|---|
| [`landing-fusion-render-flow.html`](landing-fusion-render-flow.html) | Standalone visual reference for the full HTML, HTMX fragment, Astro data API, local Compose, production Compose, and Nx paths |
| [`erd/`](erd/) | Generated data-model diagrams |

## Use cases covered

- Public catalog, blog, and SEO pages use the Django/Wagtail Fusion road.
- Small mutations and partial updates use HTMX fragments.
- Learner dashboards and course-player islands use Astro with JSON data APIs.
- Local development uses the Compose override and published localhost ports.
- Production rollout uses the base Compose file and the root deployment environment.
- Nx targets delegate to this project's Makefile so direct and graph-based workflows share one command contract.

## Source-of-truth files

- [`../Makefile`](../Makefile)
- [`../project.json`](../project.json)
- [`../docker-compose.yml`](../docker-compose.yml)
- [`../docker-compose.override.yml`](../docker-compose.override.yml)

## Remarks & Notes

- The project directory is `projects/structa.cloud/`; `precis-lms` and
  `precis-landing` are compatibility aliases, not separate current runtimes.
- Do not put credentials or a production `.env` in this documentation tree.
- Generated ERD output is not a replacement for the Django model source.

<!-- AI-generated: review needed -->
