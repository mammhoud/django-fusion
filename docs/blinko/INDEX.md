---
title: Blinko Notes Index
description: Central index for all Blinko team plans, roles, and launch documentation
navigation:
  title: Blinko Notes
  icon: i-lucide-book-open
---

# 📚 Blinko Notes — Team Plans & Launch Documentation

> **Purpose:** Consolidated reference for all team plans, roles, and launch steps across Structa Cloud products
> **Created:** 2026-08-25
> **Status:** Active working reference

---

## 📂 Directory Structure

```
docs/blinko/
├── INDEX.md                          # This file
├── dev-team-plans.md                 # Development team plans & references
├── data-analyst-plans.md             # Data analyst plans & references
├── marketing-plans.md                # Marketing plans & references
├── project-launch-steps.md           # Project launch steps & references
├── launch-readiness-checklist.md     # Complete launch & publish checklist
└── tools-auth-dashboard.md           # Astro Tools Auth & Dashboard implementation
```

---

## 🎯 Quick Links by Team

| Team | Document | Key Focus |
|------|----------|-----------|
| **Development** | [dev-team-plans.md](./dev-team-plans.md) | Product vertical slices, edition chains, backend/frontend tasks |
| **Data Analyst** | [data-analyst-plans.md](./data-analyst-plans.md) | Metrics, analytics, evidence-backed claims, pilot tracking |
| **Marketing** | [marketing-plans.md](./marketing-plans.md) | Positioning, claims register, launch campaigns, Arabic-first |
| **Launch/Release** | [project-launch-steps.md](./project-launch-steps.md) | Deployment, verification, multi-product coordination |
| **All Teams** | [launch-readiness-checklist.md](./launch-readiness-checklist.md) | End-to-end readiness gates for each product |

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