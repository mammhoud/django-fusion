# Auth System

All sites use `django-allauth` with custom `django-fusion` auth mixins. Auth views extend `PageHandler` from `django_fusion.site`.

## Adapters

Each site ships the same adapter trio in `plugins/accounts/adapters.py`:

### `AuthHTMXAdapter`

Extends `allauth.account.adapter.DefaultAccountAdapter`.

Responsibilities:
- Maps allauth template names to `auth/` fragment templates.
- Detects `HX-Request` header and returns bare fragments for HTMX, or wraps them in `layout/auth/skeleton.html` for full-page requests.
- Adds a logout success message via Django messages.

Template mapping:

| allauth default | Fragment template |
|---|---|
| `account/login.html` | `auth/login.html` |
| `account/signup.html` | `auth/register.html` |
| `account/password_reset.html` | `auth/forgot_page.html` |
| `account/password_reset_from_key.html` | `auth/reset_password.html` |
| `account/password_reset_from_key_done.html` | `auth/password_reset_key_done.html` |
| `account/password_reset_done.html` | `auth/password_reset_done.html` |
| `account/email_confirm.html` | `auth/verification_link.html` |
| `account/password_change.html` | `auth/password_change.html` |
| `account/password_set.html` | `auth/password_set.html` |
| `account/email.html` | `auth/email_manage.html` |
| `account/signup_closed.html` | `auth/signup_closed.html` |
| `socialaccount/signup.html` | `auth/social_signup.html` |
| `socialaccount/connections.html` | `auth/social_connections.html` |

### `AuthHTMXSocialAccountAdapter`

Extends `allauth.socialaccount.adapter.DefaultSocialAccountAdapter` and delegates signup checks to `AuthHTMXAdapter`.

### `RegistrationAdapter`

Extends `AuthHTMXAdapter` and routes email confirmation into the site's email service.

```python
ACCOUNT_ADAPTER = "plugins.accounts.adapters.RegistrationAdapter"
SOCIALACCOUNT_ADAPTER = "plugins.accounts.adapters.AuthHTMXSocialAccountAdapter"
```

## HTMX flow

```
Browser GET /auth/login/
├── HX-Request: true  →  AuthHTMXAdapter  →  auth/login.html (bare fragment)
└── (no header)       →  AuthHTMXAdapter  →  skeleton.html wrapping auth/login.html
```

## Customization guide

### Change the skeleton wrapper

Override `layout/auth/skeleton.html` in the site templates directory.

### Add a new auth fragment

1. Create the template at `templates/auth/my_view.html`.
2. Add the mapping in `AuthHTMXAdapter.TEMPLATE_MAP`:

```python
"account/my_view.html": "auth/my_view.html",
```

### Customize social providers

Social provider adapters live in `plugins/accounts/adapters.py`. Add provider-specific logic in `pre_social_login`.

### MFA / 2FA

Custom TOTP-based 2FA is available in profile settings via `two_factor_enabled` / `two_factor_secret` on the profile model. Optional `allauth.mfa` is available for WebAuthn/passkey support.

## Social login

Google and Facebook OAuth are integrated via django-allauth's `socialaccount` app.

### Environment variables

```
GOOGLE_OAUTH_CLIENT_ID=your-google-client-id
GOOGLE_OAUTH_SECRET=your-google-client-secret
FACEBOOK_OAUTH_CLIENT_ID=your-facebook-app-id
FACEBOOK_OAUTH_SECRET=your-facebook-app-secret
```

### Provider configuration

```python
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
        "OAUTH_PKCE_ENABLED": True,
        "APP": {
            "client_id": env("GOOGLE_OAUTH_CLIENT_ID", default=""),
            "secret": env("GOOGLE_OAUTH_SECRET", default=""),
            "key": "",
        },
    },
    "facebook": {
        "METHOD": "oauth2",
        "SCOPE": ["email", "public_profile"],
        "APP": {
            "client_id": env("FACEBOOK_OAUTH_CLIENT_ID", default=""),
            "secret": env("FACEBOOK_OAUTH_SECRET", default=""),
            "key": "",
        },
    },
}
```

### Template usage

Social buttons must use standard `<a>` elements — never `hx-post`, because OAuth redirects cannot be handled by HTMX:

```django
{% load socialaccount %}
{% get_providers as socialaccount_providers %}
{% if socialaccount_providers %}
  {% for provider in socialaccount_providers %}
    <a href="{% provider_login_url provider.id %}" class="btn btn--social">
      Continue with {{ provider.name }}
    </a>
  {% endfor %}
{% endif %}
```

## Testing

### Running auth tests

```bash
pytest tests/unit/test_auth_fragments.py -v
pytest tests/unit/test_auth_notifications.py -v
pytest tests/unit/test_app_structure.py -v

# Integration tests require running containers
CTC_BASE_URL=http://localhost:5070 STRUCTA_BASE_URL=http://localhost:5080 \
  pytest tests/integration/test_auth_flows.py -v
```

### Property-based checks

Auth templates should satisfy these properties:

| # | Property |
|---|----------|
| 1 | All `auth/` templates are pure fragments (no `{% extends %}`) |
| 2 | No `pipelines:` URL namespace references remain |
| 3 | All forms have `strategy` and `supports_sse` inputs |
| 4 | Social buttons use `<a>` not `hx-post` |
| 5 | HTMX requests return bare fragments |
| 6 | Non-HTMX requests return skeleton-wrapped fragments |

## Recommendations

1. Move the duplicated `AuthHTMXAdapter` into `django-fusion` so all sites share one implementation.
2. Add a `AUTH_SKELETON_TEMPLATE` setting instead of hardcoding `layout/auth/skeleton.html`.
3. Document the exact `ACCOUNT_FORMS` and `SOCIALACCOUNT_FORMS` overrides per site.
4. Add provider-specific `pre_social_login` hooks for domain restrictions or auto-group assignment.
