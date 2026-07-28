# Libs Integration Guide

Comprehensive reference for the three internal Python libraries used across the workspace.

---

## Overview

The workspace uses three internal Python libraries installed as git submodules under `libs/`.
They follow a strict layered dependency order:

```
django-fusion  (testing only — never in production code)
     ↑
crafts-ai (automation layer — depends on django-fusion)
     ↑
django-fusion (foundation layer — zero external lib dependencies)
```

Each library is installed into the workspace virtual environment via `uv`:

```toml
# pyproject.toml (workspace root)
[tool.uv.sources]
django-fusion = { path = "libs/django-fusion", editable = true }
crafts-ai = { path = "libs/crafts-ai", editable = true }
django-fusion  = { path = "libs/django-fusion",  editable = true }
```

---

## django-fusion (Foundation)

**Location:** `libs/django-fusion/`
**PyPI:** `django-fusion`

### What It Provides

Pure Django foundation layer with zero Wagtail/Celery/rseal dependencies:

- **Models:** `BaseModel`, `TimestampedModel`, `SoftDeleteMixin`
- **Managers:** `RoleHierarchyManager`, `GroupAccessControl`
- **Middleware:** `ErrorTrackerMiddleware`
- **Validators:** `UniqueFieldValidator`, `SlugFieldValidator`
- **Domain:** `RoleContextPayload` (dataclass for role display context)
- **Contrib:** Admin extensions, cache utilities, privacy helpers, email config

### INSTALLED_APPS Setup

```python
INSTALLED_APPS = [
    # ...
    "django_fusion",
    "django_fusion.comp",
    "django_fusion.contrib",
]
```

### Key Classes

#### ErrorTrackerMiddleware

Logs all 4xx/5xx responses with method, path, status, user email, user agent, and IP.
Logs to `django.request.errors` — 5xx at `CRITICAL`, 4xx at `ERROR`.

```python
# settings.py
MIDDLEWARE = [
    # ... other middleware ...
    "django_fusion.middlewares.error_tracker.ErrorTrackerMiddleware",
]
```

#### RoleHierarchyManager

Manages role hierarchy and permission inheritance. Subclass and define `ROLE_HIERARCHY`
and `ROLE_PERMISSIONS`:

```python
from django_fusion.managers import RoleHierarchyManager

class SiteRoleManager(RoleHierarchyManager):
    ROLE_HIERARCHY = {
        "admin": ["supervisor", "user"],
        "supervisor": ["user"],
        "user": [],
    }
    ROLE_PERMISSIONS = {
        "admin": ["auth.add_user", "auth.change_user"],
        "supervisor": ["auth.view_user"],
        "user": [],
    }

mgr = SiteRoleManager()
mgr.assign_user_to_role(request.user, "supervisor")
has_access = mgr.has_permission(request.user, "auth.view_user")
```

#### GroupAccessControl

Static helpers for group-based access control. No instantiation needed:

```python
from django_fusion.managers import GroupAccessControl

# Check group membership
if GroupAccessControl.check_group_access(request.user, ["editors", "admins"]):
    # allow access

# Filter queryset by user's groups
qs = GroupAccessControl.filter_by_group(Article.objects.all(), request.user)
```

#### BaseModel / TimestampedModel / SoftDeleteMixin

```python
from django_fusion.models.base import BaseModel
from django_fusion.models.mixins import TimestampedModel, SoftDeleteMixin

class MyModel(TimestampedModel, SoftDeleteMixin, BaseModel):
    name = models.CharField(max_length=255)

    class Meta:
        app_label = "myapp"
```

### Thin Wrappers Pattern (ctc-research example)

ctc-research uses re-export wrappers so site code never imports from `django_fusion` directly.
This insulates the site from internal API changes:

```python
# ctc-research/www/apps/middleware/error_tracker.py
from django_fusion.middlewares.error_tracker import ErrorTrackerMiddleware
__all__ = ["ErrorTrackerMiddleware"]

# ctc-research/www/apps/services/groups.py
from django_fusion.managers import GroupAccessControl, RoleHierarchyManager
__all__ = ["RoleHierarchyManager", "GroupAccessControl"]
```

VResume follows the same pattern:
```python
# VResume/www/projects/error_tracker.py
from django_fusion.middlewares.error_tracker import ErrorTrackerMiddleware
__all__ = ["ErrorTrackerMiddleware"]
```

### Adding ErrorTrackerMiddleware to a New Site

1. Create the thin wrapper:
   ```python
   # mysite/www/projects/error_tracker.py
   """Mysite error tracker — delegates to django_fusion."""
   from django_fusion.middlewares.error_tracker import ErrorTrackerMiddleware
   __all__ = ["ErrorTrackerMiddleware"]
   ```

2. Add to `settings.py` MIDDLEWARE list (after security middleware, before view middleware):
   ```python
   MIDDLEWARE = [
       "django.middleware.security.SecurityMiddleware",
       "django.contrib.sessions.middleware.SessionMiddleware",
       "www.core.error_tracker.ErrorTrackerMiddleware",
       # ... rest of middleware
   ]
   ```

---

