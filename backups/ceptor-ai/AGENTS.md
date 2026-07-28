# Structa Cloud – AI Agent Instructions

## Project Overview
Structa Cloud is a Django monorepo under `applications/`, with multiple site projects, shared configuration, shared frontend assets, and local reusable Django libraries. Do not assume this repo uses a generic `projects/customizer/design/components` app layout.

## Actual Monorepo Layout
- `applications/Makefile` is the primary Makefile for application, Django, asset, test, and site orchestration targets.
- `applications/configs/` contains shared Django configuration and settings used across sites.
- `applications/assets/` contains shared frontend assets, shared templates, static files, locale files, and asset scripts.
- `applications/libs/` contains local reusable libraries that are developed alongside the sites.
- `applications/scripts/`, `applications/tasks/`, and `applications/webpack/` contain shared automation, task, and build tooling.
- `applications/www/` contains shared/core Django code used by the application stack.

## Canonical Site Paths
Use these canonical paths when working on site-specific code:
- `applications/ctc-research/` — CTC Research site.
- `applications/lms-demo/` — Structa/LMS demo site.
- `applications/VResume/` — VResume site. Note the directory is capitalized, even though some Makefile aliases use `vresume`.

Each site can contain its own `assets/`, `plugins/`, `templates/`, `tests/`, `www/`, and site-level `Makefile` as applicable.

## Shared Settings
Shared settings live under `applications/configs/`:
- `applications/configs/base/` for base configuration modules.
- `applications/configs/settings/` for environment/site settings.
- `applications/configs/tests/` for test settings and test configuration helpers.

Prefer adding common settings in `applications/configs/` rather than duplicating them inside individual sites. Keep site-specific overrides in the relevant site path.

## Shared Frontend Assets
Shared frontend assets live under `applications/assets/`:
- `applications/assets/templates/` for templates shared across sites.
- `applications/assets/static/` for shared static files.
- `applications/assets/scripts/` for shared frontend/build scripts.
- `applications/assets/locale/` for shared localization assets.

When adding shared styles, scripts, images, or templates, place them in `applications/assets/` unless they are truly site-specific.

## Local Libraries
Local reusable libraries live under `applications/libs/`. These are the two active packages:

| Package | Path | Import Name | Absorbed From |
|---------|------|-------------|---------------|
| **django-fusion** | `applications/libs/django-fusion/` | `django_fusion` | django-grep, django-osoul, django-rseal |
| **ceptor-ai** | `applications/libs/ceptor-ai/` | `ceptor_ai` | — (standalone) |

### Merge History

The following packages were consolidated into `django-fusion` to reduce maintenance overhead:

| Original Package | Merged Into | Legacy Docs Location | What Was Absorbed |
|-----------------|-------------|---------------------|-------------------|
| **django-grep** | `django_fusion` | `applications/libs/django-fusion/docs/legacy-django-grep/` | Testing framework, property-based testing, management commands (`django_fusion.infrastructure.management.base`), validators (`django_fusion.core.utils.security.validators`) |
| **django-osoul** | `django_fusion` | `applications/libs/django-fusion/docs/legacy-django-osoul/` | Base models, handlers, auth backends, template tags (`django_fusion.infrastructure.templatetags.django_osoul_tags`) |
| **django-rseal** | `django_fusion` | (absorbed into projects/web modules) | Web views, rendering, view mixins — now in `django_fusion.web` |

Treat these as first-class local packages. Make reusable framework-level changes in the appropriate library instead of copying logic into site projects.

## Makefile Delegation
- The root `Makefile` should be a thin entrypoint that delegates application and site work to `applications/Makefile`.
- `applications/Makefile` is the canonical dispatcher for Django checks, tests, migrations, asset builds, Docker/site commands, and `WEBSITE=...` selection.
- Site Makefiles live in each `applications/<site>/` directory, for example:
  - `applications/ctc-research/Makefile`
  - `applications/lms-demo/Makefile`
  - `applications/VResume/Makefile`
- Prefer invoking site work through `applications/Makefile` unless a site Makefile target is explicitly needed.
- Preserve existing website aliases in `applications/Makefile`; do not invent new canonical site names without updating the dispatcher.

## Template Conventions
- Component template categories should not repeat the same folder name twice; for example, use `components/blocks/contact/contact_profile.html` instead of `components/blocks/contact/contact/contact_profile.html`.
Template locations are intentionally layered. Check all relevant paths before adding or moving templates:
- Shared templates: `applications/assets/templates/`.
- Site root templates: `applications/<site>/templates/`.
- Site asset templates: `applications/<site>/assets/templates/`.
- Site Django app templates: `applications/<site>/www/**/templates/`.
- Plugin templates: any template paths under `applications/<site>/plugins/`, including plugin-level `templates/` directories.

Use `{% include %}` for reusable components and pass only the required context. Prefer shared templates for cross-site UI and site templates for site-specific presentation.

## Fragment Naming Convention
Use `fragment_name` only for fragment identifiers and context keys. Do not introduce alternate names such as `fragment`, `name`, `fragment_slug`, or `fragment_key` for the same concept unless maintaining backwards compatibility with existing code.

