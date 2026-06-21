<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/cover.png">
  <img src="assets/cover.png" alt="django-grep Cover" width="100%">
</picture>

# 🐍 django-grep

<p align="center">
  <em>Unified Testing Framework — seeder, test base, fixtures, factories, assertions, pytest plugin, health checks</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/django-grep/">
    <img src="https://img.shields.io/pypi/v/django-grep?style=flat-square&logo=pypi&logoColor=white&label=PyPI" alt="PyPI version">
  </a>
  <a href="https://python.org">
    <img src="https://img.shields.io/pypi/pyversions/django-grep?style=flat-square&logo=python&logoColor=white" alt="Python versions">
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

- 🧪 **Unified Testing** – Consistent testing infrastructure across all projects
- 🔍 **Health Checks** – Production-ready health endpoints for monitoring
- 🏭 **Fixtures & Factories** – Reusable test data generation
- ⚡ **Hypothesis Integration** – Property-based testing helpers (`st_email`, `st_slug`, `st_uuid`)
- 📦 **`uv`‑ready** – Lightning-fast dependency management
- 🔒 **Test-Only** – Strict boundary: never imported in production code

---

## 📦 Installation

```bash
# Install with uv (recommended)
uv add django-grep

# Or with pip
pip install django-grep
```

For optional dependencies:

```bash
uv add "django-grep[selenium]" --dev
uv add "django-grep[playwright]" --dev
uv add "django-grep[cov]" --dev
```

---

## 📖 Public API Reference

### `BaseTestCase`

**Import:** `from django_grep.tests.base import BaseTestCase`

Base test case with common setup for Django projects. Extends `django.test.TestCase`. Provides a pre-created regular user and superuser, plus a helper to log in quickly.

**Class attributes set in `setUpTestData`:**

| Attribute | Value | Description |
|-----------|-------|-------------|
| `user` | `User` | Regular test user (`testuser / testpass123`). |
| `admin_user` | `User` | Superuser (`admin / adminpass123`). |
| `client` | `Client` | Django test client, reset before each test. |

**Methods:**

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `login(user)` | `user = None` | `User` | Log in as `self.user` or a provided user via `force_login`. |
| `login_as_admin()` | — | `User` | Log in as `self.admin_user`. |

```python
from django_grep.tests.base import BaseTestCase

class ArticleTest(BaseTestCase):
    def test_list(self):
        self.login()
        response = self.client.get("/articles/")
        self.assertEqual(response.status_code, 200)

    def test_admin_only(self):
        self.login_as_admin()
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 200)
```

---

### `BaseAPITestCase`

**Import:** `from django_grep.tests.base import BaseAPITestCase`

Extends `BaseTestCase` with convenience methods for JSON API views.

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `get_json(url, **kwargs)` | `url: str` | `Response` | GET with `Content-Type: application/json`. |
| `post_json(url, data, **kwargs)` | `url: str, data: dict` | `Response` | POST with JSON-encoded body. |
| `put_json(url, data, **kwargs)` | `url: str, data: dict` | `Response` | PUT with JSON-encoded body. |
| `patch_json(url, data, **kwargs)` | `url: str, data: dict` | `Response` | PATCH with JSON-encoded body. |
| `delete_json(url, **kwargs)` | `url: str` | `Response` | DELETE with `Content-Type: application/json`. |
| `assertJSONSuccess(response)` | `response` | `dict` | Assert HTTP 200 + `{"status": "success"}`. Returns parsed JSON. |
| `assertJSONError(response, status_code)` | `response, status_code: int = 400` | `dict` | Assert error status code + `{"status": "error"}`. Returns parsed JSON. |

```python
from django_grep.tests.base import BaseAPITestCase

class ItemAPITest(BaseAPITestCase):
    def test_create(self):
        self.login()
        response = self.post_json("/api/items/", {"name": "Widget"})
        data = self.assertJSONSuccess(response)
        self.assertIn("id", data)
```

---

### Hypothesis Strategy Helpers

**Import:** `from django_grep.tests.base import st_email, st_slug, st_uuid`

Thin wrappers around `hypothesis.strategies` so website tests never import `hypothesis` directly. Requires `hypothesis` to be installed.

| Function | Returns | Description |
|----------|---------|-------------|
| `st_email()` | `SearchStrategy[str]` | Valid email addresses via `hypothesis.strategies.emails()`. |
| `st_slug()` | `SearchStrategy[str]` | Valid Django slug strings (`^[a-z0-9]+(?:-[a-z0-9]+)*$`). |
| `st_uuid()` | `SearchStrategy[str]` | UUID4 strings. |

```python
from django_grep.tests.base import BaseTestCase, st_email, st_slug, st_uuid
from hypothesis import given, settings

class MyModelPropertyTest(BaseTestCase):
    @given(email=st_email())
    @settings(max_examples=100)
    def test_email_field_accepts_valid_emails(self, email):
        """Property: valid emails are always accepted."""
        user = User(email=email)
        # Should not raise
        self.assertIsNotNone(user.email)

    @given(slug=st_slug())
    @settings(max_examples=100)
    def test_slug_field_accepts_valid_slugs(self, slug):
        """Property: valid slugs are always accepted."""
        article = Article(slug=slug)
        self.assertRegex(article.slug, r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

    @given(uid=st_uuid())
    @settings(max_examples=50)
    def test_uuid_lookup(self, uid):
        """Property: UUID lookups never raise on valid UUIDs."""
        result = MyModel.objects.filter(external_id=uid).first()
        # Should return None, not raise
        self.assertIsNone(result)
```

---

### pytest Plugin

**Activation** — add to `conftest.py` at the repo root:

```python
pytest_plugins = ["django_grep.tests.pytest_plugin"]
```

Or in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
plugins = ["django_grep.tests.pytest_plugin"]
```

The plugin registers shared fixtures so both websites can use them without duplicating fixture definitions.

---

## 🧪 Development Setup (with `uv`)

```bash
uv add "django-grep[selenium,playwright,cov]" --dev
uv run pytest
uv run ruff check .
uv run ruff format .
```

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/amazing-feature`).
3. Commit your changes (`git commit -m 'Add some amazing feature'`).
4. Push to the branch (`git push origin feature/amazing-feature`).
5. Open a Pull Request.

---

## 📄 License

This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.

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

> 🤖 **Kiro** — the AI-powered development environment that kept the workflow smooth and the context sharp.
> 🧠 **Claude** — Anthropic's AI assistant that helped reason through architecture, write docs, and debug with clarity.
> ☁️ **AWS** — the cloud backbone powering the infrastructure this package runs on.
> 🌐 **Hostinger** — reliable and affordable hosting that keeps everything running fast and online.

---

## 🙌 Acknowledgements

- Built with ❤️ and [`uv`](https://docs.astral.sh/uv/)
- Badges from [Shields.io](https://shields.io)
- Testing powered by [Hypothesis](https://hypothesis.works/)

---

## ☕ Support

If you find this project helpful, consider buying me a coffee!

<a href="https://buymeacoffee.com/mammhoud" target="_blank">
  <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" height="50">
</a>
