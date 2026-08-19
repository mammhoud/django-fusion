# Django-Fusion ViewSet Integration Guide

## Overview

This guide explains how to use django-fusion ViewSets with Wagtail pages and comp tags.

## Available ViewSets

### ComponentViews

Base class for component-based views that work with the `comp` template tag system.

```python
from django_fusion.site import ComponentViews

class MyComponentViewSet(ComponentViews):
    component_dir = "components/myapp"
    
    def get_component(self, component_name, **context):
        return self.render_component(component_name, context)
```

### PageHandler

Handler for Wagtail pages with HTMX support.

```python
from django_fusion.site import PageHandler

class MyPageHandler(PageHandler):
    template_base = "pages/base.html"
    htmx_template_base = "pages/htmx/"
    
    def get_page(self, slug):
        from wagtail.models import Page
        return Page.objects.get(slug=slug)
```

### HTMXPaginationMixin

Mixin for adding HTMX pagination support to views.

```python
from django_fusion.site import HTMXPaginationMixin

class MyPaginatedView(HTMXPaginationMixin, TemplateView):
    template_name = "list.html"
    
    def get_queryset(self):
        return MyModel.objects.all()
```

## Integration with Wagtail Pages

### Page Component ViewSet

```python
# core/precis-ctc/www/apps/viewsets.py
from django_fusion.site import ComponentViews
from wagtail.models import Page

class PageComponentViewSet(ComponentViews):
    '''Component viewset for Wagtail pages'''
    component_dir = "components/pages"
    
    def get_page_components(self, page):
        '''Get components for a page'''
        return self.get_components(f"pages/{page.slug}")
    
    def get_pages_list(self, **kwargs):
        '''Get paginated pages list'''
        return Page.objects.live().public().order_by('-first_published_at')
```

### Site Context with ViewSets

```python
# core/precis-ctc/site.py
from django_fusion.site import ComponentViews, PageHandler
from django_fusion.site.views.tags import register
from wagtail.models import Page

@register('site_pages')
def site_pages(context):
    '''Register site pages for template usage'''
    return Page.objects.live().public().order_by('title')

@register('page_sections')
def page_sections(context, page):
    '''Register page sections for template usage'''
    return page.specific.get_sections()
```

## Using ViewSets with Templates

### Basic Template with ViewSet

```django
{# templates/pages/home.html #}
{% extends "base.html" %}
{% load comp %}
{% load site_tags %}

{% block content %}
    <h1>{{ page.title }}</h1>
    
    {# Use site_pages from register decorator #}
    {% with pages=site_pages %}
        {% for p in pages %}
            <a href="{% pageurl p %}">{{ p.title }}</a>
        {% endfor %}
    {% endwith %}
    
    {# Use page_sections from register decorator #}
    {% with sections=page_sections page=page %}
        {% comp "pages.home.sections.list" sections=sections / %}
    {% endwith %}
{% endblock %}
```

### HTMX Fragment Requests with ViewSet

```python
# core/precis-ctc/www/apps/views.py
from django_fusion.site import ComponentViews, HtmxDetails
from django_fusion.site.response import HttpResponseClientRedirect
from django.views.generic import TemplateView

class PageDetailView(TemplateView):
    template_name = "pages/detail.html"
    
    def get(self, request, *args, **kwargs):
        self.page = self.get_page()
        htmx = HtmxDetails(request)
        
        if htmx.target == 'main-content':
            # HTMX request - return only fragment
            self.template_name = "pages/detail_partial.html"
        
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page'] = self.page
        
        # Add component data
        viewset = ComponentViews()
        context['components'] = viewset.get_components('pages/detail')
        
        return context
```

## ViewSet Methods

### ComponentViews Methods

- `get_components(component_dir)`: Get all components in a directory
- `render_component(name, context)`: Render a component with context
- `get_component_path(name)`: Get the path to a component template

### PageHandler Methods

- `get_page(slug)`: Get a page by slug
- `get_pages(**filters)`: Get pages with optional filters
- `render_page(page, template)`: Render a page with specific template

### HTMXPaginationMixin Methods

- `get_paginated_queryset()`: Get paginated queryset
- `get_pagination_template()`: Get template for pagination
- `handle_htmx_pagination(request)`: Handle HTMX pagination requests

## Complete Example: Site with ViewSets

### 1. Define ViewSet

