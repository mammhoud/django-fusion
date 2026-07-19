# 🔴 django-fusion — `libs/django-fusion/`

Component system, routing framework, and view infrastructure for Django site projects.

> **Customization level**: 🔴 Not Customizable — use its public API, don't modify internals.

## Canonical Import Paths

All re-export shims have been removed. Use these paths directly:

### Routing (`comp.routes`)
```python
from django_fusion.comp.routes import (
    Site, Application, Viewset, BaseViewset,
    ModelViewset, ReadonlyModelViewset,
    route, menu_path, viewprop,
    RoutableComponent, FragmentComponent,
)
```

### Generic Views (`comp.generic`)
```python
from django_fusion.comp.generic import (
    ListModelView, CreateModelView, UpdateModelView,
    DeleteModelView, DetailModelView, TableView,
    SearchableViewMixin, Action,
)
```

### Other modules
```python
# Handlers
from django_fusion.core.handlers import PageHandler

# Services
from django_fusion.core.services import BaseService

# Middleware
from django_fusion.core.middlewares import SiteMiddleware

# Cache
from django_fusion.core.cache import cache_manager
```

## Template Tags

```django
{# Render a component by name #}
{% comp "contact.sections.form" block=block / %}

{# Tracked include (registers path for component tracking) #}
{% comp_include "path/to/template.html" %}

{# Legacy include (only for dynamic template names) #}
{% include template_name %}
```

## Component Conventions

```
components/
├── blocks/           # Full content blocks
│   ├── contact/
│   │   ├── contact_profile.html
│   │   └── sections/
│   │       └── form.html
│   └── blog/
├── partials/         # Small UI fragments
│   ├── buttons.html
│   └── icons.html
└── tags/             # Custom template tags
```

**Naming rule**: Don't repeat the folder name. Use `components/blocks/contact/contact_profile.html` NOT `components/blocks/contact/contact/contact_profile.html`.

## Fragment Convention

Always use `fragment_name` for fragment identifiers:
```python
# ✅ Correct
context['fragment_name'] = 'login-form'

# ❌ Wrong
context['fragment'] = 'login-form'
context['name'] = 'login-form'
```

## Site Setup

```python
# In site's AppConfig.ready()
from django_fusion.comp.loaders import register_include_path

register_include_path('path/to/templates')
```

## Viewset Pattern

```python
class ProductViewset(ModelViewset):
    model = Product
    fields = ['name', 'price', 'category']
    list_display = ['name', 'price']
    search_fields = ['name']
```

---

→ [Back to Python docs](README.md)
