# Precis LMS — Template Architecture

> **Last updated:** 2026-08-10
> **Template engine:** Django (DjangoTemplates) + django-fusion components + Wagtail CMS
> **Frontend companion:** Astro 5 (see `frontend/src/layouts/Layout.astro`)

---

## 1. Overview

Precis LMS uses a **multi-layout skeleton system** — different page types (landing,
learning, auth, profile, forms) each extend a purpose-built skeleton that provides the
header, layout shell, and script bundles for that context. All skeletons ultimately
extend a shared `base.html`.

```
Request → URL Router → Wagtail Page / Django View
    │
    ├── Landing pages     → layout/landing/skeleton.html
    ├── Course/learning   → layout/learning/skeleton.html
    ├── Auth (login/signup)→ layout/auth/skeleton.html
    ├── Profile/dashboard → layout/profile/skeleton.html
    └── Forms (Wagtail)   → layout/forms/skeleton.html (standalone)
```

---

## 2. Template Directory Map

```
projects/precis/precis-lms/assets/templates/
├── base.html                                ← Root layout (shared by all)
│
├── layout/                                  ← Skeleton layouts (one per use-case)
│   ├── landing/skeleton.html                ← Landing & marketing pages
│   ├── learning/skeleton.html               ← Course catalog, detail, progress
│   ├── auth/skeleton.html                   ← Login, signup, password reset
│   ├── profile/skeleton.html                ← User profile & dashboard
│   └── forms/skeleton.html                  ← Wagtail StreamField form blocks
│
├── components/                              ← django-fusion {% comp %} components
│   ├── landing/header/landing.html          ← Landing header
│   ├── learning/header/learning.html        ← LMS header
│   ├── landing/footer.html                  ← Shared footer
│   ├── partials/meta.html                   ← SEO meta tags
│   ├── plugins/mfa/webauthn/                ← Passkey/WebAuthn components
│   └── blocks/partials/form_field.html      ← Dynamic form field renderer
│
└── plugins/                                 ← Shared utilities
    ├── tables/table.html                    ← Fusion table component
    └── base/
        ├── validation.html                  ← Form validation
        └── error.html                       ← Error display
```

---

## 3. Skeleton Hierarchy

```
base.html                                    ← <html>, <head>, meta, global scripts
│
├── layout/landing/skeleton.html             ← data-usecase="landing"
│   │   Header: landing/header/landing.html
│   │   Footer: landing/footer.html
│   │   CSS:    {% render_bundle 'static' 'css' %}
│   │   JS:     {% render_bundle 'static' 'js' %}
│   │
│   └── layout/profile/skeleton.html         ← Extends landing skeleton
│       │   data-layout="profile"
│       │   Modal overlay included
│
├── layout/learning/skeleton.html            ← data-usecase="lms"
│   │   data-theme="theme2"
│   │   Header: learning/header/learning.html
│   │   No footer (learning-specific shell)
│
├── layout/auth/skeleton.html                ← data-theme="light"
│   │   bodyclass: auth-page
│   │   No header/footer
│   │   Passkey/WebAuthn integration
│
└── layout/forms/skeleton.html               ← Standalone (does not extend base)
    │   HTMX-driven dynamic forms
    │   reCAPTCHA, privacy consent, success/error templates
```

---

## 4. Template Flow

### 4.1 Landing Page Request

```
GET / → Wagtail Page
    │
    ▼
layout/landing/skeleton.html         ← data-usecase="landing"
    │
    ├── {% comp 'partials/meta.html' /%}      ← SEO meta
    ├── {% render_bundle 'static' 'css' %}    ← Webpack CSS bundle
    ├── {% comp 'landing/header/landing.html' /%}
    │
    ├── <main class="landing-shell">
    │   └── {% block content %}...{% endblock %}
    │
    ├── {% comp 'landing/footer.html' /%}
    ├── {% block modal %}{% endblock %}
    └── {% render_bundle 'static' 'js' %}     ← Webpack JS bundle
```

### 4.2 Learning (LMS) Request

```
GET /courses/ → Wagtail Page
    │
    ▼
layout/learning/skeleton.html        ← data-usecase="lms", theme2
    │
    ├── {% comp 'learning/header/learning.html' /%}
    ├── <main class="lms-shell">
    │   └── Course catalog, detail, enrollment, progress...
    └── (No footer — LMS-specific layout)
```

### 4.3 Auth Request

```
GET /accounts/login/ → allauth view
    │
    ▼
layout/auth/skeleton.html            ← data-theme="light", bodyclass="auth-page"
    │
    ├── No header, no footer
    ├── <main class="auth-container auth-container--vars">
    │   └── Login/signup/password form
    └── Passkey WebAuthn script (if enabled)
```

### 4.4 Form Submission (HTMX)

```
POST /page-with-form/ → Wagtail StreamField form block
    │
    ▼
layout/forms/skeleton.html           ← Dynamic form with HTMX
    │
    ├── hx-post → submits to same URL
    ├── hx-target="#form-messages-{block.id}"
    ├── hx-swap="innerHTML"
    │
    ├── Success → <template id="success-template-{block.id}">
    │   └── Thank you message + redirect or "Submit Another"
    │
    └── Error → <template id="error-template-{block.id}">
        └── Error message + "Try Again" button
```

---

## 5. Data Attribute Convention

Skeletons use `data-*` attributes on `<html>` or `<body>` to signal layout context
to CSS and JS:

| Attribute | Values | Used By |
|---|---|---|
| `data-usecase` | `landing`, `lms` | SCSS layout variants, JS layout init |
| `data-theme` | `theme2`, `light`, `dark` | CSS custom property overrides |
| `data-sidenav-view` | sidebar state | Side navigation toggle |
| `data-layout` | `profile` | Profile-specific CSS |
| `data-animate` | `fade-up` | Scroll reveal animations |
| `data-page` | `auth` | Auth page styling |

---

## 6. Component System (`{% comp %}`)

django-fusion provides a `{% comp "name" /%}` tag that renders registered components.
Unlike `{% include %}`, components are self-closing and discoverable:

```django
{# Registered django-fusion component #}
{% comp 'landing/header/landing.html' /%}

{# NOT: generic include (avoid for components) #}
{% include 'landing/header/landing.html' %}
```

Components are registered in django-fusion's component registry and support context
passing via `{% comp "name" key=value /%}`.

---

## 7. Webpack Integration

Templates consume webpack bundles via django-webpack-loader:

```django
{% load webpack_loader %}

{% block styles %}
    {% render_bundle 'static' 'css' %}
{% endblock %}

{% block scripts %}
    {% render_bundle 'static' 'js' %}
{% endblock %}
```

The `static` bundle is produced by `webpack/precis.config.js` → `assets/bundles/static.[hash].css`.
`bundles.json` maps chunk names to hashed filenames.

---

## 8. Related Files

| File | Role |
|---|---|
| `assets/templates/base.html` | Root layout — all skeletons extend this |
| `assets/templates/layout/landing/skeleton.html` | Landing page layout |
| `assets/templates/layout/learning/skeleton.html` | LMS course layout |
| `assets/templates/layout/auth/skeleton.html` | Authentication layout |
| `assets/templates/layout/profile/skeleton.html` | Profile/dashboard layout |
| `assets/templates/layout/forms/skeleton.html` | Wagtail forms (HTMX) |
| `frontend/src/layouts/Layout.astro` | Astro client-side layout |
| `webpack/precis.config.js` | Webpack config for static bundles |
| `libs/django-fusion/` | Component tag, fusion codec, session checker |