## Code Style & Standards
- **Python**: Follow PEP 8. Use type hints for new or modified functions where practical. Keep formatting compatible with Black's 88-character default.
- **Django**: Prefer class-based views where appropriate. Keep business logic out of views and in services/modules that match the existing local structure.
- **Wagtail/Django templates**: Follow the existing panel, model, and template patterns in the relevant site or library.
- **SCSS/CSS**: Follow existing project conventions and use BEM-style names for reusable component classes. Do not use IDs for styling.
- **Imports**: Never wrap imports in `try`/`except` blocks.

## Testing & Validation
- Use `rg` instead of recursive `grep` for code searches.
- Run the narrowest relevant checks first, then broader tests when practical.
- For Django site work, prefer commands delegated through `applications/Makefile` with the appropriate `WEBSITE=...` value.
- For shared library work, run tests or checks that cover both the library and affected sites when practical.

## Infrastructure & Proxy
- Traefik proxy (`default-proxy`) serves SSL on port 443. Certs are obtained via Let's Encrypt DNS-01 (Cloudflare) using Traefik's native `certificatesResolvers` block in `proxy/traefik/dynamic.yml`.
- Nginx media server (`shared-media`) serves static/media files for all sites.
- ACME store lives at `proxy/acme/acme.json` (mode 0600), bind-mounted into the proxy at `/etc/traefik/acme/`. The directory is git-tracked (via `.gitkeep`); `acme.json` is gitignored.
- Cloudflare credentials are read from env vars on the proxy container (`CF_DNS_API_TOKEN` recommended, or `CF_API_EMAIL` + `CF_API_KEY`). Local values come from `proxy/.env` (gitignored; copy from `proxy/.env.example`).
- HTTPS routers opt into LE via `tls: { certResolver: letsencrypt }` in the per-site router file. The catchall router intentionally has no certResolver — Traefik falls back to its internal default cert for unmatched hosts.
- The rollout is staged (see `proxy/LETSENCRYPT.md`): Stage 1 enables LE for `vresume.structa.cloud` on the Let's Encrypt **staging** CA; Stage 2 flips to the production CA and enables LE for ctc-research / structa-cloud / media / dashboard; Stage 3 deletes `proxy/traefik/dynamic/certs.yml`.
- `proxy/traefik/dynamic/certs.yml` (static self-signed certs) is kept as a fallback until Stage 3. Until it's deleted, removing `certResolver` from a router causes it to fall back to the SAN-matched self-signed cert.
- `proxy/scripts/manage-certs.sh` now provides `bootstrap-acme`, `status`, and `check-expiry` for the LE flow; the self-signed commands are retained as a legacy fallback.
- Health checks on backend services must include the correct `Host` header (set via `hostname` in Traefik healthCheck config).
- Media subdomains: `media.structa.cloud`, `media.ctc-research.com`, `media.lms-demo.com`, `media.vresume.structa.cloud`.
- Legacy self-signed certs remain in `proxy/certs/` for rollback purposes; they are no longer the source of truth.

## Authentication & Authorization
- All sites use `django-allauth` for authentication with `django-fusion` auth mixins.
- Auth views extend `PageHandler` from `django_fusion.site`.
- HTMX is used for modal-based login/register flows.
- Social auth adapters live in site `plugins/accounts/adapters.py`.
- MFA support: custom TOTP-based 2FA in profile settings (via `two_factor_enabled` / `two_factor_secret` on profile model).
- `allauth.mfa` is available as optional dependency for WebAuthn/passkey support.
- Auth email templates are managed as Wagtail snippets via `AuthEmailTemplate`.
- Account adapter: `plugins.accounts.adapters.RegistrationAdapter` (HTMX-aware, fragment rendering).
- Supported auth flows: login, signup, password reset, password change, email management, social signup, social connections.

## Component System (django-fusion)
- Use `{% comp "name" %}` for ALL rendered components from `django_fusion.comp`. This is the single canonical tag — both registered components (slots/props) and plain include-style template paths are dispatched through the same `{% comp %}` tag.
- Reserved `{% comp %}` kwargs: use `fragment_name` for the fragment identifier. The legacy synonyms `fragment`, `fragment_slug`, `fragment_key` are rejected with `TemplateSyntaxError`.
- Use `{% include "path" %}` ONLY for truly dynamic template names (e.g., `{% include template_name %}`) where the path is a runtime variable. Static literal includes should be expressed as `{% comp "path" / %}`.
- The `IncludePathComponent` class (in `django_fusion.comp.registry`) maps plain template paths to component names verbatim. `CoreExtAppConfig.ready()` calls `register_default_partials()` which globs every `*.html` under `COMPONENTS_INCLUDE_PATH_ROOTS` (`partials/`, `components/`) and pre-registers them as components — so `{% comp "components/table.html" / %}` Just Works at startup.
- Component template directories: `components/blocks/`, `components/partials/`, `tags/`.
- Component namespaces use dot notation: `{% comp "contact.sections.form" block=block / %}`.

## django-fusion Canonical Import Paths

All re-export shims have been removed. Use these canonical paths directly.

### Routing (`comp.routes`)

