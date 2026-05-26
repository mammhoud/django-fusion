# Design Document

## Overview

This design covers the consolidation of duplicated business logic from both `ctc-research.com` and `structa.cloud` into the shared packages `django-osoul` and `django-rseal`, alongside a domain-aligned rename of all Website apps. The two concerns are orthogonal but executed together to avoid a second round of import-path churn.

**Goals:**
- Single source of truth for every service, manager, middleware, and payload class
- App labels that communicate domain intent (`accounts`, `content`, `lms`, `alliance`)
- All tests using `django-grep` base classes and utilities
- Dependency direction enforced by `import-linter` in CI
- Zero deprecation shims — every import updated in-place

**Non-goals:**
- Changing the public HTTP API of either Website
- Altering database schema beyond what is required for safe renames
- Introducing new product features


## Architecture

### Package Dependency Graph

```
stdlib
  └── nawaai          (AI/MCP — zero Django imports)
        └── django-osoul   (pure Django — no Wagtail, no Celery, no django-rseal)
              └── django-rseal   (Django + Wagtail + Celery)
                    └── ctc-research.com  (Website)
                    └── structa.cloud     (Website)

django-grep  (depends on osoul + rseal, used only in tests — never in production code)
```

This direction is enforced by `import-linter` contracts checked in CI. Any import that violates the direction causes a pipeline failure.

### High-Level Component Map

```
django-osoul/
  domain/           ← primitive-only Payloads / DTOs
  managers/         ← RoleHierarchyManager, GroupAccessControl
  middlewares/      ← ErrorTrackerMiddleware
  services/         ← pure-Django service base classes
  filters/          ← UniqueFieldValidator, SlugFieldValidator (form validators)

django-rseal/
  email/            ← RoleBasedEmailTemplateSelector, EmailTemplateRegistry
  pipelines/
    managers/       ← CachedManager, BaseManager (already present)
    models/         ← Person, Certificate, Message (already present)
    services/       ← CertificateServiceBase, PersonServiceBase, MessageServiceBase, FormSubmissionService
    middlewares/    ← PrivacyConsentMiddleware
  payloads/         ← CertificatePayload, MessagePayload

ctc-research.com/apps/
  accounts/         ← renamed from handlers; thin subclasses only
  lms/              ← renamed from LMS
  content/          ← renamed from pages
  blog/             ← unchanged

structa.cloud/apps/
  accounts/         ← renamed from handlers; thin subclasses only
  alliance/         ← renamed from LMS
  content/          ← renamed from pages
  blog/             ← unchanged
```


## Components and Interfaces

### 1. django-osoul Additions

#### 1.1 `RoleHierarchyManager`

**Module:** `django_osoul.managers.role_hierarchy`
**Public export:** `django_osoul.managers.RoleHierarchyManager`

```python
class RoleHierarchyManager:
    """
    Manages role hierarchy and permission inheritance.
    Pure Django — no Wagtail, no Celery.

    Usage:
        mgr = RoleHierarchyManager()
        perms = mgr.get_all_permissions_for_role("admin")
        hierarchy = mgr.get_role_hierarchy("supervisor")
    """
    ROLE_HIERARCHY: dict[str, list[str]]   # injected via subclass or constructor
    ROLE_PERMISSIONS: dict[str, list[str]] # injected via subclass or constructor

    def get_all_permissions_for_role(self, role: str) -> set[str]: ...
    def get_role_hierarchy(self, role: str) -> list[str]: ...
    def create_or_update_group(self, role: str) -> tuple[Group, bool]: ...
    def assign_user_to_role(self, user: User, role: str) -> bool: ...
    def assign_user_to_multiple_roles(self, user: User, roles: list[str]) -> bool: ...
    def get_user_roles(self, user: User) -> list[str]: ...
    def get_user_permissions(self, user: User) -> set[str]: ...
    def has_role(self, user: User, role: str) -> bool: ...
    def has_permission(self, user: User, permission: str) -> bool: ...
```

Website subclasses override `ROLE_HIERARCHY` and `ROLE_PERMISSIONS` as class attributes.

#### 1.2 `GroupAccessControl`

**Module:** `django_osoul.managers.group_access`
**Public export:** `django_osoul.managers.GroupAccessControl`

