---
Object type: Workspace
Tags: anytype, documentation, pos, formint, knowledge-graph
Status: Active
---

# Anytype Documentation Hub

> Focused import set for Structa Cloud products. Each document uses a small description, a clear object type, and links to related objects. Implementation documents describe responsibilities, methods, and user use cases rather than reproducing source code.

## Start here

| Document | Purpose |
|---|---|
| `guides/channel-structure.md` | Vault → Channel container model — Home, Content Model, roles |
| `architecture/editions.md` | Canonical Community, Professional, and SaaS edition boundaries |
| `plans/formint-pos-professional-plan.md` | Formint Professional product and delivery contract |
| `plans/forge-migration.md` | Forge feature-transfer and retirement gates |
| `plans/tauri-desktop.md` | Formint native desktop tools and use cases |
| `plans/cloud.md` | Cloud-only multi-branch transport and operating model |
| `plans/pos-market-research.md` | Market research for Community, Formint Professional, and POS Cloud |
| `plans/project-workspace.md` | Portfolio workspace and planning hub |
| `plans/projects.md` | Repository and project workspace directory (merged from projects-list) |
| `plans/marketing-campaigns.md` | Campaign briefs and KPIs |
| `plans/sales.md` | Sales funnel and online conversion |
| `plans/online-commerce.md` | Online selling and customer trust |
| `plans/social-networks.md` | Social and community channels |
| `plans/team.md` | Team ownership and operating model |
| `products/formint-pos.md` | Product description and positioning |
| `products/_index.md` | Product portfolio index |
| `stories/starting-the-project.md` | Founder journey — how the project started |
| `goals/achievement-board.md` | Goals-as-tracker / achievement board by phase |
| `plans/startup-planner.md` | Startup product and business strategy |
| `projects/_index.md` | Bounded initiatives (Loop-CRM merge, editions chain, docs) |
| `editions/_index.md` | Formint + Precis edition tiers |
| `diagrams/_index.md` | Rendered diagram objects (SVGs + mermaid sources) |
| `objects/_object-types.md` | Object type definitions and properties |
| `objects/_tags.md` | Shared tag vocabulary |
| `objects/_relations.md` | Relations for the Anytype graph |
| `guides/pos-documentation-system.md` | Import and organization rules |

## Container model

This hub imports as **one Anytype Channel** (Vault → Channel → Objects). All Types, Properties, and Templates below are created in that Channel's Content Model; see `guides/channel-structure.md` before importing.

## Focused organization

- **architecture/** — System and edition boundaries
- **features/** — Capability descriptions and edition behavior
- **plans/** — Workspace, product, delivery, marketing, sales, and market decisions
- **products/** — Customer-facing product descriptions and positioning
- **projects/** — Bounded initiatives (Loop-CRM merge, editions chain, CTC, docs)
- **editions/** — Customer-facing edition tiers (Formint chain, Precis unified)
- **sprints/** — Time-boxed delivery cycles
- **releases/** — Version and deployment history
- **integrations/** — External connectors and channels
- **apis/** — Endpoint contracts (Loop-CRM roads, django-fusion surface)
- **components/** — Reusable UI/logic building blocks
- **tools/** — Capabilities and utilities (Tauri, Blinko, Docus, SurrealDB, Postgres/Redis)
- **pipelines/** — CI/CD and docs automation
- **styles/** — Design tokens and visual identity
- **diagrams/** — Rendered diagram objects (SVGs + mermaid sources)
- **reports/ · dashboards/ · data-pipelines/ · methodologies/ · insights/ · recommendations/** — Data-analysis layer
- **repositories/ · modules/ · documentation/** — Monorepo structure layer
- **stories/** — Founder journeys and project narratives
- **goals/** — Goals, objectives, and the achievement board
- **objects/** — Object types, relations, tags, and templates (schema)
- **guides/** — Import, channel-structure, and working methods
- **decisions/** — Durable architecture decisions

## Writing rules

- Every file is a **complete document**: frontmatter → H1 → one-line description → body → `Related` links (anatomy in `objects/_templates.md`)
- Use one focused document per decision or product concern
- Use minimal kebab-case names; do not create suffixed duplicates
- Put `Object type`, `Tags`, and `Status` in frontmatter
- Describe a tool by its responsibility, method, and user use case; do not paste implementation code
- Keep repository plans as the detailed engineering source; Anytype copies are concise knowledge-graph objects
- Treat `pos-solo`, `pos-full`, and Forge as migration labels, not new product editions
- Import the focused POS set first; legacy Anytype pages remain historical references until individually normalized

## Related

- → `architecture/editions.md` — Edition architecture
- → `plans/formint-pos-professional-plan.md` — Canonical Professional object
- → `plans/pos-market-research.md` — Edition market research
- → `objects/_object-types.md` — Object type reference
- → `objects/_relations.md` — Relation reference
- → `objects/_tags.md` — Tag reference
- → `guides/pos-documentation-system.md` — Import method
