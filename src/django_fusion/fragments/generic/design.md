# Design: Components Generic

## Overview

This package (`components.generic`) is part of `django-fusion` and provides reusable components, utilities, or routing helpers.

## Directory

Path: `django_fusion/components/generic`


### Modules
- `actions.py`
- `base.py`
- `create.py`
- `delete.py`
- `detail.py`
- `list.py`
- `search.py`
- `table.py`
- `update.py`

## Architecture / Class Diagram

```mermaid
classDiagram
    class TableView {
      +get_table()
      +get_context_data()
    }
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
    class DetailModelView {
      +has_view_permission()
      +get_object_data()
      +get_page_actions()
      +get_object_actions()
      +get_object_change_link()
    }
    generic.DetailView <|-- DetailModelView
    class UpdateModelView {
      +has_change_permission()
      +get_object_url()
      +get_page_actions()
      +message_user()
      +queryset()
    }
    FormLayoutMixin <|-- UpdateModelView
    generic.UpdateView <|-- UpdateModelView
    class DeleteModelView {
      +has_delete_permission()
      +get_deleted_objects()
      +queryset()
      +get_object()
      +get_template_names()
    }
    generic.DeleteView <|-- DeleteModelView
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
    class CreateModelView {
      +has_add_permission()
      +get_object_url()
      +message_user()
      +queryset()
      +get_form_widgets()
    }
    FormLayoutMixin <|-- CreateModelView
    generic.CreateView <|-- CreateModelView
```
## Request Flow

1. A request enters the Django view/handler defined in this package.
2. The handler validates input, resolves any related models/components, and builds context.
3. The result is rendered (template/JSON/fragment) and returned to the client.

## Usage Example

```python
from django_fusion.components.generic import TableView

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
