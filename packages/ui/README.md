# UI Components Library

Reusable HTMX and Alpine.js UI components for all websites.

## Directory Structure

```
packages/ui/
├── README.md                    (this file)
├── __init__.py
├── forms/                       (Form components)
│   ├── htmx_form.html          # HTMX form integration
│   └── validation.html         # Form validation
├── htmx/                        (HTMX utilities)
│   ├── base_fragment.html      # Base HTMX fragment
│   ├── error_handler.html      # Error handling
│   └── loading_states.html     # Loading states
├── modals/                      (Modal dialogs)
│   ├── base_modal.html         # Base modal template
│   └── modal_trigger.html      # Modal trigger pattern
├── notifications/              (Notifications & toasts)
│   ├── notification.html       # Notification component
│   └── toast_templates.html    # Toast templates
├── search/                      (Search components)
│   └── search_bar.html         # Search bar widget
└── tables/                      (Table components)
    └── htmx_table.html         # HTMX table with sorting
```

## Components

### Forms (forms/)

**htmx_form.html**
- HTMX form integration
- Real-time validation
- Error display
- Auto-submit on change

**validation.html**
- Field validation indicators
- Error messages
- Success states

### HTMX Utilities (htmx/)

**base_fragment.html**
- Base HTMX fragment setup
- Common attributes
- Event handling

**error_handler.html**
- Error response handling
- Retry logic
- User feedback

**loading_states.html**
- Loading indicators
- Disabled states
- Progress feedback

### Modals (modals/)

**base_modal.html**
- Standard modal structure
- Close buttons
- Backdrop click handling

**modal_trigger.html**
- Trigger patterns
- HTMX integration
- Event handling

### Notifications (notifications/)

**notification.html**
- Main notification component
- Auto-close timers
- Multiple display options

**toast_templates.html**
- Success toast
- Error toast
- Warning toast
- Info toast

### Search (search/)

**search_bar.html**
- Search input
- HTMX autocomplete
- Recent searches
- Search results

### Tables (tables/)

**htmx_table.html**
- Sortable columns
- Pagination
- Row actions
- Inline editing

## Usage

### In Templates

Include components in your templates:

```html
{% load static %}

<!-- Include form -->
{% include "packages/ui/forms/htmx_form.html" with form=form %}

<!-- Include modal -->
{% include "packages/ui/modals/base_modal.html" with modal_id="myModal" %}

<!-- Include toast -->
<div class="toast success">
  {% include "packages/ui/notifications/toast_templates.html" %}
</div>

<!-- Include search -->
{% include "packages/ui/search/search_bar.html" with placeholder="Search..." %}

<!-- Include table -->
{% include "packages/ui/tables/htmx_table.html" with items=items %}
```

### Configuration

Add to Django settings.py:

```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # ... other context processors
            ],
        },
    },
]

# Include packages in app directories
INSTALLED_APPS = [
    # ... other apps
    'packages.ui',
]
```

### Styling

Components use Tailwind CSS classes. Include in your base template:

```html
<link rel="stylesheet" href="{% static 'css/tailwind.css' %}">
```

### JavaScript

Include HTMX and Alpine.js:

```html
<script src="https://unpkg.com/htmx.org@1.9.10"></script>
<script src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js" defer></script>
```

## Examples

### Form Integration

```html
<form hx-post="{% url 'form_submit' %}" hx-target="#results">
  {% include "packages/ui/forms/htmx_form.html" with form=form %}
  <button type="submit" class="btn">Submit</button>
</form>
```

### Modal with HTMX

```html
<button hx-get="{% url 'modal_content' %}" 
        hx-target="#modal-body"
        class="btn btn-primary">
  Open Modal
</button>

{% include "packages/ui/modals/base_modal.html" with modal_id="modal" %}
```

### Toast Notifications

```html
<div class="toast-container">
  <div class="toast success">
    {% include "packages/ui/notifications/toast_templates.html" with message="Success!" %}
  </div>
</div>
```

### Search with Autocomplete

```html
{% include "packages/ui/search/search_bar.html" with 
    hx_get="{% url 'search' %}"
    placeholder="Search courses..."
%}
```

### Sortable Table

```html
{% include "packages/ui/tables/htmx_table.html" with 
    items=courses
    columns="title|instructor|price"
    sortable=True
%}
```

## Customization

### Override Styles

Create custom CSS:

```css
.modal {
  @apply bg-white rounded-lg shadow-lg;
}

.modal.dark {
  @apply bg-gray-800 text-white;
}
```

### Extend Components

Create custom versions:

```html
<!-- custom_form.html -->
{% include "packages/ui/forms/htmx_form.html" %}
<div class="custom-footer">
  <!-- your content -->
</div>
```

## Best Practices

1. **Always include error handlers** - Use error_handler.html for HTMX calls
2. **Use loading states** - Provide visual feedback with loading_states.html
3. **Validate forms** - Use validation.html for client-side feedback
4. **Handle accessibility** - Include ARIA labels and roles
5. **Test all states** - Test success, error, and loading states

## Troubleshooting

### Components not showing
- Check Tailwind CSS is included
- Verify HTMX is loaded
- Check browser console for errors

### HTMX requests failing
- Check URL endpoints exist
- Verify CSRF token is included
- Check request method (GET/POST)

### Styling issues
- Clear browser cache
- Rebuild Tailwind CSS
- Check CSS specificity

## See Also

- [HTMX Documentation](https://htmx.org)
- [Alpine.js Documentation](https://alpinejs.dev)
- [Tailwind CSS Documentation](https://tailwindcss.com)

