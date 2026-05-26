# Design: Comprehensive Testing and Deployment

## Overview

This spec defines the testing and deployment strategy for all packages and websites in the workspace. It consolidates all test missions from previous conversations and ensures NO test prompts are ignored.

## Architecture

### Test Categories

1. **Unit Tests** - Fast, isolated tests for individual components
   - Location: `tests/unit/`, `libs/*/tests/`
   - Run with: `pytest --ds=<settings>`

2. **Integration Tests** - Cross-component tests
   - Location: `tests/integration/`, `libs/*/tests/integration/`
   - Run with: `pytest --ds=<settings> --live-server`

3. **Property-Based Tests** - Hypothesis-based correctness tests
   - Location: `libs/*/tests/*_properties.py`
   - Run with: `pytest --hypothesis-seed=0`

4. **Selenium Tests** - End-to-end browser tests
   - Location: `tests/selenium/`, `tests/selenium-detailed/`
   - Run with: `pytest --driver=chrome`

5. **Docker Tests** - Container build and startup tests
   - Location: `tests/docker/`
   - Run with: `docker-compose up && pytest`

6. **CI/CD Tests** - Pipeline validation
   - Location: `.github/workflows/`
   - Run with: `act` or manual trigger

### Test Execution Order

```
1. Unit Tests (fastest, most isolated)
   ↓
2. Property-Based Tests (verify correctness properties)
   ↓
3. Integration Tests (cross-component)
   ↓
4. Docker Container Tests (infrastructure)
   ↓
5. CI/CD Pipeline Tests (automation)
   ↓
6. Selenium Tests (slowest, end-to-end)
   ↓
7. Deployment
```

## Components

### Test Infrastructure

- **pytest** - Test runner
- **hypothesis** - Property-based testing
- **selenium** - Browser automation
- **docker** - Container testing
- **pytest-django** - Django test support
- **pytest-cov** - Coverage reporting

### Test Configuration

- `conftest.py` - Shared fixtures
- `settings.py` - Test Django settings per package
- `pytest.ini` - Pytest configuration per package

## Dependencies

- All packages must have passing unit tests before integration tests
- All tests must pass before deployment
- Property tests validate correctness invariants

## Acceptance Criteria

- All unit tests pass (100%)
- All integration tests pass (100%)
- All property-based tests pass (100%)
- All Selenium tests pass (100%)
- All Docker container tests pass (100%)
- All CI/CD pipeline tests pass (100%)
- Both websites deployed successfully
- Post-deployment health checks pass
