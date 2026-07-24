# django-material → django-fusion Mapping

Side-by-side reference mapping viewflow/django-material (vibe branch) URL patterns to their
django-fusion equivalents. Based on analysis of
[django-material demo/urls.py](https://github.com/viewflow/django-material/blob/vibe/demo/urls.py).

---

## Site and Application Setup

### django-material (viewflow)

```python
# viewflow/django-material vibe branch
from material.urls import Site, Application, menu_path

cotton = Application(
    title="Components",
    app_name="html",
    icon="layers",
    urlpatterns=[
        menu_path("breadcrumbs/", TemplateView.as_view(
            template_name="html/breadcrumbs.html"
        ), name="breadcrumbs", title="Breadcrumbs"),
        menu_path("buttons/", TemplateView.as_view(
            template_name="html/buttons.html"
        ), name="buttons", title="Buttons"),
    ],
)

site = Site(
    title="Django Vibe",
    viewsets=[cotton, api, AtlasApp()],
    urlpatterns=[
        path("", include("demo.pages.urls")),
    ],
)
```

### django-fusion equivalent

```python
# django-fusion
from django_fusion.routes import Site, Application, menu_path

html_app = Application(
    title="Components",
    app_name="html",
    icon="layers",
    urlpatterns=[
        menu_path("breadcrumbs/", TemplateView.as_view(
            template_name="html/breadcrumbs.html"
        ), name="breadcrumbs", title="Breadcrumbs"),
        menu_path("buttons/", TemplateView.as_view(
            template_name="html/buttons.html"
        ), name="buttons", title="Buttons"),
    ],
)

site = Site(
    title="Django Vibe",
    viewsets=[html_app, api_app, AtlasApp()],
    urlpatterns=[
        path("", include("demo.pages.urls")),
    ],
)
```

The `Site`, `Application`, and `menu_path` imports map 1:1. django-fusion preserves the same API
surface with identical semantics.

---

## URL Pattern Mapping Table

| django-material URL name | View/handler class | django-fusion Equivalent | Notes |
|--------------------------|-------------------|--------------------------|-------|
| `html:breadcrumbs` | `TemplateView` | `menu_path("breadcrumbs/", TemplateView.as_view(...), ...)` | 1:1 — identical API |
| `html:buttons` | `TemplateView` | `menu_path("buttons/", TemplateView.as_view(...), ...)` | 1:1 — identical API |
| `html:cards` | `TemplateView` | `menu_path("cards/", TemplateView.as_view(...), ...)` | 1:1 |
| `html:chips` | `TemplateView` | `menu_path("chips/", TemplateView.as_view(...), ...)` | 1:1 |
| `html:dialogs` | `TemplateView` | `menu_path("dialogs/", TemplateView.as_view(...), ...)` | 1:1 |
| `html:lists` | `TemplateView` | `menu_path("lists/", TemplateView.as_view(...), ...)` | 1:1 |
| `html:menus` | `TemplateView` | `menu_path("menus/", TemplateView.as_view(...), ...)` | 1:1 |
| `html:navigation` | `TemplateView` | `menu_path("navigation/", TemplateView.as_view(...), ...)` | 1:1 |
| `html:progress` | `TemplateView` | `menu_path("progress/", TemplateView.as_view(...), ...)` | 1:1 |
| `html:tabs` | `TemplateView` | `menu_path("tabs/", TemplateView.as_view(...), ...)` | 1:1 |
| `html:text-fields` | `TemplateView` | `menu_path("text-fields/", TemplateView.as_view(...), ...)` | 1:1 |
| `api:index` | `TemplateView` | `menu_path("", TemplateView.as_view(...), ...)` | 1:1 |
| `atlas:index` | `AtlasApp().get_urls()` | `ModelViewset` in an `Application` subclass | See AtlasApp pattern below |
| `atlas:list` | `ListModelView` (via AtlasApp) | `from django_fusion.components.generic import ListModelView` | See ModelViewset mapping |
| `atlas:detail` | `DetailModelView` (via AtlasApp) | `from django_fusion.components.generic import DetailModelView` | See ModelViewset mapping |
| `atlas:create` | `CreateModelView` (via AtlasApp) | `from django_fusion.components.generic import CreateModelView` | See ModelViewset mapping |
| `atlas:update` | `UpdateModelView` (via AtlasApp) | `from django_fusion.components.generic import UpdateModelView` | See ModelViewset mapping |
| `atlas:delete` | `DeleteModelView` (via AtlasApp) | `from django_fusion.components.generic import DeleteModelView` | See ModelViewset mapping |

---

## AtlasApp Pattern: Custom Application with ModelViewset

### django-material

```python
# viewflow/django-material — AtlasApp is a custom Application subclass
from material.urls import Application
from material.frontend.views import ListModelView, DetailModelView, CreateModelView, UpdateModelView, DeleteModelView

class AtlasApp(Application):
    title = "Atlas"
    app_name = "atlas"
    icon = "map"

    def get_urls(self):
        return [
            path("", ListModelView.as_view(model=MyModel), name="index"),
            path("<int:pk>/", DetailModelView.as_view(model=MyModel), name="detail"),
            path("create/", CreateModelView.as_view(model=MyModel), name="create"),
            path("<int:pk>/update/", UpdateModelView.as_view(model=MyModel), name="update"),
            path("<int:pk>/delete/", DeleteModelView.as_view(model=MyModel), name="delete"),
        ]
```

### django-fusion equivalent

```python
# django-fusion — ModelViewset provides the same CRUD routes in one class
from django_fusion.routes import ModelViewset, Application

class AtlasModelViewset(ModelViewset):
    model = MyModel
    template_name = "atlas/mymodel"  # resolves _list, _detail, _form
    paginate_by = 25

class AtlasApp(Application):
    title = "Atlas"
    app_name = "atlas"
    icon = "map"
    urlpatterns = AtlasModelViewset.get_urlpatterns()
```

Or inline with the Application:

```python
atlas_app = Application(
    title="Atlas",
    app_name="atlas",
    icon="map",
    viewsets=[AtlasModelViewset],
)
```

The `ModelViewset` automatically generates: list, detail, create, update, and delete routes.
This eliminates the manual `get_urls()` method needed in django-material.

---

## Cotton Components → django-fusion `{% comp %}` Mapping

django-material (vibe branch) uses django-cotton for UI components. Here's how they map:

### Cotton Component

```html
<!-- cotton/button.html -->
<c-vars variant="filled" label="" disabled=False />
<button class="md3-button md3-button--{{ variant }}"
        {% if disabled %}disabled{% endif %}
        {{ attrs }}>
  {{ label }}
  {{ slot }}
</button>
```

Usage:
```html
<c-button variant="tonal" label="Save" />
<c-button variant="outlined">
  <c-slot name="default">
    <span class="icon">✓</span> Confirm
  </c-slot>
</c-button>
```

### django-fusion `{% comp %}` Equivalent

```django
{# components/material/button.html #}
{% load components %}
{% prop variant="filled" %}
{% prop label="" %}
{% prop disabled=False %}
<button class="md3-button md3-button--{{ props.variant }} {{ attrs }}"
        {% if props.disabled %}disabled{% endif %}>
  {{ props.label }}
  {% slot %}{{ slot }}{% endslot %}
</button>
```

Usage:
```django
{% comp "components/material/button.html" variant="tonal" label="Save" / %}

{% comp "components/material/button.html" variant="outlined" %}
  <span class="icon">✓</span> Confirm
{% endcomp %}
```

### Cotton Card Component → `{% comp %}`

```html
<!-- cotton/card.html -->
<c-vars title="" image="" />
<div class="md3-card" {{ attrs }}>
  {% if image %}<img class="md3-card__media" src="{{ image }}" alt="{{ title }}">{% endif %}
  <c-slot name="header">
    {% if title %}<h3 class="md3-card__title">{{ title }}</h3>{% endif %}
  </c-slot>
  <div class="md3-card__body">{{ slot }}</div>
  <c-slot name="actions" />
</div>
```

```django
{# components/material/card.html #}
{% load components %}
{% prop title="" %}
{% prop image="" %}
<div class="md3-card {{ attrs }}">
  {% if props.image %}<img class="md3-card__media" src="{{ props.image }}" alt="{{ props.title }}">{% endif %}
  {% if props.title %}<h3 class="md3-card__title">{{ props.title }}</h3>{% endif %}
  {% slot header %}{% endslot %}
  <div class="md3-card__body">{% slot %}{{ slot }}{% endslot %}</div>
  {% slot actions %}{% endslot %}
</div>
```

---

## Key Differences Summary

| Concept | django-material/Cotton | django-fusion `{% comp %}` |
|---------|----------------------|---------------------------|
| **Component call** | `<c-button />` or `{% cotton button /%}` | `{% comp "components/button.html" / %}` |
| **Variable props** | `:title="var"` (colon-prefix) | `title=var` (standard Django) |
| **Prop defaults** | `<c-vars title="Default" />` | `{% prop title="Default" %}` |
| **Named slots** | `<c-slot name="header">` | `{% slot header %}...{% endslot %}` |
| **Default slot** | `{{ slot }}` | `{% slot %}{{ slot }}{% endslot %}` |
| **HTML attrs** | `{{ attrs }}` | `{{ attrs }}` |
| **Local state** | N/A (not built-in) | `{% var key="value" %}` |
| **Fragment/HTMX** | N/A | `fragment_name="..."` kwarg |
| **File location** | `cotton/` directory | Any `components/**/*.html` under `COMPONENTS_INCLUDE_PATH_ROOTS` |
| **Auto-registration** | Directory-based | `register_default_partials()` at startup |
| **Template syntax** | HTML-like + custom tags | Pure Django template tags |

---

## Migration Path: Cotton → django-fusion

1. **Replace `<c-component>` with `{% comp %}`**: Change `<c-button />` → `{% comp "components/button.html" / %}`
2. **Replace `<c-vars>` with `{% prop %}`**: `<c-vars title="Hi" />` → `{% prop title="Hi" %}`
3. **Replace `<c-slot name="x">` with `{% slot x %}`**: Same semantics
4. **Replace `:prop="var"` with `prop=var`**: Drop the colon prefix
5. **Keep `{{ attrs }}` and `{{ slot }}`**: Identical
6. **Add `fragment_name`** for HTMX scoping if needed

---

## Related Documentation

| Topic | File |
|-------|------|
| Component Tag Reference | [COMPONENT_TAG.md](./COMPONENT_TAG.md) |
| Component System Overview | [COMPONENT_SYSTEM.md](./COMPONENT_SYSTEM.md) |
| Routing System | [ROUTING_SYSTEM.md](./ROUTING_SYSTEM.md) |
| Architecture Overview | [ARCHITECTURE_OVERVIEW.md](./ARCHITECTURE_OVERVIEW.md) |
| django-material demo source | https://github.com/viewflow/django-material/blob/vibe/demo/urls.py |
| django-cotton docs | https://django-cotton.com/docs/components |

---

**Next**: See [COMPONENT_TAG.md](./COMPONENT_TAG.md) for the full `{% comp %}` props/slots/vars API reference.
