# Page Model Refinements and Future Integrations

This document records the design decisions made during the refinement of Wagtail page models (`BasePage`, `BaseFormPage`) and explains the intended logic for fields that were removed due to lack of current implementation.

## 1. Removed Settings (BasePage)

The following fields were removed from `BasePage` to clean up the Wagtail admin interface, as they are not currently utilized in the frontend templates.

| Field Name | Description | Rationale for Removal |
|------------|-------------|-----------------------|
| `enable_dark_mode` | Toggle for dark color scheme. | Frontend handles themeing via global CSS/JS; per-page toggle not implemented. |
| `show_cta_banner` | Toggle for global Call-To-Action banner. | CTA banners are currently managed via specific `StreamField` blocks (e.g., in `BaseIndexPage`). |

## 2. Removed Advanced Form Settings (BaseFormPage)

The following fields were removed from `BaseFormPage`. These represent features intended for a more robust form handling system that is not yet fully integrated with the current `MinimalContactFormBlock`.

| Field Name | Future Integration Goal |
|------------|-------------------------|
| `enable_form_validation` | Client-side/Server-side validation toggle. |
| `custom_validation_message` | Ability to define bespoke error messages per form. |
| `enable_conditional_fields` | Logic to show/hide fields based on user input. |
| `conditional_logic_rules` | JSON structure defining the field dependency rules. |
| `enable_spam_protection` | Integration with Honeypot or CAPTCHA services. |
| `max_submissions_per_hour` | Rate limiting to prevent form abuse. |
| `require_email_verification` | Double opt-in for form submissions. |
| `send_confirmation_email` | Automated "Thank You" emails to the submitter. |
| `notification_email` | Routing submissions to specific departments/users. |

## 3. Profile, Person, and Wagtail User Linking

A critical part of the system is the association between system users and their profiles. This is handled via the `Person` model (defined in `django-osoul`).

### Model Relationships:
- **`django.contrib.auth.models.User`**: The standard Wagtail/Django user account.
- **`pipelines.Person` (aliased as Profile)**: The core profile model.
  - Linked to `User` via `models.OneToOneField(AUTH_USER_MODEL, related_name="profile")`.
  - This ensures that `user.profile` always returns the associated `Person` record.

### Automatic Record Creation:
- A signal (found in `apps/pages/signals/user.py`, currently disabled for migration safety) is designed to automatically create a `Person` record whenever a new `User` is created.
- In production, ensure this signal or a similar mechanism (like a custom Signup view) is active to maintain referential integrity.

### Field Synchronization:
- The `Person` model contains properties like `primary_email` and `primary_name` that handle fallbacks between the Profile data and the User account data.
- For most display purposes, `request.user.profile.display_name` or `request.user.profile.primary_email` should be used.
