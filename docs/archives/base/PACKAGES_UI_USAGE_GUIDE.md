# Packages/UI - Component Usage Guide

## Quick Reference

All components in `packages/ui/` are **shared across all sites** (ctc-research, lms-demo, VResume).

### Available Components

| Component | Path | Purpose |
|-----------|------|---------|
| **HTMX Form** | `forms/htmx_form.html` | Generic form with HTMX + validation |
| **Base Modal** | `modals/base_modal.html` | Bootstrap modal wrapper |
| **Notifications** | `notifications/notification.html` | Toast & alert system |
| **Search Bar** | `search/search_bar.html` | HTMX search component |
| **HTMX Helpers** | `htmx/*.html` | Fragment, error, loading states |
| **Tables** | `tables/htmx_table.html` | HTMX-enabled tables |

---

## 1. HTMX Form

### Purpose
Generic form for all HTMX requests with error display and validation.

### Basic Usage
```django
{% include "forms/htmx_form.html" with
    form=my_form
    hx_url="/api/submit/"
    hx_target="#results"
    submit_label="Submit"
%}
```

### Parameters
```python
form              # Django form object (required)
hx_url            # HTMX POST URL (required)
hx_target         # Swap target selector
hx_swap           # Swap strategy (default: outerHTML)
hx_indicator      # Loading indicator selector
form_class        # CSS class for <form>
is_multipart      # Set True for file uploads
submit_label      # Submit button text
show_cancel       # Show cancel button (default: False)
cancel_label      # Cancel button text
cancel_attrs      # HTML attributes for cancel button
```

### Complete Example
```django
{# Course Enrollment Form #}
{% load static %}

<div id="enrollment-result"></div>

<button class="btn btn-primary" 
        hx-get="{% url 'lms:course_enrollment_form' course.id %}"
        hx-target="#enrollment-modal">
    Enroll Now
</button>

<div id="enrollment-modal">
    {% include "forms/htmx_form.html" with
        form=enrollment_form
        hx_url="{% url 'lms:course_enrollment_create' course.id %}"
        hx_target="#enrollment-result"
        hx_swap="innerHTML"
        submit_label="Enroll"
        show_cancel=True
        cancel_label="Close"
        form_class="enrollment-form"
    %}
</div>
```

### Field Types Supported
- Text inputs
- Email
- Password
- Textarea
- Select dropdowns
- Checkboxes
- Radio buttons
- File uploads (with `is_multipart=True`)

### Error Display
Automatic error display under each field:
```
Field Name
[input field]
⚠️ This field is required.
```

---

## 2. Base Modal

### Purpose
Bootstrap modal wrapper with blocks for easy customization.

### Basic Usage
```django
{% include "modals/base_modal.html" with
    modal_id="myModal"
    modal_title="My Title"
    modal_icon="bi-info-circle"
%}
```

### Parameters
```python
modal_id             # HTML ID (required)
modal_title          # Title text (required)
modal_icon           # Bootstrap icon class
modal_icon_color     # Icon color (e.g., 'text-primary')
modal_title_color    # Title color class
modal_size           # 'modal-lg', 'modal-sm', ''  (default: normal)
modal_centered       # Center vertically (default: True)
```

### Block Overrides
```django
{% block modal_icon_block %}
    {# Custom icon #}
{% endblock %}

{% block modal_title_block %}
    {# Custom title #}
{% endblock %}

{% block modal_content %}
    {# Main content #}
{% endblock %}

{% block modal_footer %}
    {# Custom footer or actions #}
{% endblock %}

{% block modal_actions %}
    {# Action buttons #}
{% endblock %}
```

### Complete Example
```django
{# Enrollment Modal #}
{% include "modals/base_modal.html" with
    modal_id="enrollmentModal"
    modal_title="Enroll in Course"
    modal_icon="bi-check-circle"
    modal_icon_color="text-success"
    modal_size="modal-lg"
    modal_centered=True
%}
    {% block modal_content %}
        <div class="enrollment-info">
            <p>{{ course.title }}</p>
            <p class="text-muted">{{ course.short_description }}</p>
            <hr>
            
            {% include "forms/htmx_form.html" with
                form=enrollment_form
                hx_url="/learning/enrollment/create/{{ course.id }}/"
                hx_target="#enrollment-result"
                submit_label="Enroll Now"
            %}
        </div>
    {% endblock %}
    
    {% block modal_actions %}
        <button type="button" class="btn btn-primary">
            Proceed to Payment
        </button>
    {% endblock %}
{% endinclude %}
```

