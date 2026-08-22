---
title: Product Audit — Index & Executive Summary
description: Executive summary of the CRM, POS, LMS, and Landing Builder product audit — statuses, headline gaps, top risks, and priority recommendations.
navigation:
  title: Product Audit
  icon: i-lucide-clipboard-check
object:
  type: "reference"
  id: "docs.audit.home"
attributes:
  source_path: "audit/README.md"
  canonical_route: "/docs/en/audit"
  section: "audit"
  owner: "workspace"
  status: "maintained"
  source_of_truth: "repository-markdown"
tags:
  - structa-cloud
  - audit
  - gap-analysis
  - risk-analysis
  - recommendations
  - crm
  - pos
  - lms
  - landing-builder
links:
  - label: "Full audit report"
    to: "/docs/en/audit/product-audit"
    icon: "i-lucide-file-search"
  - label: "Plan registry"
    to: "/docs/en/plans"
    icon: "i-lucide-map"
---

# 📋 Product Audit — Index & Executive Summary

> **Audit date:** 22 August 2026 · **Scope:** CRM, POS, LMS, Landing Builder
> · **Method:** repository truth pass against the plan registry, README
> statuses, and code trees (not a production certification).

## Status at a glance

| Product | Boundary | Status | Headline finding |
|---|---|---|---|
| **CRM** (Loop-CRM) | `projects/loop-crm/` | 🟢 live | Foundation, tenancy, CRUD, finance, billing, landing, and social publishing shipped; AI hub + 6 adapters remain |
| **POS** (Formints) | `projects/formints/` | 🟢 core / 🟡 cloud | Community/Standard/Pro done in code; Cloud staging; pos-client dev; claims + docs need a truth pass |
| **LMS** (Precis) | `projects/precis/precis-main/` | 🟢 live | Courses/enrollment/progress/profile + assistant shipped; E2E suite + production rollout gates remain |
| **Landing Builder** | `projects/precis/precis-main/` · `precis-landing/` · `loop-crm/apps/pages` · `assets/theme` | 🟡 building blocks / 🔴 product | 80% of the stack exists (Wagtail + theme engine + dynamic templates); the drag-and-drop builder product itself does not exist |

## Headline gaps

1. **CRM:** AI hub (Phase 4) not started; 6 of 12 social adapters are honest
   "not wired yet" stubs; GraphQL absent; support/projects/HR module families
   unshipped.
2. **POS:** Cloud needs Postgres schema-per-tenant flip-on + staging deploy;
   pos-client cart/checkout flows unfinished; design-system package adopted
   only partially; public claims use placeholders and under-advertise editions.
3. **LMS:** No full Playwright E2E; production Docker/Traefik gates open; the
   planned Syntara → Precis Assistant merge hasn't started; assessment/community/
   badge features are partial.
4. **Landing Builder:** No drag-and-drop surface, no site scaffolding, no
   tenant isolation — but Wagtail pages, 13 themes, a theme engine, and the
   dynamic template field system are all live building blocks.

## Top 5 risks

| # | Risk | Level |
|---|---|---|
| 1 | Marketing claims run ahead of shipped code (public pricing sells vision tiers) | 🔴 High |
| 2 | Production deployment evidence is thin (Cloud staging, LMS rollout gates, CRM demo-level) | 🔴 High |
| 3 | Five POS editions share three runtime shapes — divergence and maintenance drag | 🟠 Medium |
| 4 | Duplicated surfaces: two API roads, dual task logs, three landing codebases | 🟠 Medium |
| 5 | Development artifacts and example credentials committed in the tree | 🟠 Medium |

## Priority recommendations

1. **P0 — Claims truth pass:** reconcile public surfaces (pricing pages, POS
   landing) with shipped code; replace placeholder imagery; fix the Formint
   audit register.
2. **P0 — LMS production gates:** finish Playwright E2E + Docker/Traefik
   rollout so the flagship site has a deployable path.
3. **P1 — POS Cloud promotion:** Postgres flip-on, `make verify-stack`, staging
   deploy; finish pos-client browser flows.
4. **P1 — Landing Builder MVP:** assemble the shipped blocks (Wagtail +
   `projects/assets/theme` + dynamic templates) into a component-assembly
   builder surface instead of building from scratch.
5. **P2 — Consolidation:** one API road, one task log, one landing codebase;
   wire products onto the shared theme engine.

## Full report

The detailed audit — per-product **completed / planned / missing / technical
debt**, plus **gap analysis, risk register, and phased recommendations** — is
in [**product-audit.md**](product-audit.md).

## Remarks & Notes

- Statuses follow the portfolio legend in
  `docs/startup/product-profiles.md` (🟢 live · 🟡 beta/partial · 🔴 vision).
- This audit is an engineering truth pass. Live DNS, deployment health, and
  production behavior still require operator/staging checks.
- Update this index whenever a plan in `docs/plans/` changes status.
- <!-- AI-generated: review needed -->
