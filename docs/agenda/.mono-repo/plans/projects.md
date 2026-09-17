---
Object type: Workspace
Tags: workspace, projects, planning, repository
Status: Active
Related Projects: precis-main, precis-ctc, syntara, loop-crm, formint-editions-chain
Related Products: formint-pos, precis-lms
Related Plans: project-workspace, product-development
Related Teams: product, engineering
---

# Projects — Directory & Repository Workspace

> **Description:** Navigation hub for Structa Cloud sites, libraries, infrastructure, and the current Formint product workspace. Combines directory navigation with detailed site and application references.
> **Paths normalized 2026-09-10** to the current tree (see repo `AGENTS.md` migration rules).

## Current web and platform projects

| Project | Path | Purpose | Responsibility | Status |
|---|---|---|---|---|
| Precis (unified) | `projects/structa.cloud/` | LMS + marketing catalog (merged) | Courses, enrollment, progress, catalog, SEO | Active |
| CTC Research | `projects/precis/precis-ctc/` | Research and training site | Research publication and training workflows | Active |
| Syntara (Cypercloud) | `projects/syntara/` | AI chat customization platform | AI chat customization and model configuration | In Development |
| Loop-CRM | `projects/loop-crm/` | CRM + social scheduling | Pipelines, campaigns, finance, AI hub | Active |
| Formint POS | `projects/formints/` | Restaurant POS product workspace | Restaurant operations product workspace | In Development |
| django-fusion | `libs/django-fusion/` | Shared Django component and routing library | Component routing, generic views, forms, tables, and fragments | Active |
| ceptor-ai | `libs/ceptor-ai/` (submodule, pending init) | AI client and MCP tooling | AI client, MCP server, and generation helpers | Active (external) |

> Retired paths — `projects/lms` (merged into precis-main), `projects/portfolio`
> (VResume, not pursued), `projects/tinker` (superseded by Syntara),
> `projects/pos` (now `projects/formints/`), `projects/cypercloud` (now
> `projects/syntara/`), `projects/ctc-research` (now under `projects/precis/`).
> Git history is the archive.

## Formint POS workspace

Restaurant operations product workspace containing the current desktop/application work and the path toward managed cloud services.

- **Product model:** Community, Formint Professional, POS Cloud
- **Professional boundary:** offline-capable local operations, restaurant workflows, KDS, catalog, inventory, reports, and integrations as released
- **Cloud boundary:** hosted tenants, branch coordination, analytics, billing, backups, and managed integrations
- **Status:** In Development

### POS product labels

The current customer-facing model is:

- **Community** — free/self-hosted core POS
- **Formint Professional** — offline-capable restaurant operations and premium workflows
- **POS Cloud** — hosted branches, analytics, billing, backups, and managed services

`pos-mini`, `pos-solo`, `pos-full`, and Forge are implementation or migration labels. Keep them in migration and historical objects only; do not use them as current product editions.

## Infrastructure projects

| Component | Path | Responsibility |
|---|---|---|
| Proxy | `applications/proxy/` | TLS, routing, and certificates |
| Databases | `applications/databases/` | PostgreSQL and Redis |
| Compose | `applications/compose/` | Service orchestration |

## Use

Use this page for navigation, not for detailed product or implementation claims. Link a project to its Product, Plans, Teams, and evidence objects. Update status when repository ownership or delivery state changes.

## Related

- → `project-workspace.md` — Portfolio planning hub
- → `product-development.md` — Product lifecycle
- → `../products/formint-pos.md` — Formint product
- → `../objects/_status.md` — Anytype lifecycle status
- → `../README.md` — Anytype hub
