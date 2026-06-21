# django-grep

Unified testing framework — seeder, test base, fixtures, factories, assertions, pytest plugin, health checks.

## Installation

```bash
uv add django-grep --dev
# or
pip install django-grep
```

## Directory Tree

```
django-grep/
├── src/
│   └── django_grep/
│       ├── health/          # Health check endpoints & views
│       ├── management/      # Management commands
│       ├── seeder/          # Django ORM seeder
│       ├── tests/           # Testing infrastructure
│       │   ├── assertions.py
│       │   ├── base.py
│       │   ├── factories.py
│       │   ├── fixtures.py
│       │   ├── mixins.py
│       │   ├── pytest_plugin.py
│       │   └── selenium_base.py
│       ├── __init__.py
│       ├── py.typed
│       └── typing.py
├── tests/
│   ├── selenium/
│   ├── test_nawaai/
│   ├── test_osoul/
│   ├── test_rseal/
│   └── settings.py
├── docs/
├── assets/
│   └── cover.png
├── CHANGELOG.md
├── README.md
└── pyproject.toml
```

## Usage

```python
# Base test case
from django_grep.tests.base import BaseTestCase, BaseAPITestCase

class MyModelTest(BaseTestCase):
    def test_create(self):
        obj = MyModel.objects.create(name="test")
        self.assertIsNotNone(obj.pk)

# Hypothesis property-based testing
from hypothesis import given
class MyPBTTest(BaseTestCase):
    @given(email=BaseTestCase.st_email())
    def test_email_valid(self, email):
        self.assertIn("@", email)

# Seeder
from django_grep.seeder import Seeder
seeder = Seeder()
seeder.add_entity(MyModel, 10)
seeder.execute()

# Health check URLs
# urlpatterns += [path("health/", include("django_grep.health.urls"))]
```

## Related Packages

- [django-osoul](../django-osoul/) — Pure Django foundation
- [django-rseal](../django-rseal/) — Automation layer
- [nawaai](../nawaai/) — AI/MCP toolkit
