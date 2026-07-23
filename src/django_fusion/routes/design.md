# Design: Routes

## Overview

django_fusion.routes

## Directory

Path: `django_fusion/routes`


### Modules
- `base.py`
- `components.py`
- `detection.py`
- `fragments.py`
- `model.py`
- `other.py`
- `sites.py`
- `template_resolver.py`

## Architecture / Class Diagram

```mermaid
classDiagram
    class BaseModelViewset {
      +filter_kwargs()
      +index_path()
      +has_view_permission()
      +get_list_page_actions()
      +get_list_view_kwargs()
    }
    Viewset <|-- BaseModelViewset
    class Viewset {
      +viewsets()
      +filter_kwargs()
      +urls()
    }
    BaseViewset <|-- Viewset
    class _IndexRedirectView {
      +get_redirect_url()
    }
    RedirectView <|-- _IndexRedirectView
    class RoutableComponent {
      +get_fragment_name()
      +urls()
      +setup()
      +has_permission()
      +get_route_url()
    }
    ComponentViews <|-- RoutableComponent
    BaseViewset <|-- RoutableComponent
    class FragmentComponent {
      +dispatch()
      +setup()
      +get()
      +get_queryset()
      +get_fragment_context()
    }
    RoutableComponent <|-- FragmentComponent
    class Application {
      +get_context_data()
      +has_view_permission()
      +menu_items()
    }
    IndexViewMixin <|-- Application
    Viewset <|-- Application
    class Site {
      +menu_items()
      +has_view_permission()
      +register()
      +get_absolute_url()
    }
    IndexViewMixin <|-- Site
    Viewset <|-- Site
    class ModelViewset {
      +get_object_url()
      +get_success_url()
    }
    ListBulkActionsMixin <|-- ModelViewset
    CreateViewMixin <|-- ModelViewset
    UpdateViewMixin <|-- ModelViewset
    AppMenuMixin <|-- ModelViewset
    BaseModelViewset <|-- ModelViewset
    class ReadonlyModelViewset {
    }
    DetailViewMixin <|-- ReadonlyModelViewset
    ListBulkActionsMixin <|-- ReadonlyModelViewset
    AppMenuMixin <|-- ReadonlyModelViewset
    BaseModelViewset <|-- ReadonlyModelViewset
```
## Request Flow

1. A request enters the Django view/handler defined in this package.
2. The handler validates input, resolves any related models/components, and builds context.
3. The result is rendered (template/JSON/fragment) and returned to the client.

## Usage Example

```python
from django_fusion.routes import BaseModelViewset

# Wire into urls.py
from django.urls import path
urlpatterns = [
    path('basemodelviewset/', BaseModelViewset.as_view()),
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
