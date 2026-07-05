# Templates — Usage & Best Practices

Comprehensive guide to template organization, inheritance, HTMX fragments, and Wagtail integration.

## Template Resolution

Django resolves templates through configured directories (see `configs/base/templates.py`) in this order:

1. Site-specific templates (highest priority)
2. Workspace shared templates (`assets/templates/`)
3. Django app templates (`APP_DIRS: True`)

This means you can override any shared template by placing a same-named file in the site's template directory.

## Base Templates

All page templates inherit from one of the base templates:

### `base.html` — Main Site Shell

```django
{% extends "base.html" %}
{% load i18n static %}

{% block title %}Page Title{% endblock %}
{% block content %}
  <!-- Page content -->
{% endblock %}
```

### `base_email.html` — Email Templates

```django
{% extends "base_email.html" %}
{% block email_content %}
  <!-- Email content -->
{% endblock %}
```

### `base_profile.html` — Profile Pages

```django
{% extends "base_profile.html" %}
{% block profile_content %}
  <!-- Profile content -->
{% endblock %}
```

## Layout System

Layout variants provide different page chrome for different page types:

| Layout | Directory | Use Case |
|---|---|---|
| Landing | `layout/landing/` | Marketing/landing pages |
| Apps | `layout/apps/` | Application-style pages |
| Learning | `layout/learning/` | LMS/course pages |
| Profile | `layout/profile/` | User profile pages |
| Auth | `layout/auth/` | Login/registration pages |
| Forms | `layout/forms/` | Form-centric pages |

Each layout variant provides:
- `skeleton.html` — Full page shell
- `header/` — Header components (logo, nav, user actions)
- `partials/` — Reusable partials (logo, meta)
- `meta.html` — SEO meta tags

### Using a Layout

```django
{% extends "layout/landing/skeleton.html" %}

{% block page_content %}
  <!-- Your page content -->
{% endblock %}
```

## HTMX Fragment Pattern

HTMX-powered pages use fragment wrappers for targeted DOM swaps:

### Fragment Structure

```django
{# full_page.html — full page render #}
{% extends "base.html" %}
{% block content %}
  {% include "blog/fragments/post_list.html" %}
{% endblock %}

{# fragments/post_list.html — HTMX fragment #}
<section class="fragment--post-list">
  <hx-target=".fragment--post-list">
  {% for post in posts %}
    {% include "blog/components/post_card.html" %}
  {% endfor %}
  
  {% include "plugins/pagination/numbers.html" %}
</section>
```

### Fragment Conventions

1. **Wrapper class**: `.fragment--<name>` matches the HTMX target
2. **Include strategy**: Fragments include components, not extend base templates
3. **Headers**: Include `HX-Request` where views check for it
4. **Swap strategy**: Default to `hx-swap="outerHTML"`

### Auth Fragment Pattern

```django
{# Account pages use .fragment--form as the swap target #}
<section class="fragment--form">
  <section class="auth__card card card--form">
    <div class="auth__form-header">
      <h1 class="auth__form-title">{% block form_title %}{% endblock %}</h1>
    </div>
    <form class="auth__form" hx-post="{{ request.path }}" hx-target=".fragment--form">
      {% csrf_token %}
      {{ form }}
      <button type="submit" class="auth__submit">Submit</button>
    </form>
    <div class="auth__footer">
      <a class="auth__link" href="{% url 'account_login' %}">Sign in</a>
    </div>
  </section>
</section>
```

## Component System

### django-bird Components

```django
{% comp "card" title="Hello World" variant="featured" %}
  <p>Content goes here</p>
{% endcomp %}
```

### django_fusion Components (Builtins)

Available without `{% load %}`:
- `{% comp %}` / `{% endcomp %}` — Component wrapper
- `{% slot %}` — Named content slot
- `{% prop %}` — Access component props
- `{% var %}` — Define template variables
- `{% css %}` — Include component CSS
- `{% js %}` — Include component JavaScript

### Custom Includes

```django
{% include "plugins/pagination/numbers.html" with page_obj=posts %}
{% include "plugins/modals/confirm.html" with modal_id="delete" title="Confirm Delete" %}
```

