# VResume — Template Path Tree

Path: `applications/VResume/`

## Template Resolution Order (Django TEMPLATES_DIRS)

1. `VResume/templates/` — site-specific overrides (highest priority)
2. `VResume/www/pages/<app>/templates/` — app-level page templates
3. `VResume/plugins/<name>/templates/` — plugin templates
4. `assets/templates/` — shared cross-site templates (lowest priority)

## Site Template Tree

```
VResume/templates/
└── (created as override shelf — add site-specific templates here)
```

## App Page Template Tree

```
VResume/www/pages/
├── templates/               # Root page templates
├── connect/templates/       # Contact page templates
├── home/                    # HomePage: models, migrations
├── about/                   # AboutPage: models, viewsets
├── cv/                      # ResumePage: models
├── events/                  # EventPage: models
├── blog/                    # BlogPage: models, viewsets, services
├── portfolio/               # PortfolioPage: models
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

| Model | App | Expected Template |
|-------|-----|------------------|
| HomePage | `VResume.www.pages.home` | `home/home_page.html` |
| AboutPage | `VResume.www.pages.about` | `about/about_page.html` |
| ResumePage | `VResume.www.pages.cv` | `cv/resume_page.html` |
| ContactPage | `VResume.www.pages.connect` | `connect/contact_page.html` |
| PortfolioPage | `VResume.www.pages.portfolio` | `portfolio/portfolio_page.html` |
| BlogPage | `VResume.www.pages.blog` | `blog/blog_page.html` |

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
