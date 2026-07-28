# Django-Fusion Component System

Complete guide to the component system, covering component types, lifecycle, and patterns.

## What is a Component?

A component is a reusable, self-contained piece of your application that handles:
- URL routing
- Data loading
- Template rendering
- User interactions

Components combine Django's class-based views with django-fusion's routing system to create a more modular architecture.

## Component Types

### 1. RoutableComponent

Renders a full page view accessible via a URL.

```python
from django_fusion.comp.routes import RoutableComponent

class BlogListComponent(RoutableComponent):
    """Display list of blog posts."""
    route_path = "blog/"
    template_name = "pages/blog_list.html"
    paginate_by = 10
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = self.get_queryset()
        return context
    
    def get_queryset(self):
        return Blog.objects.all().order_by('-created_at')
```

**Usage:**
- List/detail views
- Form pages
- Dashboard pages
- Admin interfaces

**URL**: `/blog/`

### 2. FragmentComponent

Renders a partial page fragment for HTMX requests.

```python
from django_fusion.comp.routes import FragmentComponent

class PostDetailFragment(FragmentComponent):
    """Display single post details."""
    route_path = "blog/<slug>/"
    fragment_name = "blog.fragments.post_detail"
    template_name = "fragments/post_detail.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs['slug']
        context['post'] = Blog.objects.get(slug=slug)
        return context
```

**Usage:**
- Modal dialogs
- Partial updates
- HTMX-powered interactions
- Inline editing

**URL**: `/blog/SLUG/` (returns HTML fragment)

### 3. Viewset

Organizes multiple related components.

```python
from django_fusion.comp.routes import BaseViewset, route

class BlogViewset(BaseViewset):
    """Blog management viewset."""
    
    @route("blog/")
    def list(self, request):
        """List all posts."""
        
    @route("blog/create/")
    def create(self, request):
        """Create new post."""
        
    @route("blog/<slug>/")
    def detail(self, request, slug):
        """View single post."""
```

**Usage:**
- CRUD operations
- Resource management
- Batch operations

### 4. Model Viewsets

Pre-built viewsets for model CRUD.

```python
from django_fusion.comp.routes import ModelViewset, ReadonlyModelViewset

class BlogViewset(ModelViewset):
    """Full CRUD for Blog model."""
    model = Blog
    template_name = "pages/blog"  # Will try blog_list, blog_detail, blog_form
    paginate_by = 20

class ReadOnlyBlogViewset(ReadonlyModelViewset):
    """Read-only viewset for Blog."""
    model = Blog
```

**Provided Routes:**
- List view
- Detail view
- Create view
- Update view
- Delete view

## Component Hierarchy

### Site

Top-level container:

```python
from django_fusion.comp.routes import Site, Application

site = Site(
    name="mysite",
    label="My Site",
    applications=[...]
)
```

**Represents**: Entire site/application

### Application

Groups related components:

```python
from django_fusion.comp.routes import Application

blog_app = Application(
    name="blog",
    label="Blog",
    components=[BlogListComponent, BlogDetailComponent],
)
```

**Represents**: Feature or module

### Component

Individual page or endpoint:

```python
class BlogListComponent(RoutableComponent):
    route_path = "blog/"
```

**Represents**: Single URL/view

### Hierarchy Diagram

```
Site (mysite)
├── Application (blog)
│   ├── RoutableComponent (list)
│   │   URL: /blog/
│   │
│   ├── RoutableComponent (detail)
│   │   URL: /blog/<slug>/
│   │
│   └── RoutableComponent (create)
│       URL: /blog/create/
│
├── Application (portfolio)
│   ├── RoutableComponent (list)
│   │   URL: /portfolio/
│   │
│   └── RoutableComponent (detail)
│       URL: /portfolio/<int:id>/
│
└── Application (admin)
    ├── RoutableComponent (dashboard)
    │   URL: /admin/
    │
    └── RoutableComponent (users)
        URL: /admin/users/
```

## Component Lifecycle

### Request Processing

```
1. Request arrives at URL
   ↓
2. Django routes to component
   ↓
3. Component.dispatch() called
   ↓
4. HTTP method handler (get, post, etc.) called
   ↓
5. get_context_data() called to load data
   ↓
6. Template rendered with context
   ↓
7. Response returned to client
```

### Method Resolution Order

