# Design: Site Management Handlers Mixins

## Overview

Handler mixins for django_fusion.

## Directory

Path: `django_fusion/site/management/handlers/mixins`


### Modules
- `cache.py`
- `fragment.py`
- `page.py`
- `search.py`
- `token.py`

## Architecture / Class Diagram

```mermaid
classDiagram
    class TokenProtectedMixin {
      +save()
      +delete()
    }
    TokenAuthMixin <|-- TokenProtectedMixin
    class ProfileContextMixin {
      +get_profile_context()
      +get_context_data()
    }
    ContextMixin <|-- ProfileContextMixin
    class ProfileDashboardMixin {
      +get_dashboard_metrics()
      +get_quick_actions()
      +get_context_data()
    }
    ProfileContextMixin <|-- ProfileDashboardMixin
    class CacheSearchMixin {
      +search_cached()
    }
    CacheMixin <|-- CacheSearchMixin
```
## Request Flow

1. A request enters the Django view/handler defined in this package.
2. The handler validates input, resolves any related models/components, and builds context.
3. The result is rendered (template/JSON/fragment) and returned to the client.

## Usage Example

```python
from django_fusion.management.handlers.mixins import TokenProtectedMixin

# Use the mixin in your own view/component class
class MyView(TokenProtectedMixin, TemplateView):
    pass
```
## Commands / Entry Points

*No management commands are defined here by default.*

If this package exposes management commands, list them below:

```bash
python manage.py <command_name>
```

## Related Documentation

- [Django docs](https://docs.djangoproject.com/)
- [Wagtail docs](https://docs.wagtail.io/)
- Other `django_fusion` packages: see the root `design.md`.
