---
Object type: Index
Tags: index, navigation, reference
Status: Active
---

# Blinko Notes — Team Plans & Launch Documentation

> **Purpose:** Consolidated reference for all team plans, roles, and launch steps across Structa Cloud products
> **Created:** 2026-08-25
> **Status:** Active working reference

---

## Documents at a glance

- **CONTENT_MODEL.md** — ⭐ The agenda definition: Anytype concept glossary, object/markdown packaging (4 packages), and the team reference contract
- **.mono-repo/** — Package B — the Anytype object graph: type definitions + per-type content objects (projects, editions, sprints, releases, integrations, APIs, components, tools, pipelines, styles, diagrams, reports, dashboards, methodologies, insights, recommendations, repositories, modules, documentation) + install guides
- **diagrams/** — Rendered diagram images + mermaid sources: API request UML, Django/Rust ERDs, Blinko SurrealDB
- **startup-story.md** — Founder journey story + goals-as-achievement tracking
- **dev-team-plans.md** — Product vertical slices, edition chains, and engineering tasks (incl. backend workstreams; `backend-plans.md` merged 2026-09-10)
- **pricing-plans.md** — Pricing strategy, revenue targets, and feature-based pricing
- **data-analyst-plans.md** — Metrics, evidence tracking, and pilot validation
- **marketing-plans.md** — Positioning, claims register, and launch campaigns
- **roles/** — Per-role working plans: tasks, validation steps, and collaborators for each team member

---

## Quick Links by Team

| Team | Document | Key Focus |
|------|----------|-----------|
| **Development** | [dev-team-plans.md](./dev-team-plans.md) | Product vertical slices, edition chains, backend/frontend tasks |
| **Data Analyst** | [data-analyst-plans.md](./data-analyst-plans.md) | Metrics, analytics, evidence-backed claims, pilot tracking |
| **Marketing** | [marketing-plans.md](./marketing-plans.md) | Positioning, claims register, launch campaigns, Arabic-first |
| **Pricing** | [pricing-plans.md](./pricing-plans.md) | Pricing strategy, revenue targets, feature-based pricing |

---

## 🔗 Canonical References (Always Current)

| Reference | Path | Purpose |
|-----------|------|---------|
| **Agenda Content Model** | `docs/agenda/CONTENT_MODEL.md` | Agenda definition, packaging, and the plans → milestones reference contract |
| **Plan Registry** | `docs/plans/README.md` | Single source of truth for all engineering plans |
| **Finished Milestones** | `docs/agenda/feature-tracking/<product>.md` § ✅ Shipped (hub: `docs/agenda/feature-tracking.md`) | Backward map of completed plans recorded as milestones |
| **Recommendations** | `docs/recommendations.md` | Prioritized next actions & sequencing |
| **Project Awareness** | `docs/guides/00-project-awareness.md` | Object graph, commands, computation paths |
| **Repository Overview** | `docs/overview.md` | Project map, stack, infrastructure, name migrations |
| **Architecture** | `docs/ARCHITECTURE.md` | Full system architecture & request flows |
| **Marketing Claims** | `docs/plans/marketing-claims.md` | Evidence-backed marketing claims register |
| **Document Lifecycle** | `docs/plans/document-lifecycle.md` | Status, ownership, archive, deletion policy |

---

## 🏗️ Current Product Vertical Slices (Active)

| Product | Canonical Path | Status | Dispatcher Target |
|---------|---------------|--------|-------------------|
| **Formint Edition Chain** | `projects/formints/` | Active | `WEBSITE=formint-pro`, `formint-cloud`, `formint-community` |
| **Precis LMS (unified)** | `projects/precis/precis-main/` | Active | `WEBSITE=precis-main` |
| **Precis Landing** | `projects/precis/precis-landing/` | Active (legacy copy) | `WEBSITE=precis-landing` |
| **CTC Research** | `projects/precis/precis-ctc/` | Active | `WEBSITE=precis-ctc` |
| **Syntara (Cypercloud)** | `projects/syntara/` | Active | `WEBSITE=syntara` |
| **Loop-CRM** | `projects/loop-crm/` | Merge in progress | — |
| **django-fusion** | `libs/django-fusion/` | Active library | — |

---

## 📋 Usage Guidelines

1. **Read the canonical references first** — these Blinko notes are lightweight pointers, not replacements
2. **Update when plans change** — keep references synchronized with `docs/plans/README.md`
3. **Cross-reference by stable IDs** — use the `object.id` from Docus frontmatter for links
4. **Minimal content principle** — each file contains only essential context + links to authoritative sources

---

## 🔄 Maintenance

- **Owner:** Workspace / Product leads
- **Review cadence:** Per sprint planning + major release gates
- **Archive policy:** Follow `docs/plans/document-lifecycle.md`

---

## Remarks & Notes

- These notes complement (not replace) the canonical plan registry at `docs/plans/README.md`
- Product-specific plans live in `docs/plans/editions/`, `docs/plans/repository/`, `docs/plans/loop-crm/`, `docs/plans/django-fusion/`
- Marketing evidence requirements are defined in `docs/plans/marketing-claims.md`
- Arabic policy (clarified 2026-09-10): agenda **hub + plans-family** files carry
  Arabic summary blocks inline (see MAIN.md § Language policy); **case studies**
  are English-only by design; **product docs** maintain EN/AR parity via the
  `docs/ar-content/` mirror structure

<!-- AI-generated: review needed -->

---

## 📂 Project Agenda System

The working agenda (feature tracking, case studies, task board, team notes,
meeting templates, closeout) lives in this directory. See
[`README.md`](./README.md) for the overview and [`MAIN.md`](./MAIN.md) for the
hub — this file is the legacy Blinko-style pointer index and no longer
restates the agenda tables.