```python
from django_fusion.comp.routes import (
    # Base routing
    Viewset, BaseViewset, ViewsetMeta, Route, route, menu_path, IndexViewMixin,
    # Descriptor
    viewprop,
    # Model viewsets
    BaseModelViewset, ModelViewset, ReadonlyModelViewset,
    ListBulkActionsMixin, CreateViewMixin, UpdateViewMixin, DeleteViewMixin, DetailViewMixin,
    # Site/Application
    Application, AppMenuMixin, Site,
    # Routable components
    RoutableComponent, FragmentComponent,
    # Fragment detection
    FragmentDetector, FragmentDetectionMixin,
)
```

### Generic CBVs (`comp.generic`)

```python
from django_fusion.comp.generic import (
    Action, CreateModelView, DeleteBulkActionView, DeleteModelView,
    DetailModelView, ListModelView, UpdateModelView,
    BaseListModelView, BaseBulkActionView, SearchableViewMixin, TableView,
)
```

### Other canonical paths

| Module | Canonical Path |
|--------|---------------|
| Handlers | `django_fusion.core.handlers` |
| Managers | `django_fusion.core.managers` |
| Models | `django_fusion.core.models` |
| Services | `django_fusion.core.services` |
| Views (FilterMixin, SearchMixin) | `django_fusion.web.views` |
| Loaders | `django_fusion.comp.loaders` |
| Middlewares | `django_fusion.core.middlewares` |
| Cache | `django_fusion.core.cache` |

## Media & Static Files
- Shared static files: `applications/assets/static/`.
- Site-specific staticfiles: `applications/<site>/assets/staticfiles/`.
- Site-specific media: `applications/<site>/assets/media/`.
- Nginx mounts each site's staticfiles under `/var/www/sites/<site>/static/`.
- Traefik routes `PathPrefix(/static/)` and `PathPrefix(/media/)` to `shared-media:80`.

## Step-by-Step Task Guides

### Adding a new shared template component

1. Pick a name under `applications/assets/templates/components/` using the existing subdirectory convention (`blocks/`, `forms/`, `modals/`, etc.)
2. Create the `.html` file with BEM class names; declare `{% load components %}` at the top
3. Accept context only via named kwargs in `{% comp "…" key=val / %}` — no globals assumed
4. Register it automatically (no manual step needed — `register_default_partials()` picks up `components/**/*.html` at startup)
5. Document the component in `applications/assets/templates/components/AGENTS.md` under the correct inventory table row (Template, Usage, required context vars)
6. Run: `make -C applications check WEBSITE=ctc-research` to verify no import or template errors

### Adding a new django-fusion Model Viewset

1. Import from the canonical path: `from django_fusion.comp.routes import ModelViewset`
2. Create the viewset class with `model`, `paginate_by`, and `template_name` class attributes
3. Add to an `Application` in the site's `www/urls.py` (or equivalent `site.py`)
4. Create templates under `<site>/www/<app>/templates/<model_name>_list.html`, `_detail.html`, `_form.html`
5. Use `{% comp "components/table.html" / %}` inside list templates — do not duplicate table HTML
6. Run: `make -C applications check WEBSITE=<site>` then `make -C applications test WEBSITE=<site>`

### Adding a new site page (Wagtail Page model)

1. Add the model in `<site>/www/<app>/models.py` extending `Page` or an existing base
2. Add Wagtail panels and `content_panels` list
3. Create the template at `<site>/www/<app>/templates/<app>/<model_slug>.html` extending the site base
4. Register in `INSTALLED_APPS` via the app's `AppConfig` (already done if app exists)
5. Run migrations: `make -C applications migrate WEBSITE=<site>`
6. Create a fixture or use Wagtail admin to attach the page to the tree

### Adding a shared config module

1. Create the module in `applications/configs/base/<name>.py`
2. Import it from `applications/configs/settings/conf.py` or from each site's `settings.py` as needed
3. Never duplicate a setting across sites — one canonical location in `configs/base/`
4. Run: `make -C applications check WEBSITE=ctc-research`, `make -C applications check WEBSITE=lms-demo`, and `make -C applications check WEBSITE=vresume` across all three sites to verify

### Running lint and type checks

```bash
# Ruff lint (all applications)
make -C applications lint
# Type check a specific site
make -C applications typecheck WEBSITE=ctc-research
# Run tests for a site
make -C applications test WEBSITE=lms-demo
# Check markdown links in docs/
python3 applications/scripts/check_markdown_links.py --scope docs/
# Preview docs locally
make docs-serve
```

---

## Documentation References

