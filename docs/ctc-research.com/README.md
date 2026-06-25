# Alliance Documentation

Welcome to the Alliance platform documentation. This directory is the single source of truth for all technical documentation, architecture guides, and product references.

## 📚 Table of Contents

### 🗺️ Project Overview
| Document | Description |
|---|---|
| [PRODUCT.md](./PRODUCT.md) | Platform overview, modules, and tech stack |
| [INSTALL.md](./INSTALL.md) | Docker-based installation and first-run guide |
| [CORE_DIRECTORY_REMOVAL_REPORT.md](../archives/ctc-research.com_CORE_DIRECTORY_REMOVAL_REPORT.md) | Core directory removal report and migration details |
| [MIGRATION_VERIFICATION_REPORT.md](../archives/ctc-research.com_MIGRATION_VERIFICATION_REPORT.md) | Migration verification report |

### 🏗️ Architecture
| Document | Description |
|---|---|
| [architecture/temporal-workflows.md](./architecture/temporal-workflows.md) | Temporal durable workflow engine — activities, workers, testing |

### 🖥️ Frontend
| Document | Description |
|---|---|
| [frontend/js-architecture.md](./frontend/js-architecture.md) | JavaScript module system design and manager overview |
| [frontend/js-codebase.md](./frontend/js-codebase.md) | Detailed JS file-by-file usage analysis |
| [frontend/pages-layout.md](./frontend/pages-layout.md) | Page layout system — PagesManager, BaseLayout, LayoutManager |
| [frontend/preloader.md](./frontend/preloader.md) | Preloader component — types, CSS variables, JS API |
| [frontend/webpack.md](./frontend/webpack.md) | Webpack configuration — common, main, dev server, optimization |
| [frontend/allauth-templates.md](./frontend/allauth-templates.md) | Django Allauth template reference |

### 📦 Apps
| Document | Description |
|---|---|
| [apps/blog.md](./apps/blog.md) | Blog CMS plugin — features, MCP integration |
| [apps/handlers.md](./apps/handlers.md) | Handlers plugin — profile, identity, security |
| [apps/contact-model.md](./apps/contact-model.md) | ContactSubmission model — analysis and improvement recommendations |
| [apps/profile-banner.md](./apps/profile-banner.md) | Profile banner actions — options and implementation examples |

### 🔌 Integrations
| Document | Description |
|---|---|
| [integrations/mcp.md](./integrations/mcp.md) | Model Context Protocol (MCP) — AI-driven development integration |

### ⚙️ Configuration
| Document | Description |
|---|---|
| [config/settings.md](./config/settings.md) | Django settings — environment variables and configuration reference |

---

## Contributing

When adding new documentation:
1. Place it in the appropriate subdirectory (`architecture/`, `frontend/`, `apps/`, `integrations/`, `config/`)
2. Add an entry to this index table
3. Use the `Alliance` brand name consistently (not `Xellent`, `CTC`, or `prj`)
4. Update cross-references if renaming or moving files




# ctc-research.com Documentation

> Xellent LMS Platform - Django + Wagtail

## Quick Links

### Getting Started
- [Getting Started Guide](getting-started/ctc_research_getting_started.md) - Complete setup guide

### Features
- [LMS Features](lms/) - Learning Management System documentation
  - [LMS Feature Roadmap](lms/01-lms-feature-roadmap.md)
  - [LMS README](lms/README.md)

### Reference
- [App Reference](reference/ctc-research-app.md) - Application structure
- [PyDocs](reference/pydocs_ctc_research.md) - API documentation

---

## Project Structure

```
ctc-research.com/
├── apps/
│   ├── accounts/          # Auth, registration, profile
│   ├── lms/               # Course, enrollment, certification
│   ├── blog/              # Blog pages
│   └── content/           # Wagtail CMS pages
├── core/                  # ASGI/WSGI, URLs, settings
├── configs/               # Dynaconf settings
├── assets/                # Static files, templates, media
└── tests/                 # Property-based tests
```

## Setup

```bash
cd ctc-research.com
uv sync --all-extras
cp .env.example .env
uv run python manage.py migrate
uv run pytest tests/ -v
```

## Health Checks

- `GET /health/` - Overall health
- `GET /health/database/` - Database connectivity
- `GET /health/assets/` - Static assets
- `GET /health/media/` - Media files

---

## Related Documentation

- [Ecosystem Overview](../ecosystem/)
- [Packages](../packages/)
- [Shared Resources](../shared/)
