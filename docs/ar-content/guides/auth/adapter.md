---
title: محوّل AuthHTMXAdapter
description: محوّل django-allauth مخصّص يفعّل عرض شظايا HTMX لكل شاشات المصادقة.
---

# AuthHTMXAdapter

`AuthHTMXAdapter` هو محوّل django-allauth مخصّص يفعّل عرض شظايا HTMX لكل شاشات المصادقة.

**الموقع:** `plugins/accounts/adapters.py` (كلا الموقعين)

## التسجيل

```python
# configs/base/auth.py
ACCOUNT_ADAPTER = "plugins.accounts.adapters.AuthHTMXAdapter"
SOCIALACCOUNT_ADAPTER = "plugins.accounts.adapters.AuthHTMXSocialAccountAdapter"
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_LOGOUT_REDIRECT_URL = "/"
```

## خريطة القوالب

يربط المحوّل أسماء قوالب allauth الداخلية بقوالب الشظايا في `auth/`:

| افتراضي allauth | قالب الشظية |
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

## كشف HTMX

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

## إشعار تسجيل الخروج

مع `ACCOUNT_LOGOUT_ON_GET = True`، يضيف المحوّل رسالة نجاح قبل إعادة التوجيه:

```python
def logout(self, request):
    messages.success(request, _("You have been signed out successfully."))
    super().logout(request)
```

تُعرَض الرسالة في صفحة الهبوط بعد إعادة التوجيه عبر إطار الرسائل في Django.

## قالب الهيكل

`SKELETON_TEMPLATE = "layout/auth/skeleton.html"` — قالب الأساس ذو التخطيط المنقسم الذي يوفّر غلاف لوحة الترحيب + لوحة النموذج لطلبات الصفحة الكاملة.

<!-- AI-generated: review needed -->