| Topic | File | Description |
|-------|------|-------------|
| Component system | `applications/libs/django-fusion/docs/COMPONENT_SYSTEM.md` | `RoutableComponent`, `FragmentComponent`, mixins, lifecycle |
| Routing system | `applications/libs/django-fusion/docs/ROUTING_SYSTEM.md` | `route_path`, URL namespaces, reversal |
| Forms & tables | `applications/libs/django-fusion/docs/FORMS_TABLES_INTEGRATION.md` | Form rendering, `TableView`, bulk actions |
| Architecture overview | `applications/libs/django-fusion/docs/ARCHITECTURE_OVERVIEW.md` | Full system diagram |
| Shared components | `applications/assets/templates/components/AGENTS.md` | Component inventory (chat, forms, modals, pagination) |
| Template resolution | `applications/VResume/AGENTS.md` | VResume template order and page models |
| Shared templates AGENTS | `applications/assets/templates/AGENTS.md` | Cross-site template rules |
| Infrastructure | `docs/infrastructure/INFRASTRUCTURE_GUIDE.md` | Traefik, Nginx, SSL, Docker layout |
| Deployment | `docs/deployment/index.md` | Deploy commands, env vars, checklists |
| Changelog | `docs/changelog/index.md` | Per-version history and release notes |
| Docs Overview | `docs/reference/docs_overview.md` | Docsify site structure and conventions |
| Docsify site | `docs/index.html` | Local preview: `make docs-serve` → http://localhost:3000 |
| Component tag API | `applications/libs/django-fusion/docs/COMPONENT_TAG.md` | Props, slots, vars, attrs with bird/cotton comparison |
| Viewflow mapping | `applications/libs/django-fusion/docs/VIEWFLOW_MAPPING.md` | django-material → django-fusion URL pattern mapping |
| Health module | `applications/libs/django-fusion/docs/HEALTH.md` | HealthCheckView, DatabaseHealthView, AssetsHealthView |
| Wagtail integration | `applications/libs/django-fusion/docs/WAGTAIL_INTEGRATION.md` | StreamField blocks, AuthEmailTemplate, viewsets |
| Site layer | `applications/libs/django-fusion/docs/SITE_LAYER.md` | PageHandler, auth mixins, paginators, plugins |
| Contrib module | `applications/libs/django-fusion/docs/CONTRIB.md` | admin, cache, debug_tools, enums, privacy, utils |
| Infrastructure module | `applications/libs/django-fusion/docs/INFRASTRUCTURE_MODULE.md` | Management commands, scripts, templatetags, locale |
| django-grep docs | `applications/libs/django-fusion/docs/legacy-django-grep/index.md` | django-grep legacy docs (merged into django-fusion) |
| django-rseal docs | (absorbed into `django_fusion.web`) | django-rseal merged into django-fusion web module |
| CTC Research site | `docs/websites/ctc-research/index.md` | CTC site architecture and docs |
| LMS Demo site | `docs/websites/lms-demo/index.md` | LMS Demo site architecture and docs |
| VResume site | `docs/websites/vresume/index.md` | VResume site architecture and docs |

---

## `{% comp %}` Component Tag — Props, Slots, Vars & Attrs

The `{% comp %}` tag is the single canonical way to render components in django-fusion. It
implements a props + slots model comparable to django-bird and django-cotton, using pure Django
template syntax.

### Quick Comparison

| Feature | django-bird | django-cotton | django-fusion `{% comp %}` |
|---------|-------------|---------------|---------------------------|
| Props declaration | `{{ props.title }}` | `<c-vars title />` | `{% prop title %}` |
| Default slot | Content between tags | Content between tags | `{% slot %}{{ slot }}{% endslot %}` |
| Named slots | `{% bird:slot header %}` | `<c-slot name="header" />` | `{% slot header %}...{% endslot %}` |
| Attrs passthrough | `{{ attrs }}` | `{{ attrs }}` | `{{ attrs }}` |
| Self-closing | `{% bird "name" / %}` | `<c-name />` | `{% comp "name" / %}` |
| Fragment ID | N/A | N/A | `fragment_name="site.fragments.app.name"` |
| Vars (local state) | N/A | N/A | `{% var key="value" %}` |

### Component Authoring Patterns

**Props:** Declare at top of template with `{% prop %}`:
```django
{% load components %}
{% prop title %}                  {# required — no default #}
{% prop summary="" %}             {# optional with default #}
{% prop show_author=True %}       {# boolean default #}
```
Props are accessed via `{{ props.<name> }}` in the template.

**Default slot:** Content between `{% comp %}...{% endcomp %}` is the default slot:
```django
{% comp "components/cards/card.html" title="Hello" %}
  <p>Slot content here</p>
{% endcomp %}
```

**Named slots:** Inject content into named regions:
```django
{% comp "components/layouts/page.html" %}
  {% slot sidebar %}<nav>...</nav>{% endslot %}
  {% slot header %}<h1>Title</h1>{% endslot %}
  <p>Main content (default slot)</p>
{% endcomp %}
```

**Attrs:** Extra kwargs become HTML attributes via `{{ attrs }}`:
```django
{% comp "components/button.html" label="Save" class="btn--primary" / %}
{# Button template receives `class="btn--primary"` via `{{ attrs }}` #}
```

**Vars (local state):** Mutable scope for accumulators and toggles:
```django
{% var counter=0 %}
{% for item in items %}
  {% var counter+=1 %}
  <li>{{ vars.counter }}. {{ item }}</li>
{% endfor %}
```

**Self-closing:** Use `{% comp "name" / %}` when no slots are needed:
```django
{% comp "components/icons/star.html" filled=True / %}
```

**Fragment name** (django-fusion specific): Scopes HTMX swap targets:
```django
{% comp "fragments/post.html" post=post fragment_name="blog.fragments.post_detail" / %}
```

See [COMPONENT_TAG.md](applications/libs/django-fusion/docs/COMPONENT_TAG.md) for the full reference.
See [VIEWFLOW_MAPPING.md](applications/libs/django-fusion/docs/VIEWFLOW_MAPPING.md) for django-material → django-fusion mapping.

