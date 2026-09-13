# Startup Docs Enhancement — Progressive Plan

> **Status:** Active (analysis complete; P1–P3 landed with this plan)
> **Scope:** Cross-project documentation (docs/startup + docs/plans registry)
> **Date:** 2026-08-20
> **Branch:** `generic`
> **Input:** 14-document startup pack (company profile, product profiles, plans & editions, Django Fusion package guide, headless/MCP, presentation, market analysis, revenue model)

## Goal

Fold the supplied 14-document startup pack into the existing `docs/startup/`
section without creating duplicate sources of truth. Every piece of the pack is
either **added** (new doc / new section), **merged** into an existing doc, or
**declined** with a reason. One plan doc records the analysis, remarks what was
added vs not added, and links each progressive phase to the docs it touches.

The startup section already has a strict convention (see
[`docs/startup/README.md`](../../startup/README.md)): strategy per product in
`startup/<product>.md`, TAM/SAM/SOM + competitive landscape in
`STRATEGY.md`/`comparison.md`, packaging in `PRICING.md`, sales in `SALES.md`,
launch in `PLAN.md`. The pack was analyzed against that structure rather than
dumped in as 14 standalone files.

## Gap analysis — pack document vs monorepo

| # | Pack doc | Monorepo status | Where it lives / lands | Action |
|---|----------|-----------------|------------------------|--------|
| 1 | Company profile | 🔴 **Not present** | No company-profile doc exists anywhere in `docs/` | ➕ Add [`docs/startup/company-profile.md`](../../startup/company-profile.md) |
| 2 | Loop-CRM product profile | 🟡 Partial | Strategy: [`startup/loop-crm.md`](../../startup/loop-crm.md) · product docs: [`docs/loop-crm/README.md`](../../loop-crm/README.md) | 🔀 Merge module/feature/integration tables into [`startup/product-profiles.md`](../../startup/product-profiles.md) |
| 3 | Plans & editions (pricing) | 🟡 Partial | Portfolio packages in [`startup/PRICING.md`](../../startup/PRICING.md) · Formint chain in [`plans/editions/README.md`](../editions/README.md) | 🔀 Merge module price book into `PRICING.md` §6 |
| 4 | Precis Platform profile | 🟡 Partial | [`docs/precis/README.md`](../../precis/README.md) + [`startup/precis.md`](../../startup/precis.md) cover LMS+landing, not the DXP-platform vision | 🔀 Merge platform vision into `product-profiles.md` (marked 🔴 vision) |
| 5 | Precis CMS profile | 🔴 **Not present** | No standalone CMS product (marketing/catalog shell lives inside precis-main) | 🔀 Merge into `product-profiles.md` (marked 🔴 vision) |
| 6 | Precis Builder profile | 🔴 **Not present** | No builder product exists in the monorepo | 🔀 Merge into `product-profiles.md` (marked 🔴 vision) |
| 7 | Precis LMS profile | 🟡 Partial | [`docs/precis/courses.md`](../../precis/courses.md) + [`startup/precis.md`](../../startup/precis.md) | 🔀 Merge feature catalog into `product-profiles.md` (🟢 live) |
| 8 | Precis Research profile | 🟡 Partial | CTC research-center site docs: [`projects/precis/precis-ctc/`](../../../projects/precis/precis-ctc/README.md) | 🔀 Merge into `product-profiles.md` (CTC 🟢, platform 🔴 vision) |
| 9 | Django Fusion framework | 🟡 Partial | [`docs/libs/django-fusion.md`](../../libs/django-fusion.md) + [`plans/django-fusion/README.md`](../django-fusion/README.md) | 🔀 Merge corrected package reality into `product-profiles.md` |
| 10 | Django Fusion package guide | ⛔ **Not added (rejected as-is)** | Real API differs from the pack (see below) | 🚫 Decline — rewrite required; canonical guides exist |
| 11 | Headless + MCP + generated projects | 🟢 Already covered | [`docs/ai/mcp-integration.md`](../../ai/mcp-integration.md) · [`plans/django-fusion/django-fusion-tasks-mcp-plan.md`](../django-fusion/django-fusion-tasks-mcp-plan.md) · [`precis-landing/backend-api.md`](../../precis/precis-landing/backend-api.md) | ✋ No new file; remark only |
| 12 | Presentation master structure | 🔴 **Not present** | No deck outline exists in `docs/` | ➕ Add [`docs/startup/presentation.md`](../../startup/presentation.md) |
| 13 | Market analysis (TAM/SAM/SOM) | 🟢 Already covered | [`STRATEGY.md`](../../startup/STRATEGY.md) §3 + [`comparison.md`](../../startup/comparison.md) §3 + per-product TAM/SAM/SOM | ✋ No new file; deltas remarked below |
| 14 | Revenue model | 🟡 Partial | Streams + strategy + discounts in [`startup/PRICING.md`](../../startup/PRICING.md); no ARR projections / unit economics | ➕ Add [`docs/startup/revenue-model.md`](../../startup/revenue-model.md) |

