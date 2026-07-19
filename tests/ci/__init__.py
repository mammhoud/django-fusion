"""CI test suite for ctc-research.com.

Package structure:
    base/       — shared config, mixins, factories
    auth/       — login, registration, email confirmation, password reset
    admin/      — admin panel and Django Unfold access
    assets/     — static file availability
    email/      — live SMTP delivery

Run all tests:
    pytest projects/CI/tests/ --ds=configs.settings

Run by module:
    pytest projects/CI/tests/auth/ --ds=configs.settings
    pytest projects/CI/tests/admin/ --ds=configs.settings
    pytest projects/CI/tests/assets/ --ds=configs.settings

Run live SMTP tests (sends real emails):
    pytest projects/CI/tests/email/ -m smtp --ds=configs.settings
"""
