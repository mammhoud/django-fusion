---
title: Yahia — Front-end + UX Design
description: Design drafts first, then interfaces — layouts, states, and flows that match the design system.
navigation:
  title: Yahia — Front-end + UX
  icon: i-lucide-pen-tool
object:
  type: "plan"
  id: "agenda.roles.yahia"
attributes:
  source_path: "agenda/roles/yahia-frontend.md"
  canonical_route: "/docs/en/agenda/roles/yahia-frontend"
  source_of_truth: "repository-markdown"
  owner: "yahia"
  status: "active"
tags:
  - structa-cloud
  - roles
  - frontend
  - design
links:
  - label: "Role Plans"
    to: "/agenda/roles"
    icon: "i-lucide-users"
  - label: "Dev Team Plans"
    to: "/agenda/dev-team-plans"
    icon: "i-lucide-code"
---

# Yahia — Front-end + UX Design

> **Goal:** Draft the design before writing the interface, so the first build is
> already the right screen.
> **Validated by:** Moustafa (intent), Mahmoud (direction) · **Review:** weekly

## Tasks

| # | Task | Done when | Validated by |
|---|---|---|---|
| 1 | Design draft for the next slice | Wireframe → screen, agreed before implementation | Moustafa |
| 2 | Front-end delivery | Layout, states, empty/error/loading, responsive | Moustafa |
| 3 | UX review of the flow | Fewer steps; the next action is obvious | Moustafa |
| 4 | Accessibility pass | Contrast, focus, labels, reading order checked | Mahmoud |
| 5 | Design-system drift check | New screens use existing tokens and blocks | Mahmoud |
| 6 | Dashboard and report surfaces | Shared with Asmaa; numbers read correctly on screen | Asmaa |

## Works with

| Person | On |
|---|---|
| Moustafa — PM + Marketing | Acceptance criteria, copy, page intent |
| Mahmoud — General Manager | Interface direction, release readiness |
| Asmaa — Data | Dashboard and report surfaces |
| Dariia — Contributor | Content and image fit inside layouts |

## Blocked?

A draft needs the page intent one level up: what the person must be able to do
here. If that is missing, ask Moustafa rather than guessing.

## Related

- → [`./README.md`](./README.md) — Role plans index
- → [`../dev-team-plans.md`](../dev-team-plans.md) — Front-end workstreams
- → [`../.mono-repo/styles/_index.md`](../.mono-repo/styles/_index.md) — Design system
