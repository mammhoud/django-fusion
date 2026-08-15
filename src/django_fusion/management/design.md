# Design: Site Management

## Overview

Django Fusion management module.

## Directory

Path: `django_fusion/site/management`


## Architecture / Class Diagram

```mermaid
classDiagram
    class BaseSnippetViewSet {
      +duplicate()
      +export_csv()
      +icon_boolean()
      +link_display()
      +image_display()
    }
    SnippetViewSet <|-- BaseSnippetViewSet
    class BaseForm {
    }
    BaseFormMixin <|-- BaseForm
    forms.Form <|-- BaseForm
    class BaseModelForm {
    }
    BaseFormMixin <|-- BaseModelForm
    forms.ModelForm <|-- BaseModelForm
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
from django_fusion.management import BaseSnippetViewSet

# Wire into urls.py
from django.urls import path
urlpatterns = [
    path('basesnippetviewset/', BaseSnippetViewSet.as_view()),
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
