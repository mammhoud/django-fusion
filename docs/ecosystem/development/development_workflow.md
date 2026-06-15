# Development Workflow

Comprehensive guide to the development workflow, branching strategy, and collaboration practices for the CTC Research and Structa Cloud ecosystem.

## 🎯 Workflow Overview

Our development workflow emphasizes code quality, collaboration, and continuous integration. We follow GitFlow principles with modern adaptations for rapid development and deployment.

### Core Principles
- **Quality First**: All code must pass tests and code review
- **Collaboration**: Transparent communication and knowledge sharing
- **Automation**: Automated testing, formatting, and deployment
- **Documentation**: Code and processes must be well-documented
- **Security**: Security considerations in every development phase

## 🌳 Branching Strategy

### Branch Types

#### Main Branches
```bash
main                    # Production-ready code
develop                 # Integration branch for features
```

#### Supporting Branches
```bash
feature/feature-name    # New features
bugfix/bug-description  # Bug fixes
hotfix/critical-fix     # Critical production fixes
release/version-number  # Release preparation
```

### Branch Naming Conventions
```bash
# Feature branches
feature/user-authentication
feature/blog-tagging-system
feature/api-rate-limiting

# Bug fix branches
bugfix/login-redirect-issue
bugfix/database-connection-timeout
bugfix/css-responsive-layout

# Hotfix branches
hotfix/security-vulnerability-fix
hotfix/critical-data-loss-prevention

# Release branches
release/v2.1.0
release/v2.1.1-hotfix
```

## 🔄 Development Process

### 1. Feature Development Workflow

#### Starting a New Feature
```bash
# 1. Sync with latest develop
git checkout develop
git pull origin develop

# 2. Create feature branch
git checkout -b feature/new-awesome-feature

# 3. Set up development environment
source .venv/bin/activate
pip install -r requirements/development.txt
python manage.py migrate
```

#### Development Cycle
```bash
# 1. Write failing tests first (TDD)
pytest tests/unit/test_new_feature.py -v

# 2. Implement feature
# Edit code files...

# 3. Run tests and ensure they pass
pytest tests/unit/test_new_feature.py -v
pytest tests/integration/ -v

# 4. Format and lint code
black .
isort .
flake8 .
mypy .

# 5. Commit changes
git add .
git commit -m "feat: implement new awesome feature

- Add user authentication system
- Implement JWT token handling
- Add comprehensive test coverage
- Update API documentation

Closes #123"
```

#### Code Quality Checks
```bash
# Run all quality checks
make quality-check

# Or run individually
black --check .                    # Code formatting
isort --check-only .               # Import sorting
flake8 .                          # Linting
mypy .                            # Type checking
bandit -r .                       # Security scanning
pytest tests/ --cov=. --cov-report=html  # Test coverage
```

### 2. Code Review Process

#### Creating Pull Requests
```bash
# 1. Push feature branch
git push origin feature/new-awesome-feature

# 2. Create pull request with template
# Use GitHub/GitLab PR template
# Include:
# - Clear description of changes
# - Link to related issues
# - Screenshots for UI changes
# - Testing instructions
# - Breaking changes (if any)
```

#### Pull Request Template
```markdown
## Description
Brief description of the changes and their purpose.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Related Issues
Closes #123
Related to #456

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Browser testing (if UI changes)

## Screenshots (if applicable)
Before: [screenshot]
After: [screenshot]

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Code is commented where necessary
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] No breaking changes (or documented)
```

#### Review Guidelines
```bash
# Reviewers should check:
# 1. Code quality and style
# 2. Test coverage and quality
# 3. Documentation updates
# 4. Security considerations
# 5. Performance implications
# 6. Breaking changes

# Review commands
git checkout feature/new-awesome-feature
pytest tests/
black --check .
flake8 .
```

### 3. Integration and Deployment

