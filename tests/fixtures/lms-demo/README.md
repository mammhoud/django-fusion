# Unified Product Test Fixtures

These fixtures live alongside the application, in the shared `tests/fixtures/`
tree — byte-identical in the root checkout and in the `structa.cloud` submodule.
This directory exists as a pointer/reference for the shared `tests/fixtures/INDEX.md`.

---

## Fixture Location

```
projects/Clients/structa.cloud/tests/fixtures/
├── auth/
│   ├── group_dummy.json    — Test groups (Students, Instructors, Admins, etc.)
│   └── user_dummy.json     — Test users (testuser, admin, instructor_demo)
└── sites/
    └── site_dummy.json     — Django sites framework entry (dummy host: localhost)
```

---

## Loading the Unified Product Fixtures

```bash
# Load auth fixtures
python manage.py --site=structa.cloud loaddata projects/Clients/structa.cloud/tests/fixtures/auth/user_dummy.json

# Load sites fixture
python manage.py --site=structa.cloud loaddata projects/Clients/structa.cloud/tests/fixtures/sites/site_dummy.json
```

Or use the workspace CLI:

```bash
node assets/scripts/workspace.mjs load-dumps --site structa
```

---

## In Tests

```python
from django_fusion.tests.base import BaseTestCase

class UnifiedProductTest(BaseTestCase):
    fixtures = [
        'projects/Clients/structa.cloud/tests/fixtures/auth/user_dummy.json',
        'projects/Clients/structa.cloud/tests/fixtures/sites/site_dummy.json',
        'tests/fixtures/lms/courses.json',
    ]

    def test_course_catalog(self):
        response = self.client.get('/lms/courses/')
        self.assertEqual(response.status_code, 200)
```

---

## Why Minimal Fixtures?

The unified product is a demo environment that intentionally seeds data programmatically
rather than from static JSON fixtures. The `populate` workspace command runs
scripts that create fresh, realistic demo content on each deploy:

```bash
node assets/scripts/workspace.mjs populate --site structa
```

This ensures the demo always shows current-looking data without stale fixture files.

For LMS course data in tests, use the shared fixtures in `tests/fixtures/lms/`:
- `tests/fixtures/lms/courses.json`
- `tests/fixtures/lms/course_tags.json`
- `tests/fixtures/lms/specializations.json`

---

## Notes

- The unified product and the medical research site (ctc-research) share the same application code (symlinked plugins/components).
- The `site_dummy.json` is a dummy: its host is `localhost`, so it can never collide with a deployed host or send mail to a real domain.
- Dispatcher: `WEBSITE=structa.cloud` selects the `backend` service (health port 8074); see `projects/Makefile`.
