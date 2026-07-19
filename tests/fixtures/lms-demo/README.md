# lms Test Fixtures

lms fixtures live alongside the application at `lms/assets/fixtures/`, not here.
This directory exists as a pointer/reference for the shared `tests/fixtures/INDEX.md`.

---

## Fixture Location

```
lms/assets/fixtures/
├── auth/
│   ├── group_dummy.json    — Test groups (Students, Instructors, Admins, etc.)
│   └── user_dummy.json     — Test users (testuser, admin, instructor_demo)
└── sites/
    └── site_dummy.json     — Django sites framework entry (structa.cloud)
```

---

## Loading lms Fixtures

```bash
# Load auth fixtures
python manage.py --site=lms loaddata lms/assets/fixtures/auth/user_dummy.json

# Load sites fixture
python manage.py --site=lms loaddata lms/assets/fixtures/sites/site_dummy.json
```

Or use the workspace CLI:

```bash
node assets/scripts/workspace.mjs load-dumps --site structa
```

---

## In Tests

```python
from django_fusion.tests.base import BaseTestCase

class LMSDemoTest(BaseTestCase):
    fixtures = [
        'lms/assets/fixtures/auth/user_dummy.json',
        'lms/assets/fixtures/sites/site_dummy.json',
        'tests/fixtures/lms/courses.json',
    ]

    def test_course_catalog(self):
        response = self.client.get('/lms/courses/')
        self.assertEqual(response.status_code, 200)
```

---

## Why Minimal Fixtures?

lms is a demo environment that intentionally seeds data programmatically
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

- lms shares the same application code as ctc-research (symlinked plugins/components).
- The `site_dummy.json` sets the domain to `structa.cloud` (port 5071 in dev).
- Database: `db_structa` (production) / `lms_demo` (dev warehouses).
