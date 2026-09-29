# Design: Components Generic

## Overview

This package (`fragments.generic`) is part of `django-fusion` and provides reusable components, utilities, or routing helpers.

## Directory

Path: `django_fusion/fragments/generic`


### Modules

- `actions.py`
- `base.py`
- `detail.py`
- `list.py`

## Architecture / Class Diagram

```mermaid
classDiagram
    class DetailModelView {
      +has_view_permission()
      +get_object_data()
      +get_page_actions()
      +get_object_actions()
      +get_object_change_link()
    }
    generic.DetailView <|-- DetailModelView
    class BaseBulkActionView {
      +get_template_names()
      +get_success_url()
      +get_form_kwargs()
      +get_queryset()
      +objects_count()
    }
    MultipleObjectMixin <|-- BaseBulkActionView
    generic.FormView <|-- BaseBulkActionView
    class DeleteBulkActionView {
      +get_deleted_objects()
      +get_context_data()
      +form_valid()
      +message_user()
    }
    BaseBulkActionView <|-- DeleteBulkActionView
    class BaseListModelView {
      +has_view_permission()
      +get_columns()
      +get_object_link_columns()
      +get_column_def()
      +get_object_url()
    }
    generic.ListView <|-- BaseListModelView
    class ListModelView {
    }
    BulkActionsMixin <|-- ListModelView
    FilterMixin <|-- ListModelView
    OrderableListViewMixin <|-- ListModelView
    BaseListModelView <|-- ListModelView
```
## Request Flow

1. A request enters the Django view/handler defined in this package.
2. The handler validates input, resolves any related models/components, and builds context.
3. The result is rendered (template/JSON/fragment) and returned to the client.

## Usage Example

```python
from django_fusion.fragments.tables.table import TableView

# Wire into urls.py
from django.urls import path
urlpatterns = [
    path('tableview/', TableView.as_view()),
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
