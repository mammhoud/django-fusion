# Design: Site Interface Views

## Overview

django_fusion.contrib.views

## Directory

Path: `django_fusion/site/interface/views`


### Modules
- `notifications.py`
- `tags.py`

## Architecture / Class Diagram

```mermaid
classDiagram
    class EnhancedTagsView {
      +get_context_data()
      +search_tags_api()
      +merge_tags_api()
    }
    PageHandler <|-- EnhancedTagsView
    NotificationMixin <|-- EnhancedTagsView
    class NotificationView {
      +get()
      +post()
    }
    ComponentViews <|-- NotificationView
    NotificationMixin <|-- NotificationView
```
## Request Flow

1. A request enters the Django view/handler defined in this package.
2. The handler validates input, resolves any related models/components, and builds context.
3. The result is rendered (template/JSON/fragment) and returned to the client.

## Usage Example

```python
from django_fusion.site.interface.views import EnhancedTagsView

# Wire into urls.py
from django.urls import path
urlpatterns = [
    path('enhancedtagsview/', EnhancedTagsView.as_view()),
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
