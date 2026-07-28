# LMS Demo — Template Path Tree

Path: `applications/lms-demo/`

## Template Resolution Order (Django TEMPLATES_DIRS)

1. `lms-demo/templates/` — site-specific overrides (highest priority)
2. `lms-demo/plugins/<name>/templates/` — plugin templates
3. `lms-demo/plugins/components/` — site component blocks
4. `assets/templates/` — shared cross-site templates (lowest priority)

## Site Template Tree

```
lms-demo/templates/
├── base_page.html          # Extends shared base.html
├── base_profile.html       # Profile-specific base template
├── base_auth.html          # Auth-specific base template
├── index.html              # Home page template (HTMX dispatcher)
├── home/
│   └── main.html           # Home page sections
│   └── sections/
│       └── clients.html    # Client logos section
├── about/                   # About page templates
├── auth/                    # Authentication templates
├── contact/                 # Contact page templates
├── errors/                  # Custom error pages (404, 500)
├── registration/            # Registration templates
└── services/                # Services page templates
```

## Plugin Template Tree

```
lms-demo/plugins/
├── accounts/templates/      # Auth & certification templates
│   ├── auth/                # Authentication views
│   └── certification/       # Certification templates
├── blog/templates/          # Blog templates
├── lms/templates/           # LMS email and learning templates
│   ├── email/               # LMS email templates
│   └── lms/                 # LMS page templates
├── profile/templates/       # Profile templates
└── components/              # Site-specific UI components
    ├── auth/                # Auth components
    ├── profile/             # Profile partials and settings
    └── blocks/              # Content blocks
```

## Available Shared Components

See `assets/templates/components/AGENTS.md` for the full inventory:
chat, cookies, forms, modals, pagination.

## Layout Variants

Use `{% extends "layout/<variant>/skeleton.html" %}`:
- `layout/apps/` — app-style layout
- `layout/landing/` — marketing/landing layout
- `layout/learning/` — LMS/learning layout
- `layout/profile/` — user profile layout
- `layout/auth/` — authentication layout (via `base_auth.html`)

## Auth & Accounts
- Adapter: `plugins.accounts.adapters.RegistrationAdapter`
- Views: `plugins.accounts.views.allauth` (AllauthLoginView, AllauthSignupView)
- HTMX fragment rendering for login/signup modals
- Social auth adapter: `AuthHTMXSocialAccountAdapter`
- Profile settings include 2FA (TOTP-based via `two_factor_enabled`)
- Templates use `{% comp %}` for component tracking

---

## Key Imports

```python
# Site routing
from django_fusion.comp.routes import (
    Site, Application, RoutableComponent, FragmentComponent,
    ModelViewset, ReadonlyModelViewset, menu_path, route,
)
# Generic CBVs
from django_fusion.comp.generic import (
    ListModelView, DetailModelView, CreateModelView,
    UpdateModelView, DeleteModelView, TableView,
    DeleteBulkActionView, SearchableViewMixin,
)
# Core
from django_fusion.core.handlers import PageHandler
from django_fusion.core.services import BaseService
from django_fusion.core.models import TimeStampedModel
# Auth
from plugins.accounts.adapters import RegistrationAdapter
# Template tag: {% load components %}
```

## Component Conventions

- All static template includes use `{% comp "components/..." / %}` — never bare `{% include %}` for static paths
- Fragment identifiers: `lms.fragments.<app>.<name>` (e.g., `lms.fragments.courses.enrollment_status`)
- HTMX modal login is triggered via `hx-get` and swaps into `#modal-container`
- LMS Demo mirrors the CTC Research LMS plugin structure — `plugins/lms/` is the canonical LMS location for this site
- Profile settings and 2FA are in `plugins/profile/` and `plugins/accounts/`

## Step-by-Step Task Guides

**Adding a new LMS Demo course module:**
1. Add the model to `lms-demo/plugins/lms/models.py`
2. Run migrations: `make -C applications makemigrations WEBSITE=lms-demo && make -C applications migrate WEBSITE=lms-demo`
3. Create the template at `lms-demo/plugins/lms/templates/lms/<module_name>.html`
4. Register the viewset in the lms `Application` in `lms-demo/www/urls.py`
5. Add a `FragmentComponent` for the module detail with `fragment_name="lms.fragments.lms.<module_name>"`

**Adding an LMS Demo blog post:**
1. Blog models live in `lms-demo/plugins/blog/models.py` — add fields there
2. Run migrations under `WEBSITE=lms-demo`
3. Blog templates at `lms-demo/plugins/blog/templates/blog/`
4. The blog list renders via `{% comp "components/pagination/numbers.html" page_obj=page_obj / %}`

**Customising the LMS Demo home page sections:**
1. Home page sections are in `lms-demo/templates/home/`
2. Each section uses `{% comp "components/blocks/..." / %}` from shared or site-specific blocks
3. Site-specific block overrides go in `lms-demo/plugins/components/`
4. To add a new section: create a template, add it to `home/main.html`, pass required context from the home view

**Running LMS Demo checks:**
```bash
make -C applications check WEBSITE=lms-demo
make -C applications test WEBSITE=lms-demo
make -C applications lint
```

## Site-Specific Deviations from Shared AGENTS.md

- LMS Demo is the Structa/LMS marketing and demo site — it has both a public marketing layer (landing, about, contact) and a gated LMS layer (courses, learning, profile)
- The LMS plugin here mirrors `ctc-research/plugins/lms/` — keep them in sync or extract to a shared lib if they diverge significantly
- WebSocket support is present (`lms-demo/www/websocket.py`) — do not remove it; it enables real-time learning progress events
- Profile settings include 2FA, certification, and learning progress — all managed via `plugins/profile/`
- No Wagtail CMS on top-level pages — pages are class-based `RoutableComponent` views, not Wagtail Page tree items

## Documentation References

| Topic | File |
|-------|------|
| Shared AGENTS | `/home/structa.cloud/AGENTS.md` |
| Shared component inventory | `applications/assets/templates/components/AGENTS.md` |
| Component system | `applications/libs/django-fusion/docs/COMPONENT_SYSTEM.md` |
| Component tag API | `applications/libs/django-fusion/docs/COMPONENT_TAG.md` |
| Routing system | `applications/libs/django-fusion/docs/ROUTING_SYSTEM.md` |
| Viewflow mapping | `applications/libs/django-fusion/docs/VIEWFLOW_MAPPING.md` |
| Auth flow | `docs/auth/README.md` |
| LMS Demo site docs | `docs/websites/lms-demo/index.md` |
| LMS Demo prompts | `applications/lms-demo/PROMPTS.md` |
| Shared prompts | `/home/structa.cloud/PROMPTS.md` |
