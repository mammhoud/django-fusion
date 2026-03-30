# AllianceCore Platform

**AllianceCore** is a production-ready, full-stack SaaS platform built on Django and Wagtail. It provides a modular foundation for building Learning Management Systems, community portals, and content-driven web applications.

---

## 🎯 Mission

To provide a battle-hardened, AI-ready platform that teams can extend quickly — without sacrificing code quality, security, or scalability.

---

## 🧩 Core Modules

| Module | Description | Status |
|---|---|---|
| **Core** | Django/Wagtail project shell, settings, URL routing, ASGI/WSGI | ✅ Stable |
| **Handlers** | User profiles, identity orchestration, Allauth adapters, 2FA, invitations | ✅ Stable |
| **Blog** | Wagtail CMS blogging engine with categories, multi-author, SEO | ✅ Stable |
| **Pages** | Wagtail pages — landing, contact form, contact submissions | ✅ Stable |
| **LMS** | Learning Management System — courses, lessons, enrollments | 🚧 In Progress |
| **CI / Temporal** | Durable background workflows (onboarding, batch processing) | ✅ Stable |

---

## 🛠️ Technology Stack

### Backend
| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| Framework | Django (latest LTS) |
| CMS | Wagtail |
| API | Django Ninja + Django Ninja Extra |
| Auth | Django Allauth (social, 2FA, passkeys) |
| Background Jobs | Django RQ + Temporal (durable workflows) |
| Database | PostgreSQL (via psycopg 3) |
| Cache | Redis (django-redis) |
| Real-Time | Django Channels (ASGI / WebSocket) |
| Observability | Sentry, Prometheus, Structlog, Django Silk |
| Storage | AWS S3 (django-storages + boto3) |

### Frontend
| Layer | Technology |
|---|---|
| Build Tool | Webpack 5 |
| CSS | Bootstrap 5 + PostCSS + SCSS |
| JS | Vanilla JS (modular, no heavy SPA framework) |
| Interactivity | AlpineJS + HTMX |
| Components | Vue SFCs (optional, per-page) |
| Internationalisation | Django i18n (AR, EN, ES, FR, IT, RU, TR, ZH-HANS, ZH-HANT) |

### Infrastructure
| Layer | Technology |
|---|---|
| Containerisation | Docker + Docker Compose |
| Web Server | Nginx |
| App Server | Gunicorn (WSGI) + Uvicorn (ASGI) |
| AI Integration | MCP via `django-grep` (source clone) |

---

## 📁 Project Layout

```
core/
├── apps/                   # Django applications (blog, handlers, pages, LMS)
├── assets/                 # Frontend static files, templates, bundles
│   ├── static/             # Source JS, SCSS, images
│   └── templates/          # Allauth and shared HTML templates
├── components/             # Reusable Django Bird components (HTML partials)
├── compose/                # Docker Compose service definitions
├── configs/                # Django settings (base, local, production)
│   └── settings/
├── core/                   # Django project core (urls, asgi, wsgi, CI)
│   └── CI/                 # Temporal workflow & activity definitions
├── docs/                   # ← You are here: all project documentation
├── locale/                 # Translation files (.po / .mo)
├── webpack/                # Webpack configuration (common + main)
├── pyproject.toml          # Project metadata and dependencies (uv)
└── package.json            # Node.js dependencies
```

---

## 🔌 AI-Readiness (MCP)

AllianceCore is designed to work with AI agents via the **Model Context Protocol (MCP)**. The `django-grep` package (installed from source) provides the MCP server that gives AI agents direct access to the Django environment.

See [integrations/mcp.md](./integrations/mcp.md) for setup and usage.

---

## 📖 Further Reading

- [Installation Guide](./INSTALL.md)
- [Settings Reference](./config/settings.md)
- [JavaScript Architecture](./frontend/js-architecture.md)
- [Temporal Workflows](./architecture/temporal-workflows.md)
