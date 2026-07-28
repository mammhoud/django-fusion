# Django-Fusion Routing System

Complete guide to URL routing in django-fusion, covering how components map to URLs, routing hierarchy, and advanced patterns.

## Overview

Django-Fusion provides automatic URL generation from component definitions. Instead of manually writing URL patterns, you define components with `route_path` values and django-fusion generates the URLs for you.

## Core Concepts

### Route Path

A `route_path` defines where a component is accessible:

```python
from django_fusion.comp.routes import RoutableComponent

class WelcomeComponent(RoutableComponent):
    route_path = ""              # Maps to /
    
class BlogListComponent(RoutableComponent):
    route_path = "blog/"         # Maps to /blog/
    
class BlogDetailComponent(RoutableComponent):
    route_path = "blog/<slug>/"  # Maps to /blog/SLUG/
```

### URL Namespace Hierarchy

URLs are generated with a three-level namespace structure:

```
Site Namespace (e.g., "vresume")
└── Application Namespace (e.g., "blog")
    └── Component URL (e.g., "blog/my-post/")
```

**Full URL**: `vresume:blog:blog_detail` → `/blog/my-post/`

### Route Types

**1. Static Routes** (no parameters)
```python
route_path = ""              # /
route_path = "about/"        # /about/
route_path = "blog/"         # /blog/
```

**2. Path Parameters**
```python
route_path = "blog/<slug>/"           # /blog/my-post/
route_path = "items/<int:id>/"        # /items/123/
route_path = "user/<str:username>/"   # /user/john/
```

**3. Nested Routes**
```python
route_path = "admin/users/"           # /admin/users/
route_path = "admin/users/<int:id>/"  # /admin/users/123/
```

## Component Routing

### RoutableComponent

Maps a full page view to a URL:

```python
from django_fusion.comp.routes import RoutableComponent

class BlogListComponent(RoutableComponent):
    route_path = "blog/"
    template_name = "pages/blog_list.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = Blog.objects.all()
        return context
```

**Generated URL**: `/blog/` (using default naming)

### FragmentComponent

Maps a fragment endpoint for HTMX requests:

```python
from django_fusion.comp.routes import FragmentComponent

class PostDetailFragment(FragmentComponent):
    route_path = "blog/<slug>/"
    fragment_name = "blog.fragments.post_detail"
    template_name = "fragments/post_detail.html"
```

**Generated URL**: `/blog/SLUG/` returns HTML fragment

## Application Architecture

### Single Application

```python
from django_fusion.comp.routes import Site, Application, RoutableComponent

class HomePage(RoutableComponent):
    route_path = ""
    
class AboutPage(RoutableComponent):
    route_path = "about/"

site = Site(
    name="main",
    applications=[
        Application(
            name="pages",
            components=[HomePage, AboutPage],
        )
    ]
)

# URLs generated:
# /
# /about/
```

### Multiple Applications

```python
site = Site(
    name="main",
    applications=[
        Application(name="pages", components=[HomePage, AboutPage]),
        Application(name="blog", components=[BlogList, BlogDetail]),
        Application(name="portfolio", components=[ProjectList, ProjectDetail]),
    ]
)

# URLs generated:
# /
# /about/
# /blog/
# /blog/<slug>/
# /portfolio/
# /portfolio/<int:id>/
```

### Application Namespaces

Each application gets its own namespace:

```python
# Access via reverse():
reverse('main:pages:home')           # /
reverse('main:blog:list')            # /blog/
reverse('main:blog:detail', args=['my-post'])  # /blog/my-post/

# In templates:
{% url 'main:blog:detail' post.slug %}
```

## Routing Hierarchy

### Three-Level Structure

```
Site
├── vresume
    ├── Application: pages
    │   ├── HomePage (route_path = "")
    │   │   URL: /
    │   │   Name: vresume:pages:home
    │   │
    │   └── AboutPage (route_path = "about/")
    │       URL: /about/
    │       Name: vresume:pages:about
    │
    ├── Application: blog
    │   ├── BlogList (route_path = "blog/")
    │   │   URL: /blog/
    │   │   Name: vresume:blog:list
    │   │
    │   └── BlogDetail (route_path = "blog/<slug>/")
    │       URL: /blog/SLUG/
    │       Name: vresume:blog:detail
    │
    └── Application: portfolio
        ├── ProjectList (route_path = "portfolio/")
        │   URL: /portfolio/
        │   Name: vresume:portfolio:list
        │
        └── ProjectDetail (route_path = "portfolio/<int:id>/")
            URL: /portfolio/123/
            Name: vresume:portfolio:detail
```