```python
class GroupAccessControl:
    @staticmethod
    def check_group_access(user: User, required_groups: list[str]) -> bool: ...
    @staticmethod
    def check_role_access(user: User, required_role: str) -> bool: ...
    @staticmethod
    def get_accessible_groups(user: User) -> list[Group]: ...
    @staticmethod
    def filter_by_group(queryset, user: User, group_field: str = "groups"): ...
```

#### 1.3 `ErrorTrackerMiddleware`

**Module:** `django_osoul.middlewares.error_tracker`
**Public export:** `django_osoul.middlewares.ErrorTrackerMiddleware`

```python
class ErrorTrackerMiddleware:
    """
    Logs 4xx and 5xx responses with request details.
    No website-specific configuration.
    """
    def __init__(self, get_response): ...
    def __call__(self, request): ...
    def _log_error(self, request, response) -> None: ...
```

#### 1.4 Form Validators

**Module:** `django_osoul.filters.validators`
**Public export:** `django_osoul.filters.UniqueFieldValidator`, `django_osoul.filters.SlugFieldValidator`

```python
class UniqueFieldValidator:
    """Validates that a field value is unique within a queryset."""
    def __init__(self, queryset, field_name: str, message: str = None): ...
    def __call__(self, value) -> None: ...

class SlugFieldValidator:
    """Validates slug format and uniqueness."""
    def __init__(self, queryset=None, message: str = None): ...
    def __call__(self, value) -> None: ...
```

#### 1.5 Primitive Payloads

**Module:** `django_osoul.domain.payloads`
**Public export:** `django_osoul.domain`

Payloads that carry only primitive/stdlib types live here. Example:

```python
@dataclass
class RoleContextPayload:
    role: str
    role_display: str
    role_color: str
    permissions: list[str]
```

---

### 2. django-rseal Additions

#### 2.1 `RoleBasedEmailTemplateSelector`

**Module:** `django_rseal.email.template_selector`
**Public export:** `django_rseal.email.RoleBasedEmailTemplateSelector`

```python
class RoleBasedEmailTemplateSelector:
    """
    Selects and renders role-based email templates.
    Accepts site-specific defaults via constructor or Django settings.

    Usage:
        selector = RoleBasedEmailTemplateSelector(
            site_name="Structa",
            site_url="https://structa.cloud",
            support_email="support@structa.cloud",
        )
        path = selector.get_template_path("admin")
        html, text = selector.render_email("admin", context)
        ctx = selector.build_context("user@example.com", "admin")
    """
    ROLE_TEMPLATES: dict[str, str]   # overridable via subclass
    LEGACY_TEMPLATES: dict[str, str] # overridable via subclass

    def __init__(
        self,
        site_name: str = None,
        site_url: str = None,
        support_email: str = None,
    ): ...

    def get_template_path(self, role: str, use_legacy: bool = False) -> str: ...
    def render_email(self, role: str, context: dict, use_legacy: bool = False) -> tuple[str, str]: ...
    def get_role_context(self, role: str) -> dict: ...
    def build_context(self, email: str, role: str, **kwargs) -> dict: ...
```

#### 2.2 `EmailTemplateRegistry`

**Module:** `django_rseal.email.registry`
**Public export:** `django_rseal.email.EmailTemplateRegistry`

```python
class EmailTemplateRegistry:
    @classmethod
    def register(cls, name: str, template_path: str, role: str = None) -> None: ...
    @classmethod
    def get(cls, name: str) -> dict | None: ...
    @classmethod
    def list_templates(cls) -> dict: ...
    @classmethod
    def get_by_role(cls, role: str) -> dict | None: ...
```

#### 2.3 `CertificateServiceBase`

**Module:** `django_rseal.pipelines.services.certificate`
**Public export:** `django_rseal.pipelines.services.CertificateServiceBase`

```python
class CertificateServiceBase:
    """
    Base service for certificate operations.
    Concrete Certificate model injected via class attribute.

    Usage:
        class CertificateService(CertificateServiceBase):
            certificate_model = Certificate
    """
    certificate_model: type  # set by subclass

    @classmethod
    def issue_certificate(
        cls,
        content_object,
        name: str,
        issuer: str,
        issue_date: date = None,
        expiry_date: date = None,
        **kwargs,
    ) -> tuple[bool, str, Any]: ...

    @classmethod
    def validate_certificate(
        cls,
        certificate_id: str,
        issuer: str = None,
        recipient_name: str = None,
    ) -> tuple[bool, str, Any]: ...

    @classmethod
    def get_certificate_profile(cls, user) -> dict: ...

    @classmethod
    def generate_certificate_report(
        cls,
        content_object,
        start_date: date = None,
        end_date: date = None,
    ) -> dict: ...
```

