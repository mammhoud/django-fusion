# Django-Fusion API Reference

Complete API reference for django-fusion components, mixins, and utilities.

## Table of Contents

- [Core Components](#core-components)
- [Sites & Applications](#sites--applications)
- [Mixins](#mixins)
- [Utilities](#utilities)
- [Settings](#settings)
- [Exceptions](#exceptions)

## Core Components

### RoutableComponent

Base class for routable components. Inherits from Django's `TemplateView`.

```python
from django_fusion.comp.routes import RoutableComponent

class MyComponent(RoutableComponent):
    route_path = "my-path/"
    template_name = "my_template.html"
```

#### Attributes

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `route_path` | str | Required | URL path pattern |
| `template_name` | str | Required | Template to render |
| `name` | str | Auto | Component name |
| `label` | str | Auto | Display label |
| `icon` | str | None | Icon class |
| `show_in_menu` | bool | True | Show in menu |

#### Methods

**render_to_response(context, **response_kwargs)**

Render template with context.

```python
context = self.get_context_data()
return self.render_to_response(context)
```

**get_context_data(**kwargs)**

Prepare data for template. Override to add custom context.

```python
def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['extra_data'] = 'value'
    return context
```

**get_template_names()**

Return list of template names to try.

```python
def get_template_names(self):
    return [
        f"pages/{self.model._meta.model_name}.html",
        "pages/default.html",
    ]
```

**dispatch(request, *args, **kwargs)**

Entry point for all requests.

```python
def dispatch(self, request, *args, **kwargs):
    # Pre-processing
    if not request.user.is_authenticated:
        return redirect('login')
    
    response = super().dispatch(request, *args, **kwargs)
    
    # Post-processing
    return response
```

### FragmentComponent

Base class for HTMX fragment components.

```python
from django_fusion.comp.routes import FragmentComponent

class MyFragment(FragmentComponent):
    route_path = "fragment-path/"
    fragment_name = "my.fragments.example"
    template_name = "fragments/my.html"
```

#### Attributes

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `fragment_name` | str | Required | Fragment identifier |
| All RoutableComponent attributes | - | - | - |

#### Methods

Same as RoutableComponent, plus:

**get_fragment_name()**

Get fragment identifier.

```python
def get_fragment_name(self):
    return self.fragment_name
```

## Sites & Applications

### Site

Top-level container for all components and applications.

```python
from django_fusion.comp.routes import Site

site = Site(
    name="mysite",
    label="My Site",
    applications=[app1, app2],
    namespace="mysite",
)
```

#### Attributes

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | str | Required | Site identifier |
| `label` | str | name | Display label |
| `applications` | list | [] | Applications |

#### Properties

**urls**

Get URL configuration tuple.

```python
urlconf, app_name, namespace = site.urls

# Usage:
path("", include((site.urls[0], site.urls[1]), namespace=site.urls[2]))
```

### Application

Organizes related components.

```python
from django_fusion.comp.routes import Application

app = Application(
    name="blog",
    label="Blog",
    components=[ListComponent, DetailComponent],
    icon="fas fa-blog",
)
```

#### Attributes

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | str | Required | App identifier |
| `label` | str | name | Display label |
| `components` | list | [] | Components |
| `icon` | str | None | Icon class |

## Mixins

### FormMixin

Add form rendering to components.

```python
from django_fusion.comp.routes import FormMixin, RoutableComponent

class MyFormComponent(FormMixin, RoutableComponent):
    model = MyModel
    form_class = MyForm
    template_name = "my_form.html"
```

#### Methods

**get_form()**

Instantiate form with data.

```python
form = self.get_form()
```

**get_form_class()**

Get form class to use.

```python
def get_form_class(self):
    return MyCustomForm
```

**form_valid(form)**

Process valid form submission.

```python
def form_valid(self, form):
    self.object = form.save()
    return redirect(self.get_success_url())
```

**form_invalid(form)**

Handle invalid form submission.

```python
def form_invalid(self, form):
    context = self.get_context_data(form=form)
    return self.render_to_response(context)
```

**get_success_url()**

Get URL after successful form submission.

```python
def get_success_url(self):
    return reverse('app:detail', args=[self.object.id])
```

### TableMixin

Add table rendering to components.

```python
from django_fusion.comp.routes import TableMixin, RoutableComponent

class MyTableComponent(TableMixin, RoutableComponent):
    model = MyModel
    paginate_by = 25
    template_name = "my_table.html"
```

#### Methods

**get_table_data()**

Get data for table display.

```python
def get_table_data(self):
    return self.get_queryset()
```

**get_columns()**

Get table column definitions.

```python
def get_columns(self):
    return [
        {'name': 'id', 'label': 'ID'},
        {'name': 'name', 'label': 'Name'},
        {'name': 'email', 'label': 'Email'},
    ]
```

**paginate_queryset(queryset, page_size)**

Paginate queryset.

```python
page_obj, page_num, is_paginated = self.paginate_queryset(
    queryset, 
    self.paginate_by
)
```

### SearchableViewMixin

Add search functionality.

```python
from django_fusion.web.views import SearchableViewMixin, RoutableComponent

class SearchableComponent(SearchableViewMixin, RoutableComponent):
    search_fields = ['title', 'content']
```

#### Methods

**get_search_query()**

Get search query from request.

```python
search = self.get_search_query()  # From request.GET['q']
```

**apply_search_filter(queryset)**

Apply search filter to queryset.

```python
queryset = self.apply_search_filter(queryset)
```

## Utilities

### FragmentDetector

Detect if request is for a fragment.

```python
from django_fusion.comp.routes import FragmentDetector

detector = FragmentDetector(request)
if detector.is_fragment_request():
    # Handle fragment request
    return fragment_template
else:
    # Handle full page request
    return full_template
```

#### Methods

**is_fragment_request()**

Check if request is for fragment.

```python
if detector.is_fragment_request():
    # True if HX-Request header is present
```

**get_fragment_identifier()**

Get fragment identifier.

```python
fragment_id = detector.get_fragment_identifier()
```

### Route Decorator

Register component routes.

```python
from django_fusion.comp.routes import route

@route('path/<int:id>/')
def component_method(self, request, id):
    pass
```

## Settings

### FUSION Configuration

Settings for django-fusion in Django's `settings.py`:

```python
# Enable component tracking
FUSION_ENABLE_TRACKING = True

# Component cache timeout (seconds)
FUSION_CACHE_TIMEOUT = 3600

# Template context processor
FUSION_TEMPLATE_CONTEXT_PROCESSOR = True

# Auto-discover components
FUSION_AUTO_DISCOVER = True

# Components module path
FUSION_COMPONENTS_PATH = 'routable_components'

# Logging
FUSION_LOG_LEVEL = 'INFO'
```

### Template Settings

Template configuration:

```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            'templates/',
            'applications/assets/templates/',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django_fusion.context_processors.fusion',
            ],
        },
    },
]
```

## Exceptions

### ComponentNotFound

Raised when component is not found.

```python
from django_fusion.comp.exceptions import ComponentNotFound

try:
    component = site.get_component('nonexistent')
except ComponentNotFound:
    # Handle missing component
```

### RouteNotFound

Raised when route is not found.

```python
from django_fusion.comp.exceptions import RouteNotFound

try:
    url = site.reverse('nonexistent')
except RouteNotFound:
    # Handle missing route
```

### TemplateNotFound

Raised when template is not found.

```python
from django.template.exceptions import TemplateDoesNotExist

try:
    template = self.get_template_names()
except TemplateDoesNotExist:
    # Handle missing template
```

## Import Paths

### Canonical Imports (Current)

Always use these canonical paths from the current version:

```python
# Routing & Components
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
    detect_fragment_strategy, add_fragment_detection_to_request,
    # Forms and Tables integration
    FormMixin, TableMixin, FormTableMixin,
    # Template resolution
    TemplateResolverMixin,
)

# Generic CBVs
from django_fusion.comp.generic import (
    Action, CreateModelView, DeleteBulkActionView, DeleteModelView,
    DetailModelView, ListModelView, UpdateModelView,
    BaseListModelView, BaseBulkActionView, SearchableViewMixin, TableView,
)

# Handlers
from django_fusion.core.handlers import PageHandler

# Services
from django_fusion.core.services import Service

# Models
from django_fusion.core.models import BaseModel

# Views
from django_fusion.web.views import FilterMixin, SearchMixin

# Cache
from django_fusion.comp.cache import get_component_map_cache
from django_fusion.core.cache import get_cache, cache_key

# Analyzer (Component scanning & tracking)
from django_fusion.analyzer import scanner, parser

# Configuration
from django_fusion.config import DynaconfSettings
```

## Common Patterns

### Form Component with Validation

```python
class BlogCreateComponent(FormMixin, RoutableComponent):
    model = Blog
    form_class = BlogForm
    template_name = "pages/blog_form.html"
    route_path = "create/"
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.created_at = timezone.now()
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('app:blog:detail', args=[self.object.slug])
```

### List Component with Filtering

```python
class BlogListComponent(TableMixin, RoutableComponent):
    model = Blog
    template_name = "pages/blog_list.html"
    route_path = "blog/"
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
        return queryset
```

### Detail Component with Related Data

```python
class BlogDetailComponent(RoutableComponent):
    model = Blog
    template_name = "pages/blog_detail.html"
    route_path = "blog/<slug>/"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = self.get_object()
        context['related'] = Blog.objects.filter(
            category=context['post'].category
        ).exclude(id=context['post'].id)[:3]
        context['comments'] = context['post'].comments.all()
        return context
    
    def get_object(self):
        slug = self.kwargs.get('slug')
        return Blog.objects.get(slug=slug)
```

## Version Compatibility

| Version | Django | Python | Status |
|---------|--------|--------|--------|
| 2.0+ | 4.2+ | 3.10+ | Current |
| 1.x | 3.2+ | 3.8+ | Legacy |

## Related Documentation

- [COMPONENT_SYSTEM.md](./COMPONENT_SYSTEM.md) - Component concepts
- [ROUTING_SYSTEM.md](./ROUTING_SYSTEM.md) - URL routing
- [FORMS_TABLES_INTEGRATION.md](./FORMS_TABLES_INTEGRATION.md) - Forms & tables
- [INTEGRATION_EXAMPLES.md](./INTEGRATION_EXAMPLES.md) - Code examples

---

**Next**: Review [INTEGRATION_EXAMPLES.md](./INTEGRATION_EXAMPLES.md) for practical examples.

