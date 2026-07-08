# Django-Fusion FAQ

Frequently asked questions about django-fusion.

## Getting Started

### Q: What is django-fusion?

A: Django-Fusion is a framework that extends Django with:
- **Component-based routing** - Map components to URLs automatically
- **Template layers** - Organize templates hierarchically (base → layout → page → component)
- **Form & table rendering** - Built-in form and table components with templates
- **HTMX support** - Fragment components for partial page updates
- **Multi-site architecture** - Manage multiple sites in one codebase

### Q: Do I need to use django-fusion?

A: No. Django-Fusion is optional and adds structure. You can use:
- Pure Django class-based views
- Django REST Framework for APIs
- Combination of both with django-fusion

Django-Fusion is most useful for:
- Multi-site projects
- Heavy form/table use cases
- Template-driven development
- HTMX-based applications

### Q: Can I use django-fusion with Wagtail?

A: Yes! Both can coexist:
- Django-Fusion components handle specific routes
- Wagtail handles page hierarchy
- Both work at the root URL path

```python
urlpatterns = [
    # Routable components FIRST
    path("", include((site.urls[0], site.urls[1]), namespace=site.urls[2])),
    
    # Wagtail LAST (catch-all)
    path("", include(wagtail_urls)),
]
```

### Q: How does routing work in django-fusion?

A: Components define `route_path` attributes that map to URLs:

```python
class BlogList(RoutableComponent):
    route_path = "blog/"  # /blog/

class BlogDetail(RoutableComponent):
    route_path = "blog/<slug>/"  # /blog/my-post/
```

URLs are auto-generated. No need for manual URL patterns!

## Components

### Q: What's the difference between RoutableComponent and FragmentComponent?

A: 
- **RoutableComponent**: Renders full pages (GET, POST, etc.)
- **FragmentComponent**: Renders HTML fragments for HTMX requests

```python
# Full page
class ListPage(RoutableComponent):
    route_path = "list/"
    template_name = "pages/list.html"

# Fragment
class FilterFragment(FragmentComponent):
    route_path = "api/filter/"
    template_name = "fragments/filter.html"
```

### Q: How do I handle POST requests?

A: Use FormMixin:

```python
class ContactComponent(FormMixin, RoutableComponent):
    form_class = ContactForm
    template_name = "forms/contact.html"
    
    def form_valid(self, form):
        form.save()
        return redirect('success')
```

### Q: How do I access URL parameters?

A: Via `self.kwargs`:

```python
class DetailComponent(RoutableComponent):
    route_path = "posts/<slug>/"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs['slug']
        context['post'] = Post.objects.get(slug=slug)
        return context
```

### Q: Can I have nested applications?

A: Yes, create multiple applications in a site:

```python
site = Site(
    name="mysite",
    applications=[
        blog_app,
        portfolio_app,
        admin_app,
    ]
)
```

Each application groups related components.

### Q: How do I register components?

A: Create a `routable_components.py` file:

```python
from django_fusion.comp.routes import Site, Application, RoutableComponent

class HomePage(RoutableComponent):
    route_path = ""

site = Site(
    name="mysite",
    applications=[
        Application(name="pages", components=[HomePage])
    ]
)
```

Then include in URLs:

```python
path("", include((site.urls[0], site.urls[1]), namespace=site.urls[2]))
```

## Templates

### Q: How should I organize templates?

A: Follow the four-layer hierarchy:

```
Base (base.html)
└── Layout (layout/default.html)
    └── Page (pages/blog_list.html)
        └── Components (components/form/search.html)
```

See [TEMPLATE_STRUCTURE.md](./TEMPLATE_STRUCTURE.md) for details.

### Q: What are data-section attributes?

A: HTML attributes for tracking template sections:

```html
<div data-component-id="blog_list" data-tracked="true">
    <section data-section="page-header">
        <h1>Blog</h1>
    </section>
    
    <section data-section="filters">
        {% include "components/form/search.html" %}
    </section>
</div>
```

Used by the component analyzer to map and track components.

### Q: Where should I put shared templates?

A: In `applications/assets/templates/`:

