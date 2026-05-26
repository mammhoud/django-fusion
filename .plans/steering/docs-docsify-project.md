---
title: Docs Docsify Project
description: Rules for placing task reports, summaries, phases, and any generated docs into the unified docsify docs/ project with correct sidebar links
inclusion: auto
---

# Docs Docsify Project

## Overview

All task completion reports, implementation summaries, phase notes, migration reports, and any other generated markdown files **must** be placed inside the `docs/` docsify project — never left at the workspace root or in ad-hoc locations.

The docs site is served by the `docs` Docker container (nginx + docsify) and is accessible at `https://docs.structa.cloud`.

---

## Docs Project Structure

```
docs/
├── README.md                    # Home page
├── _sidebar.md                  # Global navigation (must be updated for every new file)
├── ecosystem/                   # Cross-site: architecture, deployment, development, getting-started
│   ├── architecture/            # System design, specs, task systems, boundary analysis
│   ├── deployment/              # Docker, nginx, production procedures, deployment reports
│   ├── development/             # Workflows, coding standards, implementation plans, phase notes
│   └── getting-started/         # Installation, environment setup, quick-start guides
├── structa.cloud/               # structa.cloud (Tech Bridges Platform) specific docs
│   ├── apps/                    # Per-app documentation
│   ├── config/                  # Settings and configuration docs
│   ├── frontend/                # JS architecture, webpack, styling
│   ├── plugins/                 # Plugin documentation
│   ├── reference/               # API reference, pydocs
│   └── integrations/            # Third-party integrations (MCP, etc.)
├── ctc-research.com/            # ctc-research.com (LMS & Blog Platform) specific docs
│   ├── apps/                    # Per-app documentation
│   ├── config/                  # Settings and configuration docs
│   ├── frontend/                # JS architecture, webpack, styling
│   ├── lms/                     # LMS feature docs and roadmap
│   ├── reference/               # API reference, pydocs
│   └── integrations/            # Third-party integrations
├── packages/                    # Internal library docs
│   ├── django-osoul/            # Routing & component framework
│   ├── django-rseal/            # Email & Wagtail utilities
│   ├── django-grep/             # Health checks & search
│   └── nawaai/                  # AI toolkit
├── infrastructure/              # Docker, Traefik, nginx, PostgreSQL, Redis, LMS, Blinko
└── shared/                      # Cross-cutting: styling, testing, troubleshooting, scripts
```

---

## File Placement Rules

### Where does my file go?

| File type | Target directory |
|---|---|
| Task completion report, phase summary | `docs/ecosystem/development/` |
| Architecture analysis, spec summary, boundary report | `docs/ecosystem/architecture/` |
| Deployment report, migration verification, production summary | `docs/ecosystem/deployment/` |
| structa.cloud app or plugin doc | `docs/structa.cloud/apps/` or `docs/structa.cloud/plugins/` |
| ctc-research.com app or feature doc | `docs/ctc-research.com/apps/` |
| LMS feature doc | `docs/ctc-research.com/lms/` |
| Internal library (django-grep, django-osoul, django-rseal) | `docs/packages/<lib-name>/` |
| Infrastructure change (Docker, nginx, Traefik) | `docs/infrastructure/<service>/` |
| Styling or CSS report | `docs/shared/styling/` |
| Testing report or checklist | `docs/shared/testing/` |
| Troubleshooting guide | `docs/shared/troubleshooting/` |
| Getting-started or install guide | `docs/ecosystem/getting-started/` |
| Cross-site shared feature | `docs/shared/` or `docs/ecosystem/` |

### Naming Convention

- **kebab-case** for all filenames: `task-completion-report.md` not `TaskCompletionReport.md`
- **Numbered prefix** for sequential content: `01-`, `02-`, etc.
- **Descriptive suffix** for report types:
  - `*-summary.md` — high-level summary of completed work
  - `*-report.md` — detailed findings or verification results
  - `*-plan.md` — implementation or migration plan
  - `*-guide.md` — how-to guide
  - `*-checklist.md` — verification or completion checklist
  - `README.md` — section overview (one per directory)

**Examples:**

```
docs/ecosystem/development/allauth-htmx-auth-summary.md
docs/ecosystem/architecture/routing-layers-analysis.md
docs/ecosystem/deployment/webpack-unified-build-report.md
docs/structa.cloud/plugins/blog-plugin-implementation.md
docs/ctc-research.com/lms/enrollment-feature-summary.md
docs/packages/django-osoul/fragment-component-guide.md
```

