# Loop-CRM — Documentation Index

> **Canonical product path:** `projects/loop-crm/`
> **Runtime identity:** `loop-crm`
> **Main docs:** [`docs/loop-crm/`](../../../docs/loop-crm/README.md)

<!-- AI-generated: review needed -->

This directory is the **project docs project** for Loop-CRM, the unified sales +
marketing platform (Twenty DNA + Postiz DNA) on Django + django-fusion.

## 📚 Project Docs

| Doc | Covers |
|-----|--------|
| [Setup & Build](SETUP_AND_BUILD.md) | Step-by-step startup, backend + frontend setup, build and run commands |
| [Design System](DESIGN_SYSTEM.md) | Industrial-brutalist / tactical telemetry design tokens, typography, layout, components |
| [Fusion Forms & Tables](FUSION_FORMS_TABLES.md) | Fusion table/form contract backed by django-fusion RowGenerator |
| [Architecture & Extensions](ARCHITECTURE_AND_EXTENSIONS.md) | Twenty/Postiz parity, request diagrams, pipeline/workflow ordering, custom fields/forms, and Wagtail authoring |

## 🔒 Startup Strategy

- [Loop-CRM market strategy](../../../docs/startup/loop-crm.md) — MVP canvas, TAM/SAM/SOM, SaaS services, ideal clients, research backlog
- [Full portfolio strategy](../../../docs/startup/STRATEGY.md) — consolidated master

## 🔗 Related

- [Main docs — Loop-CRM](../../../docs/loop-crm/README.md) — reader-facing docs incl. env contract and commands
- [django-fusion](../../../libs/django-fusion/README.md) — shared framework used by this product

## Remarks & Notes

- Render-first: Django renders data screens (fusion tables/forms); the Astro
  shell requests `/fragments`, `/apis/core`, `/bolt`, and `/accounts` through
  the configured same-origin roads.
- No fabricated frontend data: request failures show an explicit unavailable
  state, while successful zero-row responses show the page's no-data state.
- The architecture guide includes Mermaid request, HTMX/Alpine, realtime,
  worker, domain, admin, and deployment diagrams.
- See the main docs README for the full env/config contract and command table.