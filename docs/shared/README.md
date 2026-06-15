# Shared Documentation

> Cross-cutting concerns shared across all projects

## Overview

This section contains documentation for concerns that span multiple projects.

## Sections

### [Styling](styling/)
CSS frameworks, styling conventions, and theme configuration
- [01-css-frameworks.md](styling/01-css-frameworks.md) - Tailwind CSS, CSS Modules
- [02-styling-conventions.md](styling/02-styling-conventions.md) - Best practices
- [03-theme-configuration.md](styling/03-theme-configuration.md) - Design tokens
- [04-responsive-design.md](styling/04-responsive-design.md) - Mobile-first patterns
- [README.md](styling/README.md) - Styling overview

### [Testing](testing/)
Testing guides, test reports, and coverage reports
- [README.md](testing/README.md) - Testing overview
- [test_suite_overview.md](testing/test_suite_overview.md) - Test suite structure
- [production-testing.md](testing/production-testing.md) - Production testing
- [CSV_EMAIL_TESTING.md](testing/CSV_EMAIL_TESTING.md) - Email testing
- [FINAL_VERIFICATION_CHECKLIST.md](testing/FINAL_VERIFICATION_CHECKLIST.md) - Verification checklist

### [Troubleshooting](troubleshooting/)
Common issues, debugging guide, and performance optimization
- [01-common-issues.md](troubleshooting/01-common-issues.md) - Common problems
- [debugging_guide.md](troubleshooting/debugging_guide.md) - Debugging techniques
- [log_analysis.md](troubleshooting/log_analysis.md) - Log analysis
- [performance_optimization.md](troubleshooting/performance_optimization.md) - Performance tuning
- [README.md](troubleshooting/README.md) - Troubleshooting overview

### [Scripts](scripts/)
Utility scripts for validation, testing, and maintenance
- [README.md](scripts/README.md) - Scripts overview
- [run_all_tests.py](scripts/run_all_tests.py) - Run all tests
- [validate_system.py](scripts/validate_system.py) - Validate system
- [validate_migrations.py](scripts/validate_migrations.py) - Validate migrations
- [analyze_duplication.py](scripts/analyze_duplication.py) - Analyze duplication
- [enforce_naming.py](scripts/enforce_naming.py) - Enforce naming conventions

---

## Quick Commands

### Testing
```bash
# Run all tests
python3 shared/scripts/run_all_tests.py

# Run tests for specific project
cd ctc-research.com && uv run pytest tests/ -v
cd structa.cloud && uv run pytest tests/ -v
```

### Validation
```bash
# Run all validation checks
python3 shared/scripts/validate_system.py

# Check architecture boundaries
import-linter --config .importlinter

# Analyze duplication
python3 shared/scripts/analyze_duplication.py --threshold 0.70
```

### Troubleshooting
```bash
# Check Docker logs
docker compose logs -f

# Check health endpoints
curl http://localhost:8080/health/
```

---

## Related Documentation

- [Ecosystem Overview](../ecosystem/)
- [Packages](../packages/)
- [Infrastructure](../infrastructure/)