## Remarks — what was added vs not added

### ➕ Added to `docs/startup/` (new files)

| File | Pack source | Contents |
|------|-------------|----------|
| [`company-profile.md`](../../startup/company-profile.md) | #1 | Overview, mission, vision, focus areas, product ecosystem, tech stack, competitive advantages — aligned to the real monorepo product set |
| [`product-profiles.md`](../../startup/product-profiles.md) | #2, #4–#9 | Consolidated product profiles: Loop-CRM (🟢), Precis Platform vision (🔴), Precis CMS (🔴), Precis Builder (🔴), Precis LMS (🟢), Precis Research / CTC (🟢 site, 🔴 platform), django-fusion (🟢 framework, corrected) |
| [`revenue-model.md`](../../startup/revenue-model.md) | #14 | Revenue streams, pricing strategy, ARR projections, CAC/LTV/churn/gross-margin unit economics — all 🔴 directional |
| [`presentation.md`](../../startup/presentation.md) | #12 | 25-slide executive deck outline + suggested additional slides |

### 🔀 Added into existing startup docs (no new file)

| Doc | Pack source | What was added |
|-----|-------------|----------------|
| [`PRICING.md`](../../startup/PRICING.md) §6 | #3 | Module price book: Loop-CRM (Lite $0 → Enterprise), Precis CMS, Precis Builder, Precis LMS (per-learner), Precis Research (per-researcher), add-ons, white-label/OEM — all 🔴 directional, to be validated before publishing |

### ✋ Already present — no action (remarked)

- **#11 Headless + MCP + generated projects** — covered by `docs/ai/mcp-integration.md`, the django-fusion MCP plans (`plans/django-fusion/django-fusion-tasks-mcp-plan.md`, `django-fusion-llm-mcp-enhancement-plan.md`), the headless/data-API contract in `docs/precis/precis-landing/backend-api.md`, and the CTC publish plan ([`ctc-research-publish-2026-08-18.md`](ctc-research-publish-2026-08-18.md)).
- **#13 Market analysis** — TAM/SAM/SOM and competitor head-to-head already live in `STRATEGY.md` §3/§5, `comparison.md` §3, and every per-product strategy doc. **Delta to note:** the pack quotes portfolio-level figures (~$200B TAM, ~$15B SAM, $50–100M SOM); the existing docs use per-product tags (e.g., Precis TAM ~$20–25B 🟡, Loop-CRM ~$65–70B 🟡) that are more granular. Do **not** add a second sizing doc — if a portfolio headline number is wanted, add it to `STRATEGY.md` §3 with a 🟡 tag and a source anchor.

### 🚫 Not added (declined, with reason)

| Pack doc | Reason |
|----------|--------|
| #10 Django Fusion package guide | **The pack's guide describes a fictional public API.** It claims `pip install django-fusion`, `fusion.core`/`fusion.identity`/`fusion.tenants` apps, `TenantMixin`/`TenantAwareModel`, `mcp_tool` decorators, and CLI commands that do not exist. The real framework is the in-repo `libs/django-fusion/` (src layout `src/django_fusion/`: `comp`, `fragments`, `routes`, `services`, `tasks`, `mcp`, `config`, `core`, `contrib`, `models`, `assets`, `designer`, `plugins`). Canonical developer docs already exist: [`docs/libs/django-fusion.md`](../../libs/django-fusion.md) and [`docs/plans/django-fusion/README.md`](../django-fusion/README.md). If a public package guide is ever needed, it must be written against the real API — see Phase 5 below. |
| Separate files for #5, #6, #8 | Precis CMS / Builder / Research are **vision products, not shipped code**. Standalone profiles would imply they exist. They are profiled inside `product-profiles.md` explicitly tagged 🔴 vision so the startup section stays honest about what runs today. |
| #13 as a standalone doc | Would duplicate `STRATEGY.md`/`comparison.md`. |

