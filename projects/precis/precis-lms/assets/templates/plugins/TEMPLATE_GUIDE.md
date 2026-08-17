# Template Architecture

**Stack:** Django · Bootstrap 5 · Bootstrap Icons · HTMX · Wagtail  
**Root:** `assets/templates/`

---

## Directory Map

```
assets/templates/
│
├── base.html                        Root base (all pages extend this)
├── base_auth.html                   Auth layout base
├── cert.html                        Standalone certificate page
│
├── ui/                              ── Generic reusable UI components ──
│   ├── base/                        Cross-cutting primitives
│   │   ├── confirm.html             Confirmation / delete dialog
│   │   ├── error.html               Inline HTMX error alert
│   │   ├── fragment.html            Named fragment container (HTMX OOB)
│   │   ├── loader.html              Loading states: spinner, overlay, skeleton
│   │   └── validation.html          Field-level error / success feedback
│   │
│   ├── forms/
│   │   ├── form.html                ★ Primary form (POST + HTMX, all widgets)
│   │   ├── form_simple.html         Simple standard form (method/action)
│   │   ├── form_field.html          Single field renderer (StreamField)
│   │   └── form_block.html          Wagtail block form (reCAPTCHA, consent)
│   │
│   ├── modals/
│   │   ├── modal.html               ★ HTMX trigger + skeleton (combined)
│   │   ├── modal_static.html        Block-override modal (no trigger)
│   │   └── modal_trigger.html       Standalone trigger button only
│   │
│   ├── notifications/
│   │   └── notifications.html       ★ Unified system (toast/alert/popup/SSE)
│   │
│   ├── errors/
│   │   ├── 400.html … 504.html      Full-page HTTP error pages
│   │   └── nxx.html                 Generic standalone error fallback
│   │
│   ├── pagination/
│   │   ├── numbers.html             Numbered pagination nav
│   │   ├── load_more.html           HTMX "Load More" button
│   │   └── infinite.html            Intersection Observer infinite scroll
│   │
│   ├── tables/
│   │   └── table.html               HTMX sortable table
│   │
│   ├── search/
│   │   └── search_bar.html          HTMX live search bar
│   │
│   └── headers/
│       └── breadcrumbs.html         Breadcrumb nav
│
├── modules/                         ── Domain feature templates ──
│   ├── courses/
│   │   ├── catalog.html             Course catalog page
│   │   └── filters.html             Filter sidebar (HTMX)
│   │
│   ├── newsletter/
│   │   ├── subscribe.html           Subscribe form page
│   │   ├── confirmed.html           Subscription confirmed page
│   │   ├── unsubscribe_confirm.html Unsubscribe confirmation
│   │   ├── unsubscribed.html        Unsubscribed success page
│   │   └── email/
│   │       ├── campaign.html        Newsletter campaign email
│   │       └── confirmation.html    Subscription confirm email
│   │
│   ├── privacy/
│   │   ├── privacy_policy.html      Full privacy policy page
│   │   ├── privacy_policy_modal.html  Modal / overlay fragment
│   │   ├── terms.html               Full terms of service page
│   │   ├── terms_modal.html         Modal / overlay fragment
│   │   ├── consent_required.html    Full-page consent gate
│   │   └── consent_accepted.html    OOB swap after consent POST
│   │
│   ├── certification/
│   │   └── certificate.html         Printable certificate (standalone HTML)
│   │
│
├── plugins/                         ── Plugin / integration templates ──
│   ├── emails/                      Transactional email templates
│   │   ├── base.html                Email base layout
│   │   ├── base_email.html          Alternative email base
│   │   ├── welcome.html
│   │   ├── invitation.html / .txt
│   │   ├── password_reset.html
│   │   ├── enrollment.html
│   │   ├── completion.html
│   │   ├── contact_confirmation.html
│   │   ├── contact_submission.html
│   │   ├── error_report.html
│   │   ├── bulk_email_default.html
│   │   ├── newsletter_invite.html / .txt
│   │   ├── admin_test.html
│   │   ├── admin_supervisor_test.html
│   │   ├── supervisor_test.html
│   │   ├── test_email.html
│   │   └── registration/
│   │       ├── confirmation.html
│   │       └── signin_success.html
│   │
│   └── mfa/
│       └── webauthn/snippets/
│           └── login_script.html    Passkey / WebAuthn JS snippet
│
├── partials/                        ── Live header partials (used by layout/) ──
│   ├── auth_buttons.html            Login/register or user dropdown
│   ├── language_selector.html       Language switcher with flags
│   ├── header_toggle.html           Hamburger button
│   ├── header_extra.html            Social links + auth + language + toggle
│   ├── header_links.html            Full nav menu (Wagtail top_menu)
│   ├── logo.html                    Site logo with brand_settings fallback
│   ├── meta.html                    Full <head> meta block
│   ├── announcement_banner.html     Top-of-page announcement bar
│   ├── header/
│   │   └── user_actions.html        Convenience: auth + language + toggle
│   └── navigations/
│       ├── top_nav.html             App top bar (sidebar toggle + user menu)
│       └── side_nav.html            App sidebar (dashboard/courses/settings)
│
├── layout/                          ── Page skeleton layouts ──
│   ├── landing/skeleton.html        Landing pages
│   ├── auth/skeleton.html           Auth pages
│   ├── learning/skeleton.html       LMS learning pages
│   └── profile/skeleton.html        Profile / dashboard pages
│
├── blocks/                          ── Wagtail StreamField blocks ──
│   ├── content/                     Text, image, CTA, embed, table blocks
│   ├── media/                       Gallery, video blocks
│   ├── pages/                       About, team, events blocks
│   └── contact/                     Contact, map, hours blocks
│
└── .wagtailadmin/                   Wagtail admin overrides
```

