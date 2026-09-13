---
title: CTC Research Center — Feature Tracking
description: Feature lifecycle for the CTC medical research publication site — multi-language catalogs and publish gates
navigation:
  title: CTC Research Center
  icon: i-lucide-flask-conical
object:
  type: "guide"
  id: "agenda.feature-tracking.ctc-research"
attributes:
  source_path: "agenda/feature-tracking/ctc-research.md"
  canonical_route: "/docs/en/agenda/feature-tracking/ctc-research"
  source_of_truth: "repository-markdown"
  owner: "workspace"
  status: "active"
tags:
  - structa-cloud
  - feature-tracking
  - ctc
links:
  - label: "Feature Tracking hub"
    to: "/agenda/feature-tracking"
    icon: "i-lucide-target"
  - label: "Agenda home"
    to: "/agenda/main"
    icon: "i-lucide-clipboard-list"
---

# 🎯 CTC Research Center — Feature Tracking

> **Scope:** Feature lifecycle for the medical research center's public publication site.
> **Last updated:** 2026-09-12
> **Hub:** [`feature-tracking.md`](../feature-tracking.md) — lifecycle, status definitions, and the per-product index.

---

## ✅ Shipped — Live Site

**Multi-language research publication site**

| Field | Value |
|-------|-------|
| **Status** | ✅ Shipped |
| **Priority** | P0 |
| **Product** | CTC Research |
| **Owner** | — |
| **Target** | Done |
| **Depends on** | — |

**Why it matters:** The medical research center's public publications reach readers in their own language — the core promise of the site.

**Scope:** Multi-language publication catalogs (Spanish/Swedish/Portuguese-BR), media delivery, internationalized fixtures.

**Acceptance criteria:**
- [x] Publications available in es/sv/pt-br
- [x] Media (images/documents) served reliably
- [x] Language switching works across the site

## P1 — Next Up

**Publish gates: email parity & redeploy validation**

| Field | Value |
|-------|-------|
| **Status** | 🟡 In Progress |
| **Priority** | P1 |
| **Product** | CTC Research |
| **Owner** | TBD |
| **Target** | Q4 2026 |
| **Depends on** | Deployed stack |

**Why it matters:** Nothing ships to the public site until notification emails match the site's languages and the redeploy path is proven safe.

**Scope:** Email parity end-to-end checks, `make redeploy` validation runbook.

**Out of scope:** New public features.

**Acceptance criteria:**
- [ ] Notification emails verified per language
- [ ] Redeploy validation passes on the deployed stack

**Notes:** From the 2026-09-06 truth table — deploy-gated, not code work. Demo blog templates with placeholder content are tracked for removal in [`task-tracking.md`](../task-tracking.md) backlog.

---

## Remarks & Notes

- Status values are lowercase in the template but emoji-prefixed in tables for readability
- Priority alignment with [`feature-roadmap.md`](../../features/feature-roadmap.md) is mandatory — drift causes confusion
- Read [`../feature-tracking.md`](../feature-tracking.md) for the lifecycle, definitions, and the per-product index

<!-- AI-generated: review needed -->
