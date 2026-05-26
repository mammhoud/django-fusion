# Design: Routable Components & Nested HTMX Fragment Views

**Feature Name:** routable-components-htmx-routing
**Status:** In Progress
**Updated:** 2026-04-19

---

## Actual Class Hierarchy (as implemented)

```
django.views.generic.TemplateView
└── ComponentViews  (contrib/page_handler.py)
    │   setup(), get(), post(), render_to_response()
    │
    └── RoutableComponent  (contrib/routes/components.py)
        │   route_name, route_path, icon, title, permission_required
        │   has_permission(), get_route_url(), get_breadcrumbs()
        │
        └── FragmentComponent  (contrib/routes/fragments.py)
                fragment_template, htmx_only, oob_fragments
                is_htmx_request(), get_fragment_context()
                render_oob_fragment(), render_to_response()

BaseViewset  (contrib/routes/base.py)
│   app_name, namespace, parent_namespace
│   urls property, reverse(), has_view_permission()
│
└── Viewset  (contrib/routes/base.py)  [metaclass=ViewsetMeta]
    │   viewsets, urlpatterns, declared_patterns
    │   _get_urls(), filter_kwargs()
    │
    ├── Application  (contrib/routes/sites.py)
    │       title, icon, menu_template_name, permission
    │       has_view_permission(), menu_items(), get_context_data()
    │
    └── Site  (contrib/routes/sites.py)
            title, icon, primary_color, secondary_color
            menu_items(), register(), get_absolute_url()

BaseModelViewset  (contrib/routes/model.py)
│   model, queryset, list_view_class, list_columns, ...
│   has_view_permission(), list_path property
│
└── ModelViewset  (contrib/routes/other.py)
        ListBulkActionsMixin + CreateViewMixin + UpdateViewMixin + AppMenuMixin
        get_object_url(), get_success_url()

    DeleteViewMixin  (contrib/routes/other.py)  — mixed in separately
    DetailViewMixin  (contrib/routes/other.py)  — mixed in separately
    ReadonlyModelViewset  (contrib/routes/other.py)
```

---

## URL Routing System

### How URLs Are Generated

```python
# 1. Site.urls property calls Viewset._get_urls()
# 2. _get_urls() iterates self.viewsets and self.declared_patterns
# 3. Each child viewset gets route(prefix, viewset) → URLResolver
# 4. Namespace = app_name (auto-generated from class name if None)

# Example resolution:
site = Site(viewsets=[LMSApp()])
# → path("lms/", include(LMSApp.urls, namespace="lms"))

class LMSApp(Application):
    app_name = "lms"
    viewsets = [CourseViewset()]
# → path("courses/", include(CourseViewset.urls, namespace="courses"))

class CourseViewset(ModelViewset):
    model = Course
# Auto-generates:
#   path("",          list_view,   name="list")
#   path("add/",      create_view, name="add")
#   path("<pk>/change/", update_view, name="change")
#   path("<pk>/delete/", delete_view, name="delete")
#   path("<pk>/detail/", detail_view, name="detail")
```

### URL Reverse Resolution

```python
# From within a viewset:
self.reverse("list")           # → /lms/courses/
self.reverse("change", args=[pk])  # → /lms/courses/42/change/

# From a RoutableComponent:
self.get_route_url()           # → /lms/dashboard/
```

---

## Fragment Detection Flow

```
HTTP Request
    │
    ├─ FragmentDetector.detect(request)
    │   ├─ HX-Request header present?
    │   │   ├─ NO  → strategy = "full"
    │   │   └─ YES → HX-Swap-OOB present?
    │   │               ├─ YES → strategy = "oob"
    │   │               └─ NO  → strategy = "fragment"
    │
    ├─ FragmentComponent.setup()
    │   └─ htmx_only=True and not HTMX? → PermissionDenied(400)
    │
    ├─ FragmentComponent.get()
    │   └─ calls get_fragment_context() → render fragment_template
    │
    └─ FragmentComponent.render_to_response()
        └─ HTMX request? → append OOB fragments to response body
```

### HTMX Response Headers

```python
# Set in ComponentViews.render_to_response():
response["HX-Reswap"] = "innerHTML"
response["HX-Retarget"] = self.fragment_target  # if set

# OOB fragments appended as HTML:
# <div id="fragment-id" hx-swap-oob="true">...</div>
```

---

## Permission System

