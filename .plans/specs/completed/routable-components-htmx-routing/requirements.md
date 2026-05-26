# Requirements: Routable Components & Nested HTMX Fragment Views

**Feature Name:** routable-components-htmx-routing
**Status:** In Progress
**Created:** 2026-04-19
**Updated:** 2026-04-19
**Inspired By:** [django-material vibe branch](https://github.com/viewflow/django-material/tree/vibe/demo)
**Integration:** django-osoul components + django-material patterns + HTMX fragments
**Target Migration:** ctc-research.com website

---

## Executive Summary

Enhance django-osoul's routing system to support routable components with automatic HTMX fragment detection, nested view hierarchies, and declarative menu integration. This enhancement integrates proven patterns from django-material (Material Design 3 components, CRUD interfaces, SPA-like navigation) with django-osoul's existing component system and page handlers.

The implementation will enable developers to build component-driven applications with clean URL structures, seamless HTMX interactions, and Material Design interfaces — without requiring REST APIs or frontend frameworks. This is particularly suited for the ctc-research.com website migration.

---

## Current Implementation Status

The following classes already exist in `libs/django-osoul/src/django_osoul/site/routes/`
(canonical) and mirrored in `ctc-research.com/libs/django-osoul/src/django_osoul/contrib/routes/`:

| Class | File | Status |
|---|---|---|
| `BaseViewset` | `base.py` | ✅ Complete |
| `Viewset` | `base.py` | ✅ Complete |
| `Route` / `route()` | `base.py` | ✅ Complete |
| `menu_path()` | `base.py` | ✅ Complete |
| `IndexViewMixin` | `base.py` | ✅ Complete |
| `RoutableComponent` | `components.py` | ✅ Complete + enhanced |
| `FragmentComponent` | `fragments.py` | ✅ Complete + enhanced |
| `FragmentDetector` | `detection.py` | ✅ Complete |
| `FragmentDetectionMixin` | `detection.py` | ✅ Complete |
| `BaseModelViewset` | `model.py` | ✅ Complete |
| `ModelViewset` | `other.py` | ✅ Complete |
| `ReadonlyModelViewset` | `other.py` | ✅ Complete |
| `CreateViewMixin` | `other.py` | ✅ Complete |
| `UpdateViewMixin` | `other.py` | ✅ Complete |
| `DeleteViewMixin` | `other.py` | ✅ Complete |
| `DetailViewMixin` | `other.py` | ✅ Complete |
| `ListBulkActionsMixin` | `other.py` | ✅ Complete |
| `Application` | `sites.py` | ✅ Complete + menu_order sort |
| `AppMenuMixin` | `sites.py` | ✅ Complete |
| `Site` | `sites.py` | ✅ Complete |

**New in this sprint:**
- `RoutableComponent`: added `page_title`, `menu_label`, `menu_order`, `show_in_menu`
- `FragmentComponent`: added `paginate_by`, `page_kwarg`, `get_queryset()`, proper `get()` override, HTTP 400 for `htmx_only`
- `Application.menu_items()`: sorts by `menu_order`, respects `show_in_menu`
- Template tags: `{% site_menu %}`, `{% app_menu %}`, `{% breadcrumbs %}`, `{% component_url %}`, `{% active_menu %}`, `{% fragment_pagination %}`
- Default templates: site_menu, app_menu, breadcrumbs, pagination
- ctc-research integration: `apps/core/routes.py`, `apps/lms/viewsets.py`, `apps/blog/viewsets.py`, `apps/lms/components.py`, `apps/blog/components.py`
- Fragment templates: `lms/fragments/course_list.html`, `blog/fragments/post_list.html`
- Unit tests: `tests/unit/test_routable_components.py`

**What remains:** Mirror enhancements to `ctc-research.com/libs/django-osoul/`, run tests, docs.

---

## Architecture Overview

### Integration Model

```
┌─────────────────────────────────────────────────────────────┐
│                    Django Application                        │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Site (Global Configuration)             │   │
│  │  - Title, branding, global navigation                │   │
│  │  - Application grouping and ordering                 │   │
│  └──────────────────────────────────────────────────────┘   │
│                           │                                   │
│  ┌──────────────────────┐  ┌──────────────────────┐         │
│  │   Application 1      │  │   Application 2      │         │
│  │  (e.g., LMS)         │  │  (e.g., CMS)         │         │
│  │  - app_name          │  │  - app_name          │         │
│  │  - icon, title       │  │  - icon, title       │         │
│  │  - viewsets[]        │  │  - viewsets[]        │         │
│  └──────────────────────┘  └──────────────────────┘         │
│           │                                                   │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐         │
│  │ RoutableComp │ │ ModelViewset │ │ FragmentComp │         │
│  │ (Full Page)  │ │ (CRUD Views) │ │ (HTMX Only)  │         │
│  └──────────────┘ └──────────────┘ └──────────────┘         │
│                         │                                     │
│                    ┌────▼────┐                               │
│                    │ URL Conf │                              │
│                    │ (Auto)   │                              │
│                    └──────────┘                              │
└─────────────────────────────────────────────────────────────┘
```

### Component Hierarchy (Actual Code)

```
ComponentViews (contrib/page_handler.py)
├── RoutableComponent (contrib/routes/components.py)
│   ├── route_name, route_path, icon, title
│   ├── has_permission(), get_route_url(), get_breadcrumbs()
│   └── FragmentComponent (contrib/routes/fragments.py)
│       ├── fragment_template, htmx_only, oob_fragments
│       ├── is_htmx_request(), get_fragment_context()
│       └── render_oob_fragment()
│
BaseViewset (contrib/routes/base.py)
└── Viewset (contrib/routes/base.py)
    ├── Application (contrib/routes/sites.py)
    │   ├── title, icon, menu_template_name
    │   ├── has_view_permission(), menu_items()
    │   └── get_context_data()
    └── Site (contrib/routes/sites.py)
        ├── title, icon, primary_color
        ├── menu_items(), register()
        └── get_absolute_url()

BaseModelViewset (contrib/routes/model.py)
└── ModelViewset (contrib/routes/other.py)
    ├── ListBulkActionsMixin
    ├── CreateViewMixin
    ├── UpdateViewMixin
    ├── DeleteViewMixin (separate)
    └── DetailViewMixin (separate)
```

---

## Django-Material Integration Patterns

### Material Design 3 Components

```html
<!-- Available in templates via django-material -->
<c-button.filled>Action</c-button.filled>
<c-card>Content</c-card>
<c-table>Data</c-table>
<c-form>Input</c-form>
<c-navigation.drawer>Menu</c-navigation.drawer>
```

### CRUD Interface Pattern

```python
# Automatic CRUD views — matches existing ModelViewset in other.py
class CourseViewset(ModelViewset):
    model = Course
    list_columns = ("title", "instructor", "published", "students_count")
    list_filter_fields = ("category", "level", "published")
    list_search_fields = ("title", "description")
    form_class = CourseForm
```

### SPA-like Navigation (HTMX pattern)

```html
<!-- Fragment updates without full page reload -->
<button hx-get="{% url 'lms:course-list-fragment' %}"
        hx-target="#course-list"
        hx-swap="innerHTML">
  Refresh Courses
</button>

<!-- Out-of-band updates -->
<div id="notifications" hx-swap-oob="true">
  Updated notifications
</div>
```

---

## Code Examples: Using Existing django-osoul Classes

### Example 1: RoutableComponent (Full Page)

```python
# apps/lms/components.py
from django_osoul.contrib.routes import RoutableComponent

class DashboardComponent(RoutableComponent):
    """Dashboard — full-page routable component."""

    route_name = "dashboard"
    route_path = "dashboard/"
    icon = "dashboard"
    title = "Dashboard"
    template_name = "lms/dashboard.html"

    def has_permission(self, user):
        return user.is_authenticated

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "stats": self.get_stats(),
            "recent_activity": self.get_recent_activity(),
        })
        return context

    def get_stats(self):
        from apps.lms.models import Course, Enrollment
        return {
            "total_courses": Course.objects.count(),
            "enrolled_students": Enrollment.objects.count(),
        }

    def get_recent_activity(self):
        from apps.lms.models import Activity
        return Activity.objects.all()[:10]
```

### Example 2: FragmentComponent (HTMX Only)

```python
# apps/lms/components.py
from django_osoul.contrib.routes import FragmentComponent
from django.core.paginator import Paginator
from django.db.models import Q

class CourseListFragment(FragmentComponent):
    """Course list — HTMX fragment, no full-page rendering."""

    route_name = "course-list-fragment"
    route_path = "courses/list-fragment/"
    fragment_template = "lms/fragments/course_list.html"
    htmx_only = True

    # OOB fragments to update alongside main content
    oob_fragments = {
        "course-count": "lms/fragments/course_count.html",
    }

    def has_permission(self, user):
        return user.is_authenticated

    def get_fragment_context(self, **kwargs):
        page = self.request.GET.get("page", 1)
        courses = self.get_queryset()
        paginator = Paginator(courses, 20)
        page_obj = paginator.get_page(page)
        return {
            "courses": page_obj.object_list,
            "page_obj": page_obj,
            "has_next": page_obj.has_next(),
        }

    def get_queryset(self):
        from apps.lms.models import Course
        qs = Course.objects.all()
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))
        return qs.order_by("-created_at")
```

### Example 3: ModelViewset (Full CRUD)

```python
# apps/lms/viewsets.py
from django_osoul.contrib.routes import ModelViewset
from apps.lms.models import Course
from apps.lms.forms import CourseForm

class CourseViewset(ModelViewset):
    """Full CRUD for courses — list, detail, create, update, delete."""

    model = Course
    form_class = CourseForm

    list_columns = ("title", "instructor", "category", "level", "published")
    list_filter_fields = ("category", "level", "published")
    list_search_fields = ("title", "description")

    def has_view_permission(self, user, obj=None):
        return user.has_perm("lms.view_course")

    def has_add_permission(self, user):
        return user.has_perm("lms.add_course")

    def has_change_permission(self, user, obj=None):
        return user.has_perm("lms.change_course")

    def has_delete_permission(self, user, obj=None):
        return user.has_perm("lms.delete_course")
```

### Example 4: Application + Site

```python
# apps/lms/routes.py
from django_osoul.contrib.routes import Application, Site
from .viewsets import CourseViewset, StudentViewset
from .components import DashboardComponent, CourseListFragment

class LMSApp(Application):
    """Learning Management System."""

    title = "Learning"
    icon = "school"
    app_name = "lms"

    viewsets = [
        DashboardComponent(),
        CourseViewset(),
        StudentViewset(),
    ]

    def has_view_permission(self, user, obj=None):
        return user.is_staff


class BlogApp(Application):
    title = "Blog"
    icon = "article"
    app_name = "blog"

    viewsets = [
        BlogPostViewset(),
    ]


# Global site
site = Site(
    title="CTC Research Platform",
    viewsets=[LMSApp(), BlogApp()],
)

# In core/urls.py:
# urlpatterns = [path("", site.urls)]
```

### Example 5: Fragment with OOB Updates

```python
# apps/lms/components.py
class CourseDetailComponent(RoutableComponent):
    """Course detail with nested OOB fragment updates."""

    route_name = "course-detail"
    route_path = "courses/<int:pk>/"
    title = "Course Details"
    template_name = "lms/courses/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.shortcuts import get_object_or_404
        from apps.lms.models import Course
        course = get_object_or_404(Course, pk=self.kwargs["pk"])
        context.update({
            "course": course,
            "modules": course.modules.all(),
            "reviews": course.reviews.all()[:5],
        })
        return context

    def get_oob_fragments(self, request):
        """OOB fragments to update alongside main content."""
        return {
            "course-stats": self.render_oob_fragment(
                "course-stats",
                "lms/fragments/course_stats.html",
                {"course": self.get_object()},
            ),
        }
```

---

## Migration Guide: ctc-research.com

### Current State

```
ctc-research.com/
├── apps/
│   ├── accounts/     # Auth, profiles
│   ├── blog/         # Blog posts
│   ├── content/      # Pages
│   ├── handlers/     # PageHandler classes
│   ├── lms/          # Courses, students
│   └── urls.py       # Manual URL routing
├── components/       # HTML fragment templates
│   ├── profile/
│   ├── listing/
│   └── search/
└── core/urls.py      # Root URL config
```

### Target State

```
ctc-research.com/
├── apps/
│   ├── accounts/
│   │   └── components.py   # ProfileComponent, UserViewset
│   ├── blog/
│   │   └── viewsets.py     # BlogPostViewset
│   ├── lms/
│   │   ├── viewsets.py     # CourseViewset, StudentViewset
│   │   └── components.py   # DashboardComponent, fragments
│   └── core/
│       └── routes.py       # Application + Site definitions
└── core/urls.py            # path("", site.urls)
```

### Phase 1: Foundation (Week 1-2)

**Create base component class:**
```python
# ctc-research.com/apps/core/components.py
from django_osoul.contrib.routes import RoutableComponent
from django_osoul.contrib.page_handler import PageHandler

class CTCComponent(RoutableComponent, PageHandler):
    """Base component for CTC Research — adds breadcrumbs and sidebar."""

    show_breadcrumbs = True

    def get_breadcrumbs(self):
        crumbs = [{"title": "Home", "url": "/"}]
        crumbs.extend(super().get_breadcrumbs())
        return crumbs
```

**Before (manual):**
```python
# apps/handlers/dashboard.py
class DashboardHandler(PageHandler):
    template_name = "dashboard.html"

# apps/urls.py
path("dashboard/", DashboardHandler.as_view(), name="dashboard"),
```

**After (routable):**
```python
# apps/core/components.py
class DashboardComponent(CTCComponent):
    route_name = "dashboard"
    route_path = "dashboard/"
    title = "Dashboard"
    template_name = "dashboard.html"
    icon = "dashboard"
    # No urls.py entry needed — registered via Application
```

### Phase 2: Component Migration (Week 3-4)

```python
# apps/blog/viewsets.py
from django_osoul.contrib.routes import ModelViewset
from apps.blog.models import BlogPost

class BlogPostViewset(ModelViewset):
    model = BlogPost
    list_columns = ("title", "author", "published_date", "status")
    list_filter_fields = ("status",)
    list_search_fields = ("title", "content")

# apps/lms/viewsets.py
from apps.lms.models import Course

class CourseViewset(ModelViewset):
    model = Course
    list_columns = ("title", "instructor", "category", "published")
    list_filter_fields = ("category", "published")
    list_search_fields = ("title", "description")
```

### Phase 3: Fragment Enhancement (Week 5-6)

```python
# apps/lms/components.py
from django_osoul.contrib.routes import FragmentComponent

class CourseListFragment(FragmentComponent):
    route_name = "course-list-fragment"
    route_path = "lms/courses/fragment/"
    fragment_template = "lms/fragments/course_list.html"
    htmx_only = True

    def get_fragment_context(self, **kwargs):
        from apps.lms.models import Course
        from django.core.paginator import Paginator
        page = self.request.GET.get("page", 1)
        qs = Course.objects.filter(published=True)
        paginator = Paginator(qs, 20)
        page_obj = paginator.get_page(page)
        return {"courses": page_obj.object_list, "page_obj": page_obj}
```

**Template:**
```html
<!-- lms/fragments/course_list.html -->
{% for course in courses %}
  <div class="course-card">
    <h3>{{ course.title }}</h3>
    <p>{{ course.description|truncatewords:20 }}</p>
    <a href="{{ course.get_absolute_url }}">View</a>
  </div>
{% endfor %}

{% if page_obj.has_next %}
  <button hx-get="?page={{ page_obj.next_page_number }}"
          hx-target="#course-list"
          hx-swap="beforeend">
    Load More
  </button>
{% endif %}
```

### Phase 4: Application Grouping (Week 7-8)

```python
# ctc-research.com/apps/core/routes.py
from django_osoul.contrib.routes import Application, Site
from apps.lms.viewsets import CourseViewset, StudentViewset
from apps.lms.components import DashboardComponent, CourseListFragment
from apps.blog.viewsets import BlogPostViewset
from apps.accounts.viewsets import UserViewset

class LMSApp(Application):
    title = "Learning"
    icon = "school"
    app_name = "lms"
    viewsets = [DashboardComponent(), CourseViewset(), StudentViewset()]

    def has_view_permission(self, user, obj=None):
        return user.is_staff

class BlogApp(Application):
    title = "Blog"
    icon = "article"
    app_name = "blog"
    viewsets = [BlogPostViewset()]

class AccountsApp(Application):
    title = "Accounts"
    icon = "person"
    app_name = "accounts"
    viewsets = [UserViewset()]

    def has_view_permission(self, user, obj=None):
        return user.is_authenticated

site = Site(
    title="CTC Research",
    viewsets=[LMSApp(), BlogApp(), AccountsApp()],
)
```

```python
# ctc-research.com/core/urls.py  (add to existing)
from apps.core.routes import site

urlpatterns += [
    path("app/", include(site.urls)),
]
```

### URL Structure Comparison

| Before (Manual) | After (Automatic) |
|---|---|
| `/dashboard/` | `/app/lms/dashboard/` |
| `/blog/` | `/app/blog/` |
| `/blog/<slug>/` | `/app/blog/<pk>/detail/` |
| `/courses/` | `/app/lms/courses/` |
| `/courses/<id>/` | `/app/lms/courses/<pk>/detail/` |
| `/profile/` | `/app/accounts/profile/` |

---

## Functional Requirements

### FR-1: Route Registration

- FR-1.1: `RoutableComponent` defines `route_name` and `route_path`
- FR-1.2: `Application` collects components via `viewsets` list
- FR-1.3: `Site` generates URL patterns from all applications
- FR-1.4: Routes support GET and POST
- FR-1.5: Routes support URL parameters (e.g., `<int:pk>`)

### FR-2: Fragment Detection

- FR-2.1: `FragmentDetector.detect()` returns `"full"`, `"fragment"`, or `"oob"`
- FR-2.2: Detects `HX-Request`, `HX-Target`, `HX-Trigger` headers
- FR-2.3: `FragmentComponent.htmx_only` rejects non-HTMX requests
- FR-2.4: OOB fragments appended to response content
- FR-2.5: `add_fragment_detection_to_request()` augments request object

### FR-3: ModelViewset CRUD

- FR-3.1: `ModelViewset` generates list, detail, create, update, delete views
- FR-3.2: List view supports pagination, filtering, search
- FR-3.3: Create/Update views use `form_class`
- FR-3.4: Delete view has confirmation
- FR-3.5: Bulk actions via `ListBulkActionsMixin`

### FR-4: Menu System

- FR-4.1: `Application.menu_items()` yields `AppMenuMixin` viewsets
- FR-4.2: `menu_path()` creates URL patterns with icon/title metadata
- FR-4.3: `Site.menu_items()` yields applications
- FR-4.4: Permission-based filtering via `has_view_permission()`

### FR-5: Permission System

- FR-5.1: `RoutableComponent.has_permission()` checks `permission_required`
- FR-5.2: `Application.has_view_permission()` checks application-level access
- FR-5.3: `ModelViewset` has `has_view/add/change/delete_permission()`
- FR-5.4: Permissions cascade from Site → Application → Component

---

## Non-Functional Requirements

### NFR-1: Performance
- URL resolution < 10ms
- Fragment detection < 1ms overhead
- Menu generation cached

### NFR-2: Compatibility
- Django 4.2+
- Python 3.11+
- HTMX 1.9+
- Backward compatible with existing django-osoul

### NFR-3: Usability
- Intuitive API matching DRF viewset patterns
- Clear error messages
- Comprehensive examples

---

## Out of Scope

1. REST API endpoints (no DRF integration)
2. Database schema changes
3. Custom authentication backend
4. Replacing Django admin
5. Frontend JavaScript frameworks

---

## References

- [django-material](https://github.com/viewflow/django-material) — Material Design 3 + CRUD patterns
- [Django URL dispatcher](https://docs.djangoproject.com/en/stable/topics/http/urls/)
- [HTMX documentation](https://htmx.org/docs/)
- `libs/django-osoul/src/django_osoul/contrib/routes/` — Existing implementation
- `libs/django-osoul/src/django_osoul/contrib/page_handler.py` — ComponentViews base
