# Alliance Documentation

Welcome to the Alliance platform documentation. This directory is the single source of truth for all technical documentation, architecture guides, and product references.

## 📚 Table of Contents

### 🗺️ Project Overview
| Document | Description |
|---|---|
| [PRODUCT.md](./PRODUCT.md) | Platform overview, modules, and tech stack |
| [INSTALL.md](./INSTALL.md) | Docker-based installation and first-run guide |
| [CORE_DIRECTORY_REMOVAL_REPORT.md](./CORE_DIRECTORY_REMOVAL_REPORT.md) | Core directory removal report and migration details |
| [MIGRATION_VERIFICATION_REPORT.md](./MIGRATION_VERIFICATION_REPORT.md) | Migration verification report |

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






# structa.cloud Documentation

> Alliance Platform - Django + Wagtail

## Quick Links

### Getting Started
- [Getting Started Guide](getting-started/structa_cloud_getting_started.md) - Complete setup guide

### Core Components
- [Alliance Module](alliance/) - Main application module
  - [Alliance README](alliance/README.md)
- [Plugin Architecture](plugins/) - Extensible plugin system
  - [Plugins README](plugins/README.md)

### Reference
- [App Reference](reference/structa-cloud-app.md) - Application structure
- [PyDocs](reference/pydocs_structa_cloud.md) - API documentation

---

## Project Structure

```
structa.cloud/
├── apps/
│   ├── accounts/          # Auth, registration, profile
│   ├── alliance/          # LMS models
│   ├── blog/              # Blog pages
│   └── content/           # Wagtail CMS pages
├── alliance/              # ASGI/WSGI, URLs, CI app
├── configs/               # Dynaconf settings
├── assets/                # Static files, templates, media
└── tests/                 # Test suite
```

## Setup

```bash
cd structa.cloud
uv sync --all-extras
cp .env.example .env
uv run python manage.py migrate
uv run pytest tests/ -v
```

## Key Features

### Alliance Module
- ASGI/WSGI entry points
- URL routing
- WebSocket handler
- CI/CD utilities

### Plugin System
- Extensible architecture
- Custom integrations
- Modular functionality

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
