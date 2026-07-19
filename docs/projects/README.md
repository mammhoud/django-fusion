# 🏢 Projects — Index

> Every project in the Structa Cloud monorepo — languages, frameworks, ports, domains, and documentation.

---

## Language & Framework Matrix

| Project | Language | Framework | Database | Runtime |
|---------|----------|-----------|----------|---------|
| **LMS** | Python | Django 4.2 + Wagtail 7.4 | PostgreSQL | Docker / Gunicorn |
| **Portfolio** | Python | Django 4.2 + Wagtail 7.4 | PostgreSQL | Docker / Gunicorn |
| **Cypercloud** | Python | Django 4.2 | SQLite | Docker / Gunicorn |
| **Shared** | Python | Django 4.2 + Celery + Dramatiq | PostgreSQL | Docker / Worker |
| **POS — Frontend** | TypeScript | React 19 + Vite 7 + Tailwind CSS 4 | — | Tauri 2 |
| **POS — Backend** | Rust | Diesel ORM + Tauri 2 | SQLite | Native binary |
| **POS — Sidecar** | Python | Sanic + Django ORM | SQLite | Spawned by Tauri |
| **django-fusion** | Python | Django (library) | — | pip (editable) |
| **ceptor-ai** | Python | Sanic + MCP (library) | — | pip (editable) |

---

## Project Documentation

| Project | Directory | Port | Domain | Docs |
|---------|-----------|------|--------|------|
| **LMS** | `projects/lms/` | 5071 | structa.cloud | [`lms/`](lms/) |
| **Portfolio** | `projects/portfolio/` | 5072 | vresume.structa.cloud | [`portfolio/`](portfolio/) |
| **Cypercloud** | `projects/cypercloud/` | 5073 | localhost | [`cypercloud/`](cypercloud/) |
| **Shared** | `projects/www/` | 5080 | shared core + workers | [`shared/`](shared/) |
| **POS** | `projects/pos/` | — | Desktop app | [`pos/`](pos/) |
| **Libs** | `libs/` | — | Submodules | [`libs/`](libs/) |

---

## Documentation Structure

Each project directory contains:

| File | Purpose |
|------|---------|
| `README.md` | Project overview, guide, code map, customization key |
| `configuration.md` | Settings, env vars, site registration, Docker config |
| `use-cases.md` | Real-world deployment scenarios and customization examples |

Additional project-specific files:

| Project | Extra Files |
|---------|-------------|
| **LMS** | `clone-guide.md` — How to clone LMS as template for new sites |
| **POS** | `editions.md` — Minimal/Solo/Full comparison; `rust-backend.md`, `typescript-frontend.md`, `sidecar-*.md`, `network-architecture.md`, `changelog.md` |

---

## Customization Key

| Tag | Code | Meaning |
|-----|------|---------|
| 🟢 | `customizable` | Safe to modify, extend, or override |
| 🔴 | `not-customizable` | Core framework code — modify at your own risk |
| 🟡 | `delegate` | Can be extended through delegation/hooks |
| 🔵 | `template` | Template-level customization only |
| ⚪ | `config` | Configure via settings/env vars only |

---

## Related

| Resource | Path |
|----------|------|
| Customization guide | [`../customization/`](../customization/) |
| Infrastructure docs | [`../infrastructure/`](../infrastructure/) |
| Guides | [`../guides/`](../guides/) |
| AI & Agents | [`../ai/`](../ai/) |
| Changelogs | [`../changelogs/`](../changelogs/) |
