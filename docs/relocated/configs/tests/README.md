# VResume Testing Suite

Comprehensive testing framework for VResume pages and endpoints.

## Quick Start

### 1. Populate Data

```bash
cd v1

# Populate all data (test data + pages)
python -m tests.data_populator

# Test data only (no pages)
python -m tests.data_populator --test-data

# Pages only (no test data)
python -m tests.data_populator --pages

# Clear all data
python -m tests.data_populator --clear

# Export to JSON
python -m tests.data_populator --export
```

### 2. Run Tests

```bash
# Run all tests
python -m tests.runner

# Verbose output
python -m tests.runner --verbose

# Custom base URL
python -m tests.runner --base-url http://your-server:8000
```

### 3. Using Makefile

```bash
# Populate test data
make populate-data

# Run tests
make test

# Both
make populate-data test
```

## Directory Structure

```
tests/
├── __init__.py              # Package initialization
├── runner.py                # Main test execution engine
├── data_populator.py        # Unified data population (test data + pages)
├── requests.http            # HTTP request definitions (REST Client)
├── test_pages.sh            # Shell-based page testing script
└── README.md                # This file
```

## Data Population

### Unified Data Populator

The `data_populator.py` script now supports both test data and page content:

**Test Data** (Services, Skills, Sliders, Team Members, Subscribers, Blog Tags, Campaigns):
```bash
python -m tests.data_populator --test-data
```

**Page Content** (HomePage, AboutPage, ResumePage, PortfolioPage, BlogPages, ContactPage):
```bash
python -m tests.data_populator --pages
```

**All Data** (Default):
```bash
python -m tests.data_populator
```

### What Gets Populated

#### Test Data
- Services (Web Development, UI/UX Design, Mobile Development, Cloud Solutions)
- Skills (Python, JavaScript, React, Django, PostgreSQL, Docker, AWS, Git)
- Sliders (Hero section content)
- Team Members (3 team members)
- Newsletter Subscribers (5 test subscribers)
- Blog Tags (10 tags)
- Email Campaigns (3 campaigns with deliveries and tracking)
- Form Submissions (3 test submissions)

#### Page Content
- HomePage (with sliders, team, services, skills)
- AboutPage (with bio and testimonials)
- ResumePage (with education and experience)
- PortfolioPage (with 6 projects and tags)
- BlogPage (with 4 blog posts)
- ContactPage (with form configuration)
- Global Settings (name, email, phone, social media, branding)

## Test Coverage

### Tab Views (Main Pages)
- ✓ Home page
- ✓ About page
- ✓ Resume page
- ✓ Portfolio page
- ✓ Blog page
- ✓ Contact page

Each tab is tested in two modes:
- Full page load (regular HTTP request)
- HTMX fragment (with HX-Request header)

### Modal Endpoints
- ✓ Project detail modal
- ✓ Blog detail modal

### Form Submissions
- ✓ Contact form (valid submission)
- ✓ Contact form validation (missing fields)
- ✓ Newsletter subscription
- ✓ Duplicate subscription handling

### Error Cases
- ✓ Invalid tab (404)
- ✓ Invalid project ID (404)
- ✓ Invalid blog ID (404)

## Test Results

After running tests, a detailed report is generated in `test_reports/`:

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
  "tests": [...]
}
```

## Performance Metrics

The test runner tracks:
- **Response Time**: How long each request takes
- **Content Length**: Size of response
- **Status Codes**: HTTP response codes
- **Success Rate**: Percentage of passing tests
- **Total Time**: Combined time for all tests

## Command Line Options

### data_populator.py

```bash
python -m tests.data_populator [OPTIONS]

Options:
  --test-data         Populate test data only (no pages)
  --pages             Populate page content only (no test data)
  --clear             Clear all test data
  --export            Export to JSON file
  --verbose, -v       Verbose output
  --help, -h          Show help message
```

### runner.py

```bash
python -m tests.runner [OPTIONS]

