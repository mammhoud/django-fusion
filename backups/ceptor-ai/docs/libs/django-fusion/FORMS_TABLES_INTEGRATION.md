# Forms & Tables Integration with Routes

Comprehensive guide for integrating forms and tables into django-fusion routable components with template cascading.

## Overview

This integration provides:

- **FormMixin**: Render forms in routable components with intelligent template resolution
- **TableMixin**: Render tables with data binding and pagination
- **FormTableMixin**: Combine both for search forms above data tables
- **TemplateResolverMixin**: Intelligent template path resolution across site-specific, shared, and fallback paths

## Canonical Imports

```python
from django_fusion.comp.routes import (
    RoutableComponent,
    FormMixin,
    TableMixin,
    FormTableMixin,
    TemplateResolverMixin,
)
```

## Template Resolution Cascade

Templates are resolved in this priority order:

```
1. Site-specific templates     → applications/<site>/templates/
2. Shared asset templates      → applications/assets/templates/
3. Django-fusion fallback      → django_fusion/comp/routes/templates/
```

This allows each site to override shared templates while maintaining fallback to defaults.

## Basic Usage

### Simple Form Component

```python
from django import forms
from django_fusion.comp.routes import RoutableComponent, FormMixin

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)

class ContactComponent(FormMixin, RoutableComponent):
    route_path = "contact/"
    form_class = ContactForm
    template_name = "pages/contact.html"
    
    def form_valid(self, form):
        # Process form
        send_email(form.cleaned_data)
        messages.success(self.request, "Message sent!")
        return redirect('home')
```

**Template Resolution** (for `components/form/contact.html`):
- `applications/vresume/templates/components/form/contact.html`
- `applications/assets/templates/components/form/contact.html`
- `django_fusion/comp/routes/templates/routable_components/forms/form.html`

### Simple Table Component

```python
from django.contrib.auth.models import User
from django_fusion.comp.routes import RoutableComponent, TableMixin

class UserListComponent(TableMixin, RoutableComponent):
    route_path = "users/"
    model = User
    template_name = "pages/user_list.html"
    paginate_by = 25
    
    def get_queryset(self):
        return User.objects.all().order_by('-date_joined')
```

**Template Resolution** (for `components/table/user_list.html`):
- `applications/vresume/templates/components/table/user_list.html`
- `applications/assets/templates/components/table/user_list.html`
- `django_fusion/comp/routes/templates/routable_components/tables/table.html`

### Combined Form & Table

```python
from django.contrib.auth.models import User
from django_fusion.comp.routes import RoutableComponent, FormTableMixin

class UserManagementComponent(FormTableMixin, RoutableComponent):
    route_path = "users/manage/"
    model = User
    template_name = "pages/user_management.html"
    paginate_by = 20
    
    def get_queryset(self):
        qs = User.objects.all()
        # Apply filter from form if present
        search = self.request.GET.get('search')
        if search:
            qs = qs.filter(username__icontains=search)
        return qs.order_by('-date_joined')
        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Merge form and table context
        context.update(self.get_form_table_context_data())
        return context
```

## API Reference

### FormMixin

Provides form rendering with intelligent template resolution.

#### Attributes

- **form_name** (str | None): Base name for form templates
  - Default: Model name if available
  - Used to resolve: `components/form/{form_name}.html`

- **form_class** (type[Form] | None): Form class to instantiate
  - Must be provided or override `get_form_class()`

- **form_kwargs** (dict): Additional kwargs for form initialization
  - Example: `{"initial": {...}, "prefix": "user"}`

#### Methods

- **get_form_name()** → str
  - Returns the form template base name
  - Override to customize

- **get_form_template_names()** → list[str]
  - Returns cascading template names with fallbacks
  - Override for custom resolution

- **get_form_class()** → type[Form]
  - Returns the form class to instantiate
  - Must be overridden if `form_class` not set

- **get_form_kwargs()** → dict[str, Any]
  - Returns kwargs for form initialization
  - Override to customize form instantiation

- **get_form()** → Form
  - Instantiates and returns the form
  - Uses `get_form_class()` and `get_form_kwargs()`

- **get_form_context_data()** → dict[str, Any]
  - Returns context dict with `form` and `form_name`
  - Add to component's `get_context_data()` output

### TableMixin

Provides table rendering with data binding and headers.

#### Attributes

- **table_name** (str | None): Base name for table templates
  - Default: `{model_name}_table` if available
  - Used to resolve: `plugins/tables/{table_name}.html`

- **table_headers** (list[dict] | None): Column header configuration
  - Each header dict should have:
    - `label` (str): Display name
    - `key` (str): Data key to access
    - `sortable` (bool): Whether column is sortable
    - `width` (str, optional): CSS width

- **table_data** (list | None): Table rows
  - If None, calls `get_table_data()`

#### Methods

- **get_table_name()** → str
  - Returns table template base name

- **get_table_template_names()** → list[str]
  - Returns cascading template names

- **get_table_headers()** → list[dict[str, Any]]
  - Returns column headers configuration
  - Auto-generates from model fields if not set

- **get_table_data()** → list[Any]
  - Returns table data rows
  - Default: calls `get_queryset()` if available

