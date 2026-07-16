# Test Scripts

Automated scripts for testing, validation, and deployment.

> **Note:** Domain-level test scripts and shared test runners have been moved to
> `applications/scripts/`. See that directory for `run_domain_tests.sh`,
> `test_domain_urls.py`, `run_website_tests.sh`, and `run_container_tests.sh`.

## Directory Structure

```
applications/scripts/
├── run_domain_tests.sh          (Domain integration test suite)
├── test_domain_urls.py          (Domain URL validation)
├── run_website_tests.sh         (Cross-site smoke tests)
└── run_container_tests.sh       (Container-based tests)

tests/scripts/
├── README.md                    (this file)
├── Makefile                     (Test targets)
├── deployment/                  (Production deployment)
│   ├── deploy-production.sh
│   └── verify-deployment.sh
├── validation/                  (System validation)
│   ├── test_production.py
│   ├── test_production_simple.py
│   ├── verify_runtime.py
│   ├── verify_assets_health.py
│   └── verify-ssl-config.sh
├── utilities/                   (Helper utilities)
│   ├── load_dumped_data.py
│   ├── populate_site_data.py
│   ├── split_fixtures_by_website.py
│   ├── migrate_auth_email_templates.py
│   ├── remove_auth_email_template.py
│   ├── fix-homepage.py
│   └── update-health-views.sh
└── helpers/                     (Test runners)
    ├── health-check.sh
    └── test_vresume_pages.sh
```

## Categories

### Deployment Scripts
- `deploy-production.sh` - Deploy to production
- `verify-deployment.sh` - Verify deployment success

### Validation Scripts
- `test_production.py` - Production tests
- `test_production_simple.py` - Simplified production tests
- `verify_runtime.py` - Runtime verification
- `verify_assets_health.py` - Asset health check
- `verify-ssl-config.sh` - SSL configuration validation

### Utility Scripts
- `load_dumped_data.py` - Load database dumps
- `populate_site_data.py` - Populate test data
- `split_fixtures_by_website.py` - Split fixtures by site
- `migrate_auth_email_templates.py` - Migrate auth templates
- `remove_auth_email_template.py` - Remove auth templates
- `fix-homepage.py` - Fix homepage issues
- `update-health-views.sh` - Update health views

### Helper Scripts
- `health-check.sh` - Health check
- `test_vresume_pages.sh` - Test VResume pages

### Moved to `applications/scripts/`
- `run_domain_tests.sh` - Domain integration test suite
- `test_domain_urls.py` - Domain URL validation
- `run_website_tests.sh` - Cross-site smoke tests
- `run_container_tests.sh` - Container-based tests

## Usage

### Run All Tests
```bash
make test
```

### Run Specific Script
```bash
python tests/scripts/validation/test_production.py
bash tests/scripts/deployment/deploy-production.sh
bash applications/scripts/run_domain_tests.sh
```

### Populate Test Data
```bash
python scripts/utilities/populate_site_data.py --site ctc
```

### Verify System
```bash
python scripts/validation/verify_runtime.py --site ctc
```

