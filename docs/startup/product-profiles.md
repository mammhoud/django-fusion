---
title: Product Profiles — Portfolio Catalog 🔒
description: Consolidated product profiles for the Structa Cloud portfolio — Loop-CRM, Precis Platform (CMS, Builder, LMS, Research), and django-fusion — with live (🟢) vs vision (🔴) status per product.
navigation:
  title: Product profiles 🔒
  icon: i-lucide-boxes
object:
  type: "private-profile"
  id: "docs.startup.product-profiles"
attributes:
  source_path: "startup/product-profiles.md"
  canonical_route: "/docs/en/startup/product-profiles"
  source_of_truth: "repository-markdown"
  owner: "workspace"
  status: "maintained"
  access: "private"
tags:
  - structa-cloud
  - startup
  - product-profiles
  - loop-crm
  - precis
  - cms
  - builder
  - lms
  - research
  - django-fusion
  - private
links:
  - label: "Startup home 🔒"
    to: "/startup"
    icon: "i-lucide-rocket"
  - label: "Company profile 🔒"
    to: "/startup/company-profile"
    icon: "i-lucide-building-2"
  - label: "Pricing & offers 🔒"
    to: "/startup/pricing"
    icon: "i-lucide-tags"
---

# 📦 Product Profiles — Portfolio Catalog 🔒

> **Internal only.** The *what* of every Structa Cloud product — modules,
> features, integrations — for sales, marketing, and the executive deck.
> Status legend: 🟢 live in the monorepo · 🟡 partial/beta · 🔴 vision (not
> shipped code). Strategy per product lives in `startup/<product>.md`; this
> document only profiles products and links there.

<!-- AI-generated: review needed -->

## 1. 🤝 Loop-CRM — Business Operating System 🟢

> **Path:** `projects/loop-crm/` · **Strategy:** [`loop-crm.md`](loop-crm.md) · **Product docs:** [`docs/loop-crm/`](../loop-crm/README.md)

Loop CRM is a modern operating system for organizations. Unlike traditional CRM
systems, Loop CRM unifies sales, marketing, support, projects, finance, human
resources, analytics, and AI automation in a single platform.

**Vision:** one platform to manage the entire customer lifecycle and business
operations. **Target customers:** small businesses, mid-sized companies,
enterprises, agencies, educational and healthcare organizations.

### Modules

| Module | Key features |
|--------|--------------|
| Sales | Leads, contacts, accounts, opportunities, pipelines, quotations, contracts, activities |
| Marketing | Campaigns, social publishing, email marketing, marketing automation, analytics |
| Customer Success | Renewals, customer health, lifecycle tracking |
| Support | Ticketing, knowledge base, live chat, SLA tracking |
| Projects | Tasks, kanban, timesheets, milestones |
| HR | Employees, attendance, payroll, recruitment |
| Finance | Invoices, expenses, payments, reports |
| AI | Sales agent, marketing agent, support agent, knowledge agent |

### Key features (20)

Lead management · contact management · company management · opportunity
tracking · sales pipelines · activity tracking · quotation builder · contract
management · follow-up automation · customer timeline · customer segmentation ·
campaign management · email automation · ticketing system · live chat ·
knowledge base · project management · invoice management · analytics dashboard ·
AI recommendations

### Integrations

WhatsApp · Telegram · Email · Stripe · Paymob · Zoom · Google Workspace ·
Microsoft 365

## 2. 🎓 Precis Platform — Unified Digital Experience Platform

> **Path:** `projects/structa.cloud/` (live LMS + landing) · **Strategy:** [`precis.md`](precis.md) · **Product docs:** [`docs/precis/README.md`](../precis/README.md) · **CMS/Builder profile:** [`docs/precis/cms-builder.md`](../precis/cms-builder.md)

Precis is a unified platform that enables organizations to build websites,
manage content, create learning portals, run research centers, generate
applications, launch SaaS products, manage knowledge, and operate digital
businesses — all from a single ecosystem. **Vision:** one platform, multiple
solutions, unlimited possibilities.

### Platform architecture (vision)

```text
Precis Platform
├── Core Platform
│   ├── Content Management (CMS, blogs, documentation, knowledge base)
│   ├── Experience Builder (website, landing, portal, app builder)
│   ├── Learning Suite (Precis LMS)
│   ├── Research Suite (Precis Research)
│   ├── AI Layer
│   ├── Automation Layer
│   └── Analytics Layer
```

### Shared services

Authentication (SSO, workspace management, teams) · security (RBAC,
permissions, audit logs) · platform services (notifications, billing,
subscriptions, integrations) · developer APIs (REST, GraphQL, webhooks).

**Multi-tenant architecture:** companies, universities, research centers, and
government entities each get custom branding, custom domains, separate data,
and independent billing. **Developer ecosystem:** REST/GraphQL/webhook APIs,
Python/JavaScript SDKs, extensions.

> **Reality check:** today the platform is the **LMS + landing shell** merged in
> `precis-main`. CMS/Builder/Research are vision modules profiled below.

## 3. 🎨 Precis CMS — Enterprise Content Management 🟡 under development

> **Profile:** [`docs/precis/cms-builder.md`](../precis/cms-builder.md) — the
> assets-based CMS/Builder direction, the Wagtail content core already live in
> `precis-main`, and client work under the Solo/Business editions.

Enables organizations to create, manage, publish, and distribute content
across websites, applications, portals, and knowledge platforms.

- **Content:** pages, articles, blogs, documentation, knowledge base; visual
  editor, structured content, versioning, drafts
