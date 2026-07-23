# Design: django-fusion

## Overview

django-fusion — reusable Django and Wagtail helpers for Structa Cloud sites.

## Directory

Path: `django_fusion`


### Modules
- `enums.py`
- `exceptions.py`

## Architecture / ERD

```mermaid
erDiagram
    Integration {
        CharField name
        CharField external_id
        CharField integration_type
        CharField endpoint_type
        URLField api_endpoint
        CharField api_key
        JSONField metadata
        BooleanField is_active
        DateTimeField last_sync_at
        CharField sync_status
        DateTimeField created_at
        DateTimeField updated_at
    }
    EmailLog {
        DateTimeField timestamp
        EmailField recipient
        CharField subject
        CharField status
        CharField template_used
        TextField message_body
        TextField error_message
        PositiveIntegerField retry_count
        DateTimeField last_retry_at
        ForeignKey user
        CharField group_name
        CharField task_id
        DateTimeField created_at
        DateTimeField updated_at
        DateTimeField sent_at
        CharField invitation_token
        DateTimeField token_expires_at
    }
    EmailTemplate {
        CharField name
        CharField subject
        TextField html_content
        TextField text_content
        TextField description
        BooleanField is_active
        DateTimeField created_at
        DateTimeField updated_at
        DateTimeField go_live_at
        DateTimeField expire_at
        CharField template_source
        CharField template_path
        URLField external_url
        CharField subject_template
        CharField preview_text
        FileField html_file
        FileField css_file
        TextField css_content
        CharField template_type
        CharField language
        PositiveIntegerField version
        BooleanField is_default
        BooleanField is_system
        BooleanField is_draft
        EmailField reply_to_email
        EmailField from_email
        CharField from_name
        URLField unsubscribe_url
        CharField category
        JSONField tags
        SlugField slug
        CharField cache_key
        DateTimeField last_rendered
        PositiveIntegerField render_count
        FloatField open_rate
        FloatField click_rate
        FloatField conversion_rate
        FloatField bounce_rate
    }
    UserGroup {
        CharField name
        TextField description
        IntegerField score
        ManyToManyField users
        DateTimeField created_at
        DateTimeField updated_at
    }
    UserRole {
        ForeignKey user
        CharField role
        DateTimeField assigned_at
        ForeignKey assigned_by
    }
    Role {
        CharField name
        CharField role_type
        TextField description
        JSONField permissions
        BooleanField is_default
        PositiveIntegerField level
        OneToOneField group
        DateTimeField created_at
        DateTimeField updated_at
    }

    EmailLog ||--o| auth.User : user
    UserGroup ||--o| auth.User : users
    UserRole ||--o| auth.User : user
    UserRole ||--o| auth.User : assigned_by
    Role ||--o| Group : group
```
## Request Flow

1. A request enters the Django view/handler defined in this package.
2. The handler validates input, resolves any related models/components, and builds context.
3. The result is rendered (template/JSON/fragment) and returned to the client.

## Usage Example

```python
from django_fusion...models import Integration

# Query and create instances
qs = Integration.objects.all()
obj = Integration.objects.create(name='...', external_id='...', integration_type='...')
```

```python
from django_fusion.. import BaseModelViewset

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
