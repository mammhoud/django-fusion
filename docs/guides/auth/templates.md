# Auth Fragment Templates

All auth templates are **pure fragments** — no `{% extends %}`, outermost element is always `<section class="fragment--form">`.

## Template Pattern

```html
{# Context fields: form, request #}
{# Placeholders: none #}
{% load i18n static %}
<section class="fragment--form">
  <section class="auth__card card card--form">
    <header class="auth__form-header">
      <h2 class="auth__form-title">{% trans "Title" %}</h2>
      <p class="auth__form-subtitle mb-4">{% trans "Subtitle" %}</p>
    </header>
    <form class="auth__form"
          hx-post="{% url 'plugins:...' %}"
          hx-target=".auth__form"
          hx-swap="innerHTML">
      {% csrf_token %}
      <input type="hidden" name="strategy"
             value="{% if request.htmx %}htmx{% else %}document{% endif %}">
      <input type="hidden" name="supports_sse"
             value="{{ request.supports_sse|yesno:'true,false' }}">
      {# form fields #}
    </form>
    <footer class="auth__footer">...</footer>
  </section>
</section>
```

## All Templates

| Template | Purpose | Key context |
|----------|---------|-------------|
| `auth/login.html` | Sign in | `form` |
| `auth/register.html` | Sign up | `form` |
| `auth/forgot_page.html` | Request password reset | `form` |
| `auth/reset_password.html` | Set new password | `form`, `invalid_key_form` |
| `auth/verification_link.html` | Email verification | `confirmation`, `messages` |
| `auth/password_change.html` | Change password (logged in) | `form` |
| `auth/password_set.html` | Set first password (social) | `form` |
| `auth/email_manage.html` | Manage email addresses | `form`, `emailaddresses` |
| `auth/password_reset_done.html` | Reset email sent | — |
| `auth/password_reset_key_done.html` | Password reset success | — |
| `auth/signup_closed.html` | Registration disabled | — |
| `auth/social_signup.html` | Complete social signup | `form` |
| `auth/social_connections.html` | Manage social accounts | `form`, `connected_accounts`, `disconnectable_accounts` |

## BEM CSS Standards

### Allowed namespaces

- `auth__*` — auth-specific components (`auth__card`, `auth__form`, `auth__submit`)
- `form__*` — form elements (`form__group`, `form__input`, `form__label`)
- `btn--*` — button modifiers (`btn--primary`, `btn--social`)
- Bootstrap utilities (`d-*`, `mb-*`, `text-*`, `bg-*`, etc.)
- Font Awesome (`fas`, `fab`, `fa-*`)

### Color palette

| Token | Value | Usage |
|-------|-------|-------|
| Primary | `#1E3A8A` | `btn-primary`, `text-primary` |
| Success | `#10B981` | `alert-success`, `text-success` |
| Danger | `#EF4444` | `alert-danger`, `text-danger` |
| Warning | `#F59E0B` | `alert-warning`, `text-warning` |

## Required Hidden Inputs

Every `<form>` in an auth template must include:

```html
<input type="hidden" name="strategy"
       value="{% if request.htmx %}htmx{% else %}document{% endif %}">
<input type="hidden" name="supports_sse"
       value="{{ request.supports_sse|yesno:'true,false' }}">
```

These allow the server to choose the correct response strategy.
