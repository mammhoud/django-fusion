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

- **startup-story.md** — Founder journey story + goals-as-achievement tracking
- **dev-team-plans.md** — Product vertical slices, edition chains, and engineering tasks
- **backend-plans.md** — Backend architecture, API design, and database planning
- **pricing-plans.md** — Pricing strategy, revenue targets, and feature-based pricing
- **data-analyst-plans.md** — Metrics, evidence tracking, and pilot validation
- **marketing-plans.md** — Positioning, claims register, and launch campaigns
- **tools-auth-dashboard.md** — Tools dashboard and authentication implementation

---

## Quick Links by Team

| Team | Document | Key Focus |
|------|----------|-----------|
| **Development** | [dev-team-plans.md](./dev-team-plans.md) | Product vertical slices, edition chains, backend/frontend tasks |
| **Backend** | [backend-plans.md](./backend-plans.md) | Backend architecture, API design, database planning |
| **Data Analyst** | [data-analyst-plans.md](./data-analyst-plans.md) | Metrics, analytics, evidence-backed claims, pilot tracking |
| **Marketing** | [marketing-plans.md](./marketing-plans.md) | Positioning, claims register, launch campaigns, Arabic-first |
| **Pricing** | [pricing-plans.md](./pricing-plans.md) | Pricing strategy, revenue targets, feature-based pricing |

---

## 🔗 Canonical References (Always Current)

| Reference | Path | Purpose |
|-----------|------|---------|
| **Plan Registry** | `docs/plans/README.md` | Single source of truth for all engineering plans |
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
- Arabic/English parity is maintained via `docs/ar-content/` mirror structure

<!-- AI-generated: review needed -->

---

## 📂 New: Project Agenda System (2026-08-31)

Complete project agenda system for team tracking, case studies, task management, and project completion.

| Document | Purpose |
|----------|---------|
| [`MAIN.md`](./MAIN.md) | Hub and index — how everything connects |
| [`feature-tracking.md`](./feature-tracking.md) | Feature lifecycle tracking |
| [`case-studies.md`](./case-studies.md) | Real implementations with mermaid diagrams |
| [`task-tracking.md`](./task-tracking.md) | Sprint task board |
| [`team-notes.md`](./team-notes.md) | Meeting notes and decisions |
| [`meeting-agenda.md`](./meeting-agenda.md) | Meeting templates |
| [`completion-checklist.md`](./completion-checklist.md) | Project closeout checklist |
| [`README.md`](./README.md) | Agenda system overview |

See `MAIN.md` for the full system overview and how to use it.