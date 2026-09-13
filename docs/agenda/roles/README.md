---
title: Roles — Minimal Working Plans
description: One short working plan per person: tasks, what done looks like, and who validates it.
navigation:
  title: Roles
  icon: i-lucide-users
object:
  type: "index"
  id: "agenda.roles"
attributes:
  source_path: "agenda/roles/README.md"
  canonical_route: "/docs/en/agenda/roles"
  source_of_truth: "repository-markdown"
  owner: "workspace"
  status: "active"
tags:
  - structa-cloud
  - roles
  - team
links:
  - label: "Task Tracking"
    to: "/agenda/task-tracking"
    icon: "i-lucide-list-checks"
  - label: "Completion Checklist"
    to: "/agenda/completion-checklist"
    icon: "i-lucide-check-circle"
---

# Roles — Minimal Working Plans

> **English:** One short plan per person. Each plan holds only that person's
> tasks, what "done" looks like, and who validates it. Team-wide rules live in
> [`../task-tracking.md`](../task-tracking.md) § Task Validation Workflow.
>
> **العربية:** خطة مختصرة لكل فرد. تحتوي كل خطة على مهامه فقط، ومعنى
> "مكتمل"، ومن يتحقق منها. القواعد العامة في
> [`../task-tracking.md`](../task-tracking.md).
>
> **Last updated:** 2026-09-12

## The team

| Person | Role | Plan | Validates |
|---|---|---|---|
| **Mahmoud** | General Manager + Full-stack | [`mahmoud-gm.md`](./mahmoud-gm.md) | Portfolio, revenue, scope |
| **Moustafa** | Product Manager + Marketing | [`moustafa-pm.md`](./moustafa-pm.md) | Roadmap, acceptance, claims |
| **Yahia** | Front-end + UX Design | [`yahia-frontend.md`](./yahia-frontend.md) | Design drafts, screens |
| **Asmaa** | Data Development | [`asmaa-data.md`](./asmaa-data.md) | Metrics, evidence |

`Dariia` contributes content and documentation and has no standing task list.

## The template (5 lines, no more)

Every role plan is: **Goal** → **Tasks table** → **Works with** → **Blocked?**
Nothing else. If a section grows past a screen, it belongs in a plan under
[`../../plans/`](../../plans/README.md), not here.

## Task rows are validated, not reported

Each row names the **validator** — the person who checks the "Done when" column
and marks the task complete. Nobody validates their own task. Cross-role pairs
are fixed:

| Task type | Builder | Validator |
|---|---|---|
| Product / spec / copy | Yahia, Asmaa, Dariia | **Moustafa** |
| Interface / flow | Yahia | **Moustafa** (intent) + **Mahmoud** (direction) |
| Metric / evidence | Asmaa | **Moustafa** (claims) + **Mahmoud** (revenue) |
| Backend / delivery | Mahmoud | **Moustafa** (acceptance) |
| Claims before publishing | Moustafa | **Mahmoud** (final sign-off) |

## Related

- → [`../task-tracking.md`](../task-tracking.md) — Task board + validation workflow
- → [`../completion-checklist.md`](../completion-checklist.md) — Definition of done
- → [`../.mono-repo/plans/team.md`](../.mono-repo/plans/team.md) — Team operating plan
- → [`../.mono-repo/objects/team.md`](../.mono-repo/objects/team.md) — Team object