---

## Sidebar Update Rule

**Every new file added to `docs/` must have a corresponding entry in `docs/_sidebar.md`.**

The sidebar uses docsify's nested list format. Match the nesting level to the directory depth.

### Current Sidebar Structure

```markdown
* [Documentation Overview](README.md)
* [Ecosystem](ecosystem/)
  * [Getting Started](ecosystem/getting-started/)
  * [Architecture](ecosystem/architecture/)
  * [Deployment](ecosystem/deployment/)
  * [Development](ecosystem/development/)
* [Projects]()
  * [structa.cloud](structa.cloud/)
  * [ctc-research.com](ctc-research.com/)
* [Packages](packages/)
  * [django-osoul](packages/django-osoul/)
  * [django-rseal](packages/django-rseal/)
  * [django-grep](packages/django-grep/)
  * [nawaai](packages/nawaai/)
* [Infrastructure](infrastructure/)
  * [Docker](infrastructure/docker/)
  * [Traefik](infrastructure/traefik/)
  * [Nginx](infrastructure/nginx/)
  * [PostgreSQL](infrastructure/postgres/)
  * [Redis](infrastructure/cache/)
  * [LMS](infrastructure/lms/)
  * [Blinko](infrastructure/blinko/)
* [Shared Resources](shared/)
  * [Styling](shared/styling/)
  * [Testing](shared/testing/)
  * [Troubleshooting](shared/troubleshooting/)
  * [Scripts](shared/scripts/)
```

### How to Add a New Entry

Add the link at the correct nesting level. Use the file path relative to `docs/`:

```markdown
* [Ecosystem](ecosystem/)
  * [Development](ecosystem/development/)
    * [Allauth HTMX Auth Summary](ecosystem/development/allauth-htmx-auth-summary.md)
```

For a new top-level section (rare), add it at the root level and create a `README.md` in that directory.

---

## Workflow: Adding a New Doc File

When creating any report, summary, or documentation file, follow these steps in order:

**1. Determine the correct directory** using the placement table above.

**2. Create the file** with kebab-case naming and the appropriate suffix.

**3. Add front-matter** at the top of the file:

```markdown
# Title of the Document

> Brief one-line description

**Date:** YYYY-MM-DD
**Site:** structa.cloud | ctc-research.com | Both
**Status:** Complete | In Progress | Draft
```

**4. Update `docs/_sidebar.md`** — add the link at the correct nesting level.

**5. Update the section `README.md`** — add a brief entry and link in the section's index file.

---

## Do Not Place Docs Here

These locations are **wrong** for documentation files:

| Wrong location | Correct location |
|---|---|
| Workspace root (`*.md` at `/`) | `docs/ecosystem/development/` or appropriate section |
| `websites/*.md` | `docs/ecosystem/development/` or `docs/structa.cloud/` |
| `websites/ctc-research.com/*.md` | `docs/ctc-research.com/` |
| `websites/structa.cloud/*.md` | `docs/structa.cloud/` |
| `.kiro/specs/*/` (after completion) | `docs/ecosystem/development/` (summary) |

Existing misplaced files at the workspace root (`ASSETS_FIX_SUMMARY.md`, `DEPLOYMENT_SUMMARY.md`, `HEALTH_CHECK_QUICK_REFERENCE.md`) should be moved to their correct `docs/` location when touched.

---

## Section README Template

Every directory in `docs/` should have a `README.md` that acts as the section index:

```markdown
# Section Name

> One-line description of what this section covers.

## Contents

| File | Description |
|---|---|
| [file-name.md](file-name.md) | What it covers |

## Related Sections

- [Link to related section](../other-section/)
```

---

## Quick Reference

```
Task/phase completion  →  docs/ecosystem/development/<kebab-name>-summary.md
Architecture report    →  docs/ecosystem/architecture/<kebab-name>-report.md
Deployment report      →  docs/ecosystem/deployment/<kebab-name>-report.md
structa.cloud feature  →  docs/structa.cloud/<section>/<kebab-name>.md
ctc-research feature   →  docs/ctc-research.com/<section>/<kebab-name>.md
Package/lib doc        →  docs/packages/<lib-name>/<kebab-name>.md
Infrastructure doc     →  docs/infrastructure/<service>/<kebab-name>.md
Always update          →  docs/_sidebar.md  +  section README.md
```