#### 2.4 `PersonServiceBase`

**Module:** `django_rseal.pipelines.services.person`
**Public export:** `django_rseal.pipelines.services.PersonServiceBase`

```python
class PersonServiceBase:
    """
    Base service for person/profile operations.
    Wagtail profile linking is handled via a configurable hook.
    """
    @staticmethod
    def create_person_with_profile(user: User, **defaults) -> tuple[Person, bool]: ...
    @staticmethod
    def get_user_profile_information(user: User) -> dict: ...
    @staticmethod
    def sync_person_with_user(person: Person, user: User) -> bool: ...
    @staticmethod
    def update_notification_preferences(
        person_id: str,
        preferences: dict[str, bool],
    ) -> tuple[bool, str]: ...
    @staticmethod
    def invite_person_to_register(
        person_id: str,
        inviter: User,
        invitation_type: str = "join",
        message: str = "",
    ) -> dict: ...
```

#### 2.5 `MessageServiceBase`

**Module:** `django_rseal.pipelines.services.message`
**Public export:** `django_rseal.pipelines.services.MessageServiceBase`

```python
class MessageServiceBase:
    message_model: type  # set by subclass

    @classmethod
    def send_message(
        cls,
        sender,
        recipient,
        subject: str,
        content: str,
        message_type: str = "general",
        **kwargs,
    ) -> tuple[bool, str, Any]: ...

    @classmethod
    def send_bulk_notification(
        cls,
        recipients: list,
        subject: str,
        content: str,
        **kwargs,
    ) -> dict[str, int]: ...

    @classmethod
    def get_conversation_thread(
        cls,
        participant_a,
        participant_b,
        page: int = 1,
        page_size: int = 20,
    ) -> dict: ...

    @classmethod
    def get_message_analytics(cls, user, days: int = 30) -> dict: ...
```

#### 2.6 `PrivacyConsentMiddleware`

**Module:** `django_rseal.pipelines.middlewares.privacy_consent`
**Public export:** `django_rseal.pipelines.middlewares.PrivacyConsentMiddleware`

```python
class PrivacyConsentMiddleware:
    """
    Configurable privacy consent middleware.
    No hard-coded model imports — models injected via settings or subclass.

    Usage (in settings):
        PRIVACY_CONSENT_MIDDLEWARE = {
            "PROTECTED_PATHS": ["/accounts/login/", "/accounts/signup/"],
            "PRIVACY_POLICY_MODEL": "accounts.PrivacyPolicy",
            "PRIVACY_CONSENT_MODEL": "accounts.PrivacyConsent",
            "TERMS_MODEL": "accounts.TermsOfService",
            "TERMS_CONSENT_MODEL": "accounts.TermsConsent",
        }
    """
    protected_paths: list[str]
    privacy_policy_model: str
    privacy_consent_model: str
    terms_model: str
    terms_consent_model: str

    def __init__(self, get_response): ...
    def __call__(self, request): ...
    def _is_protected_path(self, path: str) -> bool: ...
    def _get_model(self, dotted_path: str): ...
```

#### 2.7 `FormSubmissionService`

**Module:** `django_rseal.pipelines.services.form_submission`
**Public export:** `django_rseal.pipelines.services.FormSubmissionService`

```python
class FormSubmissionService:
    submission_model: type  # set by subclass or class attribute

    @classmethod
    def save_submission(
        cls,
        form_id: str,
        data: dict,
        page=None,
        ip_address: str = None,
        user_agent: str = "",
    ) -> Any: ...

    @classmethod
    def send_notification_email(
        cls,
        submission,
        recipients: list[str],
        subject: str = None,
        template_name: str = "email/form_submission_notification.html",
    ) -> bool: ...

    @classmethod
    def get_submissions_for_form(
        cls,
        form_id: str,
        limit: int = None,
        unread_only: bool = False,
    ) -> list: ...

    @classmethod
    def get_submission_stats(cls, form_id: str = None) -> dict: ...
```

