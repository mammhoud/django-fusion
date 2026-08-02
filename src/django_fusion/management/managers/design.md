# Design: Site Management Managers

## Overview

Django model manager classes with caching, role hierarchy, and search support.

## Directory

Path: `django_fusion/site/management/managers`


### Modules
- `base.py`
- `group_access.py`
- `role_hierarchy.py`
- `search.py`
- `tags.py`
- `token.py`
- `user.py`

## Architecture / Class Diagram

```mermaid
classDiagram
    class TokenCachedManager {
      +get_token_cached()
      +filter_token_cached()
    }
    TokenAwareManagerMixin <|-- TokenCachedManager
    CachedManager <|-- TokenCachedManager
    class CachedManager {
    }
    CacheSupportMixin <|-- CachedManager
    BaseManager <|-- CachedManager
```
## Request Flow

1. A request enters the Django view/handler defined in this package.
2. The handler validates input, resolves any related models/components, and builds context.
3. The result is rendered (template/JSON/fragment) and returned to the client.

## Usage Example

```python
from django_fusion.management.managers import TokenCachedManager

# Wire into urls.py
from django.urls import path
urlpatterns = [
    path('tokencachedmanager/', TokenCachedManager.as_view()),
]
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
