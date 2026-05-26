# Registration Tests Organization

## Overview
All registration tests have been moved from `websites/ctc-research.com/plugins/accounts/registration/tests/` to a centralized test location at `websites/tests/unit/accounts/registration/`.

## New Structure
```
websites/tests/unit/accounts/
├── __init__.py
├── registration/
│   ├── __init__.py
│   └── test_property_*.py (23 test files)
└── REGISTRATION_TESTS_ORGANIZATION.md
```

## Test Files (23 total)
All tests follow the property-based testing pattern with descriptive names:

### Authentication & Authorization
- `test_property_allauth_htmx_routing.py` - HTMX routing with allauth
- `test_property_allauth_hx_trigger.py` - HX trigger handling
- `test_property_allauth_token_roundtrip.py` - Token roundtrip validation
- `test_property_login_redirect.py` - Login redirect behavior
- `test_property_signin_success_email.py` - Sign-in success email

### Email & Communication
- `test_property_confirmation_email.py` - Email confirmation
- `test_property_email_failover.py` - Email failover mechanism
- `test_property_email_template_resolution.py` - Email template resolution

### Security & Rate Limiting
- `test_property_password_complexity.py` - Password complexity validation
- `test_property_rate_limiting.py` - General rate limiting
- `test_property_pw_rate_limiting.py` - Password-specific rate limiting
- `test_property_token_expiration.py` - Token expiration
- `test_property_token_single_use.py` - Single-use token enforcement

### User Management
- `test_property_group_assignment.py` - Group assignment logic
- `test_property_profile_failure_isolation.py` - Profile failure isolation
- `test_property_profile_idempotency.py` - Profile idempotency

### Configuration & Headers
- `test_property_config_validation.py` - Configuration validation
- `test_property_htmx_headers.py` - HTMX headers handling
- `test_property_hx_trigger_validity.py` - HX trigger validity

### Data Integrity
- `test_property_redirect_behavior.py` - Redirect behavior
- `test_property_single_active_snippet.py` - Single active snippet enforcement
- `test_property_transaction_rollback.py` - Transaction rollback behavior

## Running Tests
```bash
# Run all registration tests
pytest websites/tests/unit/accounts/registration/

# Run specific test file
pytest websites/tests/unit/accounts/registration/test_property_*.py

# Run with verbose output
pytest -v websites/tests/unit/accounts/registration/
```

## Migration Notes
- Original location: `websites/ctc-research.com/plugins/accounts/registration/tests/`
- New location: `websites/tests/unit/accounts/registration/`
- All test files have been copied with their original names and content preserved
- The original test directory in the plugin can be removed after verifying all tests pass in the new location
