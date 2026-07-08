# Getting Started with Django-Fusion

Quick start guide to get you building with django-fusion in 5-10 minutes.

## What is Django-Fusion?

Django-Fusion is a framework for building modern Django applications with:
- **Component-based architecture** - Organize code into reusable components
- **Template routing** - Map components to URLs automatically
- **Form & table rendering** - Integrated form/table system with templates
- **HTMX support** - Fragment-based partial page updates
- **Multi-site support** - Manage multiple sites in one codebase

## Installation

```bash
# Add to your Django project
pip install django-fusion

# Add to INSTALLED_APPS
INSTALLED_APPS = [
    # ...
    'django_fusion',
    'django_fusion.comp',
    # ...
]
```

## 5-Minute Quick Start

### 1. Define a Component

Create `pages/routable_components.py`:

```python
from django_fusion.comp.routes import Site, Application, RoutableComponent

class WelcomeComponent(RoutableComponent):
    """Simple welcome page component."""
    route_path = ""  # Maps to /
    template_name = "pages/welcome.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Welcome to Django-Fusion"
        return context

# Create Site with Application
welcome_app = Application(
    name="welcome",
    label="Welcome",
    components=[WelcomeComponent],
)

site = Site(
    name="mysite",
    applications=[welcome_app],
)
```

### 2. Create a Template

Create `templates/pages/welcome.html`:

```html
{% extends "base.html" %}

{% block title %}{{ title }}{% endblock %}

{% block content %}
    <div data-component-id="welcome" data-tracked="true">
        <h1>{{ title }}</h1>
        <p>Welcome to your first django-fusion application!</p>
    </div>
{% endblock %}
```

### 3. Register URLs

In your `urls.py`:

```python
from pages.routable_components import site

urlpatterns = [
    # ... other URLs
    path("", include((site.urls[0], site.urls[1]), namespace=site.urls[2])),
]
```

### 4. Run and View

```bash
python manage.py runserver
# Visit http://localhost:8000/
```

That's it! You have a working django-fusion component.

## Next: Add a List Component

### 1. Create a Model

```python
from django.db import models

class Blog(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
```

### 2. Create a List Component

```python
from django.views.generic import ListView
from django_fusion.comp.routes import RoutableComponent, FormMixin, TableMixin
from blogs.models import Blog

class BlogListComponent(FormMixin, TableMixin, RoutableComponent):
    """List all blog posts."""
    route_path = "blog/"
    template_name = "pages/blog_list.html"
    
    model = Blog
    paginate_by = 10
    
    def get_table_data(self):
        """Return data for table rendering."""
        return self.get_queryset()
```

### 3. Create Template

```html
{% extends "base.html" %}
{% load i18n %}

{% block content %}
    <div data-component-id="blog_list" data-tracked="true">
        
        {# Header #}
        <section data-section="page-header">
            <h1>{% trans "Blog Posts" %}</h1>
        </section>
        
        {# Search form #}
        <section data-section="filters">
            {% include "components/form/search.html" %}
        </section>
        
        {# Results table #}
        <section data-section="results">
            {% include "components/table/table.html" %}
        </section>
        
        {# Pagination #}
        <section data-section="pagination">
            {% include "components/pagination/pagination.html" %}
        </section>
    </div>
{% endblock %}
```

## Understanding the Architecture

### Component Hierarchy

```
Site (mysite)
├── Application (welcome)
│   ├── WelcomeComponent
│   │   route_path: ""
│   │   URL: /
│   │
│   └── BlogApp
│       ├── BlogListComponent
│       │   route_path: "blog/"
│       │   URL: /blog/
│       │
│       └── BlogDetailComponent
│           route_path: "blog/<slug>/"
│           URL: /blog/<slug>/
```

### URL Generation

Django-Fusion auto-generates URLs from your component definitions:
- `route_path = ""` → `/`
- `route_path = "blog/"` → `/blog/`
- `route_path = "blog/<slug>/"` → `/blog/SLUG/`

### Template Organization

Your templates are organized in layers:

```
Base Template (base.html)
├── Layout Template (layout/main.html)
│   └── Page Template (pages/blog_list.html)
│       └── Component Templates (components/form/search.html)
```

## Key Concepts

### 1. RoutableComponent
- Maps a URL path to a template
- Renders full page views
- Can include forms and tables

### 2. FragmentComponent
- Renders partial content via HTMX
- Returns page fragments instead of full pages
- Used for modal dialogs and inline updates

### 3. FormMixin
- Adds form rendering to components
- Cascades template lookups (site → shared → fallback)
- Provides form context automatically

### 4. TableMixin
- Adds table rendering to components
- Provides pagination support
- Includes column and row rendering

### 5. Application
- Groups related components
- Organizes navigation
- Can have multiple components with different routes

### 6. Site
- Top-level container
- Multiple applications
- Single URL namespace

## Template Tracking

Add `data-section` attributes to track template parts:

```html
{# Header section #}
<section data-section="page-header">
    <h1>{{ title }}</h1>
</section>

{# Form section #}
<section data-section="filters">
    {% include "components/form/search.html" %}
</section>

{# Results section #}
<section data-section="results">
    {% include "components/table/table.html" %}
</section>
```

Use the [Component Analyzer](./COMPONENT_ANALYZER.md) to track and analyze your components.

## Common Patterns

### Pattern 1: CRUD Operations

```python
class ItemListComponent(TableMixin, RoutableComponent):
    route_path = "items/"
    model = Item
    
class ItemCreateComponent(FormMixin, RoutableComponent):
    route_path = "items/create/"
    model = Item
    
class ItemDetailComponent(RoutableComponent):
    route_path = "items/<int:pk>/"
    model = Item
```

### Pattern 2: Search & Filter

```python
class SearchComponent(FormMixin, TableMixin, RoutableComponent):
    route_path = "search/"
    
    def get_table_data(self):
        queryset = Item.objects.all()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(title__icontains=query)
        return queryset
```

### Pattern 3: Modal Dialogs

```python
class ItemCreateModalComponent(FragmentComponent):
    fragment_name = "items.modals.create"
    
    def get_context_data(self, **kwargs):
        return {'form': ItemForm()}
```

## What's Next?

1. **Read the full [Architecture Overview](./ARCHITECTURE_OVERVIEW.md)**
2. **Explore [Component System](./COMPONENT_SYSTEM.md)**
3. **Review [Routing System](./ROUTING_SYSTEM.md)**
4. **Study [Integration Examples](./INTEGRATION_EXAMPLES.md)**
5. **Learn [Forms & Tables](./FORMS_TABLES_INTEGRATION.md)**

## Common Questions

**Q: Can I mix RoutableComponent and Wagtail pages?**
A: Yes! Both can coexist at the same root path.

**Q: How do I use HTMX with django-fusion?**
A: Use `FragmentComponent` for HTMX endpoints. See [Fragment Components](./FRAGMENT_COMPONENTS.md).

**Q: Where should I put my templates?**
A: Follow [Template Structure](./TEMPLATE_STRUCTURE.md) for organization.

**Q: How do I share components across sites?**
A: See [Integration Examples](./INTEGRATION_EXAMPLES.md) → "Multi-Site Customization".

## Troubleshooting

### Component not found
- Check `route_path` is correct
- Verify component is registered in Application
- Check URLs are included in `urlpatterns`

### Template not rendering
- Verify `template_name` path is correct
- Check template exists in templates directory
- Review [Template Structure](./TEMPLATE_STRUCTURE.md)

### Forms not submitting
- Check form has `method="POST"` and `{% csrf_token %}`
- Verify component has form handling logic
- See [EXAMPLES_FORMS](./EXAMPLES_FORMS.md)

## Support

- **Issues**: Check [Troubleshooting Guide](./TROUBLESHOOTING.md)
- **Questions**: See [FAQ](./FAQ.md)
- **Examples**: Review [INTEGRATION_EXAMPLES](./INTEGRATION_EXAMPLES.md)

---

**Next**: Read [Architecture Overview](./ARCHITECTURE_OVERVIEW.md) for deeper understanding.