```
applications/assets/templates/
├── base.html
├── layout/
│   └── default.html
├── components/
│   ├── form/
│   └── table/
└── shared/
```

Site-specific templates go in `<site>/templates/`.

### Q: How do I extend templates?

A: Use `{% extends %}`:

```html
{# pages/blog_list.html #}
{% extends "layout/default.html" %}

{% block main %}
    <h1>Blog Posts</h1>
    {% include "components/table/table.html" %}
{% endblock %}
```

### Q: Can I use dynamic template names?

A: Yes, override `get_template_names()`:

```python
def get_template_names(self):
    return [
        f"pages/{self.model._meta.model_name}_list.html",
        "pages/default_list.html",
    ]
```

Django will use the first one that exists.

## Forms & Tables

### Q: How do I render a form?

A: Use FormMixin:

```python
class ContactComponent(FormMixin, RoutableComponent):
    form_class = ContactForm
    template_name = "forms/contact.html"

# In template:
{{ form.as_p }}
```

### Q: How do I handle form validation errors?

A: FormMixin handles this automatically:

```python
def form_invalid(self, form):
    # Automatically re-renders form with errors
    context = self.get_context_data(form=form)
    return self.render_to_response(context)
```

Errors appear in templates via `{{ form.non_field_errors }}` and `{{ field.errors }}`.

### Q: How do I render a table?

A: Use TableMixin:

```python
class UserList(TableMixin, RoutableComponent):
    model = User
    template_name = "pages/user_list.html"
    paginate_by = 20
```

Provides paginated data automatically.

### Q: How do I add search functionality?

A: Use SearchableViewMixin:

```python
class SearchComponent(SearchableViewMixin, RoutableComponent):
    search_fields = ['title', 'content']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return self.apply_search_filter(queryset)
```

### Q: Can I combine forms and tables?

A: Yes, use both mixins:

```python
class UserManagement(FormMixin, TableMixin, RoutableComponent):
    model = User
    form_class = UserForm
    template_name = "pages/user_management.html"
    paginate_by = 20
```

## URL Routing

### Q: How do I reverse URLs?

A: Use Django's `reverse()` function:

```python
from django.urls import reverse

url = reverse('mysite:blog:detail', args=['my-post'])
# Result: /blog/my-post/
```

### Q: How do I use URLs in templates?

A: Use the `{% url %}` tag:

```html
<a href="{% url 'mysite:blog:list' %}">Blog</a>
<a href="{% url 'mysite:blog:detail' post.slug %}">{{ post.title }}</a>
```

### Q: What's the URL namespace structure?

A: Three levels:
1. **Site**: `mysite`
2. **Application**: `blog`
3. **Component**: `detail`

Full URL name: `mysite:blog:detail`

### Q: Can I use custom URL converters?

A: Yes, Django's built-in converters work:

```python
<int:id>      # Integer
<slug:slug>   # Slug
<uuid:id>     # UUID
<str:name>    # String
<path:rest>   # Path (includes slashes)
```

### Q: How do I handle URL conflicts with Wagtail?

A: Mount routable components BEFORE Wagtail:

```python
urlpatterns = [
    # Routable components FIRST
    path("", include((site.urls[0], site.urls[1]), namespace=site.urls[2])),
    
    # Wagtail LAST
    path("", include(wagtail_urls)),
]
```

## Performance

### Q: How do I optimize database queries?

A: Use `select_related` and `prefetch_related`:

```python
def get_queryset(self):
    return Post.objects.select_related(
        'author',
        'category',
    ).prefetch_related(
        'tags',
    )
```

### Q: How do I cache components?

A: Use Django's cache framework:

```python
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # 15 minutes
def get(self, request, *args, **kwargs):
    return super().get(request, *args, **kwargs)
```

### Q: How do I paginate results?

A: Set `paginate_by`:

```python
class ListComponent(TableMixin, RoutableComponent):
    paginate_by = 25
```

### Q: How do I improve template rendering?

A: 
- Use `select_related` / `prefetch_related`
- Cache expensive computations
- Use template tags for reusable logic
- Minimize template complexity