## URL Registration

### In Django URLs

```python
from pages.routable_components import site

urlpatterns = [
    # Routable components MUST be before Wagtail catch-all
    path("", include((site.urls[0], site.urls[1]), namespace=site.urls[2])),
    
    # Wagtail pages (catches remaining URLs)
    path("", include(wagtail_urls)),
]
```

### URL Tuple Structure

`site.urls` returns a 3-tuple:

```python
site.urls[0]  # URLconf module
site.urls[1]  # App name (application namespace)
site.urls[2]  # Instance name (instance namespace)
```

## URL Reversal

### reverse() Function

Get URL from component name:

```python
from django.urls import reverse

# Simple URL
url = reverse('vresume:pages:home')
# Result: /

# URL with parameter
url = reverse('vresume:blog:detail', args=['my-post'])
# Result: /blog/my-post/

# Using kwargs
url = reverse('vresume:blog:detail', kwargs={'slug': 'my-post'})
# Result: /blog/my-post/
```

### In Templates

```html
{# Simple URL #}
<a href="{% url 'vresume:pages:home' %}">Home</a>

{# URL with parameter #}
<a href="{% url 'vresume:blog:detail' post.slug %}">{{ post.title }}</a>

{# Using kwargs #}
<a href="{% url 'vresume:blog:detail' slug=post.slug %}">{{ post.title }}</a>
```

## Parameter Types

### Django URL Converters

| Converter | Pattern | Example |
|-----------|---------|---------|
| `str` | String | `<str:username>` |
| `int` | Integer | `<int:id>` |
| `slug` | Slug | `<slug:slug>` |
| `uuid` | UUID | `<uuid:id>` |
| `path` | Path | `<path:rest>` |

### Usage

```python
class BlogDetail(RoutableComponent):
    # String parameter
    route_path = "posts/<str:title>/"
    
class UserProfile(RoutableComponent):
    # Integer parameter
    route_path = "users/<int:id>/"
    
class ArticleView(RoutableComponent):
    # Slug parameter
    route_path = "articles/<slug:slug>/"
    
class FileDownload(RoutableComponent):
    # Path parameter (with slashes)
    route_path = "files/<path:filepath>"
```

### Accessing Parameters

In your component view:

```python
class BlogDetail(RoutableComponent):
    route_path = "blog/<slug:slug>/"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs['slug']  # Access parameter
        context['post'] = Blog.objects.get(slug=slug)
        return context
```

## Advanced Routing

### Dynamic Route Paths

Build routes programmatically:

```python
class DynamicComponent(RoutableComponent):
    def get_route_path(self):
        return f"items/{self.item_id}/"
```

### Conditional Routing

Register components conditionally:

```python
from django.conf import settings

components = [HomePage, AboutPage]

if settings.ENABLE_BLOG:
    components.append(BlogList)
    components.append(BlogDetail)

app = Application(name="pages", components=components)
```

### Route Inheritance

Components can inherit and override routes:

```python
class BaseComponent(RoutableComponent):
    template_name = "pages/base.html"

class HomePage(BaseComponent):
    route_path = ""
    
class BlogPage(BaseComponent):
    route_path = "blog/"
    template_name = "pages/blog.html"  # Override template
```

## Fragment Routing

### Fragment Names

Fragments map route paths to fragment identifiers:

```python
class PostDetailFragment(FragmentComponent):
    route_path = "blog/<slug>/"
    fragment_name = "blog.fragments.post_detail"
```

**URL**: `/blog/SLUG/`
**Fragment ID**: `blog.fragments.post_detail`

### Fragment Detection

Detect if request is for a fragment:

```python
from django_fusion.comp.routes import FragmentDetector

class PostDetail(RoutableComponent):
    route_path = "blog/<slug>/"
    
    def get_template_names(self):
        detector = FragmentDetector(self.request)
        if detector.is_fragment_request():
            # Return fragment template
            return ["fragments/post_detail.html"]
        # Return full page template
        return ["pages/post_detail.html"]
```

## URL Organization

### By Application

Group components in applications by feature:

