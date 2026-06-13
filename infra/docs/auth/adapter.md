# AuthHTMXAdapter

`AuthHTMXAdapter` is a custom django-allauth adapter that enables HTMX fragment rendering for all auth views.

**Location:** `plugins/accounts/adapters.py` (both sites)

## Registration

```python
# configs/base/auth.py
ACCOUNT_ADAPTER = "plugins.accounts.adapters.AuthHTMXAdapter"
SOCIALACCOUNT_ADAPTER = "plugins.accounts.adapters.AuthHTMXSocialAccountAdapter"
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_LOGOUT_REDIRECT_URL = "/"
```

## Template Map

The adapter maps allauth's internal template names to `auth/` fragment templates:

| allauth default | Fragment template |
|-----------------|-------------------|
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

## HTMX Detection

```python
def render_response(self, request, template_name, context, status=None):
    is_htmx = request.headers.get("HX-Request", False)
    fragment = render_to_string(template_name, context, request)

    if is_htmx:
        return HttpResponse(fragment)          # bare fragment
    else:
        skeleton_context = {**context, "fragment": fragment}
        skeleton = render_to_string(self.SKELETON_TEMPLATE, skeleton_context, request)
        return HttpResponse(skeleton)          # skeleton wrapping fragment
```

## Logout Notification

With `ACCOUNT_LOGOUT_ON_GET = True`, the adapter adds a success message before redirecting:

```python
def logout(self, request):
    messages.success(request, _("You have been signed out successfully."))
    super().logout(request)
```

The message is rendered on the redirect landing page via Django's messages framework.

## Skeleton Template

`SKELETON_TEMPLATE = "layout/auth/skeleton.html"` — the split-layout base template that provides the welcome panel + form panel chrome for full-page requests.
