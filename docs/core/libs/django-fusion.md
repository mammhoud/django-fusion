# django-fusion

`django-fusion` is the reusable Django/Wagtail foundation library for Structa Cloud sites. It lives in `core/libs/django-fusion/` as an editable submodule.

## Installation

```bash
uv pip install -e core/libs/django-fusion/
```

## Canonical import paths

### Routing

```python
from django_fusion.comp.routes import (
    Viewset, BaseViewset, ViewsetMeta, Route, route, menu_path, IndexViewMixin,
    viewprop,
    BaseModelViewset, ModelViewset, ReadonlyModelViewset,
    ListBulkActionsMixin, CreateViewMixin, UpdateViewMixin, DeleteViewMixin, DetailViewMixin,
    Application, AppMenuMixin, Site,
    RoutableComponent, FragmentComponent,
    FragmentDetector, FragmentDetectionMixin,
)
```

### Generic CBVs

```python
from django_fusion.comp.generic import (
    Action, CreateModelView, DeleteBulkActionView, DeleteModelView,
    DetailModelView, ListModelView, UpdateModelView,
    BaseListModelView, BaseBulkActionView, SearchableViewMixin, TableView,
)
```

### Other modules

| Module | Import |
|---|---|
| Handlers | `django_fusion.core.handlers` |
| Managers | `django_fusion.core.managers` |
| Models | `django_fusion.core.models` |
| Services | `django_fusion.core.services` |
| Views | `django_fusion.web.views` |
| Loaders | `django_fusion.comp.loaders` |
| Middlewares | `django_fusion.core.middlewares` |
| Cache | `django_fusion.core.cache` |

## Component template tags

The library provides the `{% comp %}` and `{% comp_include %}` template tags.

```django
{% comp "contact.sections.form" block=block / %}
{% comp_include "components/form/form.html" form=my_form %}
```

See [core/components/django_tags.md](../components/django_tags.md) for full usage.

## Boundaries

- No Wagtail imports in the core package.
- No Celery imports in the core package.
- No `ceptor-ai` imports in the core package.

Site-specific behavior should be added in thin adapters inside each site, not in `django-fusion`.
