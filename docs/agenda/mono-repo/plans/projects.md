---
Object type: Workspace
Tags: workspace, projects, planning, repository, portfolio
Status: Active
Related Projects: ctc-research, lms, portfolio, cypercloud, formint-pos
Related Products: formint-pos
Related Plans: project-workspace, product-development
Related Teams: product, engineering
---

# Projects — Directory & Repository Workspace

> **Description:** Navigation hub for Structa Cloud sites, libraries, infrastructure, and the current Formint product workspace. Combines directory navigation with detailed site and application references.

## Current web and platform projects

| Project | Path | Purpose | Responsibility | Status |
|---|---|---|---|---|
| CTC Research | `projects/ctc-research/` | Research and training site | Research publication and training workflows | Active |
| LMS Demo | `projects/lms/` | Learning management demonstration | Course creation, enrollment, and learner dashboards | Active |
| Portfolio | `projects/portfolio/` | Portfolio and resume site | Portfolio and resume presentation | Active |
| CyperCloud | `projects/cypercloud/` | AI chat customization platform | AI chat customization and model configuration | In Development |
| Formint POS | `projects/pos/` | Restaurant POS product workspace | Restaurant operations product workspace | In Development |
| django-fusion | `libs/django-fusion/` | Shared Django component and routing library | Component routing, generic views, forms, tables, and fragments | Active |
| ceptor-ai | `libs/ceptor-ai/` | AI client and MCP tooling | AI client, MCP server, and generation helpers | Active |

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
