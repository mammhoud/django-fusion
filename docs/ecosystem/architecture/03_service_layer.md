# Service Layer Architecture

## Overview

The service layer provides a clean separation between views and models, encapsulating business logic in reusable service classes.

## Service Patterns

### Base Service Classes

All services inherit from base classes provided by django-osoul:

```python
from django_osoul.comp.payloads.services import BaseService, TokenService
```

### Certificate Service

**Location**: `crafts_ai/pipelines/services/certificate.py`

```python
class CertificateServiceBase:
    """Base class for certificate operations."""

    certificate_model = None  # Injected by subclass

    @classmethod
    def issue_certificate(cls, user, course, completion_date=None):
        """Issue a certificate for course completion."""

    @classmethod
    def validate_certificate(cls, certificate_number):
        """Validate a certificate by its number."""

    @classmethod
    def get_certificate_profile(cls, user):
        """Get all certificates for a user."""
```

### Person Service

**Location**: `crafts_ai/pipelines/services/person.py`

```python
class PersonServiceBase:
    """Base class for person/profile operations."""

    @classmethod
    def create_person_with_profile(cls, user, data):
        """Create a Person profile for a user."""

    @classmethod
    def get_user_profile_information(cls, user):
        """Get profile information for a user."""

    @classmethod
    def sync_person_with_user(cls, person):
        """Sync Person data with User model."""

    @classmethod
    def update_notification_preferences(cls, user, preferences):
        """Update notification preferences."""

    @classmethod
    def invite_person_to_register(cls, email, inviter=None):
        """Invite a person to register."""
```

### Message Service

**Location**: `crafts_ai/pipelines/services/message.py`

```python
class MessageServiceBase:
    """Base class for messaging operations."""

    message_model = None  # Injected by subclass

    @classmethod
    def send_message(cls, sender, recipient, content, message_type="info"):
        """Send a message to a user."""

    @classmethod
    def send_bulk_notification(cls, user_ids, content, message_type="info"):
        """Send notification to multiple users."""

    @classmethod
    def get_conversation_thread(cls, user1, user2, page=1, page_size=20):
        """Get conversation between two users."""

    @classmethod
    def get_message_analytics(cls, user, date_range=None):
        """Get message statistics for a user."""
```

### Form Submission Service

**Location**: `crafts_ai/pipelines/services/form_submission.py`

```python
class FormSubmissionService:
    """Service for handling form submissions."""

    submission_model = None  # Injected by subclass

    @classmethod
    def save_submission(cls, form_name, data, user=None):
        """Save a form submission."""

    @classmethod
    def send_notification_email(cls, submission):
        """Send notification about new submission."""

    @classmethod
    def get_submissions_for_form(cls, form_name, filters=None):
        """Get all submissions for a form."""

    @classmethod
    def get_submission_stats(cls, form_name, date_range=None):
        """Get submission statistics."""
```

## Service Usage

### In Views

```python
from crafts_ai.pipelines.services import CertificateServiceBase

class MyView(View):
    def get(self, request):
        certificates = CertificateServiceBase.get_user_certificates(request.user)
        return render(request, 'certificates.html', {'certificates': certificates})
```

### In Templates

```python
{% for cert in certificates %}
    <div class="certificate">
        <h3>{{ cert.course.title }}</h3>
        <p>Issued: {{ cert.issued_at }}</p>
    </div>
{% endfor %}
```

## Best Practices

1. **Always use base classes** - Inherit from `*ServiceBase` classes
2. **Inject models** - Set `certificate_model`, `message_model`, etc. in subclasses
3. **Use class methods** - Services should primarily use `@classmethod`
4. **Keep views thin** - Delegate all business logic to services
