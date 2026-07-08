# Django-Fusion Architecture Overview

Complete guide to the dual-routing system: **Page Router** (Wagtail) vs **Component Router** (django-fusion).

## Two Routing Systems

Django-Fusion provides two complementary routing systems for different use cases:

### 1. Page Router (Wagtail CMS)

Content-driven, hierarchy-based routing for static and dynamic content pages.

```
Wagtail Page Tree (CMS)
├── Home Page (/)
├── About (/about/)
├── Blog (/blog/)
│   └── Blog Post (/blog/my-post/)
├── Services (/services/)
└── Contact (/contact/)
```

**Characteristics:**
- Hierarchical page tree in Wagtail admin
- Managed through CMS UI
- Slug-based URLs
- SEO-friendly
- Best for: Content pages, blog posts, landing pages

### 2. Component Router (django-fusion)

Programmatic, application-based routing for app functionality and dashboards.

```
Component Routes (Python)
├── /blog/list/           (BlogListComponent)
├── /blog/create/         (BlogCreateComponent)
├── /admin/users/         (UserListComponent)
├── /admin/users/create/  (UserCreateComponent)
└── /portfolio/list/      (ProjectListComponent)
```

**Characteristics:**
- Declared in Python code (Site → Application → Component)
- Programmatic structure
- RESTful URLs
- Class-based views
- Best for: Admin panels, app functionality, dashboards

## Architecture Comparison

| Aspect | Page Router (Wagtail) | Component Router (django-fusion) |
|--------|----------------------|----------------------------------|
| **Base Path** | `/` (root) | `/` (root) |
| **Structure** | Hierarchical tree | Flat applications |
| **Management** | CMS UI | Python code |
| **URL Pattern** | Slug-based | RESTful |
| **Rendering** | Page model + template | Component class |
| **Use Case** | Content pages | App functionality |
| **Example** | `/blog/my-post/` | `/blog/list/` |

## Three-Level Component Hierarchy

### Level 1: Site (Root)

The top-level container for all applications.

```python
class VResumeSite(Site):
    title = "VResume"
    icon = "view_comfy"
    menu_template_name = "components/menu/site_menu.html"
```

**Responsibilities:**
- Groups related applications
- Manages namespace and routing
- Provides site-level configuration

### Level 2: Application (Namespace)

Groups related components by feature/domain.

```python
class BlogApp(Application):
    title = "Blog"
    icon = "article"
    menu_template_name = "components/menu/app_menu.html"
    
    # Components within this app
```

**Responsibilities:**
- Groups related components
- Creates URL namespace (e.g., `/blog/`)
- Manages menu structure
- Provides app-level configuration

### Level 3: Component (View)

Individual routable views for specific functionality.

```python
class BlogListComponent(RoutableComponent):
    route_name = "blog-list"
    route_path = "list/"
    title = "Blog Posts"
    template_name = "blog/list.html"
```

**Responsibilities:**
- Renders individual views
- Handles specific URL pattern
- Manages component-level logic
- Provides context data

## Full Hierarchy Example

```
VResumeSite (Site)
├── BlogApp (Application)
│   ├── BlogListComponent (route_path="list/")
│   │   URL: /blog/list/
│   │   View: Lists all blog posts
│   │
│   └── BlogDetailComponent (route_path="<slug>/")
│       URL: /blog/my-post/
│       View: Shows single blog post
│
└── PortfolioApp (Application)
    ├── ProjectListComponent (route_path="list/")
    │   URL: /portfolio/list/
    │   View: Lists all projects
    │
    └── ProjectDetailComponent (route_path="<slug>/")
        URL: /portfolio/my-project/
        View: Shows single project
```

## URL Generation from Hierarchy

Component path = Application name + route_path

```
BlogApp.BlogListComponent
  Application name: "blog" (from app class name, lowercase)
  route_path: "list/"
  ─────────────────────
  Generated URL: /blog/list/

BlogApp.BlogDetailComponent
  Application name: "blog"
  route_path: "<slug>/"
  ─────────────────────
  Generated URL: /blog/<slug>/
```

## Component Types

### RoutableComponent

Full-page view in the routing hierarchy.

```python
class UserListComponent(RoutableComponent):
    route_name = "user_list"
    route_path = "users/"
    title = "Users"
    template_name = "users/list.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = User.objects.all()
        return context
```

**Features:**
- Full-page rendering
- Template support
- Context data injection
- Permission checking
- Breadcrumb generation

### FragmentComponent

HTMX/Unpoly partial view component.

