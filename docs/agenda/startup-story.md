---
title: Startup Story & Achievement Tracking
description: The founder journey by phase, the achievement board, the team, and the ventures in flight.
navigation:
  title: Startup Story
  icon: i-lucide-rocket
object:
  type: "story"
  id: "agenda.startup-story"
attributes:
  source_path: "agenda/startup-story.md"
  canonical_route: "/docs/en/agenda/startup-story"
  source_of_truth: "repository-markdown"
  owner: "workspace"
  status: "active"
tags:
  - structa-cloud
  - startup
  - founder
links:
  - label: "Role Plans"
    to: "/agenda/roles"
    icon: "i-lucide-users"
  - label: "Agenda Home"
    to: "/agenda/main"
    icon: "i-lucide-clipboard-list"
---

# Startup Story & Achievement Tracking

> **Purpose:** Summary pointer to the detailed founder journey and the phase-by-phase achievement board in the mono-repo documentation.
> **Status:** Active reference

---

## Story — how the project started

The full narrative of starting the project — from a first Django experiment through small sites, scalability learnings, the django-fusion component system, CMS/AI flexibility, and the desktop + cloud platform — is captured as a story in chronological phases.

**Read the full story:** `.mono-repo/stories/starting-the-project.md`

**The journey in one line:** Django small sites → htmx/Alpine/WebSockets → multi-tenant scalable databases + OAuth → API/AI/agentic backend → LMS, websites, CRM → django-fusion components → Wagtail CMS with flexible AI → Tauri desktop + cloud → documentation + Coder workspace.

## Goals as a tracker / achievement board

The goals are tracked as an achievement board organized by story phase, with each delivered item marked achieved.

**View the board:** `.mono-repo/goals/achievement-board.md`

| Category | Achieved |
|----------|:--------:|
| Technical | 10 |
| Product | 6 |
| Platform | 3 |

## Who is on it

The venture is run by four people, each with a role and a minimal working plan
in [`roles/`](./roles/README.md):

| Person | Role | Runs | Plan |
|--------|------|------|------|
| **Mahmoud** | General Manager + Full-stack | Direction, money, end-to-end delivery | [`roles/mahmoud-gm.md`](./roles/mahmoud-gm.md) |
| **Moustafa** | Product Manager + Marketing | Roadmap, acceptance, positioning | [`roles/moustafa-pm.md`](./roles/moustafa-pm.md) |
| **Yahia** | Front-end + UX Design | Design drafts, screens, flows | [`roles/yahia-frontend.md`](./roles/yahia-frontend.md) |
| **Asmaa** | Data Development | Metrics, evidence, pilots | [`roles/asmaa-data.md`](./roles/asmaa-data.md) |

## The ventures (startup portfolio)

Each venture is tracked as a project object and keeps one next step:

| Venture | Project object | Next milestone |
|---|---|---|
| Formint POS editions chain | `.mono-repo/projects/formint-editions-chain.md` | One edition shipping to desktop + mobile |
| Loop-CRM merge | `.mono-repo/projects/loop-crm-merge.md` | Workspace CRM with multi-tenant schemas |
| Precis platform (LMS + landing) | `.mono-repo/projects/docs-agenda-system.md` | Unified product surface live |
| CTC research platform | `.mono-repo/projects/ctc-research-platform.md` | Research site published with its own theme |
| django-fusion library | `.mono-repo/projects/django-fusion-library.md` | Shared components consumed by all products |

## Where planning lives

The narrative feeds into planning:

- **Strategy:** `.mono-repo/plans/startup-planner.md`, `.mono-repo/plans/business-model.md`
- **Product lifecycle:** `.mono-repo/plans/product-development.md`
- **Portfolio workspace:** `.mono-repo/plans/project-workspace.md`

## Working notes

Raw capture notes from the start of the project are kept separately:

- `.mono-repo/stories/notes/start-up-journal.md`

---

## Maintenance

- **Owner:** Founder / Product
- **Review cadence:** With each major milestone and phase completion

## Related

- → `INDEX.md` — Central team plans index
- → `.mono-repo/stories/starting-the-project.md` — Founder story
- → `.mono-repo/goals/achievement-board.md` — Achievement board
