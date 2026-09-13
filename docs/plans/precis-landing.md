# Precis Landing plans

> **Status:** Active  
> **Owner:** Precis Landing team  
> **Project:** [`projects/precis/precis-landing/`](../../projects/precis/precis-landing/) (legacy Precis Landing copy; the unified product lives in `projects/precis/precis-main/`)

Precis Landing is the Astro + Tailwind + HTMX + Alpine frontend paired with the Django + Wagtail editable content backend. This page is the canonical plan entry point under the main documentation project.

## Current implementation boundary

- Frontend: Astro pages, shared layout, Fusion theme tokens, HTMX/Alpine interactions, dark mode, skeleton/loading states.
- Backend: Django/Wagtail page models, StreamField content blocks, django-fusion handlers, seed data, page/content tests.
- Content contract: code sections and live HTML previews are authored and rendered on BlogPost pages; ordinary product/prompt surfaces remain presentation-only.

## Recommended execution order

1. Run the backend page/content tests and the frontend `npm run check` before changing block contracts.
2. Finish the remaining blog/content and preview acceptance coverage.
3. Add Playwright coverage and Docker/Traefik wiring only after the local backend/frontend checks remain green.
4. Keep new landing implementation plans in this directory and link them from [`docs/plans/README.md`](README.md).

## Verification

```bash
cd projects/precis/precis-landing/backend && make check && make test
cd ../frontend && npm run check
```

Use the project README for the current quickstart and code map. This plan intentionally records the current boundary without duplicating implementation details from the source tree.

## Planned background and AI work

Precis Landing project-owned email, editorial, cache, and AI-draft tasks must
follow the shared django-fusion task and AI plans. AI output remains an
unpublished editorial draft until an authorized user approves it; provider SDKs
and secrets stay in the backend/worker boundary, never in Astro browser code.

- [`django-fusion/django-fusion-tasks-mcp-plan.md`](django-fusion/django-fusion-tasks-mcp-plan.md) — unified tasks and task MCP
- [`django-fusion/django-fusion-llm-mcp-enhancement-plan.md`](django-fusion/django-fusion-llm-mcp-enhancement-plan.md) — provider-neutral LLM routing, caching, streaming, and AI governance

## Related

- [`../recommendations.md`](../recommendations.md) — recommended priority order
- [`README.md`](README.md) — canonical plan registry
- [`projects/precis/precis-landing/`](../../projects/precis/precis-landing/) — legacy landing site tree (unified product quickstart: [`projects/precis/precis-main/README.md`](../../projects/precis/precis-main/README.md))
- [`document-lifecycle.md`](document-lifecycle.md) — plan lifecycle and archive policy
