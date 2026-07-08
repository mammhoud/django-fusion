# Django-Fusion Best Practices

Guidelines and patterns for building maintainable, scalable applications with django-fusion.

## Code Organization

### 1. File Structure

Organize your project logically:

```
myapp/
├── routable_components.py    # Component definitions
├── forms.py                  # Form classes
├── services.py               # Business logic
├── models.py                 # Django models
├── migrations/               # Database migrations
├── tests/                    # Tests
├── templates/                # App templates
│   ├── pages/               # Full page templates
│   └── components/          # Component templates
└── assets/
    └── templates/           # Asset templates
```

### 2. Component Organization

Group components by feature:

```python
# ✅ Good: Organized by feature
class BlogListComponent(RoutableComponent):
    """Display blog posts list."""
    route_path = "blog/"

class BlogDetailComponent(RoutableComponent):
    """Display single blog post."""
    route_path = "blog/<slug>/"

class BlogCreateComponent(FormMixin, RoutableComponent):
    """Create new blog post."""
    route_path = "blog/create/"

# Group in application
blog_app = Application(
    name="blog",
    components=[BlogListComponent, BlogDetailComponent, BlogCreateComponent],
)
```

## Component Design

### 1. Single Responsibility Principle

Each component should have one clear purpose:

```python
# ✅ Good: Single responsibility
class UserListComponent(TableMixin, RoutableComponent):
    """Display list of users."""
    route_path = "users/"
    
    def get_queryset(self):
        return User.objects.all()

class UserDetailComponent(RoutableComponent):
    """Display user profile."""
    route_path = "users/<int:id>/"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = User.objects.get(id=self.kwargs['id'])
        return context

# ❌ Avoid: Too many responsibilities
class UserManagementComponent(RoutableComponent):
    """User list, detail, create, edit, delete, export, import..."""
    # This does too much!
```

### 2. Keep Components Thin

Move business logic to services:

```python
# ✅ Good: Logic in service
class UserService:
    @staticmethod
    def get_active_users(search=None):
        queryset = User.objects.filter(is_active=True)
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(email__icontains=search)
            )
        return queryset

class UserListComponent(TableMixin, RoutableComponent):
    route_path = "users/"
    
    def get_queryset(self):
        return UserService.get_active_users(
            search=self.request.GET.get('search')
        )

# ❌ Avoid: Logic in component
class UserListComponent(TableMixin, RoutableComponent):
    def get_queryset(self):
        # Complex filtering logic in component
        queryset = User.objects.filter(is_active=True)
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(email__icontains=search)
            )
        # ... more complex logic
        return queryset
```

### 3. Use Mixins for Reusability

Create custom mixins for common patterns:

```python
# ✅ Good: Reusable mixin
class FilterByUserMixin:
    """Filter queryset by current user."""
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)

class MyComponent(FilterByUserMixin, RoutableComponent):
    model = MyModel

# ❌ Avoid: Duplicated logic
class Component1(RoutableComponent):
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

class Component2(RoutableComponent):
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)
```

## Template Best Practices

### 1. Template Organization

Follow the template hierarchy:

```
Base Template (base.html)
└── Layout Template (layout/default.html)
    └── Page Template (pages/blog_list.html)
        └── Component Templates (components/form/search.html)
```

**Implementation:**

```html
{# base.html #}
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}{% endblock %}</title>
</head>
<body>
    {% block content %}{% endblock %}
</body>
</html>

{# layout/default.html #}
{% extends "base.html" %}
{% block content %}
    <header>Navigation</header>
    {% block main %}{% endblock %}
    <footer>Footer</footer>
{% endblock %}

{# pages/blog_list.html #}
{% extends "layout/default.html" %}
{% block main %}
    {% include "components/form/search.html" %}
    {% include "components/table/table.html" %}
{% endblock %}
```

### 2. Use Tracking Attributes

Add tracking for component analysis:

```html
{# ✅ Good: Tracked component #}
<div data-component-id="blog_list" data-tracked="true">
    
    <section data-section="page-header">
        <h1>Blog Posts</h1>
    </section>
    
    <section data-section="filters">
        {% include "components/form/search.html" %}
    </section>
    
    <section data-section="results">
        {% include "components/table/table.html" %}
    </section>
    
    <section data-section="pagination">
        {% include "components/pagination.html" %}
    </section>
</div>

{# ❌ Avoid: Untracked components #}
<div>
    <div>Blog Posts</div>
    {# ... content without tracking #}
</div>
```

### 3. Template Cascade

Follow the cascade pattern for template lookups:

```python
class BlogListComponent(TableMixin, RoutableComponent):
    def get_template_names(self):
        # Cascade: site-specific → shared → fallback
        return [
            # Site-specific
            "vresume/blog/list.html",
            # App-specific
            "blog/list.html",
            # Shared
            "pages/list.html",
            # Fallback
            "list.html",
        ]
```

