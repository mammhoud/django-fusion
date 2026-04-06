# ContactSubmission Model Analysis & Improvements

## Overview
The `ContactSubmission` model has been significantly enhanced with Wagtail integration, better field organization, and improved functionality. However, there are several opportunities for improvement in terms of code quality, maintainability, and best practices.

## 1. Code Smells and Anti-patterns

### 1.1 Magic Strings and Hardcoded Values
**Issue**: Multiple hardcoded field names and magic strings throughout the code.

```python
# Current problematic code
email_fields = ["email", "e_mail", "mail", "contact_email", "e-mail",
               "Email", "E-Mail", "EMAIL"]
```


**Recommendation**: Extract constants to class-level or module-level definitions.

```python
class ContactSubmission(DefaultBase, DraftStateMixin, RevisionMixin, LockableMixin):
    # Field name constants
    EMAIL_FIELD_NAMES = [
        "email", "e_mail", "mail", "contact_email", "e-mail",
        "Email", "E-Mail", "EMAIL"
    ]
    NAME_FIELD_NAMES = ["name", "full_name", "fullname", "Full Name"]
    PHONE_FIELD_NAMES = [
        "phone", "telephone", "mobile", "phone_number",
        "Phone", "Telephone", "Mobile"
    ]
```

### 1.2 Repetitive Field Extraction Logic
**Issue**: Similar pattern repeated in `get_email()`, `get_name()`, and `get_phone()` methods.

**Recommendation**: Create a generic field extraction method.

```python
def _extract_field_value(self, field_names, transform_func=None):
    """Generic method to extract field values from submitted data."""
    for field in field_names:
        if value := self.submitted_data.get(field):
            result = str(value).strip()
            return transform_func(result) if transform_func else result
    return None
```

### 1.3 Long Method with Multiple Responsibilities
**Issue**: `export_as_csv_row()` method handles both data transformation and flattening.

**Recommendation**: Split into separate methods for better single responsibility principle.

## 2. Design Pattern Opportunities

### 2.1 Strategy Pattern for Field Extraction
**Recommendation**: Implement strategy pattern for different field extraction strategies.

```python
from abc import ABC, abstractmethod

class FieldExtractor(ABC):
    @abstractmethod
    def extract(self, submitted_data: dict) -> str:
        pass

class EmailExtractor(FieldExtractor):
    def extract(self, submitted_data: dict) -> str:
        # Email extraction logic
        pass

class NameExtractor(FieldExtractor):
    def extract(self, submitted_data: dict) -> str:
        # Name extraction logic with fallback to first+last name
        pass
```

### 2.2 Factory Pattern for Export Formats
**Recommendation**: Use factory pattern for different export formats.

```python
class ExportFormatFactory:
    @staticmethod
    def create_exporter(format_type: str):
        if format_type == 'dict':
            return DictExporter()
        elif format_type == 'csv':
            return CSVExporter()
        # Add more formats as needed
```

## 3. Best Practices Violations

### 3.1 Import Organization
**Issue**: Imports are not properly organized according to PEP 8.

**Current**:
```python
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, TabbedInterface, ObjectList, MultiFieldPanel
from wagtail.models import RevisionMixin, DraftStateMixin, LockableMixin
from modelcluster.models import ClusterableModel
```

**Recommended**:
```python
# Standard library imports
from typing import Dict, List, Optional, Union

# Third-party imports
from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, ObjectList, TabbedInterface
from wagtail.models import DraftStateMixin, LockableMixin, RevisionMixin

# Local imports
from django_grep.pipelines.models import DefaultBase
```

### 3.2 Missing Type Hints
**Issue**: Methods lack type annotations for better code documentation and IDE support.

**Recommendation**: Add comprehensive type hints.

```python
from typing import Dict, List, Optional, Union, Any

def get_field_value(self, field_name: str) -> Optional[Any]:
    """Get a specific field value from submitted data."""
    return self.submitted_data.get(field_name)

def get_email(self) -> Optional[str]:
    """Get email from submitted data."""
    # Implementation

def export_as_dict(self) -> Dict[str, Any]:
    """Export submission data as dictionary."""
    # Implementation
```

