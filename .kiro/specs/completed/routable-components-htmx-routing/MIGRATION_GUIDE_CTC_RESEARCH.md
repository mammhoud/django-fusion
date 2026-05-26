# CTC Research Website Migration Guide

## Routable Components & HTMX Fragment Views

This guide provides step-by-step instructions for migrating the ctc-research.com website from manual URL routing to the new routable components system with HTMX fragments and Material Design 3 interfaces.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Architecture Overview](#architecture-overview)
3. [Phase-by-Phase Migration](#phase-by-phase-migration)
4. [Code Examples](#code-examples)
5. [Testing Strategy](#testing-strategy)
6. [Deployment](#deployment)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Packages

```bash
pip install django-osoul>=1.0.0
pip install django-material>=1.0.0
pip install htmx>=1.9.0
pip install django-cotton>=0.1.0
```

### Django Version

- Django 4.2 or higher
- Python 3.11 or higher

### Current CTC Research Structure

```
ctc-research.com/
├── apps/
│   ├── accounts/
│   ├── blog/
│   ├── content/
│   ├── handlers/
│   ├── lms/
│   ├── pages/
│   └── urls.py
├── components/
│   ├── blocks/
│   ├── common/
│   ├── contact/
│   ├── content/
│   ├── listing/
│   ├── privacy/
│   ├── profile/
│   └── search/
├── assets/
│   └── templates/
└── core/
    └── urls.py
```

---

## Architecture Overview

### Current State

```
Manual URL Routing
├── apps/urls.py (manual path definitions)
├── apps/handlers/ (PageHandler classes)
├── components/ (template fragments)
└── No automatic menu generation
```

### Target State

```
Routable Components System
├── apps/core/routes.py (Application & Site definitions)
├── apps/*/components.py (RoutableComponent, FragmentComponent, ModelViewset)
├── Automatic URL generation
├── Automatic menu generation
├── HTMX fragment support
└── Material Design 3 styling
```

### Component Hierarchy

```
Site
├── Application (LMS)
│   ├── RoutableComponent (Dashboard)
│   ├── ModelViewset (Courses)
│   └── FragmentComponent (Course List Fragment)
├── Application (Blog)
│   ├── ModelViewset (Blog Posts)
│   └── FragmentComponent (Post List Fragment)
└── Application (Content)
    ├── ModelViewset (Pages)
    └── FragmentComponent (Page List Fragment)
```

---

## Phase-by-Phase Migration

### Phase 1: Foundation Setup (Week 1-2)

#### Step 1.1: Create Core Routes Module

```python
# ctc-research.com/apps/core/routes.py
from django_osoul.contrib.routes import Application, Site, RoutableComponent
from django_osoul.contrib.page_handler import PageHandler

class CTCRoutableComponent(RoutableComponent, PageHandler):
    """Base routable component for CTC Research."""

    def get_breadcrumbs(self):
        """Generate breadcrumbs from component hierarchy."""
        breadcrumbs = []
        # Implementation will build breadcrumbs from parent components
        return breadcrumbs

    def get_sidebar_context(self):
        """Get sidebar context for Material navigation."""
        return {
            "menu_items": self.get_menu_items(),
            "user": self.request.user,
            "site_title": "CTC Research",
        }

    def get_menu_items(self):
        """Get menu items for this component."""
        return []
```

#### Step 1.2: Update Django Settings

```python
# ctc-research.com/configs/settings/base.py

INSTALLED_APPS = [
    # ... existing apps ...
    'material',
    'django_osoul.comp',
    'django_osoul.contrib',
]

# Material Design 3 Configuration
MATERIAL_DESIGN = {
    'THEME': 'light',
    'PRIMARY_COLOR': '#6750a4',  # CTC brand color
    'SECONDARY_COLOR': '#625b71',
}

# HTMX Configuration
HTMX_ENABLED = True
HTMX_ALLOWED_DOMAINS = ['ctc-research.com', 'www.ctc-research.com']
```

#### Step 1.3: Update Base Templates

```html
<!-- assets/templates/base.html -->
{% extends "material/base.html" %}
{% load static %}

{% block head %}
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{% block title %}CTC Research{% endblock %}</title>
    <link rel="stylesheet" href="{% static 'material/css/material.css' %}">
    <script src="{% static 'htmx/htmx.min.js' %}"></script>
{% endblock %}

{% block navigation %}
    <c-navigation.drawer>
        {% for app in site.applications %}
            {% if app.has_permission user %}
                <c-navigation.item>
                    <span class="material-icons">{{ app.icon }}</span>
                    <span>{{ app.title }}</span>
                    {% for component in app.components %}
                        <c-navigation.item href="{{ component.get_route_url }}">
                            {{ component.menu_label }}
                        </c-navigation.item>
                    {% endfor %}
                </c-navigation.item>
            {% endif %}
        {% endfor %}
    </c-navigation.drawer>
{% endblock %}

{% block content %}
    <div class="material-container">
        {% block breadcrumbs %}
            {% if breadcrumbs %}
                <nav aria-label="breadcrumb">
                    <ol>
                        {% for breadcrumb in breadcrumbs %}
                            <li><a href="{{ breadcrumb.url }}">{{ breadcrumb.label }}</a></li>
                        {% endfor %}
                    </ol>
                </nav>
            {% endif %}
        {% endblock %}

        {% block page_content %}{% endblock %}
    </div>
{% endblock %}
```

### Phase 2: Component Migration (Week 3-4)

#### Step 2.1: Migrate Dashboard Component

**Before:**
```python
# apps/handlers/dashboard.py
from django_osoul.contrib.page_handler import PageHandler

class DashboardHandler(PageHandler):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "stats": self.get_stats(),
            "recent_activity": self.get_recent_activity(),
        })
        return context

    def get_stats(self):
        # Implementation
        pass

# apps/urls.py
urlpatterns = [
    path("dashboard/", DashboardHandler.as_view(), name="dashboard"),
]
```

**After:**
```python
# apps/core/components.py
from apps.core.routes import CTCRoutableComponent

class DashboardComponent(CTCRoutableComponent):
    """Dashboard component - routable and full-page."""

    route_name = "dashboard"
    page_title = "Dashboard"
    template_name = "dashboard.html"

    # Menu configuration
    menu_icon = "dashboard"
    menu_label = "Dashboard"
    menu_order = 1

    def has_permission(self, user):
        """Only authenticated users can access."""
        return user.is_authenticated

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "stats": self.get_stats(),
            "recent_activity": self.get_recent_activity(),
            "upcoming_courses": self.get_upcoming_courses(),
        })
        return context

    def get_stats(self):
        """Get dashboard statistics."""
        from apps.lms.models import Course, Enrollment
        from apps.accounts.models import Instructor

        return {
            "total_courses": Course.objects.count(),
            "enrolled_students": Enrollment.objects.count(),
            "active_instructors": Instructor.objects.filter(is_active=True).count(),
        }

    def get_recent_activity(self):
        """Get recent activity for dashboard."""
        from apps.handlers.models import Activity
        return Activity.objects.all()[:10]

    def get_upcoming_courses(self):
        """Get upcoming courses."""
        from django.utils import timezone
        from apps.lms.models import Course

        return Course.objects.filter(
            start_date__gte=timezone.now()
        ).order_by('start_date')[:5]
```

#### Step 2.2: Migrate Blog Components

```python
# apps/blog/components.py
from django_osoul.contrib.routes import ModelViewset, RoutableComponent
from apps.core.routes import CTCRoutableComponent
from apps.blog.models import BlogPost
from apps.blog.forms import BlogPostForm

class BlogListComponent(CTCRoutableComponent):
    """Blog list page."""

    route_name = "blog-list"
    page_title = "Blog"
    template_name = "blog/list.html"
    menu_icon = "article"
    menu_label = "Blog"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["posts"] = BlogPost.objects.filter(
            published=True
        ).order_by('-published_date')[:10]
        return context


class BlogDetailComponent(CTCRoutableComponent):
    """Blog post detail page."""

    route_name = "blog-detail"
    page_title = "Blog Post"
    template_name = "blog/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post_slug = self.kwargs.get('slug')
        context["post"] = BlogPost.objects.get(slug=post_slug)
        context["related_posts"] = context["post"].get_related_posts()[:3]
        return context


class BlogPostViewset(ModelViewset):
    """Complete CRUD for blog posts."""

    model = BlogPost
    form_class = BlogPostForm

    # List view
    list_columns = ("title", "author", "published_date", "status")
    list_filter_fields = ("status", "published_date")
    list_search_fields = ("title", "content")
    list_template = "blog/posts/list.html"

    # Detail view
    detail_template = "blog/posts/detail.html"

    # Create/Update
    form_fields = ("title", "content", "excerpt", "featured_image", "status")
    create_template = "blog/posts/form.html"
    update_template = "blog/posts/form.html"

    # Delete
    delete_template = "blog/posts/delete_confirm.html"

    # Permissions
    permission_required = "blog.view_blogpost"

    def has_add_permission(self, user):
        return user.has_perm('blog.add_blogpost')

    def has_change_permission(self, user, obj=None):
        return user.has_perm('blog.change_blogpost')

    def has_delete_permission(self, user, obj=None):
        return user.has_perm('blog.delete_blogpost')
```

#### Step 2.3: Migrate Content Components

```python
# apps/content/components.py
from django_osoul.contrib.routes import ModelViewset
from apps.core.routes import CTCRoutableComponent
from apps.content.models import Page
from apps.content.forms import PageForm

class PageViewset(ModelViewset):
    """Complete CRUD for pages."""

    model = Page
    form_class = PageForm

    list_columns = ("title", "slug", "status", "updated_at")
    list_filter_fields = ("status",)
    list_search_fields = ("title", "content")

    form_fields = ("title", "slug", "content", "status")

    permission_required = "content.view_page"

    def has_add_permission(self, user):
        return user.has_perm('content.add_page')

    def has_change_permission(self, user, obj=None):
        return user.has_perm('content.change_page')

    def has_delete_permission(self, user, obj=None):
        return user.has_perm('content.delete_page')
```

### Phase 3: Fragment Enhancement (Week 5-6)

#### Step 3.1: Create Fragment Components

```python
# apps/lms/components.py
from django_osoul.contrib.routes import FragmentComponent
from django.core.paginator import Paginator
from django.db.models import Q
from apps.lms.models import Course

class CourseListFragment(FragmentComponent):
    """Course list as HTMX fragment."""

    route_name = "course-list-fragment"
    fragment_template = "lms/fragments/course_list.html"
    htmx_only = True
    paginate_by = 20
    pagination_style = "load_more"

    def has_permission(self, user):
        return user.is_authenticated

    def get_fragment_context(self, **kwargs):
        """Context for fragment rendering."""
        page = self.request.GET.get('page', 1)
        courses = self.get_queryset()

        paginator = Paginator(courses, self.paginate_by)
        page_obj = paginator.get_page(page)

        return {
            "courses": page_obj.object_list,
            "page_obj": page_obj,
            "paginator": paginator,
            "has_next": page_obj.has_next(),
            "next_page_url": self.get_next_page_url(page_obj),
        }

    def get_queryset(self):
        """Get courses based on filters."""
        courses = Course.objects.all()

        # Filter by category
        category = self.request.GET.get('category')
        if category:
            courses = courses.filter(category=category)

        # Search
        search = self.request.GET.get('search')
        if search:
            courses = courses.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )

        return courses.order_by('-created_at')

    def get_next_page_url(self, page_obj):
        """Get URL for next page."""
        if page_obj.has_next():
            return f"{self.request.path}?page={page_obj.next_page_number()}"
        return None
```

**Fragment Template:**
```html
<!-- lms/fragments/course_list.html -->
<div id="course-items">
    {% for course in courses %}
        <c-card class="course-card">
            <h3>{{ course.title }}</h3>
            <p class="instructor">{{ course.instructor.name }}</p>
            <p class="description">{{ course.description|truncatewords:20 }}</p>
            <div class="course-meta">
                <span class="category">{{ course.category }}</span>
                <span class="level">{{ course.get_level_display }}</span>
            </div>
            <a href="{{ course.get_absolute_url }}" class="course-link">
                View Course
            </a>
        </c-card>
    {% endfor %}

    {% if has_next %}
        <button hx-get="{{ next_page_url }}"
                hx-target="#course-items"
                hx-swap="beforeend"
                class="load-more-btn">
            Load More Courses
        </button>
    {% endif %}
</div>
```

#### Step 3.2: Add Out-of-Band Updates

```python
# apps/lms/components.py
class CourseDetailComponent(CTCRoutableComponent):
    """Course detail with nested fragments."""

    route_name = "course-detail"
    page_title = "Course Details"
    template_name = "lms/courses/detail.html"

    nested_fragments = {
        "modules": "ModuleListFragment",
        "reviews": "ReviewListFragment",
        "enrollment": "EnrollmentFragment",
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_id = self.kwargs.get('pk')
        course = Course.objects.get(pk=course_id)

        context.update({
            "course": course,
            "modules": course.modules.all(),
            "reviews": course.reviews.all()[:5],
            "enrollment_count": course.enrollments.count(),
        })
        return context

    def get_oob_fragments(self, request):
        """Return out-of-band fragments to update other parts of page."""
        course = self.get_course()

        return [
            {
                "selector": ".course-stats",
                "template": "lms/fragments/course_stats.html",
                "context": {
                    "course": course,
                    "stats": self.get_course_stats(course),
                },
            },
            {
                "selector": ".recent-reviews",
                "template": "lms/fragments/recent_reviews.html",
                "context": {
                    "reviews": self.get_recent_reviews(course),
                },
            },
        ]

    def get_course(self):
        course_id = self.kwargs.get('pk')
        return Course.objects.get(pk=course_id)

    def get_course_stats(self, course):
        return {
            "total_modules": course.modules.count(),
            "total_reviews": course.reviews.count(),
            "average_rating": course.get_average_rating(),
        }

    def get_recent_reviews(self, course):
        return course.reviews.all()[:3]
```

### Phase 4: Application Grouping (Week 7-8)

#### Step 4.1: Create Application Structure

```python
# ctc-research.com/apps/core/routes.py
from django_osoul.contrib.routes import Application, Site
from apps.core.components import DashboardComponent
from apps.blog.components import BlogListComponent, BlogPostViewset
from apps.content.components import PageViewset
from apps.lms.components import CourseViewset, StudentViewset
from apps.accounts.components import ProfileComponent, UserViewset

class ResearchApp(Application):
    """Research application."""

    app_name = "research"
    title = "Research"
    icon = "science"
    menu_order = 1

    components = [
        # Add research components here
    ]

    def has_permission(self, user):
        return user.is_authenticated


class LMSApp(Application):
    """Learning Management System application."""

    app_name = "lms"
    title = "Learning"
    icon = "school"
    menu_order = 2

    components = [
        CourseViewset(),
        StudentViewset(),
    ]

    def has_permission(self, user):
        return user.is_staff


class BlogApp(Application):
    """Blog application."""

    app_name = "blog"
    title = "Blog"
    icon = "article"
    menu_order = 3

    components = [
        BlogListComponent(),
        BlogPostViewset(),
    ]

    def has_permission(self, user):
        return True  # Public


class ContentApp(Application):
    """Content Management application."""

    app_name = "content"
    title = "Content"
    icon = "description"
    menu_order = 4

    components = [
        PageViewset(),
    ]

    def has_permission(self, user):
        return user.is_staff


class AccountsApp(Application):
    """Accounts application."""

    app_name = "accounts"
    title = "Accounts"
    icon = "person"
    menu_order = 5

    components = [
        ProfileComponent(),
        UserViewset(),
    ]

    def has_permission(self, user):
        return user.is_authenticated


# Global site configuration
site = Site(
    title="CTC Research Platform",
    logo_url="/static/images/logo.png",
    applications=[
        ResearchApp(),
        LMSApp(),
        BlogApp(),
        ContentApp(),
        AccountsApp(),
    ]
)
```

#### Step 4.2: Update Main URLs

```python
# ctc-research.com/core/urls.py
from django.contrib import admin
from django.urls import path, include
from apps.core.routes import site

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", site.urls),
]
```

### Phase 5: Testing & Optimization (Week 9-10)

#### Step 5.1: Unit Tests

```python
# tests/test_components.py
from django.test import TestCase, Client
from django.contrib.auth.models import User
from apps.core.components import DashboardComponent
from apps.lms.models import Course

class TestDashboardComponent(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('test', 'test@test.com', 'pass')

    def test_dashboard_accessible_authenticated(self):
        self.client.login(username='test', password='pass')
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)

    def test_dashboard_requires_auth(self):
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_dashboard_context_data(self):
        component = DashboardComponent()
        component.request = self.client.get('/dashboard/').wsgi_request
        context = component.get_context_data()
        self.assertIn('stats', context)
        self.assertIn('recent_activity', context)
```

#### Step 5.2: Integration Tests

```python
# tests/test_routing.py
from django.test import TestCase, Client
from django.contrib.auth.models import User

class TestRouting(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('test', 'test@test.com', 'pass')

    def test_dashboard_url_resolves(self):
        response = self.client.get('/dashboard/')
        self.assertIn(response.status_code, [200, 302])

    def test_fragment_htmx_request(self):
        self.client.login(username='test', password='pass')
        response = self.client.get(
            '/lms/course-list-fragment/',
            HTTP_HX_REQUEST='true'
        )
        self.assertEqual(response.status_code, 200)

    def test_fragment_non_htmx_request(self):
        response = self.client.get('/lms/course-list-fragment/')
        # Should return 400 or redirect for non-HTMX requests
        self.assertIn(response.status_code, [400, 302])
```

---

## Code Examples

### Example 1: Simple Routable Component

```python
class AboutComponent(CTCRoutableComponent):
    route_name = "about"
    page_title = "About Us"
    template_name = "about.html"
    menu_icon = "info"
    menu_label = "About"

    def has_permission(self, user):
        return True  # Public

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["team"] = self.get_team_members()
        return context

    def get_team_members(self):
        from apps.accounts.models import TeamMember
        return TeamMember.objects.filter(active=True)
```

### Example 2: Fragment with Pagination

```python
class BlogPostListFragment(FragmentComponent):
    route_name = "blog-posts-fragment"
    fragment_template = "blog/fragments/post_list.html"
    htmx_only = True
    paginate_by = 10

    def get_fragment_context(self, **kwargs):
        page = self.request.GET.get('page', 1)
        posts = BlogPost.objects.filter(published=True).order_by('-published_date')

        paginator = Paginator(posts, self.paginate_by)
        page_obj = paginator.get_page(page)

        return {
            "posts": page_obj.object_list,
            "page_obj": page_obj,
        }
```

### Example 3: ModelViewset with Permissions

```python
class UserViewset(ModelViewset):
    model = User
    form_class = UserForm

    list_columns = ("username", "email", "is_staff", "is_active")
    list_filter_fields = ("is_staff", "is_active")

    permission_required = "auth.view_user"

    def has_add_permission(self, user):
        return user.is_superuser

    def has_change_permission(self, user, obj=None):
        return user.is_superuser or user == obj

    def has_delete_permission(self, user, obj=None):
        return user.is_superuser
```

---

## Testing Strategy

### Unit Tests

Test individual components in isolation:

```bash
python manage.py test tests.test_components
```

### Integration Tests

Test URL routing and view interactions:

```bash
python manage.py test tests.test_routing
```

### HTMX Tests

Test fragment rendering and HTMX headers:

```bash
python manage.py test tests.test_fragments
```

### Run All Tests

```bash
python manage.py test
```

---

## Deployment

### Pre-Deployment Checklist

- [ ] All tests passing
- [ ] Static files collected
- [ ] Database migrations applied
- [ ] Environment variables configured
- [ ] Material Design CSS loaded
- [ ] HTMX library loaded
- [ ] Backup of current database

### Deployment Steps

1. **Backup current database**
   ```bash
   python manage.py dumpdata > backup.json
   ```

2. **Run migrations**
   ```bash
   python manage.py migrate
   ```

3. **Collect static files**
   ```bash
   python manage.py collectstatic --noinput
   ```

4. **Run tests**
   ```bash
   python manage.py test
   ```

5. **Deploy to production**
   ```bash
   git push production main
   ```

6. **Monitor logs**
   ```bash
   tail -f logs/application.log
   ```

---

## Troubleshooting

### Fragment Not Updating

**Problem:** HTMX fragment request returns full page instead of fragment.

**Solution:**
1. Check that `HX-Request` header is being sent
2. Verify `htmx_only = True` is set on FragmentComponent
3. Check browser console for HTMX errors
4. Verify fragment template path is correct

### Permission Denied

**Problem:** Component returns 403 Forbidden.

**Solution:**
1. Check `has_permission()` method returns True
2. Verify user has required permissions
3. Check permission_required setting
4. Review permission inheritance

### URL Not Resolving

**Problem:** Component URL returns 404 Not Found.

**Solution:**
1. Verify component is registered in Application
2. Check Application is registered in Site
3. Verify route_name is unique
4. Check URL patterns are generated correctly

### Template Not Found

**Problem:** TemplateDoesNotExist error.

**Solution:**
1. Verify template_name path is correct
2. Check template file exists
3. Verify TEMPLATES setting in Django settings
4. Check template loader configuration

---

## Performance Tips

### 1. Cache Route Metadata

```python
from django.views.decorators.cache import cache_page

@cache_page(60 * 5)  # Cache for 5 minutes
def get_menu_items(self):
    return self.site.get_menu_items()
```

### 2. Optimize Fragment Queries

```python
def get_queryset(self):
    return Course.objects.select_related(
        'instructor'
    ).prefetch_related(
        'categories'
    )
```

### 3. Use Pagination

```python
class CourseListFragment(FragmentComponent):
    paginate_by = 20  # Don't load all at once
```

### 4. Implement Query Filtering

```python
def get_fragment_context(self, **kwargs):
    courses = self.get_queryset()

    # Filter by category
    category = self.request.GET.get('category')
    if category:
        courses = courses.filter(category=category)

    return {"courses": courses}
```

---

## Next Steps

1. **Week 1-2:** Set up foundation (Phase 1)
2. **Week 3-4:** Migrate components (Phase 2)
3. **Week 5-6:** Add fragments (Phase 3)
4. **Week 7-8:** Organize applications (Phase 4)
5. **Week 9-10:** Test and optimize (Phase 5)

**Total estimated time: 10 weeks for full migration**

---

## Support & Resources

- [django-osoul Documentation](https://github.com/viewflow/django-osoul)
- [django-material Documentation](https://github.com/viewflow/django-material)
- [HTMX Documentation](https://htmx.org/)
- [Django Documentation](https://docs.djangoproject.com/)

---

## Glossary

- **RoutableComponent:** A component that renders a full page and is accessible via URL
- **FragmentComponent:** A component that renders only a partial HTML response for HTMX
- **ModelViewset:** A class that automatically generates CRUD views for a model
- **Application:** A collection of related components
- **Site:** A collection of applications that make up the website
- **Fragment:** A partial HTML response for HTMX requests
- **OOB Swap:** Out-of-band swap - updating multiple parts of the page in one response
- **HX-Request:** HTTP header sent by HTMX to indicate an AJAX request
- **Material Design 3:** Google's latest design system with updated components

