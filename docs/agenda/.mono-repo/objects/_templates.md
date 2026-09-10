# Anytype Object Templates

> **Purpose:** Small, linked templates for the Structa Cloud **Channel**. Use these templates when creating an object in Anytype; keep implementation detail in repository plans and describe responsibilities, methods, evidence, and user use cases here.
> **Container:** create all objects inside the Structa Cloud Channel (see [`guides/channel-structure.md`](../guides/channel-structure.md)). Types and Templates are per-Channel; a separate Channel starts with its own Content Model.

## Complete-document design (file anatomy)

Every file in this set is a **complete document**: importable on its own and linkable from anywhere. A complete document has exactly this anatomy:

1. **Frontmatter** — `Object type`, `Tags`, `Status` + the type's required properties (see compact table below).
2. **H1 title** — `# <Name> — <Object type label>` (e.g. `# Product — Product Description`).
3. **One-line description** — `> **Description:** <purpose in one sentence>`.
4. **Body sections** — the type's standard sections (Purpose, Outcome, Use, Proof…). Keep prose tight; prefer compact tables.
5. **Graph section** (only for types that live in the relation graph) — a `## Graph` flow path table or mermaid snippet showing source → target relations.
6. **Related links** — `## Related` with `→ relative/path.md — reason` bullets.
7. **Status reflects reality** — an object marked `Active` is current and linked from an active index; `Archived`/`Deprecated` objects link their replacement.

A file missing any of these is an *incomplete object*, not a complete document.

### Index / hub files

Index files (`_index.md`, `README.md`, `_status.md`) are navigation objects: frontmatter + a table of links. They are not duplicates of content objects and do not need the content sections above.

## Shared frontmatter

```yaml
---
Object type: [Type]
Tags: [tag-one, tag-two]
Status: Draft
---
```

Use these lifecycle values consistently:

- `Draft` — being prepared
- `Active` — current and being used
- `Planned` — approved direction, not delivered
- `Completed` — finished historical work
- `Archived` — preserved but no longer active

## Assignments — who assigns what to whom (added 2026-09-10)