## Progressive phases (linked)

> Each phase links to the docs it creates or touches. Phases are ordered so each
> one builds on the previous; links are the progressive path through the pack.

```mermaid
graph LR
    P0[P0 · Analysis & registry] --> P1[P1 · Company narrative]
    P1 --> P2[P2 · Product profiles + pricing]
    P2 --> P3[P3 · Commercial layer]
    P3 --> P4[P4 · Review & reconciliation]
    P4 -.-> P5[P5 · Public django-fusion guide (if wanted)]
```

### P0 — Analysis & registry ✅ (this plan)
- **Write:** [`plans/repository/startup-docs-enhancement-plan.md`](startup-docs-enhancement-plan.md) (this file).
- **Register:** add the plan to the canonical registry [`plans/README.md`](../README.md).
- **Link from:** [`startup/README.md`](../../startup/README.md) → "Progressive plan".

### P1 — Company narrative ✅
- **Create:** [`docs/startup/company-profile.md`](../../startup/company-profile.md).
- **Index:** add to the strategy-documents table in [`startup/README.md`](../../startup/README.md).
- **Links:** company profile ↔ product profiles ↔ revenue model ↔ master deck (each new doc links to the others).

### P2 — Product profiles + pricing ✅
- **Create:** [`docs/startup/product-profiles.md`](../../startup/product-profiles.md) (pack #2, #4–#9).
- **Update:** [`docs/startup/PRICING.md`](../../startup/PRICING.md) — add §6 module price book (pack #3).
- **Links:** `product-profiles.md` ↔ per-product strategy docs (`startup/precis.md`, `startup/loop-crm.md`, `startup/precis-ctc.md`, `startup/syntara.md`, `startup/formints.md`) and `PRICING.md` §6 ↔ `revenue-model.md`.

### P3 — Commercial layer ✅
- **Create:** [`docs/startup/revenue-model.md`](../../startup/revenue-model.md) (pack #14).
- **Create:** [`docs/startup/presentation.md`](../../startup/presentation.md) (pack #12).
- **Links:** `revenue-model.md` ↔ `PRICING.md` ↔ `PLAN.md` (goals/metrics) · `presentation.md` ↔ every profile + strategy doc it quotes.

### P4 — Review & reconciliation (next)
- [ ] Reconcile the pack's portfolio TAM figures against `STRATEGY.md` §3 — decide whether to add one portfolio headline row (🟡) or keep per-product tags only.
- [ ] Cross-check every product name in the new profiles against [`docs/plans/marketing-claims.md`](../marketing-claims.md); add any new claim there with evidence.
- [ ] Validate module prices with customer interviews before any public pricing page (upgrade 🔴 → 🟡).
- [ ] Add EN/AR parity for the new startup docs if the section is ever published (currently 🔒 private).

### P5 — Public django-fusion package guide (optional, gated)
- **Only if** a public, installable django-fusion distribution is planned: rewrite pack #10 against the **real** API (`django_fusion` src layout), place it next to [`docs/libs/django-fusion.md`](../../libs/django-fusion.md), and mirror it in `libs/django-fusion/docs/`. Do **not** ship the pack's fictional `fusion.*` package guide.

## Progressive linking map

```text
docs/startup/README.md ──► company-profile.md ──► product-profiles.md ──► revenue-model.md ──► presentation.md
        │                        │                    │  │                   │
        ▼                        ▼                    ▼  ▼                   ▼
   PLAN.md · STRATEGY.md · comparison.md        PRICING.md §6 · per-product strategy docs · marketing-claims.md
        │
        ▼
docs/plans/README.md ──► repository/startup-docs-enhancement-plan.md (this plan)
```

## Remarks & Notes

- **One source per fact:** TAM/SAM/SOM stays in `STRATEGY.md` + per-product docs; pricing stays in `PRICING.md`; revenue projections stay in the new `revenue-model.md`. New docs only *link* to these, never restate them.
- The startup section is 🔒 private by policy; all new docs carry `access: "private"` frontmatter and an `<!-- AI-generated: review needed -->` marker like the rest of the section.
- Vision products (Precis CMS / Builder / Research platform) are tagged 🔴 so profiles never imply shipped code. The monorepo's real products are: Precis (precis-main LMS+landing), CTC Research (precis-ctc), Syntara, Formint POS, Loop-CRM, and the django-fusion framework.
- Update this plan's phase checkboxes and the `docs/plans/README.md` highlights table as P4/P5 progress.