#### Merging to Develop
```bash
# 1. Ensure feature branch is up to date
git checkout feature/new-awesome-feature
git rebase develop

# 2. Merge via pull request (squash merge preferred)
# GitHub/GitLab handles the merge

# 3. Clean up feature branch
git branch -d feature/new-awesome-feature
git push origin --delete feature/new-awesome-feature
```

#### Release Process
```bash
# 1. Create release branch from develop
git checkout develop
git pull origin develop
git checkout -b release/v2.1.0

# 2. Update version numbers
# Update version in __init__.py, package.json, etc.

# 3. Run full test suite
pytest tests/
npm test

# 4. Update changelog
# Add release notes to CHANGELOG.md

# 5. Create release PR to main
# Merge release branch to main

# 6. Tag release
git checkout main
git pull origin main
git tag -a v2.1.0 -m "Release version 2.1.0"
git push origin v2.1.0

# 7. Merge back to develop
git checkout develop
git merge main
git push origin develop
```

## 🧪 Testing Strategy

### Test Types and Coverage

#### Unit Tests (70% of test suite)
```python
# tests/unit/test_user_model.py
import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

class TestUserModel:
    """Test user model functionality."""

    @pytest.mark.django_db
    def test_create_user_with_email(self):
        """Test creating user with email."""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        assert user.email == 'test@example.com'
        assert user.check_password('testpass123')
        assert user.is_active
        assert not user.is_staff

    @pytest.mark.django_db
    def test_create_superuser(self):
        """Test creating superuser."""
        user = User.objects.create_superuser(
            email='vresume@structa.cloud',
            password='adminpass123'
        )
        assert user.is_staff
        assert user.is_superuser

    def test_email_validation(self):
        """Test email validation."""
        with pytest.raises(ValidationError):
            User(email='invalid-email').full_clean()
```

#### Integration Tests (20% of test suite)
```python
# tests/integration/test_user_registration.py
import pytest
from django.test import Client
from django.urls import reverse

class TestUserRegistration:
    """Test user registration flow."""

    @pytest.mark.django_db
    def test_user_registration_flow(self):
        """Test complete user registration."""
        client = Client()

        # 1. Get registration page
        response = client.get(reverse('account_signup'))
        assert response.status_code == 200

        # 2. Submit registration form
        response = client.post(reverse('account_signup'), {
            'email': 'newuser@example.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
        })
        assert response.status_code == 302

        # 3. Verify user created
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.get(email='newuser@example.com')
        assert user.is_active
```

#### End-to-End Tests (10% of test suite)
```python
# tests/selenium/test_user_journey.py
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestUserJourney:
    """Test complete user journeys."""

    @pytest.mark.selenium
    def test_user_registration_and_login(self, selenium_driver, live_server):
        """Test user can register and login."""
        driver = selenium_driver

        # 1. Navigate to registration
        driver.get(f"{live_server.url}/accounts/signup/")

        # 2. Fill registration form
        driver.find_element(By.NAME, "email").send_keys("test@example.com")
        driver.find_element(By.NAME, "password1").send_keys("testpass123")
        driver.find_element(By.NAME, "password2").send_keys("testpass123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # 3. Verify redirect to dashboard
        WebDriverWait(driver, 10).until(
            EC.url_contains("/dashboard/")
        )
        assert "/dashboard/" in driver.current_url
```

### Test Execution

#### Local Testing
```bash
# Run all tests
pytest

# Run specific test types
pytest tests/unit/
pytest tests/integration/
pytest tests/selenium/

# Run with coverage
pytest --cov=. --cov-report=html --cov-report=term

# Run performance tests
pytest tests/performance/ --benchmark-only

# Run security tests
bandit -r .
safety check
```

#### Continuous Integration
```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip uv
        uv pip install -r requirements/test.txt

    - name: Run tests
      run: |
        pytest tests/ --cov=. --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

## 🔧 Development Tools

### Code Quality Tools

#### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]

  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: ['-r', '.']
```

