---
title: Recommendations
description: The shortest path from the current repository state to the next safe, valuable work — priorities and sequencing.
navigation:
  title: Recommendations
  icon: i-lucide-star
object:
  type: "reference"
  id: "recommendations.index"
attributes:
  source_path: "recommendations.md"
  canonical_route: "/docs/en/recommendations"
  source_of_truth: "repository-markdown"
  audience: "engineers, operators, and coding agents"
  status: "maintained"
  owner: "workspace"
tags:
  - structa-cloud
  - recommendations
  - priorities
  - sequencing
  - planning
links:
  - label: "Documentation home"
    to: "/"
    icon: "i-lucide-house"
  - label: "Project Awareness"
    to: "/guides/00-project-awareness"
    icon: "i-lucide-compass"
  - label: "Plans"
    to: "/plans"
    icon: "i-lucide-file-text"
---

# ⭐ Recommendations First

> **Purpose:** the shortest path from the current repository state to the next safe, valuable work.
>
> **Updated:** 2026-08-10

This page is the decision layer for Structa Cloud documentation. Read it before opening detailed plans.

## Recommended order

### 1. Keep `docs/plans/` as the only active plan registry

All engineering plans now belong under [`docs/plans/`](plans/README.md), organized by scope:

- `plans/repository/` — cross-repository architecture, cleanup, and delivery work;
- `plans/editions/` — Formint edition execution chain;
- `plans/precis-landing.md` — Landing site architecture and content work;
- `plans/django-fusion/` — shared framework work (tasks, MCP, sync, POS enhancements).

Do not create new plans under `docs/dev/plans/`, `projects/*/docs/`, or `docs/plans/migrated/`.

### 2. Finish the current product vertical slices before starting broad cleanup

1. **Formint edition chain** — continue from the canonical [editions index](plans/editions/README.md).
2. **Formint Cloud (`cloud` edition)** — continue Channels/WebSocket sync + Bolt dashboard work.
3. **Precis Landing** (`projects/precis/precis-landing/`) — keep the content rendering contract covered by focused tests before adding new blocks.
4. **Precis LMS** (`projects/precis/precis-main/`) — close remaining frontend and deployment tasks with owned verification commands.

### 3. Treat migration and legacy material as evidence, not scope

Completed phase reports are deleted once superseded and must not be presented as active work. See [`document-lifecycle.md`](plans/document-lifecycle.md) for policy.

### 4. Keep product knowledge separate from engineering execution

- Engineering plans: [`docs/plans/`](plans/README.md)
- Product scope & editions: [`docs/plans/editions/README.md`](plans/editions/README.md)
- Current architecture: [`docs/ARCHITECTURE.md`](ARCHITECTURE.md) + [`docs/project-structure.md`](project-structure.md)

## Current next actions

| Priority | Action | Source of truth | Verification |
|:--:|---|---|---|
| P0 | Formint edition extension chain — next executable task | [`plans/editions/README.md`](plans/editions/README.md) | Edition-specific tests |
| P0 | Precis Landing content work — preserve rendering contract | [`plans/precis-landing.md`](plans/precis-landing.md) | Backend tests + `npm run check` |
| P1 | Precis LMS — close frontend/deployment gates | `projects/precis/precis-main/backend/` | Site checks, tests, builds |
| P1 | Repository cleanup — don't delete compatibility sources prematurely | [`plans/repository/migration-cleanup-master.md`](plans/repository/migration-cleanup-master.md) | Reference scan |
| P2 | django-fusion tasks & MCP — unified bg task API, Celery removal, MCP tooling | [`plans/django-fusion/django-fusion-tasks-mcp-plan.md`](plans/django-fusion/django-fusion-tasks-mcp-plan.md) | `uv run pytest libs/django-fusion/` |
| P2 | Docs maintenance — link validation, stale ref removal | [`plans/document-lifecycle.md`](plans/document-lifecycle.md) | Link checker |

## Rules for adding a plan

1. Start with: status, owner, date, scope, dependencies, verification commands.
2. Put in `docs/plans/<scope>/`.
3. Add to [`docs/plans/README.md`](plans/README.md).
4. Link to source code — don't duplicate.
5. Mark superseded plans; delete them and record the removal in the deletion manifest.

## Recent name migrations

| Old → New | When |
|---|---|
| `formintA` → `community`, `formint` → `pro`, `formint-cloud` → `cloud`, `formintC` → `client`, `formint-standard` → `standard` | 2026-08-16 |
| `formintB` / `pos-cloud` → `formint-cloud` (now `cloud`) | 2026-08-09 |
| `precis-landing` → `projects/precis/precis-landing/`, `precis-ctc` → `projects/precis/precis-ctc/` | 2026-08-16 |
| `precis-lms` → Precis LMS (`projects/precis/precis-main/`) | Active |
| `cypercloud` → Syntara (`projects/syntara/`) | Active |
| `core/` → `projects/` | 2026 |

## Related

- [`docs/README.md`](README.md) — documentation hub
- [`docs/plans/README.md`](plans/README.md) — canonical plan registry
- [`docs/overview.md`](overview.md) — repo overview + name migration reference
- [`docs/project-structure.md`](project-structure.md) — full project tree
