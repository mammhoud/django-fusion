# Test Documentation

This directory contains documentation for the test infrastructure across both websites (structa.cloud and ctc-research.com).

## Test Structure

### Test Organization

Tests are organized by project and package:

```
tests/
├── ctc-research.com/
│   ├── tests/
│   │   ├── unit/           # Unit tests
│   │   ├── integration/    # Integration tests
│   │   ├── functional/     # Functional tests
│   │   └── selenium/       # Selenium tests
│   └── ...
├── structa.cloud/
│   ├── tests/
│   │   ├── unit/           # Unit tests
│   │   ├── integration/    # Integration tests
│   │   ├── functional/     # Functional tests
│   │   └── selenium/       # Selenium tests
│   └── ...
└── venv/libs/
    ├── django-fusion/tests/  # django_fusion package tests
    ├── ceptor-ai/tests/ # ceptor_ai package tests
    ├── django-fusion/tests/  # django_fusion package tests
    └── nawaai/tests/       # nawaai package tests
```

### Test Categories

| Category | Description | Location Pattern |
|----------|-------------|------------------|
| **Unit Tests** | Test individual functions/classes in isolation | `tests/unit/` |
| **Integration Tests** | Test interactions between components | `tests/integration/` |
| **Functional Tests** | Test user-facing functionality | `tests/functional/` |
| **Selenium Tests** | Browser automation tests | `tests/selenium/` |
| **Property-Based Tests** | Hypothesis-based property tests | `tests/property/` or `test_*.py` with `@given` |

## Running Tests

### Running Tests for Both Websites

```bash
# Run all tests for both websites
python3 scripts/run_all_tests.py

# Verify test parity between websites
python3 scripts/verify_test_parity.py
```

### Running Tests for Individual Projects

```bash
# Test ctc-research.com
cd ctc-research.com
uv run pytest tests/ -v

# Test structa.cloud
cd structa.cloud
uv run pytest tests/ -v
```

### Running Tests for Packages

```bash
# Test django_fusion
cd venv/libs/django-fusion
uv run pytest tests/ -v

# Test ceptor_ai
cd venv/libs/ceptor-ai
uv run pytest tests/ -v

# Test django_fusion
cd venv/libs/django-fusion
uv run pytest tests/ -v

# Test nawaai
cd venv/libs/nawaai
uv run pytest tests/ -v
```

### Running Specific Test Types

```bash
# Run only unit tests
pytest tests/unit/ -v

# Run only integration tests
pytest tests/integration/ -v

# Run only functional tests
pytest tests/functional/ -v

# Run only selenium tests
pytest tests/selenium/ -v

# Run tests matching a pattern
pytest -k "auth" -v  # Tests with "auth" in name
pytest -k "test_login" -v  # Tests with "test_login" in name
```

## Test Infrastructure

### BaseTestCase

All tests extend `django_fusion.tests.base.BaseTestCase` which provides:

- Hypothesis strategies: `st_email()`, `st_slug()`, `st_uuid()`
- Custom assertions: `assert_redirects_to()`, `assert_json_response()`, `assert_htmx_response()`
- Test fixtures and factories
- Authentication helpers

```python
from django_fusion.tests.base import BaseTestCase, st_email, st_slug
from hypothesis import given, strategies as st

class TestAuthentication(BaseTestCase):
    @given(st_email())
    def test_email_validation(self, email):
        # Test email validation logic
        result = validate_email(email)
        self.assertTrue(result)
```

### Factories

Reusable factory classes in `django_fusion.tests.factories`:

- `UserFactory` - Create test users
- `GroupFactory` - Create test groups
- `PersonFactory` - Create test person records
- `CourseFactory` - Create test courses
- `EnrollmentFactory` - Create test enrollments

```python
from django_fusion.tests.factories import UserFactory, CourseFactory

def test_course_enrollment(self):
    user = UserFactory()
    course = CourseFactory()
    enrollment = EnrollmentFactory(user=user, course=course)
    self.assertEqual(enrollment.user, user)
    self.assertEqual(enrollment.course, course)
```

### Assertions

Custom assertion helpers in `django_fusion.tests.assertions`:

- `assert_redirects_to(response, expected_url)` - Assert redirect to specific URL
- `assert_json_response(response, expected_data)` - Assert JSON response matches expected data
- `assert_htmx_response(response)` - Assert HTMX response headers
- `assert_form_errors(response, field, expected_error)` - Assert form field errors

```python
from django_fusion.tests.assertions import assert_json_response, assert_redirects_to

def test_api_endpoint(self):
    response = self.client.get('/api/users/')
    assert_json_response(response, {'count': 0, 'results': []})

def test_login_redirect(self):
    response = self.client.post('/login/', data={'username': 'test', 'password': 'test'})
    assert_redirects_to(response, '/dashboard/')
```

## Test Parity Verification

### What is Test Parity?

Test parity ensures both websites (structa.cloud and ctc-research.com) have similar test coverage:

- Similar test counts
- Similar test categories
- Similar test types
- All tests passing

### Why Test Parity Matters

1. **Consistency**: Both websites should have comparable test coverage
2. **Maintainability**: Changes to one website should be testable in the other
3. **Quality**: Both websites should meet the same quality standards
4. **Regression Prevention**: Tests catch regressions in both codebases

### Verifying Test Parity