---

## CRUD Sample: Adding a Field to a Model (End-to-End)

This sample covers the complete lifecycle of adding a field: model → panel → migration → template → check.

### CTC Research — Adding `featured` to Blog Post (Wagtail Page)

```python
# 1. Add field to ctc-research/plugins/blog/models.py
from wagtail.admin.panels import FieldPanel

class Post(Page):
    featured = models.BooleanField(default=False, verbose_name="Featured Post")

    content_panels = Page.content_panels + [
        FieldPanel("featured"),
    ]
```
```bash
# 2. Migrate
make -C applications makemigrations WEBSITE=ctc-research
make -C applications migrate WEBSITE=ctc-research
```
```html
{# 3. Update template: ctc-research/plugins/blog/templates/blog/post_list.html #}
{% if post.featured %}
  <span class="post-card__badge post-card__badge--featured">Featured</span>
{% endif %}
```
```bash
# 4. Verify
make -C applications check WEBSITE=ctc-research
```

### LMS Demo — Adding `difficulty_level` to Course (Django Model)

```python
# 1. Add field to lms-demo/plugins/lms/models.py
class Course(models.Model):
    DIFFICULTY_CHOICES = [
        ("beginner", "Beginner"), ("intermediate", "Intermediate"), ("advanced", "Advanced"),
    ]
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default="beginner")
```
```bash
# 2. Migrate
make -C applications makemigrations WEBSITE=lms-demo
make -C applications migrate WEBSITE=lms-demo
```
```html
{# 3. Template: lms-demo/plugins/lms/templates/lms/course_detail.html #}
<span class="badge badge--{{ course.difficulty_level }}">
  {{ course.get_difficulty_level_display }}
</span>
```
```bash
# 4. Verify
make -C applications check WEBSITE=lms-demo
```

### VResume — Adding `live_url` to PortfolioPage

```python
# 1. Add field to VResume/www/pages/portfolio/models.py
class PortfolioPage(Page):
    live_url = models.URLField(blank=True, verbose_name="Live project URL")
    content_panels = Page.content_panels + [FieldPanel("live_url")]
```
```bash
# 2. Migrate
make -C applications makemigrations WEBSITE=vresume
make -C applications migrate WEBSITE=vresume
```
```html
{# 3. Template: VResume/www/pages/portfolio/templates/portfolio/main.html #}
{% if page.live_url %}
<a class="portfolio-card__link" href="{{ page.live_url }}" target="_blank">View Live ↗</a>
{% endif %}
```
```bash
# 4. Verify
make -C applications check WEBSITE=vresume
```

---

## CRUD Sample: Creating a New Model and Wiring the Viewset

Complete end-to-end: Model → Migration → Viewset → Application → Template → URL.

```python
# 1. Model — applications/<site>/www/apps/<app>/models.py
from django.db import models

class Event(models.Model):
    title = models.CharField(max_length=200)
    date = models.DateTimeField()
    location = models.CharField(max_length=300)
    is_published = models.BooleanField(default=False)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return self.title
```
```bash
# 2. Migrate
make -C applications makemigrations WEBSITE=lms-demo
make -C applications migrate WEBSITE=lms-demo
```
```python
# 3. Viewset — applications/<site>/www/apps/<app>/viewsets.py
from django_fusion.comp.routes import ModelViewset
from .models import Event

class EventViewset(ModelViewset):
    model = Event
    paginate_by = 20
    template_name = "events/event"  # resolves _list, _detail, _form

    def get_queryset(self):
        qs = super().get_queryset()
        if search := self.request.GET.get("q"):
            qs = qs.filter(title__icontains=search)
        return qs.filter(is_published=True)
```
```python
# 4. Register in Application — site/www/urls.py
from django_fusion.comp.routes import Application
from .events.viewsets import EventViewset

events_app = Application(
    title="Events",
    app_name="events",
    viewsets=[EventViewset],
)
# Add events_app to the Site applications list
```
```html
{# 5. Templates — <app>/templates/<app>/ #}
{# event_list.html #}
{% extends "base_page.html" %}
{% block content %}
  <h1>Events</h1>
  {% for event in object_list %}
    {% comp "components/cards/event_card.html" title=event.title date=event.date / %}
  {% endfor %}
  {% comp "components/pagination/numbers.html" page_obj=page_obj / %}
{% endblock %}

{# event_detail.html #}
{% extends "base_page.html" %}
{% block content %}
  <h1>{{ object.title }}</h1>
  <p>{{ object.date }} — {{ object.location }}</p>
{% endblock %}

{# event_form.html #}
{% extends "base_page.html" %}
{% block content %}
  <form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Save</button>
  </form>
{% endblock %}
```
```bash
# 6. Verify URLs are registered and accessible
make -C applications check WEBSITE=lms-demo
# Browsable at: /events/, /events/<pk>/, /events/create/, /events/<pk>/update/
```

---

## Project Structure Tree