```python
class BlogListComponent(RoutableComponent):
    def dispatch(self, request, *args, **kwargs):
        """Entry point for all requests."""
        # Pre-processing
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        """Handle GET requests."""
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        """Prepare context for template."""
        context = super().get_context_data(**kwargs)
        context['posts'] = self.get_queryset()
        return context
    
    def get_template_names(self):
        """Determine template to render."""
        return [self.template_name]
    
    def get_queryset(self):
        """Load data from database."""
        return Blog.objects.all()
```

## Core Methods

### get_context_data()

Prepare data for the template:

```python
def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['posts'] = self.get_queryset()
    context['total_count'] = self.get_queryset().count()
    context['categories'] = Category.objects.all()
    return context
```

### get_queryset()

Load data from database:

```python
def get_queryset(self):
    queryset = Blog.objects.all()
    
    # Filter by category if provided
    category = self.request.GET.get('category')
    if category:
        queryset = queryset.filter(category__slug=category)
    
    # Filter by search term if provided
    search = self.request.GET.get('search')
    if search:
        queryset = queryset.filter(title__icontains=search)
    
    return queryset.order_by('-created_at')
```

### get_template_names()

Determine which template to use:

```python
def get_template_names(self):
    # Simple case: single template
    return [self.template_name]
    
    # Advanced: multiple template options
    return [
        f"pages/{self.model._meta.model_name}_list.html",
        "pages/default_list.html",
    ]
```

### dispatch()

Intercept all requests:

```python
def dispatch(self, request, *args, **kwargs):
    # Pre-processing (before view logic)
    
    # Check permissions
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Call original dispatch
    response = super().dispatch(request, *args, **kwargs)
    
    # Post-processing (after view logic)
    
    return response
```

## Mixins

### FormMixin

Add form rendering to components:

```python
from django_fusion.comp.routes import RoutableComponent, FormMixin

class BlogCreateComponent(FormMixin, RoutableComponent):
    route_path = "blog/create/"
    model = Blog
    form_class = BlogForm
    template_name = "pages/blog_form.html"
    
    def form_valid(self, form):
        """Handle form submission."""
        form.instance.author = self.request.user
        return super().form_valid(form)
```

**Provides:**
- Form rendering
- Template cascade
- Form validation
- Success/error handling

### TableMixin

Add table rendering to components:

```python
from django_fusion.comp.routes import RoutableComponent, TableMixin

class UserListComponent(TableMixin, RoutableComponent):
    route_path = "users/"
    model = User
    template_name = "pages/user_list.html"
    paginate_by = 25
    
    def get_table_data(self):
        """Return data for table."""
        return self.get_queryset()
```

**Provides:**
- Table rendering
- Pagination
- Sorting
- Filtering

### Combined Mixins

Use multiple mixins together:

```python
from django_fusion.comp.routes import (
    RoutableComponent,
    FormMixin,
    TableMixin,
)

class UserManagementComponent(FormMixin, TableMixin, RoutableComponent):
    """Display user list with search form."""
    route_path = "admin/users/"
    model = User
    template_name = "pages/user_management.html"
    
    def get_queryset(self):
        """Filter users by search."""
        queryset = super().get_queryset()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(email__icontains=search)
            )
        return queryset
```

## Component Properties

### Route Configuration

```python
class BlogDetailComponent(RoutableComponent):
    route_path = "blog/<slug>/"        # URL pattern
    name = "blog_detail"               # Component name
    label = "Blog Detail"              # Display name
    icon = "fas fa-newspaper"          # Icon
    show_in_menu = True                # Show in menu
```

### Template Configuration

```python
class BlogDetailComponent(RoutableComponent):
    template_name = "pages/blog_detail.html"  # Template to render
    
    def get_template_names(self):
        """Override template selection."""
        return [
            "pages/blog_detail.html",
            "pages/default_detail.html",
        ]
```

### Query Configuration

```python
class BlogListComponent(RoutableComponent):
    model = Blog                       # Model to query
    paginate_by = 10                  # Pagination size
    ordering = ['-created_at']        # Default ordering
    
    def get_queryset(self):
        """Custom query logic."""
        return super().get_queryset().filter(published=True)
```

## Request/Response Handling

### GET Requests

```python
class BlogListComponent(RoutableComponent):
    def get(self, request, *args, **kwargs):
        """Handle GET request."""
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = self.get_queryset()
        return context
```

