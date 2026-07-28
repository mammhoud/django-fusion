# Website Architecture & Routing Documentation

Organized documentation for each website's routing configuration, component hierarchy, and usage patterns.

## Documentation Structure

```
docs/
├── WEBSITE_ARCHITECTURE.md          (This file - index)
├── vresume/
│   ├── ROUTING.md                   (VResume routing config)
│   ├── COMPONENTS.md                (VResume components)
│   └── ARCHITECTURE.md              (VResume design)
├── lms-demo/
│   ├── ROUTING.md                   (LMS routing config)
│   ├── COMPONENTS.md                (LMS components)
│   └── ARCHITECTURE.md              (LMS design)
└── ctc-research/
    ├── ROUTING.md                   (CTC routing config)
    ├── COMPONENTS.md                (CTC components)
    └── ARCHITECTURE.md              (CTC design)
```

## Website Overview

### VResume

**Type:** Portfolio/Resume platform
**Purpose:** Showcase projects and blog posts
**URL:** vresume.structa.cloud

**Component Applications:**
- Blog (blog posts and listings)
- Portfolio (project showcase)

**Wagtail Pages:**
- Landing pages
- About pages
- Service pages

### LMS Demo

**Type:** Learning Management System
**Purpose:** Course management and student enrollment
**URL:** lms-demo.structa.cloud

**Component Applications:**
- Admin (user and course management)
- Dashboard (student dashboard)
- Courses (course interface)

**Wagtail Pages:**
- Course catalog pages
- Learning pages
- Pricing pages

### CTC Research

**Type:** Research portal
**Purpose:** Research project management
**URL:** ctc-research.com

**Component Applications:**
- Research (project management)
- Admin (staff administration)
- Analytics (research analytics)

**Wagtail Pages:**
- Research overview
- Team pages
- Publication listings

## Common Patterns Across Sites

### Routing Pattern

All sites follow the same pattern:

```python
# urls.py

# 1. Mount component routes first
urlpatterns = [
    path("", include(site.urls))
]

# 2. Mount Wagtail pages second
urlpatterns += i18n_patterns(
    path("", include(wagtail_urls))
)
```

### Component Hierarchy

Each site uses the same three-level hierarchy:

```
Site
├── Application 1
│   ├── Component A
│   └── Component B
└── Application 2
    ├── Component C
    └── Component D
```

### URL Structure

All sites use root path `/`:

```
/app-name/view-path/        ← Component route
/page-slug/                 ← Wagtail page
```

## Site-Specific Features

### VResume Features

- Fragment-based blog (HTMX)
- Portfolio project showcase
- Personal branding
- Fragment components for modal views

### LMS Demo Features

- User management (admin)
- Course enrollment
- Student dashboard
- Progress tracking
- Form-based course creation

### CTC Research Features

- Research project management
- Staff administration
- Analytics and reporting
- Access control per researcher

## Shared Components

### Forms & Tables

All sites use the shared FormMixin and TableMixin:

```python
from django_fusion.comp.routes import RoutableComponent, FormMixin, TableMixin

class UserListComponent(RoutableComponent, TableMixin):
    table_name = "users"
    model = User
```

### Authentication

All sites use django-allauth with django-fusion:

```python
# Auth flows shared across sites
- Login (modal)
- Signup (modal)
- Password reset
- Email verification
```

### Templates

Template resolution cascade:

```
1. Site-specific:  applications/<site>/templates/
2. Shared assets:  applications/assets/templates/
3. Django-fusion:  django_fusion/.../templates/
```

## Getting Started by Site

### For VResume

See: `docs/vresume/ROUTING.md`

Quick start:
```python
from pages.routable_components import vresume_site

urlpatterns = [
    path("", include(vresume_site.urls))
]
```

### For LMS Demo

See: `docs/lms-demo/ROUTING.md`

