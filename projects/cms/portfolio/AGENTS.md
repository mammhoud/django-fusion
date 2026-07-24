# Portfolio / VResume — AI Agent Instructions

Path: `projects/cms/portfolio/` (Makefile alias: `portfolio` / `vresume`, deployed at vresume.structa.cloud:5072)

## Scope

This directory contains the Portfolio/VResume Django site — a Wagtail-powered personal portfolio and resume builder with tab-based navigation, blog, events, and contact features. The site is deployed at **vresume.structa.cloud** on port 5072.

---

## Template Resolution Order (Django TEMPLATES_DIRS)

1. `portfolio/templates/` — site-specific overrides (highest priority)
2. `portfolio/www/pages/<app>/templates/` — app-level page templates
3. `portfolio/plugins/<name>/templates/` — plugin templates
4. `assets/templates/` — shared cross-site templates (lowest priority)

---

## Site Template Tree

```
portfolio/templates/
└── (override shelf — add site-specific templates here)
```

---

## App Page Template Tree

```
portfolio/www/pages/
├── templates/               # Root page templates
│   ├── base.html            # Main base with tabs
│   ├── skeleton.html        # Outer skeleton wrapper
│   ├── sidebar.html         # Sidebar navigation
│   └── navigator.html       # Tab navigator
├── connect/templates/       # Contact page templates
│   ├── main.html
│   └── fragment.html
├── home/                    # HomePage: models, migrations
│   └── templates/
│       ├── main.html
│       └── fragment.html
├── about/                   # AboutPage: models, viewsets
│   └── templates/
│       ├── main.html
│       └── fragment.html
├── cv/                      # ResumePage: models
│   └── templates/
│       ├── main.html
│       └── fragment.html
├── events/                  # EventPage: models, views
│   └── templates/
│       ├── main.html
│       ├── event_page.html
│       └── sections/grid.html
├── blog/                    # BlogPage: models, viewsets, services
│   └── templates/
│       ├── main.html
│       └── fragment.html
├── portfolio/               # PortfolioPage: models
│   └── templates/
│       ├── main.html
│       └── fragment.html
└── accounts/templates/      # Account/auth templates (in plugins/)
```

---

## Plugin Template Tree

```
portfolio/plugins/
└── accounts/templates/      # Auth plugin templates
    ├── auth/                # Authentication views
    └── certification/       # Certification templates
```

---

## Page Models & Templates

| Model | App | Expected Template | Route |
|-------|-----|------------------|-------|
| HomePage | `portfolio.www.pages.home` | `home/home_page.html` | `/` |
| AboutPage | `portfolio.www.pages.about` | `about/about_page.html` | `/about/` |
| ResumePage | `portfolio.www.pages.cv` | `cv/resume_page.html` | `/resume/` |
| ContactPage | `portfolio.www.pages.connect` | `connect/contact_page.html` | `/contact/` |
| PortfolioPage | `portfolio.www.pages.portfolio` | `portfolio/portfolio_page.html` | `/portfolio/` |
| BlogPage | `portfolio.www.pages.blog` | `blog/blog_page.html` | `/blog/` |
| EventPage | `portfolio.www.pages.events` | `events/event_page.html` | `/events/` |

---

## Tab-Based Navigation

Portfolio uses a unique tab-based layout in `base.html`:

- **Tabs**: home, about, resume, portfolio, blog, contact
- **Content**: rendered via `{% block vresume_content %}`
- **Dispatch**: each tab dispatches to its fragment template
- **Legacy slug redirects**: `/home-page/` → `/`, `/about-page/` → `/about/`, `/team-page/` → `/team/`, `/contact-page/` → `/contact/`

---

## Available Shared Components

All shared components from `projects/assets/templates/components/` are available:
chat, cookies, forms, modals, pagination, tables, search, breadcrumbs.

---

## Layout Variants

Use `{% extends "layout/<variant>/skeleton.html" %}`:

| Variant | Purpose |
|---------|---------|
| `layout/apps/` | App-style layout |
| `layout/landing/` | Marketing/landing layout |
| `layout/learning/` | Learning layout |
| `layout/profile/` | User profile layout |
| `layout/auth/` | Authentication layout |

---

## Auth & Accounts

- **Adapter**: `plugins.accounts.adapters.RegistrationAdapter`
- **HTMX fragment rendering** for login/signup modals
- **Social auth adapter**: `AuthHTMXSocialAccountAdapter`
- **URLs**: Account URLs exposed at `/accounts/` (allauth)

---

## Development Commands

```bash
cd projects
make dev WEBSITE=portfolio     # Run dev server
make check WEBSITE=portfolio   # Django system checks
make test WEBSITE=portfolio    # Run tests
make migrate WEBSITE=portfolio # Run migrations
```

---

## Related Docs

| Resource | Path |
|----------|------|
| Project docs | `docs/projects/portfolio/` |
| Shared templates | `projects/assets/templates/AGENTS.md` |
| django-fusion | `libs/django-fusion/AGENTS.md` |
| INFRASTRUCTURE.md | `INFRASTRUCTURE.md` |
