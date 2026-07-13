---
description: Add a new field to a Wagtail page model with full migration
agent: django-coder
---
# Add Field Workflow

You are helping a developer add a new field to a Wagtail page model.

1. Ask the user: Which page model? (e.g., `HomePage`, `ArticlePage`)
2. Ask: What is the field name? (e.g., `subtitle`, `featured_image`)
3. Ask: What is the field type? (e.g., `CharField`, `RichTextField`, `ImageField`)
4. Ask: Any specific attributes? (e.g., `max_length=255`, `blank=True`)
5. **Locate the model file** using `grep -r "class $MODEL_NAME" .`
6. **Add the field** to the model definition.
7. **Add the field to `content_panels`** in the same file.
8. **Generate migration**: `python manage.py makemigrations`
9. **Apply migration**: `python manage.py migrate`
10. **Verify**: Run `python manage.py showmigrations` to confirm it's applied.
10. **Report** the new field name and migration number to the user.

If the migration fails, rollback with `python manage.py migrate $APP zero` and retry.