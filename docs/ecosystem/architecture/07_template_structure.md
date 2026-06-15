# Template Structure Documentation

## Overview

Templates follow a hierarchical structure with base templates and reusable components.

## Template Directory Structure

```
templates/
├── base.html              # Master template
├── base_auth.html         # Auth pages base
├── components/            # Reusable components
│   ├── modal.html
│   ├── card.html
│   ├── navbar.html
│   └── footer.html
├── auth/                  # Auth templates
│   ├── login.html
│   ├── register.html
│   └── password_reset.html
├── account/               # Account templates
│   ├── dashboard.html
│   ├── profile.html
│   └── settings.html
├── lms/                   # LMS templates
│   ├── course_list.html
│   ├── course_detail.html
│   └── lesson.html
└── blog/                  # Blog templates
    ├── post_list.html
    └── post_detail.html
```

## Base Template Hierarchy

### base.html

The master template that all other templates extend.

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}{% endblock %}</title>
    {% block extra_css %}{% endblock %}
</head>
<body>
    {% include 'components/navbar.html' %}

    <main>
        {% block content %}{% endblock %}
    </main>

    {% include 'components/footer.html' %}

    {% block extra_js %}{% endblock %}
</body>
</html>
```

### base_auth.html

Base template for authentication pages.

```html
{% extends 'base.html' %}

{% block content %}
<div class="auth-container">
    <div class="auth-card">
        {% block auth_content %}{% endblock %}
    </div>
</div>
{% endblock %}
```

## Template Inheritance

### Extending Base Template

```html
{% extends 'base.html' %}

{% block title %}My Page{% endblock %}

{% block content %}
<h1>Welcome to My Page</h1>
{% endblock %}
```

### Including Components

```html
{% include 'components/card.html' with title="Hello" content="World" %}
```

## Template Tags

### Custom Tags

```python
# templatetags/my_tags.py
@register.simple_tag
def get_greeting(name):
    return f"Hello, {name}!"

@register.inclusion_tag('components/badge.html')
def show_badge(text, color='primary'):
    return {'text': text, 'color': color}
```

### Usage

```html
{% load my_tags %}

{% get_greeting "John" %}

{% show_badge "New" "success" %}
```

## HTMX Template Patterns

### Fragment Rendering

```html
<!-- Full page load -->
{% extends 'base.html' %}

{% block content %}
<div id="content">
    {% include 'lms/course_list.html' %}
</div>
{% endblock %}

<!-- HTMX partial -->
{% block htmx_content %}
<div id="course-list">
    {% for course in courses %}
        {% include 'lms/course_card.html' %}
    {% endfor %}
</div>
{% endblock %}
```

### HTMX Response Headers

```python
def my_view(request):
    response = render(request, 'partial.html')
    response['HX-Trigger'] = '{"showNotification": {"message": "Saved!"}}'
    return response
```

## Wagtail Templates

### Page Templates

```html
{% extends "base.html" %}
{% load wagtailcore_tags wagtailimages_tags %}

{% block content %}
{% image page.featured_image width-800 %}
<h1>{{ page.title }}</h1>
{{ page.body }}
{% endblock %}
```

### StreamField Blocks

```html
{% block content %}
{% for block in page.body %}
    {% if block.block_type == 'heading' %}
        <h{{ block.value.level }}>{{ block.value.text }}</h{{ block.value.level }}>
    {% elif block.block_type == 'paragraph' %}
        <p>{{ block.value }}</p>
    {% endif %}
{% endfor %}
{% endblock %}
```

## Best Practices

1. **Use blocks** - Define reusable sections with `{% block %}`
2. **Keep it DRY** - Use includes for repeated content
3. **Organize by feature** - Group related templates
4. **Use template tags** - Move logic to custom tags
5. **Test HTMX responses** - Ensure partials render correctly
