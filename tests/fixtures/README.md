# Test Fixtures

Test data organized by category for different test scenarios.

## Directory Structure

```
fixtures/
├── README.md                    (this file)
├── lms/                        (LMS data)
│   ├── course_tags.json
│   ├── courses.json
│   └── specializations.json
├── courses/                    (Course-related fixtures)
├── users/                      (User test data)
└── system/                     (System fixtures)
```

## Available Fixtures

### LMS Fixtures (lms/)
- `course_tags.json` - Course tags for categorization
- `courses.json` - Complete course data (8 courses)
- `specializations.json` - Course specializations

### Usage

Load fixtures in tests:
```python
from django.core.management import call_command
call_command('loaddata', 'fixtures/lms/courses.json')
```

Or in Django:
```bash
python manage.py loaddata fixtures/lms/courses.json
```

### Creating Fixtures

Export data:
```bash
python manage.py dumpdata lms.Course > fixtures/lms/courses.json
```

Load all fixtures:
```bash
for fixture in fixtures/**/*.json; do
  python manage.py loaddata "$fixture"
done
```

