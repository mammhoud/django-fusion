# django-osoul Usage Guide

`django-osoul` is the search and full-text indexing library for the structa.cloud monorepo. It provides site-wide search across Django models with minimal configuration.

## Installation

```bash
uv pip install -e applications/libs/django-osoul/
```

## Add to INSTALLED_APPS

```python
INSTALLED_APPS = [
    ...
    'django_osoul',
]
```

## Register Models for Search

```python
# In your app's apps.py or models.py
from django_osoul import search_registry

search_registry.register(
    model=BlogPost,
    fields=['title', 'body', 'tags__name'],
    label='Blog Post',
)
```

## Search Query

```python
from django_osoul import search

results = search(query="python tutorial", website="ctc-research.com")
# Returns: [{'model': 'BlogPost', 'pk': 1, 'title': '...', 'url': '...'}, ...]
```

## URL Configuration

```python
# urls.py
from django_osoul.urls import urlpatterns as grep_urls

urlpatterns += grep_urls
```

Default search endpoint: `GET /search/?q=<query>`

## Template Tag

```html
{% load grep_tags %}

<form action="{% grep_search_url %}" method="get">
  <input type="search" name="q" placeholder="Search...">
</form>
```

## Notes

- Search is case-insensitive and accent-folded
- Results are ranked by relevance (title match > body match)
- Configure `GREP_MIN_QUERY_LENGTH = 3` to prevent single-character queries