#### 2.8 Payloads

**Module:** `django_rseal.payloads`

```python
@dataclass
class CertificatePayload:
    id: str
    certificate_id: str
    name: str
    issuer: str
    issue_date: date
    expiry_date: date | None
    recipient: str
    status: str
    is_verified: bool
    verification_status: str

    def to_dict(self) -> dict: ...

    @classmethod
    def from_dict(cls, data: dict) -> "CertificatePayload": ...


@dataclass
class MessagePayload:
    id: str
    subject: str
    content: str
    created_at: datetime
    sender_id: str
    recipient_id: str
    is_read: bool
    read_at: datetime | None

    def to_dict(self) -> dict: ...

    @classmethod
    def from_dict(cls, data: dict) -> "MessagePayload": ...
```


### 3. django-grep Enhancements

#### 3.1 Hypothesis Strategy Helpers

**Module:** `django_grep.tests.base` (additions)

```python
from hypothesis import strategies as st

def st_email() -> st.SearchStrategy[str]:
    """Hypothesis strategy for valid email addresses."""
    ...

def st_slug() -> st.SearchStrategy[str]:
    """Hypothesis strategy for valid Django slug strings."""
    ...

def st_uuid() -> st.SearchStrategy[str]:
    """Hypothesis strategy for UUID4 strings."""
    ...
```

These wrap `hypothesis.strategies` so website tests never import `hypothesis` directly.

#### 3.2 pytest Plugin Registration

The existing `django_grep.tests.pytest_plugin` is already implemented. Both websites activate it by adding to `pyproject.toml`:

```toml
[tool.pytest.ini_options]
plugins = ["django_grep.tests.pytest_plugin"]
```

Or via `conftest.py` at the repo root:
```python
pytest_plugins = ["django_grep.tests.pytest_plugin"]
```

---

### 4. App Rename Design

#### 4.1 Rename Mapping

| Website | Old name | New name | Old label | New label |
|---------|----------|----------|-----------|-----------|
| both | `apps.handlers` | `apps.accounts` | `handlers` | `accounts` |
| ctc-research.com | `apps.LMS` | `apps.lms` | `lms` | `lms` |
| structa.cloud | `apps.LMS` | `apps.alliance` | `lms` | `alliance` |
| both | `apps.pages` | `apps.content` | `pages` | `content` |

#### 4.2 AppConfig Changes

Each renamed app gets an updated `AppConfig`:

```python
# apps/accounts/apps.py
class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounts"
    label = "accounts"
    verbose_name = _("Accounts")
```

#### 4.3 Directory Rename

```
apps/handlers/  →  apps/accounts/
apps/LMS/       →  apps/lms/        (ctc)
apps/LMS/       →  apps/alliance/   (structa)
apps/pages/     →  apps/content/
```

All `__init__.py`, `apps.py`, `migrations/`, and sub-modules move with the directory. No files are left behind.

#### 4.4 Standard Sub-Module Layout

Every Domain_App follows this layout:

```
apps/<domain_app>/
├── __init__.py
├── apps.py
├── admin/
├── filters/
├── forms/
├── managers/
├── middleware/
├── migrations/
├── models/
├── services/
├── snippets/          (Wagtail only)
├── templates/
├── templatetags/
├── views/
└── wagtail_hooks.py   (Wagtail only)
```

Sub-modules named `handlers`, `processors`, or `registration` are dissolved: their contents are redistributed into the standard layout above.


## Data Models

### Payload Dataclasses

Both payloads live in `django_rseal.payloads` because they reference Django model field types (`date`, `datetime`) and are consumed by services that interact with Django models.

```python
# django_rseal/payloads.py

from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import date, datetime


@dataclass
class CertificatePayload:
    """
    Structured result for certificate operations.
    Validates: Requirements 4.4
    """
    id: str
    certificate_id: str
    name: str
    issuer: str
    issue_date: date
    expiry_date: date | None
    recipient: str
    status: str
    is_verified: bool
    verification_status: str

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "CertificatePayload":
        return cls(**data)


@dataclass
class MessagePayload:
    """
    Structured result for message operations.
    Validates: Requirements 4.5
    """
    id: str
    subject: str
    content: str
    created_at: datetime
    sender_id: str
    recipient_id: str
    is_read: bool
    read_at: datetime | None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "MessagePayload":
        return cls(**data)
```