```
structa.cloud/
├── applications/              # Django monorepo
│   ├── Makefile              # master dispatcher for Django work
│   ├── configs/              # shared Django configuration
│   │   ├── base/             # base settings modules
│   │   ├── settings/         # environment/site settings
│   │   └── tests/            # test configuration
│   ├── assets/               # shared frontend assets & templates
│   │   ├── templates/        # shared templates
│   │   ├── static/           # shared static files
│   │   ├── scripts/          # frontend build scripts
│   │   └── locale/           # shared translations
│   ├── libs/                 # local reusable libraries
│   │   ├── django-fusion/    # component system + framework tools
│   │   └── ceptor-ai/        # AI/ML integration library
│   ├── scripts/              # shared automation scripts
│   ├── tasks/                # shared Celery/task code
│   ├── www/                  # shared Django application code
│   ├── ctc-research/         # CTC Research site
│   ├── lms-demo/             # LMS Demo site
│   ├── VResume/              # VResume site
│   └── crm/                  # CRM site
├── proxy/                    # Traefik reverse proxy + SSL
├── databases/                # PostgreSQL + Redis
├── services/                 # supporting services (media, monitoring)
├── compose/                  # central orchestration compose files
├── docs/                     # documentation (Docsify site)
├── docker-compose.yml        # root orchestrator
├── Makefile                  # root deployment dispatcher
├── AGENTS.md                 # this file
└── PROMPTS.md                # AI prompt catalog

Root-level `.md` files are limited to `README.md`, `AGENTS.md`, and `PROMPTS.md`. All other documentation lives under `docs/` in the unified structure described below.
```

---

## Site AGENTS.md and PROMPTS.md Cross-Reference

| Site | AGENTS.md | PROMPTS.md | Docs Path |
|------|-----------|------------|-----------|
| CTC Research | `applications/ctc-research/AGENTS.md` | `applications/ctc-research/PROMPTS.md` | `docs/websites/ctc-research/index.md` |
| LMS Demo | `applications/lms-demo/AGENTS.md` | `applications/lms-demo/PROMPTS.md` | `docs/websites/lms-demo/index.md` |
| VResume | `applications/VResume/AGENTS.md` | `applications/VResume/PROMPTS.md` | `docs/websites/vresume/index.md` |
| Shared (root) | `/home/structa.cloud/AGENTS.md` | `/home/structa.cloud/PROMPTS.md` | `docs/README.md` |

Each site-level AGENTS.md contains:
- Template resolution order (Django TEMPLATES_DIRS)
- Site template tree and plugin template tree
- Page models & templates table
- Key imports for that site
- Component conventions and fragment naming
- Site-specific deviations from the shared AGENTS.md
- Step-by-step task guides
- Documentation references

---

## Library Documentation Map

| Library | Path | Key Docs |
|---------|------|----------|
| django-fusion | `applications/libs/django-fusion/` | [COMPONENT_SYSTEM.md](applications/libs/django-fusion/docs/COMPONENT_SYSTEM.md), [ROUTING_SYSTEM.md](applications/libs/django-fusion/docs/ROUTING_SYSTEM.md), [COMPONENT_TAG.md](applications/libs/django-fusion/docs/COMPONENT_TAG.md), [VIEWFLOW_MAPPING.md](applications/libs/django-fusion/docs/VIEWFLOW_MAPPING.md), [FORMS_TABLES_INTEGRATION.md](applications/libs/django-fusion/docs/FORMS_TABLES_INTEGRATION.md), [ARCHITECTURE_OVERVIEW.md](applications/libs/django-fusion/docs/ARCHITECTURE_OVERVIEW.md) |
| django-grep (merged) | → `django_fusion` | [legacy-django-grep/index.md](applications/libs/django-fusion/docs/legacy-django-grep/index.md), [usage.md](applications/libs/django-fusion/docs/legacy-django-grep/usage.md) |
| django-osoul (merged) | → `django_fusion` | [legacy-django-osoul/README.md](applications/libs/django-fusion/docs/legacy-django-osoul/README.md) |
| django-rseal (merged) | → `django_fusion.web` | Source: `django_fusion/web/views/mixins.py`, `django_fusion/web/rendering.py` |
| ceptor-ai | `applications/libs/ceptor-ai/` | (standalone AI package) |

---

## Documentation Maintenance & Organization

### Prompt: Generate or Reorganize Documentation

> Generate a report, guide, or reference document for `<topic>` and save it in the unified `docs/` structure. Do not place new `.md` files in the repo root unless they are `README.md`, `AGENTS.md`, or `PROMPTS.md`.

**Expected input:**
- Topic or feature to document
- Target category under `docs/` (e.g., `guides/`, `reference/`, `changelog/`, `upcoming/`, `archives/`)

**Expected output:**
- A new markdown file placed strictly inside the relevant `docs/<category>/` directory
- An updated `docs/_sidebar.md` navigation entry
- No duplicated documentation added to the root directory
- Cross-references updated in `AGENTS.md` Documentation References table when applicable

**Related docs:** `docs/reference/docs_overview.md`, `docs/_sidebar.md`
**Related tags:** `Docsify`, `documentation`, `unified-structure`, `markdown`

---

## Default Template Tags (Builtins)

## Default Template Tags (Builtins)

The shared template configuration in `applications/configs/base/templates.py` registers the following tag libraries as Django template **builtins**, so they are available in every template without `{% load %}`:

