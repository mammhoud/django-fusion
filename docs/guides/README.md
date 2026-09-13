---
title: Guides — Learning Path
description: Numbered step-by-step tutorials for the Structa Cloud monorepo — from first clone to production mastery.
navigation:
  title: Guides
  icon: i-lucide-book-open
object:
  type: "guide"
  id: "guides.index"
attributes:
  source_path: "guides/README.md"
  canonical_route: "/docs/en/guides/"
  source_of_truth: "repository-markdown"
  audience: "engineers, operators, and coding agents"
  status: "maintained"
  owner: "workspace"
tags:
  - structa-cloud
  - onboarding
  - guides
  - learning-path
links:
  - label: "Documentation home"
    to: "/"
    icon: "i-lucide-house"
  - label: "Project awareness"
    to: "/guides/00-project-awareness"
    icon: "i-lucide-compass"
---

# 📚 Guides — Your Learning Path

> Numbered walkthroughs for common tasks across the Structa Cloud monorepo. **Follow the numbered path** for a structured journey, or jump to the guide that matches your current goal.

---

## 🗺️ The Journey — Start Here

| Step | Guide | Goal | Who Should Read |
|------|-------|------|-----------------|
| 🧭 **00** | [Project Awareness](00-project-awareness.md) | Understand the repo: structure, products, commands, how to navigate | Everyone — **read first** |
| ⚡ **01** | [Quickstart](01-quickstart.md) | Clone → `uv sync` → `just install` → `make deploy` → sites live | Newcomers, CI bootstrap, first-time deploy |
| 🔧 **02** | [Setup & Build](02-setup.md) | Per-project setup, build, CI workflows, common first steps | Project developers, operators |
| 🔐 **03** | [Auth](03-auth.md) | Django allauth, HTMX fragments, OAuth, TOTP, WebAuthn | Backend/web devs adding auth |
| 💻 **04** | [Dev](04-dev.md) | Local dev workflow, hot reload, debugging, sidecar patterns | Daily developers |
| 🚀 **05** | [Deploy](05-deploy.md) | Docker, Traefik, Let's Encrypt, health checks, DB backups | Operators, release engineers |
| 🎨 **06** | [Customize](06-customize.md) | Safe changes (🟢), hooks (🟡), templates (🔵), config (⚪), core (🔴) | Customizers, integrators |
| 📦 **07** | [Clone Site](07-clone-site.md) | Duplicate a product as a new tenant with its own domain/data | Platform engineers, SaaS builders |
| ✅ **08** | [Best Practices](08-best-practices.md) | Patterns to adopt, anti-patterns to avoid, code review checklist | All engineers |
| 📝 **09** | [Docus Implementation](09-docus.md) | Docus/Nuxt config, i18n, content pipeline, validation | Docs maintainers |
| 💊 **10** | [Fusion Assets Health](10-fusion-assets-health.md) | Static asset pipeline, CSS/JS health checks, bundle analysis | Frontend engineers |
| 🛠 **11** | [Tools Dashboard & Auth](11-tools-dashboard-auth.md) | Internal tools portal: dashboard listing, sign-in modal, unlock gate, sessions | Operators, workspace tooling |

---

## 🎯 Who Should Read What

| Persona | Start With | Then |
|---------|------------|------|
| **New engineer** | 00 → 01 → 02 | 03, 04, 05 |
| **Coding agent (AI)** | 00 → 02 (project table) | Relevant product guide |
| **Operator / DevOps** | 00 → 01 → 05 | 10 (asset health), 11 (tools portal) |
| **Frontend dev** | 00 → 02 → 04 | 06, 10 |
| **Backend dev** | 00 → 02 → 03 | 04, 08 |
| **Docs maintainer** | 00 → 09 | 08 |

---

## 📖 After the Guides

- 🏗️ [Project Structure](/docs/en/project-structure) — canonical filesystem map
- 🏛️ [Architecture](/docs/en/architecture) — high-level monorepo architecture
- 🛠️ [Commands](/docs/en/COMMANDS) — complete command catalog
- 📦 [Backend Environments](/docs/en/dev/back-env) — env vars for all projects
- 🧪 [Testing Overview](/docs/en/tests) — run tests across all projects
- 🗄️ [Database Guide](/docs/en/dev/databases) — schema, migrations, connections
- 📋 [Plans](/docs/en/plans) — implementation plans & ADRs

---

## 🔗 Related Guides (Unnumbered)

- [Config Cascade](config-cascade.md) — layered config system deep-dive
- [Fixture Loading](fixture-loading.md) — dev/test data loading patterns
- [Auth / WebAuthn Passkeys](auth/webauthn-passkeys.md) — FIDO2/WebAuthn setup

---

→ [Back to Documentation Home](/docs/en/)

<!-- AI-generated: review needed -->