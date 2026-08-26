---
title: Features
description: Feature inventory across all Structa Cloud projects — LMS, Portfolio, Syntara, POS, CTC Research.
navigation:
  title: Features
  icon: i-lucide-star
object:
  type: "reference"
  id: "features.index"
attributes:
  source_path: "features/README.md"
  canonical_route: "/docs/en/features"
  source_of_truth: "repository-markdown"
  audience: "engineers, operators, and coding agents"
  status: "maintained"
  owner: "workspace"
tags:
  - structa-cloud
  - features
  - inventory
  - lms
  - pos
  - syntara
  - precis
links:
  - label: "Documentation home"
    to: "/"
    icon: "i-lucide-house"
  - label: "Feature Roadmap"
    to: "/features/feature-roadmap"
    icon: "i-lucide-map"
  - label: "Template Fields"
    to: "/features/template-fields"
    icon: "i-lucide-layout"
---

# 🎯 Features — Feature Inventory

> Feature inventory across all Structa Cloud projects. Use this as a reference for what exists and where to find it.

---

## Feature Matrix

| Feature | LMS | Portfolio | Syntara | POS | CTC Research |
|---------|:---:|:---------:|:----------:|:---:|:------------:|
| **Auth (django-allauth)** | ✅ | ✅ | ✅ | ❌ | ✅ |
| **Social Auth** | ✅ | ✅ | ✅ | — | ✅ |
| **MFA / 2FA** | ✅ | ✅ | ❌ | — | ❌ |
| **Wagtail CMS** | ✅ | ✅ | ✅ | — | ✅ |
| **Blog** | ✅ | ❌ | ❌ | — | ✅ |
| **Courses / LMS** | ✅ | ❌ | ❌ | — | ❌ |
| **Certifications** | ✅ | ❌ | ❌ | — | ❌ |
| **Contact Forms** | ✅ | ✅ | ✅ | — | ✅ |
| **Newsletter** | ✅ | ✅ | ❌ | — | ❌ |
| **AI Chat** | ❌ | ❌ | ✅ | — | ❌ |
| **Streaming AI** | ❌ | ❌ | ✅ | — | ❌ |
| **MCP Integration** | ❌ | ❌ | 🟡 | — | ❌ |
| **POS / Sales** | ❌ | ❌ | ❌ | ✅ | ❌ |
| **Inventory** | ❌ | ❌ | ❌ | ✅ | ❌ |
| **Multi-warehouse** | ❌ | ❌ | ❌ | ✅ | ❌ |
| **Barcode Scanning** | ❌ | ❌ | ❌ | ✅ | ❌ |
| **Receipt Printing** | ❌ | ❌ | ❌ | ✅ | ❌ |
| **i18n / RTL** | ✅ | ✅ | ❌ | ✅ | ❌ |
| **PWA** | ✅ | ✅ | ❌ | ✅ | ❌ |
| **Docker Deploy** | ✅ | ✅ | ✅ | — | ✅ |

> ✅ = Live | 🟡 = Planned | ❌ = Not applicable

---

## Per-Project Feature Docs

| Project | Feature Details |
|---------|----------------|
| LMS | [Use Cases](../projects/lms/use-cases.md) — courses, certs, e-learning |
| Portfolio | [Use Cases](../projects/portfolio/use-cases.md) — resume builder, portfolios |
| Syntara | [Use Cases](../syntara/use-cases.md) — AI chat, custom prompts |
| POS | [Editions](../projects/pos/editions.md) — Minimal vs Solo vs Full |

---

## Feature Requests & Roadmap

### Planned (Phase 2+)

| Feature | Project | Priority |
|---------|---------|----------|
| Stripe billing | Syntara | 🔴 High |
| API token management | Syntara | 🔴 High |
| System templates (1-click deploy) | Syntara | 🟡 Medium |
| App marketplace | Syntara | 🟢 Low |
| WebAuthn / Passkeys | All Django | 🟡 Medium |
| Multi-region deploy | Infrastructure | 🟢 Low |

---

## Shared Feature Specifications

| Feature | Path |
|---------|------|
| Dynamic Template Field System | [`template-fields/`](template-fields/README.md) |
| DataToken Sync-Tagging | [`data-token-sync-tagging.md`](data-token-sync-tagging.md) |

## Related

| Topic | Path |
|-------|------|
| Project index | [`../projects/`](../projects/) |
| Syntara platform plan | [`../syntara/platform-plan.md`](../syntara/platform-plan.md) |
| Best practices | [`../guides/07-best-practices.md`](../guides/07-best-practices.md) |
| Repo overview | [`../repo-overview.md`](../repo-overview.md) |
