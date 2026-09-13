---
title: Loop-CRM — Feature Tracking
description: Feature lifecycle for Loop-CRM — shipped milestones across finance, demo state, research, and the AI hub
navigation:
  title: Loop-CRM
  icon: i-lucide-users
object:
  type: "guide"
  id: "agenda.feature-tracking.loop-crm"
attributes:
  source_path: "agenda/feature-tracking/loop-crm.md"
  canonical_route: "/docs/en/agenda/feature-tracking/loop-crm"
  source_of_truth: "repository-markdown"
  owner: "loop-crm"
  status: "active"
tags:
  - structa-cloud
  - feature-tracking
  - loop-crm
links:
  - label: "Feature Tracking hub"
    to: "/agenda/feature-tracking"
    icon: "i-lucide-target"
  - label: "Agenda home"
    to: "/agenda/main"
    icon: "i-lucide-clipboard-list"
---

# 🎯 Loop-CRM — Feature Tracking

> **Scope:** Feature lifecycle for Loop-CRM (CRM, billing, marketing, attribution).
> **Last updated:** 2026-09-12
> **Hub:** [`feature-tracking.md`](../feature-tracking.md) — lifecycle, status definitions, and the per-product index.

---

## ✅ Shipped — Finished Milestones

**Formint finance integration**

| Field | Value |
|-------|-------|
| **Status** | ✅ Shipped |
| **Priority** | P0 |
| **Product** | Loop-CRM |
| **Owner** | — |
| **Target** | Done (2026-08-14/15) |
| **Depends on** | — |

**Why it matters:** POS revenue from Formints lands in the Loop-CRM finance ledger so RevOps sees POS, deal, and attributed revenue in one workspace.

**Scope:** `apps/pos` ledger (`PosSale`/`PosSaleItem`/`PosPayment`), idempotent `POST /api/v1/ingest/pos/sales` with `X-API-Key`, trend split (POS vs deal), 8 new workflow actions + 4 templates with loop-guarded triggers, webhooks (HMAC + retry + dead-letter), email/Slack connectors, accounting CSV/JSON export, and real publishers for all 12 social catalog platforms.

**Acceptance criteria:**
- [x] POS → Loop-CRM ingestion works (workspace-scoped, idempotent)
- [x] Refunds net correctly in the revenue trend
- [x] Workflow actions + templates shipped with tests (29 workflow-action tests)
- [x] Webhooks/email/Slack/export/social connectors shipped with tests
- [x] Tenant isolation preserved on every new read/write path

**Notes:** Former plan `docs/plans/loop-crm/formint-integration-finance-workflows.md` — deleted after completion; git history is the archive. See [`team-notes.md`](../team-notes.md) § 2026-09-05 and [`task-tracking.md`](../task-tracking.md) § Sprint 2.

---

**Demo state & auth gap fixing**

| Field | Value |
|-------|-------|
| **Status** | ✅ Shipped |
| **Priority** | P0 |
| **Product** | Loop-CRM |
| **Owner** | — |
| **Target** | Done (2026-08-17; server half pending real deploy) |
| **Depends on** | — |

**Why it matters:** The deployed `crm.structa.cloud` preview is demo-ready: auth pages render without the CRM side nav, a deterministic demo user exists, the server boots in demo state, and every side-nav destination resolves.

**Scope:** `DEMO_MODE` setting + context processor, bare auth shell (no sidebar), demo panel with one-click fill, deterministic `seed_demo --superuser`, `LOGIN_REDIRECT_URL=/overview/`, entrypoint auto-seed, Astro pages for all six previously-404 side-nav destinations, nav catalog sync, and the Twenty/Postiz `DESIGN.md` token map.

**Acceptance criteria:**
- [x] `/accounts/login/` renders bare entrance with demo panel (when `DEMO_MODE=1`)
- [x] `seed_demo` is deterministic (idempotent, password restored, superuser flag)
- [x] Server auto-seeds on boot in demo state
- [x] Sign-in redirects to `/overview/`; every side-nav destination returns a page
- [x] Backend 255 tests + frontend 34 pages + node suite 50/50 green
- [ ] Server-half end-to-end verification against the deployed stack (requires a real deploy)