| Builtin | Source | Available tags |
|---------|--------|----------------|
| `django.templatetags.static` | Django | `{% static %}`, `{% get_static_prefix %}` |
| `unfold.templatetags.unfold` | django-unfold | Unfold admin tags |
| `django_fusion.comp.templatetags.components` | django-fusion | `{% comp %}`, `{% prop %}`, `{% slot %}`, `{% var %}`, `{% css %}`, `{% js %}` |
| `django_fusion.templatetags.ui_tags` | django-fusion | `{% table %}`, `{% pagination %}`, `{% search %}`, `{% form_field %}` |

### What this means for template authors

- You can write `{% comp "components/button.html" / %}` directly.
- You can still use `{% load components %}` for clarity or copy-paste compatibility; the library is also registered under `"components"`.

### Adding a new builtin

1. Open `applications/configs/base/templates.py`.
2. Append the dotted path to `_TEMPLATE_BUILTINS`.
3. Run `make -C applications check WEBSITE=ctc-research` to verify no import errors.

---

## Deployment & Make Commands

### Root Makefile Organization

The root `Makefile` is the central deployment orchestrator. It delegates to component Makefiles:

```
Root Makefile (make targets)
├── deploy-all              (main orchestration target)
│   ├── make preflight-network
│   ├── make deploy-preflight
│   ├── make deploy-databases
│   ├── make deploy-coder
│   ├── make deploy-media
│   ├── make deploy-app
│   ├── make deploy-tasks
│   ├── make deploy-docs
│   ├── make deploy-proxy
│   └── make deploy-customizer
├── applications/Makefile   (delegated for WEBSITE=<site> targets)
├── proxy/Makefile          (delegated for proxy-specific commands)
├── databases/Makefile      (delegated for database commands)
└── services/Makefile       (delegated for service commands)
```

### Quick Deployment Commands

```bash
# Full deployment (validates + deploys in correct dependency order)
make deploy

# Just validate (CI gate — no deploy)
make deploy-ci

# Specific component deployments
make deploy-app             # All Django applications (all sites)
make deploy-proxy           # Traefik reverse proxy
make deploy-media           # Nginx media server
make deploy-databases       # PostgreSQL + Redis
```

### Deployment Order Strategy

**Default (postgres-first)**: DB → Coder → Media → Apps → Tasks → Docs → Proxy
- ✅ Robust: database online before apps start
- ✅ Correct: media server ready before Django mounts volumes

**Legacy**: Proxy → Apps → Media → Tasks → Docs → Databases
- ⚠️  Not recommended: apps crash waiting for DB on startup
- 🔧 Kept for back-compat only

**Override order**:
```bash
make deploy DEPLOY_ORDER=postgres-first   # default
make deploy DEPLOY_ORDER=legacy           # not recommended
```

### Make Commands Tree (Full Reference)

#### Deployment

```
make deploy              # Everything (preflight → deploy-all)
make deploy-ci          # Preflight only (CI gate, no deploy)
make deploy-app         # Django apps (all sites)
make deploy-proxy       # Traefik reverse proxy
make deploy-media       # Nginx media server
make deploy-databases   # PostgreSQL + Redis
make deploy-coder       # Coder IDE platform
make deploy-customizer  # Template customizer
make deploy-tasks       # Celery workers
make deploy-docs        # Documentation site
make deploy-utilities   # Monitoring (if directory exists)
make deploy-ollama      # Ollama + Open WebUI (if directory exists)
make deploy-mailpit     # Mailpit (if directory exists)
make deploy-coolify     # Separate Coolify stack
```

#### Preflight & Validation

```
make deploy-preflight      # Smoke-test compose files
make preflight-network     # Validate network names
make create-networks       # Create Docker networks (idempotent)
make validate-deploy-order # Check DEPLOY_ORDER value
make check-docker          # Verify docker is installed & running
make deploy-ci             # CI gate (preflight only, no deploy)
```

#### Management & Monitoring

```
make status                # Show service status
make logs                  # Show logs from all services
make logs-common           # Stream Coolify logs (follow mode)
make stop                  # Stop all services
make restart               # Restart all services (= make stop + make deploy)
```

#### Cleanup & Maintenance

```
make prune                 # Remove stopped containers + volumes + images
make prune-containers      # Remove stopped containers only
make prune-volumes         # Remove unused volumes only
make prune-images          # Remove unused images only
make clean                 # Aggressive teardown (all containers, volumes, images)
```

#### Per-Site Shortcuts

```
make ctc-research          # Forward to applications/Makefile with WEBSITE=ctc-research
make lms-demo              # Forward to applications/Makefile with WEBSITE=lms-demo
make vresume               # Forward to applications/Makefile with WEBSITE=vresume
```

#### Component Makefiles (Delegate to Sub-Makefiles)

```
make proxy                 # Proxy commands (delegates to proxy/Makefile)
make databases             # Database commands (delegates to databases/Makefile)
make services              # Service commands (delegates to services/Makefile)
make customizer            # Customizer commands (delegates to applications/customizer/Makefile)
```

#### Build Commands

```
make build                 # Build all components
make build-app             # Build Django application images
make build-media           # Build media server image
make build-docs            # Build documentation image
make build-customizer      # Build customizer webpack bundles
```