## crafts-ai (Automation)

**Location:** `libs/crafts-ai/`
**PyPI:** `crafts-ai`

### What It Provides

Automation layer for pipelines, email, workflows, and privacy. Depends on `django-fusion`:

- **Email:** `RoleBasedEmailTemplateSelector`, `EmailTemplateRegistry`
- **Services:** `CertificateServiceBase`, `PersonServiceBase`, `MessageServiceBase`, `FormSubmissionService`
- **Middleware:** `PrivacyConsentMiddleware`
- **Payloads:** `CertificatePayload`, `MessagePayload`
- **Chat/Newsletter/AI:** Pipeline modules for async workflows

### INSTALLED_APPS Setup

```python
INSTALLED_APPS = [
    # ...
    "crafts_ai.pipelines",
    "crafts_ai.chat",
    "crafts_ai.email_tools",
    "crafts_ai.newsletter",
    "crafts_ai.tasks",
    "crafts_ai.seeder",
    "crafts_ai.ai",
]
```

### Required Settings

```python
# Privacy consent middleware configuration
PRIVACY_CONSENT_MIDDLEWARE = {
    "PROTECTED_PATHS": ["/accounts/login/", "/accounts/signup/"],
    "PRIVACY_POLICY_MODEL": "accounts.PrivacyPolicy",
    "PRIVACY_CONSENT_MODEL": "accounts.PrivacyConsent",
    "TERMS_MODEL": "accounts.TermsOfService",
    "TERMS_CONSENT_MODEL": "accounts.TermsConsent",
}
```

### Key Classes

#### RoleBasedEmailTemplateSelector

Selects and renders role-based email templates. Falls back to settings for site name/URL/email:

```python
from crafts_ai.email import RoleBasedEmailTemplateSelector

selector = RoleBasedEmailTemplateSelector(
    site_name="CTC Research",
    site_url="https://ctc-research.com",
    support_email="support@ctc-research.com",
)

# Render an email
html, text = selector.render_email("user", {"name": "Alice", "course": "Python 101"})

# Build full context
ctx = selector.build_context("alice@example.com", "admin")
```

Subclass to customise template paths:

```python
class CTCEmailSelector(RoleBasedEmailTemplateSelector):
    ROLE_TEMPLATES = {
        "admin": "emails/admin/welcome.html",
        "student": "emails/student/welcome.html",
        "default": "emails/default.html",
    }
```

#### EmailTemplateRegistry

Class-level registry for named email templates:

```python
from crafts_ai.email import EmailTemplateRegistry

# Register templates at app startup (e.g. in AppConfig.ready())
EmailTemplateRegistry.register("welcome", "emails/welcome.html", role="user")
EmailTemplateRegistry.register("cert_issued", "emails/cert_issued.html", role="student")

# Look up later
info = EmailTemplateRegistry.get("welcome")
# {"path": "emails/welcome.html", "role": "user"}
```

#### CertificateServiceBase

```python
from crafts_ai.pipelines.services import CertificateServiceBase
from apps.lms.models import Certificate

class CertificateService(CertificateServiceBase):
    certificate_model = Certificate

# Issue a certificate
ok, msg, cert = CertificateService.issue_certificate(
    content_object=course_enrollment,
    name="Python Fundamentals",
    issuer="CTC Research Academy",
)

# Validate
ok, reason, data = CertificateService.validate_certificate("CERT-A1B2C3D4")

# Dashboard data for a user (cached 5 minutes)
profile = CertificateService.get_certificate_profile(request.user)
```

### Usage in ctc-research

ctc-research wraps `CertificateServiceBase` in `www/apps/services/certificates.py`:

```python
# ctc-research/www/apps/services/certificates.py
from crafts_ai.pipelines.services import CertificateServiceBase
from apps.lms.models import Certificate

class CertificateService(CertificateServiceBase):
    certificate_model = Certificate
```

### Adding Email Templates Per Site

1. Create template files in your site's templates directory, e.g.:
   ```
   ctc-research/assets/templates/emails/student/welcome.html
   ctc-research/assets/templates/emails/admin/alert.html
   ```

2. Register them at startup (in an `AppConfig.ready()` method):
   ```python
   from crafts_ai.email import EmailTemplateRegistry

   class MyAppConfig(AppConfig):
       def ready(self):
           EmailTemplateRegistry.register(
               "student_welcome",
               "emails/student/welcome.html",
               role="student"
           )
   ```

3. Use the selector in a view or task:
   ```python
   from crafts_ai.email import RoleBasedEmailTemplateSelector
   from django.core.mail import send_mail

   selector = RoleBasedEmailTemplateSelector()
   html, text = selector.render_email("student", {"name": user.get_full_name()})
   send_mail("Welcome!", text, settings.DEFAULT_FROM_EMAIL, [user.email], html_message=html)
   ```

---

## django-fusion (Testing)

**Location:** `libs/django-fusion/`
**PyPI:** `django-fusion`

### What It Provides

Unified testing framework. **Never import in production code.**

