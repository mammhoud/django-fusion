# Routes Module

Declarative, class-based URL routing with integrated forms, tables, and template cascading.

## Components

### Base Routing
- **Viewset**: Class-based URL routing with automatic URL generation
- **BaseViewset**: Foundation for nested routing with parent/child relationships
- **Route**: URL pattern descriptor
- **route()**: Decorator for method-based routing
- **menu_path()**: Create menu items from routes

### Routable Components
- **RoutableComponent**: Full-page views registered in Site/Application hierarchy
- **FragmentComponent**: HTMX fragment-aware views with partial rendering

#### Fragment Name Resolution

Every routable component has a ``get_fragment_name()`` method that returns the
dotted fragment identifier. The resolution order is:

1. If ``fragment_name`` is explicitly set on the class, it is returned as-is.
2. Otherwise, a default is derived from ``route_name``::

       route_name = "dashboard"
       # → get_fragment_name() returns "components.dashboard"
       # → template: "components/dashboard.html"

This default links the component to the package's ``components/`` template
directory (``src/django_fusion/templates/components/``), which is registered
via ``APP_DIRS`` and ``COMPONENT_DIRS`` in the project template configuration.

The dotted string maps to a template path by replacing dots with slashes and
appending ``.html``::

    "profile.blog"  →  "profile/blog.html"

Both ``template_name`` and ``fragment_name`` work together:
- ``template_name``: Full-page template (used when ``strategy == "document"``)
- ``fragment_name`` (or ``get_fragment_name()``): Fragment template (used when
  ``strategy == "fragment"``, i.e. HTMX/Unpoly requests)

If neither is set, ``template_name`` defaults to ``base_page.html``.

### Forms & Tables
- **FormMixin**: Render forms with template cascading
- **TableMixin**: Render tables with data binding
- **FormTableMixin**: Combine form and table in one component
- **TemplateResolverMixin**: Intelligent template path resolution

### Model Viewsets
- **ModelViewset**: Full CRUD operations for models
- **ReadonlyModelViewset**: Read-only model operations
- Mixins: CreateViewMixin, UpdateViewMixin, DeleteViewMixin, DetailViewMixin

### Site Structure
- **Site**: Root of routing hierarchy
- **Application**: Nested application under Site
- **AppMenuMixin**: Menu integration for applications

### Fragment Detection
- **FragmentComponent**: Base for HTMX partial rendering
- **FragmentDetector**: Identifies fragment requests
- **add_fragment_detection_to_request()**: Middleware utility

## Quick Start

### Basic Routing

```python
from django_fusion.routes.components.routable import RoutableComponent

class DashboardComponent(RoutableComponent):
    route_name = "dashboard"
    route_path = "dashboard/"
    title = "Dashboard"
    template_name = "dashboard.html"
    # fragment_name defaults to "components.dashboard"
    # → resolves to "components/dashboard.html" for HTMX requests
```

Explicit fragment override:

```python
class ProfileComponent(RoutableComponent):
    route_name = "profile"
    route_path = "profile/"
    template_name = "profile/detail.html"
    fragment_name = "profile.fragments.detail"
    # → "profile/fragments/detail.html" for HTMX requests
```

### Form Component

```python
from django_fusion.routes.components.routable import RoutableComponent
from django_fusion.fragments.forms import FormMixin

class UserCreateComponent(RoutableComponent, FormMixin):
    route_name = "user_create"
    route_path = "users/create/"
    title = "Create User"
    form_name = "user"
    model = User
    form_class = UserForm
    template_name = "users/create.html"
```

### Table Component

```python
from django_fusion.routes.components.routable import RoutableComponent
from django_fusion.fragments.tables import TableMixin

class UserListComponent(RoutableComponent, TableMixin):
    route_name = "user_list"
    route_path = "users/"
    title = "Users"
    table_name = "users"
    model = User
    template_name = "users/list.html"
    
    def get_queryset(self):
        return User.objects.all()
```

### Combined Form & Table

```python
from django_fusion.routes.components.routable import RoutableComponent
from django_fusion.fragments.forms import FormTableMixin

class UserManagementComponent(RoutableComponent, FormTableMixin):
    route_name = "users_manage"
    route_path = "users/manage/"
    title = "User Management"
    form_name = "search"
    table_name = "users"
    template_name = "users/manage.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_form_table_context_data())
        return context
```

## Template Cascade

Templates are resolved from the consuming project's configured template
``DIRS`` and installed apps. Project and shared-asset templates can override
package defaults without importing or copying route implementations.

The package-owned templates live under ``src/django_fusion/templates``:

### Form Templates
- ``components/form/{form_name}.html`` — site-specific or shared form override
- ``components/form/form.html`` — canonical generic form
- ``components/form/form_field.html`` — canonical field renderer

### Component Templates
- ``fusion/components/...`` — legacy-compatible component template namespace
- ``components/...`` — canonical component namespace for new templates

Route implementations are organized by responsibility under
``django_fusion.routes``: ``core`` (base routing and sites), ``components``
(routable/fragment views), ``models`` (CRUD viewsets), ``pages`` (page
handlers/views), ``http`` (request/response helpers), and ``rendering``.
Import from those concrete modules rather than relying on a package-level
route barrel.

## Documentation

- [Forms & Tables Integration](../../docs/FORMS_TABLES_INTEGRATION.md)
- [Routable Components Guide](../../docs/ROUTABLE_COMPONENTS.md)
- [Template Resolution Strategy](../../docs/TEMPLATE_RESOLUTION.md)

## File Organization

```
django_fusion/routes/
├── __init__.py                  # Documentation only; no aggregate exports
├── core/
│   ├── base.py                  # BaseViewset, Viewset, Route, descriptors
│   ├── converters.py            # URL converters
│   └── sites.py                 # Site, Application, AppMenuMixin
├── components/
│   ├── routable.py              # RoutableComponent
│   ├── fragments.py             # FragmentComponent
│   └── dual_mode.py             # Dual rendering mixins
├── models/
│   ├── base.py                  # BaseModelViewset
│   └── crud.py                  # CRUD viewsets and mixins
├── pages/
│   ├── handler.py               # ComponentViews and PageHandler
│   ├── views.py                 # Wagtail page views
│   └── paginators.py            # Pagination helpers
├── http/
│   ├── detection.py             # Fragment detection
│   ├── response.py              # Response helpers
│   └── notifications.py         # Notification mixins
└── rendering/
    ├── renderers.py             # Rendering pipeline
    └── template_resolver.py     # Template resolution
```

## Integration Paths

### With RoutableComponent

```python
class MyComponent(RoutableComponent, FormMixin):
    # URL routing from RoutableComponent
    # Form rendering from FormMixin
    pass
```

### With Application

```python
class MyApplication(Application):
    components = [
        UserCreateComponent,
        UserListComponent,
        UserManagementComponent,
    ]
```

### With Site

```python
class MyApp(Site):
    namespace = "myapp"
    apps = [MyApplication]
```

## See Also

- Django-fusion Component System
- Template Tag Reference (`laces` / `components`)
- Middleware Integration (SiteMiddleware)