```
blog_app = Application(
    name="blog",
    components=[
        BlogListComponent,
        BlogDetailComponent,
        BlogCreateComponent,
        BlogUpdateComponent,
        BlogDeleteComponent,
    ]
)
```

### By Feature

Organize routes by feature:

```python
# User management routes
class UserList(RoutableComponent):
    route_path = "users/"

class UserDetail(RoutableComponent):
    route_path = "users/<int:id>/"

class UserCreate(RoutableComponent):
    route_path = "users/create/"

class UserUpdate(RoutableComponent):
    route_path = "users/<int:id>/edit/"

class UserDelete(RoutableComponent):
    route_path = "users/<int:id>/delete/"

# Result URLs:
# /users/
# /users/123/
# /users/create/
# /users/123/edit/
# /users/123/delete/
```

## Best Practices

### 1. Keep Routes Simple

```python
# ✅ Good: Clear, predictable routes
route_path = "blog/"
route_path = "blog/<slug>/"

# ❌ Avoid: Complex nested routes
route_path = "admin/dashboard/reports/<int:id>/export/<str:format>/"
```

### 2. Use Consistent Naming

```python
# ✅ Good: Consistent naming
class UserListComponent:
    route_path = "users/"

class UserDetailComponent:
    route_path = "users/<int:id>/"

# ❌ Avoid: Inconsistent naming
class AllUsersComponent:
    route_path = "user-list/"

class SingleUserComponent:
    route_path = "user/<int:id>/"
```

### 3. Organization by Application

```python
# ✅ Good: Grouped by feature
blog_app = Application(
    name="blog",
    components=[BlogList, BlogDetail, BlogCreate]
)

admin_app = Application(
    name="admin",
    components=[AdminDashboard, UserManagement]
)

# ❌ Avoid: Everything in one application
main_app = Application(
    name="main",
    components=[BlogList, BlogDetail, AdminDashboard, UserManagement, ...]
)
```

### 4. Use URL Reversals

```html
{# ✅ Good: Use reverse for links #}
<a href="{% url 'vresume:blog:detail' post.slug %}">{{ post.title }}</a>

{# ❌ Avoid: Hardcoded URLs #}
<a href="/blog/{{ post.slug }}/">{{ post.title }}</a>
```

### 5. Handle Missing Routes Gracefully

```python
# Include Wagtail or other catch-all after routes
urlpatterns = [
    # Routable components first
    path("", include((site.urls[0], site.urls[1]), namespace=site.urls[2])),
    
    # Wagtail pages (catches remaining)
    path("", include(wagtail_urls)),
]
```

## Troubleshooting

### Issue: Routes not generating

**Check:**
1. Is Site properly initialized?
2. Are components registered with Application?
3. Is Application registered with Site?

**Fix:**
```python
site = Site(
    name="mysite",
    applications=[
        Application(name="blog", components=[BlogList, BlogDetail])
    ]
)
```

### Issue: URL reversing fails

**Check:**
1. Are namespaces correct? (site:app:component)
2. Are parameters passed correctly?
3. Does component have route_path?

**Fix:**
```python
# Correct: site:app:component
reverse('vresume:blog:list')
reverse('vresume:blog:detail', args=['slug'])

# Incorrect patterns to avoid
reverse('blog:list')  # Missing site namespace
reverse('blog_detail', args=['slug'])  # Using incorrect name
```

### Issue: Routes conflict with Wagtail

**Check:**
1. Are routable components registered BEFORE Wagtail?
2. Does route_path match page slug?

**Fix:**
```python
# Correct order
urlpatterns = [
    # Routable components FIRST
    path("", include((site.urls[0], site.urls[1]), namespace=site.urls[2])),
    
    # Wagtail LAST
    path("", include(wagtail_urls)),
]
```

## Related Documentation

- [ARCHITECTURE_OVERVIEW.md](./ARCHITECTURE_OVERVIEW.md) - System architecture
- [COMPONENT_SYSTEM.md](./COMPONENT_SYSTEM.md) - Component types
- [FRAGMENT_COMPONENTS.md](./FRAGMENT_COMPONENTS.md) - Fragment routing
- [INTEGRATION_EXAMPLES.md](./INTEGRATION_EXAMPLES.md) - Real examples

---

**Next**: Read [COMPONENT_SYSTEM.md](./COMPONENT_SYSTEM.md) for component details.

