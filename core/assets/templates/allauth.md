# django-allauth Template Map

This guide replaces the raw allauth template inventory with the project-specific override map for the CTC Research application. It also records the auth layout conventions shared with `lms-demo` and the current `VResume` account plugin baseline.

## Template lookup convention

Django resolves customized allauth templates by their allauth-relative names, such as `account/login.html` and `socialaccount/signup.html`. In this repository the CTC Research overrides live under:

- `core/ctc-research/plugins/templates/account/`
- `core/ctc-research/plugins/templates/socialaccount/`

If a row below says **Allauth package default**, the project does not currently override that template and Django falls back to the installed `django-allauth` package template.

## Shared auth layout

Customized CTC Research allauth page templates extend `base_auth.html` and place their page-specific markup in `{% block auth_content %}`. The shared layout owns the split auth shell, logo/welcome panel, messages area, `.auth__component` wrapper, and SCSS hooks. Page templates should keep their content inside a `.fragment--form` wrapper containing an `.auth__card.card.card--form` card.

Required structure for all customized account/socialaccount page overrides:

```django
{% extends "base_auth.html" %}
{% load i18n static %}

{% block auth_content %}
<section class="fragment--form">
  <section class="auth__card card card--form">
    ...
  </section>
</section>
{% endblock auth_content %}
```

Use the existing auth SCSS/BEM classes consistently:

- Layout: `.auth`, `.auth--split-layout`, `.auth__container--split`, `.auth__form-section--split`, `.auth__form-container`, `.auth__component`
- Cards/forms: `.fragment--form`, `.auth__card`, `.card--form`, `.auth__form`, `.auth__form-header`, `.auth__form-title`, `.auth__form-subtitle`, `.auth__footer`
- Fields/actions: `.form__group`, `.form__label`, `.form__input-wrapper`, `.form__input`, `.form__icon`, `.auth__links`, `.auth__link`, `.auth__submit`

## HTMX fragment rendering notes

Several allauth forms and links include `hx-get`/`hx-post` attributes targeting `.fragment--form`. When a view renders a fragment response, the fragment must include the `.fragment--form` wrapper so swaps replace the same boundary consistently. Full-page responses should render through `base_auth.html`; HTMX responses may return just the fragment from custom PageHandler views or a full `base_auth.html` response that still contains `.fragment--form` for the target swap.

When adding or changing allauth templates:

1. Keep `hx-target=".fragment--form"` for auth flow swaps unless the view intentionally swaps a smaller element.
2. Include `hx-headers='{"X-Requested-With": "XMLHttpRequest"}'` or the existing `HX-Request` header where the corresponding view checks it.
3. Preserve hidden `strategy` fields where present so custom handlers can choose document vs. fragment rendering.
4. Return notification headers from HTMX success/error paths where the view already calls notification helpers.

## Cross-application alignment notes

- `ctc-research` now follows the same visual contract used by `lms-demo` auth templates: `.fragment--form` > `.auth__card.card.card--form` > `.auth__form-header` / `.auth__form` / `.auth__footer`.
- `lms-demo` keeps additional plugin-level templates under `core/lms-demo/templates/auth/` and `core/lms-demo/plugins/accounts/templates/auth/`; use those as copy references for auth SCSS class names and HTMX targets.
- `VResume` currently carries the account plugin code and profile templates but does not include project-level `account/`, `socialaccount/`, or `auth/` template overrides. Treat CTC Research and LMS Demo as the active auth-template references before adding VResume overrides.
- Non-allauth registration templates such as `core/ctc-research/plugins/accounts/templates/auth/*.html` are still fragment-oriented and should remain aligned with the same `.auth__*` and `.form__*` class vocabulary.

## Allauth template map

