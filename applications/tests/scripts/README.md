# Test Scripts

Automated scripts for testing, validation, and deployment.

## Directory Structure

```
scripts/
├── README.md                    (this file)
├── Makefile                     (Test targets)
├── deployment/                  (Production deployment)
│   ├── deploy-production.sh
│   └── verify-deployment.sh
├── validation/                  (System validation)
│   ├── test_production.py
│   ├── test_production_simple.py
│   ├── test_domain_urls.py
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
    ├── run_container_tests.sh
    ├── run_website_tests.sh
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
- `test_domain_urls.py` - Domain URL validation
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
- `run_container_tests.sh` - Run container tests
- `run_website_tests.sh` - Run website tests
- `health-check.sh` - Health check
- `test_vresume_pages.sh` - Test VResume pages

## Usage

### Run All Tests
```bash
make test
```

### Run Specific Script
```bash
python scripts/validation/test_production.py
bash scripts/deployment/deploy-production.sh
```

### Populate Test Data
```bash
python scripts/utilities/populate_site_data.py --site ctc
```

### Verify System
```bash
python scripts/validation/verify_runtime.py --site ctc
```