- **`BaseTestCase`** — Pre-wired test case with users, login helpers
- **`BaseAPITestCase`** — Extends BaseTestCase with JSON API helpers
- **`st_email`, `st_slug`, `st_uuid`** — Hypothesis strategy helpers for property-based tests
- **pytest plugin** — Shared fixtures for pytest sessions
- **Health check utilities** — Production-ready health endpoints

### Activating the pytest Plugin

In `conftest.py` at the repo root:

```python
pytest_plugins = ["django_fusion.tests.pytest_plugin"]
```

Or in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
plugins = ["django_fusion.tests.pytest_plugin"]
```

### BaseTestCase Usage

```python
from django_fusion.tests.base import BaseTestCase

class CoursePageTest(BaseTestCase):
    # self.user (testuser/testpass123) and self.admin_user available automatically

    def test_course_list(self):
        self.login()   # logs in as self.user
        response = self.client.get('/lms/courses/')
        self.assertEqual(response.status_code, 200)

    def test_admin_panel(self):
        self.login_as_admin()
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
```

### BaseAPITestCase Usage

```python
from django_fusion.tests.base import BaseAPITestCase

class CourseAPITest(BaseAPITestCase):
    def test_create_course(self):
        self.login_as_admin()
        response = self.post_json('/api/courses/', {
            "title": "Python 101",
            "price": "49.99",
        })
        data = self.assertJSONSuccess(response)
        self.assertIn("id", data)

    def test_invalid_request(self):
        self.login()
        response = self.post_json('/api/courses/', {})
        self.assertJSONError(response, status_code=400)
```

### Property-Based Testing with st_email, st_slug, st_uuid

```python
from django_fusion.tests.base import BaseTestCase, st_email, st_slug, st_uuid
from hypothesis import given, settings

class EmailValidationPropertyTest(BaseTestCase):
    @given(email=st_email())
    @settings(max_examples=100)
    def test_valid_emails_accepted(self, email):
        """Property: any valid email passes our validator."""
        from django_fusion.filters import UniqueFieldValidator
        from django.contrib.auth import get_user_model
        User = get_user_model()
        # Should not raise on valid emails
        validator = UniqueFieldValidator(User, "email")
        # Only fails if email exists — not on format
        self.assertIsNotNone(email)

    @given(slug=st_slug())
    @settings(max_examples=50)
    def test_slug_field_accepts_valid_slugs(self, slug):
        """Property: all st_slug() values satisfy Django slug format."""
        import re
        self.assertRegex(slug, r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
```

### Replacing VResume's data_populator.py

`VResume/www/tests/data_populator.py` is a standalone script that uses Pillow and Wagtail
directly to create test content. The django-fusion pattern replaces ad-hoc scripts with
managed fixtures and seeder helpers:

**Current approach (standalone script):**
```bash
python manage.py --site=vresume shell < VResume/www/tests/data_populator.py
```

**Recommended approach (BaseTestCase + fixtures):**
```python
# VResume/www/tests/test_portfolio.py
from django_fusion.tests.base import BaseTestCase

class PortfolioPageTest(BaseTestCase):
    fixtures = [
        'VResume/assets/fixtures/auth/user_dummy.json',
        'VResume/assets/fixtures/sites/site_dummy.json',
    ]

    def setUp(self):
        super().setUp()
        # Create Wagtail pages programmatically if needed
        from wagtail.models import Page
        # ... minimal page setup

    def test_homepage_renders(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
```

For generating dummy images (previously Pillow-based), use `django-fusion`'s seeder:
```python
from django_fusion.tests.base import BaseTestCase

class PortfolioTest(BaseTestCase):
    def test_portfolio_page(self):
        self.login()
        response = self.client.get('/portfolio/')
        self.assertContains(response, 'portfolio')
```

---

## Per-Site Integration Status

| Library | ctc-research | lms-demo | VResume |
|---------|:---:|:---:|:---:|
| django-fusion (ErrorTrackerMiddleware) | ✅ thin wrapper | ✅ | ✅ thin wrapper |
| django-fusion (RoleHierarchyManager) | ✅ thin wrapper | ✅ | — |
| django-fusion (GroupAccessControl) | ✅ thin wrapper | ✅ | — |
| django-fusion (BaseModel/mixins) | ✅ | ✅ | ✅ |
| crafts-ai (PrivacyConsentMiddleware) | ✅ thin wrapper | ✅ | — |
| crafts-ai (CertificateServiceBase) | ✅ wrapped | ✅ | — |
| crafts-ai (EmailTemplateRegistry) | ✅ | ✅ | partial |
| crafts-ai (FormSubmissionService) | ✅ | ✅ | ✅ |
| django-fusion (BaseTestCase) | ✅ | ✅ | partial |
| django-fusion (property-based testing) | ✅ | partial | — |

Legend: ✅ integrated, partial = partially used, — = not applicable

---

## See Also

- `libs/django-fusion/README.md` — full osoul API reference
- `libs/crafts-ai/README.md` — full rseal API reference
- `libs/django-fusion/README.md` — full grep API reference
- `assets/ASSETS_GUIDE.md` — frontend build reference
- `docs/infrastructure/INFRASTRUCTURE_GUIDE.md` — Docker/compose stack