**Notes:** Former plan `docs/plans/loop-crm/demo-state-gap-fixing.md` — deleted after completion; git history is the archive. See [`team-notes.md`](../team-notes.md) § 2026-09-05 and [`task-tracking.md`](../task-tracking.md) § Sprint 2.

---

**Twenty/Postiz DNA research**

| Field | Value |
|-------|-------|
| **Status** | ✅ Shipped |
| **Priority** | P1 |
| **Product** | Loop-CRM |
| **Owner** | — |
| **Target** | Done (2026-08-17) |
| **Depends on** | — |

**Why it matters:** Answers whether any single package merges CRM + social scheduling (none exists — Loop-CRM is the only merged implementation) and pins the Loop-CRM visual language so every future page ships consistent.

**Scope:** `@postiz/node` 1.0.8 + `twenty-sdk` 2.31.0 registry findings, full Twenty vs Postiz vs Loop-CRM feature matrix, design-token map in `projects/loop-crm/frontend/DESIGN.md` (substrate, ink, muted, line, accent emerald, type scale, radius/shadow rules, borrowed-pattern map).

**Acceptance criteria:**
- [x] Package findings verified against the npm registry
- [x] Feature matrix covers Twenty, Postiz, and Loop-CRM net-new value
- [x] `DESIGN.md` token map shipped with no placeholders

**Notes:** Former plan `docs/plans/loop-crm/twenty-postiz-comparison.md` — deleted after completion; git history is the archive. See [`team-notes.md`](../team-notes.md) § 2026-09-05 and [`task-tracking.md`](../task-tracking.md) § Sprint 2.

---

**AI Hub, locale support & channel connector expansion**

| Field | Value |
|-------|-------|
| **Status** | ✅ Shipped |
| **Priority** | P0 |
| **Product** | Loop-CRM |
| **Owner** | — |
| **Target** | Done (2026-09-05; live-provider verification pending real deploy) |
| **Depends on** | — |

**Why it matters:** Moves Loop-CRM past plumbing toward the AI-assisted RevOps loop — a workspace consent-gated AI surface that acts on real CRM context, an en/ar interface, and the connector catalog expansion that makes scheduled publishing real for more platforms.

**Scope:**
- **AI Hub** — a workspace consent-gated AI surface with a provider-neutral operation catalog. Operations take a bounded brief and never change CRM records without review; every result carries a human-review note.
- **Language (en/ar)** — interface language switching with right-to-left handling and shared translation catalogs, so the product reads correctly in both languages.
- **People & shell** — employee directory, onboarding tour, command palette with live search, and a profile card.
- **Connector expansion** — sign-in and publishing for Google, Meta, TikTok, and Reddit; real publish adapters gated on configured credentials, so scheduled publishing works on more platforms.

**Acceptance criteria:**
- [x] AI catalog, consent toggle, and operation run round-trip against real workspace data, scoped to the workspace
- [x] Language read/write and catalog integrity covered
- [x] People directory covered
- [x] Connector and sign-in checks green
- [x] Front-end surfaces show real data — no mocked aggregates
- [ ] Live provider credentials configured and publishing/consent verified on the deployed stack (deploy-gated)

**Notes:** No plan file was created for this slice — work dated 2026-09-05 is the archive. AI consent is explicit before any CRM context leaves the workspace. See [`dev-team-plans.md`](../dev-team-plans.md) § Loop-CRM.

---

## Remarks & Notes

- Every entry here is a finished milestone — completed plans are deleted and recorded here (git history is the archive)
- Status values are lowercase in the template but emoji-prefixed in tables for readability
- Read [`../feature-tracking.md`](../feature-tracking.md) for the lifecycle, definitions, and the per-product index

<!-- AI-generated: review needed -->
