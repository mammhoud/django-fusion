# Integration Guide

This guide explains how to integrate Django GREP into your Django project.

## Requirements

- Python 3.9+
- Django 4.0+
- Wagtail 6.0+

## Installation

```bash
pip install django-fusion
```

## Configuration

In your `settings.py`:

```python
INSTALLED_APPS = [
    # ...
    "wagtail.contrib.settings",
    "wagtail.contrib.table_block",
    "wagtail.contrib.typed_table_block",
    "wagtail.documents",
    "wagtail.embeds",
    "wagtail.images",
    "wagtail.search",
    "wagtail.snippets",
    "wagtail.sites",
    "wagtail.admin",
    "wagtail.users",
    "wagtail.locales",

    # Django GREP Packages
    "django_fusion.comp",
    "django_fusion.pipelines",
    # ...
]

# Ensure middleware includes
MIDDLEWARE = [
    # ...
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
]
```

## Component Usage

To use the components in a Wagtail Page:

```python
from wagtail.models import Page
from wagtail.fields import StreamField
from django_fusion.comp.blocks import streamBlocks

class MyPage(Page):
    content = StreamField(streamBlocks, use_json_field=True)

    content_panels = Page.content_panels + [
        FieldPanel("content"),
    ]
```

## Pipeline Models Usage

Inherit from the enhanced base models:

```python
from django_fusion.pipelines.models import DefaultBase

class Article(DefaultBase):
    title = models.CharField(max_length=200)
    # Automatically get:
    # - created_at, updated_at
    # - created_by, updated_by
    # - live, is_active
```
