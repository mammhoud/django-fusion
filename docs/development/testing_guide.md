# VResume Testing Suite - Complete Guide

## Overview

The VResume testing suite provides comprehensive testing for all pages and endpoints. It includes:

- **Automated test runner** with detailed reporting
- **Test data population** for consistent testing
- **HTTP request definitions** for manual testing
- **Performance metrics** and analysis
- **Makefile integration** for easy execution

## Directory Structure

```
v1/
├── tests/                   # Testing suite directory
│   ├── __init__.py         # Package initialization
│   ├── runner.py           # Main test execution engine
│   ├── data_populator.py   # Test data generation
│   ├── requests.http       # HTTP request definitions
│   ├── README.md           # Quick reference
│   └── GUIDE.md            # This file
├── test_reports/           # Generated test reports (auto-created)
├── makefile                # Updated with test commands
└── populate_data.py        # Original data population script
```

## Getting Started

### 1. Initial Setup

```bash
cd v1

# Full setup including test data
make setup

# Or just populate test data
make populate-data
```

### 2. Run Tests

```bash
# Run all tests with verbose output
make test

# Run tests quickly (no verbose output)
make test-quick

# Run tests against custom URL
make test-url URL=http://your-server:8000
```

### 3. View Results

```bash
# Show latest test reports
make test-reports

# View specific report
cat test_reports/test_report_20240509_103045.json
```

## Test Commands

### Makefile Commands

```bash
# Testing
make test              # Run comprehensive tests (verbose)
make test-quick        # Run tests (quiet)
make test-url          # Run tests against custom URL
make populate-data     # Populate test data
make populate-data-clear  # Clear test data
make test-reports      # Show latest test reports
make clean-test-reports # Clean all test reports

# Shortcuts
make t                 # Alias for test
make tq                # Alias for test-quick
make pd                # Alias for populate-data
make pdc               # Alias for populate-data-clear
```

### Python Commands

```bash
# Run tests
python -m tests.runner

# Run tests with options
python -m tests.runner --base-url http://custom-url:8000
python -m tests.runner --verbose
python -m tests.runner --output json

# Populate test data
python -m tests.data_populator

# Clear test data
python -m tests.data_populator --clear
python -m tests.data_populator --verbose
```

## Test Coverage

### Pages Tested

1. **Home Page** (`/pages/home/`)
   - Full page load
   - HTMX fragment

2. **About Page** (`/pages/about/`)
   - Full page load
   - HTMX fragment

3. **Resume Page** (`/pages/resume/`)
   - Full page load
   - HTMX fragment

4. **Portfolio Page** (`/pages/portfolio/`)
   - Full page load
   - HTMX fragment

5. **Blog Page** (`/pages/blog/`)
   - Full page load
   - HTMX fragment

6. **Contact Page** (`/pages/contact/`)
   - Full page load
   - HTMX fragment

### Endpoints Tested

1. **Modal Endpoints**
   - Project detail: `GET /pages/project/<project_id>/`
   - Blog detail: `GET /pages/blog/<blog_id>/`

2. **Form Endpoints**
   - Contact submit: `POST /pages/contact/submit/`
   - Newsletter subscribe: `POST /pages/subscribe/`

3. **Error Cases**
   - Invalid tab (404)
   - Invalid project ID (404)
   - Invalid blog ID (404)

### Form Validation Tests

1. **Contact Form**
   - Valid submission
   - Missing name
   - Missing email
   - Missing message

2. **Newsletter Subscription**
   - Valid email
   - Duplicate email
   - Empty email

## Test Data

### What Gets Populated

```
Services:
  - Web Development
  - UI/UX Design
  - Mobile Development
  - Cloud Solutions

Skills:
  - Python (95%)
  - JavaScript (90%)
  - React (88%)
  - Django (92%)
  - PostgreSQL (85%)
  - Docker (80%)
  - AWS (78%)
  - Git (95%)

Subscribers:
  - subscriber1@example.com
  - subscriber2@example.com
  - subscriber3@example.com

Blog Categories:
  - Technology
  - Design
  - Business
  - Tutorial
  - News

Blog Tags:
  - python
  - javascript
  - web-development
  - design
  - tutorial
  - tips
  - best-practices
```

## Test Reports

### Report Location

Test reports are automatically generated in `test_reports/` directory with timestamps:

```
test_reports/
├── test_report_20240509_103045.json
├── test_report_20240509_110230.json
└── test_report_20240509_115612.json
```

### Report Structure

```json
{
  "timestamp": "2024-05-09T10:30:45.123456",
  "base_url": "http://localhost:8000",
  "summary": {
    "total": 30,
    "passed": 28,
    "failed": 2,
    "errors": 0,
    "skipped": 0
  },
  "performance": {
    "total_time": 5.234,
    "avg_time": 0.174,
    "min_time": 0.045,
    "max_time": 0.523
  },
  "tests": [
    {
      "name": "Tab: home (Full Page)",
      "method": "GET",
      "url": "http://localhost:8000/pages/home/",
      "status_code": 200,
      "elapsed_time": 0.145,
      "content_length": 5234,
      "passed": true,
      "response_type": "text/html; charset=utf-8"
    },
    ...
  ]
}
```

