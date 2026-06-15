# Testing Strategy

## Overview

This document describes the testing strategy for the Xellent Website platform.

## Testing Pyramid

```
        /\
       /  \
      / E2E \
     /______\
    /        \
   / Integration\
  /____________\
 /              \
/   Unit Tests   \
/________________\
```

## Unit Tests

### Purpose

Test individual functions and methods in isolation.

### Tools

- **pytest**: Testing framework
- **pytest-django**: Django plugin for pytest
- **factory-boy**: Test data generation
- **hypothesis**: Property-based testing

### Example

```python
import pytest
from django.contrib.auth.models import User
from apps.courses.models import Course

@pytest.mark.django_db
class TestCourseModel:
    def test_course_creation(self):
        """Test creating a course"""
        course = Course.objects.create(
            title="Python Basics",
            description="Learn Python",
            instructor=User.objects.create_user("instructor")
        )
        assert course.title == "Python Basics"
        assert course.is_published is False

    def test_course_slug_generation(self):
        """Test slug is generated from title"""
        course = Course.objects.create(
            title="Advanced Python",
            instructor=User.objects.create_user("instructor")
        )
        assert course.slug == "advanced-python"
```

### Running Unit Tests

```bash
# Run all unit tests
pytest tests/unit/

# Run specific test file
pytest tests/unit/test_models.py

# Run specific test class
pytest tests/unit/test_models.py::TestCourseModel

# Run specific test
pytest tests/unit/test_models.py::TestCourseModel::test_course_creation

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov
```

## Integration Tests

### Purpose

Test interactions between components.

### Example

```python
import pytest
from django.test import Client
from django.contrib.auth.models import User
from apps.courses.models import Course

@pytest.mark.django_db
class TestCourseAPI:
    def test_list_courses(self):
        """Test listing courses via API"""
        client = Client()
        user = User.objects.create_user("user", "user@example.com", "password")
        course = Course.objects.create(
            title="Python",
            instructor=user
        )

        response = client.get("/api/courses/")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_create_course(self):
        """Test creating course via API"""
        client = Client()
        user = User.objects.create_user("instructor", "inst@example.com", "password")
        client.login(username="instructor", password="password")

        response = client.post("/api/courses/", {
            "title": "New Course",
            "description": "Description"
        })
        assert response.status_code == 201
        assert Course.objects.count() == 1
```

### Running Integration Tests

```bash
# Run all integration tests
pytest tests/integration/

# Run specific test file
pytest tests/integration/test_api.py

# Run with coverage
pytest --cov tests/integration/
```

## End-to-End Tests

### Purpose

Test complete user workflows.

### Tools

- **Selenium**: Browser automation
- **Playwright**: Modern browser automation
- **pytest**: Test framework

### Example

```python
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By

@pytest.fixture
def browser():
    driver = webdriver.Chrome()
    yield driver
    driver.quit()

def test_user_registration_flow(browser):
    """Test complete user registration flow"""
    # Navigate to registration page
    browser.get("http://localhost:8000/register/")

    # Fill registration form
    browser.find_element(By.NAME, "username").send_keys("newuser")
    browser.find_element(By.NAME, "email").send_keys("user@example.com")
    browser.find_element(By.NAME, "password").send_keys("SecurePassword123")
    browser.find_element(By.NAME, "password_confirm").send_keys("SecurePassword123")

    # Submit form
    browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    # Verify success
    assert "Registration successful" in browser.page_source
```

### Running E2E Tests

```bash
# Run all E2E tests
pytest tests/e2e/

# Run specific test
pytest tests/e2e/test_user_registration.py

# Run with headless browser
pytest tests/e2e/ --headless
```

## Property-Based Testing

### Purpose

Generate test cases automatically to find edge cases.

### Tools

- **hypothesis**: Property-based testing framework

### Example

```python
from hypothesis import given, strategies as st
from apps.courses.models import Course

@given(
    title=st.text(min_size=1, max_size=255),
    description=st.text()
)
def test_course_creation_with_various_inputs(title, description):
    """Test course creation with various inputs"""
    course = Course.objects.create(
        title=title,
        description=description,
        instructor=User.objects.create_user("instructor")
    )
    assert course.title == title
    assert course.description == description
```

## Test Coverage

### Measuring Coverage

```bash
# Generate coverage report
pytest --cov --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Coverage Goals

- **Overall**: 80%+ coverage
- **Critical paths**: 95%+ coverage
- **Utilities**: 90%+ coverage

## Test Organization

### Directory Structure

```
tests/
├── unit/
│   ├── test_models.py
│   ├── test_views.py
│   ├── test_serializers.py
│   └── test_forms.py
├── integration/
│   ├── test_api_endpoints.py
│   ├── test_workflows.py
│   └── test_database.py
├── e2e/
│   ├── test_user_registration.py
│   ├── test_course_enrollment.py
│   └── test_quiz_submission.py
├── fixtures/
│   ├── users.py
│   ├── courses.py
│   └── enrollments.py
└── conftest.py
```

## Test Fixtures

### Using Factory Boy

```python
import factory
from django.contrib.auth.models import User
from apps.courses.models import Course

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.Sequence(lambda n: f"user{n}@example.com")

class CourseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Course

    title = factory.Faker("sentence")
    description = factory.Faker("paragraph")
    instructor = factory.SubFactory(UserFactory)

# Usage in tests
def test_course_with_factory():
    course = CourseFactory()
    assert course.title is not None
```

## Continuous Integration

### GitHub Actions

Tests run automatically on:
- Pull requests
- Commits to main/develop
- Scheduled runs

### Test Requirements

- All tests must pass
- Coverage must not decrease
- No linting errors
- No type checking errors

## Performance Testing

### Load Testing

```bash
# Using locust
locust -f tests/load/locustfile.py

# Using Apache Bench
ab -n 1000 -c 10 http://localhost:8000/
```

### Database Performance

```bash
# Analyze slow queries
# Enable query logging
# Use Django Debug Toolbar
# Profile with django-silk
```

## Test Best Practices

### 1. Test Naming

```python
# Good
def test_user_can_enroll_in_course():
    pass

# Bad
def test_enroll():
    pass
```

### 2. Arrange-Act-Assert

```python
def test_calculate_score():
    # Arrange
    answers = ["A", "B", "C"]
    correct = ["A", "B", "C"]

    # Act
    score = calculate_score(answers, correct)

    # Assert
    assert score == 100
```

### 3. One Assertion Per Test

```python
# Good
def test_user_creation():
    user = User.objects.create_user("john")
    assert user.username == "john"

def test_user_email():
    user = User.objects.create_user("john", "john@example.com")
    assert user.email == "john@example.com"

# Avoid
def test_user_creation():
    user = User.objects.create_user("john", "john@example.com")
    assert user.username == "john"
    assert user.email == "john@example.com"
```

### 4. Use Fixtures

```python
@pytest.fixture
def user():
    return User.objects.create_user("testuser")

def test_user_profile(user):
    assert user.username == "testuser"
```

## Related Documentation

- [Development Workflow](01-development-workflow.md)
- [Code Standards and Conventions](03-code-standards-and-conventions.md)
- [Local Development Setup](../getting-started/02-local-development-setup.md)