### POST Requests

```python
class BlogCreateComponent(FormMixin, RoutableComponent):
    def post(self, request, *args, **kwargs):
        """Handle form submission."""
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)
    
    def form_valid(self, form):
        """Process valid form."""
        self.object = form.save()
        return redirect('blog:detail', slug=self.object.slug)
```

### Custom Responses

```python
class ExportComponent(RoutableComponent):
    def get(self, request, *args, **kwargs):
        """Export data as CSV."""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="data.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'Name', 'Email'])
        
        for user in self.get_queryset():
            writer.writerow([user.id, user.name, user.email])
        
        return response
```

## Accessing Component Data

### From Templates

```html
{# Access context data #}
{{ title }}
{{ posts }}

{# Access component instance #}
{{ view.request.user }}
{{ view.kwargs }}
{{ view.args }}
```

### From View

```python
# Access request
self.request.GET
self.request.POST
self.request.user

# Access URL parameters
self.kwargs['slug']
self.args

# Access component attributes
self.model
self.paginate_by
self.template_name
```

## Component Registration

### In Site

```python
from django_fusion.comp.routes import Site, Application, RoutableComponent

# Define components
class HomePage(RoutableComponent):
    route_path = ""

class AboutPage(RoutableComponent):
    route_path = "about/"

# Create application
pages_app = Application(
    name="pages",
    components=[HomePage, AboutPage],
)

# Create site
site = Site(
    name="mysite",
    applications=[pages_app],
)

# Register URLs
urlpatterns = [
    path("", include((site.urls[0], site.urls[1]), namespace=site.urls[2])),
]
```

## Best Practices

### 1. Single Responsibility

Each component should do one thing:

```python
# ✅ Good: Focused component
class BlogListComponent(RoutableComponent):
    """Display blog posts."""
    route_path = "blog/"

# ❌ Avoid: Too many responsibilities
class BlogManagementComponent(RoutableComponent):
    """Blog list, detail, create, edit, delete, export..."""
    route_path = "blog/"
```

### 2. Use Mixins for Reusability

```python
# ✅ Good: Reusable mixins
class FilterMixin:
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(title__icontains=search)
        return queryset

class BlogListComponent(FilterMixin, TableMixin, RoutableComponent):
    route_path = "blog/"

# ❌ Avoid: Duplicated logic
class BlogListComponent(RoutableComponent):
    def get_queryset(self):
        # Search logic duplicated...
```

### 3. Keep Logic in Services

```python
# ✅ Good: Logic in service layer
class BlogService:
    @staticmethod
    def get_published_posts(search=None):
        queryset = Blog.objects.filter(published=True)
        if search:
            queryset = queryset.filter(title__icontains=search)
        return queryset

class BlogListComponent(RoutableComponent):
    def get_queryset(self):
        return BlogService.get_published_posts(
            search=self.request.GET.get('search')
        )

# ❌ Avoid: Complex logic in component
class BlogListComponent(RoutableComponent):
    def get_queryset(self):
        # Complex filtering logic...
        # Publishing logic...
        # Cache logic...
```

### 4. Proper Error Handling

```python
# ✅ Good: Handle exceptions
class BlogDetailComponent(RoutableComponent):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['post'] = Blog.objects.get(slug=self.kwargs['slug'])
        except Blog.DoesNotExist:
            context['post'] = None
        return context

# ❌ Avoid: Unhandled exceptions
class BlogDetailComponent(RoutableComponent):
    def get_context_data(self, **kwargs):
        # This might raise exception
        context['post'] = Blog.objects.get(slug=self.kwargs['slug'])
```

## Related Documentation

- [ROUTING_SYSTEM.md](./ROUTING_SYSTEM.md) - URL routing
- [ARCHITECTURE_OVERVIEW.md](./ARCHITECTURE_OVERVIEW.md) - System architecture
- [FORMS_TABLES_INTEGRATION.md](./FORMS_TABLES_INTEGRATION.md) - Forms and tables
- [FRAGMENT_COMPONENTS.md](./FRAGMENT_COMPONENTS.md) - Fragment rendering
- [INTEGRATION_EXAMPLES.md](./INTEGRATION_EXAMPLES.md) - Real examples

---

**Next**: Read [ROUTING_SYSTEM.md](./ROUTING_SYSTEM.md) for URL routing details.

