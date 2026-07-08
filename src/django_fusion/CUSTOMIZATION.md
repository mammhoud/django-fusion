# Django-Osoul Customization Guide

This document describes how to customize django-fusion components for your project.

## Dynamic HTML Component Rendering

### Overview
The dynamic HTML component rendering feature allows rendering uploaded HTML files as Django components.

### Customization

To override the default fragment rendering, create a custom template at:

```
www/components/base_fragment.html
```

This template will be used instead of the default django-fusion fragment template.

### Removing Dynamic Rendering

If you don't need dynamic HTML file rendering:

1. Remove the custom template:
   ```
   rm www/core/templates/components/base/dynamic.html
   ```

2. Remove the custom templatetag:
   ```
   rm plugins/accounts/templatetags/custom_component_tags.py
   ```

3. Remove the renderer:
   ```
   rm www/apps/accounts/renderers.py
   ```

### Using base_fragment.html

Create `www/components/base_fragment.html` in your project to customize fragment rendering:

```html
{% load component_tags %}
<{{ tag_name }} {{ attributes }}>
{{ content }}
</{{ tag_name }}>
```

This overrides the default django-fusion fragment template.
