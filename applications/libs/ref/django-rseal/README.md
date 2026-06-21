<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/cover.png">
  <img src="assets/cover.png" alt="django-rseal Cover" width="100%">
</picture>

# 🐍 django-rseal

<p align="center">
  <em>Automation Layer — pipelines, services, workflows, email, signals, admin, cache, commands</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/django-rseal/">
    <img src="https://img.shields.io/pypi/v/django-rseal?style=flat-square&logo=pypi&logoColor=white&label=PyPI" alt="PyPI version">
  </a>
  <a href="https://python.org">
    <img src="https://img.shields.io/pypi/pyversions/django-rseal?style=flat-square&logo=python&logoColor=white" alt="Python versions">
  </a>
  <a href="https://github.com/astral-sh/uv">
    <img src="https://img.shields.io/badge/uv-package%20manager-de3d8b?style=flat-square&logo=uv&logoColor=white" alt="uv">
  </a>
  <a href="https://github.com/psf/black">
    <img src="https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square" alt="Code style: black">
  </a>
</p>

---

## ✨ Features

- 🔄 **Automation Pipelines** – Reusable service base classes
- 📧 **Email Automation** – Template selection, registry, sending
- 🌊 **Workflow Orchestration** – Spec task execution
- 🎨 **Wagtail Components** – StreamField blocks, snippets, hooks
- 📦 **`uv`‑ready** – Lightning-fast dependency management
- 🏗️ **Thin Subclass Pattern** – Inject project-specific models via class attributes

---

## 📦 Installation

```bash
# Install with uv (recommended)
uv add django-rseal

# Or with pip
pip install django-rseal
```

Add to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    "django_rseal.pipelines",
    "django_rseal.chat",
    "django_rseal.email_tools",
    "django_rseal.newsletter",
    "django_rseal.tasks",
    "django_rseal.seeder",
    "django_rseal.ai",
]
```

---

## 📖 Public API Reference

### `RoleBasedEmailTemplateSelector`

**Import:** `from django_rseal.email import RoleBasedEmailTemplateSelector`

Selects and renders role-based email templates. Constructor arguments override Django settings; if omitted the selector falls back to `settings.WAGTAIL_SITE_NAME`, `settings.WAGTAILADMIN_BASE_URL`, and `settings.DEFAULT_FROM_EMAIL`.

Subclass and override `ROLE_TEMPLATES` / `LEGACY_TEMPLATES` to customise template paths for a specific website.

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `get_template_path(role, use_legacy)` | `role: str, use_legacy: bool = False` | `str` | Template path for the role. Falls back to `"default"`. Never returns empty. |
| `render_email(role, context, use_legacy)` | `role: str, context: dict, use_legacy: bool = False` | `tuple[str, str]` | Renders the template and returns `(html, text)`. Falls back to default template on error. |
| `get_role_context(role)` | `role: str` | `dict` | Default display context for the role (display name, colour, permissions). |
| `build_context(email, role, **kwargs)` | `email: str, role: str` | `dict` | Complete template context. Always contains `email`, `role`, `site_name`, `site_url`, `support_email`. |

```python
from django_rseal.email import RoleBasedEmailTemplateSelector

selector = RoleBasedEmailTemplateSelector(
    site_name="Structa",
    site_url="https://structa.cloud",
    support_email="support@example.com",
)

# Get template path
path = selector.get_template_path("admin")
# "components/email/admin/base.html"

# Render email
html, text = selector.render_email("user", {"name": "Alice"})

# Build full context
ctx = selector.build_context("alice@example.com", "admin")
# {"email": "alice@example.com", "role": "admin", "site_name": "Structa",
#  "site_url": "...", "support_email": "...", "role_display": "Administrator", ...}
```

---

### `EmailTemplateRegistry`

**Import:** `from django_rseal.email import EmailTemplateRegistry`

Class-level registry for named email templates. All methods are `@classmethod` — no instantiation needed.

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `register(name, template_path, role)` | `name: str, template_path: str, role: str \| None = None` | `None` | Register a template under a unique name. |
| `get(name)` | `name: str` | `dict \| None` | Return the registration dict `{"path": ..., "role": ...}` or `None`. |
| `list_templates()` | — | `dict` | Shallow copy of the full registry. |
| `get_by_role(role)` | `role: str` | `dict \| None` | First registration whose `role` matches, or `None`. |

```python
from django_rseal.email import EmailTemplateRegistry

EmailTemplateRegistry.register("welcome", "emails/welcome.html", role="user")
EmailTemplateRegistry.register("admin_alert", "emails/admin_alert.html", role="admin")

info = EmailTemplateRegistry.get("welcome")
# {"path": "emails/welcome.html", "role": "user"}

