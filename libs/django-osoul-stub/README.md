# django-osoul-stub

A stub/mock implementation of `django-osoul` for environments where the full package cannot be installed due to dependencies like Twilio or memory constraints.

This package provides all the classes and functions that projects depend on from `django_osoul` without requiring the actual package or its complex dependencies.

## Structure

- `models/` - Stub models including BaseModel and interaction models
- `site/` - Site-related classes and enums
- `site/enums/` - Environment and upload enums
- `managers/` - Manager classes
- `core/` - Core module with models

## Usage

Install this stub when `django-osoul` is not available:

```python
# In settings.py or during import
import django_osoul  # Uses stub instead of real package
```

All modules provide dynamic attribute resolution via `__getattr__` to handle any missing imports gracefully.