## HTMX & Fragments

### Q: How do I use HTMX with django-fusion?

A: Use FragmentComponent:

```python
class FilterFragment(FragmentComponent):
    route_path = "api/filter/"
    template_name = "fragments/filter_results.html"
```

In template:

```html
<form hx-post="{% url 'mysite:api:filter' %}">
    <!-- Form fields -->
</form>
<div hx-target="this"></div>
```

### Q: How do I detect fragment requests?

A: Use FragmentDetector:

```python
from django_fusion.comp.routes import FragmentDetector

def get_template_names(self):
    detector = FragmentDetector(self.request)
    if detector.is_fragment_request():
        return ["fragments/partial.html"]
    return ["pages/full.html"]
```

### Q: Can I use both full page and fragment responses?

A: Yes! Same component can return both:

```python
class PostDetail(RoutableComponent):
    route_path = "posts/<slug>/"
    
    def get_template_names(self):
        if FragmentDetector(self.request).is_fragment_request():
            return ["fragments/post_detail.html"]
        return ["pages/post_detail.html"]
```

## Troubleshooting

### Q: Components are not loading

A:
1. Check `FUSION_AUTO_DISCOVER = True`
2. Verify `routable_components.py` exists
3. Check URLs are registered
4. Review error logs

### Q: Templates not found

A:
1. Verify template path is correct
2. Check `TEMPLATES['DIRS']` includes template directories
3. Ensure template file exists
4. Check permissions on template files

### Q: URL reversal not working

A:
1. Check namespace is correct: `site:app:component`
2. Verify parameters match route pattern
3. Ensure component is registered

### Q: Forms not submitting

A:
1. Check form has `method="POST"`
2. Include `{% csrf_token %}`
3. Verify `form_valid()` is implemented
4. Check server logs for errors

### Q: HTMX requests failing

A:
1. Check endpoint returns HTML (not JSON)
2. Verify `fragment_name` is set
3. Check `HX-Request` header is present
4. Review network requests in browser

## Advanced

### Q: Can I create custom mixins?

A: Yes! Extend existing mixins:

```python
class MyCustomMixin:
    def get_queryset(self):
        queryset = super().get_queryset()
        # Add custom filtering
        return queryset.filter(owner=self.request.user)

class MyComponent(MyCustomMixin, RoutableComponent):
    pass
```

### Q: How do I add custom context?

A: Override `get_context_data()`:

```python
def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['extra_data'] = 'value'
    return context
```

### Q: Can I customize component discovery?

A: Set `FUSION_COMPONENTS_MODULE`:

```python
# settings.py
FUSION_COMPONENTS_MODULE = 'my_components'  # Instead of routable_components

# my_components.py
site = Site(...)
```

### Q: How do I add logging?

A: Use Python's logging module:

```python
import logging

logger = logging.getLogger(__name__)

class MyComponent(RoutableComponent):
    def get_context_data(self, **kwargs):
        logger.info("Loading component")
        return super().get_context_data(**kwargs)
```

## Migration & Upgrade

### Q: How do I upgrade django-fusion?

A: 
```bash
pip install --upgrade django-fusion
python manage.py migrate
```

Check release notes for breaking changes.

### Q: How do I migrate from manual URL patterns?

A:
1. Create components with `route_path`
2. Register in Site/Application
3. Include component URLs
4. Remove manual URL patterns

### Q: Is there a v1 to v2 migration guide?

A: See the release notes in the repository for migration steps.

## Support & Resources

### Q: Where do I get help?

A:
- Check this FAQ
- Read [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
- Review [INTEGRATION_EXAMPLES.md](./INTEGRATION_EXAMPLES.md)
- Check project documentation
- Search GitHub issues

### Q: How do I report a bug?

A: Report on GitHub with:
1. Minimal reproducible example
2. Django/Python versions
3. Error message and traceback
4. Steps to reproduce

### Q: Can I contribute to django-fusion?

A: Yes! See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

### Q: Where is the source code?

A: Django-Fusion is at: `applications/libs/django-fusion/`

---

**More questions?** Check [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for detailed problem-solving.

