# Project Structure

VResume follows a modular Django/Wagtail architecture, designed to separate core infrastructure from content-specific logic.

## 📂 Root Directory

| Path | Description |
| :--- | :--- |
| `v1/` | The primary application source code. |
| `docs/` | MkDocs documentation source. |
| `compose/` | Docker Compose configuration snippets. |
| `scripts/` | Automation and utility scripts. |
| `Makefile` | The central command interface for development. |
| `mkdocs.yml` | Documentation site configuration. |

## 📦 Application Source (`v1/`)

The backend is organized into several key directories:

### `v1/core/`
The "brain" of the application. Contains shared logic that isn't specific to a single content type.
- `pages_base.py`: Base abstract models for all Wagtail pages.
- `page_blocks.py`: Reusable StreamField blocks (Hero, Services, Testimonials).
- `snippets/`: Reusable content snippets (Social links, Navbar items).
- `middleware.py`: Custom Django middleware (Cookies, Tracking).

### `v1/pages/`
Contains the actual Wagtail Apps. Each subdirectory represents a logical section of the site.
- `home/`: Homepage logic and sections.
- `about/`: About me, biography, and experience.
- `portfolio/`: Project showcase and filtering.
- `blog/`: Articles, categories, and tags.
- `cv/`: Professional resume and timeline data.
- `connect/`: Contact forms and newsletter subscriptions.
- `templates/`: Centralized HTML templates (organized by app).

### `v1/configs/`
Configuration management system.
- `settings/conf.py`: The settings loader (Pydantic + Dynaconf).
- `settings/ENV/`: YAML files containing environment-specific settings.

### `v1/assets/`
Frontend source files and compiled bundles.
- `src/`: SCSS and JavaScript source files.
- `static/`: Static assets (images, fonts).
- `bundles/`: Compiled Webpack bundles.

### `v1/webpack/`
Build system configurations for frontend assets.

## 🛠️ Infrastructure
- **Docker Stacks**: Modular compose files (`docker-compose.db.yml`, `app.yml`, `proxy.yml`) allow for independent service management.
- **Makefile**: Proxies all complex commands into simple aliases (e.g., `make dev`, `make build`).