Quick start:
```python
from www.routable_components import lms_site

urlpatterns = [
    path("", include(lms_site.urls))
]
```

### For CTC Research

See: `docs/ctc-research/ROUTING.md`

Quick start:
```python
from www.routable_components import ctc_site

urlpatterns = [
    path("", include(ctc_site.urls))
]
```

## Shared Documentation

### Global Architecture

- [Architecture Overview](../applications/libs/django-fusion/docs/INDEX.md)
- [Component System](../applications/libs/django-fusion/docs/COMPONENT_TAG.md)
- [Forms & Tables Integration](../applications/libs/django-fusion/docs/COMPONENT_CASE_STUDIES.md)
- [Routing Structure](../docs/reference/fusion_routing_structure.md)

### Development

- [Quick Start Guide](../applications/libs/django-fusion/docs/INDEX.md)
- [Integration Examples](../applications/libs/django-fusion/docs/COMPONENT_CASE_STUDIES.md)

## Analysis & Comparison

### Code Reuse

| Component | VResume | LMS | CTC |
|-----------|---------|-----|-----|
| Forms | ✓ | ✓ | ✓ |
| Tables | ✓ | ✓ | ✓ |
| Auth | ✓ | ✓ | ✓ |
| Pagination | ✓ | ✓ | ✓ |

### Template Reuse

| Template | VResume | LMS | CTC |
|----------|---------|-----|-----|
| form.html | Shared | Shared | Site-specific |
| table.html | Shared | Site-specific | Site-specific |
| menu.html | Shared | Shared | Shared |

### Routing Complexity

| Site | Components | Routes | Complexity |
|------|-----------|--------|-----------|
| VResume | 2 apps | 4 routes | Low |
| LMS | 3 apps | 8+ routes | Medium |
| CTC | 3 apps | 10+ routes | High |

## Best Practices

### 1. Use Shared Components

When possible, use shared components from assets:

```python
# ✓ Good - uses shared template
class UserListComponent(RoutableComponent, TableMixin):
    table_name = "users"  # Uses shared template
```

### 2. Override When Needed

Override in site-specific location when branding differs:

```
applications/<site>/templates/
├── plugins/tables/users.html     # Site override
```

### 3. Use FormMixin and TableMixin

Leverage these mixins for common patterns:

```python
from django_fusion.comp.routes import FormMixin, TableMixin

class UserComponent(RoutableComponent, FormMixin, TableMixin):
    form_name = "user"
    table_name = "users"
```

### 4. Organize by Feature

Group related components in applications:

```python
class AdminApp(Application):
    class UserComponent:
        pass
    class PostComponent:
        pass
```

### 5. Set Permissions

Always define permissions on components:

```python
class AdminComponent(RoutableComponent):
    permission_required = "auth.view_admin"
```

## Migration Guide

### Adding a New Component

1. Define in routable_components.py
2. Add to Application
3. Register with Site
4. Create template (or use shared)
5. Add to menu if needed

### Adding a New Application

1. Create Application class
2. Add components to it
3. Register with Site
4. Update documentation

### Adding a New Site

1. Create Site class
2. Define Applications
3. Configure urls.py (route before Wagtail)
4. Create site documentation
5. Add to WEBSITE_ARCHITECTURE.md

## Troubleshooting

### Routes Not Working

Check load order:
1. Components before Wagtail? ✓
2. i18n_patterns after? ✓
3. Application registered with Site? ✓

### Template Not Found

Check cascade:
1. Site-specific template? ✓
2. Shared assets template? ✓
3. Django-fusion fallback? ✓

### Permission Denied

Check:
1. permission_required set? ✓
2. User has permission? ✓
3. has_permission() method? ✓

## See Also

- [Django-Fusion Docs](../applications/libs/django-fusion/docs/)
- [AGENTS.md Rules](../AGENTS.md)
- [Forms & Tables Integration Summary](../docs/archives/forms_tables_integration_summary.md)

