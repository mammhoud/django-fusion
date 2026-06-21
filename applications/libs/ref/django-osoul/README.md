<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/cover.png">
  <img src="assets/cover.png" alt="django-osoul Cover" width="100%">
</picture>

# 🐍 django-osoul

<p align="center">
  <em>Pure Django Foundation Layer — models, managers, mixins, utils, comp, contrib, middlewares, filters, forms, backends, adapters, services</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/django-osoul/">
    <img src="https://img.shields.io/pypi/v/django-osoul?style=flat-square&logo=pypi&logoColor=white&label=PyPI" alt="PyPI version">
  </a>
  <a href="https://python.org">
    <img src="https://img.shields.io/pypi/pyversions/django-osoul?style=flat-square&logo=python&logoColor=white" alt="Python versions">
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

- 🏗️ **Pure Django Foundation** – Zero Wagtail, Celery, or django_rseal dependencies
- 📦 **Reusable Components** – Models, managers, mixins, utilities
- 🔧 **Clean Architecture** – Clear separation of concerns
- 🔒 **Strict Boundaries** – Enforced by import-linter in CI
- 📦 **`uv`‑ready** – Lightning-fast dependency management

---

## 📦 Installation

```bash
# Install with uv (recommended)
uv add django-osoul

# Or with pip
pip install django-osoul
```

Add to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    "django_osoul",
    "django_osoul.comp",
    "django_osoul.contrib",
]
```

---

## 🏁 Quickstart

```python
from django_osoul.models.base import BaseModel, TimeStampedModel
from django_osoul.models.mixins import TimestampedModel, SoftDeleteMixin

class MyModel(TimestampedModel, SoftDeleteMixin, BaseModel):
    name = models.CharField(max_length=255)

    class Meta:
        app_label = "myapp"
```

---

## 📖 Public API Reference

### `RoleHierarchyManager`

**Import:** `from django_osoul.managers import RoleHierarchyManager`

Manages role hierarchy and permission inheritance for Django groups. Subclass and override `ROLE_HIERARCHY` and `ROLE_PERMISSIONS` as class attributes.

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `get_all_permissions_for_role(role)` | `role: str` | `set[str]` | All permissions for the role, including inherited ones. Result is cached per-instance. |
| `get_role_hierarchy(role)` | `role: str` | `list[str]` | Full hierarchy list starting with the role itself. |
| `create_or_update_group(role)` | `role: str` | `tuple[Group, bool]` | Create or update a Django `Group` with the role's permissions. Atomic. |
| `assign_user_to_role(user, role)` | `user, role: str` | `bool` | Assign user to role and all roles in its hierarchy. Clears existing groups. Atomic. |
| `assign_user_to_multiple_roles(user, roles)` | `user, roles: list[str]` | `bool` | Assign user to multiple roles and their hierarchies. Atomic. |
| `get_user_roles(user)` | `user` | `list[str]` | Group names (roles) the user belongs to. |
| `get_user_permissions(user)` | `user` | `set[str]` | All permissions via groups and direct assignment. |
| `has_role(user, role)` | `user, role: str` | `bool` | Whether user belongs to the named group. |
| `has_permission(user, permission)` | `user, permission: str` | `bool` | Whether user has the permission (`"app.codename"` format). Superusers always return `True`. |

```python
from django_osoul.managers import RoleHierarchyManager

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
perms = mgr.get_all_permissions_for_role("admin")
# {"auth.add_user", "auth.change_user", "auth.view_user"}

mgr.assign_user_to_role(request.user, "supervisor")
```

---

### `GroupAccessControl`

**Import:** `from django_osoul.managers import GroupAccessControl`

Static helpers for group-based access control. All methods are `@staticmethod` — no instantiation needed. Superusers always pass all checks.

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `check_group_access(user, required_groups)` | `user, required_groups: list[str]` | `bool` | `True` if user belongs to any of the required groups. |
| `check_role_access(user, required_role)` | `user, required_role: str` | `bool` | `True` if user belongs to the named group. |
| `get_accessible_groups(user)` | `user` | `list[Group]` | All groups the user belongs to (all groups for superusers). |
| `filter_by_group(queryset, user, group_field)` | `queryset, user, group_field: str = "groups"` | `QuerySet` | Filter queryset to rows whose group field overlaps the user's groups. |

```python
from django_osoul.managers import GroupAccessControl

# Check access
if GroupAccessControl.check_group_access(request.user, ["editors", "admins"]):
    ...

# Filter a queryset
qs = GroupAccessControl.filter_by_group(Article.objects.all(), request.user)
```

---

### `ErrorTrackerMiddleware`

**Import:** `from django_osoul.middlewares.error_tracker import ErrorTrackerMiddleware`

Logs every 4xx/5xx response with method, path, status code, user email, user agent, and IP. No website-specific configuration required.

**Setup** — add to `MIDDLEWARE` in settings:

```python
MIDDLEWARE = [
    ...
    "django_osoul.middlewares.error_tracker.ErrorTrackerMiddleware",
]
```

Logs to the `django.request.errors` logger. 5xx responses are logged at `CRITICAL`; 4xx at `ERROR`.

---

### `UniqueFieldValidator`

**Import:** `from django_osoul.filters import UniqueFieldValidator`

Raises `ValidationError` if a value already exists in a queryset. Suitable for use in Django forms and DRF serializers.

| Parameter | Type | Description |
|-----------|------|-------------|
| `queryset_or_model` | `QuerySet` or `Model` class | The queryset or model to check against. |
| `field_name` | `str` | The model field to check for uniqueness. |
| `message` | `str` (optional) | Custom error message. |

```python
from django_osoul.filters import UniqueFieldValidator
from django.contrib.auth import get_user_model

User = get_user_model()

class RegistrationForm(forms.Form):
    username = forms.CharField(
        validators=[UniqueFieldValidator(User, "username")]
    )
```

---

### `SlugFieldValidator`

**Import:** `from django_osoul.filters import SlugFieldValidator`

Validates that a value is a valid slug (`^[a-z0-9]+(?:-[a-z0-9]+)*$`). Optionally also checks uniqueness against a queryset.

| Parameter | Type | Description |
|-----------|------|-------------|
| `queryset` | `QuerySet` (optional) | Queryset to check slug uniqueness against. |
| `message` | `str` (optional) | Custom error message for format failures. |

```python
from django_osoul.filters import SlugFieldValidator

class ArticleForm(forms.Form):
    slug = forms.CharField(
        validators=[SlugFieldValidator(queryset=Article.objects.all())]
    )
```

---

### `RoleContextPayload`

**Import:** `from django_osoul.domain import RoleContextPayload`

Dataclass carrying display context for a user role. Carries only primitive/stdlib types — safe to serialise and pass across process boundaries.

| Field | Type | Description |
|-------|------|-------------|
| `role` | `str` | Machine-readable role identifier (e.g. `"admin"`). |
| `role_display` | `str` | Human-readable role name (e.g. `"Administrator"`). |
| `role_color` | `str` | CSS colour string (e.g. `"#4CAF50"`). |
| `permissions` | `list[str]` | Human-readable permission labels. Defaults to `[]`. |

```python
from django_osoul.domain import RoleContextPayload

payload = RoleContextPayload(
    role="admin",
    role_display="Administrator",
    role_color="#4CAF50",
    permissions=["Full system access", "User management"],
)
```

---

## 🧪 Development Setup (with `uv`)

```bash
uv add "django-osoul[all]" --dev
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
- Architecture inspired by Clean Architecture principles