### Triggering Modal
```html
<!-- Button Trigger -->
<button type="button" class="btn btn-primary" 
        data-bs-toggle="modal" data-bs-target="#enrollmentModal">
    Enroll Now
</button>

<!-- Or with HTMX -->
<button hx-get="/load-modal/" hx-target="body" hx-swap="beforeend">
    Open Modal
</button>
```

---

## 3. Notifications (Toasts & Alerts)

### Purpose
Display success/error/info/warning messages to users.

### Setup (Include Once)
```django
{% include "notifications/notification.html" %}
```

### Show Toast Notification
```javascript
showNotification('success', 'Success!', 'Enrolled successfully.');
showNotification('error', 'Error', 'Could not enroll.');
showNotification('warning', 'Warning', 'Limited seats available.');
showNotification('info', 'Info', 'Processing...');
```

### Show Alert Notification
```javascript
showAlert('success', 'Success!', 'Your changes have been saved.');
showAlert('error', 'Error', 'An error occurred.', 'See details below...');
```

### Django Messages Integration
Automatically converts Django messages to toasts:
```python
# View
messages.success(request, 'Enrolled successfully!')
messages.error(request, 'Enrollment failed.')
```

### HTMX Response
Display notification from HTMX response:
```html
<!-- Server response in HTMX -->
<div id="notification" hx-swap-oob="true"
     data-notification="success"
     data-title="Success"
     data-message="Enrolled successfully.">
</div>
```

---

## 4. Search Bar

### Purpose
HTMX-enabled search with live results.

### Basic Usage
```django
{% include "search/search_bar.html" with
    hx_url="/api/search/"
    hx_target="#results"
    name="q"
    placeholder="Search..."
%}
```

### Parameters
```python
hx_url           # Search endpoint URL (required)
hx_target        # Results container selector
name             # Form field name (default: 'q')
placeholder      # Placeholder text
value            # Pre-filled value
input_class      # CSS classes for input
show_button      # Show search button (default: False)
```

### Complete Example
```django
{# Course Search #}
<div class="search-section">
    {% include "search/search_bar.html" with
        hx_url="{% url 'lms:course_search_api' %}"
        hx_target="#course-results"
        name="q"
        placeholder="Search courses by title or instructor..."
    %}
    
    <div id="course-results">
        <!-- Results will appear here -->
    </div>
</div>
```

### Search Behavior
- Triggers on: Submit + keyup (debounced 500ms)
- Auto-searches as user types
- Sends field value to endpoint
- Receives HTML fragment or JSON

### Server Endpoint
```python
# Django view
def search_api(request):
    query = request.GET.get('q', '').strip()
    results = Course.objects.filter(title__icontains=query)
    return render(request, 'search_results.html', {'results': results})
```

---

## 5. HTMX Helpers

### Base Fragment
Wrapper for HTMX responses.

```django
{% include "htmx/base_fragment.html" %}
    <div class="fragment-content">
        <!-- Your content -->
    </div>
{% endinclude %}
```

### Error Handler
Display HTMX errors gracefully.

```django
{% include "htmx/error_handler.html" with
    error_code="500"
    error_message="Server error"
%}
```

### Loading States
Show loading indicator during HTMX requests.

```django
{% include "htmx/loading_states.html" with
    indicator_id="loading"
    spinner_type="border"  {# or 'grow' #}
%}
```

---

## 6. HTMX Tables

### Purpose
Sortable, paginated table with row actions.

### Basic Usage
```django
{% include "tables/htmx_table.html" with
    headers=table_headers
    rows=table_rows
    hx_url="/api/table/"
%}
```

### Example
```django
{# Enrollment Leads Table #}
{% include "tables/htmx_table.html" with
    headers="Email,Name,Status,Actions"
    rows=enrollment_leads
    hx_url="/api/enrollment-leads/"
    hx_target="#table-results"
%}
```

