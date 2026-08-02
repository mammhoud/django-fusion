# Design: Site Management Filters

## Overview

Filters module for django_fusion.

## Directory

Path: `django_fusion/site/management/filters`


### Modules
- `base.py`
- `cache.py`
- `token.py`
- `validators.py`

## Architecture / Class Diagram

```mermaid
classDiagram
    class TokenAwareFilter {
      +run()
    }
    BaseFilterMethod <|-- TokenAwareFilter
    TokenFilterMixin <|-- TokenAwareFilter
    class _TokenFilterSet {
      +filter_by_token()
    }
    django_filters.FilterSet <|-- _TokenFilterSet
    TokenFilterMixin <|-- _TokenFilterSet
```
## Request Flow

1. A request enters the Django view/handler defined in this package.
2. The handler validates input, resolves any related models/components, and builds context.
3. The result is rendered (template/JSON/fragment) and returned to the client.

## Usage Example

```python
from django_fusion.management.filters import TokenAwareFilter

# Wire into urls.py
from django.urls import path
urlpatterns = [
    path('tokenawarefilter/', TokenAwareFilter.as_view()),
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
