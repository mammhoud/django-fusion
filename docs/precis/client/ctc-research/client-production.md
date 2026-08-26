---
title: CTC Research — Client Production Website
description: Case study of ctc-research.com as a production client website — client context, scope, stack, deployment, and evidence — the anchor reference deployment for the publishing service line.
navigation:
  title: Client production 🔒
  icon: i-lucide-globe
object:
  type: "case-study"
  id: "docs.precis-ctc.client-production"
attributes:
  source_path: "precis-ctc/client-production.md"
  canonical_route: "/docs/en/precis-ctc/client-production"
  source_of_truth: "repository-markdown"
  owner: "precis-ctc"
  status: "maintained"
  access: "private"
tags:
  - structa-cloud
  - precis-ctc
  - ctc-research
  - case-study
  - client
  - production
  - publishing
links:
  - label: "CTC docs home"
    to: "/precis-ctc"
    icon: "i-lucide-heart-pulse"
  - label: "CTC strategy 🔒"
    to: "/startup/precis-ctc"
    icon: "i-lucide-rocket"
  - label: "Publishing guide"
    to: "/precis-ctc/publishing-and-production"
    icon: "i-lucide-pen-line"
---

# 🏥 CTC Research — Client Production Website

> **Public site:** [`ctc-research.com`](https://ctc-research.com) ·
> **Canonical path:** `projects/precis/precis-ctc/` · **Runtime identity:**
> `precis-ctc` · **Owner:** CTC (medical research center)

<!-- AI-generated: review needed -->

## 1. Client context

CTC is a medical research and learning center. Its web presence is the
**anchor reference deployment** for the Structa Cloud publishing service line:
an institutional site that must present research, education, and publications
in **English and Arabic** with a managed publishing workflow — no one-off
agency build.

## 2. Scope delivered

| Area | What was delivered |
|------|--------------------|
| Institutional site | Home, about (mission/skills/FAQ), team, research, education, courses, documents, events, features, pricing, products, projects, services, blog, profile |
| Research publishing | Wagtail-managed page tree with localized slugs, SEO metadata on both render roads |
| Learning | Course catalog + detail, enrollment, learner profile (Astro road + Django road) |
| Bilingual | EN/AR with shared language contract (`/i18n/setlang/` persistence, `resolve_language` in django-fusion) |
| Content editing | Wagtail StreamFields — every section editor-managed, no frontend fallback to hard-coded content |
| Auth | allauth accounts, MFA/WebAuthn passkeys, newsletter, privacy/legal |

## 3. Stack & architecture

```text
ctc-research.com
  ├─ Traefik: HTTPS/domain/path routing (ctc-research.com + arch subdomain)
  ├─ Astro frontend: public pages and learning shell
  ├─ Django/Wagtail backend: pages, APIs, fragments, auth, learning
  ├─ Dramatiq worker + scheduler: asynchronous execution boundary
  ├─ PostgreSQL: db_precis_ctc
  ├─ Redis: cache and task broker
  └─ shared-proxy/Nginx: /media/ctc-research/ · /static/bundles/ · /sites/ctc-research/static/
```

- **Dual rendering:** server-rendered HTML / HTMX fragments (Django road) and
  data-API JSON for Astro (frontend road) — same content source.
- **Proxy contract:** admin `/admin/` + `/django-admin/` are backend-owned
  (exact `Path()` matchers for the no-slash redirect); `/profile/` and
  `/documents/` are Astro-owned; settings subtree stays Django-owned.

## 4. Deployment & operations

- One Compose/Traefik stack (`make redeploy`), environment contract in
  [`ENVIRONMENT.md`](../../projects/precis/docs/precis-ctc/ENVIRONMENT.md).
- Health checks: `/health/`, `/apis/pages/`, `/static/`, `/media/`.
- Backups + restore verified per the managed-stack runbook; monitor via the
  Dramatiq worker/scheduler and shared-proxy logs.
- Publishing pipeline: Wagtail content → localized slugs → SEO metadata on both
  roads → Astro route smoke coverage (five core routes must not regress to
  empty sections).

## 5. Evidence & outcomes

- **Live reference deployment** — the only production medical-research site in
  the portfolio; used as the demo for the publishing service line.
- **Test coverage** — 198 backend tests passing; frontend checks pass with
  per-route smoke coverage (see the [publish plan](../plans/repository/ctc-research-publish-2026-08-18.md)).
- **Repeatable product** — not a one-off build: the same publishing pipeline is
  the CTC wedge in the [startup strategy](../startup/precis-ctc.md) and the
  portfolio [comparison](../startup/comparison.md) (vs Silverchair/Atypon/agencies).
- **EN/AR parity** — shared language contract + localized content trees.

## 6. Reuse for future clients

The CTC deployment is the **reference architecture** for new publishing
clients: institutional content model (StreamFields + SEO), EN/AR pipeline,
Astro + Django dual road, and the managed hosting runbook. New client work
should clone this pattern rather than re-architect it.

## Remarks & Notes

- Public medical, legal, image-rights, and translation content requires CTC
  owner review before production publication — see the CTC README safety note.
- This case study is private by policy; client-identifying specifics beyond the
  public site (ctc-research.com) must not appear in public materials without
  owner approval.
- Keep in sync with [`publishing-and-production.md`](publishing-and-production.md)
  and the [content strategy](content-strategy.md).