## Performance Metrics

The test runner tracks:

- **Total Time**: Combined time for all tests
- **Average Time**: Mean response time per request
- **Min Time**: Fastest response
- **Max Time**: Slowest response
- **Content Length**: Response size in bytes
- **Status Codes**: HTTP response codes

## Troubleshooting

### Server Not Running

```
Error: Cannot connect to http://localhost:8000
```

**Solution:**
```bash
cd v1
python manage.py runserver
```

### Missing Dependencies

```
ModuleNotFoundError: No module named 'requests'
```

**Solution:**
```bash
pip install requests
```

### Test Data Not Populating

```bash
# Check if data was already populated
python -m tests.data_populator --verbose

# Clear and repopulate
python -m tests.data_populator --clear
python -m tests.data_populator --verbose
```

### CSRF Token Issues

If you see CSRF errors:

1. Ensure cookies are being sent with requests
2. Check CSRF middleware is enabled in Django settings
3. Verify CSRF token extraction in responses

## Advanced Usage

### Custom Base URL

```bash
# Using Makefile
make test-url URL=http://production.example.com:8000

# Using Python
python -m tests.runner --base-url http://production.example.com:8000
```

### Verbose Output

```bash
# Show detailed test execution
python -m tests.runner --verbose

# Or via Makefile
make test  # Already verbose by default
```

### CI/CD Integration

```bash
#!/bin/bash
set -e

cd v1

# Populate test data
python -m tests.data_populator

# Run tests
python -m tests.runner

# Check results
if [ $? -eq 0 ]; then
    echo "✓ All tests passed!"
    exit 0
else
    echo "✗ Some tests failed!"
    exit 1
fi
```

### Adding New Tests

Edit `tests/runner.py` and add a new test method:

```python
def run_custom_tests(self):
    """Test custom endpoints"""
    result = self.test_request(
        "Custom Test Name",
        "GET",
        urljoin(self.pages_url, "custom-endpoint/"),
        expected_status=200,
    )
    results["tests"].append(result)
```

Then call it from `run_all_tests()`:

```python
def run_all_tests(self):
    """Run all test suites"""
    self.run_tab_tests()
    self.run_modal_tests()
    self.run_form_tests()
    self.run_subscription_tests()
    self.run_error_tests()
    self.run_custom_tests()  # Add this line
```

## Manual Testing with HTTP File

### Using VS Code REST Client

1. Install [REST Client](https://marketplace.visualstudio.com/items?itemName=humao.rest-client) extension
2. Open `tests/requests.http`
3. Click "Send Request" above any request
4. Or use "Send All Requests in File" to run all

### Using Postman

1. Import `tests/requests.http` into Postman
2. Set `baseUrl` variable to your server URL
3. Run requests individually or as a collection

### Using curl

```bash
# Test home page
curl http://localhost:8000/pages/home/

# Test with HTMX header
curl -H "HX-Request: true" http://localhost:8000/pages/home/

# Test contact form
curl -X POST http://localhost:8000/pages/contact/submit/ \
  -d "fullname=John&email=john@example.com&message=Test"
```

## Best Practices

1. **Run tests regularly** - After code changes, before commits
2. **Check reports** - Review test reports for performance issues
3. **Populate fresh data** - Use `make populate-data` before testing
4. **Monitor performance** - Track response times over time
5. **Test in isolation** - Run tests against a clean database
6. **Document failures** - Keep notes on failed tests and fixes

## Performance Benchmarks

Expected response times (on modern hardware):

- Tab views: 100-300ms
- Modal endpoints: 50-150ms
- Form submissions: 200-500ms
- Error cases: 10-50ms

If response times exceed these, investigate:
- Database query performance
- Server load
- Network latency
- Template rendering

## Support & Debugging

### Enable Debug Mode

```bash
# Run with verbose output
python -m tests.runner --verbose

# Check Django logs
tail -f logs/django.log
```

### Check System Status

```bash
# Run Django checks
make check

# Show project status
make status

# Check environment
make env-check
```

### Common Issues

| Issue | Solution |
|-------|----------|
| Connection refused | Start Django server: `make dev` |
| 404 errors | Check URL patterns in `pages/urls.py` |
| CSRF errors | Verify CSRF middleware is enabled |
| Timeout errors | Increase `TIMEOUT` in `tests/runner.py` |
| Data not found | Populate test data: `make populate-data` |

## Next Steps

1. Run initial setup: `make setup`
2. Start development server: `make dev`
3. Run tests: `make test`
4. Review test reports: `make test-reports`
5. Fix any failures and re-run tests

## Resources

- [Django Testing Documentation](https://docs.djangoproject.com/en/stable/topics/testing/)
- [Requests Library](https://requests.readthedocs.io/)
- [REST Client Extension](https://marketplace.visualstudio.com/items?itemName=humao.rest-client)
- [HTMX Documentation](https://htmx.org/)

---

Last Updated: May 9, 2024
Version: 1.0.0
