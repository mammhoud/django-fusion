# Forms & Tables Integration Examples

Practical examples showing how to integrate forms and tables with routes in real applications.

## Example 1: Simple User List

### Component Definition

```python
# applications/lms_demo/www/users/routable_components.py
from django.contrib.auth.models import User
from django_fusion.comp.routes import RoutableComponent, TableMixin

class UserListComponent(RoutableComponent, TableMixin):
    route_name = "user_list"
    route_path = "users/"
    title = "User Management"
    table_name = "users"
    model = User
    template_name = "users/list.html"
    permission_required = "auth.view_user"
    
    def get_queryset(self):
        return User.objects.all().order_by('-date_joined')
    
    def get_table_headers(self):
        return [
            {"label": "Username", "key": "username", "sortable": True},
            {"label": "Email", "key": "email", "sortable": True},
            {"label": "Full Name", "key": "get_full_name", "sortable": False},
            {"label": "Joined", "key": "date_joined", "sortable": True},
            {"label": "Active", "key": "is_active", "sortable": True},
        ]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_table_context_data())
        return context
```

### Site Template Override

Create `applications/lms_demo/templates/plugins/tables/users.html`:

```html
{% load i18n %}

<div class="users-list-container">
    <div class="table-toolbar">
        <h2>{{ title }}</h2>
        <a href="{% url 'admin:users_create' %}" class="btn btn-primary">
            {% trans "Add User" %}
        </a>
    </div>

    {% include "plugins/tables/table.html" %}
</div>
```

### Shared Asset Template

Create `applications/assets/templates/plugins/tables/users.html` as the site-agnostic default:

```html
{% load i18n %}

<table class="table table-users">
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
        {% for user in table_data %}
            <tr data-user-id="{{ user.id }}">
                <td><strong>{{ user.username }}</strong></td>
                <td>{{ user.email }}</td>
                <td>{{ user.get_full_name|default:"-" }}</td>
                <td>{{ user.date_joined|date:"SHORT_DATE_FORMAT" }}</td>
                <td>
                    {% if user.is_active %}
                        <span class="badge bg-success">Active</span>
                    {% else %}
                        <span class="badge bg-secondary">Inactive</span>
                    {% endif %}
                </td>
            </tr>
        {% empty %}
            <tr><td colspan="5" class="text-center text-muted">No users found</td></tr>
        {% endfor %}
    </tbody>
</table>
```

### Template Resolution

When rendered:
1. Check: `applications/lms_demo/templates/plugins/tables/users.html` ✓ Found
2. Use site-specific template

If not found:
1. Check: `applications/assets/templates/plugins/tables/users.html` ✓ Found
2. Use shared template

If not found:
1. Check: `django_fusion/comp/routes/templates/routable_components/tables/table.html` ✓ Found
2. Use generic fallback

---

## Example 2: User Creation Form

### Component Definition

```python
# applications/lms_demo/www/users/routable_components.py
from django import forms
from django.contrib.auth.models import User
from django_fusion.comp.routes import RoutableComponent, FormMixin

class UserCreateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
    
    def clean(self):
        if self.cleaned_data['password'] != self.cleaned_data['password_confirm']:
            raise forms.ValidationError("Passwords don't match")
        return self.cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class UserCreateComponent(RoutableComponent, FormMixin):
    route_name = "user_create"
    route_path = "users/create/"
    title = "Create User"
    form_name = "user"
    model = User
    form_class = UserCreateForm
    template_name = "users/create.html"
    permission_required = "auth.add_user"
    
    def get_success_url(self):
        messages.success(self.request, f"User {self.object.username} created successfully")
        return self.reverse("user_list")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_form_context_data())
        return context
```

### Site Template Override

Create `applications/lms_demo/templates/components/form/user.html`:

```html
{% load i18n %}

<div class="user-form-container">
    <h2>{{ title }}</h2>
    
    <form method="post" class="form-user">
        {% csrf_token %}
        
        <div class="form-section">
            <h3>Account Information</h3>
            {{ form.username }}
            {{ form.email }}
        </div>
        
        <div class="form-section">
            <h3>Personal Information</h3>
            {{ form.first_name }}
            {{ form.last_name }}
        </div>
        
        <div class="form-section">
            <h3>Password</h3>
            {{ form.password }}
            {{ form.password_confirm }}
        </div>
        
        <div class="form-actions">
            <button type="submit" class="btn btn-primary">
                {% trans "Create User" %}
            </button>
            <a href="{% url 'user_list' %}" class="btn btn-secondary">
                {% trans "Cancel" %}
            </a>
        </div>
    </form>
</div>
```

---

## Example 3: User Management with Search

### Component Definition

```python
# applications/lms_demo/www/users/routable_components.py
from django import forms
from django.contrib.auth.models import User
from django.db.models import Q
from django_fusion.comp.routes import RoutableComponent, FormTableMixin

class UserSearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search by username or email...',
            'class': 'form-control'
        })
    )
    is_active = forms.BooleanField(
        required=False,
        label="Active Users Only"
    )

class UserManagementComponent(RoutableComponent, FormTableMixin):
    route_name = "user_manage"
    route_path = "users/manage/"
    title = "User Management"
    form_name = "user_search"
    table_name = "users"
    model = User
    form_class = UserSearchForm
    template_name = "users/manage.html"
    permission_required = "auth.view_user"
    
    def get_queryset(self):
        qs = User.objects.all()
        
        # Apply search filter if provided
        search = self.request.GET.get('search')
        if search:
            qs = qs.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        
        # Apply active filter
        if self.request.GET.get('is_active'):
            qs = qs.filter(is_active=True)
        
        return qs.order_by('-date_joined')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pre-fill form with current GET params
        kwargs['data'] = self.request.GET or None
        return kwargs
    
    def get_table_headers(self):
        return [
            {"label": "Username", "key": "username", "sortable": True, "width": "150px"},
            {"label": "Email", "key": "email", "sortable": True, "width": "200px"},
            {"label": "Status", "key": "is_active", "sortable": True, "width": "100px"},
            {"label": "Joined", "key": "date_joined", "sortable": True, "width": "120px"},
            {"label": "Actions", "key": "id", "sortable": False, "width": "100px"},
        ]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Merge both form and table context
        context.update(self.get_form_table_context_data())
        return context
```

### Template

Create `applications/lms_demo/templates/users/manage.html`:

```html
{% extends "base.html" %}
{% load i18n %}

{% block content %}
<div class="user-management-page">
    <header class="page-header">
        <h1>{{ title }}</h1>
    </header>
    
    <!-- Search Form -->
    <section class="search-section">
        <form method="get" class="search-form">
            <div class="form-row">
                <div class="form-col">
                    {{ form.search }}
                </div>
                <div class="form-col">
                    <label>{{ form.is_active }}</label>
                    {{ form.is_active.label_tag }}
                </div>
                <div class="form-col actions">
                    <button type="submit" class="btn btn-primary">
                        {% trans "Search" %}
                    </button>
                    <a href="?reset" class="btn btn-secondary">
                        {% trans "Clear" %}
                    </a>
                </div>
            </div>
        </form>
    </section>
    
    <!-- Results Table -->
    <section class="results-section">
        {% include "plugins/tables/users.html" %}
    </section>
</div>
{% endblock %}
```

---

## Example 4: Shared Template with Site Overrides

### Shared Template

`applications/assets/templates/plugins/tables/users.html`:

```html
{% load i18n %}

<div class="table-wrapper">
    <table class="table">
        <thead>
            <tr>
                {% for header in table_headers %}
                    <th style="{% if header.width %}width: {{ header.width }}{% endif %}">
                        {{ header.label }}
                    </th>
                {% endfor %}
            </tr>
        </thead>
        <tbody>
            {% for user in table_data %}
                <tr>
                    <td>{{ user.username }}</td>
                    <td>{{ user.email }}</td>
                    <td>
                        {% if user.is_active %}
                            <span class="badge">Active</span>
                        {% else %}
                            <span class="badge inactive">Inactive</span>
                        {% endif %}
                    </td>
                    <td>{{ user.date_joined|date:"SHORT_DATE_FORMAT" }}</td>
                    <td>
                        <a href="{% url 'user_edit' user.id %}" class="btn-small">Edit</a>
                        <a href="{% url 'user_delete' user.id %}" class="btn-small">Delete</a>
                    </td>
                </tr>
            {% empty %}
                <tr><td colspan="5" class="empty">No users found</td></tr>
            {% endfor %}
        </tbody>
    </table>
</div>
```

