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

---

## Key Imports

```python
# Site routing
from django_fusion.comp.routes import (
    Site, Application, RoutableComponent, FragmentComponent,
    ModelViewset, menu_path, route,
)
# Generic CBVs
from django_fusion.comp.generic import (
    ListModelView, DetailModelView, CreateModelView,
    UpdateModelView, DeleteModelView, TableView,
)
# Core services / handlers
from django_fusion.core.handlers import PageHandler
from django_fusion.core.services import BaseService
from django_fusion.core.models import TimeStampedModel
# Template tag
# {% load components %}
# {% comp "components/..." key=val / %}
```

## Component Conventions

- All template includes use `{% comp "components/..." / %}` — never bare `{% include %}` for static paths
- Fragment identifiers follow dot-notation: `vresume.fragments.<app>.<name>` (e.g., `vresume.fragments.blog.post_preview`)
- HTMX responses set `fragment_name` kwarg on `{% comp %}` to scope the swap target
- Tab-based navigation is driven by `{% block vresume_content %}` — each tab's fragment replaces this block
- For new page models, extend `VResume.www.pages.BasePage` (or the site's existing base) before `Page`

## Step-by-Step Task Guides

**Adding a new VResume page tab:**
1. Create the model in `VResume/www/pages/<tab>/models.py` extending the existing base
2. Add Wagtail panels; run `make -C applications migrate WEBSITE=vresume`
3. Create `VResume/www/pages/<tab>/templates/<tab>/main.html` and `fragment.html`
4. Register the tab in `VResume/www/pages/templates/base.html` tab bar
5. Add the URL in `VResume/www/urls.py` via `menu_path`
6. Add a row to `VResume/AGENTS.md` VResume Page Models & Templates table

**Adding a blog post or portfolio entry:**
1. The `BlogPage` viewset lives in `VResume/www/pages/blog/`
2. Add the entry via Wagtail admin (blog is Wagtail-managed) or via fixture
3. The list template renders with `{% comp "components/pagination/numbers.html" page_obj=page_obj / %}`
4. The detail fragment at `/blog/<slug>/` is a `FragmentComponent` with `fragment_name="vresume.fragments.blog.post_detail"`

**Running VResume-specific checks:**
```bash
make -C applications check WEBSITE=vresume
make -C applications test WEBSITE=vresume
make -C applications/VResume build          # Frontend assets
```

## Site-Specific Deviations from Shared AGENTS.md

- VResume does **not** use Wagtail StreamField body blocks on page models — pages are plain Django models using `FragmentComponent` for HTMX navigation
- There is no `ctc-research`-style plugin for `products` or `lms` in VResume — scope is: home, about, resume/CV, portfolio, blog, contact, events
- `VResume/templates/` is intentionally sparse — prefer shared templates in `assets/templates/` for cross-site components
- Social auth provider is configured via `VResume/plugins/accounts/adapters.py` but MFA (TOTP) UI is not yet present (see `upcoming/blog-projects-app.md`)

## Documentation References

| Topic | File |
|-------|------|
| Page model reference | `applications/VResume/AGENTS.md` (this file) |
| Shared components | `applications/assets/templates/components/AGENTS.md` |
| Component system | `applications/libs/django-fusion/docs/COMPONENT_SYSTEM.md` |
| Component tag API | `applications/libs/django-fusion/docs/COMPONENT_TAG.md` |
| Routing system | `applications/libs/django-fusion/docs/ROUTING_SYSTEM.md` |
| Auth flow | `docs/auth/README.md` |
| VResume site docs | `docs/websites/vresume/index.md` |
| VResume prompts | `applications/VResume/PROMPTS.md` |
| Shared prompts | `/home/structa.cloud/PROMPTS.md` |
