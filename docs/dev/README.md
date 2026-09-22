---
title: Development
description: Development references — infrastructure, databases, back-env, customization.
navigation:
  title: Development
  icon: i-lucide-code
object:
  type: "reference"
  id: "dev.index"
attributes:
  source_path: "dev/README.md"
  canonical_route: "/docs/en/dev"
  source_of_truth: "repository-markdown"
  audience: "engineers, operators, and coding agents"
  status: "maintained"
  owner: "workspace"
tags:
  - structa-cloud
  - development
  - infrastructure
  - databases
  - customization
links:
  - label: "Documentation home"
    to: "/"
    icon: "i-lucide-house"
  - label: "Infrastructure"
    to: "/dev/infrastructure"
    icon: "i-lucide-server"
  - label: "Databases"
    to: "/dev/databases"
    icon: "i-lucide-database"
  - label: "Back-env"
    to: "/dev/back-env"
    icon: "i-lucide-key"
---

# Development References

> The former `docs/dev/` documentation tree was a parallel archive and planning system. Planning is now centralized under the main documentation project:

- [Recommendations first](../recommendations.md)
- [Canonical plans](../plans/README.md)
- [Documentation lifecycle](../plans/document-lifecycle.md)

Current guides, architecture references, deployment procedures, and project documentation remain in their dedicated sections under [`docs/README.md`](../README.md). Historical development records that were previously under `docs/dev/plans/` were removed; git history is the archive.

## Current Development Sections

- [Infrastructure](/docs/en/dev/infrastructure) — proxy, workers, deployment, troubleshooting
- [Databases](/docs/en/dev/databases) — schema, migrations, fixtures, POS schema
- [Back-env](/docs/en/dev/back-env) — settings reference, environment variables
- [Customization](/docs/en/dev/customization) — methods, design system

> **Do not add new plans here.** Add them to `docs/plans/<scope>/` and link them from the canonical registry.