> Per anytype.io: Types are blueprints of Properties; Object-format Properties
> connect objects ("Connect Objects — link an Object to another through a
> Property, such as Assigned To → Alex"). The matrix below is the standard
> accountability wiring: every object type gets exactly one accountable
> relation and, where work is done, one doer relation.

| Object type | Accountable (one) | Doer / assigned (one) | Verifier (one) | Feeds into |
|---|---|---|---|---|
| **Task** | `Owner` → Person | `Assigned To` → Person | `Reviewer` → Person | Feature, Sprint |
| **Feature** | `Owner` → Person | `Assigned To` → Person | `Reviewer` → Person | Milestone, Release |
| **Sprint** | `Lead` → Person | `Assigned To` → Person (via Tasks) | `Reviewer` → Person | Plan |
| **Plan** | `Owner` → Person | `Related Teams` → Team | `Sign-off By` → Person | Goal, Project |
| **Milestone** | `Owner` → Person | `Related Tasks` → Task | `Sign-off By` → Person | Goal |
| **Project** | `Owner` → Person | `Related Teams` → Team | `Sign-off By` → Person | Workspace |
| **Release** | `Owner` → Person | `Related Pipelines` → Pipeline | `Reviewer` → Person | Changelog |
| **Decision** | `Owner` → Person | — | `Reviewer` → Person | Architecture |
| **Lead** (sales) | `Owner` → Person | — | `Reviewer` → Person | Product, Edition |
| **Claim** (marketing) | `Approved By` → Person | `Evidence Source` → Any | `Approved By` → Person | Market Research |
| **Guide / Reference** | `Owner` → Person | — | `Reviewer` → Person | Documentation |
| **Report / Insight** | `Owner` → Person | `Methodology` → Methodology | `Reviewer` → Person | Recommendation |

**Rules:**

1. `Owner` = accountable (exactly one Person, never a Team).
2. `Assigned To` = the doer; omit for review-type objects.
3. `Reviewer` / `Sign-off By` = the verification gate; must differ from `Assigned To` where both exist.
4. Unassigned objects are visible in the type's default "Unowned" view and are reviewed at sprint planning — an object with no `Owner` is a proposal, not a commitment.

## Default views per type (added 2026-09-10)

> Per doc.anytype.io: Views live on a Type, Query, or Collection and combine
> layout + filters + sorts (multiple sorts apply in order, first takes
> precedence). Queries are rule-driven and aggregate across Types; Collections
> are hand-curated. Save recurring filter sets as Views rather than new
> queries. Define each repeated filter once, as the Type's default view,
> instead of restating it in files.

| Type | Default view | Filter | Sort |
|---|---|---|---|
| Task | Board by status | `Status` ≠ Archived | `Priority`, `Due Date` |
| Feature | Board by lifecycle | — | `Priority` |
| Plan | Board: Active | `Status` = Active | `Target Date` |
| Lead | Table by stage | `Stage` ∈ {Lead…Negotiation} | `Next Step Date` |
| Milestone | Timeline | — | `Target Date` |
| Claim | Table: due for review | `Review Date` ≤ quarter end | `Review Date` |
| Unowned (all types) | Table: no owner | `Owner` is empty | `Created` |
- `Deprecated` — replaced; link the replacement

## Workspace

```markdown
---
Object type: Workspace
Tags: workspace, planning
Status: Active
Related Projects: [project]
Related Products: [product]
Related Plans: [plan]
Related Teams: [team]
---

# [Workspace name]

> **Description:** [Purpose of this portfolio or initiative hub.]

## Purpose
[Business or project purpose.]

## Operating view
[How projects, products, plans, research, channels, and teams are reviewed.]

## Related
- → `[relative/path.md]` — [reason for the link]
```

## Project

```markdown
---
Object type: Project
Tags: projects, planning
Status: Active
Owner: [person]
Related Workspace: [workspace]
Related Products: [product]
Related Teams: [team]
Related Plans: [plan]
---

# [Project name]

> **Description:** [Bounded outcome and delivery boundary.]

## Outcome
[What will be different when this project is complete?]

## Scope and gates
- In scope: [items]
- Out of scope: [items]
- Completion evidence: [test, pilot, or decision]

## Related
- → `[relative/path.md]` — [relationship]
```

## Product

```markdown
---
Object type: Product
Tags: product, positioning
Status: Active
Product Type: Application
Related Editions: [edition]
Related Features: [feature]
Related Plans: [plan]
Related Research: [research]
Related Campaigns: [campaign]
Related Teams: [team]
---

# [Product name] — Product Description

> **Description:** [Customer-facing outcome in one sentence.]

## Audience and problem
[Who has the problem and what they need.]

## Promise and boundaries
[What the product does, does not do, and how it differs by edition.]

## Proof to collect
- [Pilot, acceptance test, customer interview, or released workflow]

## Related
- → `[relative/path.md]` — [relationship]
```

## Plan

```markdown
---
Object type: Plan
Tags: planning, product-development
Status: Planned
Type: Product Development
Owner: [person]
Related Workspace: [workspace]
Related Project: [project]
Related Products: [product]
Related Editions: [edition]
Related Goals: [goal]
Related Teams: [team]
---

# [Plan name]

> **Description:** [Decision, outcome, time boundary, and method.]

## Objective
[Measurable intended result.]

## Method and milestones
1. [Step] — [evidence]
2. [Step] — [evidence]

## Risks and assumptions
- [Risk or unverified assumption]

## Related
- → `[relative/path.md]` — [relationship]
```

## Marketing campaign

Use `Object type: Plan` with `Type: Marketing Campaign`; campaigns are plans, not a second campaign type.

```yaml
Object type: Plan
Tags: marketing, campaign, content
Status: Planned
Type: Marketing Campaign
Related Products: [product]
Related Plans: [marketing-strategy, sales]
Related Channels: [website, email, linkedin]
Related Teams: [marketing, sales]
```

Required content: audience, problem, message, evidence, offer, channel, owner, KPI, review date, and claim approval status.

## Sales and online commerce

Use `Object type: Plan` with `Type: Sales` or `Type: Commerce`.

```yaml
Object type: Plan
Tags: sales, online-commerce
Status: Planned
Type: Sales
Related Products: [product]
Related Plans: [campaign, online-commerce]
Related Teams: [sales, support]
```

Record funnel stages, exit evidence, commercial terms, consent, fulfillment, support, renewal, and expansion. Never present price or conversion targets as achieved results without evidence.

## Social networks and channels

Use `Object type: Plan` with `Type: Social` and link each channel through `Related Channels` to an `Integration` object. Use `Integration.Category` values `Social`, `Community`, `Commerce`, or `Partner` where appropriate.

## Team and person

- `Team` represents a durable function or workstream.
- `Person` represents one individual.
- Link `Person → Member Of → Team` and `Team → Lead → Person`.
- Keep private personal data outside the knowledge graph.

## Compact frontmatter

| Object type | Required fields |
|---|---|
| Workspace | Status, Purpose, Related Projects, Related Products |
| Project | Status, Owner, Related Workspace, Related Products |
| Product | Status, Product Type, Related Editions, Related Plans |
| Team | Status, Team Type, Members, Lead |
| Plan | Status, Type, Owner, Related Products or Projects |
| Market Research | Status, Type, Related Editions, Evidence |
| Tool | Status, Category, Edition, Method, Use Case |
| Feature | Status, Related Editions, Priority |
| Guide | Status, Category, Target Audience |

## Market research

```yaml
Object type: Market Research
Tags: market-research, validation
Status: Active
Type: Edition
Editions: [edition]
Related Products: [product]
Related Plans: [plan]
```

Separate evidence, assumptions, validation questions, and decision impact.

## Tool

```yaml
Object type: Tool
Tags: tool, method, use-case
Status: Planned
Category: Desktop
Edition: Formint Professional
Related Features: [feature]
Related Plan: [plan]
```

Describe responsibility, method, boundary, guardrails, and user use case. Do not paste source code.

## Canonical relation naming

Use plural names for multi-value relations:

- `Related Projects`, `Related Products`, `Related Plans`, `Related Editions`
- `Related Features`, `Related Campaigns`, `Related Channels`, `Related Teams`
- `Related Research`

Use singular names only for one accountable object: `Owner`, `Lead`, `Related Project`, or `Related Workspace`.

## Naming and import rules

- Use short kebab-case filenames without `_c`, `_h`, `_r`, `copy`, or `untitled` suffixes.
- Every content object has `Object type`, `Tags`, and `Status` frontmatter.
- Every active object links to its parent workspace, product, project, plan, or team where applicable.
- Index files are navigation objects; they are not duplicated content objects.
- Preserve historical documents, but label them `Archived` or `Deprecated` and link their replacement.

## Related

- → `_object-types.md` — Type and property definitions
- → `_relations.md` — Canonical relation names
- → `_tags.md` — Shared tag vocabulary
- → `../guides/pos-documentation-system.md` — Writing and import method
