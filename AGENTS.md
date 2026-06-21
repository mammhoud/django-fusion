# Django Customizer – AI Agent Instructions

## Project Context & Philosophy

Before we dive into code, let’s define the core concepts we’re building:

| Concept | What it means for your Django project |
| :--- | :--- |
| **Django Customizer** | A web interface (built with Wagtail) that lets non‑developers add new fields to pages, change SCSS variables, and manage components without touching the codebase. |
| **Design Customizer** | A system that takes Figma designs, converts them to BEM‑compliant SCSS, and applies them to the frontend. |
| **Data Customizer** | A Wagtail‑based UI that lets users add new fields to any page model, generates the corresponding migrations, and updates the admin. |
| **Component Search** | A tool that scans your Django templates and finds all instances of a given component, highlighting duplicates and usage notes. |
| **Deployment & MCP** | A Model Context Protocol (MCP) server that monitors your deployment, checks that migrations are applied, and verifies the new design is live. |

---

## 📄 `AGENTS.md` – The AI's "README"

Place this file at the root of your Django project. It tells every AI agent (Kilo, Cursor, etc.) how to behave in your codebase.

```markdown
# Django Customizer – AI Agent Instructions

## Project Overview
This is a Django + Wagtail project that lets users customize page designs and data models through a web interface. The AI must follow strict conventions when generating or modifying code.

## Code Style & Standards
- **Python**: Follow PEP 8. Use type hints for all functions. Max line length: 88 (Black default).
- **Django**: Use class‑based views (CBV) wherever possible. Keep business logic in `services.py` files, not in views.
- **Wagtail**: All page models must inherit from `Page` and include `content_panels` and `promote_panels`. Use `StreamField` for flexible content.
- **SCSS**: Follow BEM naming: `.block__element--modifier`. Never use IDs for styling. All variables go in `_variables.scss`.
- **Templates**: Use `{% include %}` for reusable components. Pass only the necessary context.

## Architecture
- **Apps**: `core` (base settings), `customizer` (the main customizer logic), `design` (SCSS/theme management), `components` (reusable UI components).
- **Services**: Place all business logic in `services/` folders inside each app.
- **MCP Integration**: The MCP server runs on `localhost:8001` and exposes endpoints for deployment status (`/health`) and migration checks (`/migrations/status`).

## Testing
- Write unit tests for all customizer logic (`pytest`).
- Use `selenium` or `playwright` for Wagtail admin UI tests.
- Ensure migration files are tested before deployment.

## Deployment
- Use `docker-compose` for local development and production.
- The deployment script (`deploy.sh`) runs migrations, collects static files, and restarts the server.
- After deployment, verify with `curl http://localhost:8001/health` to ensure MCP is healthy.

## Wagtail Customization
- New fields added via the customizer must be saved in `Page` models using `WagtailFieldPanel`.
- Generate migrations with `python manage.py makemigrations` and apply with `python manage.py migrate`.
- Never delete a field without first confirming it's not used in any template.

## Component Search
- To find all usages of a component, use `grep -r "component_name" templates/`.
- If a component is found twice, note both locations and suggest consolidation.

## Design Changes
- When a new SCSS file is added, update `main.scss` to import it.
- Use `@use` instead of `@import` for SCSS modules.
- Ensure all new styles are responsive (mobile‑first).