### Migration Strategy for App Renames

Each app rename requires a migration that preserves the existing database table. Django uses the app label as the table prefix by default (`<app_label>_<model_name>`).

**Pattern for label-only rename (table name unchanged):**

```python
# apps/accounts/migrations/0001_rename_app_label.py
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [("handlers", "0NNN_last_migration")]

    operations = [
        # AlterModelTable for every model in the app
        migrations.AlterModelTable(name="person", table="handlers_person"),
        migrations.AlterModelTable(name="certificate", table="handlers_certificate"),
        # ... repeat for all models
    ]
```

This keeps the physical table name as `handlers_*` while Django's ORM now refers to the app as `accounts`. No data is moved.

**Pattern for model move to shared package (`SeparateDatabaseAndState`):**

```python
operations = [
    migrations.SeparateDatabaseAndState(
        state_operations=[
            migrations.DeleteModel(name="Certificate"),
        ],
        database_operations=[],  # table stays, ORM state is removed
    )
]
```

The shared package's own migration creates the model state pointing at the existing table.

### ContentType Reference Updates

After renaming, all `ContentType.objects.get(app_label="handlers")` calls must be updated to `app_label="accounts"`. A data migration handles existing `ContentType` rows:

```python
def update_content_types(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    ContentType.objects.filter(app_label="handlers").update(app_label="accounts")
    ContentType.objects.filter(app_label="pages").update(app_label="content")
    # lms → lms (ctc, no change needed)
    # lms → alliance (structa)
    ContentType.objects.filter(app_label="lms").update(app_label="alliance")
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system — essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

Property-based testing (PBT) is applicable here because the extracted classes are pure-function-like services and managers whose behavior varies meaningfully with input, and 100+ iterations will surface edge cases (empty roles, unusual email formats, large payloads, boundary pagination) that example-based tests miss.

The PBT library used is **Hypothesis** (`hypothesis` is already installed in the monorepo venv).

---

### Property 1: Template path is always non-empty

For any non-empty role string, `RoleBasedEmailTemplateSelector.get_template_path(role)` must return a non-empty string. The selector must never return `None`, `""`, or raise an exception — it falls back to the default template for unknown roles.

**Validates: Requirements 11.1**

---

### Property 2: build_context always contains required keys

For any valid email string and any role string, `RoleBasedEmailTemplateSelector.build_context(email, role)` must return a dict that contains all five keys: `email`, `role`, `site_name`, `site_url`, and `support_email`. Additional keys are permitted but these five are mandatory.

**Validates: Requirements 11.2**

---

### Property 3: Permission computation is idempotent

For any role string (including undefined roles), calling `RoleHierarchyManager.get_all_permissions_for_role(role)` twice in succession must return the same `set[str]`. The result must be deterministic and not depend on call order or internal mutable state between calls.

**Validates: Requirements 11.3**

---

### Property 4: Role hierarchy always starts with the queried role

For any role defined in `RoleHierarchyManager.ROLE_HIERARCHY`, `get_role_hierarchy(role)` must return a list whose first element is `role` itself. The role is always a member of its own hierarchy.

**Validates: Requirements 11.4**

---

### Property 5: CertificatePayload serialization round-trip

For any `CertificatePayload` instance constructed with arbitrary valid field values, calling `payload.to_dict()` followed by `CertificatePayload.from_dict(d)` must produce an object that is equal to the original (`==` comparison on all fields). No data is lost or mutated during the round-trip.

**Validates: Requirements 11.5**

---

### Property 6: PersonManager.get_or_create_for_user is idempotent

For any Django `User` instance, calling `PersonManager.get_or_create_for_user(user)` twice must return `(person, False)` on the second call — the same `Person` object, with `created=False`. No duplicate `Person` rows are created regardless of how many times the method is called.

**Validates: Requirements 11.7**

---

### Property 7: Pagination covers the full conversation without gaps or duplicates

For any conversation containing N messages (N ≥ 0), paginating through all pages of `MessageServiceBase.get_conversation_thread` with any valid `page_size` must satisfy: the union of all page results equals the full set of messages, with no message appearing on more than one page and no message missing from all pages.

**Validates: Requirements 11.8**


## Error Handling

### Extraction Errors

**Import resolution failures** — if a module being moved still has an import from the old path, the CI `import-linter` step fails with a descriptive message identifying the offending import. The developer must fix the import before the PR can merge.

**Missing grep verification** — the import-update workflow requires a grep pass before deletion. If the grep finds remaining references, the deletion step is blocked. This is enforced by the task checklist (see tasks.md).

### Migration Errors

**Irreversible migrations** — all migrations must pass `migrate <app> zero` in a test environment before merging. If a migration is not reversible, it is rejected.

**ContentType mismatch** — after renaming, any `GenericForeignKey` or `ContentType` lookup using the old `app_label` will silently return no results. The data migration that updates `ContentType` rows must run before any application code that queries by `app_label`.

**ForeignKey app_label drift** — `ForeignKey(to="handlers.Person")` string references must be updated to `"accounts.Person"`. The migration generator (`makemigrations`) will catch these if the model is still in the old location, but after the rename it will silently use the new label. A grep for `"handlers."` in migration files is part of the verification step.

### Service Errors

All service methods follow the existing `(success: bool, message: str, result: Any)` tuple convention. Exceptions are caught internally and returned as `(False, str(e), None)`. This convention is preserved in the base classes so website subclasses inherit consistent error handling.

### Middleware Errors

`PrivacyConsentMiddleware` uses lazy model loading (`apps.get_model(dotted_path)`) to avoid import-time failures when the consent models are not yet migrated. If the model cannot be resolved, the middleware logs a warning and passes the request through rather than raising a 500.

`ErrorTrackerMiddleware` never raises — it logs and always calls `get_response(request)`.


## Testing Strategy

### Overview

The testing strategy uses a dual approach: example-based unit tests for specific scenarios and property-based tests for universal invariants. Both are complementary.

### Property-Based Tests (Hypothesis)

Library: **Hypothesis** (already installed, `hypothesis>=6.0`)
Minimum iterations: **100 per property** (`@settings(max_examples=100)`)
Tag format: `# Feature: core-logic-consolidation-and-app-restructure, Property N: <property_text>`