- **get_table_context_data()** → dict[str, Any]
  - Returns context dict with `table_name`, `table_headers`, `table_data`

### FormTableMixin

Combined mixin inheriting from both FormMixin and TableMixin.

#### Methods

- **get_form_table_context_data()** → dict[str, Any]
  - Returns merged context from both form and table
  - Use in `get_context_data()`:
    ```python
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_form_table_context_data())
        return context
    ```

### TemplateResolverMixin

Intelligent template path resolution with cascade.

#### Methods

- **get_site_name()** → str | None
  - Returns current site identifier
  - Detects from resolver_match.namespace or viewset

- **get_template_names()** → list[str]
  - Returns cascaded template names for `template_name`
  - Resolution order:
    1. Site-specific path
    2. Asset path
    3. Django-fusion path

- **get_template_names_with_fallback(primary_names: list[str]) → list[str]
  - Applies cascade to multiple template names
  - Useful for Django's `get_template_names()` override

## Template Examples

### forms/form.html (Site Override)

```django
{% load i18n laces %}

<div class="custom-form-wrapper">
    <h2>{{ form_name|title }}</h2>
    
    <form method="post" class="form-modern">
        {% csrf_token %}
        {% for field in form %}
            {% if not field.is_hidden %}
                <div class="form-field">
                    {{ field.label_tag }}
                    {{ field }}
                    {% if field.errors %}
                        <span class="error">{{ field.errors.0 }}</span>
                    {% endif %}
                </div>
            {% endif %}
        {% endfor %}
        <button type="submit" class="btn-primary">Save</button>
    </form>
</div>
```

### plugins/tables/users.html (Site Override)

```django
{% load i18n %}

<div class="users-table-wrapper">
    <table class="table modern-table">
        <thead>
            <tr>
                {% for header in table_headers %}
                    <th class="{% if header.sortable %}sortable{% endif %}">
                        {{ header.label }}
                    </th>
                {% endfor %}
            </tr>
        </thead>
        <tbody>
            {% for row in table_data %}
                <tr data-user-id="{{ row.id }}">
                    <td>{{ row.username }}</td>
                    <td>{{ row.email }}</td>
                    <td>{{ row.date_joined|date:"SHORT_DATE_FORMAT" }}</td>
                </tr>
            {% empty %}
                <tr><td colspan="3" class="empty">No users found</td></tr>
            {% endfor %}
        </tbody>
    </table>
</div>
```

## File Organization

### Shared Templates (applications/assets/templates/)

```
applications/assets/templates/
├── components/form/
│   ├── form.html                    # Generic form
│   ├── user.html                    # User form
│   └── contact.html                 # Contact form
└── plugins/tables/
    ├── table.html                   # Generic table
    ├── users.html                   # Users table
    └── products.html                # Products table
```

### Site-Specific Overrides (applications/<site>/templates/)

```
applications/lms_demo/templates/
├── components/form/
│   └── user.html                    # Overrides shared user form
└── plugins/tables/
    └── users.html                   # Overrides shared users table
```

### Django-Fusion Fallbacks

```
django_fusion/comp/routes/templates/routable_components/
├── forms/
│   └── form.html                    # Generic form fallback
└── tables/
    └── table.html                   # Generic table fallback
```

## Advanced Usage

### Custom Headers with Computed Values

```python
def get_table_headers(self):
    return [
        {"label": "User", "key": "username", "sortable": True},
        {"label": "Status", "key": "is_active", "sortable": False},
        {"label": "Last Login", "key": "last_login", "sortable": True},
        {"label": "Actions", "key": "id", "sortable": False, "width": "150px"},
    ]
```

### Dynamic Form Initialization

```python
def get_form_kwargs(self):
    kwargs = super().get_form_kwargs()
    if self.request.method == 'POST':
        kwargs.update(self.request.POST)
    else:
        kwargs['initial'] = {'user': self.request.user}
    return kwargs
```

### Filtered Table with Search

```python
def get_table_data(self):
    qs = self.get_queryset()
    search = self.request.GET.get('search')
    if search:
        qs = qs.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search)
        )
    return list(qs[:50])  # Limit to 50 rows
```

### Multi-Site Customization

Each site can customize templates while maintaining shared defaults:

```
lms_demo/templates/plugins/tables/users.html
    → Specific styling for LMS

ctc_research/templates/plugins/tables/users.html
    → Specific styling for CTC

applications/assets/templates/plugins/tables/users.html
    → Shared default for all sites

django_fusion/.../table.html
    → Final fallback
```

## Best Practices

1. **Use shared templates** for common patterns (login forms, data tables)
2. **Override in assets** for site-wide customization
3. **Fall back to package templates** for minimal styling
4. **Keep form_name/table_name simple** for better caching and reuse
5. **Document custom headers** in component docstrings
6. **Use form prefixes** for multiple forms on same page
7. **Implement get_queryset()** for efficient data fetching
8. **Add pagination** for large tables (beyond 1000 rows)

## See Also

- [Routes Documentation](./ROUTES.md)
- [RoutableComponent Guide](./ROUTABLE_COMPONENTS.md)
- [Template Resolution Strategy](./TEMPLATE_RESOLUTION.md)
