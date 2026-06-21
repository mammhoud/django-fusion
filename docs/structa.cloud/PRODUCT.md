# AllianceCore – Professional Wagtail CMS Foundation

## The Heart of a Modern Digital Ecosystem

**AllianceCore** is a production-hardened, modular CMS foundation built with **Django 5.x** and **Wagtail 6.x**, designed to power complex web applications and scale from MVP to enterprise.

---

## 🧩 Installed Applications

### Core Django
| App | Purpose |
|---|---|
| `django.contrib.auth` | User authentication and permissions |
| `django.contrib.admin` | Django admin interface |
| `django.contrib.sites` | Multi-site framework |
| `django.contrib.sessions` | Session management |
| `django.contrib.messages` | Flash messaging |
| `django.contrib.staticfiles` | Static file serving |
| `django.contrib.sitemaps` | XML sitemap generation |
| `django.contrib.humanize` | Human-friendly data formatting |
| `django.contrib.contenttypes` | Generic content type framework |
| `django.contrib.postgres` | PostgreSQL-specific fields and operations |

### Wagtail CMS
| App | Purpose |
|---|---|
| `wagtail` | Core CMS engine |
| `wagtail.contrib.forms` | Form builder |
| `wagtail.contrib.redirects` | URL redirect management |
| `wagtail.contrib.routable_page` | URL routing within pages |
| `wagtail.contrib.search_promotions` | Search result promotions |
| `wagtail.contrib.sitemaps` | Wagtail sitemap integration |
| `wagtail.contrib.settings` | Site-wide settings snippets |
| `wagtail.contrib.frontend_cache` | Frontend cache invalidation |
| `wagtail.contrib.simple_translation` | Multi-language page translation |
| `wagtail.contrib.table_block` | Table content blocks |
| `wagtail.contrib.typed_table_block` | Typed table blocks |
| `wagtail.documents` | Document management |
| `wagtail.embeds` | Embedded media support |
| `wagtail.images` | Image management with renditions |
| `wagtail.search` | Full-text search |
| `wagtail.snippets` | Reusable content snippets |
| `wagtail.sites` | Wagtail site configuration |
| `wagtail.admin` | Wagtail admin interface |
| `wagtail.users` | Wagtail user management |
| `wagtail.locales` | Locale management for i18n |
| `wagtail_newsletter` | Newsletter integration |
| `wagtailfontawesomesvg` | Font Awesome SVG icons in Wagtail |
| `taggit` | Tagging support |
| `modelcluster` | In-memory model clustering for Wagtail |

### Django Unfold Admin
| App | Purpose |
|---|---|
| `unfold` | Modern admin UI replacing default Django admin |
| `unfold.contrib.filters` | Enhanced admin filters |
| `unfold.contrib.forms` | Styled admin forms |
| `unfold.contrib.inlines` | Enhanced inline admin |
| `unfold.contrib.import_export` | Import/export integration |
| `unfold.contrib.guardian` | Object-level permission UI |
| `unfold.contrib.simple_history` | History tracking UI |

### Authentication — django-allauth
| App | Purpose |
|---|---|
| `allauth` | Core allauth framework |
| `allauth.account` | Email/password account management |
| `allauth.mfa` | Multi-factor authentication (TOTP, WebAuthn, recovery codes) |
| `allauth.socialaccount` | Social authentication base |
| `allauth.socialaccount.providers.google` | Google OAuth2 |
| `allauth.socialaccount.providers.github` | GitHub OAuth2 |
| `allauth.socialaccount.providers.facebook` | Facebook OAuth2 |
| `allauth.socialaccount.providers.linkedin_oauth2` | LinkedIn OAuth2 |