- **Publishing:** scheduling, review workflows, approvals
- **Enterprise:** multi-site, multi-language, multi-tenant
- **APIs:** REST, GraphQL
- **AI:** AI writer, SEO suggestions, content summaries
- **Use cases:** corporate websites, documentation portals, knowledge centers,
  government portals, news websites

> The closest live code is the Wagtail content system in `precis-main` and
> `precis-ctc` — the standalone CMS product does not exist yet.

## 4. 🛠️ Precis Builder — Website & Application Generation Platform 🔴 vision

Allows organizations to visually create websites, portals, dashboards, and
applications using reusable components and AI-assisted generation.

- **Modules:** website builder (company/product/marketing sites), landing
  builder (campaign, lead-gen, event pages), portal builder (customer,
  employee, research portals), app builder (internal tools, dashboards, CRM
  interfaces)
- **Features:** drag & drop builder, theme system, reusable components, design
  tokens, AI generation, dynamic forms, SEO optimization

> Vision only — no builder product exists in the monorepo.

## 5. 📚 Precis LMS — Learning Experience Platform 🟢

> **Path:** `projects/structa.cloud/` (courses, enrollment, progress, profile, assistant) · **Strategy:** [`precis.md`](precis.md) · **Docs:** [`docs/precis/courses.md`](../precis/courses.md)

A learning management solution for educational institutions, academies,
enterprises, and training providers.

- **Learning:** courses, modules, lessons, learning paths
- **Assessments:** quizzes, exams, assignments, question banks
- **Community:** groups, discussions, events
- **Certification:** certificates, achievements, digital badges
- **Analytics:** progress tracking, performance metrics, completion rates
- **AI:** AI tutor, learning assistant, personalized recommendations
- **Target markets:** universities, schools, academies, enterprises, training centers

> Live scope today: courses/enrollment/progress/profile + the Assistant surface
> (`assistant.astro`) in `precis-main`. Assessments/community/badges are
> partially shipped; verify per feature before claiming in marketing.

## 6. 🔬 Precis Research — Academic Research & Publishing Platform 🟢 seed / 🔴 platform

> Seeded by the CTC Research sample · **Path:** `projects/precis/precis-ctc/` · **Sample record:** [`precis-ctc.md`](precis-ctc.md) · **Docs:** [`docs/precis-ctc/`](../precis-ctc/README.md)

Supports the complete research lifecycle from idea generation to publication:
Idea → Literature Review → Research Design → Data Collection → Analysis →
Writing → Submission → Publication.

- **Research workspace:** projects, teams, tasks
- **Literature review:** references, libraries, source management
- **Scientific writing:** manuscript builder, templates, citations
- **Publication center:** journal finder, submission tracking, publication monitoring
- **Statistics hub:** analysis, visualization, reports
- **AI research assistant:** summaries, recommendations, literature analysis
- **Learning center:** courses, workshops, certifications

> **Reality check:** the live seed is **CTC Research** (ctc-research.com) — a
> sample medical research site built with agentic coding on the Precis stack
> (`projects/precis/precis-ctc/`), demonstrating the publishing pipeline and
> EN/AR parity. It is a sample/reference, not a product. The broader
> multi-institution research platform is vision.

## 7. 🧩 django-fusion — Rapid Platform Development Framework 🟢

> **Path:** `libs/django-fusion/` · **Package guide:** [`docs/libs/django-fusion.md`](../libs/django-fusion.md) · **Plans:** [`docs/plans/django-fusion/README.md`](../plans/django-fusion/README.md)

The technology foundation powering Structa Cloud products. Provides reusable
building blocks that accelerate development and ensure consistency across all
platforms. **Vision:** build enterprise-grade products faster using a unified
architecture.

### Packages — real layout (`src/django_fusion/`)

| Real module | What it provides |
|-------------|------------------|
| `comp` | `{% comp %}` component system |
| `fragments` | HTMX fragments, tables, forms |
| `routes` / `services` | Viewset/ModelViewset routing, service layer |
| `core` / `contrib` | Core models, utilities, contrib apps |
| `config` | Layered config cascade (`config.project`) |
| `mcp` | MCP (Model Context Protocol) tool server |
| `tasks` | Background task API (Dramatiq-backed) |
| `models` / `assets` / `designer` / `plugins` | Base models, asset pipeline, designer helpers, plugins |

> **Correction note:** external startup decks sometimes list aspirational
> packages — "Fusion Core / Identity / CMS / API / Builder / Workflow /
> Analytics / AI / Notifications / Tenants" as `fusion.*` apps. **That packaging
> does not exist.** The framework is the in-repo `django_fusion` src layout
> above. Use the real module names in any public material.

### Benefits

Faster development · shared architecture · lower maintenance cost · enterprise
security · modular design · product consistency. **Used by:** Loop-CRM, Precis
(LMS + landing), CTC Research, Formint Cloud, Syntara.

## Remarks & Notes

- Status tags must stay honest: 🟢 live, 🟡 beta/partial, 🔴 vision. Vision
  profiles are directional input for the roadmap, not shipping commitments.
- Per-product strategy (MVP canvas, TAM/SAM/SOM, competitors) lives in
  `startup/<product>.md`; module prices live in [`PRICING.md`](PRICING.md) §6;
  revenue projections in [`revenue-model.md`](revenue-model.md).
- The master 25-slide deck quotes these profiles: [`presentation.md`](presentation.md).
- Private by policy — strip 🔒 markers and vision gaps before external use.
