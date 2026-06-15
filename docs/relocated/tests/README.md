# Consolidated Testing Suite

This directory contains all tests for both CTC Research and Structa Cloud websites.

## 📁 Directory Structure

```
tests/
├── README.md                    # This file
├── conftest.py                  # Shared pytest configuration
├── integration/                 # Cross-project integration tests
│   ├── test_ctc_research.py    # CTC Research integration tests
│   ├── test_structa_cloud.py   # Structa Cloud integration tests
│   └── test_cross_site.py      # Cross-site integration tests (planned)
├── selenium/                    # Browser automation tests (high-level)
│   ├── test_ctc_selenium.py    # CTC Research Selenium tests
│   ├── test_structa_selenium.py # Structa Cloud Selenium tests (planned)
│   └── test_user_flows.py      # End-to-end user flow tests (planned)
├── selenium-detailed/           # Detailed browser automation tests
│   ├── conftest.py             # Selenium-specific configuration
│   ├── test_admin_flows.py     # Admin interface tests (consolidated)
│   ├── test_user_flows.py      # User interaction flows (consolidated)
│   ├── test_auth_*.py          # Authentication flow tests
│   ├── test_blog_*.py          # Blog functionality tests
│   ├── test_*_pages.py         # Individual page tests
│   └── test_*.py               # Other specific functionality tests
├── email/                       # Email functionality tests
│   ├── test_email_sending.py   # Email sending tests
│   ├── test_email_templates.py # Email template tests (planned)
│   └── test_email_integration.py # Email integration tests (planned)
├── performance/                 # Performance and load tests
│   ├── test_load_testing.py    # Load testing (planned)
│   ├── test_performance.py     # Performance benchmarks (planned)
│   └── test_database_performance.py # Database performance (planned)
├── docker/                     # Docker environment tests (consolidated)
│   ├── test_docker_builds.py   # Docker build and deployment tests
│   ├── test_docker_services.py # Service integration tests (planned)
│   └── test_docker_health.py   # Health check tests (planned)
├── unit/                       # Unit tests for both projects
│   ├── conftest.py             # Unit test configuration
│   ├── test_blog_functionality.py # Blog and tagging functionality (consolidated)
│   ├── test_group_management.py # Group management tests
│   ├── test_property_tests.py  # Property-based tests (consolidated)
│   ├── test_tasks_recovery.py  # Task recovery tests
│   ├── test_tagging_*.py       # Additional tagging tests
│   └── test_ctc_docs_and_core_containers.py # Container property tests
└── scripts/                    # Test utility scripts
    ├── test_production.py      # Production environment testing
    └── test_production_simple.py # Simple production tests
```

## 🚀 Running Tests

### All Tests
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run tests in parallel (if pytest-xdist installed)
pytest tests/ -n auto
```

### Specific Test Categories
```bash
# Integration tests (cross-project)
pytest tests/integration/

# Selenium tests (requires browser setup)
pytest tests/selenium/
pytest tests/selenium-detailed/

# Email tests
pytest tests/email/

# Performance tests
pytest tests/performance/

# Docker tests
pytest tests/docker/

# Unit tests (both projects)
pytest tests/unit/

# Test utility scripts
pytest tests/scripts/
```

### Site-Specific Tests
```bash
# CTC Research tests only
pytest tests/ -k "ctc"

# Structa Cloud tests only
pytest tests/ -k "structa"

# Docker-related tests only
pytest tests/ -k "docker"

# Selenium tests only
pytest tests/ -k "selenium"

# Property-based tests only
pytest tests/ -k "property"
```

## 🔧 Configuration

### Environment Variables
Tests use environment variables to determine which sites to test:
- `TEST_CTC_RESEARCH=true` - Enable CTC Research tests (default: true)
- `TEST_STRUCTA_CLOUD=true` - Enable Structa Cloud tests (default: true)
- `TEST_EMAIL=true` - Enable email tests (default: true)
- `TEST_SELENIUM=false` - Enable Selenium tests (default: false, requires setup)

### Test Databases
- CTC Research: `db_ctc_test`
- Structa Cloud: `db_structa_test`

### Browser Configuration (Selenium)
Selenium tests support multiple browsers:
- Chrome (default, headless)
- Firefox
- Edge

### Docker Test Configuration
Docker tests require:
- Docker and Docker Compose installed
- Sufficient system resources for container builds
- Network access for image downloads

## 📊 Test Reports

Test results and reports are generated in:
- `reports/test-results/` - Test execution reports
- `reports/coverage/` - Code coverage reports
- `reports/performance/` - Performance test results

## 🛠️ Dependencies

Required packages for testing:
```bash
# Core testing
pytest>=7.0.0
pytest-django>=4.5.0
pytest-cov>=4.0.0

# Web testing
requests>=2.28.0
beautifulsoup4>=4.11.0

# Browser testing (optional)
selenium>=4.0.0

# Performance testing (optional)
locust>=2.0.0

# Property-based testing
hypothesis>=6.0.0

# YAML parsing (for Docker compose tests)
PyYAML>=6.0.0
```

## 🔍 Test Organization

### Integration Tests (`tests/integration/`)
- Cross-project functionality
- Service-to-service communication
- End-to-end workflows

### Unit Tests (`tests/unit/`)
- Django model tests
- View function tests
- Utility function tests
- Business logic tests
- Property-based tests

### Selenium Tests (`tests/selenium/`, `tests/selenium-detailed/`)
- Browser automation
- User interface testing
- JavaScript functionality
- Cross-browser compatibility
- Detailed page-specific tests

### Docker Tests (`tests/docker/`)
- Container build verification
- Service deployment testing
- Infrastructure validation
- Performance benchmarking

### Utility Scripts (`tests/scripts/`)
- Environment setup validation
- Production readiness checks
- Comprehensive test suites

## 🚨 Known Issues

1. **Property Tests**: Some property-based tests are skipped pending proper environment setup
2. **Selenium Setup**: Requires browser drivers and may need display configuration for CI/CD
3. **Docker Dependencies**: Some tests require specific Docker network and volume configurations
4. **Cross-Project Tests**: Some tests may need adjustment for different project configurations

## 📝 Contributing

When adding new tests:

1. **Choose the right category**: Unit tests go in `unit/`, integration tests in `integration/`, etc.
2. **Follow naming conventions**: Test files should start with `test_` and contain descriptive names
3. **Add proper documentation**: Include docstrings explaining what each test validates
4. **Consider test isolation**: Tests should not depend on each other or external state
5. **Update this README**: Document any new test categories or requirements
6. **Consolidate when possible**: Prefer consolidated test files over many small ones

## 🎯 Consolidation Benefits

This consolidated structure provides:

- **Reduced Duplication**: Eliminated duplicate test files between projects
- **Better Organization**: Clear separation by test type and scope
- **Improved Maintainability**: Related tests grouped logically
- **Cross-Project Testing**: Shared infrastructure for both CTC Research and Structa Cloud
- **Scalable Structure**: Easy to add new projects or test types

---

**Maintained By**: CTC Research Development Team