### 3.3 Inconsistent Error Handling
**Issue**: Some methods may fail silently or don't handle edge cases properly.

**Recommendation**: Add proper error handling and logging.

```python
import logging

logger = logging.getLogger(__name__)

def get_preview_url(self) -> Optional[str]:
    """Get preview URL if page exists."""
    if not self.page_id:
        return None

    try:
        from wagtail.models import Page
        page = Page.objects.get(id=self.page_id)
        return page.get_full_url()
    except Page.DoesNotExist:
        logger.warning(f"Page with ID {self.page_id} not found for submission {self.id}")
        return None
    except Exception as e:
        logger.error(f"Error getting preview URL for submission {self.id}: {e}")
        return None
```

## 4. Readability Improvements

### 4.1 Method Documentation
**Issue**: Some methods lack comprehensive docstrings.

**Recommendation**: Add detailed docstrings with parameters and return types.

```python
def mark_as_processed(self) -> None:
    """
    Mark this submission as processed and set the processed date.

    Updates the processed flag to True and sets processed_date to current time.
    Only updates the necessary fields to avoid unnecessary database writes.

    Raises:
        DatabaseError: If the update operation fails.
    """
    from django.utils import timezone
    self.processed = True
    self.processed_date = timezone.now()
    self.save(update_fields=["processed", "processed_date", "updated_at"])
```

### 4.2 Complex Logic Simplification
**Issue**: The `get_name()` method has complex nested logic.

**Recommendation**: Break down into smaller, more readable methods.

```python
def get_name(self) -> str:
    """Get name from submitted data with fallback strategies."""
    # Try direct name fields first
    direct_name = self._get_direct_name()
    if direct_name:
        return direct_name

    # Try combining first and last name
    combined_name = self._get_combined_name()
    if combined_name:
        return combined_name

    return _("Anonymous")

def _get_direct_name(self) -> Optional[str]:
    """Extract name from direct name fields."""
    return self._extract_field_value(self.NAME_FIELD_NAMES)

def _get_combined_name(self) -> Optional[str]:
    """Combine first and last name fields."""
    first_name = self.submitted_data.get("first_name", "").strip()
    last_name = self.submitted_data.get("last_name", "").strip()
    if first_name or last_name:
        return f"{first_name} {last_name}".strip()
    return None
```

## 5. Maintainability Enhancements

### 5.1 Configuration Externalization
**Issue**: Field names and other configuration are hardcoded in the model.

**Recommendation**: Move configuration to settings or separate configuration class.

```python
# In settings.py or separate config file
CONTACT_FORM_CONFIG = {
    'EMAIL_FIELDS': ["email", "e_mail", "mail", "contact_email"],
    'NAME_FIELDS': ["name", "full_name", "fullname"],
    'PHONE_FIELDS': ["phone", "telephone", "mobile", "phone_number"],
    'EXPORT_FORMATS': ['dict', 'csv', 'json'],
}
```

### 5.2 Validation Methods
**Issue**: No validation for submitted data integrity.

**Recommendation**: Add validation methods.

```python
def clean(self) -> None:
    """Validate model data before saving."""
    super().clean()
    self._validate_submitted_data()
    self._validate_page_reference()

def _validate_submitted_data(self) -> None:
    """Validate that submitted_data is properly formatted."""
    if not isinstance(self.submitted_data, dict):
        raise ValidationError(_("Submitted data must be a dictionary"))

    if not self.submitted_data:
        raise ValidationError(_("Submitted data cannot be empty"))

def _validate_page_reference(self) -> None:
    """Validate that page_id references an existing page."""
    if self.page_id:
        from wagtail.models import Page
        if not Page.objects.filter(id=self.page_id).exists():
            raise ValidationError(_("Referenced page does not exist"))
```

## 6. Performance Optimizations

### 6.1 Database Query Optimization
**Issue**: `get_preview_url()` method performs database query every time it's called.

