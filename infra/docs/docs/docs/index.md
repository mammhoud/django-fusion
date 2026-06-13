# VResume Documentation

Welcome to the official documentation for **VResume** — a personal portfolio CMS built with Django, Wagtail, HTMX, and Bootstrap.

**Live:** [vresume.structa.cloud](https://vresume.structa.cloud) · **Author:** [mammhoud](https://github.com/mammhoud) · **Company:** [Structa](https://structa.cloud)

---

## Quick Links

| | |
|---|---|
| [Getting Started](getting_started.md) | First-time setup, local dev, Docker |
| [Deployment](deployment.md) | Production setup, SSL, Docker Compose |
| [Development](development.md) | Dev workflow, Makefile, commands |
| [Architecture](architecture/index.md) | System design, models, request flow |
| [Project Structure](architecture/project_structure.md) | Directory tree and module breakdown |
| [Configuration](architecture/configuration.md) | YAML settings, Jinja, and Pydantic |
| [Design System](design/index.md) | BEM conventions, SCSS, JS components |
| [User Guide](user-guide/index.md) | Content editor guide (blog, portfolio, newsletter) |
| [Change Logs](logs/index.md) | Refactoring notes and change history |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, Django 5, Wagtail CMS |
| Frontend | HTMX, Bootstrap 5, SCSS (BEM), Webpack |
| Database | PostgreSQL (production), SQLite (local dev) |
| Task queue | Celery + Redis |
| Infrastructure | Docker, Gunicorn, Nginx |
| Dev tools | Ruff, Pytest, webpack-bundle-analyzer |

---

## Template Structure (v1.1)

All templates live in a single directory: `v1/pages/templates/`

```
pages/templates/
├── base.html           Root layout
├── skeleton.html       Thin extends-base wrapper
├── navigator.html      Tab navigation
├── sidebar.html        Profile sidebar
├── layout/             meta, footer, cookie-popup
├── errors/             400–504 error pages
├── email/              Transactional email bases
├── home/               fragment + sections
├── about/              fragment + sections
├── resume/             fragment + sections
├── portfolio/          fragment + sections + modals
├── blog/               fragment + sections + modals + standalone
├── skills/             fragment + sections
└── connect/            fragment + sections + newsletter + emails + blocks
```

See [architecture/templates-flow.md](architecture/templates-flow.md) for the full tree and HTMX flow diagrams.

---

## Support & Contact

For support, inquiries, or enterprise deployments, please contact us:

- **Company Email**: [structa.cloud@gmail.com](mailto:structa.cloud@gmail.com)
- **Developer Email**: [mahmoud.ezzat.moustafa@gmail.com](mailto:mahmoud.ezzat.moustafa@gmail.com)
- **Phone / WhatsApp**: +201016127655

---

Developed with ❤️ by **mammhoud** @ **Structa**
