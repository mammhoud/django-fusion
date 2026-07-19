# Test Fixtures Index

Complete reference for all test fixtures across the workspace.

---

## Overview

Fixtures are JSON files used to populate databases for testing and development.
Each site maintains its own fixtures alongside its application code, with copies
of LMS-specific fixtures also available in this shared `tests/fixtures/` directory.

---

## How to Load Fixtures

### Django management command
```bash
# Load a single fixture
python manage.py --site=ctc-research loaddata ctc-research/assets/fixtures/auth/user_dummy.json

# Load from tests/fixtures
python manage.py --site=ctc-research loaddata tests/fixtures/lms/courses.json
```

### Using the workspace CLI
```bash
# Load dumped data for a site
npm --prefix assets run load-dumps -- --site ctc
npm --prefix assets run load-dumps -- --site all

# Or via workspace.mjs directly
node assets/scripts/workspace.mjs load-dumps --site ctc-research
```

### Via Make
```bash
make load-dumps-site WEBSITE=ctc
make populate-data-all
```

### Shell loop (all fixtures in a directory)
```bash
for fixture in ctc-research/assets/fixtures/**/*.json; do
  python manage.py --site=ctc-research loaddata "$fixture"
done
```

---

## Fixtures by Site

### ctc-research (LMS)

**Location:** `ctc-research/assets/fixtures/`

| Directory | Files | Purpose |
|-----------|-------|---------|
| `auth/` | `group_dummy.json`, `user_dummy.json` | Test users and groups |
| `sites/` | `site_dummy.json` | Django sites framework config |
| `production/` | `cleaned-dump-data.json`, `just-locales.json` | Production seed data |
| `test/` | `core-data.json`, `initial_choices.json`, `locales.json`, `pages.json`, `users.json` | Test environment data |
| `by-model/auth/` | `auth-group.json`, `auth-permission.json`, `auth-user.json` | Auth model exports |
| `by-model/wagtailprojects/` | Page tree, site, workflow, collection fixtures | Wagtail CMS structure |
| `by-model/wagtailimages/` | `wagtailimages-image.json`, `wagtailimages-rendition.json` | Image library |
| `by-model/handlers/` | `handlers-organization.json` | Organization data |
| `by-model/modules/` | Activity types, status choices, derived status | LMS module config |
| `cleaned/` | `essential-data.json`, `filtered-dump-data.json` | Cleaned production snapshots |
| `original/` | `ctc-research-data.json`, `wagtail_pages_dump.json` | Raw database dumps |

Recommended load order for a fresh test database:
```bash
python manage.py --site=ctc-research loaddata ctc-research/assets/fixtures/auth/user_dummy.json
python manage.py --site=ctc-research loaddata ctc-research/assets/fixtures/sites/site_dummy.json
python manage.py --site=ctc-research loaddata ctc-research/assets/fixtures/test/locales.json
python manage.py --site=ctc-research loaddata ctc-research/assets/fixtures/test/core-data.json
python manage.py --site=ctc-research loaddata tests/fixtures/lms/courses.json
```

---

### lms (LMS Demo)

**Location:** `lms/assets/fixtures/`

Minimal fixtures — the demo environment seeds data programmatically via `populate`.

| Directory | Files | Purpose |
|-----------|-------|---------|
| `auth/` | `group_dummy.json`, `user_dummy.json` | Test users and groups |
| `sites/` | `site_dummy.json` | Django sites framework config |

See `tests/fixtures/lms/README.md` for details.

---

### VResume (Portfolio)

**Location:** `VResume/assets/fixtures/`

| Directory | Files | Purpose |
|-----------|-------|---------|
| `auth/` | `group_dummy.json`, `user_dummy.json` | Test users and groups |
| `sites/` | `site_dummy.json` | Django sites framework config |

See `tests/fixtures/vresume/README.md` for details.

---

## Shared LMS Fixtures

`tests/fixtures/lms/` contains copies of ctc-research LMS fixtures for use in
cross-site integration tests and the shared test suite.

| File | Records | Description |
|------|---------|-------------|
| `courses.json` | 8 courses | Complete course data with descriptions and metadata |
| `course_tags.json` | Multiple | Tag taxonomy for course categorization |
| `specializations.json` | Multiple | Course specialization groupings |

Load in tests:
```python
from django.test import TestCase

class CourseTest(TestCase):
    fixtures = ['tests/fixtures/lms/courses.json']
```

---

## Creating New Fixtures

Export from a running Django site:
```bash
# Export a specific model
python manage.py --site=ctc-research dumpdata lms.Course --indent 2 > tests/fixtures/lms/courses.json

# Export auth data
python manage.py --site=ctc-research dumpdata auth.User auth.Group --indent 2 \
    > ctc-research/assets/fixtures/auth/user_dummy.json

# Export full database (large — use for production snapshots)
python manage.py --site=ctc-research dumpdata --indent 2 --natural-foreign --natural-primary \
    > ctc-research/assets/fixtures/dump-data.json
```

---

## Using Fixtures in Tests (django-fusion)

With `django-fusion`'s `BaseTestCase`, fixtures load automatically via the standard Django mechanism:

```python
from django_fusion.tests.base import BaseTestCase

class CourseListTest(BaseTestCase):
    fixtures = [
        'ctc-research/assets/fixtures/auth/user_dummy.json',
        'tests/fixtures/lms/courses.json',
    ]

    def test_courses_listed(self):
        self.login()
        response = self.client.get('/lms/courses/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Python')
```
