---
# yaml-language-server: $schema=schemas/workspace.schema.json
Object type:
    - Workspace
Status: Published---

# Makefile — Build & Automation System

> **Type:** Workspace 🏢
> **Description:** The Structa Cloud build system — Makefile targets for development, testing, deployment, and repository management across all projects.

---

## Overview

The repository uses a layered Makefile delegation system:

| Makefile | Path | Purpose |
|----------|------|---------|
| **Root** | `Makefile` | Thin entrypoint, delegates to projects/ |
| **Project** | `projects/Makefile` | Canonical dispatcher — WEBSITE selection |
| **Site** | `projects/<site>/Makefile` | Site-specific commands |

---

## Project Context

| Aspect | Description |
|--------|-------------|
| **Root Path** | `Makefile` |
| **Dispatcher** | `projects/Makefile` |
| **Color** | Stone (#78716c) / Slate (#64748b) — representing build tools and infrastructure |
| **Format** | GNU Make with bash commands |

---

## Common Targets

| Target | Category | Description |
|--------|----------|-------------|
| `make dev WEBSITE=<site>` | Development | Run dev server for a site |
| `make deploy` | Deployment | Full stack deployment |
| `make test WEBSITE=<site>` | Testing | Run site tests |
| `make check WEBSITE=<site>` | Validation | Django system checks |
| `make pos` | POS | POS development targets |
| `make push` | Git | Push repo + submodules |

---

## Related Docs

- → `website-descriptions.md` — Site descriptions
- → `../../guides/setup.md` — Quick start
- → `../../guides/deployment.md` — Deployment guide
- → `../README.md` — Master index