### Third-Party Integrations
| App | Purpose |
|---|---|
| `webpack_loader` | Webpack bundle integration |
| `django_htmx` | HTMX request/response helpers |
| `import_export` | Django import/export for admin |
| `simple_history` | Model change history tracking |
| `django_extensions` | Developer utilities (shell_plus, etc.) |
| `django_structlog` | Structured JSON logging |
| `heroicons` | Heroicons SVG icon set |
| `embed_video` | Video embedding (YouTube, Vimeo) |
| `colorfield` | Color picker field |
| `django_rq` | Redis Queue background jobs |

### django-osoul (Internal Library)
| App | Purpose |
|---|---|
| `django_osoul.pipelines` | Core models, auth views, newsletter, user pipelines |
| `django_osoul.comp` | PageHandler, HTMX components, notification system |
| `django_osoul.mcp_designer` | MCP server integration for AI tooling |

### Project Apps
| App | Purpose |
|---|---|
| `apps.pages` | Wagtail page models (HomePage, AboutPage, etc.) |
| `apps.handlers` | Core request handlers, startup diagnostics, signals |
| `apps.handlers.registration` | Allauth registration adapter, AuthEmailTemplate, token generator, email service |
| `apps.blog` | Blog engine with multi-author support |
| `apps.LMS` | Learning Management System (courses, modules, lessons, quizzes, certificates) |
| `alliance.CI` | CI/CD utilities and deployment helpers |
| `alliance` | Alliance platform core |

---

## 🔌 Key Features Added in Latest Release

### Authentication & Registration (`apps.handlers.registration`)
- `RegistrationAdapter` — custom allauth `DefaultAccountAdapter` routing lifecycle events into the email service
- `AuthEmailTemplate` — Wagtail snippet for editable transactional email templates (registration confirmation, sign-in success) with single-active invariant
- `RegistrationTokenGenerator` — HMAC-SHA256 signed tokens with allauth key embedding and 24-hour expiry
- `AllauthLoginView` / `AllauthSignupView` — `PageHandler` subclasses with HTMX fragment rendering and `HX-Trigger: showNotification` on every response
- Multi-sender SMTP email service with failover and Django backend fallback

### Server Diagnostics (`apps.handlers.startup`)
- Startup validation in `HandlersConfig.ready()`: SECRET_KEY length, insecure placeholder detection, duplicate YAML settings, URL routing resolution, middleware ordering

### Health Check
- `GET /health/` → `{"status": "ok"}` — served by `django_osoul.pipelines` (shared with ctc-research)

### Management Commands
| Command | Description |
|---|---|
| `validate_config` | Audit YAML/`.env` for duplicate settings and insecure SECRET_KEY |
| `verify_deployment` | Docker container, network, port, env var, Traefik, and health checks |

### Social Authentication
- Google, GitHub, Facebook, LinkedIn OAuth2 providers configured
- `SocialAccountAdapter` from django-osoul for custom signup flow

### MFA
- TOTP, WebAuthn, and recovery codes via `allauth.mfa`

---

## 🏗️ Architecture

```
structa.cloud/
├── core/                        # Django project root (PORT=5080)
│   ├── apps/
│   │   ├── handlers/            # Core app: auth, registration, startup, health
│   │   │   └── registration/    # Allauth adapter, tokens, emails, views
│   │   ├── pages/               # Wagtail page models
│   │   ├── blog/                # Blog engine
│   │   └── LMS/                 # Learning Management System
│   ├── configs/                 # Dynaconf + Pydantic settings
│   └── compose/                 # Docker + Traefik configs
└── libs/
    └── django-osoul/             # Shared internal library
        └── src/django_osoul/
            ├── pipelines/       # Models, auth views, /health/, newsletter
            └── comp/            # PageHandler, HTMX, notifications
```

---

## 🚀 Quick Start

```bash
# Local development (SQLite)
cd core && ./run_containers.sh

# Production (Postgres + Redis + Traefik)
cd core && ./run_containers.sh --prod
```

---

[View Live Demo](https://core.structa.cloud) | [Purchase License](https://structa.cloud)
