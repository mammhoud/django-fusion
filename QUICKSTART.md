# Forms & Tables Integration Quick Start

30-second setup guide for using forms and tables with routes.

Paths in this file are relative to the django-fusion repository root, where the
package lives at `src/django_fusion/`.

> If `django-fusion` is checked out as a submodule of a larger workspace, the
> paths below are still relative to the *library* root — the library is a
> standalone package and never resolves against a surrounding repository.

## 1. Import Mixins

```python
from django_fusion.routes.components.routable import RoutableComponent
from django_fusion.fragments.forms import (
    FormMixin,
    FormTableMixin,
)
from django_fusion.fragments.tables import TableMixin
```

## 2. Create Component

### Option A: Just Forms

```python
class CreateUserComponent(RoutableComponent, FormMixin):
    route_name = "create_user"
    route_path = "create/"
    title = "Create User"
    form_name = "user"
    form_class = UserForm
    template_name = "users/create.html"
```

### Option B: Just Tables

```python
class UserListComponent(RoutableComponent, TableMixin):
    route_name = "user_list"
    route_path = ""
    title = "Users"
    table_name = "users"
    model = User
    template_name = "users/list.html"

    def get_queryset(self):
        return User.objects.all()
```

### Option C: Both (Search + List)

```python
class UserManagementComponent(RoutableComponent, FormTableMixin):
    route_name = "users"
    route_path = ""
    title = "User Management"
    form_name = "search"
    table_name = "users"
    form_class = SearchForm
    model = User
    template_name = "users/manage.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_form_table_context_data())
        return context
```

## 3. Template Resolution

Two things compose here, and it is worth keeping them separate.

**The mixin returns a short name chain.** `FormMixin` returns exactly two names:

```text
components/form/<form_name>.html    # your form-specific template
components/form/form.html           # framework fallback
```

`TableMixin` returns two as well:

```text
plugins/tables/<table_name>.html    # your table-specific template
components/table.html               # framework fallback
```

**Django's loader then resolves each name through your `DIRS`.** So a
site-specific override is a matter of putting a file earlier in the search path,
not of changing the chain:

```text
1. <your-project>/templates/components/form/user.html   ← override wins here
2. src/django_fusion/templates/components/form/user.html
3. src/django_fusion/templates/components/form/form.html
```

To customise, create the file at the path in step 1. If it is absent, the chain
falls through to the framework template. See DF-006 for the full logic.

## 4. Create Site Template (Optional)

```text
<your-project>/templates/components/form/user.html
```

## 5. Add to Application

```python
class AdminApp(Application):
    components = [
        CreateUserComponent,
        UserListComponent,
        UserManagementComponent,
    ]
```

## Template Examples

### Form Template

```html
{% load i18n %}
<form method="post">
    {% csrf_token %}
    {% for field in form %}
        {{ field.label_tag }}
        {{ field }}
        {% if field.errors %}
            <span>{{ field.errors.0 }}</span>
        {% endif %}
    {% endfor %}
    <button type="submit">Save</button>
</form>
```

### Table Template

```html
{% load i18n %}
<table>
    <thead>
        <tr>
            {% for header in table_headers %}
                <th>{{ header.label }}</th>
            {% endfor %}
        </tr>
    </thead>
    <tbody>
        {% for row in table_data %}
            <tr>
                {% for header in table_headers %}
                    <td>{{ row|get_item:header.key }}</td>
                {% endfor %}
            </tr>
        {% empty %}
            <tr><td>No data</td></tr>
        {% endfor %}
    </tbody>
</table>
```

### Search + List Template

```html
{% load i18n %}

<div class="management-page">
    <!-- Search Form -->
    <form method="get">
        {{ form.search }}
        <button type="submit">Search</button>
    </form>

    <!-- Results table: this is exactly the path the TableMixin chain expects. -->
    {% include "plugins/tables/users.html" %}
</div>
```

## Common Configuration

### Auto-Generate Headers from Model

```python
def get_table_headers(self):
    # Automatically generates from model fields
    return super().get_table_headers()
```

### Custom Headers

```python
def get_table_headers(self):
    return [
        {"label": "Username", "key": "username", "sortable": True},
        {"label": "Email",    "key": "email",    "sortable": True},
        {"label": "Active",   "key": "is_active", "sortable": False},
    ]
```

### Filter Table Data

```python
def get_table_data(self):
    qs = super().get_queryset()
    search = self.request.GET.get('search')
    if search:
        qs = qs.filter(username__icontains=search)
    return list(qs)
```

### Custom Form Initialization

```python
def get_form_kwargs(self):
    kwargs = super().get_form_kwargs()
    kwargs['initial'] = {'user': self.request.user}
    return kwargs
```

## Key Attributes

### FormMixin

| Attribute | Type | Purpose |
|-----------|------|---------|
| `form_name`  | str  | Used for template lookup |
| `form_class` | class | Form to instantiate |
| `form_kwargs` | dict | Kwargs for form init |

### TableMixin

| Attribute | Type | Purpose |
|-----------|------|---------|
| `table_name`    | str  | Used for template lookup |
| `table_headers` | list | Column configuration |
| `table_data`    | list | Table rows |

## Key Methods

### FormMixin

```python
get_form_name()              # Returns form template name
get_form_template_names()    # Returns template resolution list
get_form_class()             # Returns form class to use
get_form_kwargs()            # Returns form initialization kwargs
get_form()                   # Returns instantiated form
get_form_context_data()      # Returns context dict for template
```

### TableMixin

```python
get_table_name()             # Returns table template name
get_table_template_names()   # Returns template resolution list
get_table_headers()          # Returns column headers
get_table_data()             # Returns table rows
get_table_context_data()     # Returns context dict for template
```

### FormTableMixin

```python
get_form_table_context_data() # Returns merged form+table context
```

## Next: Full Documentation

- [DF-006 — Forms & Tables full reference](./docs/06-forms-and-tables.md)
- [DF-012 — Integration examples](./docs/12-integration-examples.md)
- [DF-000 — Documentation index](./docs/INDEX.md)