```
Site.has_view_permission(user)
    └─ checks self.permission (string perm or None)

Application.has_view_permission(user)
    └─ checks self.permission (callable or string perm)

RoutableComponent.has_permission(user)
    └─ checks self.permission_required (string or list)
    └─ raises PermissionDenied in setup() if False

ModelViewset.has_view_permission(user, obj)
    └─ has_object_perm(user, "view", model, obj)
    └─ OR has_change_permission(user, obj)

ModelViewset.has_add_permission(user)
    └─ has_object_perm(user, "add", model)

ModelViewset.has_change_permission(user, obj)
    └─ has_object_perm(user, "change", model, obj)

ModelViewset.has_delete_permission(user, obj)
    └─ has_object_perm(user, "delete", model, obj)
```

---

## Menu System

```python
# Site.menu_items() → yields Application instances
# Application.menu_items() → yields:
#   1. AppMenuMixin viewsets (ModelViewset, RoutableComponent)
#   2. URLPatterns created with menu_path() (have .icon attribute)

# Template rendering:
# {% for app in site.menu_items() %}
#   {% for item in app.menu_items() %}
#     <a href="...">{{ item.title }}</a>
#   {% endfor %}
# {% endfor %}
```

---

## Template Context

```python
# RoutableComponent.get_context_data() adds:
{
    "breadcrumbs": [...],   # from get_breadcrumbs()
    "title": self.title,
    "icon": self.icon,
    "component": self,
    # + parent ComponentViews context
}

# Application.get_context_data() adds:
{
    "app_name": ...,
    "title": ...,
    "icon": ...,
    "app_url": request.path,
    "viewset": self,
}
```

---

## Template Resolution

```python
# FragmentComponent.get_template_names():
#   HTMX request + fragment_template set → [fragment_template]
#   Otherwise → parent resolution (template_name)

# ModelViewset views use django-osoul generic views:
#   ListModelView, CreateModelView, UpdateModelView,
#   DeleteModelView, DetailModelView
```

---

## Caching Strategy

```python
# Site._viewset_models — @cached_property
#   Maps model class → viewset for get_absolute_url()

# Viewset._urls_cache — instance cache
#   Stores generated URL patterns after first call to .urls

# Menu generation — not yet cached (task 4.1)
# Fragment HTML — not yet cached (task 4.1)
```

---

## Integration with ctc-research.com

### Current URL Structure

```python
# ctc-research.com/core/urls.py
urlpatterns += i18n_patterns(
    path("", include("apps.urls")),          # manual routing
    path("privacy/", include(...)),
    path("", include("django_rseal.pipelines.urls")),
    path("", include(wagtail_urls)),
)

# ctc-research.com/apps/urls.py
urlpatterns = [
    path("blog/", include("apps.blog.urls", namespace="blog")),
    path("lms/", include("apps.lms.urls")),
    path("", include("apps.accounts.urls")),
]
```

### Target Integration

```python
# ctc-research.com/apps/core/routes.py
from django_osoul.contrib.routes import Application, Site

class LMSApp(Application):
    title = "Learning"
    app_name = "lms"
    viewsets = [CourseViewset(), StudentViewset(), DashboardComponent()]

class BlogApp(Application):
    title = "Blog"
    app_name = "blog"
    viewsets = [BlogPostViewset()]

site = Site(title="CTC Research", viewsets=[LMSApp(), BlogApp()])

# ctc-research.com/core/urls.py  (add alongside existing)
from apps.core.routes import site
urlpatterns += [path("app/", include(site.urls))]
```

---

## Error Handling

```python
# RoutableComponent.setup() → PermissionDenied if has_permission() is False
# FragmentComponent.setup() → PermissionDenied if htmx_only and not HTMX

# ComponentViews.handle_error():
#   HTMX request → JsonResponse({"error": ...}, status=400)
#   Regular request → render page with error context

# ModelViewset views use Django's standard 404/403 handling
```

---

## Security

- CSRF: All POST forms must include `{% csrf_token %}`
- XSS: Django auto-escapes template variables
- Permissions: Checked at setup() before any view logic
- HTMX: `htmx_only` flag prevents direct URL access to fragment endpoints

---

## Configuration

```python
# settings.py — no special configuration required
# django-osoul routes work with standard Django settings

# Optional: cache timeout for menu generation
DJANGO_OSOUL = {
    "MENU_CACHE_TIMEOUT": 300,  # seconds
}
```
