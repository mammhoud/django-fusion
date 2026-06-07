# Generic Components Usage Guide

**Location:** `assets/templates/generic/`  
**Date:** June 7, 2026  
**Version:** 1.0.0  

---

## Table of Contents

1. [Overview](#overview)
2. [Components](#components)
3. [Notifications System](#notifications-system)
4. [Modals System](#modals-system)
5. [Forms System](#forms-system)
6. [Usage Patterns](#usage-patterns)
7. [Implementation Flows](#implementation-flows)
8. [Examples](#examples)
9. [Troubleshooting](#troubleshooting)

---

## Overview

The `assets/templates/generic/` directory contains reusable, consolidated UI components for notifications, toasts, popups, modals, and forms. These components:

✅ **Centralized** - Single source of truth for all UI patterns  
✅ **Reusable** - Can be used across all sites and applications  
✅ **Consistent** - Unified styling and behavior  
✅ **Well-Documented** - Clear usage patterns and examples  
✅ **HTMX-Compatible** - Works with AJAX and HTMX  
✅ **Bootstrap-Based** - Uses Bootstrap 5 styling  

### File Structure

```
assets/templates/generic/
├── _notifications.html      # Toasts, alerts, popups
├── _modals.html            # Modal dialogs
├── _forms.html             # Form templates
├── _form.html              # Generic form (legacy)
├── button.html             # Button components
├── _confirm_delete.html    # Confirmation modals
├── _list.html              # List templates
├── _detail.html            # Detail views
└── COMPONENTS_USAGE_GUIDE.md (this file)
```

---

## Components

### 1. Notifications (_notifications.html)

**Purpose:** Unified notification system for messages, toasts, alerts, and popups

**Includes:**
- Django messages fallback
- Toast container (top-right, auto-dismiss)
- Alert container (inline, persistent)
- Popup/modal container
- SSE connection status indicator

**Use When:**
- You need to display temporary notifications (toasts)
- You need persistent alerts with details
- You want modal-style popups with actions
- You're using Django messages

### 2. Modals (_modals.html)

**Purpose:** Reusable Bootstrap modal template

**Features:**
- Standard modal structure (header, body, footer)
- Icon support
- Multiple sizes (sm, md, lg, xl)
- Centered/scrollable options
- Custom content blocks
- Action buttons

**Use When:**
- You need dialogs for user interactions
- You want confirmation prompts
- You need forms in a modal
- You want consistent modal styling

### 3. Forms (_forms.html)

**Purpose:** Generic form template with HTMX support

**Supports:**
- Django form rendering
- HTMX integration
- Field validation display
- Error handling
- Multipart uploads
- Custom submit/cancel actions

**Use When:**
- You need to render Django forms
- You want HTMX AJAX submission
- You need field-level validation display
- You're implementing a standard form

---

## Notifications System

### Overview

The notifications system provides three types of notifications:

1. **Toasts** - Temporary, auto-dismiss (5 seconds)
2. **Alerts** - Persistent, requires manual dismissal
3. **Popups** - Modal-style, requires user interaction

### Toast System

#### Usage

```django
{% include "generic/_notifications.html" %}
```

#### JavaScript API

```javascript
// Create a success toast
showNotification({
    title: "Success",
    message: "Action completed successfully",
    level: "success",
    icon: "bi-check-circle-fill",
    duration: 5000
});

// Create an error toast
showNotification({
    title: "Error",
    message: "Something went wrong",
    level: "danger",
    icon: "bi-x-circle-fill"
});

// Create a warning toast
showNotification({
    title: "Warning",
    message: "Be careful!",
    level: "warning",
    icon: "bi-exclamation-triangle-fill"
});

// Create an info toast
showNotification({
    title: "Info",
    message: "Here's some information",
    level: "info",
    icon: "bi-info-circle-fill"
});
```

#### Toast Container

- **Position:** Top-right
- **Z-index:** 1055
- **Auto-dismiss:** 5 seconds (configurable)
- **Animation:** Fade in/out

#### Levels & Colors

| Level | Color | Icon | Usage |
|-------|-------|------|-------|
| success | Green | check-circle-fill | Success messages |
| danger | Red | x-circle-fill | Error messages |
| warning | Orange | exclamation-triangle-fill | Warnings |
| info | Blue | info-circle-fill | Information |

### Alert System

#### Usage

```django
{% include "generic/_notifications.html" %}
```

#### JavaScript API

```javascript
// Create a persistent alert
showAlert({
    title: "Important",
    message: "This is an important message",
    level: "warning",
    icon: "bi-exclamation-triangle",
    badge: "Action Required",
    details: "<p>Additional details about the alert</p>"
});
```

#### Features

- **Dismissible:** User can close with button
- **Details:** Collapsible additional information
- **Badge:** Optional badge for categorization
- **Icons:** Visual level indicators
- **Persistent:** Stays until dismissed

### Popup System

#### Usage

```javascript
// Create a popup
showPopup({
    title: "Confirm Action",
    message: "<p>Are you sure you want to continue?</p>",
    level: "warning",
    size: "modal-md",
    showCancel: true,
    actions: '<button class="btn btn-primary">Confirm</button>'
});
```

#### Features

- **Modal-style:** Requires user interaction
- **Custom Actions:** Add custom buttons
- **Sizes:** sm, md, lg, xl
- **Content:** Supports HTML content
- **Backdrop:** Static backdrop (can't dismiss by clicking outside)

---

## Modals System

### Overview

Generic modal template with full Bootstrap integration

### Structure

```
Modal
├── Header
│   ├── Title (with optional icon)
│   └── Close button
├── Body
│   └── Custom content
└── Footer
    ├── Cancel button (optional)
    └── Action buttons (custom)
```

### Basic Usage

```django
{% include "generic/_modals.html" with
    modal_id="myModal"
    modal_title="Modal Title"
    modal_icon="bi-person"
    modal_body_content="Your content here"
%}
```

### With Custom Content

```django
{% include "generic/_modals.html" with
    modal_id="editUserModal"
    modal_title="Edit User"
    modal_icon="bi-pencil"
    modal_icon_color="text-warning"
    modal_size="modal-lg"
    modal_centered=True
%}
    {% block modal_content %}
        <form method="POST">
            {% csrf_token %}
            {{ form.as_p }}
        </form>
    {% endblock %}
    {% block modal_actions %}
        <button type="button" class="btn btn-primary">Save</button>
    {% endblock %}
{% endblock %}
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| modal_id | string | required | Unique ID for the modal |
| modal_title | string | "" | Modal title text |
| modal_icon | string | "" | Bootstrap icon class (e.g., "bi-person") |
| modal_icon_color | string | "text-primary" | Icon color class |
| modal_size | string | "modal-md" | Size: sm, md, lg, xl |
| modal_centered | bool | True | Center modal vertically |
| modal_scrollable | bool | False | Allow scrolling of modal body |
| modal_body_content | string | "" | Body content (HTML) |
| show_close_button | bool | True | Show close button |
| modal_primary_action | string | "" | Primary action button text |

### Sizes

```
modal-sm   - Small modal
modal-md   - Medium modal (default)
modal-lg   - Large modal
modal-xl   - Extra large modal
```

### Bootstrap Icons

Use any Bootstrap icon:
- `bi-person` - Person
- `bi-pencil` - Edit
- `bi-trash` - Delete
- `bi-plus-circle` - Add
- `bi-info-circle` - Info
- `bi-warning` - Warning
- `bi-check-circle` - Success

---

## Forms System

### Overview

Generic form template with Django integration and HTMX support

### Structure

```
Form
├── Non-field errors
├── Form fields
│   ├── Label
│   ├── Input wrapper
│   ├── Help text
│   └── Field errors
└── Form actions
    ├── Cancel (optional)
    └── Submit
```

### Basic Usage

```django
{% include "generic/_forms.html" with form=my_form %}
```

### With HTMX Integration

```django
{% include "generic/_forms.html" with
    form=my_form
    hx_post="/api/users/create/"
    hx_target="#user-list"
    hx_swap="outerHTML"
    hx_indicator="#form-spinner"
%}
```

### With Custom Actions

```django
{% include "generic/_forms.html" with
    form=my_form
    submit_label="Save Changes"
    show_cancel=True
    cancel_label="Discard"
    form_class="custom-form"
%}
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| form | object | required | Django form object |
| hx_post | string | "" | HTMX POST URL |
| hx_target | string | "" | HTMX target selector |
| hx_swap | string | "outerHTML" | HTMX swap strategy |
| hx_indicator | string | "" | HTMX loading indicator ID |
| is_multipart | bool | False | Enable file upload |
| form_class | string | "" | Additional CSS classes |
| submit_label | string | "Submit" | Submit button text |
| show_cancel | bool | False | Show cancel button |
| cancel_label | string | "Cancel" | Cancel button text |
| cancel_onclick | string | "" | Cancel onclick handler |
| submit_attrs | string | "" | Additional submit button attributes |

### HTMX Integration Example

```django
{% include "generic/_forms.html" with
    form=contact_form
    hx_post="/api/contact/"
    hx_target="#success-message"
    hx_swap="innerHTML swap:1s"
    hx_indicator="#contact-spinner"
    submit_label="Send Message"
%}
```

### Field Types Supported

- **Text Input** - text, email, password, url, etc.
- **Textarea** - Large text areas
- **Select** - Dropdown lists
- **Select Multiple** - Multi-select
- **Checkbox** - Single checkbox
- **Radio** - Radio button groups
- **File Upload** - File input with cloud icon
- **Hidden** - Hidden fields (not displayed)

### Form Validation Display

Validation errors are shown:
- ✅ Field-level errors under each field
- ✅ Non-field errors at top of form
- ✅ Red text with icon indicators
- ✅ Required field indicators (*)

---

## Usage Patterns

### Pattern 1: Toast Notification After Form Submit

**Flow:**
1. User submits form via HTMX
2. Server returns success response
3. JavaScript shows toast notification
4. Form clears or redirects

**Implementation:**

```html
<!-- HTML -->
<form hx-post="/api/contact/" hx-swap="none" id="contact-form">
    <!-- form fields -->
</form>

<!-- JavaScript -->
<script>
document.getElementById('contact-form').addEventListener('htmx:xhr:loadend', function(e) {
    if (e.detail.xhr.status === 200) {
        showNotification({
            title: "Success",
            message: "Message sent successfully",
            level: "success"
        });
    }
});
</script>
```

### Pattern 2: Modal Form with Validation

**Flow:**
1. Click "Edit" button
2. Modal opens with form
3. User submits form
4. Validation errors show in form
5. Success toast appears

**Implementation:**

```html
<!-- Button triggers modal -->
<button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#editModal">
    Edit
</button>

<!-- Modal with form -->
<div class="modal fade" id="editModal">
    {% include "generic/_modals.html" with
        modal_id="editModal"
        modal_title="Edit User"
    %}
    {% block modal_content %}
        {% include "generic/_forms.html" with
            form=user_form
            hx_post="/api/users/update/"
            hx_target="#editModal-content"
            hx_swap="innerHTML"
        %}
    {% endblock %}
</div>
```

### Pattern 3: Alert with Details

**Flow:**
1. Important information needs to be displayed
2. User can view basic message
3. User can expand to see details
4. User can dismiss when ready

**Implementation:**

```javascript
showAlert({
    title: "Maintenance Scheduled",
    message: "System maintenance is scheduled for tomorrow.",
    level: "warning",
    icon: "bi-exclamation-triangle",
    badge: "Maintenance",
    details: `
        <p><strong>Date:</strong> June 8, 2026</p>
        <p><strong>Time:</strong> 2:00 AM - 4:00 AM EST</p>
        <p><strong>Impact:</strong> All services will be unavailable</p>
    `
});
```

### Pattern 4: Confirmation Popup

**Flow:**
1. User initiates destructive action (delete, etc.)
2. Confirmation popup appears
3. User chooses to confirm or cancel
4. Action executed or cancelled

**Implementation:**

```javascript
function deleteUser(userId) {
    showPopup({
        title: "Delete User?",
        message: "<p>Are you sure you want to delete this user? This action cannot be undone.</p>",
        level: "danger",
        size: "modal-md",
        showCancel: true,
        actions: `<button class="btn btn-danger" onclick="confirmDelete(${userId})">Delete</button>`
    });
}

function confirmDelete(userId) {
    fetch(`/api/users/${userId}/delete/`, { method: 'DELETE' })
        .then(response => {
            if (response.ok) {
                showNotification({
                    title: "Deleted",
                    message: "User deleted successfully",
                    level: "success"
                });
            }
        });
}
```

---

## Implementation Flows

### Flow 1: Complete Form Submission with Validation

```
Start
  ↓
User fills form
  ↓
User clicks Submit
  ↓
HTMX sends POST request with form data
  ↓
Server validates form
  ├─ If Invalid: Return form with errors
  │   ↓
  │   HTMX swaps form in place
  │   ↓
  │   Errors display under fields
  │   ↓
  │   Go to "User fills form"
  │
  └─ If Valid: Process and return success
      ↓
      HTMX swaps response
      ↓
      JavaScript shows success toast
      ↓
      Clear form or redirect
      ↓
      End
```

### Flow 2: Modal Dialog Workflow

```
Start
  ↓
User clicks action button
  ↓
Modal opens with content/form
  ↓
User interacts with content
  ├─ If Form:
  │   ├─ Fill form fields
  │   ├─ Click Submit
  │   ├─ Validate (repeat if errors)
  │   └─ Show success toast
  │
  └─ If Confirmation:
      ├─ Click Confirm
      ├─ Execute action
      └─ Show result notification
      ↓
Modal closes
  ↓
Page updates (if needed)
  ↓
End
```

### Flow 3: Notification Display Chain

```
Start
  ↓
Include _notifications.html in base template
  ↓
Django messages rendered in container
  ↓
JavaScript initializes notification system
  ↓
User action triggers notification
  ├─ Toast: Shows, auto-dismisses after 5s
  ├─ Alert: Shows, requires manual dismissal
  └─ Popup: Shows, blocks interaction
      ↓
User dismisses or timeout occurs
  ↓
Notification removed from DOM
  ↓
End
```

### Flow 4: HTMX Form with Notification

```
Start
  ↓
Form with hx-post attribute
  ↓
User fills and submits
  ↓
HTMX intercepts submit
  ↓
Sends POST via AJAX
  ↓
Show loading indicator
  ↓
Server processes request
  ├─ Success:
  │   ├─ Return 200 with response
  │   ├─ HTMX swaps response
  │   ├─ htmx:xhr:loadend event fires
  │   ├─ JavaScript shows success toast
  │   └─ Form resets
  │
  └─ Error:
      ├─ Return 400+ status
      ├─ HTMX handles error
      ├─ Show error toast
      └─ Keep form visible
        ↓
End
```

---

## Examples

### Example 1: Contact Form with Toast Notification

**HTML:**
```html
<form id="contact-form" hx-post="/api/contact/" hx-swap="none">
    {% csrf_token %}
    <div class="form-group">
        <label for="name">Name</label>
        <input type="text" class="form-control" id="name" name="name" required>
    </div>
    <div class="form-group">
        <label for="email">Email</label>
        <input type="email" class="form-control" id="email" name="email" required>
    </div>
    <div class="form-group">
        <label for="message">Message</label>
        <textarea class="form-control" id="message" name="message" required></textarea>
    </div>
    <button type="submit" class="btn btn-primary">Send</button>
</form>

<!-- Include notifications -->
{% include "generic/_notifications.html" %}
```

**JavaScript:**
```javascript
document.getElementById('contact-form').addEventListener('htmx:responseEnd', function(e) {
    if (e.detail.xhr.status === 201) {
        showNotification({
            title: "Message Sent",
            message: "Your message has been sent successfully",
            level: "success"
        });
        this.reset();
    } else if (e.detail.xhr.status >= 400) {
        showNotification({
            title: "Error",
            message: "Failed to send message. Please try again.",
            level: "danger"
        });
    }
});
```

### Example 2: Edit Modal with Form

**HTML:**
```html
<!-- Edit Button -->
<button class="btn btn-sm btn-primary" data-bs-toggle="modal" data-bs-target="#editUserModal">
    <i class="bi bi-pencil"></i> Edit
</button>

<!-- Modal with Form -->
{% include "generic/_modals.html" with
    modal_id="editUserModal"
    modal_title="Edit User"
    modal_icon="bi-pencil"
    modal_icon_color="text-primary"
    modal_size="modal-lg"
%}
    {% block modal_content %}
        {% include "generic/_forms.html" with
            form=user_form
            hx_post="/api/users/update/"
            hx_target="#editUserModal-content"
            hx_swap="innerHTML"
            show_cancel=True
        %}
    {% endblock %}
{% endblock %}

<!-- Include notifications -->
{% include "generic/_notifications.html" %}
```

**View:**
```python
def update_user(request):
    user = request.user
    form = UserForm(request.POST or None, instance=user)
    
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            # Return success message via HTMX
            return render(request, 'generic/_forms.html', {
                'form': form,
                'message': 'User updated successfully'
            })
    
    return render(request, 'generic/_forms.html', {'form': form})
```

### Example 3: Delete Confirmation Popup

**HTML:**
```html
<button class="btn btn-sm btn-danger" onclick="confirmDelete({{ user.id }})">
    <i class="bi bi-trash"></i> Delete
</button>

<!-- Include notifications -->
{% include "generic/_notifications.html" %}
```

**JavaScript:**
```javascript
function confirmDelete(userId) {
    showPopup({
        title: "Delete User",
        message: "<p>Are you sure you want to delete this user? This action cannot be undone.</p>",
        level: "danger",
        size: "modal-md",
        showCancel: true,
        actions: `
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-danger" onclick="deleteUser(${userId})">Delete</button>
        `
    });
}

function deleteUser(userId) {
    fetch(`/api/users/${userId}/delete/`, { method: 'DELETE' })
        .then(response => {
            if (response.ok) {
                showNotification({
                    title: "Deleted",
                    message: "User has been deleted",
                    level: "success"
                });
                // Reload table after 1 second
                setTimeout(() => location.reload(), 1000);
            } else {
                showNotification({
                    title: "Error",
                    message: "Failed to delete user",
                    level: "danger"
                });
            }
        });
}
```

---

## Troubleshooting

### Issue: Notifications not appearing

**Cause:** Component not included in template  
**Solution:** Add `{% include "generic/_notifications.html" %}` to base template

**Cause:** JavaScript not loaded  
**Solution:** Ensure notification JS is included in static files

**Cause:** Container ID mismatch  
**Solution:** Check that container ID is `#notification-container`

### Issue: Modal not centering

**Cause:** `modal_centered` parameter not True  
**Solution:** Add `modal_centered=True` to include

### Issue: Form validation not showing

**Cause:** Form not rendered with template  
**Solution:** Use `{% include "generic/_forms.html" with form=form_object %}`

### Issue: HTMX not swapping form

**Cause:** Incorrect hx-target selector  
**Solution:** Ensure selector matches form ID or wrapper ID

**Cause:** Form not returning proper HTML  
**Solution:** Render form template in response

### Issue: Toast disappearing too quickly

**Cause:** Default timeout (5000ms)  
**Solution:** Pass custom `duration` in notification options

### Issue: Modal backdrop not preventing dismissal

**Cause:** `data-bs-backdrop="static"` not set  
**Solution:** Ensure it's in modal template (already included)

---

## Best Practices

### ✅ DO

1. **Use for consistent styling** - All notifications use same style
2. **Include in base template** - Add `_notifications.html` once
3. **Use HTMX for forms** - Better UX than page reload
4. **Show confirmation for destructive actions** - Use popups for delete/remove
5. **Provide feedback** - Show notifications after actions
6. **Use appropriate levels** - success, danger, warning, info
7. **Keep messages clear** - Short, actionable text
8. **Use icons** - Visual indicators help users quickly understand

### ❌ DON'T

1. **Don't create custom notification systems** - Use unified system
2. **Don't mix notification types** - Use toast for temporary, alert for persistent
3. **Don't forget CSRF tokens** - Always include in forms
4. **Don't leave forms without feedback** - Show validation errors
5. **Don't ignore accessibility** - Use proper ARIA labels
6. **Don't auto-dismiss important alerts** - Use persistent alerts
7. **Don't add too many notifications** - Can overwhelm users
8. **Don't use popups for non-critical info** - Use toasts instead

---

## Integration Checklist

- [ ] Add `{% include "generic/_notifications.html" %}` to base template
- [ ] Add `_notifications.html`, `_modals.html`, `_forms.html` JavaScript
- [ ] Include Bootstrap CSS and Icons
- [ ] Test toast notifications
- [ ] Test alert notifications
- [ ] Test modals with content
- [ ] Test forms with validation
- [ ] Test HTMX integration
- [ ] Test on mobile devices
- [ ] Test accessibility

---

## Related Documentation

- Bootstrap Modal Docs: https://getbootstrap.com/docs/5.0/components/modal/
- Bootstrap Form Docs: https://getbootstrap.com/docs/5.0/forms/overview/
- Bootstrap Icons: https://icons.getbootstrap.com/
- HTMX Documentation: https://htmx.org/
- Django Messages: https://docs.djangoproject.com/en/stable/contrib/messages/

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | June 7, 2026 | Initial release |

---

**Last Updated:** June 7, 2026  
**Maintained by:** Development Team  
**Status:** ✅ Active & Maintained

