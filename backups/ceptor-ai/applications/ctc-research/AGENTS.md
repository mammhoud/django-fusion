# CTC Research — Template Path Tree

Path: `applications/ctc-research/`

## Template Resolution Order (Django TEMPLATES_DIRS)

1. `ctc-research/templates/` — site-specific overrides (highest priority)
2. `ctc-research/plugins/<name>/templates/` — plugin templates
3. `ctc-research/plugins/components/` — site component blocks
4. `assets/templates/` — shared cross-site templates (lowest priority)

## Site Template Tree

```
ctc-research/templates/
├── base_page.html          # Extends shared base.html
├── base_auth.html          # Auth layout wrapper
├── base_profile.html       # Profile layout wrapper
├── index.html              # Home page template (HTMX dispatcher)
├── home/
│   └── main.html           # Home page sections
│   └── sections/
│       └── clients.html    # Client logos section
├── about/                   # About page templates
├── contact/                 # Contact page templates
├── registration/            # Registration/signup templates
└── services/                # Services page templates
```

## Plugin Template Tree

```
ctc-research/plugins/
├── accounts/templates/      # Auth templates (extends base_auth.html)
│   ├── account/             # allauth overrides: login, signup, password_reset, etc.
│   ├── email/               # Email confirmation templates
│   ├── learning/            # Learning platform templates
│   ├── lms/                 # LMS blocks and fragments
│   ├── profile/             # User profile: forms, modals, partials, sections, settings
│   └── socialaccount/       # Social auth (Google, GitHub, etc.)
├── blog/templates/          # Blog templates
├── lms/templates/           # LMS-specific templates
├── profile/templates/       # Profile templates
└── components/              # Site-specific UI components
    ├── blocks/              # Content blocks
    ├── common/              # Shared partials and modals
    └── contact/             # Contact form components
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
from django_fusion.core.cache import CacheService
# Auth
from django_fusion.site import PageHandler
from plugins.accounts.adapters import RegistrationAdapter
# Template tag: {% load components %}
```

## Component Conventions

- Use `{% comp "components/blocks/<name>/<name>.html" / %}` for all block components — no bare `{% include %}` for static paths
- Fragment identifiers follow dot-notation: `ctc.fragments.<app>.<name>` (e.g., `ctc.fragments.blog.post_list`)
- HTMX modal login/signup is triggered via `hx-get` against the auth fragment URL and swaps into `#modal-container`
- CTC Research uses the LMS plugin — LMS-specific fragments use `ctc.fragments.lms.<name>`
- Site-specific component overrides go in `plugins/components/` — never in `assets/templates/components/` unless cross-site

## Step-by-Step Task Guides

**Adding a new CTC blog post type (custom Post model field):**
1. Add the field to `ctc-research/www/apps/blog/models.py` (or the plugin model under `plugins/blog/`)
2. Add the `FieldPanel` to `content_panels`
3. Run `make -C applications makemigrations WEBSITE=ctc-research && make -C applications migrate WEBSITE=ctc-research`
4. Update the blog list template: `ctc-research/plugins/blog/templates/blog/` — use `{% comp "components/..." / %}` for shared layout
5. Update `ctc-research/AGENTS.md` Plugin Template Tree if a new template directory is created

**Adding a new LMS course section (CTC Research):**
1. CTC-Research LMS models live under `plugins/lms/` — add the new model there
2. Migrations run under `WEBSITE=ctc-research`
3. LMS templates: `ctc-research/plugins/lms/templates/lms/`
4. LMS fragments use `fragment_name="ctc.fragments.lms.<name>"`
5. Register the new viewset in the lms Application in `ctc-research/www/urls.py`

**Adding a site-specific component block:**
1. Create `ctc-research/plugins/components/blocks/<name>.html`
2. The file is auto-registered because `COMPONENTS_INCLUDE_PATH_ROOTS` includes `plugins/components/`
3. Use `{% comp "blocks/<name>.html" / %}` — uses component namespace, not full path
4. If the component will be reused across sites, move it to `assets/templates/components/blocks/` instead

**Running CTC Research checks:**
```bash
make -C applications check WEBSITE=ctc-research
make -C applications test WEBSITE=ctc-research
make -C applications lint
```

## Site-Specific Deviations from Shared AGENTS.md

- CTC Research is the primary LMS site — `plugins/lms/` is the canonical LMS plugin location; `lms-demo` mirrors it
- Profile settings (2FA TOTP) are fully implemented in `plugins/profile/` — see `plugins/accounts/adapters.py` for the `two_factor_enabled` check
- Social auth supports Google and GitHub — adapters in `plugins/accounts/adapters.py`
- `plugins/components/` hosts CTC-specific component blocks (`blocks/`, `common/`, `contact/`) — these take priority over `assets/templates/components/` for CTC-scoped renders
- Auth email templates are managed as Wagtail snippets via `AuthEmailTemplate` — do not add raw email template files without a corresponding snippet

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
| CTC Research site docs | `docs/websites/ctc-research/index.md` |
| CTC Research prompts | `applications/ctc-research/PROMPTS.md` |
| Shared prompts | `/home/structa.cloud/PROMPTS.md` |
