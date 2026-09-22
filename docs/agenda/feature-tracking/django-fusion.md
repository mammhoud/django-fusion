---
title: django-fusion — Feature Tracking
description: Feature lifecycle for the django-fusion component framework — components, routing, fragments, and tooling
navigation:
  title: django-fusion
  icon: i-lucide-blocks
object:
  type: "guide"
  id: "agenda.feature-tracking.django-fusion"
attributes:
  source_path: "agenda/feature-tracking/django-fusion.md"
  canonical_route: "/docs/en/agenda/feature-tracking/django-fusion"
  source_of_truth: "repository-markdown"
  owner: "django-fusion"
  status: "active"
tags:
  - structa-cloud
  - feature-tracking
  - django-fusion
links:
  - label: "Feature Tracking hub"
    to: "/agenda/feature-tracking"
    icon: "i-lucide-target"
  - label: "Agenda home"
    to: "/agenda/main"
    icon: "i-lucide-clipboard-list"
---

# 🎯 django-fusion (Component Framework) — Feature Tracking

> **Scope:** Feature lifecycle for the shared django-fusion component framework used across the products.
> **Last updated:** 2026-09-12
> **Hub:** [`feature-tracking.md`](../feature-tracking.md) — lifecycle, status definitions, and the per-product index.

---

## ✅ Shipped

**DataToken Sync Tagging**

| Field | Value |
|-------|-------|
| **Status** | ✅ Shipped |
| **Priority** | P1 |
| **Product** | django-fusion |
| **Owner** | — |
| **Target** | Done |
| **Depends on** | — |

**Why it matters:** GenericForeignKey-based sync row tagging with parent/child tree, progress tracking, and auto-untag, UUID PK support — enables reliable sync operations across POS editions.

**Scope:** Sync tag model, parent/child relationships, progress tracking, auto-untag behavior.

**Acceptance criteria:**
- [ ] Sync rows can be tagged
- [ ] Parent/child tree maintained
- [ ] Progress tracked
- [ ] Auto-untag on completion
- [ ] UUID PK supported

**Notes:** Shipped in django-fusion library. 🔧

---

## P1 — Next Up (Q4 2026)

**MCP Integration**

| Field | Value |
|-------|-------|
| **Status** | 🟡 In Progress |
| **Priority** | P1 |
| **Product** | django-fusion |
| **Owner** | TBD |
| **Target** | Q4 2026 |
| **Depends on** | — |

**Why it matters:** Model Context Protocol for AI-assisted development — makes django-fusion components discoverable by AI tools.

**Scope:** MCP server integration, component schema exposure, tool definitions.

**Out of scope:** AI-powered component generation, natural language component queries.

**Acceptance criteria:**
- [ ] MCP server connects to django-fusion
- [ ] Component schemas exposed
- [ ] Tool definitions for component operations

**Notes:** AI integration feature.

---

**Component Storybook**

| Field | Value |
|-------|-------|
| **Status** | ⚪ Proposed |
| **Priority** | P1 |
| **Product** | django-fusion |
| **Owner** | TBD |
| **Target** | Q4 2026 |
| **Depends on** | — |

**Why it matters:** Isolated component preview + documentation — improves component development and discoverability.

**Scope:** Storybook configuration, component stories, documentation extraction.

**Out of scope:** Interactive component playground, visual regression testing.

**Acceptance criteria:**
- [ ] Storybook configured for django-fusion
- [ ] Component stories written
- [ ] Documentation extracted from components

**Notes:** Developer experience feature.

---

**Hot Reload**

| Field | Value |
|-------|-------|
| **Status** | ⚪ Proposed |
| **Priority** | P1 |
| **Product** | django-fusion |
| **Owner** | TBD |
| **Target** | Q4 2026 |
| **Depends on** | — |

**Why it matters:** Template hot reload in development — faster iteration.

**Scope:** File watching, template reload, component reload, dev server integration.

**Out of scope:** Production hot reload, stateful component preservation.

**Acceptance criteria:**
- [ ] Template changes reload automatically
- [ ] Component changes reload automatically
- [ ] Dev server integration

**Notes:** Developer experience feature.

---

## P2 — Planned (Q1 2027)

**TypeScript Components**

| Field | Value |
|-------|-------|
| **Status** | ⚪ Proposed |
| **Priority** | P2 |
| **Product** | django-fusion |
| **Owner** | TBD |
| **Target** | Q1 2027 |
| **Depends on** | MCP Integration |

**Why it matters:** First-class TypeScript component support — better frontend integration.

**Scope:** TypeScript component definitions, type generation, frontend integration.

**Out of scope:** Full TypeScript rewrite of django-fusion.

**Acceptance criteria:**
- [ ] TypeScript types for components
- [ ] Type generation from component metadata
- [ ] Frontend TypeScript integration

**Notes:** Depends on MCP Integration for metadata exposure.

---

**Visual Builder**

| Field | Value |
|-------|-------|
| **Status** | ⚪ Proposed |
| **Priority** | P2 |
| **Product** | django-fusion |
| **Owner** | TBD |
| **Target** | Q1 2027 |
| **Depends on** | Component Storybook |

**Why it matters:** Drag-and-drop page builder using components — empowers non-developers to build pages.

**Scope:** Visual builder UI, component palette, page model, published page rendering.

**Out of scope:** Custom component creation in builder, responsive design controls.

**Acceptance criteria:**
- [ ] Component palette displayed
- [ ] Drag-and-drop page construction
- [ ] Pages saved and rendered

**Notes:** Depends on Component Storybook for component metadata.

---

**Component Analytics**

| Field | Value |
|-------|-------|
| **Status** | ⚪ Proposed |
| **Priority** | P2 |
| **Product** | django-fusion |
| **Owner** | TBD |
| **Target** | Q1 2027 |
| **Depends on** | — |

**Why it matters:** Usage tracking per component — understand which components are actually used.

**Scope:** Usage event tracking, component usage dashboard, adoption metrics.

**Out of scope:** Performance analytics, user behavior analytics.

**Acceptance criteria:**
- [ ] Component usage events tracked
- [ ] Usage dashboard
- [ ] Adoption metrics

**Notes:** Observability feature.

---

## Remarks & Notes

- Status values are lowercase in the template but emoji-prefixed in tables for readability
- Priority alignment with [`feature-roadmap.md`](../../features/feature-roadmap.md) is mandatory — drift causes confusion
- Read [`../feature-tracking.md`](../feature-tracking.md) for the lifecycle, definitions, and the per-product index

<!-- AI-generated: review needed -->