by_role = EmailTemplateRegistry.get_by_role("admin")
# {"path": "emails/admin_alert.html", "role": "admin"}

all_templates = EmailTemplateRegistry.list_templates()
```

---

### `CertificateServiceBase`

**Import:** `from django_rseal.pipelines.services import CertificateServiceBase`

Base service for certificate operations. Inject the concrete model via the `certificate_model` class attribute.

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `issue_certificate(content_object, name, issuer, issue_date, expiry_date, **kwargs)` | — | `tuple[bool, str, obj]` | Issue a new certificate. Returns `(True, "Certificate issued successfully", cert)` or `(False, error_msg, None)`. |
| `validate_certificate(certificate_id, issuer, recipient_name)` | `certificate_id: str, issuer: str \| None, recipient_name: str \| None` | `tuple[bool, str, dict]` | Validate a certificate by ID. Returns `(True, "Certificate is valid", data_dict)` or `(False, reason, None)`. |
| `get_certificate_profile(user)` | `user` | `dict` | Certificate dashboard dict for a user. Cached for 5 minutes. |
| `generate_certificate_report(content_object, start_date, end_date)` | `content_object, start_date: date \| None, end_date: date \| None` | `dict` | Report with period, summary, monthly breakdown, and issuer statistics. |

```python
from django_rseal.pipelines.services import CertificateServiceBase
from apps.lms.models import Certificate

class CertificateService(CertificateServiceBase):
    certificate_model = Certificate

ok, msg, cert = CertificateService.issue_certificate(
    content_object=user,
    name="Python Fundamentals",
    issuer="Structa Academy",
)

ok, reason, data = CertificateService.validate_certificate("CERT-A1B2C3D4")
```

---

### `PersonServiceBase`

**Import:** `from django_rseal.pipelines.services import PersonServiceBase`

Base class for person/profile service implementations. Inject the concrete model via `person_model`.

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `create_person(**kwargs)` | `**kwargs` | — | Create a new person. Raises `NotImplementedError` — override in subclass. |
| `update_person(person, **kwargs)` | `person, **kwargs` | — | Update person details. Override in subclass. |
| `get_person(**kwargs)` | `**kwargs` | — | Get person by criteria. Override in subclass. |

```python
from django_rseal.pipelines.services import PersonServiceBase
from apps.accounts.models import Person

class PersonService(PersonServiceBase):
    person_model = Person

    @classmethod
    def create_person(cls, user, **kwargs):
        return cls.person_model.objects.create(user=user, **kwargs)
```

---

### `MessageServiceBase`

**Import:** `from django_rseal.pipelines.services import MessageServiceBase`

Base class for message service implementations. Inject the concrete model via `message_model`.

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `send_message(recipient, subject, body, **kwargs)` | `recipient, subject: str, body: str` | — | Send a message. Override in subclass. |
| `get_messages(user, **kwargs)` | `user, **kwargs` | — | Get messages for a user. Override in subclass. |

```python
from django_rseal.pipelines.services import MessageServiceBase
from apps.accounts.models import Message

class MessageService(MessageServiceBase):
    message_model = Message

    @classmethod
    def send_message(cls, recipient, subject, body, **kwargs):
        return cls.message_model.objects.create(
            recipient=recipient, subject=subject, body=body, **kwargs
        )
```

---

### `FormSubmissionService`

**Import:** `from django_rseal.pipelines.services import FormSubmissionService`

Base class for form submission service implementations. Inject the concrete model via `form_submission_model`.

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `submit_form(form_data, **kwargs)` | `form_data: dict` | — | Submit a form. Override in subclass. |
| `get_submissions(form_id, **kwargs)` | `form_id, **kwargs` | — | Get submissions for a form. Override in subclass. |

```python
from django_rseal.pipelines.services import FormSubmissionService
from apps.content.models import FormSubmission

class ContactFormService(FormSubmissionService):
    form_submission_model = FormSubmission

    @classmethod
    def submit_form(cls, form_data, **kwargs):
        return cls.form_submission_model.objects.create(**form_data)
```

---

### `PrivacyConsentMiddleware`

**Import:** `from django_rseal.pipelines.middlewares import PrivacyConsentMiddleware`

Configurable privacy consent middleware. Models are resolved lazily via `apps.get_model` — no hard-coded model imports. If a model cannot be resolved the middleware logs a warning and passes the request through.

**Setup** — add to `MIDDLEWARE` and configure in settings:

```python
MIDDLEWARE = [
    ...
    "django_rseal.pipelines.middlewares.PrivacyConsentMiddleware",
]