---

## Canonical Include Paths

### ui/base — primitives

```django
{% include "ui/base/confirm.html" with modal_id="deleteModal" confirm_url="/api/delete/1/" confirm_title="Delete?" %}
{% include "ui/base/error.html" with message="Could not save." %}
{% include "ui/base/validation.html" with errors=field.errors success_message="Looks good!" %}
{% include "ui/base/loader.html" %}   {# exposes #ui-spinner-template, #ui-loading-overlay-template, #ui-skeleton-template #}
{% include "ui/base/fragment.html" with fragment_name="course_list" %}
```

### ui/forms

```django
{# Primary: HTMX + POST, all widgets #}
{% include "ui/forms/form.html" with form=my_form hx_post="/api/save/" hx_target="#result" submit_label="Save" %}

{# Simple: standard server-rendered #}
{% include "ui/forms/form_simple.html" with form=my_form action="/contact/" %}
```

### ui/modals

```django
{# Combined trigger + skeleton (most common) #}
{% include "ui/modals/modal.html" with
    modal_id="editModal"
    modal_title="Edit User"
    modal_icon="bi-pencil"
    modal_size="modal-lg"
    hx_url="/users/42/edit/"
    btn_label="Edit"
%}

{# Trigger only (skeleton already on page) #}
{% include "ui/modals/modal_trigger.html" with hx_url="/users/42/" hx_target="#myModal-body" label="View" %}

{# Block-override static modal #}
{% include "ui/modals/modal_static.html" with id="confirmModal" title="Confirm?" body="Are you sure?" %}
```

### ui/notifications

```django
{# Include ONCE in base.html, just before </body> #}
{% include "ui/notifications/notification.html" %}

{# JS API: #}
{# showToast('success', 'Saved!')  #}
{# showToast('danger', 'Error!', 'Title', 7000)  #}
{# showAlert({ level: 'warning', title: 'Alert', message: 'Low disk.', badge: 'Action needed' })  #}
{# showErrorAlert('Connection failed.')  #}
{# showPopup({ title: 'Confirm', message: '<p>Continue?</p>', showCancel: true, actions: '...' })  #}
```

### ui/pagination, tables, search, headers