```bash
# Run test parity verification
python3 scripts/verify_test_parity.py

# Output includes:
# - Test count comparison
# - Test category comparison
# - Test type comparison
# - Parity status (pass/fail)
# - Recommendations for improving parity
```

### Test Parity Report

The test parity verification generates `TEST_PARITY_REPORT.json` with:

```json
{
  "parity_status": "pass",
  "test_counts": {
    "ctc-research.com": 150,
    "structa.cloud": 148
  },
  "category_counts": {
    "unit": {"ctc": 50, "structa": 48},
    "integration": {"ctc": 40, "structa": 42},
    "functional": {"ctc": 40, "structa": 38},
    "selenium": {"ctc": 20, "structa": 20}
  },
  "differences": [],
  "recommendations": []
}
```

## Property-Based Testing

### Hypothesis Integration

The project uses Hypothesis for property-based testing:

```python
from hypothesis import given, strategies as st
from django_fusion.tests.base import st_email, st_slug

@given(st_email())
def test_email_property(self, email):
    # Property: All valid emails should pass validation
    result = validate_email(email)
    self.assertTrue(result)

@given(st.text(min_size=1, max_size=100))
def test_slug_property(self, text):
    # Property: slugify should always produce valid slugs
    slug = slugify(text)
    self.assertTrue(is_valid_slug(slug))
```

### Property Test Strategies

| Strategy | Description | Usage |
|----------|-------------|-------|
| `st_email()` | Generate valid email addresses | `@given(st_email())` |
| `st_slug()` | Generate valid slugs | `@given(st_slug())` |
| `st_uuid()` | Generate valid UUIDs | `@given(st_uuid())` |
| `st.text()` | Generate text strings | `@given(st.text(min_size=1))` |
| `st.integers()` | Generate integers | `@given(st.integers(min_value=0))` |
| `st.lists()` | Generate lists | `@given(st.lists(st.text()))` |

### Writing Property Tests

1. **Identify properties**: What should always be true?
2. **Define strategies**: What inputs to generate?
3. **Write test**: Implement property check
4. **Run tests**: Verify properties hold

Example property test:

```python
from hypothesis import given, strategies as st

@given(st.integers(min_value=0), st.integers(min_value=0))
def test_addition_commutative(self, a, b):
    # Property: addition is commutative
    self.assertEqual(a + b, b + a)

@given(st.lists(st.integers()))
def test_sorting_idempotent(self, lst):
    # Property: sorting is idempotent
    sorted_once = sorted(lst)
    sorted_twice = sorted(sorted_once)
    self.assertEqual(sorted_once, sorted_twice)
```

## Test Reports

### Test Execution Report

After running tests, `TEST_REPORT.json` is generated:

```json
{
  "timestamp": "2026-04-17T10:30:00Z",
  "projects": {
    "ctc-research.com": {
      "total": 150,
      "passed": 148,
      "failed": 2,
      "skipped": 0,
      "duration": 45.2
    },
    "structa.cloud": {
      "total": 148,
      "passed": 146,
      "failed": 2,
      "skipped": 0,
      "duration": 42.8
    }
  },
  "packages": {
    "django_fusion": {"total": 50, "passed": 50, "failed": 0},
    "ceptor_ai": {"total": 40, "passed": 40, "failed": 0},
    "django_fusion": {"total": 30, "passed": 30, "failed": 0},
    "nawaai": {"total": 20, "passed": 20, "failed": 0}
  },
  "summary": {
    "total_tests": 388,
    "total_passed": 384,
    "total_failed": 4,
    "success_rate": 98.97
  }
}
```

### Coverage Reports

Coverage reports are generated using pytest-cov:

```bash
# Generate coverage report
pytest --cov=. --cov-report=html --cov-report=term

# Output:
# - HTML coverage report in htmlcov/
# - Terminal coverage summary
# - Coverage data in .coverage
```

## CI/CD Integration

### GitHub Actions Workflows

Tests run automatically in CI:

- `.github/workflows/test.yml` - Runs tests on push/PR
- `.github/workflows/test-parity.yml` - Verifies test parity
- `.github/workflows/coverage.yml` - Generates coverage reports

### CI Test Execution

```yaml
# Example test job
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: python3 scripts/run_all_tests.py
      - run: python3 scripts/verify_test_parity.py
```

## Troubleshooting Tests

### Common Test Issues

1. **Database errors**: Ensure test database is properly configured
2. **Fixture loading errors**: Check fixture file paths and formats
3. **Import errors**: Verify test imports from correct packages
4. **Timeout errors**: Increase test timeout or optimize slow tests

### Debugging Tests

```bash
# Run tests with debug output
pytest -v --tb=short

# Run specific test with pdb
pytest tests/test_auth.py::TestLogin::test_login_success -v --pdb

# Run tests with logging
pytest -v --log-level=DEBUG

# Run tests with coverage debugging
pytest --cov=. --cov-report=term --no-cov-on-fail
```

### Test Maintenance

1. **Regularly run tests**: Ensure tests pass regularly
2. **Update test data**: Keep test data current with schema changes
3. **Review test parity**: Ensure both websites maintain parity
4. **Add new tests**: Add tests for new features
5. **Remove obsolete tests**: Remove tests for removed features

## Related Documentation

- [Scripts Documentation](../scripts/README.md) - Test script usage
- [Development Documentation](../development/README.md) - Test-driven development workflow
- [Architecture Documentation](../architecture/README.md) - Test infrastructure architecture
- [Deployment Documentation](../deployment/README.md) - CI/CD test integration