#### IDE Configuration

##### VS Code Settings
```json
{
  "python.defaultInterpreterPath": "./.venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.mypyEnabled": true,
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests/"],
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}
```

##### PyCharm Configuration
```python
# Code style: Black
# Import optimization: isort
# Type checking: mypy
# Test runner: pytest
# Django support: enabled
```

### Development Scripts

#### Makefile Commands
```makefile
# Makefile
.PHONY: install test lint format clean

install:
	python -m pip install --upgrade pip uv
	uv pip install -r requirements/development.txt
	pre-commit install

test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=. --cov-report=html --cov-report=term

lint:
	flake8 .
	mypy .
	bandit -r .

format:
	black .
	isort .

quality-check: format lint test

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .coverage htmlcov/ .pytest_cache/

dev-server:
	python manage.py runserver 8000

migrate:
	python manage.py migrate

collectstatic:
	python manage.py collectstatic --noinput

shell:
	python manage.py shell_plus

docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f
```

## 📊 Performance Monitoring

### Development Performance

#### Database Query Optimization
```python
# Use Django Debug Toolbar in development
INSTALLED_APPS = [
    # ...
    'debug_toolbar',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    # ...
]

# Monitor slow queries
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

#### Performance Testing
```python
# tests/performance/test_api_performance.py
import pytest
from django.test import Client
from django.urls import reverse

class TestAPIPerformance:
    """Test API endpoint performance."""

    @pytest.mark.benchmark
    def test_user_list_performance(self, benchmark):
        """Test user list API performance."""
        client = Client()

        def api_call():
            return client.get(reverse('api:user-list'))

        result = benchmark(api_call)
        assert result.status_code == 200
        # Benchmark automatically measures execution time
```

### Code Quality Metrics

#### Coverage Requirements
```ini
# .coveragerc
[run]
source = .
omit =
    */migrations/*
    */venv/*
    */tests/*
    manage.py
    */settings/*
    */wsgi.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError

fail_under = 85
```

## 🚨 Troubleshooting

### Common Development Issues

#### Environment Issues
```bash
# Python version mismatch
pyenv install 3.11.7
pyenv local 3.11.7

# Virtual environment corruption
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -r requirements/development.txt

# Database connection issues
docker compose down
docker compose up -d postgres
python manage.py migrate
```

#### Test Issues
```bash
# Test database issues
pytest --create-db

# Selenium issues
# Install browser drivers
pip install webdriver-manager

# Coverage issues
pytest --cov=. --cov-report=html --cov-fail-under=85
```

#### Code Quality Issues
```bash
# Import sorting conflicts
isort --diff .
isort .

# Type checking errors
mypy --install-types
mypy .

# Security issues
bandit -r . -f json -o security-report.json
```

## 📚 Best Practices

### Code Organization
- **Single Responsibility**: Each function/class has one clear purpose
- **DRY Principle**: Avoid code duplication
- **Meaningful Names**: Use descriptive variable and function names
- **Small Functions**: Keep functions focused and concise
- **Documentation**: Document complex logic and APIs

### Git Best Practices
- **Atomic Commits**: Each commit represents a single logical change
- **Clear Messages**: Use conventional commit format
- **Regular Pushes**: Push changes frequently to avoid conflicts
- **Branch Hygiene**: Delete merged branches promptly
- **Rebase vs Merge**: Use rebase for feature branches, merge for releases

### Testing Best Practices
- **Test First**: Write tests before implementation (TDD)
- **Test Coverage**: Maintain >85% test coverage
- **Test Isolation**: Tests should not depend on each other
- **Realistic Data**: Use factories for test data generation
- **Performance Tests**: Include performance benchmarks

---

*This workflow guide ensures consistent, high-quality development practices across the entire team. Regular updates reflect evolving best practices and tooling improvements.*

*Last updated: 2024-12-19 | Version: 2.0.0*
