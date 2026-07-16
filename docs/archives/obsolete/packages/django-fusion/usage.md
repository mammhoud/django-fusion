# django-fusion Usage Guide

`django-fusion` is the shared site utility library for the structa.cloud monorepo. It provides language detection, file utilities, context processors, and site management helpers.

## Installation

The package is installed as an editable local dependency from `core/libs/django-fusion/`:

```bash
uv pip install -e core/libs/django-fusion/
```

## Language Utilities

```python
from django_fusion.site.utils import get_language_code, detect_language

# Detect language from request
lang = detect_language(request)  # returns 'en', 'ar', 'fr', etc.
```

## File Utilities

```python
from django_fusion.site.utils import get_file_extension, safe_filename

ext = get_file_extension("document.pdf")   # → 'pdf'
name = safe_filename("My Report (2026).pdf")  # → 'my_report_2026.pdf'
```

## Context Processors

Add to `TEMPLATES[0]['OPTIONS']['context_processors']` in your site settings:

```python
'django_fusion.context_processors.site_context',
'django_fusion.context_processors.language_context',
```

## Language Switcher

```python
from django_fusion.site._language import LanguageSwitcher

switcher = LanguageSwitcher(request)
available = switcher.get_available_languages()
current = switcher.get_current_language()
```

## Site Settings

```python
from django_fusion.site import SiteSettings

settings = SiteSettings.for_request(request)
theme = settings.theme   # 'light' | 'dark'
```

## Import Path Reference

| Old path (utilities.py) | New path (django-fusion) |
|------------------------|------------------------|
| `utilities.get_file_ext` | `django_fusion.site.utils.get_file_extension` |
| `utilities.detect_lang` | `django_fusion.site.utils.detect_language` |
| `utilities.safe_name` | `django_fusion.site.utils.safe_filename` |

## Notes

- Phase 3 migrated `core/utilities.py` into this package
- Language switching reference files: `/data/refrences/django-fusion/django_fusion/site/_language.py`
- Phase 7 will complete the language switcher component implementation