## URL Routing Best Practices

### 1. Consistent Naming

Use consistent patterns for route paths:

```python
# ✅ Good: Consistent RESTful pattern
class ResourceListComponent(RoutableComponent):
    route_path = "resource/"

class ResourceCreateComponent(RoutableComponent):
    route_path = "resource/create/"

class ResourceDetailComponent(RoutableComponent):
    route_path = "resource/<int:id>/"

class ResourceUpdateComponent(RoutableComponent):
    route_path = "resource/<int:id>/edit/"

class ResourceDeleteComponent(RoutableComponent):
    route_path = "resource/<int:id>/delete/"

# ❌ Avoid: Inconsistent naming
route_path = "items/"              # List
route_path = "item/add/"           # Create
route_path = "item_detail/<id>/"   # Detail
route_path = "update-item/<id>/"   # Update
```

### 2. URL Reversals in Templates

Use `{% url %}` tag instead of hardcoding:

```html
{# ✅ Good: Using URL reversal #}
<a href="{% url 'vresume:blog:list' %}">Blog</a>
<a href="{% url 'vresume:blog:detail' post.slug %}">{{ post.title }}</a>
<a href="{% url 'vresume:blog:edit' post.id %}">Edit</a>

{# ❌ Avoid: Hardcoded URLs #}
<a href="/blog/">Blog</a>
<a href="/blog/{{ post.slug }}/">{{ post.title }}</a>
<a href="/blog/{{ post.id }}/edit/">Edit</a>
```

### 3. Handle URL Conflicts

Mount routable components before catch-all routes:

```python
# ✅ Good: Correct order
urlpatterns = [
    # Routable components FIRST
    path("", include((site.urls[0], site.urls[1]), namespace=site.urls[2])),
    
    # Wagtail pages LAST (catch-all)
    path("", include(wagtail_urls)),
]

# ❌ Avoid: Wrong order (Wagtail catches everything)
urlpatterns = [
    path("", include(wagtail_urls)),  # Catch-all first!
    path("", include((site.urls[0], site.urls[1]), namespace=site.urls[2])),
]
```

## Form Handling Best Practices

### 1. Form Validation

Implement proper validation:

```python
# ✅ Good: Comprehensive validation
class ContactFormComponent(FormMixin, RoutableComponent):
    form_class = ContactForm
    template_name = "forms/contact.html"
    
    def form_valid(self, form):
        # Validate custom logic
        if not self.validate_captcha():
            form.add_error(None, "Captcha verification failed")
            return self.form_invalid(form)
        
        # Process form
        try:
            # Send email
            send_contact_email(form.cleaned_data)
            messages.success(self.request, "Message sent successfully!")
            return redirect('home')
        except Exception as e:
            messages.error(self.request, "Error sending message")
            return self.form_invalid(form)
```

### 2. Success URL Handling

Always implement get_success_url():

```python
# ✅ Good: Dynamic success URL
def get_success_url(self):
    return reverse('app:detail', args=[self.object.id])

# ❌ Avoid: Static redirect
def form_valid(self, form):
    self.object = form.save()
    return redirect('/success/')  # Hardcoded!
```

## Performance Best Practices

### 1. Optimize Queries

Use select_related and prefetch_related:

```python
# ✅ Good: Optimized queries
class PostListComponent(TableMixin, RoutableComponent):
    def get_queryset(self):
        return Post.objects.select_related(
            'author',
            'category',
        ).prefetch_related(
            'tags',
            'comments',
        ).filter(published=True)

# ❌ Avoid: N+1 queries
class PostListComponent(TableMixin, RoutableComponent):
    def get_queryset(self):
        return Post.objects.filter(published=True)
        # Each post will trigger additional queries for author, tags, etc.
```

### 2. Implement Caching

Cache expensive operations:

```python
# ✅ Good: Cached data
from django.views.decorators.cache import cache_page

class StatsComponent(RoutableComponent):
    @cache_page(60 * 15)  # Cache for 15 minutes
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Expensive calculation cached
        context['stats'] = self.get_cached_stats()
        return context
```

### 3. Pagination

Always paginate large datasets:

```python
# ✅ Good: Paginated results
class PostListComponent(TableMixin, RoutableComponent):
    paginate_by = 20  # Limit page size
    
    def get_queryset(self):
        return Post.objects.all().order_by('-created_at')

# ❌ Avoid: Loading all data
class PostListComponent(RoutableComponent):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = Post.objects.all()  # Could be thousands!
        return context
```

## Security Best Practices

### 1. Permission Checks

Always check user permissions:

```python
# ✅ Good: Permission check
class AdminComponent(RoutableComponent):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied("Admin access required")
        return super().dispatch(request, *args, **kwargs)

# ❌ Avoid: No permission check
class AdminComponent(RoutableComponent):
    # Anyone can access!
    pass
```