**Recommendation**: Add caching or use select_related/prefetch_related.

```python
from django.core.cache import cache
from django.conf import settings

def get_preview_url(self) -> Optional[str]:
    """Get preview URL if page exists (with caching)."""
    if not self.page_id:
        return None

    cache_key = f"submission_preview_url_{self.page_id}"
    cached_url = cache.get(cache_key)

    if cached_url is not None:
        return cached_url

    try:
        from wagtail.models import Page
        page = Page.objects.get(id=self.page_id)
        url = page.get_full_url()
        cache.set(cache_key, url, timeout=getattr(settings, 'SUBMISSION_URL_CACHE_TIMEOUT', 3600))
        return url
    except Page.DoesNotExist:
        cache.set(cache_key, None, timeout=300)  # Cache negative result for shorter time
        return None
```

### 6.2 Bulk Operations Support
**Issue**: No support for bulk operations on submissions.

**Recommendation**: Add class methods for bulk operations.

```python
@classmethod
def bulk_mark_processed(cls, submission_ids: List[int]) -> int:
    """Mark multiple submissions as processed in a single query."""
    from django.utils import timezone

    updated_count = cls.objects.filter(
        id__in=submission_ids,
        processed=False
    ).update(
        processed=True,
        processed_date=timezone.now()
    )

    return updated_count
```

## 7. Security Considerations

### 7.1 Data Sanitization
**Issue**: No sanitization of user-submitted data before storage or display.

**Recommendation**: Add data sanitization methods.

```python
import bleach
from django.utils.html import escape

def sanitize_submitted_data(self) -> None:
    """Sanitize submitted data to prevent XSS and other attacks."""
    if isinstance(self.submitted_data, dict):
        self.submitted_data = self._sanitize_dict(self.submitted_data)

def _sanitize_dict(self, data: dict) -> dict:
    """Recursively sanitize dictionary values."""
    sanitized = {}
    for key, value in data.items():
        if isinstance(value, str):
            sanitized[key] = bleach.clean(value, strip=True)
        elif isinstance(value, dict):
            sanitized[key] = self._sanitize_dict(value)
        elif isinstance(value, list):
            sanitized[key] = [
                bleach.clean(item, strip=True) if isinstance(item, str) else item
                for item in value
            ]
        else:
            sanitized[key] = value
    return sanitized
```

### 7.2 Access Control
**Issue**: No built-in access control for sensitive submission data.

**Recommendation**: Add permission checking methods.

```python
def can_view(self, user) -> bool:
    """Check if user can view this submission."""
    if user.is_superuser:
        return True

    return user.has_perm('contact.view_contactsubmission')

def can_export(self, user) -> bool:
    """Check if user can export this submission."""
    return user.has_perm('contact.can_export')
```

## 8. Additional Recommendations

### 8.1 Add Model Managers
**Recommendation**: Create custom managers for common queries.

```python
class ContactSubmissionManager(models.Manager):
    def processed(self):
        return self.filter(processed=True)

    def pending(self):
        return self.filter(processed=False)

    def by_form(self, form_id: str):
        return self.filter(form_id=form_id)

    def recent(self, days: int = 7):
        from django.utils import timezone
        from datetime import timedelta

        cutoff_date = timezone.now() - timedelta(days=days)
        return self.filter(submission_date__gte=cutoff_date)

# Add to model
objects = ContactSubmissionManager()
```

### 8.2 Add Model Signals
**Recommendation**: Use Django signals for automated processing.

```python
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=ContactSubmission)
def handle_new_submission(sender, instance, created, **kwargs):
    """Handle new submission creation."""
    if created:
        # Send notification email
        # Log submission
        # Trigger automated processing
        pass
```

## Implementation Priority

1. **High Priority**: Type hints, error handling, data sanitization
2. **Medium Priority**: Extract constants, improve method organization, add caching
3. **Low Priority**: Design patterns implementation, bulk operations, custom managers

These improvements will significantly enhance the code's maintainability, security, and performance while maintaining existing functionality.