```python
class BlogListFragment(FragmentComponent):
    route_name = "blog-list-fragment"
    route_path = "list-fragment/"
    fragment_name = "blog.fragments.post_list"
    paginate_by = 10
    
    def get_queryset(self):
        return BlogPost.objects.filter(status="published")
```

**Features:**
- Fragment template support
- HTMX auto-detection
- Partial rendering
- Pagination support
- OOB (out-of-band) fragments

## Coexistence at Root Level

Both systems share the root path `/`:

```
Request to: /blog/list/
1. Check component routes → MATCH: BlogListComponent
2. Return component response

Request to: /about/
1. Check component routes → NO MATCH
2. Check Wagtail pages → MATCH: About page
3. Return page response

Request to: /invalid/
1. Check component routes → NO MATCH
2. Check Wagtail pages → NO MATCH
3. Return 404
```

**Critical Load Order:**
1. Component routes registered FIRST
2. Wagtail catch-all comes AFTER
3. Django checks in order: component → page → 404

## Implementation in urls.py

```python
# applications/<site>/www/core/urls.py

from pages.routable_components import vresume_site
from django.urls import include, path

# Step 1: Mount component routes at root (CHECKED FIRST)
urlpatterns = [
    path("", include((
        vresume_site.urls[0],      # URL patterns
        vresume_site.urls[1],      # App name
        vresume_site.urls[2]       # Namespace
    )))
]

# Step 2: Mount Wagtail pages (CHECKED SECOND, has catch-all)
from django.conf.urls.i18n import i18n_patterns
from wagtail import urls as wagtail_urls

urlpatterns += i18n_patterns(
    path("", include(wagtail_urls)),  # Catches unmatched routes
    prefix_default_language=False,
)
```

## When to Use Each System

### Use Page Router (Wagtail) for:

- Content pages (About, Services, Contact)
- Blog posts (if using Wagtail for blogging)
- Marketing pages
- FAQ sections
- Testimonial pages
- Any content-driven page

**Example:**
```
/about/
/services/
/blog/wagtail-post/
/contact/
```

### Use Component Router (django-fusion) for:

- Admin dashboards
- User management
- Data tables and lists
- Forms and input
- App functionality
- Dashboard analytics
- Settings pages

**Example:**
```
/admin/users/
/admin/users/create/
/dashboard/analytics/
/portfolio/list/
```

## Routing Resolution Flow

```
User Request: GET /blog/my-post/
    ↓
1. Check django-fusion Component Routes
   └─ Does "/blog/my-post/" match a component route?
      ├─ YES → Render BlogDetailComponent
      │        Return component response
      │        DONE ✓
      │
      └─ NO → Continue to step 2
    ↓
2. Check Wagtail Pages (in i18n_patterns)
   └─ Does "/blog/my-post/" match a Wagtail page?
      ├─ YES → Render Wagtail page
      │        Return page response
      │        DONE ✓
      │
      └─ NO → Continue to step 3
    ↓
3. Return 404 Not Found
```

## Namespace Hierarchy

Component namespaces follow the hierarchy:

```
blog:blog-list              ← BlogApp.BlogListComponent
blog:blog-detail            ← BlogApp.BlogDetailComponent
admin:user-list             ← AdminApp.UserListComponent
admin:user-create           ← AdminApp.UserCreateComponent
portfolio:project-list      ← PortfolioApp.ProjectListComponent
```

## Context Data Available

In component templates:

```django
{{ title }}                 {# From component.title #}
{{ page_title }}            {# From component.page_title or title #}
{{ breadcrumbs }}           {# Auto-generated from hierarchy #}
{{ icon }}                  {# From component.icon #}
{{ component }}             {# The component instance #}
```

## Permission Integration

Components support permission checking:

```python
class AdminComponent(RoutableComponent):
    permission_required = "auth.view_admin"  # Single permission
    # or
    permission_required = [                  # Multiple permissions
        "auth.view_admin",
        "auth.change_user",
    ]
    
    def has_permission(self, user):
        # Custom permission logic
        return user.is_staff
```

## Menu Integration

Components can appear in navigation menus:

```python
class BlogListComponent(AppMenuMixin, RoutableComponent):
    menu_label = "All Posts"
    show_in_menu = True
    menu_order = 10
```

## See Also

- [Component System Guide](./COMPONENT_SYSTEM.md)
- [Page Router Documentation](./PAGE_ROUTER.md)
- [Routable Components Guide](./ROUTABLE_COMPONENTS.md)
- [Forms & Tables Integration](./FORMS_TABLES_INTEGRATION.md)
- [Root Path Routing Structure](../FUSION_ROUTING_STRUCTURE.md)