| Allauth template | Project override path |
| --- | --- |
| `account/account_inactive.html` | `core/ctc-research/plugins/templates/account/account_inactive.html` |
| `account/base_confirm_code.html` | Allauth package default (no project override) |
| `account/base_entrance.html` | Allauth package default (no project override) |
| `account/base_manage.html` | Allauth package default (no project override) |
| `account/base_manage_email.html` | Allauth package default (no project override) |
| `account/base_manage_password.html` | Allauth package default (no project override) |
| `account/base_manage_phone.html` | Allauth package default (no project override) |
| `account/base_reauthenticate.html` | Allauth package default (no project override) |
| `account/confirm_email_verification_code.html` | `core/ctc-research/plugins/templates/account/confirm_email_verification_code.html` |
| `account/confirm_login_code.html` | `core/ctc-research/plugins/templates/account/confirm_login_code.html` |
| `account/confirm_password_reset_code.html` | Allauth package default (no project override) |
| `account/confirm_phone_verification_code.html` | `core/ctc-research/plugins/templates/account/confirm_phone_verification_code.html` |
| `account/email/account_already_exists_message.txt` | Allauth package default (no project override) |
| `account/email/account_already_exists_subject.txt` | Allauth package default (no project override) |
| `account/email/base_message.txt` | Allauth package default (no project override) |
| `account/email/base_notification.txt` | Allauth package default (no project override) |
| `account/email/email_changed_message.txt` | Allauth package default (no project override) |
| `account/email/email_changed_subject.txt` | Allauth package default (no project override) |
| `account/email/email_confirm_message.txt` | Allauth package default (no project override) |
| `account/email/email_confirm_subject.txt` | Allauth package default (no project override) |
| `account/email/email_confirmation_message.txt` | Allauth package default (no project override) |
| `account/email/email_confirmation_signup_message.txt` | Allauth package default (no project override) |
| `account/email/email_confirmation_signup_subject.txt` | Allauth package default (no project override) |
| `account/email/email_confirmation_subject.txt` | Allauth package default (no project override) |
| `account/email/email_deleted_message.txt` | Allauth package default (no project override) |
| `account/email/email_deleted_subject.txt` | Allauth package default (no project override) |
| `account/email/login_code_message.txt` | Allauth package default (no project override) |
| `account/email/login_code_subject.txt` | Allauth package default (no project override) |
| `account/email/password_changed_message.txt` | Allauth package default (no project override) |
| `account/email/password_changed_subject.txt` | Allauth package default (no project override) |
| `account/email/password_reset_code_message.txt` | Allauth package default (no project override) |
| `account/email/password_reset_code_subject.txt` | Allauth package default (no project override) |
| `account/email/password_reset_key_message.txt` | Allauth package default (no project override) |
| `account/email/password_reset_key_subject.txt` | Allauth package default (no project override) |
| `account/email/password_reset_message.txt` | Allauth package default (no project override) |
| `account/email/password_reset_subject.txt` | Allauth package default (no project override) |
| `account/email/password_set_message.txt` | Allauth package default (no project override) |
| `account/email/password_set_subject.txt` | Allauth package default (no project override) |
| `account/email/unknown_account_message.txt` | Allauth package default (no project override) |
| `account/email/unknown_account_subject.txt` | Allauth package default (no project override) |
| `account/email.html` | `core/ctc-research/plugins/templates/account/email.html` |
| `account/email_change.html` | Allauth package default (no project override) |
| `account/email_confirm.html` | `core/ctc-research/plugins/templates/account/email_confirm.html` |
| `account/login.html` | `core/ctc-research/plugins/templates/account/login.html` |
| `account/logout.html` | `core/ctc-research/plugins/templates/account/logout.html` |
| `account/messages/cannot_delete_primary_email.txt` | Allauth package default (no project override) |
| `account/messages/email_confirmation_failed.txt` | Allauth package default (no project override) |
| `account/messages/email_confirmation_sent.txt` | Allauth package default (no project override) |
| `account/messages/email_confirmed.txt` | Allauth package default (no project override) |
| `account/messages/email_deleted.txt` | Allauth package default (no project override) |
| `account/messages/logged_in.txt` | Allauth package default (no project override) |
| `account/messages/logged_out.txt` | Allauth package default (no project override) |
| `account/messages/login_code_sent.txt` | Allauth package default (no project override) |
| `account/messages/password_changed.txt` | Allauth package default (no project override) |
| `account/messages/password_set.txt` | Allauth package default (no project override) |
| `account/messages/phone_verification_sent.txt` | Allauth package default (no project override) |
| `account/messages/phone_verified.txt` | Allauth package default (no project override) |
| `account/messages/primary_email_set.txt` | Allauth package default (no project override) |
| `account/messages/unverified_primary_email.txt` | Allauth package default (no project override) |
| `account/password_change.html` | `core/ctc-research/plugins/templates/account/password_change.html` |
| `account/password_reset.html` | `core/ctc-research/plugins/templates/account/password_reset.html` |
| `account/password_reset_done.html` | `core/ctc-research/plugins/templates/account/password_reset_done.html` |
| `account/password_reset_from_key.html` | `core/ctc-research/plugins/templates/account/password_reset_from_key.html` |
| `account/password_reset_from_key_done.html` | `core/ctc-research/plugins/templates/account/password_reset_from_key_done.html` |
| `account/password_set.html` | `core/ctc-research/plugins/templates/account/password_set.html` |
| `account/phone_change.html` | `core/ctc-research/plugins/templates/account/phone_change.html` |
| `account/reauthenticate.html` | `core/ctc-research/plugins/templates/account/reauthenticate.html` |
| `account/request_login_code.html` | `core/ctc-research/plugins/templates/account/request_login_code.html` |
| `account/signup.html` | `core/ctc-research/plugins/templates/account/signup.html` |
| `account/signup_by_passkey.html` | Allauth package default (no project override) |
| `account/signup_closed.html` | Allauth package default (no project override) |
| `account/snippets/already_logged_in.html` | `core/ctc-research/plugins/templates/account/snippets/already_logged_in.html` |
| `account/snippets/warn_no_email.html` | `core/ctc-research/plugins/templates/account/snippets/warn_no_email.html` |
| `account/verification_sent.html` | `core/ctc-research/plugins/templates/account/verification_sent.html` |
| `account/verified_email_required.html` | `core/ctc-research/plugins/templates/account/verified_email_required.html` |
| `socialaccount/authentication_error.html` | `core/ctc-research/plugins/templates/socialaccount/authentication_error.html` |
| `socialaccount/base_entrance.html` | Allauth package default (no project override) |
| `socialaccount/base_manage.html` | Allauth package default (no project override) |
| `socialaccount/connections.html` | `core/ctc-research/plugins/templates/socialaccount/connections.html` |
| `socialaccount/email/account_connected_message.txt` | Allauth package default (no project override) |
| `socialaccount/email/account_connected_subject.txt` | Allauth package default (no project override) |
| `socialaccount/email/account_disconnected_message.txt` | Allauth package default (no project override) |
| `socialaccount/email/account_disconnected_subject.txt` | Allauth package default (no project override) |
| `socialaccount/login.html` | Allauth package default (no project override) |
| `socialaccount/login_cancelled.html` | `core/ctc-research/plugins/templates/socialaccount/login_cancelled.html` |
| `socialaccount/login_redirect.html` | `core/ctc-research/plugins/templates/socialaccount/login_redirect.html` |
| `socialaccount/messages/account_connected.txt` | Allauth package default (no project override) |
| `socialaccount/messages/account_connected_other.txt` | Allauth package default (no project override) |
| `socialaccount/messages/account_connected_updated.txt` | Allauth package default (no project override) |
| `socialaccount/messages/account_disconnected.txt` | Allauth package default (no project override) |
| `socialaccount/signup.html` | `core/ctc-research/plugins/templates/socialaccount/signup.html` |
| `socialaccount/snippets/login.html` | `core/ctc-research/plugins/templates/socialaccount/snippets/login.html` |
| `socialaccount/snippets/login_extra.html` | `core/ctc-research/plugins/templates/socialaccount/snippets/login_extra.html` |
| `socialaccount/snippets/provider_list.html` | `core/ctc-research/plugins/templates/socialaccount/snippets/provider_list.html` |

## Exceptions and related templates

- `core/ctc-research/plugins/templates/account/enrollment_success.html` is a profile/enrollment page, not a django-allauth override in the installed allauth template list. It continues to extend `profile/skeleton.html`.
- Snippet overrides under `account/snippets/` and `socialaccount/snippets/` are intentionally small partials and do not extend `base_auth.html`; they are included by page templates.
- Email/message `.txt` templates are not wrapped in `base_auth.html`; use email base templates or allauth defaults as appropriate.