## Wagtail Templates

### Page Templates

Place in the site's `www/pages/<app>/templates/` or reference by model:

```python
class BlogPage(Page):
    template = "blog/blog_page.html"
```

### StreamField Blocks

```django
{# blocks/content/rich_text.html #}
<div class="block--rich-text">
  {{ value|richtext }}
</div>
```

### Wagtail Admin Overrides

Override admin templates in `templates/wagtailadmin/`:
- `pages/edit.html` — Page editor
- `snippets/formsubmission/` — Custom snippet views
- `userbar/` — Frontend user bar

## BEM CSS Conventions

Use BEM-style classes consistently:

```html
<!-- Block -->
<div class="card">

  <!-- Element -->
  <h2 class="card__title">Title</h2>
  <p class="card__content">Content</p>
  
  <!-- Modifier -->
  <div class="card--featured">Featured card</div>
</div>
```

### Auth BEM Classes

| Class | Purpose |
|---|---|
| `.auth` | Auth page wrapper |
| `.auth--split-layout` | Split layout modifier |
| `.auth__container--split` | Split container |
| `.auth__form-section--split` | Form side of split |
| `.auth__card` | Auth card container |
| `.card--form` | Form card modifier |
| `.auth__form-header` | Form header (title/subtitle) |
| `.auth__form-title` | Form title |
| `.auth__form-subtitle` | Form subtitle |
| `.auth__form` | The form element |
| `.auth__footer` | Form footer (links) |
| `.auth__link` | Footer links |
| `.auth__submit` | Submit button |
| `.form__group` | Form field group |
| `.form__label` | Field label |
| `.form__input-wrapper` | Input wrapper |
| `.form__input` | Input element |
| `.form__icon` | Input icon |

## Email Templates

Email templates extend `base_email.html` and live in `plugins/emails/`:

```django
{% extends "base_email.html" %}
{% block email_content %}
  <h1>Welcome, {{ user.username }}!</h1>
  <p>Your account has been created.</p>
{% endblock %}
```

### Available Email Templates

| Template | Purpose |
|---|---|
| `welcome.html` | New user welcome |
| `password_reset.html` | Password reset |
| `enrollment.html` | Course enrollment |
| `completion.html` | Course completion |
| `newsletter_invite.html` | Newsletter invitation |
| `bulk_email_default.html` | Default bulk email |
| `admin_test.html` | Admin test email |
| `test_email.html` | Test email |

## Error Pages

Error templates live in `plugins/errors/`:

| Template | HTTP Status |
|---|---|
| `400.html` | Bad Request |
| `401.html` | Unauthorized |
| `403.html` | Forbidden |
| `404.html` | Not Found |
| `429.html` | Too Many Requests |
| `500.html` | Internal Server Error |
| `502.html` | Bad Gateway |
| `503.html` | Service Unavailable |
| `504.html` | Gateway Timeout |

## Functional Template Organization

### By Function (Not by Origin)

Templates are organized by what they do, not where they came from:

| Function | Directory | Examples |
|---|---|---|
| Authentication | `auth/`, `account/`, `registration/`, `socialaccount/` | Login, signup, password reset |
| Blog | `blog/` | Posts, authors, tags, comments |
| Courses/LMS | `courses/`, `lms/`, `learning/` | Course listings, details, checkout |
| Email | `plugins/emails/`, `email/` | Welcome, password reset, newsletter |
| Layout | `layout/<variant>/` | Landing, apps, learning, profile shells |
| Pages | `home/`, `about/`, `contact/`, `events/`, etc. | Page-specific sections |
| Plugins | `plugins/<name>/` | Reusable cross-cutting templates |
| Wagtail | `wagtailadmin/`, `wagtailcore/`, `blocks/` | CMS integration |

### Component Reuse

When creating a new component:
1. Check `plugins/` for existing reusable versions
2. Check `components/` for generic UI components
3. Check `blocks/` for Wagtail-specific blocks
4. Create new only if nothing suitable exists

## See Also

- `assets/templates/README.md` — Template directory layout
- [websites.md](websites.md) — Per-website template paths
- [packages.md](packages.md) — Template-related packages (django-bird, django_fusion)
