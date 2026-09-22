---
Object type: Workspace
Tags: plans, strategy, workspace, business
Status: Active
---

# Plans — Workspace, Product & Go-to-Market

> Business, product, delivery, marketing, sales, online selling, social, team, research, and operating plans. Each plan links back to a workspace, project, product, team, or evidence object.

> **Note:** Legacy duplicates (`_legacy/networking-detailed`, `_legacy/marketing-strategy-expanded`, `_legacy/operational-plan-expanded`, `_legacy/risk-management-detailed`, `_legacy/start-up`, `_legacy/projects-list`) are preserved as Historical stubs in `_legacy/` and redirect to their canonical files.

## Workspace and portfolio

| Document | Description |
|---|---|
| `project-workspace.md` | Portfolio hub linking projects, products, plans, teams, and evidence |
| `projects.md` | Repository and project workspace directory (merged from projects-list) |

## Product and delivery

| Document | Description |
|---|---|
| `formint-pos-professional-plan.md` | Canonical Formint Professional product and delivery contract |
| `product-development.md` | Evidence-led lifecycle from research to release and learning |
| `forge-migration.md` | Forge-to-Formint parity and retirement gates |
| `tauri-desktop.md` | Formint native desktop tools and use cases |
| `cloud.md` | POS Cloud operating model and cloud-only transport boundary |
| `operational-plan.md` | Operations, deployment, customer service, and recovery |
| `monitoring.md` | Monitoring, evaluation, and metrics |

## Marketing, sales and online selling

| Document | Description |
|---|---|
| `marketing-strategy.md` | Integrated positioning, campaigns, channels, and sales strategy |
| `marketing-campaigns.md` | Campaign briefs, messages, proof, channels, and KPIs |
| `sales.md` | Funnel, demos, pilots, proposals, onboarding, and expansion |
| `online-commerce.md` | Product pages, checkout, fulfillment, trust, and support |
| `social-networks.md` | Social, community, content, and partnership channels |
| `networking.md` | Community and partnership building |
| `team.md` | Team ownership, members, and periodic operating tasks |

## Research and business

| Document | Description |
|---|---|
| `pos-market-research.md` | POS edition market hypotheses and validation questions |
| `market-research.md` | General Structa Cloud research; keep separate from POS research |
| `business-model.md` | Business Model Canvas and revenue hypotheses |
| `resources.md` | Resource allocation and partnership planning |
| `risk-management.md` | Financial, operational, reputational, and strategic risks |
| `legal-compliance.md` | Legal and regulatory compliance |

## Startup and measurement

| Document | Description |
|---|---|
| `startup-planner.md` | Startup planning and strategy (canonical; start-up is historical) |

## Story and origin

| Document | Description |
|---|---|
| `../stories/starting-the-project.md` | Founder journey — how the project started and evolved |
| `../stories/notes/start-up-journal.md` | Raw working notes from the start |

The founder story and its planning context are connected: the narrative (**Story**) explains why things were done while the planning docs define what will be done. The `goals/achievement-board.md` tracks the outcomes each story phase delivered.

## Graph rules

- Use `Object type: Plan` for campaign, sales, commerce, social, product development, and team operating plans
- Use `Product` for customer-facing product descriptions and positioning
- Use `Project` for bounded initiatives and `Workspace` for portfolio or initiative hubs
- Link channels as `Integration` objects through `Related Channels`
- Keep price, market size, conversion, compliance, and performance claims as hypotheses until evidence is recorded

## Related

- → `../README.md` — Anytype hub
- → `../objects/_object-types.md` — Type definitions
- → `../objects/_relations.md` — Relations
- → `../objects/_templates.md` — Templates
- → `../products/_index.md` — Product portfolio
- → `../objects/_status.md` — Lifecycle status