### 2. Input Validation

Always validate user input:

```python
# ✅ Good: Input validation
class SearchComponent(SearchableViewMixin, RoutableComponent):
    def get_queryset(self):
        search = self.request.GET.get('q', '').strip()
        
        # Validate input
        if not search or len(search) < 2:
            return Post.objects.none()
        
        if len(search) > 100:
            return Post.objects.none()
        
        # Safe to search
        return Post.objects.filter(title__icontains=search)

# ❌ Avoid: No validation
class SearchComponent(RoutableComponent):
    def get_context_data(self, **kwargs):
        search = self.request.GET.get('q')
        # Vulnerable to injection!
        context['results'] = Post.objects.filter(title__icontains=search)
```

### 3. CSRF Protection

Always include CSRF token in forms:

```html
{# ✅ Good: CSRF token included #}
<form method="post" action="{% url 'app:create' %}">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Submit</button>
</form>

{# ❌ Avoid: Missing CSRF token #}
<form method="post" action="{% url 'app:create' %}">
    {{ form.as_p }}
    <button type="submit">Submit</button>
</form>
```

## Testing Best Practices

### 1. Test Components

Write tests for component logic:

```python
from django.test import TestCase, Client
from django.urls import reverse

class BlogListComponentTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.post = Post.objects.create(
            title="Test Post",
            slug="test-post",
        )
    
    def test_list_component_renders(self):
        response = self.client.get(reverse('vresume:blog:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Post")
    
    def test_pagination_works(self):
        # Create 30 posts
        for i in range(30):
            Post.objects.create(title=f"Post {i}", slug=f"post-{i}")
        
        response = self.client.get(reverse('vresume:blog:list'))
        self.assertEqual(len(response.context['object_list']), 20)
```

### 2. Test Forms

Test form validation:

```python
class ContactFormTests(TestCase):
    def test_valid_form(self):
        form = ContactForm(data={
            'name': 'John Doe',
            'email': 'john@example.com',
            'message': 'Test message',
        })
        self.assertTrue(form.is_valid())
    
    def test_invalid_email(self):
        form = ContactForm(data={
            'name': 'John',
            'email': 'invalid-email',
            'message': 'Message',
        })
        self.assertFalse(form.is_valid())
```

## Deployment Best Practices

### 1. Settings Configuration

Use environment-based settings:

```python
# settings.py
import os

DEBUG = os.environ.get('DEBUG', False) == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
    }
}

# Fusion settings
FUSION_CACHE_TIMEOUT = int(os.environ.get('FUSION_CACHE_TIMEOUT', 3600))
```

### 2. Static Files

Properly configure static files:

```python
# settings.py
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Whitenoise for static file serving
MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # ... other middleware
]
```

### 3. Media Files

Configure media handling:

```python
# settings.py
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# In urls.py
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

## Documentation Best Practices

### 1. Document Components

Add docstrings to components:

```python
class BlogListComponent(TableMixin, RoutableComponent):
    """
    Display paginated list of published blog posts.
    
    URL: /blog/
    Template: pages/blog_list.html
    Context:
        - posts: Paginated list of Blog objects
        - page_obj: Current page object
        - is_paginated: Whether results are paginated
    """
    route_path = "blog/"
    template_name = "pages/blog_list.html"
    paginate_by = 20
```

### 2. Docstring Format

Use standard Python docstring format:

```python
def get_queryset(self):
    """
    Get published blog posts, ordered by creation date.
    
    Returns:
        QuerySet: Filtered and ordered Blog objects
    
    Example:
        queryset = component.get_queryset()
        # Returns: <QuerySet [<Blog: Post 1>, <Blog: Post 2>, ...]>
    """
```

## Checklist for New Components

- [ ] Single responsibility principle applied
- [ ] Proper URL routing configured
- [ ] Template organized and tracked
- [ ] Context data prepared correctly
- [ ] Forms validated and handled
- [ ] Permissions checked
- [ ] Query optimization done
- [ ] Error handling implemented
- [ ] Tests written
- [ ] Documentation added
- [ ] Code reviewed
- [ ] Deployed to staging first

## Related Documentation

- [COMPONENT_SYSTEM.md](./COMPONENT_SYSTEM.md) - Component concepts
- [ROUTING_SYSTEM.md](./ROUTING_SYSTEM.md) - URL routing
- [TEMPLATE_STRUCTURE.md](./TEMPLATE_STRUCTURE.md) - Template organization
- [INTEGRATION_EXAMPLES.md](./INTEGRATION_EXAMPLES.md) - Real examples

---

**Next**: Read [INTEGRATION_EXAMPLES.md](./INTEGRATION_EXAMPLES.md) for practical patterns.

