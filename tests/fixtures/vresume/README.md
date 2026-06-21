# VResume Test Fixtures

VResume fixtures live alongside the application at `VResume/assets/fixtures/`, not here.
This directory exists as a pointer/reference for the shared `tests/fixtures/INDEX.md`.

---

## Fixture Location

```
VResume/assets/fixtures/
├── auth/
│   ├── group_dummy.json    — Test groups (Editors, Viewers, etc.)
│   └── user_dummy.json     — Test users (testuser, admin)
└── sites/
    └── site_dummy.json     — Django sites framework entry (vresume.structa.cloud)
```

---

## Loading VResume Fixtures

```bash
# Load auth fixtures
python manage.py --site=vresume loaddata VResume/assets/fixtures/auth/user_dummy.json

# Load sites fixture
python manage.py --site=vresume loaddata VResume/assets/fixtures/sites/site_dummy.json
```

Or use the workspace CLI:

```bash
node assets/scripts/workspace.mjs load-dumps --site vresume
```

---

## In Tests

```python
from django_osoul.tests.base import BaseTestCase

class VResumePageTest(BaseTestCase):
    fixtures = [
        'VResume/assets/fixtures/auth/user_dummy.json',
        'VResume/assets/fixtures/sites/site_dummy.json',
    ]

    def test_homepage_loads(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
```

---

## Populating Test Content

VResume's `VResume/www/tests/data_populator.py` creates sample portfolio content (Wagtail pages,
images, blog posts) using Pillow for image generation. It is a standalone script invoked as:

```bash
python manage.py --site=vresume shell < VResume/www/tests/data_populator.py
```

For full integration with `django-osoul`, consider migrating data_populator to use
`BaseTestCase` fixtures or the `django_osoul.tests.pytest_plugin` so test data is
managed consistently with the rest of the workspace.

---

## Notes

- VResume uses Wagtail CMS, so site fixtures must be loaded before page fixtures.
- The `site_dummy.json` sets the domain to `vresume.structa.cloud` (port 5072 in dev).
- VResume has no LMS fixtures — it is a portfolio site with no course data.