Each property maps to one `@given`-decorated test function in the shared package's own test suite.

```python
# venv/libs/django-rseal/tests/test_email_selector_properties.py

# Feature: core-logic-consolidation-and-app-restructure, Property 1: Template path is always non-empty
# Feature: core-logic-consolidation-and-app-restructure, Property 2: build_context always contains required keys
from hypothesis import given, settings
from hypothesis import strategies as st
from django_grep.tests.base import st_email, st_slug
from django_rseal.email import RoleBasedEmailTemplateSelector

@given(st.text(min_size=1))
@settings(max_examples=100)
def test_get_template_path_always_non_empty(role: str):
    # Feature: core-logic-consolidation-and-app-restructure, Property 1
    selector = RoleBasedEmailTemplateSelector()
    result = selector.get_template_path(role)
    assert isinstance(result, str) and len(result) > 0

@given(st_email(), st.text(min_size=1))
@settings(max_examples=100)
def test_build_context_always_has_required_keys(email: str, role: str):
    # Feature: core-logic-consolidation-and-app-restructure, Property 2
    selector = RoleBasedEmailTemplateSelector()
    ctx = selector.build_context(email, role)
    for key in ("email", "role", "site_name", "site_url", "support_email"):
        assert key in ctx
```

```python
# venv/libs/django-osoul/tests/test_role_hierarchy_properties.py

# Feature: core-logic-consolidation-and-app-restructure, Property 3: Permission computation is idempotent
# Feature: core-logic-consolidation-and-app-restructure, Property 4: Role hierarchy always starts with the queried role
from hypothesis import given, settings, assume
from hypothesis import strategies as st
from django_osoul.managers import RoleHierarchyManager

DEFINED_ROLES = ["admin", "supervisor", "user"]

@given(st.text(min_size=1))
@settings(max_examples=100)
def test_get_all_permissions_idempotent(role: str):
    # Feature: core-logic-consolidation-and-app-restructure, Property 3
    mgr = RoleHierarchyManager()
    result1 = mgr.get_all_permissions_for_role(role)
    result2 = mgr.get_all_permissions_for_role(role)
    assert result1 == result2

@given(st.sampled_from(DEFINED_ROLES))
@settings(max_examples=100)
def test_role_hierarchy_starts_with_role(role: str):
    # Feature: core-logic-consolidation-and-app-restructure, Property 4
    mgr = RoleHierarchyManager()
    hierarchy = mgr.get_role_hierarchy(role)
    assert len(hierarchy) >= 1
    assert hierarchy[0] == role
```

