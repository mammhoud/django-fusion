# Design: Components Forms

## Overview

django_fusion.fragments.forms — Form integration with tag generation.

## Directory

Path: `django_fusion/fragments/forms`


### Modules

- `create.py`
- `delete.py`
- `forms.py`
- `mixins.py`
- `search.py`
- `tag_generator.py`
- `update.py`

## Architecture / Class Diagram

```mermaid
classDiagram
    class FormTableMixin {
      +get_form_table_context_data()
    }
    FormMixin <|-- FormTableMixin
    TableMixin <|-- FormTableMixin
    class BaseForm {
    }
    BaseFormMixin <|-- BaseForm
    forms.Form <|-- BaseForm
    class BaseModelForm {
    }
    BaseFormMixin <|-- BaseModelForm
    forms.ModelForm <|-- BaseModelForm
    class CreateModelView {
      +has_add_permission()
      +get_object_url()
      +message_user()
      +queryset()
      +get_form_widgets()
    }
    FormLayoutMixin <|-- CreateModelView
    generic.CreateView <|-- CreateModelView
    class DeleteModelView {
      +has_delete_permission()
      +get_deleted_objects()
      +queryset()
      +get_object()
      +get_template_names()
    }
    generic.DeleteView <|-- DeleteModelView
    class UpdateModelView {
      +has_change_permission()
      +get_object_url()
      +get_page_actions()
      +message_user()
      +queryset()
    }
    FormLayoutMixin <|-- UpdateModelView
    generic.UpdateView <|-- UpdateModelView
```
## Request Flow

1. A request enters the Django view/handler defined in this package.
2. The handler validates input, resolves any related models/components, and builds context.
3. The result is rendered (template/JSON/fragment) and returned to the client.

## Usage Example

```python
from django_fusion.fragments.forms import FormTableMixin

# Use the mixin in your own view/component class
class MyView(FormTableMixin, TemplateView):
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