---

## Integration with Course System

### 1. Enrollment Modal
```django
{# plugins/templates/learning/_course_enrollment_modal.html #}
{% include "modals/base_modal.html" with
    modal_id="enrollmentModal"
    modal_title="Enroll in Course"
    modal_icon="bi-check-circle"
%}
    {% block modal_content %}
        {% include "forms/htmx_form.html" with
            form=enrollment_form
            hx_url="{% url 'lms:course_enrollment_create' course.id %}"
            hx_target="#enrollment-result"
            submit_label="Enroll"
        %}
    {% endblock %}
{% endinclude %}
```

### 2. Course Search
```django
{# In course catalog #}
{% include "search/search_bar.html" with
    hx_url="{% url 'lms:course_search_api' %}"
    hx_target="#course-results"
    placeholder="Search courses..."
%}
```

### 3. Success Message
```django
{# After enrollment #}
{% include "notifications/notification.html" %}

<script>
    showNotification('success', 'Enrolled!', 'You are now enrolled in this course.');
</script>
```

---

## Settings Configuration

Ensure `packages/ui/` is in template directories:

```python
# settings.py
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'packages/ui',        # ← Add this line
            BASE_DIR / 'plugins/templates',
            BASE_DIR / 'templates',
        ],
        'APP_DIRS': True,
        ...
    }
]
```

---

## CSS Classes Reference

### Form Classes
```
form__group         # Field container
form__label         # Label element
form__input         # Input field
form__input-wrapper # Input wrapper
form-text           # Help text
invalid-feedback    # Error message
```

### Modal Classes
```
modal               # Modal container
modal-header        # Header section
modal-title         # Title
modal-body          # Body content
modal-footer        # Footer
modal-lg            # Large size
modal-sm            # Small size
```

### Notification Classes
```
toast               # Toast notification
toast-header        # Header
toast-body          # Body
alert               # Alert box
alert-success       # Success variant
alert-danger        # Error variant
alert-warning       # Warning variant
```

---

## Common Patterns

### Pattern 1: Form + Modal
```django
<button hx-get="/enrollment-form/" hx-target="#modal">
    Enroll
</button>

<div id="modal">
    {% include "modals/base_modal.html" %}
        {% block modal_content %}
            {% include "forms/htmx_form.html" %}
        {% endblock %}
    {% endinclude %}
</div>
```

### Pattern 2: Search + Results
```django
{% include "search/search_bar.html" with hx_target="#results" %}

<div id="results">
    {% for item in items %}
        <!-- Results render here -->
    {% endfor %}
</div>
```

### Pattern 3: Form + Notification
```django
{% include "forms/htmx_form.html" %}

{% include "notifications/notification.html" %}

<script>
    // After form submission
    showNotification('success', 'Submitted!', 'Your form was accepted.');
</script>
```

---

## Troubleshooting

### Form Not Validating
- Check `csrf_token` is present
- Verify form object has errors
- Ensure hx_url is correct

### Modal Not Opening
- Check modal_id is unique
- Verify Bootstrap is loaded
- Use `data-bs-toggle="modal"`

### Search Not Working
- Check hx_url endpoint exists
- Verify response is HTML fragment
- Check browser console for errors

### Notifications Not Showing
- Include notification component
- Check notification.html is loaded
- Verify JavaScript is initialized

---

## Performance Tips

1. **Lazy Load Images** in forms
2. **Debounce Search** (built-in: 500ms)
3. **Paginate Tables** (built-in)
4. **Cache Modal Content** with HTMX
5. **Minimize CSS** for production

---

## Browser Support

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- ✅ Mobile browsers

---

## Best Practices

1. Always include `{% csrf_token %}` in forms
2. Use semantic HTML in modal content
3. Validate on both client and server
4. Handle errors gracefully
5. Show loading states during requests
6. Test on mobile devices

---

## Next Steps

1. ✅ Reference packages/ui in settings
2. ✅ Use components in your templates
3. ✅ Customize with block overrides
4. ✅ Handle responses in JavaScript
5. ✅ Test across devices

---

**Ready to use!** 🚀

All components are production-ready and tested across all sites.

