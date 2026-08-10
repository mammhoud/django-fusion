# Architecture Overview — DF-002

> Source of truth: `src/django_fusion/__init__.py` docstring, `AGENTS.md`,
> top-level package directories under `src/django_fusion/`.

## Module map

```
django_fusion/
├── analyzer/        # Scanner + parser → JSON tracking of {% comp %} usage
├── comp/            # Component tag, registry, props, loader, cache, templates
│   ├── _init.py     # Component, BoundComponent, ComponentRegistry
│   ├── registry.py  # Include-path registration and alias policy
│   ├── loader/      # Template discovery and HTMX-safe loader
│   ├── cache.py     # ComponentMapCache (portable backend fallback)
│   └── templatetags/
├── fragments/       # Generic views, forms, tables, and fragment helpers
├── config/          # conf, conf_utils, constants, loader
├── contrib/         # admin, cache utils, debug_tools, email_config, privacy
├── routes/          # Site/Application routing, views, pages, fragments
├── management/      # Managers and shared management helpers
├── models/          # Shared abstract and concrete model infrastructure
├── services/        # Service and token APIs
├── core/health/     # /health/, /health/database/, /health/assets/
├── infrastructure/  # Management commands, scripts, template tags, locale
├── site/            # Allauth adapter, context processors, notifications, paginators
└── wagtail/         # blocks.py, snippets.py, viewsets.py
```

## Layered design

| Layer | Module(s) | Responsibility |
|-------|-----------|---------------|
| Foundation | `models`, `management.managers`, `services`, `comp.cache` | Models, managers, service base, and component cache |
| Request-handling | `routes.page_handler`, `core.middlewares` | `PageHandler`, error tracking, privacy, language |
| Routing | `routes` | `Site` / `Application` / `ModelViewset` and HTMX-aware components |
| Components | `comp`, `fragments` | Registry, fragment detection, `{% comp %}` tag, generic views, forms, tables |
| Forms / Tables | `fragments.forms`, `fragments.tables` | `FormMixin`, `TableMixin`, `FormTableMixin` |
| Site-level | `site.*`), `web.*` | Allauth flows, context processors, template rendering helpers |
| CMS | `wagtail.*` | StreamField blocks, `AuthEmailTemplate` snippet, snippet viewsets |
| Ops | `core.health`, `contrib.{cache,debug_tools,privacy}` | `/health/`, monitoring, consent |
| Config | `config.{conf,loader}`, `infrastructure` | Multi-env YAML settings |
| Analysis | `analyzer` | Static analysis of `{% comp %}` usage across templates |

## Request flow (Mermaid)

```mermaid
flowchart LR
    A[HTTP Request] --> B[Django URLconf]
    B --> C[Site.urls]
    C --> D[Application.urls]
    D --> E[Viewset / ModelViewset]
    E --> F[RoutableComponent / FragmentComponent]
    F --> G[resolve_template_name]
    G --> H{strategy}
    H -->|fragment| I[fragment template]
    H -->|document| J[full-page template]
    I --> K[{% comp %} registry.render]
    J --> K
    K --> L[Response]
    L --> M[HTTP Response]
```

## When would I touch this?

- **`models/`, `management/managers/`, or `services/`** — when adding shared
  framework infrastructure reused by multiple apps.
- **`comp/` or `fragments/`** — when extending the component and rendering systems.
- **`site/` / `web/`** — when adding an auth flow or new context processor.
- **`wagtail/`** — when adding a new StreamField block or snippet viewset.
- **`contrib/`** — when shipping opt-in Django tools (privacy, debug,
  monitoring) that callers can enable per project.
- **`infrastructure/`** — for locale files, custom `manage.py` commands,
  or pre-build scripts.

## Public surface (canonical imports)

Per `AGENTS.md`:

```python
from django_fusion.routes.core.base import (
    Viewset,
    BaseViewset,
    ViewsetMeta,
    Route,
    route,
    menu_path,
    IndexViewMixin,
)
from django_fusion.core.utils import viewprop
from django_fusion.routes.models.base import BaseModelViewset
from django_fusion.routes.models.crud import (
    ModelViewset,
    ReadonlyModelViewset,
    ListBulkActionsMixin,
    CreateViewMixin,
    UpdateViewMixin,
    DeleteViewMixin,
    DetailViewMixin,
)
from django_fusion.routes.core.sites import (
    Application,
    AppMenuMixin,
    Site,
)
from django_fusion.routes.components.routable import RoutableComponent
from django_fusion.routes.components.fragments import FragmentComponent
from django_fusion.routes.http.detection import (
    FragmentDetector,
    FragmentDetectionMixin,
)
from django_fusion.fragments.generic.base import Action
from django_fusion.fragments.generic.list import BaseListModelView, ListModelView
from django_fusion.fragments.generic.detail import DetailModelView
from django_fusion.fragments.generic.actions import BaseBulkActionView, DeleteBulkActionView
from django_fusion.fragments.forms.create import CreateModelView
from django_fusion.fragments.forms.update import UpdateModelView
from django_fusion.fragments.forms.delete import DeleteModelView
from django_fusion.fragments.forms.search import SearchableViewMixin
from django_fusion.fragments.tables.table import TableView
```

See DF-008 for the full per-module docstring reference.

## Versioning & stability

`__version__ = "0.5.0"`. Below `1.0`, minor versions may reorganise
the public surface. After `1.0`, the canonical import paths above are
considered stable.
