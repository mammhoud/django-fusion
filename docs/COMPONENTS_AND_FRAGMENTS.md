# Component and Fragment Usage Guide

## Overview

This guide covers using django-fusion and crafts-ai component systems with Wagtail pages.

## Directory Structure

```
applications/<site>/
├── templates/
│   ├── components/           # Component templates
│   │   ├── base/             # Base fragments
│   │   ├── blocks/           # StreamField blocks
│   │   └── pages/            # Page-specific fragments
│   └── pages/                # Page templates
│       ├── base.html         # Base page template
│       └── home/             # Home page fragments
│           ├── sections/     # Page sections
│           └── main.html     # Main content
```

## Comp Tags Usage

### Basic Component Usage

```django
{% load comp %}
{% comp "component.name" arg1=value arg2=value / %}
```

### Fragment Separation

```django
{% load comp %}
{# Main page template #}
{% comp "pages.home.main" / %}

{# Section fragment #}
{% comp "pages.home.sections.slider" / %}

{# HTMX fragment requests #}
{% comp "pages.home.sections.content" fragment="content" / %}
```

### HTMX Fragment Requests

```django
{# In component template - check for HTMX request #}
{% if request.htmx %}
    {# Return only the fragment #}
    {% comp "components.partials.fragment" / %}
{% else %}
    {# Return full page #}
    {% include "pages/base.html" %}
{% endif %}
```

## Notification Component

The shared notification component is located at `applications/assets/templates/plugins/notifications/notification.html`.

Include it in `base.html` before `</body>`:

```django
{% include "plugins/notifications/notification.html" %}
```

## ViewSet Integration

### Site.py with ViewSets

```python
# applications/<site>/site.py
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

### Component ViewSet Pattern

```python
# applications/<site>/www/apps/viewsets.py
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

## SPA Page Pattern

### Single Page Application Template

```django
{# pages/spa/base.html #}
{% extends "base.html" %}
{% load comp %}
{% load htmx %}

{% block content %}
    <div id="spa-container" hx-target="this" hx-swap="outerHTML">
        {% comp "spa.navbar" / %}
        
        <main id="main-content">
            {% comp "spa.content" page=page / %}
        </main>
        
        {% comp "spa.footer" / %}
    </div>
{% endblock %}

{% block extra_js %}
    <script>
        // SPA navigation with HTMX
        document.addEventListener('htmx:configRequest', function(evt) {
            evt.detail.headers['X-HX-Current-URL'] = window.location.href;
        });
    </script>
{% endblock %}
```

## Navigation Pattern

### Dynamic Navigation

```django
{# templates/components/navigation/main.html #}
{% load wagtailcore_tags %}
{% load comp %}

<nav class="main-nav">
    <ul class="nav-list">
        <li class="nav-item">
            <a href="/" class="nav-link {% if request.resolver_match.url_name == 'home' %}active{% endif %}">
                Home
            </a>
        </li>
        
        {% for page in site_pages %}
            <li class="nav-item">
                <a href="{% pageurl page %}" 
                   class="nav-link"
                   hx-get="{% url 'page_section' page.id 'content' %}"
                   hx-target="#main-content">
                    {{ page.title }}
                </a>
            </li>
        {% endfor %}
    </ul>
</nav>
```

## Fragment Naming Convention

Follow this naming pattern for fragments:

```
component.category.subcategory.name
```

Examples:
- `pages.home.main` - Main home page content
- `pages.home.sections.slider` - Slider section
- `components.cards.page_card` - Page card component
- `components.blocks.text_block` - Text block

## HTMX Events

Common HTMX events for fragments:

```javascript
// After fragment is loaded
document.addEventListener('htmx:afterOnLoad', function(evt) {
    console.log('Fragment loaded:', evt.detail.xhr.response);
});

// Before request
document.addEventListener('htmx:beforeRequest', function(evt) {
    console.log('Requesting:', evt.detail.requestConfig);
});

// After swap
document.addEventListener('htmx:afterSwap', function(evt) {
    console.log('Content swapped');
});
```

## Migration from Include to Comp

1. Add `{% load comp %}` at the top of the template
2. Replace `{% include "path/to/template.html" %}` with `{% comp "component.name" / %}`
3. Create corresponding ComponentViewSet if needed
4. Use HTMX attributes on comp tags for dynamic loading
