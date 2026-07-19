# VResume — Template Path Tree

Path: `projects/portfolio/`

## Template Resolution Order (Django TEMPLATES_DIRS)

1. `VResume/templates/` — site-specific overrides (highest priority)
2. `VResume/www/pages/<app>/templates/` — app-level page templates
3. `VResume/plugins/<name>/templates/` — plugin templates
4. `assets/templates/` — shared cross-site templates (lowest priority)

## Site Template Tree

```
VResume/templates/
└── (override shelf — add site-specific templates here)
```

## App Page Template Tree

```
VResume/www/pages/
├── templates/               # Root page templates (base.html, skeleton.html)
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

## Plugin Template Tree

```
VResume/plugins/
└── accounts/templates/      # Auth plugin templates
    ├── auth/                # Authentication views
    └── certification/       # Certification templates
```

## VResume Page Models & Templates

| Model | App | Expected Template | Route |
|-------|-----|------------------|-------|
| HomePage | `VResume.www.pages.home` | `home/home_page.html` | `/` |
| AboutPage | `VResume.www.pages.about` | `about/about_page.html` | `/about/` |
| ResumePage | `VResume.www.pages.cv` | `cv/resume_page.html` | `/resume/` |
| ContactPage | `VResume.www.pages.connect` | `connect/contact_page.html` | `/contact/` |
| PortfolioPage | `VResume.www.pages.portfolio` | `portfolio/portfolio_page.html` | `/portfolio/` |
| BlogPage | `VResume.www.pages.blog` | `blog/blog_page.html` | `/blog/` |
| EventPage | `VResume.www.pages.events` | `events/event_page.html` | `/events/` |

## Tab-Based Navigation

VResume uses a unique tab-based layout in `base.html`:
- Tabs: home, about, resume, portfolio, blog, contact
- Content rendered via `{% block vresume_content %}`
- Each tab dispatches to its fragment template
- Legacy slug redirects: `/home-page/` → `/`, `/about-page/` → `/about/`, `/team-page/` → `/team/`, `/contact-page/` → `/contact/`

## Available Shared Components

See `assets/templates/components/AGENTS.md` for the full inventory:
chat, cookies, forms, modals, pagination.

## Layout Variants

Use `{% extends "layout/<variant>/skeleton.html" %}`:
- `layout/apps/` — app-style layout
- `layout/landing/` — marketing/landing layout
- `layout/learning/` — LMS/learning layout
- `layout/profile/` — user profile layout
- `layout/auth/` — authentication layout

## Auth & Accounts
- Adapter: `plugins.accounts.adapters.RegistrationAdapter`
- HTMX fragment rendering for login/signup modals
- Social auth adapter: `AuthHTMXSocialAccountAdapter`
- Account URLs exposed at `/accounts/` (allauth)
