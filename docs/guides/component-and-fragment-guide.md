# Component and Fragment Usage Guide

## Overview

This guide covers using django-fusion and ceptor-ai component systems with Wagtail pages.

## Directory Structure

```
core/<site>/
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

The shared notification component is located at `core/assets/templates/plugins/notifications/notification.html`.

Include it in `base.html` before `</body>`:

```django
{% include "plugins/notifications/notification.html" %}
```

## ViewSet Integration

### Site.py with ViewSets

```python
# core/<site>/site.py
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
# core/<site>/www/apps/viewsets.py
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

### Default Fragment Name Derivation

Every `RoutableComponent` and `FragmentComponent` has a `get_fragment_name()`
method that returns the dotted fragment identifier. The resolution order is:

1. If `fragment_name` is explicitly set on the class, it is returned as-is.
2. Otherwise, a default is derived from `route_name`:

   ```python
   route_name = "dashboard"
   # → get_fragment_name() returns "components.dashboard"
   # → template: "components/dashboard.html"
   ```

This default links the component to the package's `components/` template
directory (`django_fusion/comp/templates/components/`), which is registered
via `APP_DIRS` and `COMPONENT_DIRS` in the project template configuration.

### `template_name` and `fragment_name` Together

Both attributes work together to control which template is used:

- `template_name`: Full-page template (used when `strategy == "document"`,
  i.e. regular browser navigation)
- `fragment_name` (or `get_fragment_name()` default): Fragment template
  (used when `strategy == "fragment"`, i.e. HTMX/Unpoly requests)

If neither `fragment_name` nor `route_name` is set, `get_fragment_name()`
returns `None` and the full-page `template_name` is used for all requests.

Example with both set:

```python
class ProfileComponent(RoutableComponent):
    route_name = "profile"
    route_path = "profile/"
    template_name = "profile/detail.html"       # full-page
    fragment_name = "profile.fragments.detail"   # HTMX partial
    # → "profile/detail.html" for regular requests
    # → "profile/fragments/detail.html" for HTMX requests
```

Example with default derivation (no explicit `fragment_name`):

```python
class DashboardComponent(RoutableComponent):
    route_name = "dashboard"
    route_path = "dashboard/"
    template_name = "dashboard.html"   # full-page
    # fragment_name not set → defaults to "components.dashboard"
    # → "dashboard.html" for regular requests
    # → "components/dashboard.html" for HTMX requests
```

### Paginated View Fragment Name Derivation

`PaginatedComponentView` and `PaginatedListView` also implement
`get_fragment_name()` with their own default derivation strategies.

#### PaginatedComponentView

When `fragment_name` is not set, the default is derived from
`items_template` by converting the path to a dotted name:

```python
class MyPaginatedView(PaginatedComponentView):
    items_template = "components/items/list.html"
    # fragment_name not set
    # → get_fragment_name() returns "components.items.list"
    # → template: "components/items/list.html"
```

This links the paginated view's fragment to the same template that
renders its items, so HTMX requests automatically use the right partial.

#### PaginatedListView

When `fragment_name` is not set, the default is derived from the model's
`app_label` and `model_name`:

```python
class ArticleListView(PaginatedListView):
    model = Article  # app_label="blog", model_name="article"
    fragment_name = None  # explicitly unset to opt in
    # → get_fragment_name() returns "components.blog.article_list"
    # → template: "components/blog/article_list.html"
```

This links the paginated list fragment to a model-specific template in
the `components/` directory.

> **Note:** The base `PaginatedListView` sets
> `fragment_name = "components.paginated_list"` as a sensible default.
> Subclasses that want model-derived derivation must explicitly set
> `fragment_name = None` to opt in.

#### Derivation Priority Chain

For all paginated views, the resolution order is:

1. **Explicit `fragment_name`** — returned as-is if set.
2. **`model._meta`** (PaginatedListView only) —
   `f"components.{app_label}.{model_name}_list"`.
3. **`items_template`** (PaginatedComponentView and up) —
   path converted to dotted name (e.g. `"components/items/list.html"`
   → `"components.items.list"`).
4. **`None`** — falls back to the base mixin, which returns `None`.

Example showing the full chain:

```python
class ProductListView(PaginatedListView):
    model = Product       # app_label="shop", model_name="product"
    fragment_name = None  # unset → derives from model
    # → "components.shop.product_list"
    # → "components/shop/product_list.html"

class CustomListView(PaginatedListView):
    model = None          # no model
    fragment_name = None  # unset
    items_template = "shop/fragments/list.html"
    # → falls back to items_template → "shop.fragments.list"
    # → "shop/fragments/list.html"

class OverrideListView(PaginatedListView):
    model = Product
    fragment_name = "my.custom_list"  # explicit → always wins
    # → "my.custom_list"
    # → "my/custom_list.html"
```

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
