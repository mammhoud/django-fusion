---
title: Changelogs
description: Version history and release notes across all Structa Cloud projects.
navigation:
  title: Changelogs
  icon: i-lucide-git-commit
object:
  type: "reference"
  id: "changelogs.index"
attributes:
  source_path: "changelogs/README.md"
  canonical_route: "/docs/en/changelogs"
  source_of_truth: "repository-markdown"
  audience: "engineers, operators, and coding agents"
  status: "maintained"
  owner: "workspace"
tags:
  - structa-cloud
  - changelogs
  - releases
  - version-history
links:
  - label: "Documentation home"
    to: "/"
    icon: "i-lucide-house"
  - label: "Recent Changes"
    to: "/recent-changes"
    icon: "i-lucide-history"
---

# 📝 Changelogs

> Version history and release notes across all Structa Cloud projects — extracted from the real `CHANGELOG.md` at repo root.

---

## Per-Project Changelogs

| Project | Changelog | Coverage |
|---------|-----------|----------|
| Repo-wide infrastructure | [`repo.md`](repo.md) | Core rename, CI gates, docs overhaul |
| POS desktop app | [`pos.md`](pos.md) | Gaming center, 3-edition system, Cloud CRM |
| django-fusion | [GitHub Releases](https://github.com/mammhoud/django-fusion/releases) | Component registry, analyzer, routing |
| ceptor-ai | [GitHub Releases](https://github.com/mammhoud/ceptor-ai/releases) | MCP integration, chat streaming |

---

## Repo-Wide Timeline

### 2026-07-19 — Infrastructure Restructuring (current)

- `core/` → `projects/` — standard monorepo convention
- `core/libs/` → `libs/` — libraries at repo root (git submodules)
- `core/lms-demo/` → `projects/lms/` — canonical naming
- `core/VResume/` → `projects/portfolio/` — descriptive name
- `core/tinker/` → `projects/cypercloud/` — new brand

### 2026-07-01 — Docs Cross-Link Sweep + CI Gates

- Fixed every broken relative cross-link in legacy library READMEs
- Added `check_markdown_links.py` and `check_extras_in_docs.py` CI scripts
- Fixed `_LazyIncludeTemplate.template` rendering equivalence bug
- Renamed legacy codenames (nawaai → ceptor-ai, crafts → ceptor)

### 2026-06-30 — Template Reorganization

- Deduplicated 60+ template files across `projects/assets/templates/`
- Inlined per-site Django settings with Dynaconf
- Stabilized component system with canonical import paths

---

## Conventions

```markdown
## YYYY-MM-DD — short title

### category: description

- Specific change with file path when relevant
```

Each entry links to the relevant project docs for full context.

---

## Related

| Topic | Path |
|-------|------|
| Repo infrastructure | [`repo.md`](repo.md) |
| POS changelog | [`pos.md`](pos.md) |
| Libs changelog | [`libs.md`](libs.md) |
| Recent changes | [`../recent-changes.md`](../recent-changes.md) |
| POS editions | [`../projects/pos/editions.md`](../projects/pos/editions.md) |
