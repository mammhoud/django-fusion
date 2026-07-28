# Utility Functions

Django-grep provides utility functions for common tasks like text manipulation, validation, datetime formatting, and HTTP responses.

## Table of Contents

- [Text Utilities](#text-utilities)
- [Validators](#validators)
- [Datetime Utilities](#datetime-utilities)
- [Response Helpers](#response-helpers)

---

## Text Utilities

### slugify_unique

Generate unique slug for a model instance.

**Usage:**
```python
from django_fusion.utils import slugify_unique
from myapp.models import Article

slug = slugify_unique(Article, "My Article Title")
# Returns: "my-article-title" or "my-article-title-2" if exists
```

**Parameters:**
- `model_class` - Django model class
- `text` - Text to slugify
- `slug_field` - Name of slug field (default: 'slug')
- `max_length` - Maximum slug length (default: 50)

**Returns:** Unique slug string

---

### truncate_words

Truncate text to specified number of words.

**Usage:**
```python
from django_fusion.utils import truncate_words

text = "This is a very long text that needs to be truncated"
result = truncate_words(text, 5)
# Returns: "This is a very long..."
```

**Parameters:**
- `text` - Text to truncate
- `num_words` - Maximum number of words (default: 50)
- `suffix` - Suffix to add if truncated (default: '...')

**Returns:** Truncated text string

---

## Validators

### validate_email_format

Validate email format using regex.

**Usage:**
```python
from django_fusion.utils import validate_email_format

is_valid = validate_email_format("user@example.com")
# Returns: True

is_valid = validate_email_format("invalid-email")
# Returns: False
```

**Parameters:**
- `email` - Email address to validate

**Returns:** Boolean (True if valid, False otherwise)

---

### validate_email_domain

Validate email domain against whitelist.

**Usage:**
```python
from django_fusion.utils import validate_email_domain

allowed = ["example.com", "test.com"]
is_valid = validate_email_domain("user@example.com", allowed)
# Returns: True

is_valid = validate_email_domain("user@other.com", allowed)
# Returns: False
```

**Parameters:**
- `email` - Email address to validate
- `allowed_domains` - List of allowed domain names

**Returns:** Boolean (True if domain is allowed, False otherwise)

---

## Datetime Utilities

### format_relative_time

Format datetime as relative time (e.g., '2 hours ago').

**Usage:**
```python
from django_fusion.utils import format_relative_time
from django.utils import timezone
from datetime import timedelta

dt = timezone.now() - timedelta(hours=2)
result = format_relative_time(dt)
# Returns: "2 hours ago"
```

**Parameters:**
- `dt` - Datetime object to format

**Returns:** Human-readable relative time string

**Examples:**
- 30 seconds ago → "just now"
- 5 minutes ago → "5 minutes ago"
- 2 hours ago → "2 hours ago"
- 3 days ago → "3 days ago"
- 2 months ago → "2 months ago"
- 1 year ago → "1 year ago"

---

### format_duration

Format seconds as human-readable duration.

**Usage:**
```python
from django_fusion.utils import format_duration

result = format_duration(3665)
# Returns: "1h 1m 5s"

result = format_duration(125)
# Returns: "2m 5s"

result = format_duration(45)
# Returns: "45s"
```

**Parameters:**
- `seconds` - Number of seconds

**Returns:** Formatted duration string

---

## Response Helpers

### success_response

Return standardized success JSON response.

**Usage:**
```python
from django_fusion.utils import success_response

return success_response(
    data={"id": 1, "name": "John"},
    message="User created successfully"
)
```

**Parameters:**
- `data` - Data dictionary (default: {})
- `message` - Success message (default: "Success")
- `status` - HTTP status code (default: 200)

**Returns:** JsonResponse with format:
```json
{
    "status": "success",
    "message": "User created successfully",
    "data": {"id": 1, "name": "John"}
}
```

---

### error_response

Return standardized error JSON response.

**Usage:**
```python
from django_fusion.utils import error_response

return error_response(
    message="Validation failed",
    errors={"email": "Invalid format"},
    status=400
)
```

**Parameters:**
- `message` - Error message
- `errors` - Dictionary of field errors (default: {})
- `status` - HTTP status code (default: 400)

**Returns:** JsonResponse with format:
```json
{
    "status": "error",
    "message": "Validation failed",
    "errors": {"email": "Invalid format"}
}
```

---

## Complete Examples

### Article Slug Generation

```python
from django_fusion.utils import slugify_unique
from myapp.models import Article

def create_article(title, content):
    slug = slugify_unique(Article, title)
    article = Article.objects.create(
        title=title,
        slug=slug,
        content=content
    )
    return article
```

### Email Validation

```python
from django_fusion.utils import validate_email_format, validate_email_domain

def validate_user_email(email):
    # Check format
    if not validate_email_format(email):
        return False, "Invalid email format"

    # Check domain
    allowed_domains = ["company.com", "partner.com"]
    if not validate_email_domain(email, allowed_domains):
        return False, "Email domain not allowed"

    return True, "Email is valid"
```

### API Response Handling

```python
from django_fusion.utils import success_response, error_response
from django.views import View

class UserAPIView(View):
    def post(self, request):
        try:
            # Create user
            user = User.objects.create(
                email=request.POST.get("email"),
                name=request.POST.get("name")
            )

            return success_response(
                data={"id": user.id, "email": user.email},
                message="User created successfully",
                status=201
            )

        except Exception as e:
            return error_response(
                message="Failed to create user",
                errors={"detail": str(e)},
                status=400
            )
```

---

## Related Documentation

- [Model Mixins](models.md)
- [View Mixins](views.md)
- [Template Tags](templatetags.md)