### CTC Research Override

`applications/ctc_research/templates/plugins/tables/users.html`:

```html
{% load i18n %}

<div class="users-table-ctc">
    <table class="table modern">
        <thead>
            <tr>
                {% for header in table_headers %}
                    <th>{{ header.label }}</th>
                {% endfor %}
            </tr>
        </thead>
        <tbody>
            {% for user in table_data %}
                <tr class="user-row {% if not user.is_active %}inactive{% endif %}">
                    <td class="username">
                        <strong>{{ user.username }}</strong>
                    </td>
                    <td class="email">
                        <a href="mailto:{{ user.email }}">{{ user.email }}</a>
                    </td>
                    <td class="status">
                        <span class="status-badge {% if user.is_active %}active{% else %}inactive{% endif %}">
                            {{ user.is_active|yesno:"Active,Inactive" }}
                        </span>
                    </td>
                    <td class="date">{{ user.date_joined|date:"d M Y" }}</td>
                    <td class="actions">
                        <div class="action-buttons">
                            <button class="btn-edit" data-user-id="{{ user.id }}">Edit</button>
                            <button class="btn-delete" data-user-id="{{ user.id }}">Delete</button>
                        </div>
                    </td>
                </tr>
            {% empty %}
                <tr><td colspan="5" class="no-data">No users found</td></tr>
            {% endfor %}
        </tbody>
    </table>
</div>
```

### LMS Demo Override

`applications/lms_demo/templates/plugins/tables/users.html`:

```html
{% load i18n %}

<div class="lms-users-list">
    <div class="table-toolbar">
        <div class="table-stats">
            Total: <strong>{{ table_data|length }}</strong>
        </div>
    </div>
    
    <table class="table lms-table">
        <thead>
            <tr>
                {% for header in table_headers %}
                    <th>{{ header.label }}</th>
                {% endfor %}
            </tr>
        </thead>
        <tbody>
            {% for user in table_data %}
                <tr data-user="{{ user.id }}">
                    <td>{{ user.username }}</td>
                    <td>{{ user.email }}</td>
                    <td>
                        <span class="status" data-status="{% if user.is_active %}active{% else %}inactive{% endif %}">
                            {% if user.is_active %}Active{% else %}Inactive{% endif %}
                        </span>
                    </td>
                    <td>{{ user.date_joined|date:"d/m/Y" }}</td>
                    <td>
                        <button class="action-menu-btn" data-user-id="{{ user.id }}">⋮</button>
                    </td>
                </tr>
            {% empty %}
                <tr><td colspan="5" class="empty-state">No users in system</td></tr>
            {% endfor %}
        </tbody>
    </table>
</div>
```

---

## Integration Checklist

When integrating forms/tables with routes:

- [ ] Define component with `RoutableComponent` base
- [ ] Add `FormMixin` and/or `TableMixin`
- [ ] Set `route_name`, `route_path`, `title`
- [ ] Set `form_name`/`table_name` for template resolution
- [ ] Define `template_name` for full-page rendering
- [ ] Override `get_form_class()` or set `form_class`
- [ ] Override `get_queryset()` for tables
- [ ] Override `get_table_headers()` for custom columns
- [ ] Implement `get_context_data()` to inject mixins' context
- [ ] Create site-specific template override (optional)
- [ ] Create shared asset template as fallback (optional)
- [ ] Test template resolution cascade
- [ ] Add permission checks if needed

## Template Priority Hints

- Use **site-specific** templates for site branding/UX
- Use **asset templates** for common patterns across sites
- Rely on **django-fusion** templates for minimal styling
- Keep **form_name/table_name** generic for reusability