```django
{% include "ui/pagination/numbers.html" %}
{% include "ui/pagination/load_more.html" %}
{% include "ui/pagination/infinite.html" %}
{% include "ui/tables/table.html" with headers=cols rows=data %}
{% include "ui/search/search_bar.html" with hx_url="/search/" hx_target="#results" %}
{% include "ui/headers/breadcrumbs.html" with breadcrumbs=crumbs %}
```

### modules/

```django
{% include "modules/courses/filters.html" %}
{% comp "components/assistant/widget.html" / %}   {# Precis Assistant floating widget #}
```

### plugins/

```django
{# In base_auth.html (already configured): #}
{% include "plugins/mfa/webauthn/snippets/login_script.html" with button_id="passkey_login" %}

{# Email template_name in views.py: #}
{# "plugins/emails/welcome.html"  #}
{# "plugins/emails/password_reset.html"  #}
{# "plugins/emails/enrollment.html"  #}
```

---

## base.html — what it includes

```django
{% include "ui/notifications/notifications.html" %}   {# in {% block modal %} #}
<div id="modal-container"></div>
```

---

## Naming Conventions

| Pattern | Meaning |
|---------|---------|
| `ui/base/*.html` | Stateless primitive — include anywhere |
| `ui/forms/form.html` | Primary variant (HTMX-capable) |
| `ui/forms/form_simple.html` | Simple variant (standard POST only) |
| `ui/modals/modal.html` | Primary variant (trigger + skeleton) |
| `ui/modals/modal_static.html` | Static / block-override variant |
| `ui/modals/modal_trigger.html` | Single-purpose trigger button |
| `modules/*/` | Domain feature page or fragment |
| `plugins/emails/` | `template_name` for Django email backends |
| `plugins/mfa/` | Conditionally included security snippets |
| No `_` prefix | All files — underscore prefix convention dropped |

---

## Removed

| Was | Now |
|-----|-----|
| `generic/_confirm.html` | `ui/base/confirm.html` |
| `generic/_error.html` | `ui/base/error.html` |
| `generic/_fragment.html` | `ui/base/fragment.html` |
| `generic/_loader.html` | `ui/base/loader.html` |
| `generic/_validation.html` | `ui/base/validation.html` |
| `generic/forms/_form.html` | `ui/forms/form.html` |
| `generic/forms/form.html` | `ui/forms/form_simple.html` |
| `generic/forms/field.html` | `ui/forms/form_field.html` |
| `generic/forms/skeleton.html` | `ui/forms/form_block.html` |
| `generic/modals/_modal.html` | `ui/modals/modal.html` |
| `generic/modals/modal.html` | `ui/modals/modal_static.html` |
| `generic/modals/modal_trigger.html` | `ui/modals/modal_trigger.html` |
| `generic/notifications/notification.html` | `ui/notifications/notifications.html` |
| `generic/errors/*.html` | `ui/errors/*.html` |
| `generic/pagination/*.html` | `ui/pagination/*.html` |
| `generic/tables/htmx_table.html` | `ui/tables/table.html` |
| `generic/search/search_bar.html` | `ui/search/search_bar.html` |
| `generic/headers/breadcrumbs.html` | `ui/headers/breadcrumbs.html` |
| `generic/courses/_filters.html` | `modules/courses/filters.html` |
| `generic/courses/search.html` | `modules/courses/catalog.html` |
| `generic/newsletter/*.html` | `modules/newsletter/*.html` |
| `generic/privacy/*.html` | `modules/privacy/*.html` |
| `generic/certification/cert_fallback.html` | `modules/certification/certificate.html` |
| `generic/chat/bubble.html` | `components/assistant/widget.html` |
| `generic/emails/*.html` | `plugins/emails/*.html` |
| `generic/mfa/**` | `plugins/mfa/**` |
| `generic/COMPONENTS_USAGE_GUIDE.md` | `ui/TEMPLATE_GUIDE.md` (this file) |

**Last updated:** June 2026
