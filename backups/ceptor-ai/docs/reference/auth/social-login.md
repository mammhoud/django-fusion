# Social Login Setup

Google and Facebook OAuth are integrated via django-allauth's `socialaccount` app.

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

## Environment Variables

Set these in your `.env` file or deployment secrets:

```
GOOGLE_OAUTH_CLIENT_ID=your-google-client-id
GOOGLE_OAUTH_SECRET=your-google-client-secret
FACEBOOK_OAUTH_CLIENT_ID=your-facebook-app-id
FACEBOOK_OAUTH_SECRET=your-facebook-app-secret
```

## Google OAuth App Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable **Google+ API** or **Google Identity**
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
5. Set **Authorized redirect URIs**:
   - `https://ctc-research.com/accounts/google/login/callback/`
   - `https://structa.cloud/accounts/google/login/callback/`
6. Copy the Client ID and Secret to your env vars

## Facebook OAuth App Setup

1. Go to Facebook Developer Portal (https://developers.facebook.com/)
2. Create a new app → **Consumer** type
3. Add **Facebook Login** product
4. Set **Valid OAuth Redirect URIs**:
   - `https://ctc-research.com/accounts/facebook/login/callback/`
   - `https://structa.cloud/accounts/facebook/login/callback/`
5. Copy the App ID and Secret to your env vars

## Django Admin Setup

After setting env vars, create `SocialApp` records in Django admin:

1. Go to `/admin/socialaccount/socialapp/`
2. Add a new SocialApp for Google:
   - Provider: Google
   - Name: Google
   - Client ID: (from env)
   - Secret key: (from env)
   - Sites: select your site
3. Repeat for Facebook

## Template Usage

Social buttons use standard `<a>` elements — **never `hx-post`** (OAuth redirects cannot be handled by HTMX):

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

## Callback URLs

| Provider | Callback URL |
|----------|-------------|
| Google | `/accounts/google/login/callback/` |
| Facebook | `/accounts/facebook/login/callback/` |

These are handled automatically by allauth when `allauth.urls` is included at `/accounts/`.
