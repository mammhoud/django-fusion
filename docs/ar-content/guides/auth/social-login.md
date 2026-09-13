---
title: إعداد تسجيل الدخول الاجتماعي
description: دمج OAuth عبر Google وFacebook باستخدام تطبيق socialaccount في django-allauth.
---

# إعداد تسجيل الدخول الاجتماعي

يُدمج OAuth لكلٍّ من Google وFacebook عبر تطبيق `socialaccount` في django-allauth.

## INSTALLED_APPS

```python
INSTALLED_APPS = [
    ...
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.facebook",
    ...
]
```

## SOCIALACCOUNT_PROVIDERS

```python
# configs/base/auth.py
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

## متغيرات البيئة

اضبط هذه القيم في ملف `.env` أو في أسرار النشر:

```
GOOGLE_OAUTH_CLIENT_ID=your-google-client-id
GOOGLE_OAUTH_SECRET=your-google-client-secret
FACEBOOK_OAUTH_CLIENT_ID=your-facebook-app-id
FACEBOOK_OAUTH_SECRET=your-facebook-app-secret
```

## إعداد تطبيق Google OAuth

1. اذهب إلى [Google Cloud Console](https://console.cloud.google.com/)
2. أنشئ مشروعاً جديداً أو اختر مشروعاً قائماً
3. فعّل **Google+ API** أو **Google Identity**
4. اذهب إلى **Credentials** ← **Create Credentials** ← **OAuth 2.0 Client ID**
5. اضبط **Authorized redirect URIs**:
   - `https://ctc-research.com/accounts/google/login/callback/`
   - `https://structa.cloud/accounts/google/login/callback/`
6. انسخ Client ID وSecret إلى متغيرات البيئة

## إعداد تطبيق Facebook OAuth

1. اذهب إلى [Facebook Developer Portal](https://developers.facebook.com/)
2. أنشئ تطبيقاً جديداً من نوع **Consumer**
3. أضف منتج **Facebook Login**
4. اضبط **Valid OAuth Redirect URIs**:
   - `https://ctc-research.com/accounts/facebook/login/callback/`
   - `https://structa.cloud/accounts/facebook/login/callback/`
5. انسخ App ID وSecret إلى متغيرات البيئة

## إعداد مشرف Django

بعد ضبط متغيرات البيئة، أنشئ سجلات `SocialApp` في مشرف Django:

1. اذهب إلى `/admin/socialaccount/socialapp/`
2. أضف SocialApp جديداً لـ Google:
   - Provider: Google
   - Name: Google
   - Client ID: (من متغيرات البيئة)
   - Secret key: (من متغيرات البيئة)
   - Sites: اختر موقعك
3. كرّر الخطوات لـ Facebook

## استخدام القوالب

تستخدم الأزرار الاجتماعية عناصر `<a>` قياسية — **ولا تستخدم `hx-post` أبداً** (لا يستطيع HTMX التعامل مع إعادات توجيه OAuth):

```html
{% load socialaccount %}
{% get_providers as socialaccount_providers %}
{% if socialaccount_providers %}
<div class="auth__social row">
  {% for provider in socialaccount_providers %}
    {% if provider.id == "google" %}
    <div class="col-xxl-6 d-grid">
      <a href="{% provider_login_url 'google' %}"
         class="btn btn--social bg-google mb-2 mb-xxl-0">
        <i class="fab fa-google me-2"></i>
        {% trans "Continue with Google" %}
      </a>
    </div>
    {% endif %}
  {% endfor %}
</div>
{% endif %}
```

## عناوين الاستدعاء (Callback)

| المزوّد | عنوان الاستدعاء |
|----------|-------------|
| Google | `/accounts/google/login/callback/` |
| Facebook | `/accounts/facebook/login/callback/` |

يتولّى allauth هذه العناوين تلقائياً عند تضمين `allauth.urls` على المسار `/accounts/`.

<!-- AI-generated: review needed -->
