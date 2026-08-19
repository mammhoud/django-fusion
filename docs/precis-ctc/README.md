# CTC Research Documentation

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

- [Project docs index](../../projects/precis/precis-ctc/docs/README.md)
- [Content map](../../projects/precis/precis-ctc/docs/CONTENTS.md)
- [Component registry and frontend components](../../projects/precis/precis-ctc/docs/COMPONENTS.md)
- [Template architecture](../../projects/precis/precis-ctc/docs/TEMPLATES.md)
- [Setup and build](../../projects/precis/precis-ctc/docs/SETUP_AND_BUILD.md)
- [Environment and redeploy](../../projects/precis/precis-ctc/docs/ENVIRONMENT.md)
- [Enhancement register](../../projects/precis/precis-ctc/docs/ENHANCEMENTS.md)
- [Learning cases & techniques](../../projects/precis/precis-ctc/docs/LEARNING_CASES.md)
- [Publish plan](../plans/repository/ctc-research-publish-2026-08-18.md)
- [Cross-module workflows](../plans/repository/precis-ctc-workflows.md)

## Content & publishing

- [Content strategy, ICP & market research](content-strategy.md)
- [Publishing workflow & production notes](publishing-and-production.md)

## Startup strategy 🔒

- [CTC Research market strategy](../startup/precis-ctc.md) — MVP canvas, TAM/SAM/SOM, SaaS services, ideal clients, research backlog
- [Full portfolio strategy](../startup/STRATEGY.md) — consolidated master

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
are in [Environment and redeploy](../../projects/precis/precis-ctc/docs/ENVIRONMENT.md).

## Remarks & Notes

- The filesystem path `projects/precis/precis-ctc/` is canonical. Do not create new code under historical paths such as `projects/precis-ctc/` or `projects/precis/lms-ctc/`.
- Public medical, legal, image-rights, and translation content requires CTC owner review before production publication.
- Generated bundles, collected static files, and runtime media are different asset classes; follow the environment guide rather than copying one into another.