#### Coolify Management (Separate Stack)

```
make deploy-coolify        # Full Coolify deployment
make restart-coolify       # Restart Coolify service
make build-coolify         # Rebuild Coolify images
make list-coolify          # List Coolify containers
make upgrade-coolify       # Upgrade to latest
make start-coolify         # Start Coolify service
make stop-coolify          # Stop Coolify service
```

#### Certificate Management

```
make cert-generate         # Generate self-signed certificates
make cert-backup           # Backup current certificates
make cert-restore          # Restore from backup
make cert-validate         # Validate certificate/key pairs
make cert-check            # Check certificate expiry
```

#### Git Operations

```
make push                  # Push repo + all lib submodules to origin
make push-libs             # Push only library submodules
make push-lib LIB=name     # Push specific library (e.g., LIB=django-fusion)
make pull                  # Pull from origin (auto-rebase if diverged)
make sync                  # Pull then push in one step
```

#### Versioning

```
make bump-action-patch     # Bump deploy-preflight action (patch)
make bump-action-minor     # Bump deploy-preflight action (minor)
make bump-action-major     # Bump deploy-preflight action (major)
make bump-app-patch        # Bump applications version (patch)
make bump-app-minor        # Bump applications version (minor)
make bump-app-major        # Bump applications version (major)
make verify-release        # Sanity-check published action tag
```

#### Help Commands

```
make help                  # Main command reference
make help-all              # Extended help + component-specific help
```

### Common Workflows

#### Deploy All Services (First Time)

```bash
# 1. Validate everything is correct (CI gate)
make deploy-ci

# 2. Create networks + preflight checks
make preflight-network
make deploy-preflight

# 3. Deploy everything in correct order
make deploy
```

#### Redeploy a Single Site

```bash
# Redeploy CTC Research only
make ctc-research docker-up

# Or: full application redeployment (all sites)
make deploy-app
```

#### Monitor Services

```bash
# Check what's running
make status

# View all logs
make logs

# Stream specific service logs
docker logs ctc-research-website -f --tail 50
```

#### Clean & Restart

```bash
# Stop everything
make stop

# Restart from scratch
make deploy
```

#### Git Workflow

```bash
# Push changes to GitHub
make push                  # Pushes main repo + libraries

# Pull latest changes
make pull                  # Smart merge (auto-rebase if diverged)

# Full sync
make sync                  # Pull + push in one command
```

### Environment Variables

```bash
# Deployment configuration
export DEPLOY_ORDER=postgres-first  # or: legacy

# Git authentication
export GITHUB_TOKEN=ghp_xxxxx...    # For make push/pull/sync

# Pull strategy
export PULL_MODE=rebase            # or: merge

# Sync options
export SYNC_MODE=rebase            # or: merge
export SYNC_SKIP_PUSH=1            # Pull only, don't push
```

### Docker Compose File Tree

```
docker-compose.yml (root orchestrator)
├── databases/docker-compose.yml
├── proxy/docker-compose.yml
└── compose/docker-compose.applications.yml
    ├── applications/ctc-research/docker-compose.yml
    ├── applications/lms-demo/docker-compose.yml
    ├── applications/VResume/docker-compose.yml
    ├── applications/crm/docker-compose.yml
    └── (applications/customizer/ commented out)

Optional compose files:
├── compose/docker-compose.docs.yml
├── compose/docker-compose.tasks.yml
├── services/docker-compose.media.yml
└── source/docker-compose.yml (Coolify, external)
```

### Network Configuration

All services share these Docker networks:

| Network | Purpose | Services |
|---------|---------|----------|
| `common` | Default for most services | Django apps, media, databases |
| `traefik-net` | Proxy-specific network | Traefik, backend apps |
| `internal` | Internal only (no egress) | Redis, internal databases |
| `utilities-net` | Monitoring stack | Prometheus, Grafana, Loki |
| `warehouse-net` | Data warehouse | Clickhouse, ETL services |
| `ollama-net` | AI/ML services | Ollama, Open WebUI |

Networks are created idempotently by `make create-networks` (prerequisite of `make deploy-all`).

### Troubleshooting Deployments

**Preflight Fails**:
```bash
make deploy-ci            # See which check fails
make deploy-preflight     # Validate compose files only
make preflight-network    # Validate network names only
```

**Service Won't Start**:
```bash
make logs                 # See all logs
make status               # Check running services
make deploy-databases     # Deploy databases first
make deploy-app           # Then deploy apps
```

**Out of Disk Space**:
```bash
make prune                # Safe cleanup
# or
make clean                # Aggressive cleanup (full reset)
```

**Need to Rebuild**:
```bash
make build                # Rebuild all images
make build-app            # Rebuild apps only
make deploy               # Redeploy
```

### See Also

- **[docs/deployment/index.md](./docs/deployment/index.md)** – Comprehensive deployment reference
- **[README.md](./README.md)** – Project overview
- **[docs/deployment/](./docs/deployment/)** – Detailed deployment documentation
- **[applications/Makefile](./applications/Makefile)** – Django-specific commands
- **[proxy/Makefile](./proxy/Makefile)** – Proxy-specific commands
