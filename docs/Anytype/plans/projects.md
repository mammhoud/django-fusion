---
# yaml-language-server: $schema=schemas/bookmark.schema.json
Object type:
    - Bookmark
    - Development
    - Documentation
    - Publishing
    - Staging
    - Done
Tags:
- Development
- Documentation
- Publishing
- Staging
- Done
    - projects
    - reference
    - index
Status: Published
---

# Projects — Directory & Repository Hub

> **Type:** Bookmark 🔖
> **Description:** Complete index of all Structa Cloud projects, sites, and applications — organized by category with direct repository paths.

---

## Web Projects

| Project | Path | Domain | Port | Status |
|---------|------|--------|:----:|--------|
| **CTC Research** | `projects/ctc-research/` | ctc-research.com | 5070 | ✅ Complete |
| **LMS Demo** | `projects/lms/` | structa.cloud | 5071 | ✅ Complete |
| **VResume / Portfolio** | `projects/portfolio/` | vresume.structa.cloud | 5072 | ✅ Complete |
| **CyperCloud AI** | `projects/cypercloud/` | localhost | 5073 | 🚧 Development |
| **Tinker (Template Customizer)** | `projects/tinker/` | — | — | 📋 Planned |

---

## POS Editions

| Edition | Path | Stack | Sync | Status |
|---------|------|-------|------|--------|
| **pos-mini** | `projects/pos/pos-mini/` | Rust (Tauri) + SQLite | Air-gapped | ✅ Complete |
| **pos-solo** | `projects/pos/pos-solo/` | Python (Django+Robyn) + SQLite | LAN | 🚧 In Development |
| **pos-full** | `projects/pos/pos-full/` | Python (Django+Robyn) + PostgreSQL | Cloud | 📋 Planned |
| **pos-cloud** | `projects/pos/pos-cloud/` | Web UI + PostgreSQL | Cloud | 📋 Planned |

---

## Shared Libraries

| Library | Path | Purpose |
|---------|------|---------|
| **django-fusion** | `libs/django-fusion/` | Component system, routing, forms/tables |
| **ceptor-ai** | `libs/ceptor-ai/` | AI chat client, MCP server, agent generation |

---

## Infrastructure

| Component | Path | Purpose |
|-----------|------|---------|
| **Traefik Proxy** | `applications/proxy/` | SSL termination, reverse proxy |
| **PostgreSQL + Redis** | `applications/databases/` | Data persistence, caching |
| **Docker Orchestration** | `applications/compose/` | Docker Compose files |
| **Kilo MCP Server** | `applications/kilo/` | MCP integration server |

---

## Documentation

| Section | Path | Description |
|---------|------|-------------|
| **MkDocs Site** | `docs/` | Full documentation site |
| **AnyType Workspace** | `docs/Anytype/` | Project knowledge graph |
| **AI Prompts** | `docs/ai/` | AI agent instructions |
| **Guides** | `docs/guides/` | Setup, deployment, customization |

---

## Project Color Map

| Project | Primary Color | Hex | Represents |
|---------|--------------|-----|------------|
| **CTC Research** | Sky Blue | `#0ea5e9` | Research, knowledge, trust |
| **LMS Demo** | Emerald | `#10b981` | Learning, growth, education |
| **VResume** | Violet | `#8b5cf6` | Creativity, portfolio, identity |
| **CyperCloud** | Cyan | `#06b6d4` | AI, intelligence, cloud |
| **Tinker** | Amber | `#f59e0b` | Customization, creativity, warmth |
| **pos-mini** | Rust Red | `#f7524a` | Lightweight, fast, minimal |
| **pos-solo** | Teal | `#0d9488` | Balanced, standalone, reliable |
| **pos-full** | Gold | `#eab308` | Enterprise, premium, scale |

---

## Related Docs

- → `projects-list.md` — Detailed project listing
- → `../../architecture/website-descriptions.md` — Full site descriptions
- → `product-development.md` — Product development lifecycle
- → `../../README.md` — Master index
