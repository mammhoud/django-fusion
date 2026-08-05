# LMS — Configuration Reference

> **Domain:** structa.cloud | **Port:** 5071 | **DB:** PostgreSQL `db_structa`

---

## Site Registration

```yaml
# projects/configs/settings/ENV/sites.yml
sites:
  lms:
    domain: structa.cloud
    db_name: db_structa
    port: 5071
    path: lms
    site_id: 2
```

---

## Environment Variables

| Variable | Required | Default | Purpose |
|----------|:--------:|---------|---------|
| `DB_NAME_LMS` | ✅ | `db_structa` | PostgreSQL database name |
| `LMS_HOST` | ✅ | `structa.cloud` | Site domain |
| `DJANGO_SETTINGS_MODULE` | — | `settings` | Settings module path |
| `DJANGO_DEBUG` | — | `False` | Enable debug mode |
| `DJANGO_SECRET_KEY` | ✅ | — | Django secret key |
| `DJANGO_ALLOWED_HOSTS` | — | `*` | Allowed hostnames |
| `STRIPE_API_KEY` | — | — | Stripe payment integration |
| `STRIPE_WEBHOOK_SECRET` | — | — | Stripe webhook verification |
| `PAYPAL_CLIENT_ID` | — | — | PayPal integration |
| `PAYPAL_CLIENT_SECRET` | — | — | PayPal secret |

---

## Django Settings

### `settings.py` Key Sections

```python
# Site identity
SITE_ID = 2
SITE_NAME = "LMS"

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME_LMS", "db_structa"),
        "HOST": os.environ.get("DB_HOST", "postgres"),
    }
}

# Installed apps (site-specific)
LOCAL_APPS = [
    "plugins.accounts",
    "plugins.blog",
    "plugins.lms",          # Courses, lessons, certifications
    "plugins.products",     # Course catalog for payments
    "plugins.profile",
]
```

---

## Plugins

### LMS Plugin (`plugins/lms/`)

Handles course management, student progress, certifications, and learning paths.

| Setting | Value | Purpose |
|---------|-------|---------|
| `LMS_COURSE_PAGE_SIZE` | 12 | Courses per page in listings |
| `LMS_CERTIFICATE_TEMPLATE` | `certificate.html` | Certificate PDF template |
| `LMS_ENROLLMENT_CONFIRMATION` | True | Send email on enrollment |

### Accounts Plugin (`plugins/accounts/`)

Auth adapters configured in `adapters.py`:

```python
class RegistrationAdapter(DefaultAccountAdapter):
    """HTMX-aware registration with fragment rendering."""
    pass

class AuthHTMXSocialAccountAdapter(SocialAccountAdapter):
    """Social auth with HTMX modal integration."""
    pass
```

Supported social providers: Google, Facebook, GitHub.

### Products Plugin (`plugins/products/`)

Bridges courses to payment providers:

| Setting | Value | Purpose |
|---------|-------|---------|
| `PRODUCT_CURRENCY` | `USD` | Default currency |
| `PRODUCT_TAX_RATE` | `0` | Tax rate (0 = no tax) |

---

## Wagtail CMS Configuration

```python
WAGTAIL_SITE_NAME = "LMS"
WAGTAILADMIN_BASE_URL = "https://structa.cloud"
```

### Page Types

| Model | Template | Purpose |
|-------|----------|---------|
| `HomePage` | `home/main.html` | Landing page |
| `CoursePage` | `courses/detail.html` | Course detail with lessons |
| `BlogPage` | `blog/post.html` | Blog post with rich text |
| `ProfilePage` | `profile/dashboard.html` | User dashboard |

---

## Worker Configuration

Background tasks are handled by the shared worker stack (`projects/www/worker/`):

| Worker | Queue | Tasks |
|--------|-------|-------|
| Dramatiq | `email` | Enrollment confirmations, certificate emails, password resets |
| Celery Beat | `scheduled` | Course reminder emails, analytics aggregation |

---

## Docker Compose

```yaml
lms-web:
  build:
    args:
      PROJECT_PATH: lms
  container_name: lms-web
  expose:
    - "5071"
  labels:
    - "traefik.enable=true"
    - "traefik.http.routers.lms.rule=Host(`structa.cloud`)"
  volumes:
    - ./lms/assets/staticfiles:/var/www/sites/lms/static
    - ./lms/assets/media:/var/www/sites/lms/media
```

---

## Related

| Resource | Path |
|----------|------|
| LMS site docs | [`README.md`](README.md) |
| LMS use cases | [`use-cases.md`](use-cases.md) |
| Clone guide | [`clone-guide.md`](clone-guide.md) |
| Backend env setup | [`../../back-env/`](../../back-env/) |