PRIVACY_CONSENT_MIDDLEWARE = {
    "PROTECTED_PATHS": ["/accounts/login/", "/accounts/signup/"],
    "PRIVACY_POLICY_MODEL": "accounts.PrivacyPolicy",
    "PRIVACY_CONSENT_MODEL": "accounts.PrivacyConsent",
    "TERMS_MODEL": "accounts.TermsOfService",
    "TERMS_CONSENT_MODEL": "accounts.TermsConsent",
}
```

When an authenticated user accesses a protected path without having consented, the middleware renders `privacy/consent_required.html` with `policy` and `terms` context variables.

---

### `CertificatePayload`

**Import:** `from django_rseal.payloads import CertificatePayload`

Structured result dataclass for certificate operations. Carries only stdlib types — safe to serialise across process boundaries.

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | UUID string. |
| `certificate_id` | `str` | Human-readable certificate ID (e.g. `"CERT-A1B2C3D4"`). |
| `name` | `str` | Certificate name. |
| `issuer` | `str` | Issuing organisation. |
| `issue_date` | `date` | Date of issue. |
| `expiry_date` | `date \| None` | Expiry date, or `None` if non-expiring. |
| `recipient` | `str` | String representation of the recipient. |
| `status` | `str` | `"valid"`, `"expired"`, `"pending"`, or `"revoked"`. |
| `is_verified` | `bool` | Whether the certificate has been verified. |
| `verification_status` | `str` | Verification status string. |

```python
from django_rseal.payloads import CertificatePayload

payload = CertificatePayload(
    id="abc123",
    certificate_id="CERT-A1B2",
    name="Python Fundamentals",
    issuer="Structa Academy",
    issue_date=date(2025, 1, 1),
    expiry_date=None,
    recipient="Alice Smith",
    status="valid",
    is_verified=True,
    verification_status="verified",
)

# Round-trip serialisation
data = payload.to_dict()
restored = CertificatePayload.from_dict(data)
assert restored == payload
```

---

### `MessagePayload`

**Import:** `from django_rseal.payloads import MessagePayload`

Structured result dataclass for message operations.

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | UUID string. |
| `subject` | `str` | Message subject. |
| `content` | `str` | Message body. |
| `created_at` | `datetime` | Creation timestamp. |
| `sender_id` | `str` | Sender user ID. |
| `recipient_id` | `str` | Recipient user ID. |
| `is_read` | `bool` | Whether the message has been read. |
| `read_at` | `datetime \| None` | When the message was read, or `None`. |

```python
from django_rseal.payloads import MessagePayload
from datetime import datetime

payload = MessagePayload(
    id="msg-001",
    subject="Welcome",
    content="Hello!",
    created_at=datetime.now(),
    sender_id="user-1",
    recipient_id="user-2",
    is_read=False,
    read_at=None,
)

data = payload.to_dict()
restored = MessagePayload.from_dict(data)
```

---

## 🧪 Development Setup (with `uv`)

```bash
uv add "django-rseal[all]" --dev
uv run pytest
uv run ruff check .
uv run ruff format .
```

---

## 🤝 Contributing

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/amazing-feature`).
3. Commit your changes (`git commit -m 'Add some amazing feature'`).
4. Push to the branch (`git push origin feature/amazing-feature`).
5. Open a Pull Request.

---

## 📄 License

MIT License – see the [LICENSE](LICENSE) file for details.

---

## 🛠️ Built With

A heartfelt thank you to the tools and AI assistants that made developing this package a joy.

<p align="center">
  <a href="https://kiro.dev" title="Kiro – AI-powered dev environment">
    <img src="https://img.shields.io/badge/Kiro-AI%20Dev%20Environment-6C63FF?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik0xMiAyTDIgN2wxMCA1IDEwLTV6TTIgMTdsOCA0IDgtNE0yIDEybDggNCA4LTQiLz48L3N2Zz4=" alt="Kiro">
  </a>
  &nbsp;
  <a href="https://claude.ai" title="Claude by Anthropic">
    <img src="https://img.shields.io/badge/Claude-Anthropic%20AI-D97757?style=for-the-badge&logo=anthropic&logoColor=white" alt="Claude">
  </a>
  &nbsp;
  <a href="https://aws.amazon.com" title="Amazon Web Services">
    <img src="https://img.shields.io/badge/AWS-Amazon%20Web%20Services-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white" alt="AWS">
  </a>
  &nbsp;
  <a href="https://www.hostinger.com" title="Hostinger – Web Hosting">
    <img src="https://img.shields.io/badge/Hostinger-Web%20Hosting-673DE6?style=for-the-badge&logo=hostinger&logoColor=white" alt="Hostinger">
  </a>
</p>

---

## 🙌 Acknowledgements

- Built with ❤️ and [`uv`](https://docs.astral.sh/uv/)
- Powered by [Wagtail](https://wagtail.org/) and [Celery](https://docs.celeryq.dev/)