Options:
  --base-url URL      Base URL for testing (default: http://localhost:8000)
  --verbose, -v       Verbose output
  --output, -o        Output format: json or text (default: json)
  --help, -h          Show help message
```

### test_pages.sh

```bash
bash tests/test_pages.sh [BASE_URL] [VERBOSE]

Examples:
  bash tests/test_pages.sh                           # Uses http://localhost:8000
  bash tests/test_pages.sh http://custom-url:8000    # Custom URL
  bash tests/test_pages.sh http://localhost:8000 true # Verbose output
```

## Testing Methods

### Option 1: Python Runner (Recommended)

```bash
cd v1

# Run all tests
python -m tests.runner

# Run with custom base URL
python -m tests.runner --base-url http://your-server:8000

# Verbose output
python -m tests.runner --verbose
```

### Option 2: HTTP File (VS Code REST Client)

1. Install [REST Client](https://marketplace.visualstudio.com/items?itemName=humao.rest-client) extension
2. Open `tests/requests.http`
3. Click "Send Request" to test individual endpoints
4. Or use "Send All Requests in File" to run all tests

### Option 3: Shell Script

```bash
bash tests/test_pages.sh
bash tests/test_pages.sh http://custom-url:8000
bash tests/test_pages.sh http://localhost:8000 true  # Verbose
```

### Option 4: Using Makefile

```bash
cd v1

# Run tests
make test

# Run tests with data population
make populate-data
make test
```

## Troubleshooting

### Server Not Running

```
Error: Cannot connect to http://localhost:8000
```

**Solution**: Start the Django development server:
```bash
cd v1
python manage.py runserver
```

### Missing Dependencies

```
ModuleNotFoundError: No module named 'requests'
```

**Solution**: Install required packages:
```bash
pip install requests
```

### CSRF Token Issues

The test runner automatically handles CSRF tokens for POST requests. If you see CSRF errors:
1. Ensure cookies are being sent with requests
2. Check that CSRF middleware is enabled in Django settings
3. Verify the CSRF token is being extracted from responses

### Page Models Not Found

If you see import errors for page models:
1. Ensure all page apps are installed in Django settings
2. Run migrations: `python manage.py migrate`
3. Check that page models are properly defined

## Integration with CI/CD

To integrate with CI/CD pipelines:

```bash
#!/bin/bash
cd v1

# Populate test data
python -m tests.data_populator --test-data

# Run tests
python -m tests.runner

# Check if all tests passed
if [ $? -eq 0 ]; then
    echo "All tests passed!"
    exit 0
else
    echo "Some tests failed!"
    exit 1
fi
```

## API Endpoints Reference

### Tab Views
- `GET /pages/home/` - Home page
- `GET /pages/about/` - About page
- `GET /pages/resume/` - Resume page
- `GET /pages/portfolio/` - Portfolio page
- `GET /pages/blog/` - Blog page
- `GET /pages/contact/` - Contact page

### Modal Endpoints
- `GET /pages/project/<project_id>/` - Project detail
- `GET /pages/blog/<blog_id>/` - Blog post detail

### Form Endpoints
- `POST /pages/contact/submit/` - Submit contact form
- `POST /pages/subscribe/` - Subscribe to newsletter

### Blog App
- `GET /pages/blog/` - Blog list
- `GET /blog/preview/<pk>/` - Blog post preview

### Connect App
- `GET /pages/comm/` - Communications page

## Notes

- All tests use the `HX-Request: true` header for HTMX endpoints
- Contact form and subscription endpoints send real emails (configure SMTP in settings)
- Test data is not persisted between runs (except subscriptions)
- Response times may vary based on server load and database performance
- Test reports are timestamped and stored in `test_reports/` directory
- Data export includes metadata about what was populated

## Contributing

To add new tests:

1. Edit `tests/runner.py`
2. Add a new test method to the `TestRunner` class
3. Call the method from `run_all_tests()`
4. Run tests to verify

Example:

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

## Support

For issues or questions:
1. Check the test report for detailed error messages
2. Review Django logs for server-side errors
3. Verify all required models and views are properly configured
4. Ensure database migrations are up to date
5. Run `make check` to verify Django system checks

---

Last Updated: May 9, 2026
Version: 2.0.0
