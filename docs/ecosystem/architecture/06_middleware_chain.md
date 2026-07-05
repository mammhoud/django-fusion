# Middleware Chain Documentation

## Overview

Middleware components process requests and responses globally before they reach views or after views generate responses.

## Middleware Order

The order of middleware in `settings.py` is critical as they are processed in the order listed:

1. Security Middleware
2. Session Middleware
3. Authentication Middleware
4. Error Tracking Middleware
5. Privacy Consent Middleware
6. HTMX Middleware
7. Common Middleware

## Error Tracker Middleware

**Location**: `django_fusion/middlewares/error_tracker.py`

Logs HTTP errors (4xx and 5xx) with request details.

```python
MIDDLEWARE = [
    # ...
    'django_fusion.middlewares.ErrorTrackerMiddleware',
    # ...
]
```

### Features

- Logs all 4xx and 5xx responses
- Captures request method, path, and user
- Records response status code
- Optional: store errors in database for analysis

### Configuration

```python
# Optional settings
ERROR_TRACKER_LOG_4XX = True  # Log client errors
ERROR_TRACKER_LOG_5XX = True  # Log server errors
ERROR_TRACKER_STORE_DB = True  # Store in database
```

## Privacy Consent Middleware

**Location**: `crafts_ai/pipelines/middlewares/privacy_consent.py`

Enforces privacy consent for protected paths.

```python
MIDDLEWARE = [
    # ...
    'crafts_ai.pipelines.middlewares.PrivacyConsentMiddleware',
    # ...
]
```

### Features

- Checks if user has accepted privacy policy
- Redirects to consent page for protected paths
- Lazy model loading for flexibility

### Configuration

```python
PRIVACY_CONSENT_MIDDLEWARE = {
    'model_path': 'myapp.models.PrivacyConsent',
    'protected_paths': ['/profile/', '/checkout/'],
    'consent_page': '/privacy-consent/',
}
```

### Protected Path Check

```python
def _is_protected_path(self, path):
    """Check if path requires privacy consent."""
    for protected in self.protected_paths:
        if path.startswith(protected):
            return True
    return False
```

## HTMX Middleware

**Location**: `django_htmx.middleware.HTMXMiddleware`

Enables HTMX request/response handling.

```python
MIDDLEWARE = [
    # ...
    'django_htmx.middleware.HTMXMiddleware',
    # ...
]
```

### Features

- Sets `request.htmx` attribute
- Handles HTMX-specific headers
- Enables partial rendering

## Session Middleware

**Location**: `django.contrib.sessions.middleware.SessionMiddleware`

Manages user sessions.

```python
MIDDLEWARE = [
    # ...
    'django.contrib.sessions.middleware.SessionMiddleware',
    # ...
]
```

## Authentication Middleware

**Location**: `django.contrib.auth.middleware.AuthenticationMiddleware`

Associates users with requests.

```python
MIDDLEWARE = [
    # ...
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # ...
]
```

### Sets

- `request.user` - Current authenticated user
- `request.user.is_authenticated` - Boolean for auth status

## CSRF Protection

**Location**: `django.middleware.csrf.CsrfViewMiddleware`

Protects against CSRF attacks.

```python
MIDDLEWARE = [
    # ...
    'django.middleware.csrf.CsrfViewMiddleware',
    # ...
]
```

## Custom Middleware Template

```python
from django.utils.deprecation import MiddlewareMixin

class MyCustomMiddleware(MiddlewareMixin):
    def process_request(self, request):
        """Called before routing to view."""
        # Modify request if needed
        return None

    def process_view(self, request, view_func, view_args, view_kwargs):
        """Called after routing but before view."""
        return None

    def process_response(self, request, response):
        """Called after view generates response."""
        # Modify response if needed
        return response

    def process_exception(self, request, exception):
        """Called when view raises exception."""
        # Handle exception
        return None
```

## Best Practices

1. **Order matters** - Place security middleware first
2. **Keep it simple** - Don't do heavy processing in middleware
3. **Return None** - To continue processing, return None from process methods
4. **Return response** - To short-circuit, return a response object