```python
# venv/libs/django-rseal/tests/test_payload_properties.py

# Feature: core-logic-consolidation-and-app-restructure, Property 5: CertificatePayload serialization round-trip
from hypothesis import given, settings
from hypothesis import strategies as st
from datetime import date
from django_rseal.payloads import CertificatePayload

@given(
    id=st.uuids().map(str),
    certificate_id=st.text(min_size=1, max_size=50),
    name=st.text(min_size=1, max_size=100),
    issuer=st.text(min_size=1, max_size=100),
    issue_date=st.dates(),
    expiry_date=st.one_of(st.none(), st.dates()),
    recipient=st.text(min_size=1, max_size=100),
    status=st.sampled_from(["valid", "expired", "pending", "revoked"]),
    is_verified=st.booleans(),
    verification_status=st.text(min_size=1, max_size=50),
)
@settings(max_examples=100)
def test_certificate_payload_round_trip(**kwargs):
    # Feature: core-logic-consolidation-and-app-restructure, Property 5
    payload = CertificatePayload(**kwargs)
    reconstructed = CertificatePayload.from_dict(payload.to_dict())
    assert payload == reconstructed
```

### Unit Tests (Example-Based)

Unit tests focus on:
- Specific examples that demonstrate correct behavior (e.g. `admin` role gets all permissions)
- Integration points between components (e.g. website subclass delegates to base class)
- Edge cases and error conditions (e.g. unknown role returns default template)

Existing tests in `structa.cloud/tests/test_group_management.py` are migrated to use `django_grep.tests.base.BaseTestCase` and moved to `venv/libs/django-osoul/tests/` since they test `RoleHierarchyManager` which moves to `django-osoul`.

### Integration Tests

One integration test per extracted service verifies that the service produces the same result when called from both websites with equivalent inputs (Requirement 11.6). These are example-based (1-3 representative inputs) and live in a shared `tests/integration/` directory.

### Test Migration Checklist

For each test file in `ctc-research.com/tests/` and `structa.cloud/tests/`:

1. Replace `from django.test import TestCase` → `from django_grep.tests.base import BaseTestCase`
2. Replace inline `factory_boy` patterns → `from django_grep.tests.factories import ModelFactory`
3. Replace custom assertion helpers → `from django_grep.tests.assertions import ...`
4. Replace fixture loading → `from django_grep.tests.fixtures import ...`
5. Replace test mixin imports → `from django_grep.tests.mixins import ...`
6. If the test covers logic now in a shared package, move the test to that package's `tests/` directory and replace the website-level test with a thin integration call

### CI Test Commands

```bash
# Unit + property tests for shared packages
pytest venv/libs/django-osoul/tests/ --hypothesis-seed=0
pytest venv/libs/django-rseal/tests/ --hypothesis-seed=0

# Website tests (after migration)
pytest structa.cloud/tests/ --ds=structa.cloud.configs.settings
pytest ctc-research.com/tests/ --ds=ctc-research.com.configs.settings

# Import linter
lint-imports --config .importlinter
```

### import-linter Contract Design

**File:** `.importlinter` at repo root

```ini
[importlinter]
root_packages =
    django_osoul
    django_rseal
    django_grep
    nawaai

[importlinter:contract:osoul-no-wagtail]
name = django-osoul must not import Wagtail or Celery
type = forbidden
source_modules =
    django_osoul
forbidden_modules =
    wagtail
    celery
    django_rseal

[importlinter:contract:rseal-no-websites]
name = django-rseal must not import website apps
type = forbidden
source_modules =
    django_rseal
forbidden_modules =
    apps

[importlinter:contract:nawaai-no-django]
name = nawaai must not import Django
type = forbidden
source_modules =
    nawaai
forbidden_modules =
    django
    django_osoul
    django_rseal

[importlinter:contract:dependency-layers]
name = Dependency layer ordering
type = layers
layers =
    nawaai
    django_osoul
    django_rseal
```