```python
# core/precis-ctc/www/apps/viewsets.py
from django_fusion.site import ComponentViews, PageHandler
from django_fusion.site.plugins import HtmxDetails
from wagtail.models import Page

class SiteComponentViewSet(ComponentViews):
    '''Component viewset for site-wide components'''
    component_dir = "components/site"
    
    def get_header(self):
        return self.render_fragment('header')
    
    def get_footer(self):
        return self.render_fragment('footer')
    
    def get_pages_list(self, **kwargs):
        return Page.objects.live().public().order_by('-first_published_at')
    
    def get_page_by_slug(self, slug):
        return Page.objects.get(slug=slug)

class SitePageHandler(PageHandler):
    '''Page handler for site pages'''
    template_base = "pages/base.html"
    htmx_template_base = "pages/htmx/"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pages'] = self.get_pages(**kwargs)
        return context
```

### 2. Create Site Context Tags

```python
# core/precis-ctc/site.py
from django_fusion.site import ComponentViews, PageHandler
from django_fusion.site.views.tags import register
from wagtail.models import Page

@register('site_pages')
def site_pages(context):
    '''Register site pages for template usage'''
    return Page.objects.live().public().order_by('title')

@register('page_sections')
def page_sections(context, page):
    '''Register page sections for template usage'''
    return page.specific.get_sections()
```

### 3. Create Component Templates

```django
{# templates/components/site/header.html #}
{% load comp %}
{% load wagtailcore_tags %}

<header class="site-header">
    <nav class="nav-main">
        <a href="/" class="nav-logo">Site Logo</a>
        <ul class="nav-list">
            {% for page in site_pages %}
                <li class="nav-item">
                    <a href="{% pageurl page %}" class="nav-link">
                        {{ page.title }}
                    </a>
                </li>
            {% endfor %}
        </ul>
    </nav>
</header>
```

### 4. Use in Pages

```django
{# templates/pages/home.html #}
{% extends "base.html" %}
{% load comp %}

{% block content %}
    {# Load header component #}
    {% comp "site.header" / %}
    
    {# Main content #}
    <main class="content">
        <h1>{{ page.title }}</h1>
        {{ page.body }}
        
        {# Load pages list #}
        {% comp "site.pages_list" pages=pages / %}
    </main>
    
    {# Load footer component #}
    {% comp "site.footer" / %}
{% endblock %}
```

## HTMX Integration with ViewSets

### HTMX Fragment Request

```django
{# In template #}
<a href="{% url 'page_fragment' page.id 'content' %}"
   hx-get="{% url 'page_fragment' page.id 'content' %}"
   hx-target="#main-content"
   hx-swap="innerHTML">
    Load Content
</a>

<div id="main-content"></div>
```

### ViewSet Handler for HTMX

```python
# core/precis-ctc/www/apps/htmx.py
from django_fusion.site import ComponentViews, HtmxDetails
from django_fusion.site.response import HttpResponseClientRedirect
from django.views.generic import View

class PageFragmentView(View):
    '''View for HTMX fragment requests'''
    
    def get(self, request, page_id, fragment):
        htmx = HtmxDetails(request)
        
        # Get page
        from wagtail.models import Page
        page = Page.objects.get(id=page_id)
        
        # Create viewset
        viewset = ComponentViews()
        
        # Get fragment
        fragment_content = viewset.render_fragment(
            f'pages/{page.slug}/{fragment}',
            page=page
        )
        
        if htmx.request:
            # HTMX request - return fragment only
            return HttpResponse(fragment_content)
        
        # Full request - return full page
        return render(request, 'pages/detail.html', {
            'page': page,
            'content': fragment_content
        })
```

## Benefits of Using ViewSets

1. **Separation of Concerns**: Components separated from logic
2. **Reusability**: Components can be reused across pages
3. **HTMX Support**: Built-in support for HTMX fragment requests
4. **Context Isolation**: Each component has its own context
5. **Testability**: Components can be tested independently

## Migration from Traditional Views

### Before (Traditional View)

```python
# views.py
def home(request):
    pages = Page.objects.live().public()
    return render(request, 'home.html', {'pages': pages})
```

### After (ViewSet-Based)

```python
# viewsets.py
from django_fusion.site import ComponentViews

class HomeComponentViewSet(ComponentViews):
    def get_pages(self):
        return Page.objects.live().public()
    
    def render_home(self, request):
        return self.render_component('home', {
            'pages': self.get_pages()
        })
```

### Template Updates

```django
{# Before #}
{% for page in pages %}
    {{ page.title }}
{% endfor %}

{# After #}
{% comp "home.pages_list" pages=pages / %}
```
