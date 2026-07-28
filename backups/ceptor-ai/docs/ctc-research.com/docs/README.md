# Alliance Documentation

Welcome to the Alliance platform documentation. This directory is the single source of truth for all technical documentation, architecture guides, and product references.

## 📚 Table of Contents

### 🗺️ Project Overview
| Document | Description |
|---|---|
| [PRODUCT.md](./PRODUCT.md) | Platform overview, modules, and tech stack |
| [INSTALL.md](./INSTALL.md) | Docker-based installation and first-run guide |

### 🏗️ Architecture
| Document | Description |
|---|---|
| [architecture/temporal-workflows.md](../../../docs/ctc-research.com/architecture/temporal-workflows.md) | Temporal durable workflow engine — activities, workers, testing |

### 🖥️ Frontend
| Document | Description |
|---|---|
| [frontend/js-architecture.md](./frontend/js-architecture.md) | JavaScript module system design and manager overview |
| [frontend/js-codebase.md](./frontend/js-codebase.md) | Detailed JS file-by-file usage analysis |
| [frontend/pages-layout.md](../../../docs/ctc-research.com/frontend/pages-layout.md) | Page layout system — PagesManager, BaseLayout, LayoutManager |
| [frontend/preloader.md](./frontend/preloader.md) | Preloader component — types, CSS variables, JS API |
| [frontend/webpack.md](../../../docs/ctc-research.com/frontend/webpack.md) | Webpack configuration — common, main, dev server, optimization |
| [frontend/allauth-templates.md](../../../docs/ctc-research.com/frontend/allauth-templates.md) | Django Allauth template reference |

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
